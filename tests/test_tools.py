"""
Unit tests for tools.
"""
import pytest
from tools import PolicyLookupTool, CostCalculatorTool, ReportGeneratorTool


class TestPolicyLookupTool:
    """Tests for PolicyLookupTool."""

    def test_init(self):
        """Test tool initialization."""
        tool = PolicyLookupTool(use_rag=True)
        assert tool is not None
        assert tool.use_rag == True

    def test_lookup(self):
        """Test policy lookup."""
        tool = PolicyLookupTool()
        user_profile = {
            "location": "朝阳",
            "identity_info": {"male_beijing_hukou": True}
        }
        result = tool.lookup(user_profile)
        assert result is not None
        assert "purchase_restriction" in result


class TestCostCalculatorTool:
    """Tests for CostCalculatorTool."""

    def test_init(self):
        """Test tool initialization."""
        tool = CostCalculatorTool()
        assert tool is not None
        assert tool.loan_interest_rates is not None

    def test_calculate(self):
        """Test cost calculation."""
        tool = CostCalculatorTool()
        user_profile = {
            "budget": 9000000,
            "purchase_needs": {"is_first_home": True}
        }
        result = tool.calculate(user_profile, {})
        assert result is not None
        assert "total_cost" in result
        assert "down_payment" in result


class TestReportGeneratorTool:
    """Tests for ReportGeneratorTool."""

    def test_init(self):
        """Test tool initialization."""
        tool = ReportGeneratorTool()
        assert tool is not None

    def test_generate(self):
        """Test report generation."""
        tool = ReportGeneratorTool()
        result = tool.generate({}, {}, {})
        assert result is not None
        assert "report_content" in result
        assert "sections" in result
