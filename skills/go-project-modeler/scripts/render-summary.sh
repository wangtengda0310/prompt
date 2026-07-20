#!/usr/bin/env bash
# scripts/render-summary.sh
# 将 JSON 数据转换为 Summary 格式（约150字符）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 从标准输入读取 JSON 数据
main() {
    local input_json=$(cat)

    # 提取关键信息
    local project_name=$(echo "$input_json" | grep -o '"project_name":"[^"]*"' | cut -d'"' -f4 | head -1)
    local total_packages=$(echo "$input_json" | grep -o '"total_packages":[0-9]*' | grep -o '[0-9]*' | head -1)
    local total_files=$(echo "$input_json" | grep -o '"total_files":[0-9]*' | grep -o '[0-9]*' | head -1)
    local health_score=$(echo "$input_json" | grep -o '"overall_health":[0-9.]*' | grep -o '[0-9.]*' | head -1)
    local chaos_index=$(echo "$input_json" | grep -o '"chaos_index":[0-9]*' | grep -o '[0-9]*' | head -1)

    # 提取主要包路径（前3个）
    local main_packages=$(echo "$input_json" | grep -o '"package":"[^"]*"' | cut -d'"' -f4 | sort -u | head -3 | tr '\n' ',' | sed 's/,$//')

    # 生成摘要（控制在150字符左右）
    cat <<EOF
📊 ${project_name}: ${total_packages}包/${total_files}文件, 健康${health_score}分, 混乱${chaos_index}
📦 核心: ${main_packages}
EOF
}

main "$@"
