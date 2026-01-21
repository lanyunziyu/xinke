#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页搜索工具

集成网页搜索功能，用于在线搜索相关信息
"""
import json
from typing import Dict, Any, Union
import logging
import uuid

from app.core.tools.base_tool import BaseTool, ToolExecuteResult, ToolStatus, tool_execute, auto_register_tool
from app.utils.mcp_client import MCPClient

logger = logging.getLogger(__name__)


@auto_register_tool
class QuarkWebSearchTool(BaseTool):
    """
    网页搜索工具

    用于在线搜索相关信息，支持指定最大结果数量
    """

    def __init__(self):
        super().__init__(
            tool_code="quark_web_search",
            tool_name="网页搜索工具",
            description="用于在线搜索相关信息，支持指定最大结果数量"
        )
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

    def _build_model_data(
                self,
                preview: str,
                resource_id: str,
                max_preview_length: int = 400
        ) -> str:
        """
        构建给模型查看的精简文本
        """
        if not preview:
            preview = "搜索结果为空或已被过滤"

        if len(preview) > max_preview_length:
            preview = preview[:max_preview_length] + "...(已截断)"

        result = ToolExecuteResult(
            status=ToolStatus.SUCCESS,
            data=preview,
            message=(
                f"网页搜索成功，包含网页内容的完整结果放在资源ID:{resource_id}"
            ),
            tool_code=self.tool_code
        )
        result_dict = result.to_dict()
        keys_to_remove = ["error", "request_id", "model_data", "resource_data", "execution_time", "tool_code"]
        for key in keys_to_remove:
            result_dict.pop(key, None)

        return json.dumps(result_dict, ensure_ascii=False)


    @tool_execute(validate_params=True, log_execution=True)
    def execute(self, **kwargs) -> Union[Any, ToolExecuteResult]:
        """
        执行网页搜索

        Args:
            query (str): 搜索关键词
            max_results (int): 最大结果数量，默认为3

        Returns:
            ToolExecuteResult: 搜索结果
        """
        query = kwargs.get('query', '')
        max_results = kwargs.get('max_results', 3)
        request_id = kwargs.get('request_id', str(uuid.uuid4()))

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
                return ToolExecuteResult(
                    status=ToolStatus.ERROR,
                    error="搜索失败，可能是网络错误或服务不可用",
                    message="网页搜索失败"
                )
            # 格式化搜索结果
            formatted_results = self.format_search_results(result)

            # 保存原始结果到上下文
            conversation_id = self.get_conversation_id(**kwargs)
            resource_id = self.set_context(conversation_id, f"web_search_result", result)
            # 过滤搜索内容，删除*正文*部分
            filter_results = self._filter_search_content(formatted_results)
            model_data = self._build_model_data(
                preview=filter_results,
                resource_id=resource_id
            )

            logger.info(f"网页搜索查询: {query}, 结果数量: {max_results}")
            logger.debug(f"搜索结果: {formatted_results}")

            # 返回搜索结果
            return ToolExecuteResult(
                status=ToolStatus.SUCCESS,
                data=formatted_results,
                model_data=model_data,
                message=f"成功搜索'{query}', 该工具返回的完整结果（含正文）的资源ID: {resource_id}"
            )

        except ValueError as ve:
            logger.error(f"网页搜索参数错误: {str(ve)}, request_id: {request_id}")
            return ToolExecuteResult(
                status=ToolStatus.INVALID_PARAMS,
                error=str(ve),
                message="参数验证失败"
            )
        except Exception as e:
            logger.error(f"网页搜索失败: {str(e)}, request_id: {request_id}")
            return ToolExecuteResult(
                status=ToolStatus.ERROR,
                error=str(e),
                message="网页搜索失败"
            )


    def get_tool_schema(self) -> Dict[str, Any]:
        """
        获取工具的schema定义

        Returns:
            Dict[str, Any]: OpenAI Function Calling格式的schema
        """
        return {
            "type": "function",
            "function": {
                "name": self.tool_code,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "最大结果数量，默认为3",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        }

    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """
        参数验证

        Args:
            **kwargs: 需要验证的参数

        Returns:
            Dict[str, Any]: 验证结果
        """
        query = kwargs.get('query', '')
        max_results = kwargs.get('max_results', 3)

        # 验证 query
        if not isinstance(query, str) or not query.strip():
            return {
                "valid": False,
                "error": "query 必须是非空字符串"
            }

        # 验证 max_results
        if not isinstance(max_results, int) or max_results < 1 or max_results > 10:
            return {
                "valid": False,
                "error": "max_results 必须是1到10之间的整数"
            }

        return {"valid": True}




def main():
    # 示例执行
    tool = QuarkWebSearchTool()

    # 测试网页搜索
    result = tool.execute(
        query="月坛学区",
        max_results=3
    )
    print("网页搜索结果:", result)


if __name__ == "__main__":
    main()
