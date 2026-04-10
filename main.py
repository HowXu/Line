from client.window import MainWindow
from server.ai import DeepSeekAPI
from server.data import DataManager
from server.sql import SQLManager

def main():
    dataManager = DataManager()
    sqlManager = SQLManager(dataManager)
    sqlManager.connect()
    sqlManager.load_history_to_both()
    deepseekAPI = DeepSeekAPI(dataManager,sqlManager)
    app = MainWindow(dataManager,deepseekAPI)
    app.run()

if __name__ == "__main__":
    main()