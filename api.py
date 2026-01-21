"""
FastAPI application for Housing Finance Advisor.

Provides REST API endpoints for the housing finance solution generator.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from loguru import logger

from config import config
from agents import MainAgent
from tools import PolicyLookupTool, CostCalculatorTool, ReportGeneratorTool
from utils import setup_logger, validate_user_input


# Initialize FastAPI app
app = FastAPI(
    title="Housing Finance Advisor API",
    description="一站式购房资金方案生成助手 API",
    version="1.0.0"
)

# Setup logger
setup_logger(log_level=config.LOG_LEVEL)

# Initialize tools and agent (singleton)
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
agent = MainAgent(tools=tools)


# Request/Response Models
class IdentityInfo(BaseModel):
    male_beijing_hukou: bool = Field(description="男方是否京籍")
    female_beijing_hukou: bool = Field(description="女方是否京籍")
    marital_status: str = Field(description="婚姻状况")
    purchase_as_married: Optional[bool] = Field(None, description="是否以已婚状态购房")


class ResidenceStatus(BaseModel):
    properties_in_beijing: int = Field(description="北京名下房产数量")
    properties_nationwide: Optional[int] = Field(None, description="全国名下房产数量")


class PurchaseNeeds(BaseModel):
    purpose: str = Field(description="购房目的")
    is_first_home: bool = Field(description="是否首套房")


class CoreRequirements(BaseModel):
    loan_preference: str = Field(description="贷款方式偏好")
    concerns: list[str] = Field(default=[], description="关注的问题")


class UserProfileRequest(BaseModel):
    identity_info: IdentityInfo
    residence_status: ResidenceStatus
    purchase_needs: PurchaseNeeds
    budget: float = Field(gt=0, description="购房预算")
    core_requirements: CoreRequirements
    location: str = Field(description="意向购房区域")


class SolutionResponse(BaseModel):
    status: str
    user_profile: Dict[str, Any]
    solution: Dict[str, Any]


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Housing Finance Advisor API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/generate-solution", response_model=SolutionResponse)
async def generate_solution(request: UserProfileRequest):
    """
    Generate personalized housing finance solution.

    Args:
        request: User profile and requirements

    Returns:
        Complete housing finance solution including:
        - Policy interpretation
        - Cost breakdown
        - Action steps
        - Summary
    """
    try:
        logger.info(f"Received solution request for location: {request.location}")

        # Convert Pydantic model to dict
        user_profile = request.model_dump()

        # Validate input
        is_valid, errors = validate_user_input(user_profile)
        if not is_valid:
            raise HTTPException(status_code=400, detail={"errors": errors})

        # Generate solution using agent
        result = agent.run(user_profile)

        logger.info("Solution generated successfully")
        return result

    except Exception as e:
        logger.error(f"Error generating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/lookup-policy")
async def lookup_policy(location: str, buyer_type: str):
    """
    Look up housing policies for a specific location and buyer type.

    Args:
        location: District/region name
        buyer_type: Type of buyer (京籍/非京籍, 首套/二套)

    Returns:
        Relevant housing policies
    """
    try:
        logger.info(f"Policy lookup request: {location}, {buyer_type}")

        policy_tool = tools["policy_lookup"]
        policies = policy_tool.lookup({
            "location": location,
            "buyer_type": buyer_type
        })

        return {"status": "success", "policies": policies}

    except Exception as e:
        logger.error(f"Error looking up policy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/calculate-cost")
async def calculate_cost(
    total_price: float,
    is_first_home: bool,
    loan_type: str = "combination"
):
    """
    Calculate housing purchase costs.

    Args:
        total_price: Total property price
        is_first_home: Whether this is first home purchase
        loan_type: Type of loan (commercial, provident_fund, combination)

    Returns:
        Detailed cost breakdown
    """
    try:
        logger.info(f"Cost calculation request: {total_price}")

        calculator_tool = tools["cost_calculator"]
        cost_breakdown = calculator_tool.calculate(
            user_profile={
                "budget": total_price,
                "purchase_needs": {"is_first_home": is_first_home},
                "loan_preference": loan_type
            },
            policies={}  # TODO: Fetch relevant policies
        )

        return {"status": "success", "cost_breakdown": cost_breakdown}

    except Exception as e:
        logger.error(f"Error calculating cost: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
