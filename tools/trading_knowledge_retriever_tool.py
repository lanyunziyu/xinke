#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易知识检索工具

专业的房地产二手交易知识检索工具,提供全面的房产知识、交易流程、
政策法规等多维度信息。支持多轮对话和上下文管理。
"""
import json
from typing import Dict, Any, Optional, List
import logging

from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from services.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class TradingKnowledgeRetrieverArgs(BaseModel):
    """交易知识检索工具参数模型"""

    # 必填参数
    query: str = Field(..., description="用户问题,例如:北京二手房交易流程是什么?")
    source: str = Field(..., description="调用方来源标识,用于追踪和统计")
    user: str = Field(
        ...,
        description="用户标识,用于定义终端用户身份,需保证在应用内唯一"
    )

    # 可选参数
    topk: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="知识库检索相似度,返回top k个相关结果,默认5"
    )
    dialogue_context: Optional[str] = Field(
        None,
        description="对话上下文信息,JSON字符串格式,包含历史对话"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="会话ID,用于多轮对话上下文管理。如需基于之前的聊天记录继续对话,必须传入之前的conversation_id"
    )


class TradingKnowledgeRetrieverTool(BaseTool):
    """交易知识检索工具

    专业的房地产二手交易知识检索工具,提供全面的房产知识、交易流程、
    政策法规等多维度信息。支持多轮对话和上下文管理。
    """

    name: str = "trading_knowledge_retriever"
    description: str = (
        "专业的房地产二手交易知识检索工具,提供房产知识、交易流程、"
        "政策法规等信息。支持多轮对话和上下文理解。"
    )
    args_schema: type[BaseModel] = TradingKnowledgeRetrieverArgs

    def __init__(self):
        super().__init__()
        self.mcp_client = MCPClient()
        # 会话管理字典,存储会话ID和上下文
        self.conversation_contexts: Dict[str, List[Dict[str, str]]] = {}

    def _build_dialogue_context(
        self,
        conversation_id: Optional[str],
        current_query: str,
        dialogue_context: Optional[str] = None
    ) -> Optional[str]:
        """
        构建对话上下文

        Args:
            conversation_id: 会话ID
            current_query: 当前查询
            dialogue_context: 外部传入的对话上下文

        Returns:
            格式化的对话上下文JSON字符串
        """
        try:
            # 如果外部已提供对话上下文,直接使用
            if dialogue_context:
                return dialogue_context

            # 如果有conversation_id且本地有历史记录,使用本地上下文
            if conversation_id and conversation_id in self.conversation_contexts:
                context = self.conversation_contexts[conversation_id]
                return json.dumps(context, ensure_ascii=False)

            return None

        except Exception as e:
            logger.warning(f"构建对话上下文失败: {e}")
            return None

    def _update_conversation_context(
        self,
        conversation_id: str,
        query: str,
        response: str
    ) -> None:
        """
        更新会话上下文

        Args:
            conversation_id: 会话ID
            query: 用户查询
            response: 系统响应
        """
        try:
            if conversation_id not in self.conversation_contexts:
                self.conversation_contexts[conversation_id] = []

            # 添加当前对话轮次
            self.conversation_contexts[conversation_id].append({
                "role": "user",
                "content": query
            })
            self.conversation_contexts[conversation_id].append({
                "role": "assistant",
                "content": response
            })

            # 保持最近10轮对话(20条消息)
            max_messages = 20
            if len(self.conversation_contexts[conversation_id]) > max_messages:
                self.conversation_contexts[conversation_id] = \
                    self.conversation_contexts[conversation_id][-max_messages:]

        except Exception as e:
            logger.warning(f"更新会话上下文失败: {e}")

    def _clean_arguments(self, **kwargs) -> Dict[str, Any]:
        """清理参数,移除None值"""
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

                # 处理content列表
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]

                    if isinstance(first_item, dict) and "text" in first_item:
                        text_content = first_item["text"]
                        # 尝试解析JSON
                        try:
                            data = json.loads(text_content)
                            return {
                                "status": "success",
                                "data": data,
                                "message": "知识检索成功"
                            }
                        except json.JSONDecodeError:
                            # 如果不是JSON,直接返回文本
                            return {
                                "status": "success",
                                "data": {
                                    "answer": text_content
                                },
                                "message": "知识检索成功"
                            }

                    if isinstance(first_item, dict):
                        for field in ["content", "data", "result", "message", "answer"]:
                            if field in first_item:
                                return {
                                    "status": "success",
                                    "data": {
                                        "answer": first_item[field]
                                    },
                                    "message": "知识检索成功"
                                }
                        return {
                            "status": "success",
                            "data": first_item,
                            "message": "知识检索成功"
                        }

                    if isinstance(first_item, str):
                        return {
                            "status": "success",
                            "data": {
                                "answer": first_item
                            },
                            "message": "知识检索成功"
                        }

                # 如果content是字典
                if isinstance(content, dict):
                    return {
                        "status": "success",
                        "data": content,
                        "message": "知识检索成功"
                    }

                # 如果content是字符串
                if isinstance(content, str):
                    return {
                        "status": "success",
                        "data": {
                            "answer": content
                        },
                        "message": "知识检索成功"
                    }

                return {
                    "status": "success",
                    "data": {
                        "answer": str(content)
                    },
                    "message": "知识检索成功"
                }

            # 如果没有标准的result.content结构,检查其他可能的字段
            if "result" in result:
                result_data = result["result"]
                if isinstance(result_data, str):
                    return {
                        "status": "success",
                        "data": {
                            "answer": result_data
                        },
                        "message": "知识检索成功"
                    }
                if isinstance(result_data, dict):
                    return {
                        "status": "success",
                        "data": result_data,
                        "message": "知识检索成功"
                    }

            # 兜底返回
            return {
                "status": "success",
                "data": result,
                "message": "知识检索完成"
            }

        except Exception as e:
            logger.error(f"格式化知识检索结果失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "结果格式化失败"
            }

    def run(
        self,
        query: str,
        source: str,
        user: str,
        topk: Optional[int] = 5,
        dialogue_context: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行交易知识检索

        Args:
            query: 用户问题
            source: 调用方来源标识
            user: 用户标识
            topk: 检索结果数量
            dialogue_context: 对话上下文
            conversation_id: 会话ID

        Returns:
            知识检索结果字典
        """
        try:
            logger.info(f"执行交易知识检索,用户:{user},问题:{query}")

            # 构建对话上下文
            built_context = self._build_dialogue_context(
                conversation_id, query, dialogue_context
            )

            # 准备参数 (注意: topk参数类型是string)
            arguments = {
                "query": query,
                "source": source,
                "user": user,
                "topk": str(topk) if topk else "5"
            }

            # 添加可选参数
            if built_context:
                arguments["dialogue_context"] = built_context
            if conversation_id:
                arguments["conversation_id"] = conversation_id

            # 调用MCP服务
            result = self.mcp_client.call_tool(
                tool_name="xiaoyi-knowledge-search",
                method="trading_knowledge_retriever",
                arguments=arguments
            )

            if result is None:
                return {
                    "status": "error",
                    "error": "MCP服务无响应",
                    "message": "知识检索失败"
                }

            # 格式化返回结果
            formatted_result = self._format_result(result)

            # 更新会话上下文
            if conversation_id and formatted_result["status"] == "success":
                response_text = ""
                if isinstance(formatted_result["data"], dict):
                    response_text = formatted_result["data"].get("answer", "")
                    if not response_text:
                        # 尝试其他可能的字段
                        response_text = str(formatted_result["data"])
                elif isinstance(formatted_result["data"], str):
                    response_text = formatted_result["data"]

                if response_text:
                    self._update_conversation_context(
                        conversation_id, query, response_text
                    )

            logger.info(f"交易知识检索完成,用户:{user}")
            return formatted_result

        except Exception as e:
            logger.error(f"交易知识检索失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "知识检索失败"
            }


def main():
    """测试工具执行"""
    tool = TradingKnowledgeRetrieverTool()

    # 测试用例1: 单轮问答
    print("=== 测试单轮问答 ===")
    result = tool.run(
        query="北京二手房交易需要哪些税费?",
        source="test_app",
        user="test_user_001",
        topk=5
    )
    print("单轮问答结果:", json.dumps(result, ensure_ascii=False, indent=2))

    # 测试用例2: 多轮对话
    print("\n=== 测试多轮对话 ===")
    conv_id = "conv_001"

    # 第一轮
    print("\n第一轮对话:")
    result1 = tool.run(
        query="什么是满五唯一?",
        source="test_app",
        user="test_user_001",
        conversation_id=conv_id,
        topk=3
    )
    print("结果:", json.dumps(result1, ensure_ascii=False, indent=2))

    # 第二轮(基于上下文)
    print("\n第二轮对话(基于上下文):")
    result2 = tool.run(
        query="它有什么税费优惠?",
        source="test_app",
        user="test_user_001",
        conversation_id=conv_id,
        topk=3
    )
    print("结果:", json.dumps(result2, ensure_ascii=False, indent=2))

    # 测试获取schema
    print("\n=== 工具Schema ===")
    schema = tool.get_schema()
    print(json.dumps(schema, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
