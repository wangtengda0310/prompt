#!/bin/bash
# ASCII 宽度处理脚本 - 用于计算和校正文本在 ASCII 艺术框中的显示宽度
# 用途：处理多字节字符（如中文）的宽度计算，确保文本在 ASCII 边框中对齐
#
# 使用方法：
#   source ascii-width.sh
#   width=$(get_display_width "你好世界")
#   padded=$(pad_text "标题" 20)
#   boxed=$(create_box "内容" 40)
#
# 依赖：
#   - wcwidth (可选，如果没有则使用内置的简化算法)
#   - Bash 4.0+

# 内置字符宽度映射表
# 返回单个字符的显示宽度：1=半角，2=全角
function char_width() {
    local char="$1"
    local code=$(printf '%d' "'$char")

    # ASCII 可见字符 (0x20-0x7E)
    if [ "$code" -ge 32 ] && [ "$code" -le 126 ]; then
        echo 1
        return
    fi

    # 常见全角字符范围（CJK 统一汉字）
    if [ "$code" -ge 19968 ] && [ "$code" -le 40869 ]; then
        echo 2
        return
    fi

    # CJK 扩展 A
    if [ "$code" -ge 13312 ] && [ "$code" -le 19903 ]; then
        echo 2
        return
    fi

    # 全角标点符号
    if [ "$code" -ge 65281 ] && [ "$code" -le 65374 ]; then
        echo 2
        return
    fi

    # 默认假设为半角
    echo 1
}

# 计算字符串的显示宽度
# get_display_width "你好世界"  # 输出: 8
function get_display_width() {
    local text="$1"
    local width=0
    local i=0
    local len=${#text}

    while [ "$i" -lt "$len" ]; do
        local char="${text:$i:1}"
        width=$((width + $(char_width "$char")))
        i=$((i + 1))
    done

    echo "$width"
}

# 文本左对齐填充（考虑显示宽度）
# pad_text "标题" 20  # 输出: "标题                "
function pad_text() {
    local text="$1"
    local target_width="$2"
    local fill_char="${3:- }"
    local current_width=$(get_display_width "$text")
    local padding=$((target_width - current_width))

    if [ "$padding" -le 0 ]; then
        echo "$text"
        return
    fi

    local padding_str=""
    for ((i=0; i<padding; i++)); do
        padding_str="${padding_str}${fill_char}"
    done

    echo "${text}${padding_str}"
}

# 文本居中对齐（考虑显示宽度）
# center_text "标题" 40  # 输出: "              标题              "
function center_text() {
    local text="$1"
    local target_width="$2"
    local current_width=$(get_display_width "$text")

    if [ "$current_width" -ge "$target_width" ]; then
        echo "$text"
        return
    fi

    local padding=$((target_width - current_width))
    local left_pad=$((padding / 2))
    local right_pad=$((padding - left_pad))

    local left_str=""
    local right_str=""

    for ((i=0; i<left_pad; i++)); do
        left_str="${left_str} "
    done

    for ((i=0; i<right_pad; i++)); do
        right_str="${right_str} "
    done

    echo "${left_str}${text}${right_str}"
}

# 创建 ASCII 边框（单行）
# create_border 40  # 输出: "########################################"
function create_border() {
    local width="$1"
    local char="${2:-#}"
    local border=""

    for ((i=0; i<width; i++)); do
        border="${border}${char}"
    done

    echo "$border"
}

# 创建单行文本框
# create_line "标题内容" 40  # 输出带左右边框的行
function create_line() {
    local text="$1"
    local box_width="$2"
    local content_width=$((box_width - 2))  # 减去左右边框
    local padded_text=$(pad_text "$text" "$content_width")
    echo "# ${padded_text} #"
}

# 创建居中文本框
# create_centered_line "标题" 40  # 输出居中的标题行
function create_centered_line() {
    local text="$1"
    local box_width="$2"
    local content_width=$((box_width - 2))
    local centered_text=$(center_text "$text" "$content_width")
    echo "# ${centered_text} #"
}

# 创建完整文本框
# create_box "多行\n内容" 40
function create_box() {
    local text="$1"
    local box_width="$2"
    local border=$(create_border "$box_width")

    echo "$border"
    echo "$text" | while IFS= read -r line; do
        create_line "$line" "$box_width"
    done
    echo "$border"
}

# 截断文本以适应指定宽度
# truncate_text "很长的文本内容" 10  # 输出: "很长的文本..."
function truncate_text() {
    local text="$1"
    local max_width="$2"
    local ellipsis="${3:-...}"
    local ellipsis_width=$(get_display_width "$ellipsis")
    local current_width=0
    local result=""
    local i=0
    local len=${#text}

    while [ "$i" -lt "$len" ]; do
        local char="${text:$i:1}"
        local char_w=$(char_width "$char")
        local new_width=$((current_width + char_w))

        if [ "$new_width" -gt "$((max_width - ellipsis_width))" ]; then
            result="${result}${ellipsis}"
            break
        fi

        result="${result}${char}"
        current_width="$new_width"
        i=$((i + 1))
    done

    echo "$result"
}

# 检测 wcwidth 命令是否可用
if command -v wcwidth &> /dev/null; then
    # 如果有 wcwidth 命令，使用更精确的计算
    function get_display_width() {
        wcwidth "$1" 2>/dev/null || echo ${#1}
    }
fi

# 导出函数以便在其他脚本中使用
export -f char_width
export -f get_display_width
export -f pad_text
export -f center_text
export -f create_border
export -f create_line
export -f create_centered_line
export -f create_box
export -f truncate_text
