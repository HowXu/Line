from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

# 工厂方法模式

class LogStrategy(ABC):
    """日志策略接口"""
    
    @abstractmethod
    def format(self, data: Any, max_length: int = 200) -> str:
        """
        格式化
        
        Args:
            data: 要格式化的数据
            max_length: 最大长度，超过则截断
            
        Returns:
            格式化后的字符串
        """
        pass
    
    @abstractmethod
    def log(self, data: Any, prefix: str = "", max_length: int = 200):
        """
        输出

        Args:
            data: 要输出的数据
            prefix: 日志前缀
            max_length: 最大长度
        """
        pass


class APILogStrategy(LogStrategy):
    
    def format(self, data: Any, max_length: int = 200) -> str:
        """格式化 API 数据"""
        if data is None:
            return "None"
        
        # 转换为字符串
        data_str = str(data)
        
        # 截断处理
        if len(data_str) > max_length:
            truncated_len = max_length - 20  # 预留空间给截断提示
            data_str = data_str[:truncated_len] + f"\n... [截断，共{len(str(data))}字符]"
        
        return data_str
    
    def log(self, data: Any, prefix: str = "API", max_length: int = 200):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_data = self.format(data, max_length)
        print(f"[{timestamp}] [{prefix}] {formatted_data}")


class RequestLogStrategy(LogStrategy):
    
    def format(self, data: Any, max_length: int = 300) -> str:
        if data is None:
            return "None"
        
        # 如果是字典，格式化 JSON
        if isinstance(data, dict):
            import json
            try:
                data_str = json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                data_str = str(data)
        else:
            data_str = str(data)
        
        # 截断处理
        if len(data_str) > max_length:
            lines = data_str.split('\n')
            if len(lines) > 20:  # 如果超过 20 行
                data_str = '\n'.join(lines[:10]) + '\n...\n' + '\n'.join(lines[-5:])
                data_str += f"\n... [截断，共{len(lines)}行]"
            else:
                truncated_len = max_length - 30
                data_str = data_str[:truncated_len] + f"\n... [截断，共{len(str(data))}字符]"
        
        return data_str
    
    def log(self, data: Any, prefix: str = "Request", max_length: int = 300):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_data = self.format(data, max_length)
        print(f"\n{'='*60}")
        print(f"[{timestamp}] [{prefix}]")
        print(f"{'='*60}")
        print(formatted_data)
        print(f"{'='*60}\n")


class ResponseLogStrategy(LogStrategy):
    
    def format(self, data: Any, max_length: int = 500) -> str:
        if data is None:
            return "None"
        
        # 如果是字典，格式化 JSON
        if isinstance(data, dict):
            import json
            try:
                data_str = json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                data_str = str(data)
        else:
            data_str = str(data)
        
        # 截断处理
        if len(data_str) > max_length:
            lines = data_str.split('\n')
            if len(lines) > 30:  # 如果超过 30 行
                data_str = '\n'.join(lines[:15]) + '\n...\n' + '\n'.join(lines[-10:])
                data_str += f"\n... [截断，共{len(lines)}行]"
            else:
                truncated_len = max_length - 30
                data_str = data_str[:truncated_len] + f"\n... [截断，共{len(str(data))}字符]"
        
        return data_str
    
    def log(self, data: Any, prefix: str = "Response", max_length: int = 500):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_data = self.format(data, max_length)
        print(f"\n{'='*60}")
        print(f"[{timestamp}] [{prefix}]")
        print(f"{'='*60}")
        print(formatted_data)
        print(f"{'='*60}\n")


class DebugLogStrategy(LogStrategy):
    
    def format(self, data: Any, max_length: int = 150) -> str:
        if data is None:
            return "None"
        
        data_str = str(data)
        
        # 截断处理
        if len(data_str) > max_length:
            truncated_len = max_length - 20
            data_str = data_str[:truncated_len] + f"\n... [截断]"
        
        return data_str
    
    def log(self, data: Any, prefix: str = "Debug", max_length: int = 150):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # 精确到毫秒
        formatted_data = self.format(data, max_length)
        print(f"[{timestamp}] [{prefix}] {formatted_data}")
