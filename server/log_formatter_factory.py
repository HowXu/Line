from server.log_strategy import (
    LogStrategy,
    LogStrategyCreator,
    APILogStrategy,
    RequestLogStrategy,
    ResponseLogStrategy,
    DebugLogStrategy,
    APILogCreator,
    RequestLogCreator,
    ResponseLogCreator,
    DebugLogCreator,
)

# 简单工厂 + 工厂方法 双视图
#   - LogFormatterFactory.create()：经典简单工厂，根据字符串键直接返回具体策略
#   - LogFormatterFactory.get_creator()：工厂方法模式入口，返回对应 LogStrategyCreator
#   - get_logger() / get_creator()：便捷函数


class LogFormatterFactory:
    """
    日志策略的工厂集合：

    - create() 走"简单工厂"分支：键 -> 策略类 -> 实例
    - get_creator() 走"工厂方法"分支：键 -> Creator（Creator 内部决定实例化哪个产品）
    """

    _strategies = {
        "api": APILogStrategy,
        "request": RequestLogStrategy,
        "response": ResponseLogStrategy,
        "debug": DebugLogStrategy,
    }

    _creators = {
        "api": APILogCreator,
        "request": RequestLogCreator,
        "response": ResponseLogCreator,
        "debug": DebugLogCreator,
    }

    @classmethod
    def create(cls, log_type: str = "api") -> LogStrategy:
        """简单工厂：根据类型直接返回 LogStrategy 实例。"""
        strategy_class = cls._strategies.get(log_type.lower())
        if strategy_class is None:
            raise ValueError(
                f"Unknown log type: {log_type}\n"
                f"Available types: {', '.join(cls._strategies.keys())}"
            )
        return strategy_class()

    @classmethod
    def get_creator(cls, log_type: str = "api") -> LogStrategyCreator:
        """工厂方法：返回具体 LogStrategyCreator，由 Creator 自行决定实例化哪个产品。"""
        creator_class = cls._creators.get(log_type.lower())
        if creator_class is None:
            raise ValueError(
                f"Unknown log type: {log_type}\n"
                f"Available types: {', '.join(cls._creators.keys())}"
            )
        return creator_class()

    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """注册新的具体策略。"""
        if not issubclass(strategy_class, LogStrategy):
            raise TypeError("Strategy class must inherit from LogStrategy")
        cls._strategies[name.lower()] = strategy_class

    @classmethod
    def register_creator(cls, name: str, creator_class: type):
        """注册新的具体创建者。"""
        if not issubclass(creator_class, LogStrategyCreator):
            raise TypeError("Creator class must inherit from LogStrategyCreator")
        cls._creators[name.lower()] = creator_class

    @classmethod
    def get_available_strategies(cls) -> list:
        return list(cls._strategies.keys())


def get_logger(log_type: str = "api") -> LogStrategy:
    """便捷函数：走简单工厂。"""
    return LogFormatterFactory.create(log_type)


def get_creator(log_type: str = "api") -> LogStrategyCreator:
    """便捷函数：走工厂方法。"""
    return LogFormatterFactory.get_creator(log_type)
