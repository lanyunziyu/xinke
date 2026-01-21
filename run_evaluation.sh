#!/bin/bash

# 购房资金方案自动评测系统 - 运行脚本

echo "=============================================================================="
echo "购房资金方案自动评测系统"
echo "=============================================================================="
echo ""

# 检查环境
echo "1. 检查环境配置..."

if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到.env文件，请确保已配置OPENAI_API_KEY"
    echo "   创建.env文件并添加:"
    echo "   OPENAI_API_KEY=your_api_key"
    echo ""
fi

# 询问用户选择
echo "请选择运行模式:"
echo "  1) 快速测试 (1-2分钟，验证系统可用性)"
echo "  2) 完整评测 (5-10分钟，运行所有测试用例)"
echo "  3) 查看最新评测报告"
echo ""

read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "=============================================================================="
        echo "运行快速测试..."
        echo "=============================================================================="
        python evaluation/quick_test_evaluator.py
        ;;
    2)
        echo ""
        echo "=============================================================================="
        echo "运行完整评测..."
        echo "=============================================================================="
        echo "⏱️  预计需要 5-10 分钟，请耐心等待..."
        echo ""
        python evaluation/housing_finance_evaluator.py
        ;;
    3)
        echo ""
        echo "=============================================================================="
        echo "最新评测报告"
        echo "=============================================================================="
        latest_report=$(ls -t evaluation/reports/*.json 2>/dev/null | head -1)

        if [ -z "$latest_report" ]; then
            echo "❌ 未找到评测报告，请先运行评测"
        else
            echo "报告文件: $latest_report"
            echo ""

            # 显示摘要信息
            echo "评测摘要:"
            echo "---"
            python -c '
import json
import sys
try:
    with open("'"$latest_report"'", "r", encoding="utf-8") as f:
        data = json.load(f)
        print("评测时间:", data["timestamp"])
        print("耗时: {:.2f}秒".format(data["duration_seconds"]))
        print("测试用例: {}/{} 通过 ({:.1f}%)".format(data["passed_cases"], data["total_cases"], data["pass_rate"]))
        print("验证点: {}/{} 通过 ({:.1f}%)".format(data["passed_validation_points"], data["total_validation_points"], data["validation_pass_rate"]))
        print("平均得分: {:.1f}分".format(data["average_score"]))
except Exception as e:
    print("无法解析报告:", str(e))
    sys.exit(1)
'
        fi
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "=============================================================================="
echo "更多信息请查看:"
echo "  - 评测文档: evaluation/README.md"
echo "  - 交付说明: EVALUATION_SUMMARY.md"
echo "  - 测试用例: evaluation/housing_finance_testcases.json"
echo "=============================================================================="
