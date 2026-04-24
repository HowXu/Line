import customtkinter as ctk
from client.ui_flyweight import UIFlyweightFactory
from datetime import datetime

# 外观模式

class MessageRenderer:
    """消息渲染外观类"""
    
    def __init__(self, chat_frame):
        self.chat_frame = chat_frame
        self.flyweight_factory = UIFlyweightFactory()
    
    def render_send_message(self, text: str):
        """渲染发送的消息（右侧）"""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        
        # 使用享元工厂获取可复用的配置
        container_config = self.flyweight_factory.get_frame_config("transparent_container")
        msg_frame_config = self.flyweight_factory.get_frame_config("sent_message")
        label_config = self.flyweight_factory.get_label_config("message_content")
        time_label_config = self.flyweight_factory.get_label_config("time_label")
        
        # 消息容器
        msg_container = ctk.CTkFrame(
            self.chat_frame,
            **container_config
        )
        msg_container.pack(fill="x", pady=5)
        
        # 自己的消息靠右
        msg_frame = ctk.CTkFrame(
            msg_container,
            **msg_frame_config
        )
        msg_frame.pack(side="right", padx=10)
        
        # 消息内容
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=text,
            **label_config
        )
        msg_label.pack(padx=12, pady=8)
        
        # 时间标签
        time_label = ctk.CTkLabel(
            msg_container,
            text=time_str,
            **time_label_config
        )
        time_label.pack(side="right", padx=5)
        
        # 自动滚动到底部
        self._scroll_to_bottom()
    
    def render_receive_message(self, text: str, avatar_image):
        """渲染接收的消息（左侧）"""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        
        # 使用享元工厂获取可复用的配置
        container_config = self.flyweight_factory.get_frame_config("transparent_container")
        msg_frame_config = self.flyweight_factory.get_frame_config("received_message")
        label_config = self.flyweight_factory.get_label_config("message_content")
        time_label_config = self.flyweight_factory.get_label_config("time_label")
        avatar_config = self.flyweight_factory.get_label_config("avatar")
        
        # 消息容器
        msg_container = ctk.CTkFrame(
            self.chat_frame,
            **container_config
        )
        msg_container.pack(fill="x", pady=5)
        
        # 头像
        avatar = ctk.CTkLabel(
            msg_container,
            image=avatar_image,
            **avatar_config
        )
        avatar.pack(side="left")
        
        # 消息气泡
        msg_frame = ctk.CTkFrame(
            msg_container,
            **msg_frame_config
        )
        msg_frame.pack(side="left", padx=5)
        
        # 消息内容
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=text,
            **label_config
        )
        msg_label.pack(padx=12, pady=8)
        
        # 时间标签
        time_label = ctk.CTkLabel(
            msg_container,
            text=time_str,
            **time_label_config
        )
        time_label.pack(side="left", padx=5)
        
        # 自动滚动到底部
        self._scroll_to_bottom()
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        if hasattr(self.chat_frame, '_parent_canvas'):
            self.chat_frame._parent_canvas.update_idletasks()
            self.chat_frame._parent_canvas.yview_moveto(1.0)


class ChatRendererFacade:

    def __init__(self, chat_frame):
        self.chat_frame = chat_frame
        self.message_renderer = MessageRenderer(chat_frame)
    
    def render_message(self, text: str, sender: str, avatar_image=None):
        """
        渲染消息的统一接口
        
        Args:
            text: 消息文本
            sender: 发送者 ("me" 或 "ta")
            avatar_image: 头像图片（仅当 sender 为 "ta" 时需要）
        """
        if sender == "me":
            self.message_renderer.render_send_message(text)
        elif sender == "ta":
            self.message_renderer.render_receive_message(text, avatar_image)
    
    def render_messages_batch(self, messages: list):
        """
        批量渲染
        
        Args:
            messages: 消息列表，每个元素为 dict:
                     {
                         "text": str,
                         "sender": str,
                         "avatar_image": optional
                     }
        """
        for msg in messages:
            self.render_message(
                text=msg["text"],
                sender=msg["sender"],
                avatar_image=msg.get("avatar_image")
            )
    
    def clear_chat(self):
        """清空聊天区域"""
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
