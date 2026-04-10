import customtkinter as ctk
from PIL import Image, ImageDraw
from datetime import datetime
import threading
import time
from server.data import DataManager
from server.ai import DeepSeekAPI

# 设置主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainWindow:
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
        # 通过init更新DeepSeek上下文

        
    def setup_ui(self):
        # ========== 顶部标题栏 ==========
        self.top_frame = ctk.CTkFrame(
            self.window, 
            height=60, 
            corner_radius=0,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"]
        )
        self.top_frame.pack(fill="x")
        self.top_frame.pack_propagate(False)

        # 好友信息
        self.friend_label = ctk.CTkLabel(
            self.top_frame,
            text=self.friend_name,
            font=("Segoe UI", 18, "bold")
        )
        
        self.friend_label.pack(side="left", padx=(25,0))
        
        # 在线状态
        self.status_label = ctk.CTkLabel(
            self.top_frame,
            text="● 在线",
            font=("Segoe UI", 11),
            text_color="green"
        )
        
        self.status_label.pack(side="left", padx=(15,0))
        
        # 菜单按钮
        menu_btn = ctk.CTkButton(
            self.top_frame,
            text="⋯",
            width=40,
            height=40,
            font=("Segoe UI", 20),
            fg_color="transparent",
            hover_color=("gray70", "gray30")
        )
        menu_btn.pack(side="right", padx=10, pady=10)
        
        # ========== 聊天记录区域 ==========
        self.chat_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent"
        )
        self.chat_frame.pack(fill="both", expand=True, pady=10)
        self.chat_frame._scrollbar.configure(width=0) # No滚动条
        
        # ========== 底部输入区域 ==========
        self.bottom_frame = ctk.CTkFrame(self.window, corner_radius=0)
        self.bottom_frame.pack(fill="x", padx=10, pady=10)
        
        # 输入框
        self.input_text = ctk.CTkTextbox(
            self.bottom_frame,
            height=80,
            font=("Segoe UI", 13),
            wrap="word"
        )
        self.input_text.pack(fill="x", padx=5, pady=(5, 0))
        
        # 绑定回车发送
        self.input_text.bind("<Return>", self.render_send_event)
        self.input_text.bind("<Shift-Return>", self.new_line)
        
        # 按钮行
        self.button_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=5)
        
        # 发送按钮
        self.send_btn = ctk.CTkButton(
            self.button_frame,
            text="发送",
            width=80,
            command=self.input_message
        )
        self.send_btn.pack(side="right", padx=5)
        
        # 加载已有的信息
        self.load_histories()
        
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
        row = self.dataManager.display_conext
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
