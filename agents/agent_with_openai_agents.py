"""
使用 openai-agents 库实现的Agent。

openai-agents 是OpenAI官方的Agent框架，使用起来更简单。
"""
from typing import Dict, Any
from loguru import logger


class HousingFinanceAgent:
    """
    购房资金方案生成Agent。

    使用 openai-agents 库实现。
    """

    def __init__(self, tools: Dict[str, Any] = None):
        """
        初始化Agent。

        Args:
            tools: 工具字典
        """
        try:
            from openai_agents import Agent, function_tool
        except ImportError:
            raise ImportError(
                "请安装 openai-agents: pip install openai-agents==0.2.3"
            )

        self.tools = tools or {}
        self.agent = None

        logger.info(f"HousingFinanceAgent初始化，加载了{len(self.tools)}个工具")

    def setup_agent(self, system_prompt: str = None):
        """
        设置Agent。

        Args:
            system_prompt: 系统提示词
        """
        from openai_agents import Agent

        if not system_prompt:
            system_prompt = self._get_default_prompt()

        # 将工具转换为openai-agents格式
        agent_tools = self._convert_tools()

        # 创建agent
        self.agent = Agent(
            model="gpt-4-turbo-preview",
            instructions=system_prompt,
            tools=agent_tools
        )

        logger.info("Agent设置完成")

    def run(self, user_message: str) -> Dict[str, Any]:
        """
        运行Agent。

        Args:
            user_message: 用户消息

        Returns:
            Agent的回复
        """
        if not self.agent:
            self.setup_agent()

        logger.info("开始处理用户请求")

        try:
            # 运行agent
            response = self.agent.run(user_message)

            logger.info("Agent执行完成")
            return {
                "status": "success",
                "content": response.content,
                "tool_calls": response.tool_calls if hasattr(response, 'tool_calls') else []
            }

        except Exception as e:
            logger.error(f"执行出错: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _convert_tools(self) -> list:
        """
        将工具转换为openai-agents格式。

        Returns:
            openai-agents格式的工具列表
        """
        from openai_agents import function_tool

        agent_tools = []

        for tool_name, tool_instance in self.tools.items():
            # 获取工具的schema
            if hasattr(tool_instance, 'get_schema'):
                schema = tool_instance.get_schema()

                # 创建function_tool
                @function_tool(
                    name=schema['function']['name'],
                    description=schema['function']['description'],
                    parameters=schema['function']['parameters']
                )
                def tool_func(**kwargs):
                    return tool_instance.run(**kwargs)

                agent_tools.append(tool_func)

        return agent_tools

    def _get_default_prompt(self) -> str:
        """获取默认的系统提示词。"""
        return """
你是一个专业的购房资金方案助手。

你的角色：
1. 客观中立 - 不推销产品，基于政策和用户需求提供建议
2. 通俗易懂 - 将复杂政策转化为"人话"
3. 结构清晰 - 输出有明确的模块划分

你需要帮助用户：
- 理解适用的购房政策（限购、贷款、税费）
- 计算精确的资金方案（首付、月供、税费）
- 规划办理步骤

工作流程：
1. 先调用 policy_lookup 查询相关政策
2. 再调用 cost_calculator 计算具体成本
3. 最后用通俗语言总结方案

回复风格：
- 避免法律术语
- 多用场景化例子
- 突出关键数字和注意事项
""".strip()
