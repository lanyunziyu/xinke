# 购房资金方案生成助手 - API 文档

## 概述

本 API 提供购房资金方案生成服务，支持政策查询、成本计算、方案报告生成等功能。

**基础信息**:
- 基础 URL: `http://localhost:8000`
- API 文档: `http://localhost:8000/docs` (Swagger UI)
- ReDoc 文档: `http://localhost:8000/redoc`

**特性**:
- ✅ 流式输出（Server-Sent Events）
- ✅ 非流式输出（JSON）
- ✅ 多轮对话支持
- ✅ 会话管理
- ✅ CORS 支持

## 快速开始

### 1. 启动服务

```bash
# 方式 1: 直接运行
python api_app.py

# 方式 2: 使用 uvicorn
uvicorn api_app:app --reload --port 8000

# 方式 3: 生产环境
uvicorn api_app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. 测试连接

```bash
curl http://localhost:8000/health
```

### 3. 发送对话请求

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "北京首套房首付比例是多少？",
    "stream": false
  }'
```

## API 端点

### 1. 根端点

**GET /** - 获取 API 基本信息

**响应示例**:
```json
{
  "name": "购房资金方案生成助手 API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### 2. 健康检查

**GET /health** - 检查服务健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "tools_count": 5
}
```

**状态码**:
- `200`: 服务正常
- `503`: 服务不可用

---

### 3. 对话接口

**POST /chat** - 与 Agent 对话

#### 请求体

```json
{
  "message": "我想在海淀区买首套房，预算600万",
  "conversation_id": "conv_abc123",  // 可选，用于多轮对话
  "max_iterations": 15,              // 可选，默认 15
  "stream": true                     // 可选，默认 true
}
```

**参数说明**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| message | string | 是 | - | 用户消息 |
| conversation_id | string | 否 | null | 会话 ID，用于多轮对话 |
| max_iterations | integer | 否 | 15 | 最大迭代次数（1-30） |
| stream | boolean | 否 | true | 是否使用流式输出 |

#### 响应模式

##### 模式 1: 流式响应 (stream=true)

**响应类型**: `text/event-stream` (Server-Sent Events)

**事件类型**:

1. **thinking** - Agent 正在思考
```
event: thinking
data: {"message": "正在理解您的需求...", "conversation_id": "conv_abc123"}
```

2. **tool_call** - 开始调用工具
```
event: tool_call
data: {
  "tool_name": "trading_knowledge_retriever",
  "tool_args": {"query": "首套房政策", "source": "api", "user": "user_123"},
  "message": "正在调用 trading_knowledge_retriever..."
}
```

3. **tool_result** - 工具返回结果
```
event: tool_result
data: {
  "tool_name": "trading_knowledge_retriever",
  "result": {"status": "success", "data": "..."},
  "message": "trading_knowledge_retriever 执行完成"
}
```

4. **response_start** - 开始生成回复
```
event: response_start
data: {"message": "开始生成回复...", "iterations": 3}
```

5. **response_chunk** - 回复片段（流式生成）
```
event: response_chunk
data: {"content": "简单来说，北京首套房..."}
```

6. **response_end** - 回复结束
```
event: response_end
data: {"message": "回复生成完成", "full_response": "完整回复内容"}
```

7. **done** - 处理完成
```
event: done
data: {
  "status": "success",
  "iterations": 3,
  "conversation_id": "conv_abc123",
  "user_id": "user_123"
}
```

8. **error** - 错误
```
event: error
data: {"error": "错误信息", "message": "处理失败"}
```

##### 模式 2: 非流式响应 (stream=false)

**响应类型**: `application/json`

**成功响应**:
```json
{
  "status": "success",
  "response": "简单来说，北京首套房的首付比例是30%...",
  "iterations": 3,
  "conversation_id": "conv_abc123",
  "user_id": "user_123"
}
```

**错误响应**:
```json
{
  "status": "error",
  "error": "错误信息",
  "iterations": 2,
  "conversation_id": "conv_abc123",
  "user_id": "user_123"
}
```

---

### 4. 重置会话

**POST /reset** - 重置会话

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| conversation_id | string | 否 | 要重置的会话 ID。不提供则重置所有会话 |

**请求示例**:
```bash
# 重置指定会话
curl -X POST "http://localhost:8000/reset?conversation_id=conv_abc123"

# 重置所有会话
curl -X POST "http://localhost:8000/reset"
```

**响应示例**:
```json
{
  "status": "success",
  "message": "会话 conv_abc123 已重置"
}
```

---

### 5. 列出会话

**GET /sessions** - 列出所有活跃会话

**响应示例**:
```json
{
  "total": 2,
  "sessions": [
    {
      "conversation_id": "conv_abc123",
      "created_at": "2026-01-21T14:00:00",
      "message_count": 5
    },
    {
      "conversation_id": "conv_def456",
      "created_at": "2026-01-21T15:00:00",
      "message_count": 3
    }
  ]
}
```

---

### 6. 获取会话信息

**GET /sessions/{conversation_id}** - 获取指定会话信息

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| conversation_id | string | 是 | 会话 ID |

**响应示例**:
```json
{
  "conversation_id": "conv_abc123",
  "created_at": "2026-01-21T14:00:00",
  "message_count": 5,
  "last_activity": "2026-01-21T14:30:00"
}
```

**错误响应**:
```json
{
  "status": "error",
  "error": "会话不存在",
  "path": "/sessions/conv_abc123"
}
```

---

## 使用示例

### Python 示例

#### 1. 流式对话（推荐）

```python
import requests
import sseclient  # pip install sseclient-py
import json

url = "http://localhost:8000/chat"

payload = {
    "message": "我想在海淀区买首套房，预算600万",
    "stream": True
}

response = requests.post(url, json=payload, stream=True)
client = sseclient.SSEClient(response)

for event in client.events():
    event_type = event.event
    event_data = json.loads(event.data)

    if event_type == "response_chunk":
        print(event_data["content"], end="", flush=True)
    elif event_type == "done":
        print(f"\n\n完成！会话 ID: {event_data['conversation_id']}")
```

#### 2. 非流式对话

```python
import requests

url = "http://localhost:8000/chat"

payload = {
    "message": "北京首套房首付比例？",
    "stream": False
}

response = requests.post(url, json=payload)
result = response.json()

print(result["response"])
print(f"会话 ID: {result['conversation_id']}")
```

#### 3. 多轮对话

```python
import requests

url = "http://localhost:8000/chat"

# 第一轮
payload1 = {
    "message": "什么是满五唯一？",
    "stream": False
}
response1 = requests.post(url, json=payload1)
result1 = response1.json()
conv_id = result1["conversation_id"]

print(f"第一轮: {result1['response']}")

# 第二轮（基于上下文）
payload2 = {
    "message": "它有什么税费优惠？",  # "它"指满五唯一
    "stream": False,
    "conversation_id": conv_id  # 传递会话 ID
}
response2 = requests.post(url, json=payload2)
result2 = response2.json()

print(f"第二轮: {result2['response']}")
```

#### 4. 使用客户端封装

```python
from examples.api_client_example import HousingFinanceAPIClient

# 创建客户端
client = HousingFinanceAPIClient("http://localhost:8000")

# 健康检查
health = client.health_check()
print(f"服务状态: {health['status']}")

# 流式对话
for event in client.chat("北京首套房首付？", stream=True):
    if event["type"] == "response_chunk":
        print(event["data"]["content"], end="", flush=True)

# 多轮对话（会话 ID 自动管理）
result = client.chat("那二套房呢？", stream=False)
print(result["response"])
```

### JavaScript/TypeScript 示例

#### 1. 流式对话（使用 EventSource）

```javascript
const eventSource = new EventSource('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: '北京首套房首付比例？',
    stream: true
  })
});

eventSource.addEventListener('response_chunk', (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content);
});

eventSource.addEventListener('done', (event) => {
  const data = JSON.parse(event.data);
  console.log('完成！会话 ID:', data.conversation_id);
  eventSource.close();
});

eventSource.addEventListener('error', (event) => {
  console.error('错误:', event);
  eventSource.close();
});
```

#### 2. 非流式对话（使用 fetch）

```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: '北京首套房首付比例？',
    stream: false
  })
});

const result = await response.json();
console.log(result.response);
console.log('会话 ID:', result.conversation_id);
```

### cURL 示例

#### 1. 非流式对话

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "北京首套房首付比例？",
    "stream": false
  }'
```

#### 2. 流式对话

```bash
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "北京首套房首付比例？",
    "stream": true
  }'
```

#### 3. 多轮对话

```bash
# 第一轮
CONV_ID=$(curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是满五唯一？", "stream": false}' \
  | jq -r '.conversation_id')

# 第二轮
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"它有什么优惠？\", \"stream\": false, \"conversation_id\": \"$CONV_ID\"}"
```

## 错误处理

### HTTP 状态码

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在（如会话不存在） |
| 500 | 服务器内部错误 |
| 503 | 服务不可用（Agent 未初始化） |

### 错误响应格式

```json
{
  "status": "error",
  "error": "错误描述",
  "path": "/chat"
}
```

### 常见错误

1. **Agent 未初始化**
```json
{
  "detail": "Agent 未初始化"
}
```
**解决方法**: 检查环境变量配置，确保 OPENAI_API_KEY 已设置

2. **会话不存在**
```json
{
  "status": "error",
  "error": "会话不存在"
}
```
**解决方法**: 使用有效的 conversation_id 或不传递该参数

3. **参数验证失败**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**解决方法**: 检查请求参数是否完整和正确

## 部署指南

### 开发环境

```bash
# 安装依赖
pip install fastapi uvicorn sseclient-py

# 启动服务（自动重载）
uvicorn api_app:app --reload --port 8000
```

### 生产环境

```bash
# 使用多个 worker
uvicorn api_app:app --host 0.0.0.0 --port 8000 --workers 4

# 使用 Gunicorn
gunicorn api_app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建镜像
docker build -t housing-finance-api .

# 运行容器
docker run -p 8000:8000 --env-file .env housing-finance-api
```

## 性能优化

### 1. 连接池

```python
# 在 api_app.py 中配置
app.state.http_client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.http_client.aclose()
```

### 2. 缓存

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_common_answer(query: str):
    # 缓存常见问题的回答
    pass
```

### 3. 异步处理

```python
# 使用异步工具调用
async def async_tool_call(tool_name, tool_args):
    # 异步执行工具
    pass
```

## 监控和日志

### 日志配置

日志级别: INFO
日志格式: `<time> | <level> | <message>`

### 监控指标

- 请求数量和成功率
- 平均响应时间
- 工具调用次数
- 错误率
- 活跃会话数

### 健康检查

```bash
# 定期检查服务状态
while true; do
  curl -s http://localhost:8000/health | jq .
  sleep 60
done
```

## FAQ

### Q: 如何处理长时间运行的请求？

A: 使用流式输出（stream=true），可以实时看到处理进度，避免超时。

### Q: 如何实现会话持久化？

A: 目前会话存储在内存中。生产环境建议使用 Redis:
```python
import redis
sessions = redis.Redis(host='localhost', port=6379, db=0)
```

### Q: 如何限制请求频率？

A: 使用 slowapi:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, ...):
    ...
```

### Q: 如何添加认证？

A: 使用 FastAPI 的 Security:
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/chat")
async def chat(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # 验证 token
    ...
```

## 更多资源

- **完整示例**: `examples/api_client_example.py`
- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **项目仓库**: [GitHub链接]

## 联系支持

- 问题反馈: [GitHub Issues]
- 邮箱: support@example.com
