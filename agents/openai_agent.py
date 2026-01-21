"""
OpenAI Function Calling Agent.

使用OpenAI的function calling实现的Agent。
"""
from typing import Dict, Any, List, Optional
from loguru import logger
import json


class OpenAIAgent:
    """
    基于OpenAI Function Calling的Agent。

    工作流程：
    1. 收集所有工具的schema
    2. 将用户请求 + 工具schema 发送给OpenAI
    3. OpenAI返回要调用的工具和参数
    4. 执行工具，将结果返回给OpenAI
    5. OpenAI生成最终答案
    """

    def __init__(
        self,
        tools: Dict[str, Any],
        api_key: str = None,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7
    ):
        """
        初始化Agent。

        Args:
            tools: 工具字典 {tool_name: tool_instance}
            api_key: OpenAI API密钥
            model: 使用的模型
            temperature: 温度参数
        """
        self.tools = tools
        self.model = model
        self.temperature = temperature

        # 初始化OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        except ImportError:
            raise ImportError("请安装openai: pip install openai")

        # 收集工具schema
        self.tools_schema = self._build_tools_schema()

        logger.info(f"OpenAIAgent初始化完成，加载了{len(self.tools)}个工具")

    def _build_tools_schema(self) -> List[Dict[str, Any]]:
        """构建所有工具的schema列表。"""
        schemas = []
        for tool_name, tool_instance in self.tools.items():
            if hasattr(tool_instance, 'get_schema'):
                schema = tool_instance.get_schema()
                schemas.append(schema)
                logger.debug(f"已加载工具: {tool_name}")
        return schemas

    def run(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        运行Agent处理用户请求。

        Args:
            user_message: 用户消息
            system_prompt: 系统提示词（可选）
            max_iterations: 最大迭代次数

        Returns:
            包含最终答案的字典
        """
        logger.info("开始处理用户请求")

        # 构建消息历史
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"迭代 {iteration}/{max_iterations}")

            try:
                # 调用OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools_schema,  # 传入工具schema
                    tool_choice="auto",
                    temperature=self.temperature
                )

                message = response.choices[0].message

                # 检查是否要调用工具
                if message.tool_calls:
                    logger.info(f"LLM请求调用 {len(message.tool_calls)} 个工具")

                    # 将assistant消息添加到历史
                    messages.append(message)

                    # 执行所有工具调用
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        logger.info(f"调用工具: {tool_name}")
                        logger.debug(f"参数: {tool_args}")

                        # 执行工具
                        tool_result = self._execute_tool(tool_name, tool_args)

                        # 将工具结果添加到消息历史
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })

                    # 继续循环，让LLM处理工具结果
                    continue

                else:
                    # LLM返回最终答案
                    logger.info("Agent完成执行")
                    return {
                        "status": "success",
                        "content": message.content,
                        "iterations": iteration,
                        "usage": {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens
                        }
                    }

            except Exception as e:
                logger.error(f"执行出错: {str(e)}")
                return {
                    "status": "error",
                    "error": str(e),
                    "iterations": iteration
                }

        # 达到最大迭代次数
        logger.warning(f"达到最大迭代次数 {max_iterations}")
        return {
            "status": "max_iterations",
            "message": "达到最大迭代次数",
            "iterations": max_iterations
        }

    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """
        执行指定工具。

        Args:
            tool_name: 工具名称
            tool_args: 工具参数

        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            error_msg = f"工具不存在: {tool_name}"
            logger.error(error_msg)
            return {"error": error_msg}

        tool = self.tools[tool_name]

        try:
            # 调用工具的run方法
            result = tool.run(**tool_args)
            logger.info(f"工具 {tool_name} 执行成功")
            return result

        except Exception as e:
            error_msg = f"工具执行出错: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_tools_info(self) -> str:
        """获取所有工具的信息（用于调试）。"""
        info = "可用工具列表:\n"
        for i, schema in enumerate(self.tools_schema, 1):
            func = schema["function"]
            info += f"{i}. {func['name']}: {func['description']}\n"
        return info
