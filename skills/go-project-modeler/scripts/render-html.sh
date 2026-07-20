#!/usr/bin/env bash
# scripts/render-html.sh
# 将 JSON 数据转换为 HTML5 报告

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 从标准输入读取 JSON 数据
main() {
    local input_json=$(cat)
    local output_html="${1:--}"

    # 提取项目基本信息
    local project_name=$(echo "$input_json" | grep -o '"project_name":"[^"]*"' | cut -d'"' -f4)
    local go_version=$(echo "$input_json" | grep -o '"go_version":"[^"]*"' | cut -d'"' -f4)
    local total_packages=$(echo "$input_json" | grep -o '"total_packages":[0-9]*' | grep -o '[0-9]*' | head -1)
    local total_files=$(echo "$input_json" | grep -o '"total_files":[0-9]*' | grep -o '[0-9]*' | head -1)

    # 提取健康度数据
    local health_score=$(echo "$input_json" | grep -o '"overall_health":[0-9.]*' | grep -o '[0-9.]*' | head -1)
    local chaos_index=$(echo "$input_json" | grep -o '"chaos_index":[0-9]*' | grep -o '[0-9]*' | head -1)

    # 生成 HTML5
    cat <<EOF > "$output_html"
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Go 项目分析报告 - ${project_name}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .health-section {
            padding: 30px;
        }
        .health-score {
            text-align: center;
            margin-bottom: 30px;
        }
        .health-score .score {
            font-size: 4em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .health-score .label {
            color: #666;
            margin-top: 10px;
        }
        .chaos-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }
        .chaos-healthy { background: #d4edda; color: #155724; }
        .chaos-warning { background: #fff3cd; color: #856404; }
        .chaos-danger { background: #f8d7da; color: #721c24; }
        .content {
            padding: 0 30px 30px;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .package-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
        }
        .package-item {
            background: #f8f9fa;
            padding: 10px 15px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.9em;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Go 项目分析报告</h1>
            <p>${project_name}</p>
            <p>Go 版本: ${go_version}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>总包数</h3>
                <div class="value">${total_packages}</div>
            </div>
            <div class="stat-card">
                <h3>总文件数</h3>
                <div class="value">${total_files}</div>
            </div>
            <div class="stat-card">
                <h3>健康分</h3>
                <div class="value">${health_score}</div>
            </div>
            <div class="stat-card">
                <h3>混乱指数</h3>
                <div class="value">${chaos_index}</div>
            </div>
        </div>

        <div class="health-section">
            <div class="health-score">
                <div class="score">${health_score}</div>
                <div class="label">整体健康度</div>
                <span class="chaos-badge $(if [ "$chaos_index" -le 20 ]; then echo 'chaos-healthy'; elif [ "$chaos_index" -le 40 ]; then echo 'chaos-warning'; else echo 'chaos-danger'; fi)">
                    混乱指数: ${chaos_index}
                </span>
            </div>
        </div>

        <div class="content">
            <div class="section">
                <h2>📦 项目结构</h2>
                <div class="package-list">
EOF

    # 提取包列表
    echo "$input_json" | grep -o '"package":"[^"]*"' | cut -d'"' -f4 | sort -u | while read -r pkg; do
        echo "                    <div class=\"package-item\">${pkg}</div>" >> "$output_html"
    done

    cat <<EOF >> "$output_html"
                </div>
            </div>
        </div>

        <div class="footer">
            <p>生成时间: $(date '+%Y-%m-%d %H:%M:%S')</p>
            <p>由 go-project-modeler 生成</p>
        </div>
    </div>
</body>
</html>
EOF

    if [ "$output_html" != "-" ]; then
        echo "HTML 报告已生成: $output_html"
    fi
}

main "$@"
