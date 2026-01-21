"""
Report Generator Tool (报告生成工具)

Generates structured, human-readable housing finance reports.
Supports multiple output formats (Markdown, PDF, HTML).
"""
from typing import Dict, Any
from pathlib import Path
from loguru import logger
from pydantic import BaseModel, Field

try:
    from .base_tool import BaseTool
except ImportError:
    # 支持直接运行
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.base_tool import BaseTool


# ============================================================================
# 1. Schema定义 - 使用Pydantic定义输入参数
# ============================================================================

class ReportGeneratorInput(BaseModel):
    """报告生成工具的输入参数Schema。"""

    user_profile: Dict[str, Any] = Field(
        description="用户画像信息，包括身份、购房需求、预算等"
    )
    policies: Dict[str, Any] = Field(
        description="政策信息，包括限购、贷款、税费等政策内容"
    )
    cost_breakdown: Dict[str, Any] = Field(
        description="成本明细，包括首付、月供、税费等计算结果"
    )


# ============================================================================
# 2. 工具实现 - 继承BaseTool，实现run方法
# ============================================================================

class ReportGeneratorTool(BaseTool):
    """
    报告生成工具。

    根据用户画像、政策信息和成本计算结果，生成结构化的购房方案报告。
    报告包括：政策解读、成本清单、办理步骤、方案总结。
    """

    # 工具名称 - OpenAI会看到这个名字
    name = "report_generator"

    # 工具描述 - OpenAI根据这个描述决定什么时候调用这个工具
    description = """
    生成完整的购房资金方案报告。

    输入用户信息、政策信息和成本计算结果后，自动生成包含以下内容的报告：
    1. 人话版政策解读 - 将复杂政策转化为通俗语言
    2. 结构化成本清单 - 详细的资金明细
    3. 办理步骤清单 - 分步骤的行动指南
    4. 方案总结 - 关键信息汇总

    报告格式清晰，可直接发送给客户。
    """.strip()

    # 参数Schema - 告诉OpenAI需要传什么参数
    args_schema = ReportGeneratorInput

    def __init__(self, template_dir: Path = None, output_format: str = "markdown"):
        """
        初始化报告生成工具。

        Args:
            template_dir: 报告模板目录
            output_format: 输出格式 (markdown, pdf, html)
        """
        super().__init__()
        self.template_dir = template_dir
        self.output_format = output_format
        logger.info(f"ReportGeneratorTool初始化，输出格式: {output_format}")

    # ============================================================================
    # 3. run方法 - 这是工具的核心逻辑，Agent会调用这个方法
    # ============================================================================

    def run(
        self,
        user_profile: Dict[str, Any],
        policies: Dict[str, Any],
        cost_breakdown: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成购房方案报告 - 使用LLM生成人话版报告。

        这个方法会被Agent自动调用，参数由OpenAI根据schema传入。

        Args:
            user_profile: 用户画像信息
            policies: 政策信息
            cost_breakdown: 成本计算结果

        Returns:
            包含报告内容的字典
        """
        logger.info("开始生成购房方案报告（使用LLM）")

        # 使用LLM生成报告
        report_content = self._generate_report_with_llm(
            user_profile, policies, cost_breakdown
        )

        report = {
            "report_content": report_content,
            "user_profile": user_profile,
            "policies": policies,
            "cost_breakdown": cost_breakdown,
        }

        logger.info("报告生成完成")
        return report

    # ============================================================================
    # 核心方法 - 使用LLM生成报告
    # ============================================================================

    def _generate_report_with_llm(
        self,
        user_profile: Dict[str, Any],
        policies: Dict[str, Any],
        cost_breakdown: Dict[str, Any]
    ) -> str:
        """
        使用LLM生成购房方案报告。

        这是核心方法，通过精心设计的prompt让LLM生成通俗易懂的报告。

        Args:
            user_profile: 用户画像
            policies: 政策信息
            cost_breakdown: 成本计算

        Returns:
            LLM生成的完整报告文本
        """
        import json
        from openai import OpenAI
        import os
        from dotenv import load_dotenv

        # 加载环境变量
        load_dotenv()

        # 初始化OpenAI客户端
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_API_BASE_URL')

        if not api_key:
            logger.error("未找到OPENAI_API_KEY，无法生成报告")
            raise ValueError("必须配置 OPENAI_API_KEY 才能生成报告")

        try:
            # 支持自定义base_url
            if base_url:
                client = OpenAI(api_key=api_key, base_url=base_url)
                logger.info(f"使用自定义API端点: {base_url}")
            else:
                client = OpenAI(api_key=api_key)

            # 构建给LLM的prompt
            system_prompt = self._create_report_generation_prompt()
            user_message = self._format_data_for_llm(user_profile, policies, cost_breakdown)

            logger.info("调用LLM生成报告...")

            # 调用LLM
            response = client.chat.completions.create(
                model="Qwen3-Max",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=3000
            )

            report_content = response.choices[0].message.content
            logger.info(f"LLM生成报告成功，长度: {len(report_content)}字符")

            return report_content

        except Exception as e:
            logger.error(f"LLM生成报告失败: {str(e)}")
            raise

    def _create_report_generation_prompt(self) -> str:
        """
        创建报告生成的System Prompt。

        这个prompt定义了LLM的角色、任务和输出格式。

        Returns:
            System prompt字符串
        """
        return """
你是一位资深的购房顾问，专注于为客户生成通俗易懂、专业准确的购房资金方案报告。

## 你的角色定位

1. **客观中立**：不推销产品，基于政策和数据提供建议
2. **通俗易懂**：将复杂的政策法规转化为"人话"，像和朋友聊天一样解释
3. **结构清晰**：报告要有明确的模块划分，便于客户理解和执行
4. **重点突出**：用表格、列表、加粗等方式突出关键数字

## 你的任务

用户会提供三部分信息：
1. **用户画像**（user_profile）：客户的基本情况和购房需求
2. **政策信息**（policies）：适用的购房政策
3. **成本明细**（cost_breakdown）：详细的资金计算结果

你需要生成一份**完整的购房资金方案报告**，包含以下部分：

### 一、客户情况总结
- 简洁概括客户的购房需求和预算
- 突出关键信息（区域、预算、身份、首套/二套）

### 二、政策解读（人话版）
- **核心要求**：把复杂政策转化为大白话
- 使用"也就是说..."、"简单来说..."
- 举实际例子说明
- 突出限制条件和注意事项
- 覆盖：限购政策、贷款政策、公积金政策、税费政策

### 三、资金方案详解
- **用表格**展示成本总览（房屋总价、首付、贷款、税费）
- 详细说明贷款结构（商贷+公积金的组合）
- 月供计算及还款压力分析
- 各项税费明细

### 四、办理步骤清单
- 分阶段列出办理步骤
- 每个步骤要具体可操作
- 标注预计时间或注意事项
- 使用 [ ] 复选框格式

### 五、方案总结与建议
- 提炼关键数字（需准备多少现金、月供多少）
- 给出专业建议
- 风险提示

## 输出格式要求

1. 使用Markdown格式
2. 使用表格展示数字
3. 使用列表和复选框
4. 使用加粗突出重点
5. 语言通俗易懂，避免专业术语
6. 多用"您"、"建议"等亲切用语

## 语言风格示例

❌ 差的表达：
"根据《北京市限购政策》第三条，非京籍购房需满足连续60个月社保或纳税证明。"

✅ 好的表达：
"简单来说，如果您不是北京户口，需要在北京连续缴纳5年社保或个税才能买房。也就是说，中间不能断档，否则就要重新计算。"

❌ 差的表达：
"契税按差额累进税率计征。"

✅ 好的表达：
"契税就是买房时交的税，根据房子面积不同，税率也不同：
• 90平米以下：交1%
• 90-140平米：交1.5%
• 140平米以上：交3%"

现在，请根据用户提供的数据，生成一份专业、通俗、实用的购房资金方案报告！
""".strip()

    def _format_data_for_llm(
        self,
        user_profile: Dict[str, Any],
        policies: Dict[str, Any],
        cost_breakdown: Dict[str, Any]
    ) -> str:
        """
        将三个参数格式化为给LLM的输入。

        Args:
            user_profile: 用户画像
            policies: 政策信息
            cost_breakdown: 成本计算

        Returns:
            格式化的字符串
        """
        import json

        formatted_data = f"""
请根据以下信息生成购房资金方案报告：

# 一、用户画像
```json
{json.dumps(user_profile, ensure_ascii=False, indent=2)}
```

# 二、适用政策
```json
{json.dumps(policies, ensure_ascii=False, indent=2)}
```

# 三、成本计算结果
```json
{json.dumps(cost_breakdown, ensure_ascii=False, indent=2)}
```

---

请生成一份通俗易懂、结构清晰的购房资金方案报告。记住：
1. 用"人话"解释政策，不要法律术语
2. 用表格展示关键数字
3. 给出具体的办理步骤
4. 突出重点和风险提示
"""
        return formatted_data.strip()

    def save_report(self, report_content: str, output_path: Path) -> Path:
        """
        保存报告到文件。

        Args:
            report_content: 报告内容
            output_path: 输出路径

        Returns:
            保存的文件路径
        """
        # TODO: 实现文件保存逻辑
        logger.info(f"保存报告到 {output_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content, encoding='utf-8')

        return output_path

    def export_to_pdf(self, markdown_content: str, output_path: Path) -> Path:
        """
        将Markdown报告转换为PDF。

        Args:
            markdown_content: Markdown格式的报告
            output_path: 输出PDF路径

        Returns:
            PDF文件路径
        """
        # TODO: 实现PDF导出
        # 可以使用 reportlab 或 weasyprint
        logger.info(f"导出PDF到 {output_path}")
        return output_path


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    # 支持直接运行（修复相对导入问题）
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    # 查看工具schema
    tool = ReportGeneratorTool()

    print("=" * 80)
    print("ReportGeneratorTool Schema:")
    print("=" * 80)

    import json
    schema = tool.get_schema()
    print(json.dumps(schema, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("测试工具调用:")
    print("=" * 80)

    # 测试调用
    result = tool.run(
        user_profile={
            "location": "朝阳",
            "budget": 9000000,
            "identity_info": {"京籍": True}
        },
        policies={
            "purchase_restriction": "京籍首套可以购买",
            "loan_policy": "首套商贷首付30%"
        },
        cost_breakdown={
            "down_payment": {"amount": 2700000, "percentage": 30},
            "monthly_payment": {"total": 25000, "years": 30}
        }
    )

    print("\n生成的报告:")
    print(result['report_content'])
