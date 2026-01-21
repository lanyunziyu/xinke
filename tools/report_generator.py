"""
Report Generator Tool (报告生成工具)

Generates structured, human-readable housing finance reports.
Supports multiple output formats (Markdown, PDF, HTML).
"""
from typing import Dict, Any
from pathlib import Path
from loguru import logger
from pydantic import BaseModel, Field

from .base_tool import BaseTool


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
        生成购房方案报告。

        这个方法会被Agent自动调用，参数由OpenAI根据schema传入。

        Args:
            user_profile: 用户画像信息
            policies: 政策信息
            cost_breakdown: 成本计算结果

        Returns:
            包含报告内容的字典
        """
        logger.info("开始生成购房方案报告")

        # 生成各个部分
        report = {
            "report_content": self._build_report_content(
                user_profile, policies, cost_breakdown
            ),
            "sections": {
                "policy_interpretation": self._generate_policy_section(policies),
                "cost_breakdown": self._generate_cost_section(cost_breakdown),
                "action_steps": self._generate_action_steps(user_profile, policies),
                "summary": self._generate_summary(user_profile, cost_breakdown),
            }
        }

        logger.info("报告生成完成")
        return report

    # ============================================================================
    # 辅助方法 - 实现具体的报告生成逻辑
    # ============================================================================

    def _build_report_content(
        self,
        user_profile: Dict[str, Any],
        policies: Dict[str, Any],
        cost_breakdown: Dict[str, Any]
    ) -> str:
        """
        构建完整报告内容。

        Returns:
            格式化的报告字符串
        """
        # TODO: 实现完整的报告生成逻辑
        # 可以使用Jinja2模板，或者直接拼接字符串

        content = f"""
# 购房资金方案报告

## 一、客户画像
{self._format_user_profile(user_profile)}

## 二、政策解读（人话版）
{self._generate_policy_section(policies)}

## 三、资金方案
{self._generate_cost_section(cost_breakdown)}

## 四、办理步骤
{self._generate_action_steps(user_profile, policies)}

## 五、方案总结
{self._generate_summary(user_profile, cost_breakdown)}
"""
        return content.strip()

    def _format_user_profile(self, user_profile: Dict[str, Any]) -> str:
        """格式化用户画像信息。"""
        # TODO: 实现用户画像格式化
        return f"""
- 购房区域：{user_profile.get('location', 'N/A')}
- 购房预算：{user_profile.get('budget', 0) / 10000:.0f}万元
- 身份情况：{user_profile.get('identity_info', {})}
- 购房需求：{user_profile.get('purchase_needs', {})}
""".strip()

    def _generate_policy_section(self, policies: Dict[str, Any]) -> str:
        """
        生成政策解读部分（人话版）。

        核心：将复杂的政策法规转化为通俗易懂的语言。

        Args:
            policies: 政策信息

        Returns:
            人话版政策解读
        """
        # TODO: 实现政策解读逻辑
        # 技巧：
        # 1. 避免法律术语，用"大白话"
        # 2. 多用"也就是说..."、"简单来说..."
        # 3. 举实际例子
        # 4. 突出关键限制和注意事项

        policy_text = "### 购房资格\n"

        if 'purchase_restriction' in policies:
            policy_text += f"{policies['purchase_restriction']}\n\n"

        policy_text += "### 贷款政策\n"
        if 'loan_policy' in policies:
            policy_text += f"{policies['loan_policy']}\n\n"

        policy_text += "### 公积金政策\n"
        if 'provident_fund' in policies:
            policy_text += f"{policies['provident_fund']}\n"

        return policy_text

    def _generate_cost_section(self, cost_breakdown: Dict[str, Any]) -> str:
        """
        生成结构化成本清单。

        Args:
            cost_breakdown: 成本计算结果

        Returns:
            格式化的成本清单
        """
        # TODO: 实现成本清单生成
        # 使用表格格式，清晰展示各项费用

        cost_text = """
### 购房成本总览

| 项目 | 金额 | 说明 |
|------|------|------|
"""

        # 添加首付
        if 'down_payment' in cost_breakdown:
            dp = cost_breakdown['down_payment']
            cost_text += f"| 首付款 | {dp.get('amount', 0)}元 | 占比{dp.get('percentage', 0)}% |\n"

        # 添加贷款
        if 'loan_breakdown' in cost_breakdown:
            loan = cost_breakdown['loan_breakdown']
            cost_text += f"| 贷款总额 | {loan.get('total_loan', 0)}元 | |\n"

        # 添加月供
        if 'monthly_payment' in cost_breakdown:
            monthly = cost_breakdown['monthly_payment']
            cost_text += f"| 月供 | {monthly.get('total', 0)}元 | {monthly.get('years', 30)}年 |\n"

        # 添加税费
        if 'taxes' in cost_breakdown:
            taxes = cost_breakdown['taxes']
            total_tax = sum(taxes.values()) if isinstance(taxes, dict) else 0
            cost_text += f"| 各项税费 | {total_tax}元 | 契税+增值税+个税 |\n"

        return cost_text

    def _generate_action_steps(
        self,
        user_profile: Dict[str, Any],
        policies: Dict[str, Any]
    ) -> str:
        """
        生成办理步骤清单。

        Args:
            user_profile: 用户信息
            policies: 政策信息

        Returns:
            分步骤的行动指南
        """
        # TODO: 实现步骤清单生成
        # 根据用户情况，生成个性化的办理步骤

        steps = """
### 阶段一：准备阶段
- [ ] 准备身份证、户口本、婚姻证明等材料
- [ ] 查询个人征信报告
- [ ] 确认公积金缴存情况

### 阶段二：贷款申请
- [ ] 选择贷款银行
- [ ] 提交贷款申请材料
- [ ] 等待银行审批

### 阶段三：交易过户
- [ ] 签订购房合同
- [ ] 办理网签
- [ ] 缴纳税费
- [ ] 办理过户登记

### 阶段四：贷款发放
- [ ] 领取房产证
- [ ] 办理抵押登记
- [ ] 银行放款
"""
        return steps

    def _generate_summary(
        self,
        user_profile: Dict[str, Any],
        cost_breakdown: Dict[str, Any]
    ) -> str:
        """
        生成方案总结（关键信息汇总）。

        Args:
            user_profile: 用户信息
            cost_breakdown: 成本计算结果

        Returns:
            方案总结
        """
        # TODO: 实现总结生成
        # 提炼最关键的信息

        summary = """
### 核心数据一览
"""

        # 提取关键数字
        if 'down_payment' in cost_breakdown:
            dp_amount = cost_breakdown['down_payment'].get('amount', 0)
            summary += f"- 💰 需准备现金：{dp_amount / 10000:.0f}万元（首付+税费+其他费用）\n"

        if 'monthly_payment' in cost_breakdown:
            monthly = cost_breakdown['monthly_payment'].get('total', 0)
            summary += f"- 💳 月供金额：{monthly:.0f}元\n"

        summary += """
### 重要提示
- ⚠️ 本方案基于当前政策，具体以最新政策为准
- ⚠️ 贷款审批以银行实际评估为准
- ⚠️ 建议提前准备好所有材料

### 专业建议
- ✅ 建议保留一定的流动资金作为应急储备
- ✅ 注意月供不超过家庭月收入的50%
- ✅ 办理前再次核实最新政策
"""
        return summary

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
