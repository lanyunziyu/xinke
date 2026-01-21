"""
简单示例：展示OpenAI Agent的完整使用流程。
"""
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from agents.openai_agent import OpenAIAgent
from loguru import logger


# ============================================================================
# 1. 定义工具的输入schema (使用Pydantic)
# ============================================================================

class PolicyLookupInput(BaseModel):
    """政策查询工具的输入参数。"""
    location: str = Field(description="购房区域，如：朝阳、海淀")
    buyer_type: str = Field(description="购房者类型，如：京籍首套、非京籍")


class CostCalculatorInput(BaseModel):
    """成本计算工具的输入参数。"""
    total_price: float = Field(description="房屋总价，单位：元")
    is_first_home: bool = Field(description="是否首套房")
    loan_type: str = Field(default="combination", description="贷款类型: commercial/provident_fund/combination")


# ============================================================================
# 2. 实现具体的工具类
# ============================================================================

class PolicyLookupTool(BaseTool):
    """政策查询工具 - 根据区域和购房者类型查询相关政策。"""

    name = "policy_lookup"
    description = "查询购房相关政策，包括限购政策、贷款政策、税费政策等"
    args_schema = PolicyLookupInput

    def run(self, location: str, buyer_type: str) -> dict:
        """执行政策查询。"""
        logger.info(f"查询政策: location={location}, buyer_type={buyer_type}")

        # TODO: 这里应该是真实的政策查询逻辑
        # 可以从数据库、向量数据库或API查询

        return {
            "location": location,
            "buyer_type": buyer_type,
            "policies": {
                "限购政策": f"{location}区域，{buyer_type}购房者可以购买住宅",
                "贷款政策": "首套房商贷最低首付30%，公积金最低首付20%",
                "组合贷说明": "可以申请组合贷，先申请公积金贷款，不足部分用商贷补充",
                "税费政策": "首套房90平以下契税1%，90-140平契税1.5%"
            }
        }


class CostCalculatorTool(BaseTool):
    """成本计算工具 - 计算购房总成本，包括首付、贷款、税费等。"""

    name = "cost_calculator"
    description = "计算购房成本，包括首付、贷款金额、月供、税费等详细费用"
    args_schema = CostCalculatorInput

    def run(self, total_price: float, is_first_home: bool, loan_type: str = "combination") -> dict:
        """执行成本计算。"""
        logger.info(f"计算成本: total_price={total_price}, is_first_home={is_first_home}")

        # TODO: 这里是真实的计算逻辑
        # 根据政策计算首付、贷款、月供等

        # 简单示例计算
        down_payment_ratio = 0.3 if is_first_home else 0.4
        down_payment = total_price * down_payment_ratio
        loan_amount = total_price - down_payment

        # 假设利率和30年贷款
        annual_rate = 0.0365  # 3.65%
        months = 360
        monthly_rate = annual_rate / 12
        monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)

        # 税费计算（简化）
        deed_tax = total_price * 0.01  # 假设1%契税

        return {
            "房屋总价": f"{total_price:,.0f}元",
            "首付金额": f"{down_payment:,.0f}元 ({down_payment_ratio*100}%)",
            "贷款金额": f"{loan_amount:,.0f}元",
            "贷款方式": loan_type,
            "月供金额": f"{monthly_payment:,.0f}元",
            "贷款年限": "30年",
            "契税": f"{deed_tax:,.0f}元",
            "购房总成本": f"{total_price + deed_tax:,.0f}元"
        }


# ============================================================================
# 3. 创建Agent并运行
# ============================================================================

def main():
    """主函数。"""
    print("=" * 80)
    print("OpenAI Function Calling Agent 示例")
    print("=" * 80)

    # 初始化工具
    tools = {
        "policy_lookup": PolicyLookupTool(),
        "cost_calculator": CostCalculatorTool()
    }

    print("\n1. 查看工具Schema:")
    print("-" * 80)
    for tool_name, tool in tools.items():
        schema = tool.get_schema()
        print(f"\n工具名称: {schema['function']['name']}")
        print(f"工具描述: {schema['function']['description']}")
        print(f"参数: {json.dumps(schema['function']['parameters'], ensure_ascii=False, indent=2)}")

    # 初始化Agent
    try:
        agent = OpenAIAgent(
            tools=tools,
            model="gpt-4-turbo-preview",
            temperature=0.7
        )

        print("\n" + "=" * 80)
        print("2. 运行Agent:")
        print("-" * 80)

        # 系统提示词
        system_prompt = """
你是一个专业的购房资金方案助手。

你需要：
1. 先调用 policy_lookup 查询相关政策
2. 再调用 cost_calculator 计算具体成本
3. 最后用通俗易懂的语言总结方案

注意：
- 把复杂的政策术语转化为"人话"
- 突出关键数字（首付、月供）
- 给出具体的建议
""".strip()

        # 用户请求
        user_message = """
我想在朝阳区买房，情况如下：
- 京籍，首套房
- 预算900万
- 想用组合贷

请帮我分析一下需要准备多少钱，月供多少。
"""

        print(f"\n用户请求:\n{user_message}")
        print("\n" + "-" * 80)
        print("Agent执行中...\n")

        # 运行Agent
        result = agent.run(
            user_message=user_message,
            system_prompt=system_prompt,
            max_iterations=5
        )

        print("\n" + "=" * 80)
        print("3. 执行结果:")
        print("-" * 80)
        print(f"状态: {result['status']}")
        print(f"迭代次数: {result['iterations']}")

        if result['status'] == 'success':
            print(f"\nAgent回复:\n{result['content']}")
            print(f"\nToken使用: {result['usage']}")
        else:
            print(f"错误: {result.get('error', result.get('message'))}")

    except ImportError as e:
        print(f"\n❌ 错误: {e}")
        print("\n请安装依赖: pip install openai")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请检查：")
        print("1. 是否设置了 OPENAI_API_KEY 环境变量")
        print("2. API key是否有效")
        print("3. 网络连接是否正常")


if __name__ == "__main__":
    main()
