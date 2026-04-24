from server.log_strategy import (
    LogStrategy,
    APILogStrategy,
    RequestLogStrategy,
    ResponseLogStrategy,
    DebugLogStrategy
)

# 简单工厂模式

class LogFormatterFactory:
    
    _strategies = {
        'api': APILogStrategy,
        'request': RequestLogStrategy,
        'response': ResponseLogStrategy,
        'debug': DebugLogStrategy
    }
    
    @classmethod
    def create(cls, log_type: str = 'api') -> LogStrategy:
        """
        策略
        
        Args:
            log_type: 日志类型 ('api', 'request', 'response', 'debug')
            
        Returns:
            LogStrategy: 日志策略实例
            
        Raises:
            ValueError: 无效的日志类型
        """
        strategy_class = cls._strategies.get(log_type.lower())
        
        if strategy_class is None:
            raise ValueError(
                f"Unknown log type: {log_type}\n"
                f"Available types: {', '.join(cls._strategies.keys())}"
            )
        
        return strategy_class()
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """
        注册
        
        Args:
            name: 策略名称
            strategy_class: 策略类
        """
        if not issubclass(strategy_class, LogStrategy):
            raise TypeError("Strategy class must inherit from LogStrategy")
        
        cls._strategies[name.lower()] = strategy_class
    
    @classmethod
    def get_available_strategies(cls) -> list:
        return list(cls._strategies.keys())


# 便捷函数
def get_logger(log_type: str = 'api') -> LogStrategy:
    """
    获取策略实例
    
    Args:
        log_type: 日志类型
        
    Returns:
        LogStrategy: 策略实例
    """
    return LogFormatterFactory.create(log_type)
