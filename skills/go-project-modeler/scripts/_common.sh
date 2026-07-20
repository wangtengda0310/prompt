#!/usr/bin/env bash
# scripts/_common.sh
# 共享函数库，被所有脚本 source

# detect_go_root - 检测 Go 项目根目录
#
# 从当前目录向上查找，直到找到包含有效 go.mod 或 go.work 的目录
# 有效 go.mod 必须包含 module 指令
#
# 输出:
#   找到的 Go 项目根目录路径
#
# 返回值:
#   0 - 找到 Go 项目根目录
#   1 - 未找到（到达根目录仍未找到）
#
# 使用示例:
#   root=$(detect_go_root) || { echo "错误：不在 Go 项目中"; exit 1; }
detect_go_root() {
    local current_dir="$PWD"
    # 向上遍历目录树，直到根目录
    while [ "$current_dir" != "/" ]; do
        # 检查 go.work 文件
        if [ -f "$current_dir/go.work" ]; then
            echo "$current_dir"
            return 0
        fi
        # 检查 go.mod 文件，并验证其有效性（包含 module 指令）
        if [ -f "$current_dir/go.mod" ]; then
            # 使用 grep 检查 go.mod 是否包含 module 指令
            if grep -qE '^module[[:space:]]' "$current_dir/go.mod" 2>/dev/null; then
                echo "$current_dir"
                return 0
            fi
        fi
        # 移动到父目录
        current_dir="$(dirname "$current_dir")"
    done
    return 1
}

# check_go_version - 检查 Go 版本是否满足最低要求
#
# 执行 go version 命令解析版本号，验证是否 >= 1.20
#
# 输出:
#   Go 版本号（如 "go1.20"）或错误消息
#
# 返回值:
#   0 - Go 版本满足要求
#   1 - Go 未安装或版本不满足要求
#
# 使用示例:
#   version=$(check_go_version) || { echo "错误：$version"; exit 1; }
check_go_version() {
    # 解析 go version 输出，提取版本号（如 "go1.20.5" -> "go1.20"）
    local go_version_output=$(go version 2>/dev/null)
    if [ -z "$go_version_output" ]; then
        echo "ERROR: Go 未安装或不在 PATH 中。请访问 https://go.dev/dl/ 下载安装。"
        return 1
    fi

    # 提取版本号（支持 "go1.20" 和 "go1.20.5" 格式）
    local go_version=$(echo "$go_version_output" | grep -oE 'go[0-9]+\.[0-9]+' | head -1)

    # 解析主版本号和次版本号
    local major_minor=$(echo "$go_version" | cut -d'.' -f2)  # 提取 "1" 和 "20" 中的 "20"
    local minor=$(echo "$go_version" | cut -d'.' -f2)  # 次版本号

    # 检查次版本号是否 >= 20
    if [ "$minor" -lt 20 ]; then
        echo "ERROR: Go 版本 $go_version 不满足要求（最低 1.20）。当前版本：$go_version_output，请升级。"
        return 1
    fi

    echo "$go_version"
    return 0
}

# output_json - 处理 JSON 输出的转义
#
# 从标准输入读取 JSON 内容，转义特殊字符后输出
# 主要处理 Windows 路径中的反斜杠
#
# 输入:
#   标准输入的 JSON 内容
#
# 输出:
#   转义后的 JSON 内容
#
# 使用示例:
#   echo '{"path": "C:\\Users"}' | output_json
#   cat <<EOF | output_json
#   {"path": "$HOME"}
#   EOF
output_json() {
    # 转义反斜杠（Windows 路径兼容）
    # 注意：这种方式假设输入已经是有效的 JSON 格式
    # 如果需要完整的 JSON 处理，建议使用 jq 生成 JSON 而非字符串拼接
    cat - | sed 's/\\/\\\\/g'
}
