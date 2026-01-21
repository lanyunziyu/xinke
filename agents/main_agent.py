"""
Main Agent (方案生成 Agent)

This is the orchestrator agent that coordinates all tools to generate
personalized housing finance solutions.
"""
from typing import Dict, Any, List
from loguru import logger


class MainAgent:
    """
    Main Agent for generating housing finance solutions.

    This agent orchestrates the workflow:
    1. Receives user profile and requirements
    2. Calls Policy Lookup to fetch relevant policies
    3. Calls Cost Calculator to compute financial breakdown
    4. Calls Report Generator to produce final structured report
    """

    def __init__(self, tools: Dict[str, Any] = None):
        """
        Initialize the Main Agent.

        Args:
            tools: Dictionary of tool instances
                - policy_lookup: PolicyLookupTool instance
                - cost_calculator: CostCalculatorTool instance
                - report_generator: ReportGeneratorTool instance
        """
        self.tools = tools or {}
        self.conversation_history: List[Dict[str, str]] = []
        logger.info("MainAgent initialized")

    def run(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.

        Args:
            user_profile: Dictionary containing:
                - identity_info: 身份特征 (京籍/非京籍, 婚姻状况等)
                - residence_status: 居住现状 (名下房产情况)
                - purchase_needs: 购房需求 (首套/二套等)
                - budget: 购房预算
                - core_requirements: 核心需求 (贷款方式偏好等)
                - location: 意向区域

        Returns:
            Dictionary containing the complete housing finance solution:
                - policy_interpretation: "人话版"政策解读
                - cost_breakdown: 结构化成本清单
                - action_steps: 办理步骤清单
                - summary: 智能服务小结
        """
        logger.info(f"Processing user profile: {user_profile}")

        # TODO: Implement main agent logic
        # Step 1: Extract user requirements and validate input

        # Step 2: Call Policy Lookup tool
        # policies = self.tools['policy_lookup'].lookup(user_profile)

        # Step 3: Call Cost Calculator tool
        # cost_breakdown = self.tools['cost_calculator'].calculate(user_profile, policies)

        # Step 4: Call Report Generator tool
        # report = self.tools['report_generator'].generate(user_profile, policies, cost_breakdown)

        # Step 5: Return structured response
        return {
            "status": "success",
            "user_profile": user_profile,
            "solution": {
                "policy_interpretation": "TODO: 政策解读",
                "cost_breakdown": "TODO: 成本清单",
                "action_steps": "TODO: 步骤清单",
                "summary": "TODO: 服务小结",
            }
        }

    def _validate_user_profile(self, user_profile: Dict[str, Any]) -> bool:
        """
        Validate user profile input.

        Args:
            user_profile: User profile dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "identity_info",
            "residence_status",
            "purchase_needs",
            "budget",
        ]

        # TODO: Implement validation logic
        return True

    def _create_system_prompt(self) -> str:
        """
        Create system prompt for the agent.

        Returns:
            System prompt string defining agent behavior
        """
        prompt = """
        你是一个专业的购房资金方案生成助手。你的角色定位是：

        1. 客观中立：不推销任何产品，仅基于政策和用户需求提供建议
        2. 通俗易懂：将复杂的政策法规转化为"人话"，像经纪人一样解释
        3. 结构清晰：输出的方案要有明确的模块划分，便于客户理解和执行

        你需要帮助用户：
        - 理解适用的购房政策（限购、贷款、税费等）
        - 计算精确的资金方案（首付、月供、税费明细）
        - 规划清晰的办理步骤（贷款申请、户口迁出等流程）

        回复风格：
        - 避免使用晦涩的法律术语
        - 多用场景化的例子说明
        - 突出关键数字和重点注意事项
        """
        return prompt.strip()
