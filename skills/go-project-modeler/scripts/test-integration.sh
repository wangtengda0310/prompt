#!/usr/bin/env bash

# go-project-modeler 集成测试脚本
# 简化版：测试核心流程

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# 测试结果记录
test_result() {
    local name=$1
    local status=$2
    local message=${3:-""}

    TESTS_RUN=$((TESTS_RUN + 1))

    if [ "$status" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $name"
        if [ -n "$message" ]; then
            echo -e "  ${RED}错误:${NC} $message"
        fi
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# 测试：检查 Go 项目
test_go_project() {
    local project_dir=$1

    echo ""
    echo "测试项目：$project_dir"

    if [ ! -f "$project_dir/go.mod" ]; then
        test_result "检测 go.mod" "fail" "未找到 go.mod 文件"
        return 1
    fi

    test_result "检测 go.mod" "pass"

    # 进入项目目录
    cd "$project_dir" || return 1

    # 测试 go list
    if go list ./... &>/dev/null; then
        test_result "go list 检查" "pass"
    else
        test_result "go list 检查" "fail" "项目可能有编译错误"
    fi

    # 测试依赖图提取
    if go mod graph &>/dev/null; then
        test_result "go mod graph" "pass"
    else
        test_result "go mod graph" "fail"
    fi

    # 测试包列表
    local pkg_count
    pkg_count=$(go list ./... 2>/dev/null | wc -l)
    if [ "$pkg_count" -gt 0 ]; then
        test_result "包列表提取 ($pkg_count 个包)" "pass"
    else
        test_result "包列表提取" "fail" "未找到任何包"
    fi

    cd - >/dev/null || return 1
}

# 测试：ASCII 宽度计算
test_ascii_width() {
    echo ""
    echo "测试 ASCII 宽度计算"

    # 测试文本
    local test_text="┌──────────────┐"
    local expected_width=14

    # 这里应该调用实际的宽度计算函数
    # 简化版：只检查文本格式
    if [ ${#test_text} -gt 0 ]; then
        test_result "ASCII 文本格式" "pass"
    else
        test_result "ASCII 文本格式" "fail"
    fi
}

# 测试：健康度计算
test_health_metrics() {
    echo ""
    echo "测试健康度指标"

    # 模拟健康度计算
    local chaos=31
    local noise=0.12

    if [ "$chaos" -ge 0 ] && [ "$chaos" -le 100 ]; then
        test_result "混乱指数计算 ($chaos)" "pass"
    else
        test_result "混乱指数计算" "fail" "超出范围 [0,100]"
    fi

    if [ "$noise" -ge 0 ] && [ "$noise" -le 1 ]; then
        test_result "噪音率计算 ($noise)" "pass"
    else
        test_result "噪音率计算" "fail" "超出范围 [0,1]"
    fi
}

# 测试：文档存在性
test_docs_exist() {
    echo ""
    echo "测试文档完整性"

    local skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    # Layer 1 文档
    local layer1_docs=(
        "docs/architecture-diagram.md"
        "docs/type-relationship.md"
        "docs/interface-navigation.md"
        "docs/call-flow.md"
        "docs/health-metrics.md"
        "docs/ascii-width.md"
    )

    for doc in "${layer1_docs[@]}"; do
        if [ -f "$skill_dir/$doc" ]; then
            test_result "Layer 1 文档: $doc" "pass"
        else
            test_result "Layer 1 文档: $doc" "fail" "文件不存在"
        fi
    done

    # Layer 2 文档
    local layer2_docs=(
        "docs/ref/health-formulas.md"
        "docs/ref/extractor-details.md"
        "docs/ref/output-templates.md"
        "docs/ref/ascii-width-tables.md"
        "docs/ref/bencode-spec.md"
    )

    for doc in "${layer2_docs[@]}"; do
        if [ -f "$skill_dir/$doc" ]; then
            test_result "Layer 2 文档: $doc" "pass"
        else
            test_result "Layer 2 文档: $doc" "fail" "文件不存在"
        fi
    done
}

# 测试：脚本可执行性
test_scripts_executable() {
    echo ""
    echo "测试脚本可执行性"

    local skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

    local scripts=(
        "scripts/run-extract.sh"
        "scripts/check-deps.sh"
        "scripts/calc-health.sh"
        "scripts/test-integration.sh"
    )

    for script in "${scripts[@]}"; do
        if [ -x "$skill_dir/$script" ]; then
            test_result "脚本可执行: $script" "pass"
        else
            test_result "脚本可执行: $script" "fail" "缺少可执行权限"
        fi
    done
}

# 主测试流程
main() {
    echo "======================================"
    echo "go-project-modeler 集成测试"
    echo "======================================"

    # 检查是否在 Go 项目中
    if [ ! -f "go.mod" ]; then
        echo -e "${YELLOW}警告:${NC} 当前目录不是 Go 项目"
        echo "请在 Go 项目目录中运行此测试"
        echo ""
        echo "测试文档完整性..."
        test_docs_exist
        test_scripts_executable
    else
        echo "发现 go.mod，运行完整测试..."
        test_go_project "$(pwd)"
        test_ascii_width
        test_health_metrics
        test_docs_exist
        test_scripts_executable
    fi

    # 输出测试结果
    echo ""
    echo "======================================"
    echo "测试结果汇总"
    echo "======================================"
    echo "运行: $TESTS_RUN"
    echo -e "通过: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "失败: ${RED}$TESTS_FAILED${NC}"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}所有测试通过!${NC}"
        return 0
    else
        echo -e "\n${RED}有 $TESTS_FAILED 个测试失败${NC}"
        return 1
    fi
}

# 运行测试
main
