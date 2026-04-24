from abc import ABC, abstractmethod
from client.ui_component import UIComponent

# 组合模式

class UIElement(ABC):
    
    @abstractmethod
    def build(self, parent) -> any:
        pass
    
    @abstractmethod
    def add_child(self, child):
        pass
    
    @abstractmethod
    def remove_child(self, child):
        pass
    
    @abstractmethod
    def get_children(self):
        pass


class LeafElement(UIElement):
    
    def __init__(self, component: UIComponent, pack_config: dict = None):
        self.component = component
        self.pack_config = pack_config or {}
        self.children = []
    
    def build(self, parent):
        widget = self.component.create(parent)
        if self.pack_config:
            widget.pack(**self.pack_config)
        return widget
    
    def add_child(self, child):
        raise NotImplementedError("no children for leaf element")
    
    def remove_child(self, child):
        raise NotImplementedError("no children for leaf element")
    
    def get_children(self):
        return self.children.copy()
    
    def get_component(self):
        return self.component


class CompositeElement(UIElement):
    
    def __init__(self, component: UIComponent, pack_config: dict = None):
        self.component = component
        self.pack_config = pack_config or {}
        self.children = []
    
    def build(self, parent):
        widget = self.component.create(parent)
        if self.pack_config:
            widget.pack(**self.pack_config)
        
        for child in self.children:
            child.build(widget)
        
        return widget
    
    def add_child(self, child: UIElement):
        self.children.append(child)
    
    def remove_child(self, child: UIElement):
        self.children.remove(child)
    
    def get_children(self):
        return self.children.copy()
    
    def get_component(self):
        return self.component


class UICompositeBuilder:
    
    def __init__(self):
        self.root = None
        self.current_stack = []
    
    def set_root(self, root: CompositeElement):
        self.root = root
        self.current_stack = [root]
        return self
    
    def add_frame(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        frame = CompositeElement(component, pack_config)
        current_parent = self.current_stack[-1]
        current_parent.add_child(frame)
        self.current_stack.append(frame)
        return self
    
    def add_label(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        label = LeafElement(component, pack_config)
        current_parent = self.current_stack[-1]
        current_parent.add_child(label)
        return self
    
    def add_button(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        button = LeafElement(component, pack_config)
        current_parent = self.current_stack[-1]
        current_parent.add_child(button)
        return self
    
    def add_textbox(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        textbox = LeafElement(component, pack_config)
        current_parent = self.current_stack[-1]
        current_parent.add_child(textbox)
        return self
    
    def end_frame(self) -> 'UICompositeBuilder':
        if len(self.current_stack) > 1:
            self.current_stack.pop()
        return self
    
    def build(self) -> CompositeElement:
        return self.root
