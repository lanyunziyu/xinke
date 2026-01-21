"""
购房资金方案生成助手 - FastAPI 服务

提供 HTTP API 接口，支持：
- 流式对话（Server-Sent Events）
- 非流式对话
- 会话管理
- 健康检查
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import asyncio
from loguru import logger
import uvicorn

from agents.streaming_housing_finance_agent import StreamingHousingFinanceAgent, StreamEventType
from agents.housing_finance_agent import HousingFinanceAgent
from tools.trading_knowledge_retriever_tool import TradingKnowledgeRetrieverTool
from tools.quark_web_search_tool import QuarkWebSearchTool
from tools.trade_cost_calculate_tool import TradeCostCalculateTool
from tools.trade_cost_calculate_form_tool import TradeCostCalculateFormTool
from tools.report_generator import ReportGeneratorTool


# ============================================================================
# FastAPI 应用初始化
# ============================================================================

app = FastAPI(
    title="购房资金方案生成助手 API",
    description="智能购房助手，提供政策查询、成本计算、方案生成等服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# 全局变量：Agent 实例和会话管理
# ============================================================================

# Agent 实例（启动时初始化）
streaming_agent: Optional[StreamingHousingFinanceAgent] = None
sync_agent: Optional[HousingFinanceAgent] = None

# 会话存储（简单实现，生产环境应使用 Redis）
sessions: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# 请求/响应模型
# ============================================================================

class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., description="用户消息", min_length=1)
    conversation_id: Optional[str] = Field(None, description="会话 ID（用于多轮对话）")
    max_iterations: int = Field(15, description="最大迭代次数", ge=1, le=30)
    stream: bool = Field(True, description="是否使用流式输出")


class ChatResponse(BaseModel):
    """对话响应（非流式）"""
    status: str = Field(..., description="状态：success 或 error")
    response: Optional[str] = Field(None, description="Agent 的回复")
    error: Optional[str] = Field(None, description="错误信息")
    iterations: int = Field(..., description="执行迭代次数")
    conversation_id: str = Field(..., description="会话 ID")
    user_id: str = Field(..., description="用户 ID")


class SessionInfo(BaseModel):
    """会话信息"""
    conversation_id: str
    created_at: str
    message_count: int


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    agent_initialized: bool
    tools_count: int


# ============================================================================
# 启动和关闭事件
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化 Agent"""
    global streaming_agent, sync_agent

    logger.info("=" * 80)
    logger.info("初始化购房资金方案生成助手 API")
    logger.info("=" * 80)

    try:
        # 初始化工具
        tools = {
            "trading_knowledge_retriever": TradingKnowledgeRetrieverTool(),
            "quark_web_search": QuarkWebSearchTool(),
            "trade_cost_calculate": TradeCostCalculateTool(),
            "trade_cost_calculate_form": TradeCostCalculateFormTool(),
            "report_generator": ReportGeneratorTool()
        }

        logger.info(f"✓ 已加载 {len(tools)} 个工具:")
        for tool_name in tools.keys():
            logger.info(f"  • {tool_name}")

        # 初始化流式 Agent
        streaming_agent = StreamingHousingFinanceAgent(tools=tools)
        logger.info("✓ 流式 Agent 初始化完成")

        # 初始化同步 Agent
        sync_agent = HousingFinanceAgent(tools=tools)
        logger.info("✓ 同步 Agent 初始化完成")

        logger.info("=" * 80)
        logger.info("API 服务已启动")
        logger.info("访问 http://localhost:8000/docs 查看 API 文档")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"✗ Agent 初始化失败: {str(e)}")
        logger.exception(e)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("API 服务正在关闭...")
    # 清理会话
    sessions.clear()
    logger.info("✓ 资源清理完成")


# ============================================================================
# API 端点
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """根端点"""
    return {
        "name": "购房资金方案生成助手 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy" if streaming_agent and sync_agent else "unhealthy",
        agent_initialized=streaming_agent is not None and sync_agent is not None,
        tools_count=len(streaming_agent.tools) if streaming_agent else 0
    )


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    对话端点。

    支持流式和非流式两种模式：
    - stream=true: 返回 SSE 流式响应
    - stream=false: 返回 JSON 响应
    """
    if not streaming_agent or not sync_agent:
        raise HTTPException(status_code=503, detail="Agent 未初始化")

    if request.stream:
        # 流式响应
        return StreamingResponse(
            stream_chat_events(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
            }
        )
    else:
        # 非流式响应
        result = sync_agent.run(
            user_message=request.message,
            max_iterations=request.max_iterations,
            conversation_id=request.conversation_id
        )

        # 更新会话信息
        if result.get("conversation_id"):
            update_session(result["conversation_id"])

        if result["status"] == "success":
            return ChatResponse(
                status="success",
                response=result["response"],
                iterations=result["iterations"],
                conversation_id=result["conversation_id"],
                user_id=result["user_id"]
            )
        else:
            return ChatResponse(
                status="error",
                error=result.get("error", "未知错误"),
                iterations=result.get("iterations", 0),
                conversation_id=result.get("conversation_id", ""),
                user_id=result.get("user_id", "")
            )


async def stream_chat_events(request: ChatRequest):
    """
    生成 SSE 事件流。

    每个事件格式：
    event: <event_type>
    data: <json_data>
    """
    try:
        async for event in streaming_agent.stream_run(
            user_message=request.message,
            max_iterations=request.max_iterations,
            conversation_id=request.conversation_id
        ):
            event_type = event["type"]
            event_data = event["data"]

            # 更新会话信息
            if "conversation_id" in event_data:
                update_session(event_data["conversation_id"])

            # 格式化为 SSE 格式
            sse_event = f"event: {event_type}\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"
            yield sse_event

            # 小延迟，确保客户端能正常接收
            await asyncio.sleep(0.01)

    except Exception as e:
        logger.error(f"流式响应出错: {str(e)}")
        error_event = {
            "type": StreamEventType.ERROR,
            "data": {
                "error": str(e),
                "message": "处理失败"
            }
        }
        yield f"event: {StreamEventType.ERROR}\ndata: {json.dumps(error_event['data'], ensure_ascii=False)}\n\n"


@app.post("/reset")
async def reset_conversation(conversation_id: Optional[str] = None):
    """
    重置会话。

    如果提供 conversation_id，则重置指定会话；
    否则重置所有会话。
    """
    if conversation_id:
        if conversation_id in sessions:
            del sessions[conversation_id]
            return {"status": "success", "message": f"会话 {conversation_id} 已重置"}
        else:
            raise HTTPException(status_code=404, detail="会话不存在")
    else:
        sessions.clear()
        if streaming_agent:
            streaming_agent.reset_conversation()
        if sync_agent:
            sync_agent.reset_conversation()
        return {"status": "success", "message": "所有会话已重置"}


@app.get("/sessions")
async def list_sessions():
    """列出所有活跃会话"""
    session_list = [
        SessionInfo(
            conversation_id=conv_id,
            created_at=info.get("created_at", ""),
            message_count=info.get("message_count", 0)
        )
        for conv_id, info in sessions.items()
    ]
    return {
        "total": len(session_list),
        "sessions": session_list
    }


@app.get("/sessions/{conversation_id}")
async def get_session(conversation_id: str):
    """获取指定会话信息"""
    if conversation_id in sessions:
        return sessions[conversation_id]
    else:
        raise HTTPException(status_code=404, detail="会话不存在")


# ============================================================================
# 辅助函数
# ============================================================================

def update_session(conversation_id: str):
    """更新会话信息"""
    import datetime

    if conversation_id not in sessions:
        sessions[conversation_id] = {
            "conversation_id": conversation_id,
            "created_at": datetime.datetime.now().isoformat(),
            "message_count": 0,
            "last_activity": datetime.datetime.now().isoformat()
        }

    sessions[conversation_id]["message_count"] += 1
    sessions[conversation_id]["last_activity"] = datetime.datetime.now().isoformat()


# ============================================================================
# 异常处理
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.detail,
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常: {str(exc)}")
    logger.exception(exc)

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "内部服务器错误",
            "detail": str(exc)
        }
    )


# ============================================================================
# 主函数
# ============================================================================

def main():
    """启动服务"""
    import sys

    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    # 启动服务
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
