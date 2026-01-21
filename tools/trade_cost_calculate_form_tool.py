#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购房成本表单工具

用于获取购房成本计算的表单配置或批量计算。
支持灵活的参数组合,所有参数均为可选。
"""
import json
from typing import Dict, Any, List, Optional
import logging

from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from services.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class TradeCostCalculateFormArgs(BaseModel):
    """购房成本表单工具参数模型"""

    calType: Optional[List[str]] = Field(None, description="费用计算类型列表")
    mode: Optional[int] = Field(None, description="模式:0-粗算,1-精算")
    districtCode: Optional[str] = Field(None, description="城区code")
    cityCode: Optional[str] = Field(None, description="城市code")
    houseCode: Optional[str] = Field(None, description="房源code,业务唯一标识")
    calcId: Optional[str] = Field(None, description="计算ID")
    source: Optional[str] = Field(None, description="来源标识")
    paramMap: Optional[Dict[str, Any]] = Field(None, description="参数映射对象")


class TradeCostCalculateFormTool(BaseTool):
    """购房成本表单工具

    用于获取购房成本计算的表单配置或批量计算。
    支持灵活的参数组合,所有参数均为可选。
    """

    name: str = "trade_cost_calculate_form"
    description: str = "购房成本表单工具,获取或配置购房成本计算表单"
    args_schema: type[BaseModel] = TradeCostCalculateFormArgs

    def __init__(self):
        super().__init__()
        self.mcp_client = MCPClient()

    def _clean_arguments(self, **kwargs) -> Dict[str, Any]:
        """
        清理参数,移除None值

        Args:
            **kwargs: 原始参数

        Returns:
            清理后的参数字典
        """
        return {k: v for k, v in kwargs.items() if v is not None}

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
                                "message": "表单数据获取成功"
                            }
                        except json.JSONDecodeError:
                            return {
                                "status": "success",
                                "data": first_item["text"],
                                "message": "表单数据获取成功"
                            }

                    if isinstance(first_item, dict):
                        for field in ["content", "data", "result", "message"]:
                            if field in first_item:
                                return {
                                    "status": "success",
                                    "data": first_item[field],
                                    "message": "表单数据获取成功"
                                }
                        return {
                            "status": "success",
                            "data": first_item,
                            "message": "表单数据获取成功"
                        }

                    if isinstance(first_item, str):
                        return {
                            "status": "success",
                            "data": first_item,
                            "message": "表单数据获取成功"
                        }

                if isinstance(content, str):
                    return {
                        "status": "success",
                        "data": content,
                        "message": "表单数据获取成功"
                    }

                if isinstance(content, dict):
                    return {
                        "status": "success",
                        "data": content,
                        "message": "表单数据获取成功"
                    }

                return {
                    "status": "success",
                    "data": str(content),
                    "message": "表单数据获取成功"
                }

            if "result" in result:
                result_data = result["result"]
                if isinstance(result_data, str):
                    return {
                        "status": "success",
                        "data": result_data,
                        "message": "表单数据获取成功"
                    }
                if isinstance(result_data, dict):
                    return {
                        "status": "success",
                        "data": result_data,
                        "message": "表单数据获取成功"
                    }

            return {
                "status": "success",
                "data": result,
                "message": "表单操作完成"
            }

        except Exception as e:
            logger.error(f"格式化表单结果失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "结果格式化失败"
            }

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        执行表单工具操作

        Args:
            **kwargs: 可选参数

        Returns:
            表单数据或操作结果
        """
        try:
            logger.info(f"执行购房成本表单工具,参数: {kwargs}")

            arguments = self._clean_arguments(**kwargs)

            result = self.mcp_client.call_tool(
                tool_name="xiaoyi-knowledge-search",
                method="trade_cost_calculate_form_tool",
                arguments=arguments
            )

            if result is None:
                return {
                    "status": "error",
                    "error": "MCP服务无响应",
                    "message": "表单工具调用失败"
                }

            formatted_result = self._format_result(result)

            logger.info("购房成本表单工具执行完成")
            return formatted_result

        except Exception as e:
            logger.error(f"购房成本表单工具执行失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "表单工具执行失败"
            }


def main():
    """测试工具执行"""
    tool = TradeCostCalculateFormTool()

    # 测试用例1: 获取表单配置
    result = tool.run(
        mode=1,
        cityCode="110000",
        districtCode="110108"
    )
    print("表单工具结果:", json.dumps(result, ensure_ascii=False, indent=2))

    # 测试用例2: 无参数调用
    result2 = tool.run()
    print("\n无参数调用结果:", json.dumps(result2, ensure_ascii=False, indent=2))

    # 测试获取schema
    schema = tool.get_schema()
    print("\n工具Schema:", json.dumps(schema, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
