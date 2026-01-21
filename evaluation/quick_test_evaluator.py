#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购房资金方案快速测试版本

运行单个测试用例来验证评测系统是否正常工作
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.housing_finance_agent import HousingFinanceAgent
from tools.trading_knowledge_retriever_tool import TradingKnowledgeRetrieverTool
from tools.quark_web_search_tool import QuarkWebSearchTool
from tools.trade_cost_calculate_tool import TradeCostCalculateTool
from tools.trade_cost_calculate_form_tool import TradeCostCalculateFormTool
from tools.report_generator import ReportGeneratorTool


def main():
    """快速测试评测系统"""
    print("=" * 80)
    print("购房资金方案评测系统 - 快速测试")
    print("=" * 80)

    # 初始化Agent
    print("\n1. 初始化Agent...")
    try:
        tools = {
            "trading_knowledge_retriever": TradingKnowledgeRetrieverTool(),
            "quark_web_search": QuarkWebSearchTool(),
            "trade_cost_calculate": TradeCostCalculateTool(),
            "trade_cost_calculate_form": TradeCostCalculateFormTool(),
            "report_generator": ReportGeneratorTool()
        }

        agent = HousingFinanceAgent(tools=tools)
        print("✓ Agent初始化成功")
    except Exception as e:
        print(f"✗ Agent初始化失败: {e}")
        return

    # 运行简单测试
    print("\n2. 运行测试查询...")
    test_query = "我是北京户口，想在朝阳区买首套房，总价900万，贷款630万，30年等额本息。请计算首付和月供。"

    print(f"测试查询: {test_query}")
    print("\n正在执行Agent...")

    try:
        result = agent.run(test_query, max_iterations=10)

        if result['status'] == 'success':
            print(f"\n✓ Agent执行成功")
            print(f"迭代次数: {result['iterations']}")
            print(f"\nAgent响应:\n{'-' * 80}")
            print(result['response'])
            print('-' * 80)

            # 简单验证
            response = result['response']
            print("\n3. 验证响应内容...")

            checks = []

            # 检查是否包含首付信息
            if '首付' in response or '270' in response:
                checks.append(("✓", "包含首付信息"))
            else:
                checks.append(("✗", "缺少首付信息"))

            # 检查是否包含月供信息
            if '月供' in response:
                checks.append(("✓", "包含月供信息"))
            else:
                checks.append(("✗", "缺少月供信息"))

            # 检查是否包含贷款信息
            if '贷款' in response or '630' in response:
                checks.append(("✓", "包含贷款信息"))
            else:
                checks.append(("✗", "缺少贷款信息"))

            # 检查是否包含税费信息
            if '税' in response or '契税' in response:
                checks.append(("✓", "包含税费信息"))
            else:
                checks.append(("✗", "缺少税费信息"))

            for symbol, msg in checks:
                print(f"  {symbol} {msg}")

            passed = sum(1 for s, _ in checks if s == "✓")
            total = len(checks)

            print(f"\n基本验证通过率: {passed}/{total} ({passed/total*100:.0f}%)")

            if passed == total:
                print("\n🎉 快速测试通过！评测系统可以正常工作。")
            elif passed >= total * 0.75:
                print("\n⚠️  快速测试部分通过，建议运行完整评测。")
            else:
                print("\n❌ 快速测试失败，请检查Agent配置。")

        else:
            print(f"\n✗ Agent执行失败: {result.get('error', '未知错误')}")

    except Exception as e:
        print(f"\n✗ 执行异常: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("提示: 运行完整评测请执行:")
    print("  python evaluation/housing_finance_evaluator.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
