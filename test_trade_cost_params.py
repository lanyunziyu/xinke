#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购房成本测算工具 - 测试入参示例

提供多种场景的测试参数，方便快速测试和调试
"""
from tools.trade_cost_calculate_tool import TradeCostCalculateTool

def test_case_1_pure_commercial_loan():
    """
    测试场景1: 北京朝阳区 - 首套房纯商贷

    房源信息:
    - 地址: 朝阳区建国路88号SOHO现代城
    - 面积: 110.5平米
    - 楼层: 15/30层
    - 建成年代: 2011年后
    - 房龄: 满五年

    交易信息:
    - 成交价: 900万
    - 首付: 270万 (30%)
    - 商贷: 630万，30年，等额本息
    """
    tool = TradeCostCalculateTool()

    params = {
        # 房屋基本信息
        "FANG_XING": "LOU_FANG",
        "FANG_WU_LEI_XING": "SHANG_PIN_FANG",
        "FANG_WU_XING_ZHI": "ZHU_ZHAI",
        "CHAN_QUAN_DI_ZHI": "北京市朝阳区建国路88号SOHO现代城2号楼1单元1501室",
        "JIAN_ZHU_MIAN_JI": 110.5,
        "ZONG_LOU_CENG": 30,
        "SUO_ZAI_LOU_CENG": 15,
        "JIAN_CHENG_NIAN_DAI": "2011_BIGGER",

        # 区域信息
        "cityCode": "110000",
        "districtCode": "110105",
        "CITY_DISTRICT_CODE": ["110000", "110105"],
        "FANG_WU_SUO_ZAI_QU_YU": "110105",
        "JIE_DAO_XIANG_ZHEN": "JIE_DAO",

        # 价格信息
        "CHENG_JIAO_JIA": 900.0,
        "WANG_QIAN_JIA_GE": 900.0,

        # 交易信息
        "mode": 0,
        "FANG_WU_CHI_YOU_NIAN_XIAN": "MAN_WU",
        "FANG_WU_TAO_SHU": "SHOU_TAO",
        "CHU_SHOU_FANG_JIA_TING_CHI_YOU_TAO_SHU": "WEI_YI",

        # 交易主体
        "GOU_MAI_REN_XING_ZHI": "GE_REN",
        "CHU_SHOU_REN_XING_ZHI": "GE_REN",
        "NENG_FOU_TI_GONG_YUAN_SHI_QI_SHUI_PIAO": "SHI",

        # 贷款信息 - 纯商贷
        "JIAO_YI_FANG_SHI": "CHUN_SHANG_DAI",
        "SHANG_DAI_DAI_KUAN_JIN_E": 6300000,  # 630万元
        "SHANG_DAI_DAI_KUAN_NIAN_XIAN": 30,
        "HUAN_KUAN_FANG_SHI": "DENG_E_BEN_XI",

        # 业务标识
        "houseCode": "BJ_CHAOYANG_TEST_001"
    }

    result = tool.run(**params)
    return result


def test_case_2_combination_loan():
    """
    测试场景2: 北京海淀区 - 首套房组合贷

    房源信息:
    - 地址: 海淀区颐和园路15号院
    - 面积: 95平米
    - 楼层: 10/20层
    - 建成年代: 2007-2010
    - 房龄: 满二不满五

    交易信息:
    - 成交价: 600万
    - 首付: 120万 (20%)
    - 商贷: 368万，30年
    - 公积金贷款: 112万，30年
    """
    tool = TradeCostCalculateTool()

    params = {
        # 房屋基本信息
        "FANG_XING": "LOU_FANG",
        "FANG_WU_LEI_XING": "SHANG_PIN_FANG",
        "FANG_WU_XING_ZHI": "ZHU_ZHAI",
        "CHAN_QUAN_DI_ZHI": "北京市海淀区颐和园路15号院2号楼2单元1001室",
        "JIAN_ZHU_MIAN_JI": 95.0,
        "ZONG_LOU_CENG": 20,
        "SUO_ZAI_LOU_CENG": 10,
        "JIAN_CHENG_NIAN_DAI": "2007-2010",

        # 区域信息
        "cityCode": "110000",
        "districtCode": "110108",
        "CITY_DISTRICT_CODE": ["110000", "110108"],
        "FANG_WU_SUO_ZAI_QU_YU": "110108",
        "JIE_DAO_XIANG_ZHEN": "JIE_DAO",

        # 价格信息
        "CHENG_JIAO_JIA": 600.0,
        "WANG_QIAN_JIA_GE": 600.0,

        # 交易信息
        "mode": 0,
        "FANG_WU_CHI_YOU_NIAN_XIAN": "MAN_ER_BU_MAN_WU",
        "FANG_WU_TAO_SHU": "SHOU_TAO",
        "CHU_SHOU_FANG_JIA_TING_CHI_YOU_TAO_SHU": "BU_WEI_YI",

        # 交易主体
        "GOU_MAI_REN_XING_ZHI": "GE_REN",
        "CHU_SHOU_REN_XING_ZHI": "GE_REN",
        "NENG_FOU_TI_GONG_YUAN_SHI_QI_SHUI_PIAO": "SHI",

        # 贷款信息 - 组合贷
        "JIAO_YI_FANG_SHI": "ZU_HE_DAI",
        "SHANG_DAI_DAI_KUAN_JIN_E": 3680000,  # 368万元
        "SHANG_DAI_DAI_KUAN_NIAN_XIAN": 30,
        "GONG_JI_JIN_DAI_KUAN_JIN_E": 1120000,  # 112万元
        "GONG_JI_JIN_DAI_KUAN_NIAN_XIAN": 30,
        "HUAN_KUAN_FANG_SHI": "DENG_E_BEN_XI",

        # 业务标识
        "houseCode": "BJ_HAIDIAN_TEST_002"
    }

    result = tool.run(**params)
    return result


def test_case_3_second_home():
    """
    测试场景3: 北京西城区 - 二套房纯商贷

    房源信息:
    - 地址: 西城区金融街购物中心
    - 面积: 150平米
    - 楼层: 25/33层
    - 建成年代: 2011年后
    - 房龄: 不满二年

    交易信息:
    - 成交价: 1500万
    - 首付: 900万 (60% - 二套房)
    - 商贷: 600万，20年，等额本金
    """
    tool = TradeCostCalculateTool()

    params = {
        # 房屋基本信息
        "FANG_XING": "LOU_FANG",
        "FANG_WU_LEI_XING": "SHANG_PIN_FANG",
        "FANG_WU_XING_ZHI": "ZHU_ZHAI",
        "CHAN_QUAN_DI_ZHI": "北京市西城区金融街购物中心3号楼2单元2501室",
        "JIAN_ZHU_MIAN_JI": 150.0,
        "ZONG_LOU_CENG": 33,
        "SUO_ZAI_LOU_CENG": 25,
        "JIAN_CHENG_NIAN_DAI": "2011_BIGGER",

        # 区域信息
        "cityCode": "110000",
        "districtCode": "110102",
        "CITY_DISTRICT_CODE": ["110000", "110102"],
        "FANG_WU_SUO_ZAI_QU_YU": "110102",
        "JIE_DAO_XIANG_ZHEN": "JIE_DAO",

        # 价格信息
        "CHENG_JIAO_JIA": 1500.0,
        "WANG_QIAN_JIA_GE": 1500.0,

        # 交易信息
        "mode": 0,
        "FANG_WU_CHI_YOU_NIAN_XIAN": "BU_MAN_ER",
        "FANG_WU_TAO_SHU": "ER_TAO",
        "CHU_SHOU_FANG_JIA_TING_CHI_YOU_TAO_SHU": "BU_WEI_YI",

        # 交易主体
        "GOU_MAI_REN_XING_ZHI": "GE_REN",
        "CHU_SHOU_REN_XING_ZHI": "GE_REN",
        "NENG_FOU_TI_GONG_YUAN_SHI_QI_SHUI_PIAO": "FOU",

        # 贷款信息 - 纯商贷
        "JIAO_YI_FANG_SHI": "CHUN_SHANG_DAI",
        "SHANG_DAI_DAI_KUAN_JIN_E": 6000000,  # 600万元
        "SHANG_DAI_DAI_KUAN_NIAN_XIAN": 20,
        "HUAN_KUAN_FANG_SHI": "DENG_E_BEN_JIN",

        # 业务标识
        "houseCode": "BJ_XICHENG_TEST_003"
    }

    result = tool.run(**params)
    return result


def test_minimal_params():
    """
    测试场景4: 最小参数集（只传必需参数）

    用于测试工具对可选参数的处理
    """
    tool = TradeCostCalculateTool()

    # 只传少量关键参数，其他由工具自动填充空字符串
    params = {
        "CHENG_JIAO_JIA": 500.0,
        "SHANG_DAI_DAI_KUAN_JIN_E": 3000000,
        "SHANG_DAI_DAI_KUAN_NIAN_XIAN": 30,
        "houseCode": "MINIMAL_TEST"
    }

    result = tool.run(**params)
    return result


if __name__ == "__main__":
    import json

    print("=" * 80)
    print("测试场景1: 北京朝阳区 - 首套房纯商贷")
    print("=" * 80)
    result1 = test_case_1_pure_commercial_loan()
    print(json.dumps(result1, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("测试场景2: 北京海淀区 - 首套房组合贷")
    print("=" * 80)
    result2 = test_case_2_combination_loan()
    print(json.dumps(result2, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("测试场景3: 北京西城区 - 二套房纯商贷")
    print("=" * 80)
    result3 = test_case_3_second_home()
    print(json.dumps(result3, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("测试场景4: 最小参数集")
    print("=" * 80)
    result4 = test_minimal_params()
    print(json.dumps(result4, ensure_ascii=False, indent=2))
