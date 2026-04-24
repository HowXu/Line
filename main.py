from client.window import MainWindow
from server.factory import ManagerFactory

def main():
    factory = ManagerFactory()
    dataManager = factory.get_manager("data")
    deepseekAPI = factory.get_manager("api")
    app = MainWindow(dataManager,deepseekAPI)
    app.run()

if __name__ == "__main__":
    main()