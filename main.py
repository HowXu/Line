from client.window import MainWindow
from server.factory import ManagerFactory
from abc import ABC, abstractmethod

# 代理模式

class IApplication(ABC):
    """应用程序接口"""
    
    @abstractmethod
    def launch(self):
        """启动应用程序"""
        pass
    
    @abstractmethod
    def shutdown(self):
        """关闭应用程序"""
        pass


class RealApplication:
    """真实应用程序类"""
    
    def __init__(self):
        self.factory = ManagerFactory()
        self.dataManager = None
        self.deepseekAPI = None
        self.app = None
    
    def initialize(self):
        """初始化应用程序组件"""
        print("初始化应用程序组件...")
        self.dataManager = self.factory.get_manager("data")
        self.deepseekAPI = self.factory.get_manager("api")
        self.app = MainWindow(self.dataManager, self.deepseekAPI)
        print("初始化完成")
    
    def launch(self):
        """启动应用程序"""
        if self.app is None:
            self.initialize()
        print("启动 Line AI Chat Application...")
        self.app.run()
    
    def shutdown(self):
        """关闭应用程序"""
        print("正在关闭应用程序...")
        if self.app:
            print("清理资源...")
        print("应用程序已关闭")


class ApplicationProxy(IApplication):
    """应用程序代理类"""
    
    def __init__(self):
        self.real_app = None
        self._initialized = False
        self._log_enabled = True
        self._validation_enabled = True
    
    def _log(self, message: str):
        """日志记录"""
        if self._log_enabled:
            print(f"[Proxy Log] {message}")
    
    def _validate_environment(self) -> bool:
        """验证运行环境"""
        if not self._validation_enabled:
            return True
        
        self._log("验证运行环境...")
        
        try:
            # 检查必要的组件
            from client.window import MainWindow
            from server.factory import ManagerFactory
            
            self._log("✓ 核心模块检查通过")
            return True
            
        except ImportError as e:
            self._log(f"✗ 模块导入失败：{e}")
            return False
    
    def _pre_launch_checks(self):
        """启动前检查"""
        self._log("执行启动前检查...")
        
        if not self._validate_environment():
            raise RuntimeError("环境验证失败，无法启动应用程序")
        
        self._log("✓ 启动前检查通过")
    
    def _post_launch_actions(self):
        """启动后操作"""
        self._log("应用程序已成功启动")
    
    def launch(self):
        """代理启动方法"""
        self._log("请求启动应用程序")
        
        # 启动前检查
        self._pre_launch_checks()
        
        # 创建并初始化真实应用程序
        if self.real_app is None:
            self._log("创建应用程序实例...")
            self.real_app = RealApplication()
        
        # 启动应用程序
        try:
            self.real_app.launch()
            self._post_launch_actions()
        except Exception as e:
            self._log(f"启动失败：{e}")
            raise
    
    def shutdown(self):
        """代理关闭方法"""
        self._log("请求关闭应用程序")
        
        if self.real_app:
            self.real_app.shutdown()
        
        self._log("代理已关闭")
    
    def enable_logging(self, enabled: bool = True):
        """启用/禁用日志"""
        self._log_enabled = enabled
        self._log(f"日志功能已{'启用' if enabled else '禁用'}")
    
    def enable_validation(self, enabled: bool = True):
        """启用/禁用环境验证"""
        self._validation_enabled = enabled
        self._log(f"环境验证已{'启用' if enabled else '禁用'}")


def main():
    """主函数 - 使用代理模式启动应用程序"""
    # 创建应用程序代理
    app_proxy = ApplicationProxy()
    
    # 可选：配置代理功能
    app_proxy.enable_logging(True)  # 启用日志
    app_proxy.enable_validation(True)  # 启用环境验证
    
    # 通过代理启动应用程序
    try:
        app_proxy.launch()
    except Exception as e:
        print(f"应用程序启动失败：{e}")
        app_proxy.shutdown()
    finally:
        app_proxy.shutdown()


if __name__ == "__main__":
    main()
