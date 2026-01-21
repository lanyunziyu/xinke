# 房产购房助手 Vue 前端集成指南

## 📋 项目概述

这是一个基于Vue 3的房产购房助手前端应用，集成了5个核心工具的AI Agent，提供一站式购房资金方案生成服务。

### 🎯 核心功能
- **智能对话**：通过聊天界面与AI助手交互
- **政策查询**：实时获取最新购房政策信息
- **成本计算**：精确计算购房各项费用
- **方案生成**：生成专业的购房资金方案报告
- **多轮对话**：支持问题补充和持续咨询

### 🛠️ 技术架构

**后端服务（Python）**：
- FastAPI + 聊天接口（`api_app.py`）
- HousingFinanceAgent（房产助手Agent）
- 5个核心工具集成：
  - `trading_knowledge_retriever` - 交易知识检索
  - `quark_web_search` - 网页搜索
  - `trade_cost_calculate` - 成本计算
  - `trade_cost_calculate_form` - 表单配置
  - `report_generator` - 报告生成

**前端应用（Vue 3）**：
- Vue 3 + Composition API
- Element Plus UI组件库
- Pinia状态管理
- Tailwind CSS样式
- Axios网络请求
- Marked Markdown渲染

## 🚀 快速开始

### 1. 后端服务启动

```bash
# 进入项目根目录
cd /workspace/bella-infra/user/libeibei031/spech/xinke

# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 OPENAI_API_KEY 等必要配置

# 启动聊天API服务
python api_app.py
```

服务将在 http://localhost:8000 启动

### 2. 前端应用启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动

### 3. API 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 测试聊天接口（非流式）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想在朝阳区买房，预算900万，男方北京户口，女方非京籍，打算以已婚状态购房",
    "stream": false
  }'

# 测试聊天接口（流式）
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想了解北京首套房首付比例",
    "stream": true
  }'
```

## 📡 API 接口说明

### 核心聊天接口

**POST /chat**

请求格式：
```json
{
  "message": "用户消息内容",
  "stream": false,
  "conversation_id": "可选的会话ID",
  "user_id": "可选的用户ID"
}
```

响应格式（非流式）：
```json
{
  "id": "响应ID",
  "message": "助手回复内容",
  "conversation_id": "会话ID",
  "timestamp": "时间戳",
  "metadata": {
    "iterations": 8,
    "tools_used": ["trading_knowledge_retriever", "report_generator"],
    "session_id": "会话标识"
  }
}
```

流式响应格式：
```
data: {"type": "start", "id": "response_id"}
data: {"type": "chunk", "content": "内容片段"}
data: {"type": "metadata", "iterations": 8, "tools_used": [...]}
data: {"type": "end", "id": "response_id"}
```

### 辅助接口

- **GET /health** - 健康检查
- **GET /conversations/{id}** - 获取会话历史
- **DELETE /conversations/{id}** - 删除会话

## 🎨 前端组件架构

### 主要组件

1. **App.vue** - 主应用组件
   - 步骤指示器
   - 路由控制
   - 全局状态管理

2. **UserInputArea.vue** - 用户输入区域
   - 支持自然语言输入
   - 表单验证
   - 语音输入（可扩展）

3. **ModelFeedback.vue** - Agent反馈区域
   - 对话历史展示
   - 信息补充表单
   - 实时聊天界面

4. **ReportView.vue** - 报告展示组件
   - Markdown渲染
   - 结构化数据提取
   - 交互式操作

5. **ReportModal.vue** - 报告详情弹窗
   - 完整报告查看
   - 分享和下载功能

### 状态管理 (housing.js)

```javascript
// 核心状态
const state = {
  userInput: '',           // 用户输入
  conversationHistory: [], // 对话历史
  currentStep: 'input',    // 当前步骤
  reportData: null,        // 报告数据
  loading: false,          // 加载状态
  sessionId: null          // 会话ID
}

// 主要方法
const actions = {
  submitUserInput,         // 提交用户输入
  supplementInformation,   // 补充信息
  sendChatMessage,        // 发送聊天消息
  generateReport          // 生成报告
}
```

## 🔧 配置说明

### 环境变量 (.env)

```bash
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE_URL=https://openapi-ait.ke.com/v1
OPENAI_MODEL=Qwen3-Max

# MCP服务配置
MCP_XIAOYI_ENDPOINT=内部MCP服务地址
MCP_WEB_SEARCH_ENDPOINT=网页搜索服务地址
```

### 前端配置

```javascript
// api/housing.js 中的基础URL配置
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',  // 后端服务地址
  timeout: 30000
})
```

## 📖 使用流程

### 1. 用户输入阶段
用户通过自然语言输入购房需求：
```
"我想在朝阳区买房，具体情况如下：
- 男方：北京户口
- 女方：非北京户口
- 婚姻状态：未婚（后续以已婚状态购房）
- 总预算：900万
- 贷款方式：优先考虑市属组合贷"
```

### 2. Agent处理阶段
系统自动调用5个核心工具：
- 查询购房政策（trading_knowledge_retriever）
- 补充最新信息（quark_web_search）
- 计算购房成本（trade_cost_calculate）
- 生成方案报告（report_generator）

### 3. 结果展示阶段
展示完整的购房资金方案：
- 方案概览（首付、月供、总成本）
- 政策解读
- 成本明细
- 操作步骤
- 专家建议

### 4. 持续咨询阶段
用户可以继续提问：
- "女方异地公积金如何转移？"
- "如果房价降到800万，月供会减少多少？"
- "户口迁移需要什么材料？"

## 🎯 核心特性

### 1. 智能对话流
- 自然语言理解和处理
- 上下文记忆和连续对话
- 智能信息提取和结构化

### 2. 实时数据集成
- 最新购房政策查询
- 精确成本计算
- 动态报告生成

### 3. 用户友好界面
- 渐进式表单填写
- 可视化数据展示
- 响应式设计

### 4. 专业报告生成
- Markdown格式报告
- PDF导出功能
- 分享和保存

## 🔍 调试和开发

### 后端调试

```bash
# 查看API文档
http://localhost:8000/docs

# 查看日志
tail -f logs/app.log

# 测试单个工具
python -c "
from tools.trading_knowledge_retriever_tool import TradingKnowledgeRetrieverTool
tool = TradingKnowledgeRetrieverTool()
result = tool.run('北京首套房政策', '测试', 'test_user')
print(result)
"
```

### 前端调试

```bash
# 开发模式启动（带热重载）
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 常见问题

1. **Agent初始化失败**
   - 检查 OPENAI_API_KEY 是否正确设置
   - 确认网络连接正常
   - 查看MCP服务是否可用

2. **前端API调用失败**
   - 确认后端服务已启动
   - 检查CORS配置
   - 验证API基础URL配置

3. **报告生成异常**
   - 检查用户输入信息完整性
   - 确认所有工具正常响应
   - 查看Agent处理日志

## 📈 扩展建议

### 1. 功能扩展
- 添加语音输入/输出
- 集成地图选房功能
- 添加房贷计算器
- 支持多城市政策

### 2. 技术优化
- 实现服务端渲染（SSR）
- 添加缓存机制
- 优化移动端体验
- 集成埋点统计

### 3. 业务拓展
- 支持二手房评估
- 添加投资建议
- 集成房源推荐
- 提供专家咨询

## 📝 更新日志

### v1.0.0 (2026-01-21)
- ✅ 完成基础架构搭建
- ✅ 集成5个核心工具
- ✅ 实现聊天式交互
- ✅ 完成报告生成功能
- ✅ 添加Vue前端界面

### 下一步计划
- 🔄 优化流式响应体验
- 🔄 添加更多城市支持
- 🔄 完善错误处理机制
- 🔄 增加单元测试覆盖

---

**开发团队**：AI Agent开发组
**文档更新**：2026-01-21
**版本**：v1.0.0