# 示例代码

## simple_example.py - 基础示例

展示了OpenAI Function Calling Agent的完整使用流程：

1. **定义工具** - 使用 `BaseTool` 和 Pydantic 定义工具
2. **创建Agent** - 使用 `OpenAIAgent`
3. **运行Agent** - 自动调用工具并生成方案

### 运行方法

```bash
# 1. 确保设置了API key
export OPENAI_API_KEY="your-api-key"

# 2. 运行示例
python examples/simple_example.py
```

### 工作流程

```
用户请求
   ↓
Agent发送请求 + 工具schema给OpenAI
   ↓
OpenAI分析后返回: 需要调用policy_lookup工具
   ↓
Agent执行 policy_lookup(location="朝阳", buyer_type="京籍首套")
   ↓
将工具结果返回给OpenAI
   ↓
OpenAI分析后返回: 需要调用cost_calculator工具
   ↓
Agent执行 cost_calculator(total_price=9000000, is_first_home=True)
   ↓
将工具结果返回给OpenAI
   ↓
OpenAI生成最终的购房方案
   ↓
返回给用户
```

## 核心概念

### 1. 工具Schema

每个工具通过 `get_schema()` 方法生成schema，告诉LLM：
- 工具名称
- 工具功能
- 需要什么参数
- 参数类型

```python
{
    "type": "function",
    "function": {
        "name": "policy_lookup",
        "description": "查询购房相关政策...",
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

### 2. Agent工作流

1. 收集所有工具的schema
2. 发送给OpenAI (带 `tools` 参数)
3. OpenAI返回要调用的函数和参数
4. Agent执行对应的工具
5. 将结果返回给OpenAI
6. 重复直到OpenAI返回最终答案

### 3. 如何添加新工具

```python
from pydantic import BaseModel, Field
from tools.base_tool import BaseTool

# 1. 定义输入schema
class MyToolInput(BaseModel):
    param1: str = Field(description="参数1说明")
    param2: int = Field(description="参数2说明")

# 2. 实现工具类
class MyTool(BaseTool):
    name = "my_tool"
    description = "工具功能描述"
    args_schema = MyToolInput

    def run(self, param1: str, param2: int) -> dict:
        # 实现工具逻辑
        return {"result": "..."}

# 3. 添加到agent
tools = {
    "my_tool": MyTool()
}
agent = OpenAIAgent(tools=tools)
```

## 常见问题

### Q: 工具没有被调用？

检查：
- 工具的 `description` 是否清晰
- 参数的 `description` 是否完整
- system_prompt中是否提示了工具的用途

### Q: 如何调试工具调用？

使用logger查看日志：
```python
from loguru import logger
logger.add("debug.log", level="DEBUG")
```

### Q: 如何限制工具调用次数？

设置 `max_iterations` 参数：
```python
result = agent.run(
    user_message=message,
    max_iterations=3  # 最多3次迭代
)
```
