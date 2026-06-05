from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# 工厂方法模式（Factory Method Pattern）
# ---------------------------------------------------------------------------
# 角色：
#   - Product（抽象产品）：LogStrategy
#   - ConcreteProduct（具体产品）：APILogStrategy / RequestLogStrategy /
#                                   ResponseLogStrategy / DebugLogStrategy
#   - Creator（抽象创建者）：LogStrategyCreator
#         - 声明工厂方法 create_strategy()，由子类决定具体产品类型
#   - ConcreteCreator（具体创建者）：APILogCreator / RequestLogCreator /
#                                    ResponseLogCreator / DebugLogCreator
#         - 实现 create_strategy()，返回对应的具体策略实例
#
# 设计意图：将"对象创建"延迟到子类，调用方只依赖 Creator 抽象层，
#          新增日志类型时只需新增一组 Product + Creator，不修改既有工厂逻辑。
# ---------------------------------------------------------------------------


# ============================================================
# Product：抽象产品
# ============================================================
class LogStrategy(ABC):
    """日志策略接口（Product）。"""

    @abstractmethod
    def format(self, data: Any, max_length: int = 200) -> str:
        """
        格式化日志数据。

        Args:
            data: 待格式化的原始数据。
            max_length: 输出最大长度。

        Returns:
            格式化后的字符串。
        """
        pass

    @abstractmethod
    def log(self, data: Any, prefix: str = "", max_length: int = 200):
        """
        输出一条日志。

        Args:
            data: 待输出数据。
            prefix: 日志前缀（模块名）。
            max_length: 输出最大长度。
        """
        pass


# ============================================================
# ConcreteProduct：具体产品
# ============================================================
class APILogStrategy(LogStrategy):
    """API 调用日志策略。"""

    def format(self, data: Any, max_length: int = 200) -> str:
        if data is None:
            return "None"
        data_str = str(data)
        if len(data_str) > max_length:
            truncated_len = max_length - 20
            data_str = data_str[:truncated_len] + f"\n... [截断，共{len(str(data))}字符]"
        return data_str

    def log(self, data: Any, prefix: str = "API", max_length: int = 200):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_data = self.format(data, max_length)
        print(f"[{timestamp}] [{prefix}] {formatted_data}")


class RequestLogStrategy(LogStrategy):
    """HTTP 请求日志策略。"""

    def format(self, data: Any, max_length: int = 300) -> str:
        if data is None:
            return "None"
        if isinstance(data, dict):
            import json
            try:
                data_str = json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                data_str = str(data)
        else:
            data_str = str(data)
        if len(data_str) > max_length:
            lines = data_str.split("\n")
            if len(lines) > 20:
                data_str = "\n".join(lines[:10]) + "\n...\n" + "\n".join(lines[-5:])
                data_str += f"\n... [截断，共{len(lines)}行]"
            else:
                truncated_len = max_length - 30
                data_str = data_str[:truncated_len] + f"\n... [截断，共{len(str(data))}字符]"
        return data_str

    def log(self, data: Any, prefix: str = "Request", max_length: int = 300):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_data = self.format(data, max_length)
        print(f"\n{'=' * 60}")
        print(f"[{timestamp}] [{prefix}]")
        print(f"{'=' * 60}")
        print(formatted_data)
        print(f"{'=' * 60}\n")


class ResponseLogStrategy(LogStrategy):
    """HTTP 响应日志策略。"""

    def format(self, data: Any, max_length: int = 500) -> str:
        if data is None:
            return "None"
        if isinstance(data, dict):
            import json
            try:
                data_str = json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                data_str = str(data)
        else:
            data_str = str(data)
        if len(data_str) > max_length:
            lines = data_str.split("\n")
            if len(lines) > 30:
                data_str = "\n".join(lines[:15]) + "\n...\n" + "\n".join(lines[-10:])
                data_str += f"\n... [截断，共{len(lines)}行]"
            else:
                truncated_len = max_length - 30
                data_str = data_str[:truncated_len] + f"\n... [截断，共{len(str(data))}字符]"
        return data_str

    def log(self, data: Any, prefix: str = "Response", max_length: int = 500):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_data = self.format(data, max_length)
        print(f"\n{'=' * 60}")
        print(f"[{timestamp}] [{prefix}]")
        print(f"{'=' * 60}")
        print(formatted_data)
        print(f"{'=' * 60}\n")


class DebugLogStrategy(LogStrategy):
    """调试日志策略。"""

    def format(self, data: Any, max_length: int = 150) -> str:
        if data is None:
            return "None"
        data_str = str(data)
        if len(data_str) > max_length:
            truncated_len = max_length - 20
            data_str = data_str[:truncated_len] + f"\n... [截断]"
        return data_str

    def log(self, data: Any, prefix: str = "Debug", max_length: int = 150):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        formatted_data = self.format(data, max_length)
        print(f"[{timestamp}] [{prefix}] {formatted_data}")


# ============================================================
# Creator：抽象创建者
# ============================================================
class LogStrategyCreator(ABC):
    """
    抽象创建者（Creator）。

    声明工厂方法 create_strategy()，由子类返回具体 LogStrategy 实例。
    调用方只持有 Creator 引用，不直接 new 出具体策略。
    """

    @abstractmethod
    def create_strategy(self) -> LogStrategy:
        """工厂方法：返回具体日志策略实例。"""
        pass

    def log(self, data: Any, prefix: str = "", max_length: int = 200):
        """
        模板方法：使用工厂方法构造策略并执行 log。
        由 Creator 基类统一约束调用流程。
        """
        strategy = self.create_strategy()
        strategy.log(data, prefix=prefix, max_length=max_length)


# ============================================================
# ConcreteCreator：具体创建者
# ============================================================
class APILogCreator(LogStrategyCreator):
    """工厂方法：创建 APILogStrategy。"""

    def create_strategy(self) -> LogStrategy:
        return APILogStrategy()


class RequestLogCreator(LogStrategyCreator):
    """工厂方法：创建 RequestLogStrategy。"""

    def create_strategy(self) -> LogStrategy:
        return RequestLogStrategy()


class ResponseLogCreator(LogStrategyCreator):
    """工厂方法：创建 ResponseLogStrategy。"""

    def create_strategy(self) -> LogStrategy:
        return ResponseLogStrategy()


class DebugLogCreator(LogStrategyCreator):
    """工厂方法：创建 DebugLogStrategy。"""

    def create_strategy(self) -> LogStrategy:
        return DebugLogStrategy()


# ============================================================
# LogContext：策略模式的上下文（Context）
# 同时也是工厂方法模式的客户端。
# ============================================================
class LogContext:
    """
    策略上下文（Context）。

    持有当前 Creator，由调用方通过 set_creator() 在运行时切换
    日志策略族；调用 write() 时由 Context 委托给当前 Creator，
    Creator 再通过工厂方法 create_strategy() 实例化具体策略。
    """

    def __init__(self, creator: LogStrategyCreator = None):
        self._creator = creator or APILogCreator()

    def set_creator(self, creator: LogStrategyCreator):
        self._creator = creator

    def write(self, data: Any, prefix: str = "", max_length: int = 200):
        self._creator.log(data, prefix=prefix, max_length=max_length)
