#!/usr/bin/env bash
# scripts/check-deps.sh
# 前置条件检查：Go 环境、go.mod 存在、scope 有效性
#
# 输出格式：JSON
# {
#   "go_root": "项目根目录路径",
#   "go_version": "Go 版本号",
#   "has_gomod": true,
#   "scopes": ["子模块路径1", "子模块路径2", ...]
# }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

# main - 主函数，执行前置条件检查并输出 JSON 结果
#
# 流程：
#   1. 检测 Go 项目根目录（通过 go.mod 或 go.work）
#   2. 验证 Go 版本是否 >= 1.20
#   3. 解析 go.work 或 go.mod 获取可用的子模块（scopes）
#   4. 输出 JSON 格式的检查结果
#
# 错误处理：
#   - 任何步骤失败都会输出错误信息到 stderr
#   - 输出 JSON 格式的错误消息到 stdout
#   - 退出码为 1 表示失败
main() {
    # 步骤 1: 检测 Go 项目根目录
    local go_root
    go_root="$(detect_go_root)" || {
        local err_msg="不在 Go 项目中（未找到 go.mod 或 go.work）"
        echo "ERROR: $err_msg" >&2
        output_json <<< "{\"error\": \"$err_msg\", \"suggestion\": \"请在 Go 项目根目录下运行此脚本\"}"
        exit 1
    }

    # 步骤 2: 检查 Go 版本
    local go_version
    go_version="$(check_go_version)" || {
        local err_msg="$go_version"  # check_go_version 的输出包含错误详情
        echo "ERROR: $err_msg" >&2
        output_json <<< "{\"error\": \"$err_msg\"}"
        exit 1
    }

    # 步骤 3: 检测可用的 scope（子模块）
    # scopes 数组用于存储所有可用的子模块路径
    local scopes=()

    if [ -f "$go_root/go.work" ]; then
        # 3a. 解析 go.work 文件中的 use 指令
        # go.work 支持两种格式：
        #   - 多行格式: use (\n  ./rain-excel-checker\n  ./rain-robot\n)
        #   - 单行格式: use ./rain-excel-checker

        local in_use_block=false

        while read -r line; do
            # 去除行首行尾的空白字符
            line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

            # 检测 use 块的开始标记: "use ("
            if [[ "$line" =~ ^use[[:space:]]*\( ]]; then
                in_use_block=true
                continue
            fi

            # 检测 use 块的结束标记: ")"
            if [ "$in_use_block" = true ] && [ "$line" = ")" ]; then
                in_use_block=false
                continue
            fi

            # 在 use 块内，提取路径（格式：./path 或 ./path/）
            if [ "$in_use_block" = true ] && [[ "$line" =~ ^\.\/(.+)$ ]]; then
                local scope_path="${BASH_REMATCH[1]}"
                scope_path="${scope_path%/}"  # 移除末尾斜杠

                # 验证目录是否存在
                if [ -d "$go_root/$scope_path" ]; then
                    scopes+=("$scope_path")
                fi
            fi

            # 处理单行格式: use ./path
            if [ "$in_use_block" = false ] && [[ "$line" =~ ^use[[:space:]]+\.\/(.+)$ ]]; then
                local scope_path="${BASH_REMATCH[1]}"
                scope_path="${scope_path%/}"  # 移除末尾斜杠

                # 验证目录是否存在
                if [ -d "$go_root/$scope_path" ]; then
                    scopes+=("$scope_path")
                fi
            fi
        done < "$go_root/go.work"

    elif [ -f "$go_root/go.mod" ]; then
        # 3b. 单模块项目（没有 go.work）
        # 使用 "." 表示当前目录是唯一的作用域
        scopes+=(".")
    fi

    # 步骤 4: 输出 JSON 格式的检查结果
    # 注意：使用 output_json 处理路径中的反斜杠（Windows 兼容）
    cat <<EOF | output_json
{
  "go_root": "$go_root",
  "go_version": "$go_version",
  "has_gomod": true,
  "scopes": [$(printf '"%s",' "${scopes[@]}" | sed 's/,$//')]
}
EOF
}

# 执行主函数，传入所有命令行参数
main "$@"
