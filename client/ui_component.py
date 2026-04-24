from abc import ABC, abstractmethod
import customtkinter as ctk

# 桥接模式

class UIComponent(ABC):
    @abstractmethod
    def create(self, parent) -> any:
        pass

    @abstractmethod
    def get_component(self):
        pass


class FrameComponent(UIComponent):
    
    def __init__(self, height=None, corner_radius=None, bg_color=None, fg_color=None, **kwargs):
        self.height = height
        self.corner_radius = corner_radius
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.kwargs = kwargs
        self.component = None
    
    def create(self, parent):
        kwargs = {
            'master': parent,
            'height': self.height,
            'corner_radius': self.corner_radius,
            **self.kwargs
        }
        if self.bg_color is not None:
            kwargs['bg_color'] = self.bg_color
        if self.fg_color is not None:
            kwargs['fg_color'] = self.fg_color
        self.component = ctk.CTkFrame(**kwargs)
        return self.component
    
    def get_component(self):
        return self.component


class LabelComponent(UIComponent):
    
    def __init__(self, text="", font=None, text_color=None, image=None, **kwargs):
        self.text = text
        self.font = font
        self.text_color = text_color
        self.image = image
        self.kwargs = kwargs
        self.component = None
    
    def create(self, parent):
        self.component = ctk.CTkLabel(
            parent,
            text=self.text,
            font=self.font,
            text_color=self.text_color,
            image=self.image,
            **self.kwargs
        )
        return self.component
    
    def get_component(self):
        return self.component


class ButtonComponent(UIComponent):
    
    def __init__(self, text="", width=None, height=None, font=None, 
                 fg_color=None, hover_color=None, command=None, **kwargs):
        self.text = text
        self.width = width
        self.height = height
        self.font = font
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.command = command
        self.kwargs = kwargs
        self.component = None
    
    def create(self, parent):
        kwargs = {
            'master': parent,
            'text': self.text,
            'command': self.command,
            **self.kwargs
        }
        if self.width is not None:
            kwargs['width'] = self.width
        if self.height is not None:
            kwargs['height'] = self.height
        if self.font is not None:
            kwargs['font'] = self.font
        if self.fg_color is not None:
            kwargs['fg_color'] = self.fg_color
        if self.hover_color is not None:
            kwargs['hover_color'] = self.hover_color
        self.component = ctk.CTkButton(**kwargs)
        return self.component
    
    def get_component(self):
        return self.component


class ScrollableFrameComponent(UIComponent):
    
    def __init__(self, bg_color=None, fg_color=None, **kwargs):
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.kwargs = kwargs
        self.component = None
    
    def create(self, parent):
        kwargs = {
            'master': parent,
            **self.kwargs
        }
        if self.bg_color is not None:
            kwargs['bg_color'] = self.bg_color
        if self.fg_color is not None:
            kwargs['fg_color'] = self.fg_color
        self.component = ctk.CTkScrollableFrame(**kwargs)
        return self.component
    
    def get_component(self):
        return self.component


class TextboxComponent(UIComponent):
    
    def __init__(self, height=None, font=None, wrap=None, **kwargs):
        self.height = height
        self.font = font
        self.wrap = wrap
        self.kwargs = kwargs
        self.component = None
    
    def create(self, parent):
        self.component = ctk.CTkTextbox(
            parent,
            height=self.height,
            font=self.font,
            wrap=self.wrap,
            **self.kwargs
        )
        return self.component
    
    def get_component(self):
        return self.component
