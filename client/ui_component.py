from abc import ABC, abstractmethod
import customtkinter as ctk

# ---------------------------------------------------------------------------
# 桥接模式（Bridge Pattern）
# ---------------------------------------------------------------------------
# 角色：
#   - Abstraction（抽象部分）：UIComponent
#         - 持有一个 UIComponentImplementor 的引用，对外暴露业务级 API
#   - RefinedAbstraction（精化抽象）：FrameComponent / LabelComponent /
#                                     ButtonComponent / ScrollableFrameComponent /
#                                     TextboxComponent
#   - Implementor（实现部分接口）：UIComponentImplementor
#         - 定义底层实现接口（不同 GUI 后端都可以实现）
#   - ConcreteImplementor（具体实现）：CTkComponentImplementor
#         - 基于 CustomTkinter 的实现
#
# 设计意图：把"UI 组件的抽象接口"与"底层 GUI 引擎"解耦，
#          使得未来切换到 Qt / Web / 命令行渲染时不需要改业务侧。
# ---------------------------------------------------------------------------


# ============================================================
# Implementor：实现部分接口
# ============================================================
class UIComponentImplementor(ABC):
    """实现部分：底层 GUI 引擎的抽象。"""

    @abstractmethod
    def create_widget(self, parent, spec: dict):
        """根据 spec 构造底层 widget。"""
        pass

    @abstractmethod
    def configure(self, widget, spec: dict):
        """设置 widget 通用属性。"""
        pass


# ============================================================
# ConcreteImplementor：CustomTkinter 实现
# ============================================================
class CTkComponentImplementor(UIComponentImplementor):
    """基于 CustomTkinter 的实现。"""

    WIDGET_TYPE_KEY = "_widget_type"

    def create_widget(self, parent, spec: dict):
        widget_type = spec.get(self.WIDGET_TYPE_KEY)
        if widget_type == "frame":
            return ctk.CTkFrame(parent, **{k: v for k, v in spec.items() if k != self.WIDGET_TYPE_KEY})
        if widget_type == "label":
            return ctk.CTkLabel(parent, **{k: v for k, v in spec.items() if k != self.WIDGET_TYPE_KEY})
        if widget_type == "button":
            return ctk.CTkButton(parent, **{k: v for k, v in spec.items() if k != self.WIDGET_TYPE_KEY})
        if widget_type == "scrollable_frame":
            return ctk.CTkScrollableFrame(parent, **{k: v for k, v in spec.items() if k != self.WIDGET_TYPE_KEY})
        if widget_type == "textbox":
            return ctk.CTkTextbox(parent, **{k: v for k, v in spec.items() if k != self.WIDGET_TYPE_KEY})
        raise ValueError(f"Unknown widget type: {widget_type}")

    def configure(self, widget, spec: dict):
        if hasattr(widget, "configure"):
            try:
                widget.configure(**{k: v for k, v in spec.items() if k != self.WIDGET_TYPE_KEY})
            except Exception:
                pass


# ============================================================
# Abstraction：抽象部分
# ============================================================
class UIComponent(ABC):
    """抽象部分：UI 组件对外的统一接口，内部委托给 Implementor。"""

    def __init__(self, implementor: UIComponentImplementor = None):
        # 默认实现为 CustomTkinter 实现
        self._implementor: UIComponentImplementor = implementor or CTkComponentImplementor()
        self.component = None

    def set_implementor(self, implementor: UIComponentImplementor):
        """桥接模式关键方法：运行时切换底层实现。"""
        self._implementor = implementor

    def _build_spec(self) -> dict:
        """由子类实现，返回 spec（含 _widget_type）。"""
        raise NotImplementedError

    @abstractmethod
    def create(self, parent) -> any:
        pass

    @abstractmethod
    def get_component(self):
        pass


# ============================================================
# RefinedAbstraction：精化抽象
# ============================================================
class FrameComponent(UIComponent):
    def __init__(self, height=None, corner_radius=None, bg_color=None, fg_color=None, **kwargs):
        super().__init__()
        self._height = height
        self._corner_radius = corner_radius
        self._bg_color = bg_color
        self._fg_color = fg_color
        self._kwargs = kwargs

    def _build_spec(self) -> dict:
        spec = {CTkComponentImplementor.WIDGET_TYPE_KEY: "frame"}
        if self._height is not None:
            spec["height"] = self._height
        if self._corner_radius is not None:
            spec["corner_radius"] = self._corner_radius
        if self._bg_color is not None:
            spec["bg_color"] = self._bg_color
        if self._fg_color is not None:
            spec["fg_color"] = self._fg_color
        spec.update(self._kwargs)
        return spec

    def create(self, parent):
        spec = self._build_spec()
        self.component = self._implementor.create_widget(parent, spec)
        return self.component

    def get_component(self):
        return self.component


class LabelComponent(UIComponent):
    def __init__(self, text="", font=None, text_color=None, image=None, **kwargs):
        super().__init__()
        self._text = text
        self._font = font
        self._text_color = text_color
        self._image = image
        self._kwargs = kwargs

    def _build_spec(self) -> dict:
        spec = {CTkComponentImplementor.WIDGET_TYPE_KEY: "label", "text": self._text}
        if self._font is not None:
            spec["font"] = self._font
        if self._text_color is not None:
            spec["text_color"] = self._text_color
        if self._image is not None:
            spec["image"] = self._image
        spec.update(self._kwargs)
        return spec

    def create(self, parent):
        spec = self._build_spec()
        self.component = self._implementor.create_widget(parent, spec)
        return self.component

    def get_component(self):
        return self.component


class ButtonComponent(UIComponent):
    def __init__(self, text="", width=None, height=None, font=None,
                 fg_color=None, hover_color=None, command=None, **kwargs):
        super().__init__()
        self._text = text
        self._width = width
        self._height = height
        self._font = font
        self._fg_color = fg_color
        self._hover_color = hover_color
        self._command = command
        self._kwargs = kwargs

    def _build_spec(self) -> dict:
        spec = {CTkComponentImplementor.WIDGET_TYPE_KEY: "button", "text": self._text, "command": self._command}
        if self._width is not None:
            spec["width"] = self._width
        if self._height is not None:
            spec["height"] = self._height
        if self._font is not None:
            spec["font"] = self._font
        if self._fg_color is not None:
            spec["fg_color"] = self._fg_color
        if self._hover_color is not None:
            spec["hover_color"] = self._hover_color
        spec.update(self._kwargs)
        return spec

    def create(self, parent):
        spec = self._build_spec()
        self.component = self._implementor.create_widget(parent, spec)
        return self.component

    def get_component(self):
        return self.component


class ScrollableFrameComponent(UIComponent):
    def __init__(self, bg_color=None, fg_color=None, **kwargs):
        super().__init__()
        self._bg_color = bg_color
        self._fg_color = fg_color
        self._kwargs = kwargs

    def _build_spec(self) -> dict:
        spec = {CTkComponentImplementor.WIDGET_TYPE_KEY: "scrollable_frame"}
        if self._bg_color is not None:
            spec["bg_color"] = self._bg_color
        if self._fg_color is not None:
            spec["fg_color"] = self._fg_color
        spec.update(self._kwargs)
        return spec

    def create(self, parent):
        spec = self._build_spec()
        self.component = self._implementor.create_widget(parent, spec)
        return self.component

    def get_component(self):
        return self.component


class TextboxComponent(UIComponent):
    def __init__(self, height=None, font=None, wrap=None, **kwargs):
        super().__init__()
        self._height = height
        self._font = font
        self._wrap = wrap
        self._kwargs = kwargs

    def _build_spec(self) -> dict:
        spec = {CTkComponentImplementor.WIDGET_TYPE_KEY: "textbox"}
        if self._height is not None:
            spec["height"] = self._height
        if self._font is not None:
            spec["font"] = self._font
        if self._wrap is not None:
            spec["wrap"] = self._wrap
        spec.update(self._kwargs)
        return spec

    def create(self, parent):
        spec = self._build_spec()
        self.component = self._implementor.create_widget(parent, spec)
        return self.component

    def get_component(self):
        return self.component
