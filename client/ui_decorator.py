from client.ui_component import UIComponent
from client.ui_composite import UIElement, LeafElement, CompositeElement

# 装饰模式

class UIDecorator(UIElement):
    
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
    
    def build(self, parent):
        widget = self.wrapped.build(parent)
        if hasattr(widget, '_scrollbar'):
            widget._scrollbar.configure(width=0)
        return widget


class AutoScrollDecorator(UIDecorator):
    
    def build(self, parent):
        widget = self.wrapped.build(parent)
        if hasattr(widget, '_parent_canvas'):
            widget._parent_canvas.update_idletasks()
            widget._parent_canvas.yview_moveto(1.0)
        return widget


class BorderedDecorator(UIDecorator):
    
    def __init__(self, wrapped: UIElement, border_width: int = 2, border_color: str = "gray"):
        super().__init__(wrapped)
        self.border_width = border_width
        self.border_color = border_color
    
    def build(self, parent):
        widget = self.wrapped.build(parent)
        if hasattr(widget, 'configure'):
            widget.configure(border_width=self.border_width)
        return widget


class StyledDecorator(UIDecorator):
    
    def __init__(self, wrapped: UIElement, **style_kwargs):
        super().__init__(wrapped)
        self.style_kwargs = style_kwargs
    
    def build(self, parent):
        widget = self.wrapped.build(parent)
        if hasattr(widget, 'configure'):
            for key, value in self.style_kwargs.items():
                try:
                    widget.configure(**{key: value})
                except:
                    pass
        return widget


class EventBindingDecorator(UIDecorator):
    
    def __init__(self, wrapped: UIElement, events: list = None):
        super().__init__(wrapped)
        self.events = events or []
    
    def build(self, parent):
        widget = self.wrapped.build(parent)
        for event_seq, handler in self.events:
            widget.bind(event_seq, handler)
        return widget
    
    def add_event(self, event_seq, handler):
        self.events.append((event_seq, handler))


class CompositeDecorator(UIDecorator):
    
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
