"""
一站式购房资金方案生成助手

基于 OpenAI Agent SDK 实现的智能购房助手，能够：
1. 查询和解读购房政策
2. 计算精确的购房成本
3. 生成通俗易懂的购房方案报告

使用的工具：
- trading_knowledge_retriever：查询交易知识和政策
- quark_web_search：补充最新政策信息
- trade_cost_calculate：计算购房成本明细
- trade_cost_calculate_form：获取成本计算表单配置
- report_generator：生成购房方案报告
"""
import json
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger
from openai import OpenAI
import os
from dotenv import load_dotenv


class HousingFinanceAgent:
    """
    一站式购房资金方案生成助手。

    这个 Agent 能够理解用户的购房需求，自动调用相关工具，
    并生成一份完整的、通俗易懂的购房资金方案报告。
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

        logger.info(f"HousingFinanceAgent 初始化完成")
        logger.info(f"- 模型: {self.model}")
        logger.info(f"- 工具数量: {len(self.tools)}")
        logger.info(f"- 用户ID: {self.session_user_id}")

    def _build_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        构建所有工具的 OpenAI Function Calling Schema。

        Returns:
            工具 schema 列表
        """
        schemas = []
        for tool_name, tool_instance in self.tools.items():
            if hasattr(tool_instance, 'get_schema'):
                schema = tool_instance.get_schema()
                schemas.append(schema)
                logger.debug(f"加载工具 schema: {tool_name}")

        logger.info(f"已构建 {len(schemas)} 个工具 schema")
        return schemas

    def _get_system_prompt(self) -> str:
        """
        获取 Agent 的系统提示词。

        Returns:
            系统提示词字符串
        """
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
- 从用户描述中提取关键信息：
  - 购房区域（如：朝阳、海淀）
  - 身份信息（京籍/非京籍、婚姻状态）
  - 购房需求（首套/二套、房屋总价）
  - 贷款需求（商贷/公积金/组合贷）

### 第二步：查询相关政策
- 使用 **trading_knowledge_retriever** 工具查询：
  - 限购政策（该身份是否可以购买）
  - 贷款政策（首付比例、利率）
  - 公积金政策（额度、提取规则）
  - 税费政策（契税、个税等）
  - 其他相关政策（户口迁移、办理流程）

- 如果知识库信息不够新或不够详细，使用 **quark_web_search** 补充最新政策

### 第三步：计算购房成本
- 如果用户提供了完整的房屋信息，使用 **trade_cost_calculate** 工具计算：
  - 精确的首付金额
  - 贷款金额和月供
  - 各项税费明细
  - 总成本汇总

- 如果信息不完整，可以先做粗略估算，或者询问用户补充信息

### 第四步：生成方案报告
- 使用 **report_generator** 工具生成完整报告：
  - 输入 user_profile（用户画像）
  - 输入 policies（政策信息）
  - 输入 cost_breakdown（成本计算结果）

- 工具会自动生成一份包含以下内容的报告：
  - 客户情况总结
  - 政策解读（人话版）
  - 资金方案详解
  - 办理步骤清单
  - 方案总结与建议

## 重要注意事项

1. **工具调用顺序**：
   - 先查政策（trading_knowledge_retriever）
   - 再算成本（trade_cost_calculate）
   - 最后生成报告（report_generator）

2. **数据传递**：
   - 将查询到的政策信息整理为结构化数据
   - 将计算出的成本明细整理为结构化数据
   - 传递给 report_generator 时要确保格式正确

3. **用户体验**：
   - 如果信息不足，友好地询问用户
   - 及时反馈进度（"正在查询政策..."、"正在计算成本..."）
   - 最终报告要清晰、完整、易懂

4. **专业性**：
   - 基于真实政策，不要编造
   - 计算要精确，不要估算错误
   - 给出的建议要合理、可执行

5. **会话管理**：
   - 使用 conversation_id 保持上下文
   - 可以支持多轮对话和追问
   - 记住用户之前提供的信息

## 示例对话

**用户**: 我想在朝阳区买房，预算900万，京籍首套，想用组合贷。

**你的思考过程**:
1. 提取信息：朝阳区、900万、京籍、首套、组合贷
2. 调用 trading_knowledge_retriever 查询朝阳区首套购房政策
3. 如果有完整房屋信息，调用 trade_cost_calculate 计算成本
4. 整理数据，调用 report_generator 生成报告
5. 将报告呈现给用户，用通俗语言解读关键点

现在，请根据用户的需求，按照上述流程工作！
""".strip()

    def run(
        self,
        user_message: str,
        max_iterations: int = 100,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        运行 Agent，处理用户请求。

        Args:
            user_message: 用户的输入消息
            max_iterations: 最大迭代次数（防止无限循环）
            conversation_id: 会话 ID（用于多轮对话）

        Returns:
            包含 Agent 回复的字典
        """
        logger.info("=" * 80)
        logger.info("开始处理用户请求")
        logger.info(f"用户消息: {user_message}")

        # 更新会话 ID
        if conversation_id:
            self.conversation_id = conversation_id
        elif not self.conversation_id:
            self.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"

        logger.info(f"会话 ID: {self.conversation_id}")

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
                        tool_args = json.loads(tool_call.function.arguments)

                        logger.info(f"调用工具: {tool_name}")
                        logger.debug(f"参数: {json.dumps(tool_args, ensure_ascii=False)}")

                        # 执行工具
                        tool_result = self._execute_tool(tool_name, tool_args)

                        logger.info(f"工具返回: {type(tool_result)}")
                        logger.debug(f"结果预览: {str(tool_result)[:200]}...")

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

            logger.info("=" * 80)

            return {
                "status": "success",
                "response": final_response,
                "iterations": iteration,
                "conversation_id": self.conversation_id,
                "user_id": self.session_user_id
            }

        except Exception as e:
            logger.error(f"Agent 执行失败: {str(e)}")
            logger.exception(e)
            return {
                "status": "error",
                "error": str(e),
                "iterations": iteration,
                "conversation_id": self.conversation_id
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
                    tool_args["source"] = "housing_finance_agent"
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


def main():
    """测试 Agent 运行。"""
    print("=" * 80)
    print("一站式购房资金方案生成助手 - 测试")
    print("=" * 80)

    # 导入工具
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from tools.trading_knowledge_retriever_tool import TradingKnowledgeRetrieverTool
    from tools.quark_web_search_tool import QuarkWebSearchTool
    from tools.trade_cost_calculate_tool import TradeCostCalculateTool
    from tools.trade_cost_calculate_form_tool import TradeCostCalculateFormTool
    from tools.report_generator import ReportGeneratorTool

    # 初始化工具
    tools = {
        "trading_knowledge_retriever": TradingKnowledgeRetrieverTool(),
        "quark_web_search": QuarkWebSearchTool(),
        "trade_cost_calculate": TradeCostCalculateTool(),
        "trade_cost_calculate_form": TradeCostCalculateFormTool(),
        "report_generator": ReportGeneratorTool()
    }

    print("\n✓ 工具加载成功:")
    for name in tools.keys():
        print(f"  - {name}")

    # 创建 Agent
    agent = HousingFinanceAgent(tools=tools)
    print("\n✓ Agent 创建成功")

    # 测试用例：参考 README 中的实际案例
    user_message = """
我想在朝阳区买房，具体情况如下：

**身份信息**：
- 男方：北京户口
- 女方：非北京户口
- 婚姻状态：未婚（后续以已婚状态购房）
- 公积金：两人均正常缴纳，男方最高额

**购房需求**：
- 区域：朝阳区
- 房屋性质：首套婚房
- 总预算：900万
- 贷款方式：优先考虑市属组合贷

**需要了解的信息**：
1. 我们这种情况能否购买？有什么限制？
2. 组合贷具体怎么办理？首付和月供大概多少？
3. 公积金如何提取？女方异地公积金能用吗？
4. 如果涉及户口迁移，有什么注意事项？
5. 整个购房流程和成本清单是怎样的？

请给我一份完整的购房资金方案。
"""

    print("\n" + "=" * 80)
    print("用户请求:")
    print(user_message)
    print("=" * 80)

    # 运行 Agent
    print("\nAgent 开始执行...\n")
    result = agent.run(user_message)

    print("\n" + "=" * 80)
    print("执行结果:")
    print("=" * 80)

    if result["status"] == "success":
        print(f"\n✓ 执行成功")
        print(f"迭代次数: {result['iterations']}")
        print(f"会话 ID: {result['conversation_id']}")
        print(f"\n{'-' * 80}")
        print("Agent 回复:")
        print(f"{'-' * 80}\n")
        print(result["response"])
    else:
        print(f"\n✗ 执行失败")
        print(f"错误: {result['error']}")


if __name__ == "__main__":
    main()
