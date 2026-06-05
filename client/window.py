import customtkinter as ctk
from PIL import Image, ImageDraw
from datetime import datetime
import threading
import time
from server.data import DataManager
from server.ai import DeepSeekAPI
from client.ui_component import (
    FrameComponent, LabelComponent, ButtonComponent,
    ScrollableFrameComponent, TextboxComponent
)
from client.ui_composite import CompositeElement, LeafElement, UICompositeBuilder
from client.ui_decorator import ScrollbarHiddenDecorator, EventBindingDecorator
from client.ui_facade import ChatRendererFacade
from client.ui_flyweight import get_flyweight_factory, make_circular_image

# 设置主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainWindow:
    """
    单例模式（Singleton Pattern）：
    - 私有类属性 _instance 保存唯一实例
    - 使用 _lock 保证多线程场景下也只创建一次
    - 重写 __new__ 控制实例化
    - 重写 __init__ 也加锁，避免重复初始化覆盖
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, dataManager: DataManager, deepSeekAPI: DeepSeekAPI):
        # 单例 + 线程安全：仅首次真正初始化
        with MainWindow._lock:
            if MainWindow._initialized:
                return
            self.dataManager = dataManager
            self.API = deepSeekAPI
            self.window = ctk.CTk()
            self.window.title("Line")
            self.window.geometry("450x750")
            self.window.minsize(350, 500)
            self.window.iconbitmap("resources/icon.ico")

            self.friend_name = "Eva"
            self.current_user = "me"

            self.flyweight_factory = get_flyweight_factory()
            self.renderer = None

            self.setup_ui()
            MainWindow._initialized = True

    def setup_ui(self):
        top_header = self.build_top_header()
        top_header.build(self.window)
        
        chat_area = self.build_chat_area()
        chat_area.build(self.window)
        
        input_area = self.build_input_area()
        input_area.build(self.window)
        
        # 初始化渲染外观（在 UI 组件创建完成后）
        self.renderer = ChatRendererFacade(self.chat_frame)
        
        self.load_histories()

    def build_top_header(self) -> CompositeElement:
        top_frame = FrameComponent(
            height=60,
            corner_radius=0,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"]
        )
        top_header = CompositeElement(top_frame, {"fill": "x", "padx": 0, "pady": 0})
        
        friend_label = LabelComponent(
            text=self.friend_name,
            font=("Segoe UI", 18, "bold")
        )
        top_header.add_child(LeafElement(friend_label, {"side": "left", "padx": (25, 0)}))
        
        status_label = LabelComponent(
            text="● 在线",
            font=("Segoe UI", 11),
            text_color="green"
        )
        top_header.add_child(LeafElement(status_label, {"side": "left", "padx": (15, 0)}))
        
        menu_btn = ButtonComponent(
            text="⋯",
            width=40,
            height=40,
            font=("Segoe UI", 20),
            fg_color="transparent",
            hover_color=("gray70", "gray30")
        )
        top_header.add_child(LeafElement(menu_btn, {"side": "right", "padx": 10, "pady": 10}))
        
        original_build = top_header.build
        def build_and_fix(parent):
            widget = original_build(parent)
            widget.pack_propagate(False)
            return widget
        top_header.build = build_and_fix
        
        return top_header
    
    def build_chat_area(self) -> CompositeElement:
        chat_frame = ScrollableFrameComponent(fg_color="transparent")
        chat_area = CompositeElement(chat_frame, {"fill": "both", "expand": True, "pady": 10})
        
        chat_area = ScrollbarHiddenDecorator(chat_area)
        
        self.chat_frame = None
        original_build = chat_area.build
        def build_and_store(parent):
            widget = original_build(parent)
            self.chat_frame = widget
            return widget
        chat_area.build = build_and_store
        
        return chat_area
    
    def build_input_area(self) -> CompositeElement:
        bottom_frame = FrameComponent(corner_radius=0, height=120)
        input_area = CompositeElement(bottom_frame, {"fill": "x", "padx": 10, "pady": 10})
        
        input_text = TextboxComponent(
            height=80,
            font=("Segoe UI", 13),
            wrap="word"
        )
        input_text_leaf = LeafElement(input_text, {"fill": "x", "padx": 5, "pady": (5, 0)})
        input_text_leaf = EventBindingDecorator(input_text_leaf, [
            ("<Return>", self.render_send_event),
            ("<Shift-Return>", self.new_line)
        ])
        input_area.add_child(input_text_leaf)
        
        button_frame = FrameComponent(fg_color="transparent", height=40)
        button_frame_composite = CompositeElement(button_frame, {"fill": "x", "pady": 5})
        input_area.add_child(button_frame_composite)
        
        send_btn = ButtonComponent(
            text="发送",
            width=80,
            command=self.input_message
        )
        button_frame_composite.add_child(LeafElement(send_btn, {"side": "right", "padx": 5}))
        
        self.input_text = None
        original_build = input_area.build
        def build_and_store(parent):
            widget = original_build(parent)
            if hasattr(input_text, 'component'):
                self.input_text = input_text.component
            return widget
        input_area.build = build_and_store
        
        return input_area
        
    # 这是一个 client 方法 负责发送消息和在前端展示
    def render_send(self, text: str):
        """渲染发送的消息（使用外观模式）"""
        self.renderer.render_message(text, "me")
        
    # 这是一个 Client 方法 负责接收消息和在前端展示
    def render_receive(self, text: str):
        """渲染接收的消息（使用外观模式）"""
        avatar_img = self.flyweight_factory.get_circular_image("resources/ta.png", size=30)
        self.renderer.render_message(text, "ta", avatar_img)
        
    # 这是一个需要调用后端的方法
    def input_message(self):
        """发送消息"""
        message = self.input_text.get("0.0", "end").strip()
        
        if not message:
            return
        
        # 前端更新
        self.render_send(message)
        
        # 清空输入框
        self.input_text.delete("0.0", "end")

        # 后端提交DeepSeek API 异步进行
        threading.Thread(target=self.reply, args=(message,), daemon=True).start()
        
    # 挂载给事件监听
    def render_send_event(self, event):
        """回车发送"""
        if not event.state & 0x1:  # 没有按 Shift
            self.input_message()
            return "break"
        return None
        
    def new_line(self, event):
        """Shift+回车换行"""
        self.input_text.insert("end", "\n")
        return "break"
        
    # 这是一个需要调用后端的方法
    def reply(self, user_message):
        # 调用API获取回复
        (should_reply, response) = self.API.fetch(user_message) # fetch结果会自动解析 之需要更新前端栈就可以了 返回结果是直接一个str给前端用
        # 在主线程中更新 UI 更新前端栈
        if should_reply:
            self.window.after(0, lambda: self.render_receive(response))
        
    def load_histories(self):
        """加载历史消息（使用外观模式的批量渲染）"""
        row = self.dataManager.data.display_conext
        messages = []
        
        # 准备头像（享元模式）
        avatar_img = self.flyweight_factory.get_circular_image("resources/ta.png", size=30)
        
        for msg in row:
            is_me = (msg['sender'] == "me")
            messages.append({
                "text": msg['text'],
                "sender": msg['sender'],
                "avatar_image": avatar_img if not is_me else None
            })
        
        # 批量渲染
        self.renderer.render_messages_batch(messages)
            
    def run(self):
        self.window.mainloop()
