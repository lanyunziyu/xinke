#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xiaoyi-knowledge-search MCP 工具使用示例

演示三个工具的基本使用方法:
1. TradeCostCalculateTool - 购房成本测算
2. TradeCostCalculateFormTool - 购房成本表单
3. TradingKnowledgeRetrieverTool - 交易知识检索
"""
import json
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import (
    TradeCostCalculateTool,
    TradeCostCalculateFormTool,
    TradingKnowledgeRetrieverTool
)


def example_trade_cost_calculate():
    """示例1: 购房成本测算工具"""
    print("=" * 80)
    print("示例1: 购房成本测算工具")
    print("=" * 80)

    tool = TradeCostCalculateTool()

    # 测试场景: 北京海淀区,满五唯一商品房,首套房
    result = tool.run(
        # 房屋基本信息
        FANG_XING="LOU_FANG",
        FANG_WU_LEI_XING="SHANG_PIN_FANG",
        FANG_WU_XING_ZHI="ZHU_ZHAI",
        CHAN_QUAN_DI_ZHI="北京市海淀区中关村大街1号",
        JIAN_ZHU_MIAN_JI=90.0,
        ZONG_LOU_CENG=30,
        SUO_ZAI_LOU_CENG=15,
        JIAN_CHENG_NIAN_DAI="2011_BIGGER",

        # 区域信息
        cityCode="110000",
        districtCode="110108",
        CITY_DISTRICT_CODE=["110000", "110108"],
        FANG_WU_SUO_ZAI_QU_YU="42",
        JIE_DAO_XIANG_ZHEN="JIE_DAO",

        # 价格信息
        CHENG_JIAO_JIA=600.0,
        WANG_QIAN_JIA_GE=600.0,

        # 交易信息
        mode=1,  # 精算模式
        FANG_WU_CHI_YOU_NIAN_XIAN="MAN_WU",
        FANG_WU_TAO_SHU="SHOU_TAO",
        CHU_SHOU_FANG_JIA_TING_CHI_YOU_TAO_SHU="WEI_YI",

        # 交易主体信息
        GOU_MAI_REN_XING_ZHI="GE_REN",
        CHU_SHOU_REN_XING_ZHI="GE_REN",
        NENG_FOU_TI_GONG_YUAN_SHI_QI_SHUI_PIAO="SHI",

        # 贷款信息
        JIAO_YI_FANG_SHI="CHUN_SHANG_DAI",
        DAI_KUAN_JIN_E=400.0,
        DAI_KUAN_NIAN_XIAN=25,
        HUAN_KUAN_FANG_SHI="DENG_E_BEN_XI",

        # 业务标识
        houseCode="EXAMPLE_HOUSE_001"
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()


def example_trade_cost_form():
    """示例2: 购房成本表单工具"""
    print("=" * 80)
    print("示例2: 购房成本表单工具")
    print("=" * 80)

    tool = TradeCostCalculateFormTool()

    # 场景1: 获取北京海淀区的表单配置
    print("场景1: 获取表单配置")
    result1 = tool.run(
        mode=1,
        cityCode="110000",
        districtCode="110108"
    )
    print(json.dumps(result1, ensure_ascii=False, indent=2))
    print()

    # 场景2: 带房源code调用
    print("场景2: 带房源code调用")
    result2 = tool.run(
        cityCode="110000",
        houseCode="EXAMPLE_HOUSE_001"
    )
    print(json.dumps(result2, ensure_ascii=False, indent=2))
    print()


def example_trading_knowledge_retriever():
    """示例3: 交易知识检索工具"""
    print("=" * 80)
    print("示例3: 交易知识检索工具")
    print("=" * 80)

    tool = TradingKnowledgeRetrieverTool()

    # 场景1: 单轮知识问答
    print("场景1: 单轮知识问答")
    result1 = tool.run(
        query="北京二手房交易需要缴纳哪些税费?",
        source="example_app",
        user="user_123",
        topk=5
    )
    print(json.dumps(result1, ensure_ascii=False, indent=2))
    print()

    # 场景2: 多轮对话(使用UUID格式的conversation_id)
    import uuid
    print("场景2: 多轮对话")
    conversation_id = str(uuid.uuid4())  # 生成标准UUID
    print(f"会话ID: {conversation_id}")

    # 第一轮
    print("\n第一轮对话:")
    result2 = tool.run(
        query="什么是满五唯一?",
        source="example_app",
        user="user_123",
        conversation_id=conversation_id,
        topk=3
    )
    print(json.dumps(result2, ensure_ascii=False, indent=2))
    print()

    # 第二轮(基于上下文)
    print("第二轮对话(基于上下文):")
    result3 = tool.run(
        query="满足这个条件可以减免哪些税费?",
        source="example_app",
        user="user_123",
        conversation_id=conversation_id,
        topk=3
    )
    print(json.dumps(result3, ensure_ascii=False, indent=2))
    print()

    # 第三轮(继续深入)
    print("第三轮对话(继续深入):")
    result4 = tool.run(
        query="如何判断房屋是否满五唯一?",
        source="example_app",
        user="user_123",
        conversation_id=conversation_id,
        topk=3
    )
    print(json.dumps(result4, ensure_ascii=False, indent=2))
    print()


def example_get_schemas():
    """示例4: 获取工具Schema"""
    print("=" * 80)
    print("示例4: 获取工具Schema(用于OpenAI Function Calling)")
    print("=" * 80)

    tools = [
        TradeCostCalculateTool(),
        TradeCostCalculateFormTool(),
        TradingKnowledgeRetrieverTool()
    ]

    for tool in tools:
        print(f"\n{tool.name} Schema:")
        schema = tool.get_schema()
        print(json.dumps(schema, ensure_ascii=False, indent=2))
        print()


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("xiaoyi-knowledge-search MCP 工具使用示例")
    print("=" * 80 + "\n")

    try:
        # 示例1: 购房成本测算
        example_trade_cost_calculate()

        # 示例2: 购房成本表单
        example_trade_cost_form()

        # 示例3: 交易知识检索
        example_trading_knowledge_retriever()

        # 示例4: 获取Schema
        # example_get_schemas()

    except Exception as e:
        print(f"执行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
