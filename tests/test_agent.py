"""
Unit tests for main agent.
"""
import pytest
from agents import MainAgent
from tools import PolicyLookupTool, CostCalculatorTool, ReportGeneratorTool


class TestMainAgent:
    """Tests for MainAgent."""

    def test_init(self):
        """Test agent initialization."""
        agent = MainAgent()
        assert agent is not None
        assert agent.tools is not None

    def test_init_with_tools(self):
        """Test agent initialization with tools."""
        tools = {
            "policy_lookup": PolicyLookupTool(),
            "cost_calculator": CostCalculatorTool(),
            "report_generator": ReportGeneratorTool(),
        }
        agent = MainAgent(tools=tools)
        assert agent is not None
        assert len(agent.tools) == 3

    def test_run(self):
        """Test agent run method."""
        tools = {
            "policy_lookup": PolicyLookupTool(),
            "cost_calculator": CostCalculatorTool(),
            "report_generator": ReportGeneratorTool(),
        }
        agent = MainAgent(tools=tools)

        user_profile = {
            "identity_info": {"male_beijing_hukou": True},
            "residence_status": {"properties_in_beijing": 0},
            "purchase_needs": {"is_first_home": True},
            "budget": 9000000,
            "location": "朝阳"
        }

        result = agent.run(user_profile)
        assert result is not None
        assert result["status"] == "success"
        assert "solution" in result
