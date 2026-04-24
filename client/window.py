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

# 设置主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainWindow:
    # 主页面遵循单例模式
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            return cls._instance
        return cls._instance

    def __init__(self,dataManager: DataManager,deepSeekAPI: DeepSeekAPI):
        self.dataManager = dataManager # 这个用来管理对话上下文 因为同时涉及前端渲染和后端推送
        self.API = deepSeekAPI # 上下文统一
        self.window = ctk.CTk()
        self.window.title("Line") # window title
        self.window.geometry('450x750') # window size
        self.window.minsize(350, 500) # minimum window size
        self.window.iconbitmap('resources/icon.ico')  # Windows 系统使用 .ico 文件
        
        self.friend_name = "Eva"
        self.current_user = "me"
        
        self.setup_ui()
        # 通过 init 更新 DeepSeek 上下文

    def setup_ui(self):
        top_header = self.build_top_header()
        top_header.build(self.window)
        
        chat_area = self.build_chat_area()
        chat_area.build(self.window)
        
        input_area = self.build_input_area()
        input_area.build(self.window)
        
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
        
    # 这是一个client方法 负责发送消息和在前端展示
    def render_send(self, text: str):
        # chat line
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        
        # 消息容器
        msg_container = ctk.CTkFrame(
            self.chat_frame,
            fg_color="transparent"
        )
        msg_container.pack(fill="x", pady=5)
        # 自己的消息靠右
        msg_frame = ctk.CTkFrame(
            msg_container,
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
            corner_radius=15
        )
        msg_frame.pack(side="right", padx=10)
        
        # 消息内容
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=text,
            font=("Segoe UI", 13),
            wraplength=250,
            justify="left"
        )
        msg_label.pack(padx=12, pady=8)
        
        # 时间标签
        time_label = ctk.CTkLabel(
            msg_container,
            text=time_str,
            font=("Segoe UI", 10),
            text_color="gray"
        )
        time_label.pack(side="right", padx=5)
        # 更新窗口
        self.chat_frame._parent_canvas.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)
        
    # 这是一个Client方法 负责接收消息和在前端展示
    def render_receive(self, text: str):
        # chat line
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        
        # 消息容器
        msg_container = ctk.CTkFrame(
            self.chat_frame,
            fg_color="transparent"
        )
        msg_container.pack(fill="x", pady=5)
        
        # 对方的消息靠左
        # 头像
        avatar_img = make_circular_image("resources/ta.png", size=30)
        avatar = ctk.CTkLabel(
            msg_container,
            image=avatar_img,
            text="",
            width=40,
            height=40
        )
        avatar.pack(side="left")
        
        # 消息气泡
        msg_frame = ctk.CTkFrame(
            msg_container,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"],
            corner_radius=15
        )
        msg_frame.pack(side="left", padx=5)
        
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=text,
            font=("Segoe UI", 13),
            wraplength=250,
            justify="left"
        )
        msg_label.pack(padx=12, pady=8)
        
        # 时间标签
        time_label = ctk.CTkLabel(
            msg_container,
            text=time_str,
            font=("Segoe UI", 10),
            text_color="gray"
        )
        time_label.pack(side="left", padx=5)
        
        self.chat_frame._parent_canvas.update_idletasks()
        # 滚动到底部
        self.chat_frame._parent_canvas.yview_moveto(1.0)
        
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
        row = self.dataManager.data.display_conext
        for msg in row:
            is_me = (msg['sender'] == "me")
            if is_me:
                self.render_send(msg['text'])
            else:
                self.render_receive(msg['text'])
            
    def run(self):
        self.window.mainloop()

# 头像设置
def make_circular_image(image_path, size=40):
    img = Image.open(image_path).resize((size, size), Image.Resampling.LANCZOS)
    
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([(0, 0), (size, size)], fill=255)
    
    circular_img = Image.new("RGBA", (size, size))
    circular_img.paste(img, (0, 0), mask)
    
    return ctk.CTkImage(light_image=circular_img, dark_image=circular_img, size=(size, size))
