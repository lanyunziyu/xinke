"""
Base Tool class for OpenAI Function Calling.

所有工具继承这个基类，自动生成OpenAI function calling schema。
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import inspect
from pydantic import BaseModel


class BaseTool(ABC):
    """
    工具基类。

    子类需要：
    1. 定义 name 和 description
    2. 定义 args_schema (Pydantic模型)
    3. 实现 run() 方法
    """

    name: str = ""
    description: str = ""
    args_schema: Optional[type[BaseModel]] = None

    def __init__(self):
        if not self.name:
            self.name = self.__class__.__name__.replace("Tool", "").lower()
        if not self.description:
            self.description = self.__class__.__doc__ or "No description"

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """
        工具的主要执行逻辑。

        Args:
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        pass

    def get_schema(self) -> Dict[str, Any]:
        """
        生成OpenAI function calling schema。

        Returns:
            符合OpenAI格式的工具schema
        """
        if self.args_schema:
            # 使用Pydantic模型生成schema
            parameters = self.args_schema.model_json_schema()
        else:
            # 从run方法签名生成schema
            parameters = self._generate_schema_from_signature()

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": parameters
            }
        }

    def _generate_schema_from_signature(self) -> Dict[str, Any]:
        """从run()方法签名生成参数schema。"""
        sig = inspect.signature(self.run)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'kwargs']:
                continue

            # 获取类型注解
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str

            properties[param_name] = {
                "type": self._python_type_to_json_type(param_type),
                "description": f"Parameter: {param_name}"
            }

            # 没有默认值的是必填参数
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    @staticmethod
    def _python_type_to_json_type(py_type) -> str:
        """Python类型转JSON schema类型。"""
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        # 处理typing模块的类型
        if hasattr(py_type, '__origin__'):
            return type_mapping.get(py_type.__origin__, "string")

        return type_mapping.get(py_type, "string")

    def __call__(self, **kwargs) -> Any:
        """让工具实例可以直接调用。"""
        return self.run(**kwargs)
