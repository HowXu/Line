import customtkinter as ctk
from PIL import Image, ImageDraw

# 享元模式

class UIFlyweightFactory:
    """UI 享元工厂类"""
    
    _instance = None
    _flyweights = {}
    _image_cache = {}
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._init_flyweights()
            self._initialized = True
    
    def _init_flyweights(self):
        # Frame 配置
        self._flyweights['transparent_container'] = {
            'fg_color': 'transparent',
            'corner_radius': 0
        }
        
        self._flyweights['sent_message'] = {
            'fg_color': ctk.ThemeManager.theme["CTkButton"]["fg_color"],
            'corner_radius': 15
        }
        
        self._flyweights['received_message'] = {
            'fg_color': ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"],
            'corner_radius': 15
        }
        
        self._flyweights['button_frame'] = {
            'fg_color': 'transparent',
            'corner_radius': 0
        }
        
        # Label 配置
        self._flyweights['message_content'] = {
            'font': ("Segoe UI", 13),
            'wraplength': 250,
            'justify': "left"
        }
        
        self._flyweights['time_label'] = {
            'font': ("Segoe UI", 10),
            'text_color': "gray"
        }
        
        self._flyweights['avatar'] = {
            'text': "",
            'width': 40,
            'height': 40
        }
        
        self._flyweights['title_label'] = {
            'font': ("Segoe UI", 18, "bold")
        }
        
        self._flyweights['status_label'] = {
            'font': ("Segoe UI", 11),
            'text_color': "green"
        }
        
        self._flyweights['menu_button'] = {
            'font': ("Segoe UI", 20),
            'width': 40,
            'height': 40,
            'fg_color': "transparent",
            'hover_color': ("gray70", "gray30")
        }
    
    def get_frame_config(self, config_type: str) -> dict:
        return self._flyweights.get(config_type, {}).copy()
    
    def get_label_config(self, config_type: str) -> dict:
        return self._flyweights.get(config_type, {}).copy()
    
    def get_button_config(self, config_type: str) -> dict:
        return self._flyweights.get(config_type, {}).copy()
    
    def get_circular_image(self, image_path: str, size: int = 40):
        """
        获取头像
        
        Args:
            image_path: 图片路径
            size: 圆形图片大小
            
        Returns:
            CTkImage: 圆形图片对象
        """
        # 缓存键
        cache_key = f"{image_path}_{size}"
        
        # 检查
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        
        # 创建
        try:
            img = Image.open(image_path).resize((size, size), Image.Resampling.LANCZOS)
            
            # 创建蒙版
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([(0, 0), (size, size)], fill=255)
            
            # 应用
            circular_img = Image.new("RGBA", (size, size))
            circular_img.paste(img, (0, 0), mask)
            
            ctk_image = ctk.CTkImage(
                light_image=circular_img,
                dark_image=circular_img,
                size=(size, size)
            )
            
            # 缓存
            self._image_cache[cache_key] = ctk_image
            
            return ctk_image
            
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def clear_image_cache(self):
        self._image_cache.clear()
    
    def get_cache_stats(self) -> dict:
        return {
            'config_count': len(self._flyweights),
            'image_count': len(self._image_cache),
            'total_flyweights': len(self._flyweights) + len(self._image_cache)
        }


# 便捷函数
def get_flyweight_factory() -> UIFlyweightFactory:
    return UIFlyweightFactory()


def make_circular_image(image_path: str, size: int = 40):
    """
    Args:
        image_path: 图片路径
        size: 圆形图片大小
        
    Returns:
        CTkImage: 圆形图片对象
    """
    factory = UIFlyweightFactory()
    return factory.get_circular_image(image_path, size)
