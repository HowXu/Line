from abc import ABC, abstractmethod

# ---------------------------------------------------------------------------
# 适配器模式（Adapter Pattern）
# ---------------------------------------------------------------------------
# 角色：
#   - Target（目标抽象）：ILogger           —— 业务层期望的统一接口
#   - Adaptee（被适配者）：DebugLogger / ReleaseLogger
#         —— 现成的、不同接口的日志输出能力
#   - Adapter（适配器）：DebugLoggerAdapter / ReleaseLoggerAdapter
#         —— 实现 Target 接口，内部委托给 Adaptee，并补齐接口差异
# ---------------------------------------------------------------------------


class ILogger(ABC):
    """目标抽象：业务层期望的统一日志接口。"""

    @abstractmethod
    def log(self, msg: str, level: str = "INFO"):
        pass

    @abstractmethod
    def debug(self, msg: str):
        pass

    @abstractmethod
    def info(self, msg: str):
        pass

    @abstractmethod
    def warn(self, msg: str):
        pass

    @abstractmethod
    def error(self, msg: str):
        pass


class DebugLogger:
    """被适配者 A：现成的"只接受字符串、只输出到 stdout"的日志对象。"""

    def __init__(self):
        self._prefix = "[Debug]"

    def log(self, msg: str):
        # 原接口：只接 msg，没有 level/前缀
        print(f"{self._prefix} {msg}")


class ReleaseLogger:
    """被适配者 B：另一个不同接口的日志对象。"""

    def __init__(self):
        self._tag = "[Release]"

    def log(self, msg: str):
        # 原接口：只接 msg，tag 写死在内部
        print(f"{self._tag} {msg}")


class DebugLoggerAdapter(ILogger):
    """把 DebugLogger 适配成 ILogger。"""

    def __init__(self, adaptee: DebugLogger):
        self._adaptee = adaptee

    def log(self, msg: str, level: str = "INFO"):
        # 接口转换：补出 level
        self._adaptee.log(f"[{level}] {msg}")

    def debug(self, msg: str):
        self._adaptee.log(msg)

    def info(self, msg: str):
        self._adaptee.log(msg)

    def warn(self, msg: str):
        self._adaptee.log(f"[WARN] {msg}")

    def error(self, msg: str):
        self._adaptee.log(f"[ERROR] {msg}")


class ReleaseLoggerAdapter(ILogger):
    """把 ReleaseLogger 适配成 ILogger。"""

    def __init__(self, adaptee: ReleaseLogger):
        self._adaptee = adaptee

    def log(self, msg: str, level: str = "INFO"):
        self._adaptee.log(f"[{level}] {msg}")

    def debug(self, msg: str):
        self._adaptee.log(msg)

    def info(self, msg: str):
        self._adaptee.log(msg)

    def warn(self, msg: str):
        self._adaptee.log(f"[WARN] {msg}")

    def error(self, msg: str):
        self._adaptee.log(f"[ERROR] {msg}")


# ---------------------------------------------------------------------------
# 兼容层：保留旧类名 LoggerAdapter，避免破坏历史引用
# ---------------------------------------------------------------------------
class LoggerAdapter(ILogger):
    """
    通用适配器：自动包装任意带 .log(msg) 方法的对象到 ILogger 接口。
    旧调用方代码 `LoggerAdapter(debug_logger)` 仍可工作。
    """

    def __init__(self, logger):
        self._adaptee = logger

    def log(self, msg: str, level: str = "INFO"):
        self._adaptee.log(f"[{level}] {msg}")

    def debug(self, msg: str):
        self._adaptee.log(msg)

    def info(self, msg: str):
        self._adaptee.log(msg)

    def warn(self, msg: str):
        self._adaptee.log(f"[WARN] {msg}")

    def error(self, msg: str):
        self._adaptee.log(f"[ERROR] {msg}")
