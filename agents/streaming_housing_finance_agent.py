"""
支持流式输出的购房资金方案生成助手

基于 HousingFinanceAgent，增加了流式输出支持，可以实时推送：
- 工具调用事件
- 工具执行结果
- 最终回复（支持流式生成）
"""
import json
import uuid
from typing import Dict, Any, Optional, AsyncIterator
from pathlib import Path
from loguru import logger
from openai import OpenAI
import os
from dotenv import load_dotenv
from enum import Enum


class StreamEventType(str, Enum):
    """流式事件类型"""
    THINKING = "thinking"           # Agent 正在思考
    TOOL_CALL = "tool_call"         # 开始调用工具
    TOOL_RESULT = "tool_result"     # 工具返回结果
    RESPONSE_START = "response_start"  # 开始生成回复
    RESPONSE_CHUNK = "response_chunk"  # 回复片段
    RESPONSE_END = "response_end"   # 回复结束
    ERROR = "error"                 # 错误
    DONE = "done"                   # 完成


class StreamingHousingFinanceAgent:
    """
    支持流式输出的购房资金方案生成助手。

    相比 HousingFinanceAgent，这个版本支持：
    1. 实时推送工具调用事件
    2. 实时推送工具执行结果
    3. 流式生成最终回复
    """

    def __init__(self, tools: Dict[str, Any] = None):
        """
        初始化购房助手。

        Args:
            tools: 工具字典，key 为工具名，value 为工具实例
        """
        # 加载环境变量
        load_dotenv()

        # 初始化 OpenAI 客户端
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_API_BASE_URL')

        if not api_key:
            raise ValueError("必须设置 OPENAI_API_KEY 环境变量")

        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            logger.info(f"使用自定义 API 端点: {base_url}")
        else:
            self.client = OpenAI(api_key=api_key)

        # 设置模型
        self.model = os.getenv('OPENAI_MODEL', 'Qwen3-Max')

        # 工具管理
        self.tools = tools or {}
        self.tool_schemas = self._build_tool_schemas()

        # 会话管理
        self.conversation_id = None
        self.session_user_id = f"user_{uuid.uuid4().hex[:8]}"

        logger.info(f"StreamingHousingFinanceAgent 初始化完成")
        logger.info(f"- 模型: {self.model}")
        logger.info(f"- 工具数量: {len(self.tools)}")

    def _build_tool_schemas(self):
        """构建工具 schemas"""
        schemas = []
        for tool_name, tool_instance in self.tools.items():
            if hasattr(tool_instance, 'get_schema'):
                schema = tool_instance.get_schema()
                schemas.append(schema)
        return schemas

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """
你是一位资深的购房顾问，专注于为客户生成通俗易懂、专业准确的购房资金方案。

## 你的角色定位

1. **客观中立**：不推销产品，基于政策和数据提供建议
2. **通俗易懂**：将复杂的政策法规转化为"人话"，像和朋友聊天一样解释
3. **结构清晰**：工作流程有序，信息完整
4. **专业准确**：基于真实政策和精确计算

## 你的工作流程

当用户提出购房需求时，你需要按以下步骤进行：

### 第一步：理解用户需求
从用户描述中提取关键信息：区域、身份、购房需求、预算、贷款方式等。

### 第二步：查询相关政策
使用 **trading_knowledge_retriever** 工具查询限购、贷款、公积金、税费等政策。
如果知识库信息不够新，使用 **quark_web_search** 补充最新政策。

### 第三步：计算购房成本
如果用户提供了完整的房屋信息，使用 **trade_cost_calculate** 工具计算精确成本。

### 第四步：生成方案报告
使用 **report_generator** 工具生成完整报告。

## 重要注意事项

1. **工具调用顺序**：先查政策 → 再算成本 → 最后生成报告
2. **数据传递**：确保传递给工具的数据格式正确
3. **用户体验**：如果信息不足，友好地询问用户
4. **专业性**：基于真实政策，不要编造

现在，请根据用户的需求，按照上述流程工作！
""".strip()

    async def stream_run(
        self,
        user_message: str,
        max_iterations: int = 15,
        conversation_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式运行 Agent，实时推送事件。

        Args:
            user_message: 用户消息
            max_iterations: 最大迭代次数
            conversation_id: 会话 ID

        Yields:
            事件字典，包含 type 和 data 字段
        """
        logger.info("=" * 80)
        logger.info("开始流式处理用户请求")
        logger.info(f"用户消息: {user_message}")

        # 更新会话 ID
        if conversation_id:
            self.conversation_id = conversation_id
        elif not self.conversation_id:
            self.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"

        logger.info(f"会话 ID: {self.conversation_id}")

        # 推送思考事件
        yield {
            "type": StreamEventType.THINKING,
            "data": {
                "message": "正在理解您的需求...",
                "conversation_id": self.conversation_id
            }
        }

        # 初始化消息历史
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_message}
        ]

        # 迭代执行
        iteration = 0
        final_response = None

        try:
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"\n--- 迭代 {iteration} ---")

                # 推送迭代信息
                yield {
                    "type": StreamEventType.THINKING,
                    "data": {
                        "message": f"正在处理... (第 {iteration} 步)",
                        "iteration": iteration
                    }
                }

                # 调用 OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tool_schemas if self.tool_schemas else None,
                    tool_choice="auto"
                )

                response_message = response.choices[0].message

                # 检查是否需要调用工具
                if response_message.tool_calls:
                    logger.info(f"需要调用 {len(response_message.tool_calls)} 个工具")

                    # 将 assistant 的消息添加到历史
                    messages.append({
                        "role": "assistant",
                        "content": response_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in response_message.tool_calls
                        ]
                    })

                    # 执行工具调用
                    for tool_call in response_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args_str = tool_call.function.arguments

                        try:
                            tool_args = json.loads(tool_args_str)
                        except json.JSONDecodeError:
                            tool_args = {}

                        # 推送工具调用事件
                        yield {
                            "type": StreamEventType.TOOL_CALL,
                            "data": {
                                "tool_name": tool_name,
                                "tool_args": tool_args,
                                "message": f"正在调用 {tool_name}..."
                            }
                        }

                        logger.info(f"调用工具: {tool_name}")
                        logger.debug(f"参数: {json.dumps(tool_args, ensure_ascii=False)}")

                        # 执行工具
                        tool_result = self._execute_tool(tool_name, tool_args)

                        logger.info(f"工具返回: {type(tool_result)}")

                        # 推送工具结果事件
                        yield {
                            "type": StreamEventType.TOOL_RESULT,
                            "data": {
                                "tool_name": tool_name,
                                "result": tool_result,
                                "message": f"{tool_name} 执行完成"
                            }
                        }

                        # 将工具结果添加到消息历史
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })

                else:
                    # 没有工具调用，说明得到最终回复
                    final_response = response_message.content
                    logger.info("得到最终回复")
                    break

            if iteration >= max_iterations:
                logger.warning(f"达到最大迭代次数 {max_iterations}")
                final_response = "抱歉，处理时间过长，请稍后重试或简化您的问题。"

            # 推送回复开始事件
            yield {
                "type": StreamEventType.RESPONSE_START,
                "data": {
                    "message": "开始生成回复...",
                    "iterations": iteration
                }
            }

            # 流式推送最终回复（模拟流式输出）
            if final_response:
                # 将回复按句子分割
                sentences = final_response.split('\n')
                for sentence in sentences:
                    if sentence.strip():
                        yield {
                            "type": StreamEventType.RESPONSE_CHUNK,
                            "data": {
                                "content": sentence + '\n'
                            }
                        }

            # 推送回复结束事件
            yield {
                "type": StreamEventType.RESPONSE_END,
                "data": {
                    "message": "回复生成完成",
                    "full_response": final_response
                }
            }

            # 推送完成事件
            yield {
                "type": StreamEventType.DONE,
                "data": {
                    "status": "success",
                    "iterations": iteration,
                    "conversation_id": self.conversation_id,
                    "user_id": self.session_user_id
                }
            }

            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Agent 执行失败: {str(e)}")
            logger.exception(e)

            # 推送错误事件
            yield {
                "type": StreamEventType.ERROR,
                "data": {
                    "error": str(e),
                    "message": "处理失败，请稍后重试"
                }
            }

            # 推送完成事件
            yield {
                "type": StreamEventType.DONE,
                "data": {
                    "status": "error",
                    "iterations": iteration,
                    "conversation_id": self.conversation_id
                }
            }

    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """
        执行指定的工具。

        Args:
            tool_name: 工具名称
            tool_args: 工具参数

        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            error_msg = f"工具 {tool_name} 不存在"
            logger.error(error_msg)
            return {"error": error_msg}

        tool_instance = self.tools[tool_name]

        try:
            # 为知识检索工具自动添加必要参数
            if tool_name == "trading_knowledge_retriever":
                if "source" not in tool_args:
                    tool_args["source"] = "housing_finance_api"
                if "user" not in tool_args:
                    tool_args["user"] = self.session_user_id
                if "conversation_id" not in tool_args and self.conversation_id:
                    tool_args["conversation_id"] = self.conversation_id

            # 执行工具
            result = tool_instance.run(**tool_args)
            return result

        except Exception as e:
            error_msg = f"工具 {tool_name} 执行失败: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            return {"error": error_msg}

    def reset_conversation(self):
        """重置会话，开始新的对话。"""
        self.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        logger.info(f"重置会话，新会话 ID: {self.conversation_id}")
