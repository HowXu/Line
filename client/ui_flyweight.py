import customtkinter as ctk
from PIL import Image, ImageDraw
from abc import ABC, abstractmethod
import threading

# ---------------------------------------------------------------------------
# 享元模式（Flyweight Pattern）
# ---------------------------------------------------------------------------
# 角色：
#   - Flyweight（抽象享元）：UIFlyweight
#         - 声明内蕴状态（intrinsic）与外蕴状态（extrinsic）的操作
#   - ConcreteFlyweight（具体享元）：ImageFlyweight / ConfigFlyweight
#         - 缓存的图片对象、配置字典
#   - FlyweightFactory（享元工厂）：UIFlyweightFactory
#         - 负责创建并管理共享对象池，避免重复构造
#   - Client（客户端）：通过 factory 获取共享对象，按 key 复用
# ---------------------------------------------------------------------------


# ============================================================
# 抽象享元
# ============================================================
class UIFlyweight(ABC):
    """抽象享元：所有可被共享的 UI 资源都遵循此契约。"""

    @abstractmethod
    def get_key(self) -> str:
        """返回该享元在内蕴缓存中的唯一 key。"""
        pass

    @abstractmethod
    def reuse_count(self) -> int:
        """返回该享元被复用的次数，用于统计命中率。"""
        pass


# ============================================================
# 具体享元 A：可复用的图片对象
# ============================================================
class ImageFlyweight(UIFlyweight):
    """图片享元：缓存相同 path+size 的图片对象，避免重复 IO 与解码。"""

    def __init__(self, image_path: str, size: int):
        self._image_path = image_path
        self._size = size
        self._key = f"{image_path}_{size}"
        self._hits = 0
        self._image = self._build()

    def _build(self):
        try:
            img = Image.open(self._image_path).resize(
                (self._size, self._size), Image.Resampling.LANCZOS
            )
            mask = Image.new("L", (self._size, self._size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([(0, 0), (self._size, self._size)], fill=255)
            circular_img = Image.new("RGBA", (self._size, self._size))
            circular_img.paste(img, (0, 0), mask)
            return ctk.CTkImage(
                light_image=circular_img,
                dark_image=circular_img,
                size=(self._size, self._size),
            )
        except Exception as e:
            print(f"Error loading image {self._image_path}: {e}")
            return None

    def get_key(self) -> str:
        return self._key

    def reuse_count(self) -> int:
        return self._hits

    def hit(self):
        self._hits += 1

    @property
    def image(self):
        return self._image


# ============================================================
# 具体享元 B：可复用的配置字典
# ============================================================
class ConfigFlyweight(UIFlyweight):
    """配置享元：缓存同名 UI 配置，避免每次渲染时重复构造。"""

    def __init__(self, key: str, config: dict):
        self._key = key
        self._config = dict(config)  # 拷贝避免外部篡改
        self._hits = 0

    def get_key(self) -> str:
        return self._key

    def reuse_count(self) -> int:
        return self._hits

    def hit(self):
        self._hits += 1

    def get_config(self) -> dict:
        self._hits += 1
        return self._config.copy()


# ============================================================
# 享元工厂：UIFlyweightFactory（同时是单例）
# ============================================================
class UIFlyweightFactory:
    """UI 享元工厂：单例 + 双层缓存（图片 + 配置）。"""

    _instance = None
    _lock = threading.Lock()
    _flyweights: dict = {}
    _image_cache: dict = {}

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._init_flyweights()
            self._initialized = True

    def _init_flyweights(self):
        # Frame 配置
        self._flyweights["transparent_container"] = ConfigFlyweight(
            "transparent_container",
            {"fg_color": "transparent", "corner_radius": 0},
        )
        self._flyweights["sent_message"] = ConfigFlyweight(
            "sent_message",
            {
                "fg_color": ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                "corner_radius": 15,
            },
        )
        self._flyweights["received_message"] = ConfigFlyweight(
            "received_message",
            {
                "fg_color": ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"],
                "corner_radius": 15,
            },
        )
        self._flyweights["button_frame"] = ConfigFlyweight(
            "button_frame",
            {"fg_color": "transparent", "corner_radius": 0},
        )
        # Label 配置
        self._flyweights["message_content"] = ConfigFlyweight(
            "message_content",
            {"font": ("Segoe UI", 13), "wraplength": 250, "justify": "left"},
        )
        self._flyweights["time_label"] = ConfigFlyweight(
            "time_label",
            {"font": ("Segoe UI", 10), "text_color": "gray"},
        )
        self._flyweights["avatar"] = ConfigFlyweight(
            "avatar",
            {"text": "", "width": 40, "height": 40},
        )
        self._flyweights["title_label"] = ConfigFlyweight(
            "title_label", {"font": ("Segoe UI", 18, "bold")}
        )
        self._flyweights["status_label"] = ConfigFlyweight(
            "status_label", {"font": ("Segoe UI", 11), "text_color": "green"}
        )
        self._flyweights["menu_button"] = ConfigFlyweight(
            "menu_button",
            {
                "font": ("Segoe UI", 20),
                "width": 40,
                "height": 40,
                "fg_color": "transparent",
                "hover_color": ("gray70", "gray30"),
            },
        )

    # ---------------- 图片享元 ----------------
    def get_circular_image(self, image_path: str, size: int = 40):
        """获取或创建图片享元。"""
        cache_key = f"{image_path}_{size}"
        cached = self._image_cache.get(cache_key)
        if cached is not None:
            cached.hit()
            return cached.image
        flyweight = ImageFlyweight(image_path, size)
        self._image_cache[cache_key] = flyweight
        return flyweight.image

    # ---------------- 配置享元 ----------------
    def get_frame_config(self, config_type: str) -> dict:
        return self._get_config(config_type)

    def get_label_config(self, config_type: str) -> dict:
        return self._get_config(config_type)

    def get_button_config(self, config_type: str) -> dict:
        return self._get_config(config_type)

    def _get_config(self, config_type: str) -> dict:
        cfg = self._flyweights.get(config_type)
        if cfg is None:
            return {}
        return cfg.get_config()

    # ---------------- 维护 ----------------
    def clear_image_cache(self):
        self._image_cache.clear()

    def get_cache_stats(self) -> dict:
        image_total = sum(f.reuse_count() for f in self._image_cache.values())
        config_total = sum(f.reuse_count() for f in self._flyweights.values())
        return {
            "config_count": len(self._flyweights),
            "image_count": len(self._image_cache),
            "total_flyweights": len(self._flyweights) + len(self._image_cache),
            "image_hits": image_total,
            "config_hits": config_total,
        }


# 便捷函数
def get_flyweight_factory() -> UIFlyweightFactory:
    return UIFlyweightFactory()


def make_circular_image(image_path: str, size: int = 40):
    factory = UIFlyweightFactory()
    return factory.get_circular_image(image_path, size)
