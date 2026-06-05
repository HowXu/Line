import customtkinter as ctk
from datetime import datetime
from client.ui_flyweight import UIFlyweightFactory

# ---------------------------------------------------------------------------
# 外观模式（Facade Pattern）
# ---------------------------------------------------------------------------
# 角色：
#   - Facade（外观）：ChatRendererFacade
#         - 对外暴露 render_message / render_messages_batch / clear_chat
#   - Subsystem（子系统）：
#       - MessageContainerBuilder：负责消息容器的创建与布局
#       - AvatarRenderer：负责头像区域
#       - MessageBubbleRenderer：负责气泡区域
#       - TimeLabelRenderer：负责时间标签
#       - AutoScrollService：负责滚动到底部
# ---------------------------------------------------------------------------


# ============================================================
# 子系统 1：MessageContainerBuilder
# ============================================================
class MessageContainerBuilder:
    """负责创建消息容器 frame 与其基础布局。"""

    def __init__(self, flyweight_factory: UIFlyweightFactory):
        self._flyweight = flyweight_factory

    def build_container(self, parent) -> ctk.CTkFrame:
        container = ctk.CTkFrame(parent, **self._flyweight.get_frame_config("transparent_container"))
        container.pack(fill="x", pady=5)
        return container


# ============================================================
# 子系统 2：AvatarRenderer
# ============================================================
class AvatarRenderer:
    """负责头像子区域的渲染（接收方消息左侧）。"""

    def __init__(self, flyweight_factory: UIFlyweightFactory):
        self._flyweight = flyweight_factory

    def render(self, parent, avatar_image):
        avatar = ctk.CTkLabel(parent, image=avatar_image, **self._flyweight.get_label_config("avatar"))
        avatar.pack(side="left")
        return avatar


# ============================================================
# 子系统 3：MessageBubbleRenderer
# ============================================================
class MessageBubbleRenderer:
    """负责消息气泡的渲染（文字部分）。"""

    def __init__(self, flyweight_factory: UIFlyweightFactory):
        self._flyweight = flyweight_factory

    def render(self, parent, text: str, side: str = "left", pack: dict = None):
        bubble_type = "received_message" if side == "left" else "sent_message"
        bubble = ctk.CTkFrame(parent, **self._flyweight.get_frame_config(bubble_type))
        bubble.pack(side=side, padx=10 if side == "right" else 5)
        label = ctk.CTkLabel(bubble, text=text, **self._flyweight.get_label_config("message_content"))
        label.pack(padx=12, pady=8)
        return bubble


# ============================================================
# 子系统 4：TimeLabelRenderer
# ============================================================
class TimeLabelRenderer:
    """负责时间标签的渲染。"""

    def __init__(self, flyweight_factory: UIFlyweightFactory):
        self._flyweight = flyweight_factory

    def render(self, parent, side: str = "right") -> ctk.CTkLabel:
        time_str = datetime.now().strftime("%H:%M")
        label = ctk.CTkLabel(parent, text=time_str, **self._flyweight.get_label_config("time_label"))
        label.pack(side=side, padx=5)
        return label


# ============================================================
# 子系统 5：AutoScrollService
# ============================================================
class AutoScrollService:
    """负责自动滚动到最底端。"""

    def scroll_to_bottom(self, chat_frame):
        if hasattr(chat_frame, "_parent_canvas"):
            chat_frame._parent_canvas.update_idletasks()
            chat_frame._parent_canvas.yview_moveto(1.0)


# ============================================================
# MessageRenderer：内部分装，由 Facade 委托
# ============================================================
class MessageRenderer:
    """内部子系统调度器（Facade 内部进一步拆解）。"""

    def __init__(self, chat_frame):
        self.chat_frame = chat_frame
        self.flyweight_factory = UIFlyweightFactory()
        self._container_builder = MessageContainerBuilder(self.flyweight_factory)
        self._avatar_renderer = AvatarRenderer(self.flyweight_factory)
        self._bubble_renderer = MessageBubbleRenderer(self.flyweight_factory)
        self._time_renderer = TimeLabelRenderer(self.flyweight_factory)
        self._scroller = AutoScrollService()

    def render_send_message(self, text: str):
        container = self._container_builder.build_container(self.chat_frame)
        self._bubble_renderer.render(container, text, side="right")
        self._time_renderer.render(container, side="right")
        self._scroller.scroll_to_bottom(self.chat_frame)

    def render_receive_message(self, text: str, avatar_image):
        container = self._container_builder.build_container(self.chat_frame)
        self._avatar_renderer.render(container, avatar_image)
        self._bubble_renderer.render(container, text, side="left")
        self._time_renderer.render(container, side="left")
        self._scroller.scroll_to_bottom(self.chat_frame)


# ============================================================
# Facade：对外统一接口
# ============================================================
class ChatRendererFacade:
    """外观：客户端只与 Facade 交互，由 Facade 编排各子系统。"""

    def __init__(self, chat_frame):
        self.chat_frame = chat_frame
        self.message_renderer = MessageRenderer(chat_frame)

    def render_message(self, text: str, sender: str, avatar_image=None):
        """统一的渲染入口。"""
        if sender == "me":
            self.message_renderer.render_send_message(text)
        elif sender == "ta":
            self.message_renderer.render_receive_message(text, avatar_image)
        else:
            raise ValueError(f"Unknown sender: {sender}")

    def render_messages_batch(self, messages: list):
        """批量渲染。"""
        for msg in messages:
            self.render_message(
                text=msg["text"],
                sender=msg["sender"],
                avatar_image=msg.get("avatar_image"),
            )

    def clear_chat(self):
        """清空聊天区域。"""
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
