#!/usr/bin/env bash
# scripts/run-extract.sh
# 数据提取统一入口

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

# extract_module_deps - 提取模块依赖关系
#
# 从指定范围的 go.mod 文件中提取模块依赖关系
# 过滤掉外部依赖（带版本号的依赖），只保留本地模块间依赖
#
# 参数:
#   $1 - scope: 相对于 go_root 的路径范围（如 "." 或 "rain-excel-checker"）
#   $2 - go_root: Go 项目根目录路径
#
# 输出:
#   JSON 格式的依赖关系数组：[{"from":"module","to":"dep"},...]
#
# 返回值:
#   0 - 成功
#   非0 - 失败（目录不存在、go命令失败等）
#
# 使用示例:
#   extract_module_deps "." "/path/to/go/root"
extract_module_deps() {
    local scope="$1"
    local go_root="$2"

    cd "$go_root/$scope"

    # go mod graph 输出格式：module dep@version
    # 提取本地模块间依赖：
    # 1. 获取当前模块名（从 go.mod 的 module 指令）
    # 2. 过滤掉外部依赖（@v0.0.0 以外的版本号）
    # 3. 只保留本地模块（通过 replace 指向的本地依赖）
    local module_name
    module_name=$(grep '^module ' go.mod | awk '{print $2}')

    # 提取本地依赖：grep -v "@v[0-9]" 过滤掉带版本号的依赖
    # 只保留 @v0.0.0 的本地依赖（replace 指令）
    go mod graph 2>/dev/null | \
        awk -v mod="$module_name" '
        # 只处理当前模块的依赖行
        $1 == mod {
            dep = $2
            # 先排除带版本号的依赖（如 @v1.2.3）
            # 再保留本地依赖（@v0.0.0）
            if (dep !~ /@v[1-9][0-9]*\.[0-9]+\.[0-9]+/ && dep ~ /@v0\.0\.0$/) {
                # 移除版本号后缀
                gsub(/@v0\.0\.0$/, "", dep)
                deps[dep] = 1
            }
        }
        END {
            print "["
            first = 1
            for (d in deps) {
                if (!first) printf ","
                printf "{\"from\":\"%s\",\"to\":\"%s\"}", mod, d
                first = 0
            }
            print "]"
        }'
}

# extract_package_info - 提取包信息（名称、文件数、导入）
#
# 使用 go list -f 提取包的元信息
#
# 参数:
#   $1 - scope: 相对于 go_root 的路径范围（如 "." 或 "rain-excel-checker"）
#   $2 - go_root: Go 项目根目录路径
#
# 输出:
#   JSON 格式的包信息数组：[{"name":"...","path":"...","go_files":N,"test_files":N,"imports":[...]},...]
#
# 返回值:
#   0 - 成功
#   非0 - 失败
extract_package_info() {
    local scope="$1"
    local go_root="$2"

    cd "$go_root/$scope"

    # go list -f 输出每个包的信息
    go list -f '{{.Name}}|{{.ImportPath}}|{{len .GoFiles}}|{{len .TestGoFiles}}|{{join .Imports ","}}' ./... 2>/dev/null | \
    awk -F'|' '
    BEGIN {
        print "["
    }
    {
        name = $1
        path = $2
        gofiles = $3
        testfiles = $4
        imports = $5

        if (NR > 1) printf ",\n"

        printf "  {\"name\":\"%s\",\"path\":\"%s\",\"go_files\":%s,\"test_files\":%s,\"imports\":[", name, path, gofiles, testfiles

        n = split(imports, imp, ",")
        for (i = 1; i <= n; i++) {
            if (i > 1) printf ","
            printf "\"%s\"", imp[i]
        }
        printf "]}"
    }
    END {
        print "\n]"
    }
    '
}

# extract_interfaces - 提取接口定义和实现者
#
# 当前实现：通过解析源代码提取接口定义（简化版）
# 限制：
#   - 只提取直接在当前包中定义的接口
#   - 不自动检测隐式实现者（Go 的隐式接口实现需要在运行时通过类型检查）
#   - 输出的 implementers 列表为空（需要后续通过 go/ast 或类型信息分析）
#
# 参数:
#   $1 - scope: 相对于 go_root 的路径范围（如 "." 或 "rain-excel-checker"）
#   $2 - go_root: Go 项目根目录路径
#
# 输出:
#   JSON 格式的接口信息：{"interfaces":[{"name":"...","path":"...","implementers":[...]},...]}
#
# 返回值:
#   0 - 成功
extract_interfaces() {
    local scope="$1"
    local go_root="$2"

    cd "$go_root/$scope"

    # 使用 grep 直接提取所有接口定义，避免嵌套 while 循环
    local tmpfile=$(mktemp)

    # 查找所有 .go 文件中的接口定义
    # 步骤1：使用 grep 提取所有接口定义行（带文件名和行号）
    grep -rnE '^type[[:space:]]+[A-Z][a-zA-Z0-9_]*[[:space:]]+interface[[:space:]]*\{' \
        --include="*.go" --exclude="*_test.go" . 2>/dev/null > "$tmpfile" || true

    # 生成 JSON 输出
    echo "{"
    echo "  \"interfaces\": ["

    local first=1
    while IFS=: read -r file_path line_num line_content; do
        if [ -n "$line_content" ]; then
            # 提取接口名（type 和 interface 之间的标识符）
            local interface_name=$(echo "$line_content" | sed -E 's/^type[[:space:]]+([A-Z][a-zA-Z0-9_]*).*/\1/')

            # 获取包的导入路径（通过 go list 获取）
            local file_dir=$(dirname "$file_path")
            local pkg_path=""
            if [ "$file_dir" = "." ]; then
                pkg_path=$(go list -f '{{.ImportPath}}' . 2>/dev/null || echo "")
            else
                # 移除开头的 ./ 再传给 go list
                local dir_for_golist="${file_dir#./}"
                if [ -n "$dir_for_golist" ]; then
                    pkg_path=$(go list -f '{{.ImportPath}}' "./$dir_for_golist" 2>/dev/null || echo "")
                fi
            fi

            # 输出接口信息
            if [ -n "$pkg_path" ] && [ -n "$interface_name" ]; then
                if [ "$first" -eq 1 ]; then
                    first=0
                else
                    echo ","
                fi

                # 转义包路径中的反斜杠（Windows 路径）
                pkg_path_escaped=$(echo "$pkg_path" | sed 's/\\/\\\\/g')

                printf "    {\"name\":\"%s\",\"path\":\"%s\",\"implementers\":[]}" \
                    "$interface_name" "$pkg_path_escaped"
            fi
        fi
    done < "$tmpfile"

    echo ""
    echo "  ]"
    echo "}"

    rm -f "$tmpfile"
}

# main - 主函数
#
# 处理命令行参数，执行各类提取操作
#
# 参数:
#   $1 - action: 操作类型（deps|packages|interfaces|all），默认为 "deps"
#   $2 - scope: 可选，相对于 go_root 的路径范围，默认为 "."
#
# 输出:
#   JSON 格式的提取结果到 stdout
#
# 返回值:
#   0 - 成功
#   1 - 失败（detect_go_root失败、go命令失败等）
main() {
    local action="${1:-deps}"
    local scope="${2:-.}"
    local go_root
    go_root="$(detect_go_root)" || exit 1

    case "$action" in
        deps)
            extract_module_deps "$scope" "$go_root"
            ;;
        packages)
            extract_package_info "$scope" "$go_root"
            ;;
        interfaces)
            extract_interfaces "$scope" "$go_root"
            ;;
        all)
            echo "{"
            echo "  \"module_deps\": $(extract_module_deps "$scope" "$go_root"),"
            echo "  \"packages\": $(extract_package_info "$scope" "$go_root"),"
            echo "  \"interfaces\": $(extract_interfaces "$scope" "$go_root")"
            echo "}"
            ;;
        *)
            echo "ERROR: Unknown action $action" >&2
            echo "Usage: $0 {deps|packages|interfaces|all} [scope]" >&2
            exit 1
            ;;
    esac
}

main "$@"
