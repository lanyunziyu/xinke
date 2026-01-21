"""
使用 openai-agents 库的完整示例。

openai-agents 是OpenAI官方的Agent框架，更简单易用。
安装: pip install openai-agents==0.2.3
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from loguru import logger


# ============================================================================
# 1. 定义工具 (和之前一样)
# ============================================================================

class PolicyLookupInput(BaseModel):
    """政策查询输入参数。"""
    location: str = Field(description="购房区域，如：朝阳、海淀")
    buyer_type: str = Field(description="购房者类型，如：京籍首套、非京籍")


class PolicyLookupTool(BaseTool):
    """政策查询工具。"""
    name = "policy_lookup"
    description = "查询购房相关政策，包括限购、贷款、税费等政策"
    args_schema = PolicyLookupInput

    def run(self, location: str, buyer_type: str) -> dict:
        logger.info(f"查询政策: {location}, {buyer_type}")
        return {
            "location": location,
            "buyer_type": buyer_type,
            "policies": {
                "限购政策": f"{location}，{buyer_type}可以购买住宅",
                "贷款政策": "首套商贷首付30%，公积金20%",
                "组合贷": "可以申请组合贷，先公积金后商贷",
                "税费": "首套90平以下契税1%"
            }
        }


class CostCalculatorInput(BaseModel):
    """成本计算输入参数。"""
    total_price: float = Field(description="房屋总价，单位：元")
    is_first_home: bool = Field(description="是否首套房")


class CostCalculatorTool(BaseTool):
    """成本计算工具。"""
    name = "cost_calculator"
    description = "计算购房成本，包括首付、月供、税费等"
    args_schema = CostCalculatorInput

    def run(self, total_price: float, is_first_home: bool) -> dict:
        logger.info(f"计算成本: {total_price}")

        down_payment_ratio = 0.3 if is_first_home else 0.4
        down_payment = total_price * down_payment_ratio
        loan_amount = total_price - down_payment

        # 月供计算
        annual_rate = 0.0365
        months = 360
        monthly_rate = annual_rate / 12
        monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)

        deed_tax = total_price * 0.01

        return {
            "房屋总价": f"{total_price/10000:.0f}万元",
            "首付": f"{down_payment/10000:.0f}万元 ({down_payment_ratio*100}%)",
            "贷款": f"{loan_amount/10000:.0f}万元",
            "月供": f"{monthly_payment:.0f}元/月",
            "契税": f"{deed_tax/10000:.1f}万元"
        }


# ============================================================================
# 2. 使用openai-agents框架
# ============================================================================

def example_with_openai_agents():
    """使用openai-agents库运行Agent。"""
    print("=" * 80)
    print("使用 openai-agents 库运行Agent")
    print("=" * 80)

    try:
        from openai_agents import Agent

        # 初始化工具
        tools = {
            "policy_lookup": PolicyLookupTool(),
            "cost_calculator": CostCalculatorTool()
        }

        print("\n✓ 工具加载成功")
        for name in tools.keys():
            print(f"  - {name}")

        # 将工具转换为openai-agents格式
        from openai_agents import function_tool

        agent_tools = []

        # 转换 policy_lookup
        policy_tool = tools["policy_lookup"]
        policy_schema = policy_tool.get_schema()

        @function_tool(
            name=policy_schema['function']['name'],
            description=policy_schema['function']['description']
        )
        def policy_lookup_func(location: str, buyer_type: str) -> dict:
            """查询购房政策。"""
            return policy_tool.run(location=location, buyer_type=buyer_type)

        agent_tools.append(policy_lookup_func)

        # 转换 cost_calculator
        cost_tool = tools["cost_calculator"]
        cost_schema = cost_tool.get_schema()

        @function_tool(
            name=cost_schema['function']['name'],
            description=cost_schema['function']['description']
        )
        def cost_calculator_func(total_price: float, is_first_home: bool) -> dict:
            """计算购房成本。"""
            return cost_tool.run(total_price=total_price, is_first_home=is_first_home)

        agent_tools.append(cost_calculator_func)

        print("✓ 工具转换成功")

        # 创建Agent
        agent = Agent(
            model="gpt-4-turbo-preview",
            instructions="""
你是专业的购房资金方案助手。

工作流程：
1. 调用 policy_lookup 查询政策
2. 调用 cost_calculator 计算成本
3. 用通俗语言总结方案

注意：
- 把政策转化为"人话"
- 突出首付和月供数字
- 给出具体建议
""".strip(),
            tools=agent_tools
        )

        print("✓ Agent创建成功\n")

        # 用户请求
        user_message = """
我想在朝阳区买房：
- 京籍，首套房
- 预算900万
- 想用组合贷

请帮我分析需要准备多少钱，月供多少。
"""

        print("用户请求:")
        print(user_message)
        print("\n" + "-" * 80)
        print("Agent执行中...\n")

        # 运行Agent
        response = agent.run(user_message)

        print("-" * 80)
        print("\nAgent回复:")
        print(response.content)

        print("\n" + "=" * 80)
        print("✓ 执行完成")
        print("=" * 80)

    except ImportError as e:
        print(f"\n❌ 错误: {e}")
        print("\n请安装依赖:")
        print("  pip install openai-agents==0.2.3")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请检查:")
        print("1. 是否设置了 OPENAI_API_KEY 环境变量")
        print("2. API key是否有效")
        print("3. 网络连接是否正常")


# ============================================================================
# 3. 对比两种方式
# ============================================================================

def show_comparison():
    """展示两种实现方式的对比。"""
    print("\n" + "=" * 80)
    print("两种实现方式对比")
    print("=" * 80)

    print("\n方式1: 手动实现 Function Calling")
    print("-" * 80)
    print("优点:")
    print("  ✓ 完全控制调用流程")
    print("  ✓ 可以自定义迭代逻辑")
    print("  ✓ 更灵活")
    print("\n缺点:")
    print("  ✗ 需要手动处理消息历史")
    print("  ✗ 需要自己实现重试逻辑")
    print("  ✗ 代码较多")

    print("\n方式2: 使用 openai-agents 库")
    print("-" * 80)
    print("优点:")
    print("  ✓ 代码简洁")
    print("  ✓ 自动处理工具调用")
    print("  ✓ OpenAI官方维护")
    print("\n缺点:")
    print("  ✗ 灵活性稍低")
    print("  ✗ 依赖特定版本")

    print("\n推荐:")
    print("  • 如果是简单场景，用 openai-agents 更快")
    print("  • 如果需要复杂控制，手动实现更好")
    print("=" * 80)


if __name__ == "__main__":
    # 运行示例
    example_with_openai_agents()

    # 显示对比
    show_comparison()
