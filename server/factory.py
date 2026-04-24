from server.data import DataManager
from server.sql import SQLManager, PostgreSQLFactory, PostgreSQLManager
from server.ai import DeepSeekAPI

# 抽象工厂模式 + 简单工厂模式
class ManagerFactory:
    def __init__(self):
        self.dataManager = DataManager()
        # 使用抽象工厂创建 SQL 管理器
        sql_factory = PostgreSQLFactory()
        self.sqlManager = sql_factory.create_sql_manager(self.dataManager)
        self.sqlManager.connect()
        self.sqlManager.load_history_to_both()
        self.deepseekAPI = DeepSeekAPI(self.dataManager,self.sqlManager)
    
    def get_manager(self,category: str):
        match category:
            case "sql":
                return self.sqlManager
            case "data":
                return self.dataManager
            case "api":
                return self.deepseekAPI
