import psycopg2
from psycopg2 import OperationalError

from server.data import DataManager

# database location
conn_params = {
    'host': '127.0.0.1',
    'port': '5432',
    'database': 'records',
    'user': 'howxu',
    'password': 'howxu'
}


class SQLManager:
    def __init__(self,dataManager: DataManager):
        self.connection = None
        self.cursor = None
        self.dataManager = dataManager
        
    def connect(self):
        try:
            self.connection = psycopg2.connect(**conn_params)
            self.cursor = self.connection.cursor()
        except OperationalError as e:
            print(f"连接失败: {e}")
    
    def load_history_to_both(self):
        # 实际上不会是None 因为会在connect之前就报错
        try:
            self.cursor.execute("""
                                SELECT * FROM (
                                    SELECT * FROM chat_messages 
                                    ORDER BY updated_at DESC 
                                    LIMIT 128
                                ) AS subquery 
                                ORDER BY updated_at ASC;""")
            response = self.cursor.fetchall()
            for row in response:
                is_me = (row[1] == "me")
                if is_me:
                    self.dataManager.add_display_context("me",row[2],row[4])
                    self.dataManager.add_inner_context("me",row[2],row[4])
                else:
                    self.dataManager.add_display_context("ta",row[2],row[4])
                    self.dataManager.add_inner_context("ta",row[2],row[4])
        except Exception as e:
            print(f"查询失败: {e}")
            
    def load_history(self):
        # 实际上不会是None 因为会在connect之前就报错
        try:
            self.cursor.execute("""
                                SELECT * FROM (
                                    SELECT * FROM chat_messages 
                                    ORDER BY updated_at DESC 
                                    LIMIT 128
                                ) AS subquery 
                                ORDER BY updated_at ASC;""")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"查询失败: {e}")
            return []
        
    def save_new(self, sender, text):
        try:
            self.cursor.execute(
                "INSERT INTO chat_messages (sender, content,created_at,updated_at) VALUES (%s, %s, NOW(), NOW())",
                (sender, text)
            )
            self.connection.commit()
        except Exception as e:
            print(f"保存消息失败: {e}")
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()