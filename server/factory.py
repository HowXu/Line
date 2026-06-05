from server.data import DataManager
from server.sql import SQLManager, create_sql_factory
from server.ai import DeepSeekAPI

# 抽象工厂 + 简单工厂 双视图
#   - ManagerFactory.get_manager(): 简单工厂（按字符串键返回具体管理器）
#   - ManagerFactory 的构造函数内部调用抽象工厂 create_sql_factory()
#     来获得一组兼容的 SQL 产品（Manager + Connection），体现抽象工厂意图。
SQL_VENDOR = "postgresql"


class ManagerFactory:
    """
    管理器集合工厂。

    - 通过 create_sql_factory() 拿到抽象工厂（产品族）
    - 抽象工厂一次性产出 SQLManager + SQLConnection 一组兼容产品
    - 本类对外按字符串键暴露各类管理器（DataManager / DeepSeekAPI / SQLManager）
    """

    def __init__(self, sql_vendor: str = SQL_VENDOR):
        self.dataManager = DataManager()

        # 抽象工厂：一次性产出 SQLManager + SQLConnection 一族
        sql_factory = create_sql_factory(sql_vendor)
        self.sqlManager: SQLManager = sql_factory.create_sql_manager(self.dataManager)
        self.sqlConnection = sql_factory.create_sql_connection()
        if hasattr(self.sqlConnection, "open"):
            self.sqlConnection.open()

        self.sqlManager.connect()
        self.sqlManager.load_history_to_both()
        self.deepseekAPI = DeepSeekAPI(self.dataManager, self.sqlManager)

    def get_manager(self, category: str):
        """简单工厂入口：按字符串键返回具体管理器。"""
        match category:
            case "sql":
                return self.sqlManager
            case "connection":
                return self.sqlConnection
            case "data":
                return self.dataManager
            case "api":
                return self.deepseekAPI
            case _:
                raise ValueError(f"Unknown manager category: {category}")
