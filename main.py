"""
Main entry point for the Housing Finance Advisor application.

一站式购房资金方案生成助手
"""
from pathlib import Path
from typing import Dict, Any

from loguru import logger

from config import config
from agents import MainAgent
from tools import PolicyLookupTool, CostCalculatorTool, ReportGeneratorTool
from utils import setup_logger


def initialize_tools() -> Dict[str, Any]:
    """
    Initialize all tools required by the main agent.

    Returns:
        Dictionary of initialized tool instances
    """
    logger.info("Initializing tools...")

    tools = {
        "policy_lookup": PolicyLookupTool(
            use_rag=config.TOOL_CONFIG["policy_lookup"]["use_rag"]
        ),
        "cost_calculator": CostCalculatorTool(),
        "report_generator": ReportGeneratorTool(
            template_dir=config.TOOL_CONFIG["report_generator"]["template_dir"],
            output_format=config.TOOL_CONFIG["report_generator"]["output_format"]
        ),
    }

    logger.info("Tools initialized successfully")
    return tools


def initialize_agent(tools: Dict[str, Any]) -> MainAgent:
    """
    Initialize the main agent with tools.

    Args:
        tools: Dictionary of tool instances

    Returns:
        Initialized MainAgent instance
    """
    logger.info("Initializing Main Agent...")
    agent = MainAgent(tools=tools)
    logger.info("Main Agent initialized successfully")
    return agent


def run_example():
    """
    Run an example scenario based on the provided case.

    This demonstrates the full workflow using the sample customer profile
    from the document.
    """
    # Example customer profile from the document
    example_profile = {
        "identity_info": {
            "male_beijing_hukou": True,
            "female_beijing_hukou": False,
            "marital_status": "未婚",
            "purchase_as_married": True,
            "provident_fund": {
                "male": "最高额",
                "female": "正常缴纳",
            }
        },
        "residence_status": {
            "properties_in_beijing": 0,
            "properties_nationwide": 0,
        },
        "purchase_needs": {
            "purpose": "首套婚房",
            "is_first_home": True,
        },
        "budget": 9000000,  # 900万
        "core_requirements": {
            "loan_preference": "市属组合贷",
            "concerns": ["贷款政策", "公积金提取", "户口迁出"],
        },
        "location": "朝阳",
    }

    logger.info("=" * 60)
    logger.info("Running example scenario")
    logger.info("=" * 60)

    # Initialize system
    tools = initialize_tools()
    agent = initialize_agent(tools)

    # Run agent
    result = agent.run(example_profile)

    # Display results
    logger.info("=" * 60)
    logger.info("Generated Solution:")
    logger.info(f"Status: {result['status']}")
    logger.info(f"Solution: {result['solution']}")
    logger.info("=" * 60)

    return result


def main():
    """
    Main function.
    """
    # Setup logging
    setup_logger(
        log_level=config.LOG_LEVEL,
        log_file=config.LOGS_DIR / "app.log"
    )

    logger.info("Starting Housing Finance Advisor Application")
    logger.info(f"Environment: {config.APP_ENV}")

    # Run example
    run_example()

    # TODO: Add CLI interface or API server
    # For now, just run the example

    logger.info("Application completed")


if __name__ == "__main__":
    main()
