import json
import requests
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP (Model Context Protocol) 客户端
    支持工具调用功能
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化MCP客户端
        
        Args:
            config_path: MCP配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            # 获取项目根目录的绝对路径
            # current_dir = os.path.dirname(os.path.abspath(__file__))
            # project_root = os.path.dirname(os.path.dirname(current_dir))
            config_path = os.path.join("config", "mcp_config.json")
        
        self.config = self._load_config(config_path)
        self.session = requests.Session()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载MCP配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                # 兼容两种配置格式:
                # 1. {"mcpServers": {...}} - 标准格式
                # 2. {...} - 直接的工具配置
                if "mcpServers" in config_data:
                    return config_data["mcpServers"]
                return config_data
        except FileNotFoundError:
            logger.error(f"MCP配置文件未找到: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"MCP配置文件格式错误: {e}")
            raise
    
    def call_tool(self, tool_name: str, method: str, arguments: Dict[str, Any], 
                  request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        调用MCP工具
        
        Args:
            tool_name: 工具名称 (如 'amap-mcp', 'web-search')
            method: 方法名称 (如 'common_search')
            arguments: 方法参数
            request_id: 请求ID，如果为None则自动生成
            
        Returns:
            工具调用结果
        """
        if tool_name not in self.config:
            raise ValueError(f"未找到工具配置: {tool_name}")
        
        tool_config = self.config[tool_name]
        url = f"{tool_config['url']}tools/call"
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            **tool_config.get("headers", {})
        }
        
        # 构建请求体
        request_id = request_id or f"req_{hash(str(arguments))}"
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": arguments
            }
        }
        
        try:
            logger.info(f"调用MCP工具: {tool_name}.{method}")
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
            
            response = self.session.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"MCP工具调用成功: {tool_name}.{method}")
            logger.debug(f"响应结果: {json.dumps(result, ensure_ascii=False)}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP工具调用失败: {tool_name}.{method}, 错误: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"MCP响应解析失败: {e}")
            raise
    
    def get_available_tools(self) -> list:
        """
        获取可用的工具列表
        
        Returns:
            工具名称列表
        """
        return list(self.config.keys())
    
    def validate_tool_config(self, tool_name: str) -> bool:
        """
        验证工具配置是否有效
        
        Args:
            tool_name: 工具名称
            
        Returns:
            配置是否有效
        """
        if tool_name not in self.config:
            return False
        
        tool_config = self.config[tool_name]
        required_fields = ["url", "headers"]
        
        for field in required_fields:
            if field not in tool_config:
                logger.error(f"工具 {tool_name} 缺少必需配置字段: {field}")
                return False
        
        if "Authorization" not in tool_config["headers"]:
            logger.error(f"工具 {tool_name} 缺少Authorization头")
            return False
        
        return True


# 使用示例
if __name__ == "__main__":
    # 创建MCP客户端实例
    mcp_client = MCPClient()
    
    # 调用web-search工具的common_search方法
    try:
        result = mcp_client.call_tool(
            tool_name="web-search",
            method="common_search",
            arguments={
                "query": "房地产市场趋势 2024",
                "max_results": 5
            }
        )
        print("调用结果:", json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"调用失败: {e}") 