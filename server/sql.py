import psycopg2
from psycopg2 import OperationalError
from server.data import DataManager
from abc import ABC, abstractmethod

# database location
conn_params = {
    "host": "127.0.0.1",
    "port": "5432",
    "database": "records",
    "user": "howxu",
    "password": "howxu",
}

# ---------------------------------------------------------------------------
# 抽象工厂模式（Abstract Factory Pattern）
# ---------------------------------------------------------------------------
# 角色：
#   - AbstractFactory（抽象工厂）：SQLFactory / ConnectionFactory
#   - ConcreteFactory（具体工厂）：PostgreSQLFactory / PostgreSQLConnectionFactory
#   - AbstractProduct（抽象产品）：SQLManager / SQLConnection
#   - ConcreteProduct（具体产品）：PostgreSQLManager / PostgreSQLConnection
#   - Client（客户端）：ManagerFactory
#
# 设计意图：以"数据库族"为切换单位，工厂接口一次性产出一组相关产品
#          （Manager + Connection），确保系列产品之间互相兼容。
# ---------------------------------------------------------------------------


# ============================================================
# 抽象产品 A：SQLManager
# ============================================================
class SQLManager(ABC):
    """抽象产品：SQL 管理器。"""

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def load_history_to_both(self):
        pass

    @abstractmethod
    def load_history(self):
        pass

    @abstractmethod
    def save_new(self, sender, text):
        pass

    @abstractmethod
    def close(self):
        pass


# ============================================================
# 抽象产品 B：SQLConnection
# （同一数据库族中第二个相关产品，体现"产品族"概念）
# ============================================================
class SQLConnection(ABC):
    """抽象产品：连接/事务对象（同一产品族的互补件）。"""

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        pass


# ============================================================
# 具体产品 A1：PostgreSQLManager
# ============================================================
class PostgreSQLManager(SQLManager):
    def __init__(self, dataManager: DataManager):
        self.connection = None
        self.cursor = None
        self.dataManager = dataManager

    def connect(self):
        try:
            self.connection = psycopg2.connect(**conn_params)
            self.cursor = self.connection.cursor()
        except OperationalError as e:
            print(f"连接失败：{e}")

    def load_history_to_both(self):
        try:
            self.cursor.execute(
                """
                SELECT * FROM (
                    SELECT * FROM chat_messages
                    ORDER BY updated_at DESC
                    LIMIT 128
                ) AS subquery
                ORDER BY updated_at ASC;
                """
            )
            response = self.cursor.fetchall()
            for row in response:
                is_me = row[1] == "me"
                if is_me:
                    self.dataManager.add_display_context("me", row[2], row[4])
                    self.dataManager.add_inner_context("me", row[2], row[4])
                else:
                    self.dataManager.add_display_context("ta", row[2], row[4])
                    self.dataManager.add_inner_context("ta", row[2], row[4])
        except Exception as e:
            print(f"查询失败：{e}")

    def load_history(self):
        try:
            self.cursor.execute(
                """
                SELECT * FROM (
                    SELECT * FROM chat_messages
                    ORDER BY updated_at DESC
                    LIMIT 128
                ) AS subquery
                ORDER BY updated_at ASC;
                """
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"查询失败：{e}")
            return []

    def save_new(self, sender, text):
        try:
            self.cursor.execute(
                "INSERT INTO chat_messages (sender, content,created_at,updated_at) "
                "VALUES (%s, %s, NOW(), NOW())",
                (sender, text),
            )
            self.connection.commit()
        except Exception as e:
            print(f"保存消息失败：{e}")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


# ============================================================
# 具体产品 B1：PostgreSQLConnection
# ============================================================
class PostgreSQLConnection(SQLConnection):
    """PostgreSQL 连接对象（事务、连接复用层面的产品）。"""

    def __init__(self):
        self._conn = None
        self._in_transaction = False

    def open(self):
        try:
            self._conn = psycopg2.connect(**conn_params)
            self._in_transaction = False
        except OperationalError as e:
            print(f"[PostgreSQLConnection] 连接失败：{e}")

    def commit(self):
        if self._conn and self._in_transaction:
            self._conn.commit()
            self._in_transaction = False

    def rollback(self):
        if self._conn and self._in_transaction:
            self._conn.rollback()
            self._in_transaction = False

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def is_alive(self) -> bool:
        return self._conn is not None and self._conn.closed == 0

    @property
    def raw(self):
        return self._conn


# ============================================================
# 抽象工厂：同时产出两个相关产品（产品族）
# ============================================================
class SQLFactory(ABC):
    """抽象工厂：产出 SQLManager + SQLConnection 一族相关产品。"""

    @abstractmethod
    def create_sql_manager(self, dataManager: DataManager) -> SQLManager:
        pass

    @abstractmethod
    def create_sql_connection(self) -> SQLConnection:
        pass


# ============================================================
# 具体工厂：PostgreSQL 工厂（同时产出 PostgreSQL 系产品）
# ============================================================
class PostgreSQLFactory(SQLFactory):
    """PostgreSQL 工厂：产出一组兼容的 PostgreSQL 产品。"""

    def create_sql_manager(self, dataManager: DataManager) -> SQLManager:
        return PostgreSQLManager(dataManager)

    def create_sql_connection(self) -> SQLConnection:
        return PostgreSQLConnection()


# ============================================================
# （可选）扩展族：MySQL 工厂
# 体现"产品族可扩展"的能力，使抽象工厂优势真正落地。
# ============================================================
class MySQLManager(SQLManager):
    """占位实现：示意 MySQL 族的 Manager，验证工厂可替换。"""

    def __init__(self, dataManager: DataManager):
        self._dataManager = dataManager
        self._connected = False

    def connect(self):
        self._connected = True

    def load_history_to_both(self):
        pass

    def load_history(self):
        return []

    def save_new(self, sender, text):
        pass

    def close(self):
        self._connected = False


class MySQLConnection(SQLConnection):
    """占位实现：示意 MySQL 族的 Connection。"""

    def open(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

    def is_alive(self) -> bool:
        return False


class MySQLFactory(SQLFactory):
    """MySQL 工厂：可作为 PostgreSQLFactory 的可替换实现。"""

    def create_sql_manager(self, dataManager: DataManager) -> SQLManager:
        return MySQLManager(dataManager)

    def create_sql_connection(self) -> SQLConnection:
        return MySQLConnection()


# ============================================================
# 工厂选择器：根据配置决定实例化哪个具体工厂
# ============================================================
def create_sql_factory(vendor: str = "postgresql") -> SQLFactory:
    """根据数据库厂商选择具体工厂。"""
    vendor = vendor.lower()
    if vendor == "postgresql":
        return PostgreSQLFactory()
    if vendor == "mysql":
        return MySQLFactory()
    raise ValueError(f"Unsupported SQL vendor: {vendor}")
