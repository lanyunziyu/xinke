# 快速入门指南

## 项目架构总览

```
用户请求
   ↓
【OpenAI Agent】
   ↓
 ├─ Tool 1: PolicyLookupTool (政策检索)
 ├─ Tool 2: CostCalculatorTool (资金测算)
 └─ Tool 3: ReportGeneratorTool (报告生成)
   ↓
结构化购房方案报告
```

## 核心机制：工具如何被调用？

### 1. 工具定义 (tools/base_tool.py)

```python
class PolicyLookupTool(BaseTool):
    name = "policy_lookup"
    description = "查询购房政策"
    args_schema = PolicyLookupInput  # Pydantic模型定义参数

    def run(self, location: str, buyer_type: str) -> dict:
        # 实现工具逻辑
        return {"policies": "..."}
```

### 2. 自动生成Schema

工具通过 `get_schema()` 方法自动生成OpenAI function calling schema：

```json
{
  "type": "function",
  "function": {
    "name": "policy_lookup",
    "description": "查询购房政策",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string", "description": "购房区域"},
        "buyer_type": {"type": "string", "description": "购房者类型"}
      },
      "required": ["location", "buyer_type"]
    }
  }
}
```

### 3. Agent收集所有工具Schema

```python
agent = OpenAIAgent(tools={
    "policy_lookup": PolicyLookupTool(),
    "cost_calculator": CostCalculatorTool()
})

# Agent自动收集所有工具的schema
# 发送给OpenAI时带上 tools=[schema1, schema2, ...]
```

### 4. OpenAI决定调用哪个工具

```
用户: "我想在朝阳买房，预算900万"
    ↓
OpenAI分析 → 返回:
{
  "tool_calls": [
    {
      "function": {
        "name": "policy_lookup",
        "arguments": '{"location": "朝阳", "buyer_type": "首套"}'
      }
    }
  ]
}
```

### 5. Agent执行工具

```python
# Agent解析OpenAI返回的tool_call
tool_name = "policy_lookup"
tool_args = {"location": "朝阳", "buyer_type": "首套"}

# 执行对应工具
result = tools[tool_name].run(**tool_args)

# 将结果返回给OpenAI
```

### 6. 循环直到完成

```
OpenAI → 调用policy_lookup → Agent执行 → 返回结果
  ↓
OpenAI → 调用cost_calculator → Agent执行 → 返回结果
  ↓
OpenAI → 生成最终方案 → 完成
```

## 环境配置

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加你的OpenAI API密钥
OPENAI_API_KEY=sk-your-api-key-here
```

## 运行示例

### 方式1: 运行简单示例（推荐）

```bash
python examples/simple_example.py
```

这个示例展示：
- ✓ 如何定义工具
- ✓ 如何生成schema
- ✓ Agent如何自动调用工具
- ✓ 完整的工作流程

### 方式2: 使用openai-agents库

```bash
# 先安装
pip install openai-agents==0.2.3

# 运行示例
python examples/example_with_openai_agents.py
```

### 方式3: 运行主程序

```bash
python main.py
```

## 项目结构说明

```
xinke/
├── agents/                    # Agent实现
│   ├── openai_agent.py       # 手动实现的OpenAI Agent
│   └── agent_with_openai_agents.py  # 使用openai-agents库
│
├── tools/                     # 工具模块
│   ├── base_tool.py          # 工具基类（核心！）
│   ├── policy_lookup.py      # 政策查询工具
│   ├── cost_calculator.py    # 成本计算工具
│   └── report_generator.py   # 报告生成工具
│
├── examples/                  # 示例代码
│   ├── simple_example.py     # 基础示例（推荐从这里开始）
│   └── example_with_openai_agents.py  # 使用openai-agents
│
├── config/                    # 配置
│   └── config.py
│
├── utils/                     # 工具函数
│   ├── logger.py
│   └── validators.py
│
└── data/                      # 数据目录
    ├── policies/             # 政策文档（需要你添加）
    └── vector_db/            # 向量数据库
```

## 开发流程

### Step 1: 先运行示例，理解机制

```bash
python examples/simple_example.py
```

### Step 2: 实现具体的工具逻辑

编辑文件：
- `tools/policy_lookup.py` - 实现政策查询
- `tools/cost_calculator.py` - 实现成本计算
- `tools/report_generator.py` - 实现报告生成

### Step 3: 添加政策数据

在 `data/policies/` 目录下添加政策文档。

### Step 4: (可选) 集成RAG

如果需要RAG，在 `PolicyLookupTool` 中：
1. 加载政策文档
2. 生成embeddings
3. 存入向量数据库
4. 在查询时检索

### Step 5: 测试完整流程

```bash
python main.py
```

## 核心概念总结

### 工具 (Tool)

```python
# 1. 继承BaseTool
# 2. 定义name, description, args_schema
# 3. 实现run()方法
class MyTool(BaseTool):
    name = "my_tool"
    description = "工具功能"
    args_schema = MyToolInput

    def run(self, **kwargs):
        return {"result": "..."}
```

### Schema

```python
# 工具自动生成schema
schema = tool.get_schema()

# Schema告诉OpenAI：
# - 工具名称
# - 工具功能
# - 需要什么参数
# - 参数类型和说明
```

### Agent

```python
# Agent的工作：
# 1. 收集所有工具的schema
# 2. 发送给OpenAI (带tools参数)
# 3. OpenAI返回要调用的工具
# 4. Agent执行工具
# 5. 返回结果给OpenAI
# 6. 循环直到完成
```

## 常见问题

### Q1: 工具没有被调用？

**检查清单：**
- [ ] 工具的 `description` 是否清晰描述了功能
- [ ] 参数的 `description` 是否完整
- [ ] system_prompt中是否提示了什么时候用这个工具
- [ ] API key是否正确

### Q2: 如何添加新工具？

```python
# 1. 定义输入schema
class NewToolInput(BaseModel):
    param1: str = Field(description="参数说明")

# 2. 实现工具类
class NewTool(BaseTool):
    name = "new_tool"
    description = "新工具功能"
    args_schema = NewToolInput

    def run(self, param1: str):
        return {"result": "..."}

# 3. 添加到agent
tools["new_tool"] = NewTool()
```

### Q3: 如何调试？

```python
# 方法1: 查看工具schema
tool = PolicyLookupTool()
print(tool.get_schema())

# 方法2: 手动调用工具测试
result = tool.run(location="朝阳", buyer_type="京籍")
print(result)

# 方法3: 启用详细日志
from loguru import logger
logger.add("debug.log", level="DEBUG")
```

### Q4: 使用哪种Agent实现方式？

| 场景 | 推荐方式 |
|------|---------|
| 快速原型 | openai-agents库 |
| 需要复杂控制 | 手动实现OpenAI Agent |
| 生产环境 | 根据需求选择 |

## 下一步

1. ✅ 框架已搭建完成
2. ⏭️ 安装依赖: `pip install -r requirements.txt`
3. ⏭️ 配置API key
4. ⏭️ 运行示例: `python examples/simple_example.py`
5. ⏭️ 实现具体的工具逻辑
6. ⏭️ 添加政策数据
7. ⏭️ 集成RAG (可选)

## 参考资料

- [OpenAI Function Calling文档](https://platform.openai.com/docs/guides/function-calling)
- [openai-agents库](https://github.com/openai/openai-agents)
- 项目示例代码: `examples/`

---

**祝开发顺利！一天内完成没问题！** 🚀
