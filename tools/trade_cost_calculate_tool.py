#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购房成本测算工具

用于精确计算二手房交易中的各项成本,包括税费、贷款等详细信息。
支持粗算(mode=0)和精算(mode=1)两种模式。
"""
import json
from typing import Dict, Any, List, Literal, Optional
from enum import Enum
import logging
from pathlib import Path

from pydantic import BaseModel, Field

# 支持直接运行和模块导入
try:
    from .base_tool import BaseTool
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.base_tool import BaseTool

try:
    from services.mcp_client import MCPClient
except ImportError:
    try:
        from ..services.mcp_client import MCPClient
    except ImportError:
        MCPClient = None  # MCP客户端可选

logger = logging.getLogger(__name__)


# 枚举定义
class FangXing(str, Enum):
    """房型"""
    LOU_FANG = "LOU_FANG"  # 楼房
    PING_FANG = "PING_FANG"  # 平房
    DI_XIA_SHI = "DI_XIA_SHI"  # 地下室


class FangWuLeiXing(str, Enum):
    """房屋类型"""
    SHANG_PIN_FANG = "SHANG_PIN_FANG"  # 商品房
    CHENG_BEN_JIA_YI_GOU_GONG_FANG = "CHENG_BEN_JIA_YI_GOU_GONG_FANG"  # 成本价已购公房
    YOU_HUI_JIA_BIAO_ZHUN_JIA_YI_GOU_GONG_FANG = "YOU_HUI_JIA_BIAO_ZHUN_JIA_YI_GOU_GONG_FANG"  # 优惠价/标准价已购公房
    JING_JI_SHI_YONG_FANG_08_NIAN_4_YUE_11_RI_ZHI_QIAN = "JING_JI_SHI_YONG_FANG_08_NIAN_4_YUE_11_RI_ZHI_QIAN"  # 经济适用房(08年4月11日之前)
    JING_JI_SHI_YONG_FANG_08_NIAN_4_YUE_11_RI_ZHI_HOU = "JING_JI_SHI_YONG_FANG_08_NIAN_4_YUE_11_RI_ZHI_HOU"  # 经济适用房(08年4月11日之后)
    AN_JING_SHI_FANG_GUAN_LI_DE_FANG_WU = "AN_JING_SHI_FANG_GUAN_LI_DE_FANG_WU"  # 按经适房管理的房屋
    XIAN_JIA_SHANG_PIN_FANG = "XIAN_JIA_SHANG_PIN_FANG"  # 限价商品房
    ZI_ZHU_XING_SHANG_PIN_FANG = "ZI_ZHU_XING_SHANG_PIN_FANG"  # 自住型商品房


class TradeCostCalculateArgs(BaseModel):
    """购房成本测算工具参数模型"""

    # 房屋基本信息组
    FANG_XING: Optional[Literal["LOU_FANG", "PING_FANG", "DI_XIA_SHI"]] = Field(
        default=None, description="房型:LOU_FANG(楼房)/PING_FANG(平房)/DI_XIA_SHI(地下室)"
    )
    FANG_WU_LEI_XING: Optional[Literal[
        "SHANG_PIN_FANG",
        "CHENG_BEN_JIA_YI_GOU_GONG_FANG",
        "YOU_HUI_JIA_BIAO_ZHUN_JIA_YI_GOU_GONG_FANG",
        "JING_JI_SHI_YONG_FANG_08_NIAN_4_YUE_11_RI_ZHI_QIAN",
        "JING_JI_SHI_YONG_FANG_08_NIAN_4_YUE_11_RI_ZHI_HOU",
        "AN_JING_SHI_FANG_GUAN_LI_DE_FANG_WU",
        "XIAN_JIA_SHANG_PIN_FANG",
        "ZI_ZHU_XING_SHANG_PIN_FANG"
    ]] = Field(default=None, description="房屋类型")
    FANG_WU_XING_ZHI: Optional[Literal["ZHU_ZHAI", "FEI_ZHU_ZHAI", "CHE_WEI"]] = Field(
        default=None, description="房屋性质:ZHU_ZHAI(住宅)/FEI_ZHU_ZHAI(非住宅)/CHE_WEI(车位)"
    )
    CHAN_QUAN_DI_ZHI: Optional[str] = Field(
        default=None, description="产权地址,示例:北京市海淀区颐和园路15号院2号楼2单元501室"
    )
    JIAN_ZHU_MIAN_JI: Optional[float] = Field(default=None, ge=0, description="建筑面积(平方米)")
    ZONG_LOU_CENG: Optional[int] = Field(default=None, ge=1, description="总楼层(层)")
    SUO_ZAI_LOU_CENG: Optional[int] = Field(default=None, ge=1, description="所在楼层(层)")
    JIAN_CHENG_NIAN_DAI: Optional[Literal[
        "2011_BIGGER",
        "2007-2010",
        "2004-2006",
        "2000-2003",
        "1991-1999",
        "1981-1990",
        "1971-1980",
        "1970_SMALLER",
        "WU_JIAN_ZHU_NIAN_DAI"
    ]] = Field(default=None, description="建成年代")

    # 区域信息组
    districtCode: Optional[str] = Field(default=None, description="城区code,ALL表示全国通用")
    cityCode: Optional[str] = Field(default=None, description="城市code,ALL表示全国通用")
    CITY_DISTRICT_CODE: Optional[List[str]] = Field(
        default=None, description="城市城区编码数组,示例:['110000','110108']"
    )
    FANG_WU_SUO_ZAI_QU_YU: Optional[str] = Field(default=None, description="房屋所在区域code")
    JIE_DAO_XIANG_ZHEN: Optional[Literal["JIE_DAO", "XIANG", "ZHEN"]] = Field(
        default=None, description="街道乡镇:JIE_DAO(街道)/XIANG(乡)/ZHEN(镇)"
    )

    # 价格信息组
    CHENG_JIAO_JIA: Optional[float] = Field(default=None, ge=0, description="成交价(万元)")
    WANG_QIAN_JIA_GE: Optional[float] = Field(default=None, ge=0, description="网签价格(万元)")

    # 交易信息组
    mode: Optional[int] = Field(default=0, description="模式:0-粗算,1-精算")
    FANG_WU_CHI_YOU_NIAN_XIAN: Optional[Literal["BU_MAN_ER", "MAN_ER_BU_MAN_WU", "MAN_WU"]] = Field(
        default=None, description="房屋持有年限:BU_MAN_ER(不满二)/MAN_ER_BU_MAN_WU(满二不满五)/MAN_WU(满五)"
    )
    FANG_WU_TAO_SHU: Optional[Literal["SHOU_TAO", "ER_TAO", "SAN_TAO"]] = Field(
        default=None, description="房屋套数:SHOU_TAO(首套)/ER_TAO(二套)/SAN_TAO(三套)"
    )
    CHU_SHOU_FANG_JIA_TING_CHI_YOU_TAO_SHU: Optional[Literal["WEI_YI", "BU_WEI_YI"]] = Field(
        default=None, description="出售方家庭持有套数:WEI_YI(唯一)/BU_WEI_YI(不唯一)"
    )

    # 交易主体信息组
    GOU_MAI_REN_XING_ZHI: Optional[Literal["GE_REN", "FEI_GE_REN"]] = Field(
        default=None, description="购买人性质:GE_REN(个人)/FEI_GE_REN(非个人)"
    )
    CHU_SHOU_REN_XING_ZHI: Optional[Literal["GE_REN", "FEI_GE_REN"]] = Field(
        default=None, description="出售人性质:GE_REN(个人)/FEI_GE_REN(非个人)"
    )
    NENG_FOU_TI_GONG_YUAN_SHI_QI_SHUI_PIAO: Optional[Literal["SHI", "FOU"]] = Field(
        default=None, description="能否提供原始契税票:SHI(是)/FOU(否)"
    )

    # 贷款信息组
    JIAO_YI_FANG_SHI: Optional[str] = Field(default=None, description="交易方式,如:CHUN_SHANG_DAI(纯商贷)")
    DAI_KUAN_JIN_E: Optional[float] = Field(default=None, ge=0, description="贷款金额(万元)")
    DAI_KUAN_NIAN_XIAN: Optional[int] = Field(default=None, ge=1, le=30, description="贷款年限(年)")
    HUAN_KUAN_FANG_SHI: Optional[Literal["DENG_E_BEN_JIN", "DENG_E_BEN_XI"]] = Field(
        default=None, description="还款方式:DENG_E_BEN_JIN(等额本金)/DENG_E_BEN_XI(等额本息)"
    )

    # 商贷专用字段
    SHANG_DAI_DAI_KUAN_JIN_E: Optional[float] = Field(default=None, ge=0, description="商贷贷款金额(元)")
    SHANG_DAI_DAI_KUAN_NIAN_XIAN: Optional[int] = Field(default=None, ge=1, le=30, description="商贷贷款年限(年)")

    # 公积金贷款专用字段(可选)
    GONG_JI_JIN_DAI_KUAN_JIN_E: Optional[float] = Field(default=None, ge=0, description="公积金贷款金额(元)")
    GONG_JI_JIN_DAI_KUAN_NIAN_XIAN: Optional[int] = Field(default=None, ge=1, le=30, description="公积金贷款年限(年)")

    # 业务标识
    houseCode: Optional[str] = Field(default=None, description="房源code,业务唯一标识")


class TradeCostCalculateTool(BaseTool):
    """购房成本测算工具

    用于精确计算购房各项成本,包括税费、贷款等详细信息。
    支持粗算(mode=0)和精算(mode=1)两种模式。
    """

    name: str = "trade_cost_calculate"
    description: str = "购房成本测算工具,计算购房各项费用明细,支持粗算和精算模式"
    args_schema: type[BaseModel] = TradeCostCalculateArgs

    def __init__(self):
        super().__init__()
        self.mcp_client = MCPClient()

    def _prepare_arguments(self, **kwargs) -> Dict[str, Any]:
        """
        准备MCP调用参数,确保所有参数格式正确

        跳过None值(不传递),将Enum转换为字符串值

        Args:
            **kwargs: 原始参数

        Returns:
            格式化后的参数字典,不包含None值
        """
        prepared = {}
        for key, value in kwargs.items():
            # 跳过None值 - 完全不传递该参数
            if value is None:
                continue
            # 处理Enum
            elif isinstance(value, Enum):
                prepared[key] = value.value
            # 处理列表
            elif isinstance(value, list):
                prepared[key] = [v.value if isinstance(v, Enum) else v for v in value]
            # 其他值直接使用
            else:
                prepared[key] = value
        return prepared

    def _format_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化MCP返回结果

        Args:
            result: MCP原始返回结果

        Returns:
            格式化后的结果
        """
        try:
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]

                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]

                    if isinstance(first_item, dict) and "text" in first_item:
                        try:
                            data = json.loads(first_item["text"])
                            return {
                                "status": "success",
                                "data": data,
                                "message": "购房成本计算成功"
                            }
                        except json.JSONDecodeError:
                            return {
                                "status": "success",
                                "data": first_item["text"],
                                "message": "购房成本计算成功"
                            }

                    if isinstance(first_item, dict):
                        for field in ["content", "data", "result", "message"]:
                            if field in first_item:
                                return {
                                    "status": "success",
                                    "data": first_item[field],
                                    "message": "购房成本计算成功"
                                }
                        return {
                            "status": "success",
                            "data": first_item,
                            "message": "购房成本计算成功"
                        }

                    if isinstance(first_item, str):
                        return {
                            "status": "success",
                            "data": first_item,
                            "message": "购房成本计算成功"
                        }

                if isinstance(content, str):
                    return {
                        "status": "success",
                        "data": content,
                        "message": "购房成本计算成功"
                    }

                if isinstance(content, dict):
                    return {
                        "status": "success",
                        "data": content,
                        "message": "购房成本计算成功"
                    }

                return {
                    "status": "success",
                    "data": str(content),
                    "message": "购房成本计算成功"
                }

            if "result" in result:
                result_data = result["result"]
                if isinstance(result_data, str):
                    return {
                        "status": "success",
                        "data": result_data,
                        "message": "购房成本计算成功"
                    }
                if isinstance(result_data, dict):
                    return {
                        "status": "success",
                        "data": result_data,
                        "message": "购房成本计算成功"
                    }

            return {
                "status": "success",
                "data": result,
                "message": "购房成本计算完成"
            }

        except Exception as e:
            logger.error(f"格式化购房成本计算结果失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "结果格式化失败"
            }

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        执行购房成本计算

        Args:
            **kwargs: 38个必填参数

        Returns:
            购房成本计算结果字典
        """
        try:
            logger.info(f"开始购房成本计算,房源code: {kwargs.get('houseCode')}")

            arguments = self._prepare_arguments(**kwargs)

            result = self.mcp_client.call_tool(
                tool_name="xiaoyi-knowledge-search",
                method="trade_cost_calculate",
                arguments=arguments
            )

            if result is None:
                return {
                    "status": "error",
                    "error": "MCP服务无响应",
                    "message": "购房成本计算失败"
                }

            formatted_result = self._format_result(result)

            logger.info(f"购房成本计算完成,房源code: {kwargs.get('houseCode')}")
            return formatted_result

        except Exception as e:
            logger.error(f"购房成本计算失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "购房成本计算失败"
            }


def main():
    """测试工具执行"""
    tool = TradeCostCalculateTool()

    # 测试用例: 北京朝阳区普通商品房 - 首套房纯商贷
    # 场景: 900万成交价，贷款630万(70%贷款比例)，30年等额本息
    result = tool.run(
        # 房屋基本信息
        FANG_XING="LOU_FANG",                              # 楼房
        FANG_WU_LEI_XING="SHANG_PIN_FANG",                # 商品房
        FANG_WU_XING_ZHI="ZHU_ZHAI",                      # 住宅
        CHAN_QUAN_DI_ZHI="北京市朝阳区建国路88号SOHO现代城2号楼1单元1501室",
        JIAN_ZHU_MIAN_JI=110.5,                           # 110.5平米
        ZONG_LOU_CENG=30,                                 # 总30层
        SUO_ZAI_LOU_CENG=15,                              # 第15层
        JIAN_CHENG_NIAN_DAI="2011_BIGGER",                # 2011年后建成

        # 区域信息
        cityCode="110000",                                # 北京市
        districtCode="110105",                            # 朝阳区
        CITY_DISTRICT_CODE=["110000", "110105"],         # 城市城区编码
        FANG_WU_SUO_ZAI_QU_YU="110105",                  # 朝阳区
        JIE_DAO_XIANG_ZHEN="JIE_DAO",                    # 街道

        # 价格信息
        CHENG_JIAO_JIA=900.0,                            # 成交价900万
        WANG_QIAN_JIA_GE=900.0,                          # 网签价900万

        # 交易信息
        mode=0,                                           # 粗算模式
        FANG_WU_CHI_YOU_NIAN_XIAN="MAN_WU",              # 满五年
        FANG_WU_TAO_SHU="SHOU_TAO",                      # 首套房
        CHU_SHOU_FANG_JIA_TING_CHI_YOU_TAO_SHU="WEI_YI", # 卖方唯一住房

        # 交易主体
        GOU_MAI_REN_XING_ZHI="GE_REN",                   # 买方个人
        CHU_SHOU_REN_XING_ZHI="GE_REN",                  # 卖方个人
        NENG_FOU_TI_GONG_YUAN_SHI_QI_SHUI_PIAO="SHI",    # 能提供原始契税票

        # 贷款信息 - 纯商贷
        JIAO_YI_FANG_SHI="CHUN_SHANG_DAI",               # 纯商贷
        SHANG_DAI_DAI_KUAN_JIN_E=6300000,                # 商贷630万元(注意单位是元)
        SHANG_DAI_DAI_KUAN_NIAN_XIAN=30,                 # 30年
        HUAN_KUAN_FANG_SHI="DENG_E_BEN_XI",              # 等额本息

        # 业务标识
        houseCode="BJ_CHAOYANG_TEST_20260121_001"        # 房源唯一标识
    )
    print("购房成本计算结果:", json.dumps(result, ensure_ascii=False, indent=2))

    # 测试获取schema
    schema = tool.get_schema()
    print("\n工具Schema:", json.dumps(schema, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
