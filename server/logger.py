# 适配器模式
class DebugLogger:
    def __init__(self):
        pass
    def log(self, msg: str):
        print(f"[Debug] {msg}")

class ReleaseLogger:
    def __init__(self):
        pass
    def log(self, msg: str):
        print(f"[Release] {msg}")

class LoggerAdapter:
    def __init__(self, logger: DebugLogger):
        self.logger = logger
    def log(self, msg: str):
        self.logger.log(msg)
