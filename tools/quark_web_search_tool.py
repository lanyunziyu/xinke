#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页搜索工具

集成网页搜索功能，用于在线搜索相关信息
"""
import json
from typing import Dict, Any, Optional
import logging

from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from services.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class QuarkWebSearchArgs(BaseModel):
    """网页搜索工具参数模型"""
    query: str = Field(..., description="搜索关键词")
    max_results: int = Field(default=3, ge=1, le=10, description="最大结果数量，默认为3")


class QuarkWebSearchTool(BaseTool):
    """用于在线搜索相关信息，支持指定最大结果数量"""

    name: str = "quark_web_search"
    description: str = "用于在线搜索相关信息，支持指定最大结果数量"
    args_schema: type[BaseModel] = QuarkWebSearchArgs

    def __init__(self):
        super().__init__()
        self.mcp_client = MCPClient()

    def format_search_results(self, results: dict) -> str:
        """
        格式化搜索结果

        Args:
            results: MCP客户端返回的搜索结果

        Returns:
            格式化后的搜索结果字符串
        """
        try:
            # 处理MCP返回的结果格式
            if "result" in results and "content" in results["result"]:
                content = results["result"]["content"]

                # 如果content是列表，处理第一个元素
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]

                    # 如果第一个元素是字典且包含text字段
                    if isinstance(first_item, dict) and "text" in first_item:
                        return first_item["text"]

                    # 如果第一个元素是字典但没有text字段，尝试其他字段
                    if isinstance(first_item, dict):
                        # 查找可能的文本字段
                        for field in ["content", "data", "result", "message"]:
                            if field in first_item:
                                return str(first_item[field])
                        # 如果没有找到，返回整个字典
                        return json.dumps(first_item, ensure_ascii=False, indent=2)

                    # 如果第一个元素是字符串，直接返回
                    if isinstance(first_item, str):
                        return first_item

                # 如果content是字符串，直接返回
                if isinstance(content, str):
                    return content

                # 如果content是字典，尝试格式化
                if isinstance(content, dict):
                    return json.dumps(content, ensure_ascii=False, indent=2)

                # 其他情况直接转换为字符串
                return str(content)

            # 如果没有标准的result.content结构，检查其他可能的字段
            if "result" in results:
                result = results["result"]
                if isinstance(result, str):
                    return result
                if isinstance(result, dict):
                    return json.dumps(result, ensure_ascii=False, indent=2)

            # 如果都没有，返回整个结果
            return json.dumps(results, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"格式化搜索结果失败: {e}")
            return f"搜索结果格式化失败: {str(e)}"

    def _filter_search_content(self, content: str, include_url: bool = False) -> str:
        """
        过滤搜索结果内容，只保留标题、URL和站点名称

        Args:
            content: 原始搜索结果内容
            include_url: 是否包含URL

        Returns:
            过滤后的搜索结果内容
        """
        try:
            # 按行分割内容
            lines = content.split('\n')
            filtered_lines = []
            allowed_prefixes = ("标题：", "站点名称：")
            if include_url:
                allowed_prefixes = ("标题：", "URL：", "站点名称：")

            for raw_line in lines:
                line = raw_line.strip()

                # 保留空行用于分隔
                if not line:
                    filtered_lines.append("")
                    continue

                # 保留标题
                if line.startswith("# 搜索结果"):
                    filtered_lines.append(line)
                    continue

                # 保留指定字段
                if line.startswith(allowed_prefixes):
                    filtered_lines.append(line)
                    continue

                # 保留分隔符（只由-组成）
                if set(line) <= {"-"}:
                    filtered_lines.append(line)
                    continue

            # 去除首尾空行
            filtered_text = '\n'.join(filtered_lines).strip()
            return filtered_text

        except Exception as e:
            logger.error(f"过滤搜索内容失败: {e}")
            return content  # 如果过滤失败，返回原始内容

    def run(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """
        执行网页搜索

        Args:
            query: 搜索关键词
            max_results: 最大结果数量，默认为3

        Returns:
            搜索结果字典
        """
        try:
            # 调用MCP客户端进行网页搜索
            result = self.mcp_client.call_tool(
                tool_name="web-search",
                method="common_search",
                arguments={
                    "query": query,
                    "max_results": max_results
                }
            )

            if result is None:
                return {
                    "status": "error",
                    "error": "搜索失败，可能是网络错误或服务不可用",
                    "message": "网页搜索失败"
                }

            # 格式化搜索结果
            formatted_results = self.format_search_results(result)

            # 过滤搜索内容，删除正文部分
            filtered_results = self._filter_search_content(formatted_results)

            logger.info(f"网页搜索查询: {query}, 结果数量: {max_results}")
            logger.debug(f"搜索结果: {formatted_results}")

            # 返回搜索结果
            return {
                "status": "success",
                "data": formatted_results,
                "filtered_data": filtered_results,
                "message": f"成功搜索'{query}'"
            }

        except Exception as e:
            logger.error(f"网页搜索失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "网页搜索失败"
            }




def main():
    """测试工具执行"""
    tool = QuarkWebSearchTool()

    # 测试网页搜索
    result = tool.run(query="月坛学区", max_results=3)
    print("网页搜索结果:", json.dumps(result, ensure_ascii=False, indent=2))

    # 测试获取schema
    schema = tool.get_schema()
    print("\n工具Schema:", json.dumps(schema, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
