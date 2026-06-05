from abc import ABC, abstractmethod
from client.ui_component import UIComponent
from client.ui_composite import UIElement, LeafElement, CompositeElement

# 装饰模式（Decorator Pattern）
# 角色：
#   - Component（抽象构件）：UIComponent / UIElement
#   - ConcreteComponent（具体构件）：FrameComponent / LabelComponent / LeafElement / CompositeElement ...
#   - Decorator（抽象装饰器）：UIComponentDecorator / UIDecorator
#   - ConcreteDecorator（具体装饰器）：ScrollbarHiddenDecorator / AutoScrollDecorator /
#                                    BorderedDecorator / StyledDecorator / EventBindingDecorator /
#                                    CompositeDecorator
#
# 设计意图：在不修改原有 UI 构件的前提下，动态地为其附加额外职责（隐藏滚动条、
#          自动滚动、边框、样式、事件绑定、装饰器叠加等），符合"开闭原则"。
#          装饰器与被装饰对象继承自同一抽象层（UIComponent / UIElement），
#          因此对客户端完全透明，可以嵌套组合形成"装饰链"。


# ---------------------------------------------------------------------------
# 第一层装饰：装饰 UIComponent（最细粒度，桥接模式产出的具体组件）
# ---------------------------------------------------------------------------

class UIComponentDecorator(UIComponent):
    """抽象装饰器：装饰 UIComponent，与被装饰对象实现同一接口。"""

    def __init__(self, wrapped: UIComponent):
        self._wrapped = wrapped

    @abstractmethod
    def create(self, parent):
        """先创建被装饰对象，再附加额外职责。"""
        return self._wrapped.create(parent)

    def get_component(self):
        return self._wrapped.get_component()


class HighlightDecorator(UIComponentDecorator):
    """高亮装饰器：为目标组件附加高亮背景。"""

    def __init__(self, wrapped: UIComponent, color: str = "#3B82F6"):
        super().__init__(wrapped)
        self._color = color

    def create(self, parent):
        widget = super().create(parent)
        if hasattr(widget, "configure"):
            try:
                widget.configure(fg_color=self._color)
            except Exception:
                pass
        return widget


class DisabledDecorator(UIComponentDecorator):
    """禁用装饰器：构建后立即将组件置为 disabled 状态。"""

    def create(self, parent):
        widget = super().create(parent)
        if hasattr(widget, "configure"):
            try:
                widget.configure(state="disabled")
            except Exception:
                pass
        return widget


class TooltipDecorator(UIComponentDecorator):
    """工具提示装饰器：为目标组件附加悬浮提示（占位实现，记录绑定信息）。"""

    def __init__(self, wrapped: UIComponent, text: str = ""):
        super().__init__(wrapped)
        self._tooltip_text = text

    def create(self, parent):
        widget = super().create(parent)
        if self._tooltip_text and hasattr(widget, "bind"):
            try:
                widget.bind("<Enter>", lambda _e: print(f"[tooltip] {self._tooltip_text}"))
            except Exception:
                pass
        return widget


# ---------------------------------------------------------------------------
# 第二层装饰：装饰 UIElement（组合模式中的元素，粒度更大）
# ---------------------------------------------------------------------------

class UIDecorator(UIElement):
    """抽象装饰器：装饰 UIElement，统一转发接口。"""

    def __init__(self, wrapped: UIElement):
        self.wrapped = wrapped

    def build(self, parent):
        return self.wrapped.build(parent)

    def add_child(self, child):
        self.wrapped.add_child(child)

    def remove_child(self, child):
        self.wrapped.remove_child(child)

    def get_children(self):
        return self.wrapped.get_children()

    def get_component(self):
        return self.wrapped.get_component()


class ScrollbarHiddenDecorator(UIDecorator):
    """隐藏滚动条装饰器：build 完成后将内部 scrollbar 宽度置 0。"""

    def build(self, parent):
        widget = self.wrapped.build(parent)
        if hasattr(widget, "_scrollbar"):
            widget._scrollbar.configure(width=0)
        return widget


class AutoScrollDecorator(UIDecorator):
    """自动滚动装饰器：build 完成后将画布滚动到最底端。"""

    def build(self, parent):
        widget = self.wrapped.build(parent)
        if hasattr(widget, "_parent_canvas"):
            widget._parent_canvas.update_idletasks()
            widget._parent_canvas.yview_moveto(1.0)
        return widget


class BorderedDecorator(UIDecorator):
    """边框装饰器：为组件附加边框宽度。"""

    def __init__(self, wrapped: UIElement, border_width: int = 2, border_color: str = "gray"):
        super().__init__(wrapped)
        self.border_width = border_width
        self.border_color = border_color

    def build(self, parent):
        widget = self.wrapped.build(parent)
        if hasattr(widget, "configure"):
            try:
                widget.configure(border_width=self.border_width)
            except Exception:
                pass
        return widget


class StyledDecorator(UIDecorator):
    """通用样式装饰器：批量向组件写入 configure 参数。"""

    def __init__(self, wrapped: UIElement, **style_kwargs):
        super().__init__(wrapped)
        self.style_kwargs = style_kwargs

    def build(self, parent):
        widget = self.wrapped.build(parent)
        if hasattr(widget, "configure"):
            for key, value in self.style_kwargs.items():
                try:
                    widget.configure(**{key: value})
                except Exception:
                    pass
        return widget


class EventBindingDecorator(UIDecorator):
    """事件绑定装饰器：build 时为组件批量绑定事件。"""

    def __init__(self, wrapped: UIElement, events: list = None):
        super().__init__(wrapped)
        self.events = events or []

    def build(self, parent):
        widget = self.wrapped.build(parent)
        for event_seq, handler in self.events:
            if hasattr(widget, "bind"):
                widget.bind(event_seq, handler)
        return widget

    def add_event(self, event_seq, handler):
        self.events.append((event_seq, handler))


class CompositeDecorator(UIDecorator):
    """装饰器组合：把多个具体装饰器叠加到同一个元素上。"""

    def __init__(self, wrapped: UIElement, decorators: list = None):
        super().__init__(wrapped)
        self.decorators = decorators or []

    def add_decorator(self, decorator: UIDecorator):
        self.decorators.append(decorator)

    def build(self, parent):
        widget = self.wrapped.build(parent)
        for decorator in self.decorators:
            widget = decorator.build(parent)
        return widget
