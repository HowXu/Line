from client.window import MainWindow
from server.factory import ManagerFactory
from abc import ABC, abstractmethod
import threading

# ---------------------------------------------------------------------------
# 代理模式（Proxy Pattern）
# ---------------------------------------------------------------------------
# 角色：
#   - Subject（抽象主题）：IApplication
#         - 业务层期望的统一接口
#   - RealSubject（真实主题）：RealApplication
#         - 实际执行业务的对象
#   - Proxy（代理）：ApplicationProxy
#         - 控制对 RealApplication 的访问：
#             * 启动前预检（环境/依赖/参数）
#             * 延迟实例化（Lazy Initialization）
#             * 访问控制（鉴权/重复启动检测）
#             * 异常转换与日志
# ---------------------------------------------------------------------------


class IApplication(ABC):
    """抽象主题：业务层期望的统一应用接口。"""

    @abstractmethod
    def launch(self):
        """启动应用程序。"""
        pass

    @abstractmethod
    def shutdown(self):
        """关闭应用程序。"""
        pass


class RealApplication(IApplication):
    """真实主题：实际执行业务逻辑。"""

    def __init__(self):
        self.factory: ManagerFactory = None
        self.dataManager = None
        self.deepseekAPI = None
        self.app: MainWindow = None
        self._initialized = False
        self._running = False

    def initialize(self):
        """初始化应用程序组件。"""
        print("初始化应用程序组件...")
        self.factory = ManagerFactory()
        self.dataManager = self.factory.get_manager("data")
        self.deepseekAPI = self.factory.get_manager("api")
        self.app = MainWindow(self.dataManager, self.deepseekAPI)
        self._initialized = True
        print("初始化完成")

    def launch(self):
        """启动应用程序（实际执行）。"""
        if not self._initialized:
            self.initialize()
        if self._running:
            print("[RealApplication] 已在运行中，跳过重复启动")
            return
        self._running = True
        print("启动 Line AI Chat Application...")
        self.app.run()
        self._running = False

    def shutdown(self):
        """关闭应用程序（实际执行）。"""
        print("正在关闭应用程序...")
        if self.app:
            print("清理资源...")
        self._running = False
        print("应用程序已关闭")


class ApplicationProxy(IApplication):
    """代理：控制对 RealApplication 的访问。"""

    # 进程级可重入锁
    _state_lock = threading.Lock()

    def __init__(self, access_token: str = "default-token"):
        self._access_token = access_token
        self._real_app: RealApplication = None  # 延迟实例化
        self._log_enabled = True
        self._validation_enabled = True
        self._is_launched = False
        self._access_count = 0

    # ---------------- 访问控制 ----------------
    def _authorize(self) -> bool:
        """简单鉴权：检查 access_token 非空。"""
        return bool(self._access_token)

    def _check_double_launch(self) -> bool:
        """防止同一代理实例被重复启动。"""
        if self._is_launched:
            print("[Proxy] 拒绝重复启动")
            return False
        return True

    # ---------------- 内部日志 ----------------
    def _log(self, message: str):
        if self._log_enabled:
            print(f"[Proxy Log] {message}")

    # ---------------- 启动前检查 ----------------
    def _validate_environment(self) -> bool:
        if not self._validation_enabled:
            return True
        self._log("验证运行环境...")
        try:
            from client.window import MainWindow  # noqa: F401
            from server.factory import ManagerFactory  # noqa: F401
            self._log("✓ 核心模块检查通过")
            return True
        except ImportError as e:
            self._log(f"✗ 模块导入失败：{e}")
            return False

    def _pre_launch_checks(self):
        self._log("执行启动前检查...")
        if not self._authorize():
            raise PermissionError("未授权，无法启动应用程序")
        if not self._validate_environment():
            raise RuntimeError("环境验证失败，无法启动应用程序")
        if not self._check_double_launch():
            raise RuntimeError("应用程序已经在运行中")
        self._log("✓ 启动前检查通过")

    def _post_launch_actions(self):
        self._log("应用程序已成功启动")
        self._is_launched = True
        self._access_count += 1

    # ---------------- IApplication 接口 ----------------
    def launch(self):
        self._log("请求启动应用程序")
        # 启动前检查
        self._pre_launch_checks()

        # 延迟实例化：仅在真正需要时才创建 RealApplication
        if self._real_app is None:
            with self._state_lock:
                if self._real_app is None:
                    self._log("创建应用程序实例（懒加载）...")
                    self._real_app = RealApplication()

        # 启动
        try:
            self._real_app.launch()
            self._post_launch_actions()
        except Exception as e:
            self._log(f"启动失败：{e}")
            self._is_launched = False
            raise

    def shutdown(self):
        self._log("请求关闭应用程序")
        if self._real_app:
            self._real_app.shutdown()
        self._is_launched = False
        self._log("代理已关闭")

    # ---------------- 代理配置 ----------------
    def enable_logging(self, enabled: bool = True):
        self._log_enabled = enabled
        self._log(f"日志功能已{'启用' if enabled else '禁用'}")

    def enable_validation(self, enabled: bool = True):
        self._validation_enabled = enabled
        self._log(f"环境验证已{'启用' if enabled else '禁用'}")

    def set_access_token(self, token: str):
        self._access_token = token
        self._log("访问令牌已更新")

    def get_access_stats(self) -> dict:
        return {
            "access_count": self._access_count,
            "is_launched": self._is_launched,
            "real_app_initialized": self._real_app is not None,
        }


def main():
    """主函数 - 使用代理模式启动应用程序。"""
    app_proxy = ApplicationProxy()

    # 可选：配置代理功能
    app_proxy.enable_logging(True)
    app_proxy.enable_validation(True)

    try:
        app_proxy.launch()
    except Exception as e:
        print(f"应用程序启动失败：{e}")
        app_proxy.shutdown()
    finally:
        app_proxy.shutdown()


if __name__ == "__main__":
    main()
