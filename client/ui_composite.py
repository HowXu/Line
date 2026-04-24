from abc import ABC, abstractmethod
from client.ui_component import UIComponent

# 组合模式
# 将 UI 组件组织成树形结构，统一处理单个组件和组件容器

class UIElement(ABC):
    """UI 元素抽象基类（组合模式的 Component）"""
    
    @abstractmethod
    def build(self, parent) -> any:
        """构建 UI 元素"""
        pass
    
    @abstractmethod
    def add_child(self, child):
        """添加子元素"""
        pass
    
    @abstractmethod
    def remove_child(self, child):
        """移除子元素"""
        pass
    
    @abstractmethod
    def get_children(self):
        """获取子元素列表"""
        pass


class LeafElement(UIElement):
    """叶子节点（组合模式的 Leaf）"""
    
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
        raise NotImplementedError("叶子节点不能添加子元素")
    
    def remove_child(self, child):
        raise NotImplementedError("叶子节点不能移除子元素")
    
    def get_children(self):
        return self.children.copy()
    
    def get_component(self):
        return self.component


class CompositeElement(UIElement):
    """复合节点（组合模式的 Composite）"""
    
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
    """UI 组合结构构建器"""
    
    def __init__(self):
        self.root = None
        self.current_stack = []
    
    def set_root(self, root: CompositeElement):
        self.root = root
        self.current_stack = [root]
        return self
    
    def add_frame(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        """添加框架容器"""
        frame = CompositeElement(component, pack_config)
        current_parent = self.current_stack[-1]
        current_parent.add_child(frame)
        self.current_stack.append(frame)
        return self
    
    def add_label(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        """添加标签"""
        label = LeafElement(component, pack_config)
        current_parent = self.current_stack[-1]
        current_parent.add_child(label)
        return self
    
    def add_button(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        """添加按钮"""
        button = LeafElement(component, pack_config)
        current_parent = self.current_stack[-1]
        current_parent.add_child(button)
        return self
    
    def add_textbox(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        """添加文本框"""
        textbox = LeafElement(component, pack_config)
        current_parent = self.current_stack[-1]
        current_parent.add_child(textbox)
        return self
    
    def end_frame(self) -> 'UICompositeBuilder':
        """结束当前框架"""
        if len(self.current_stack) > 1:
            self.current_stack.pop()
        return self
    
    def build(self) -> CompositeElement:
        return self.root
