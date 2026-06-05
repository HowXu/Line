from abc import ABC, abstractmethod
from client.ui_component import UIComponent

# ---------------------------------------------------------------------------
# 组合模式（Composite Pattern）
# ---------------------------------------------------------------------------
# 角色：
#   - Component（抽象构件）：UIElement
#         - 统一叶子节点与组合节点的接口
#   - Leaf（叶子节点）：LeafElement
#   - Composite（组合节点）：CompositeElement
#   - Client（客户端）：window.py / ui_decorator.py 等
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 建造者模式（Builder Pattern）
# ---------------------------------------------------------------------------
# 角色：
#   - Product（产品）：UIComposite
#   - Builder（抽象建造者）：UIBuilder
#   - ConcreteBuilder（具体建造者）：UICompositeBuilder
#   - Director（指挥者）：UIDirector
# ---------------------------------------------------------------------------


# ============================================================
# 组合模式 —— 抽象构件
# ============================================================
class UIElement(ABC):
    """组合模式抽象构件。"""

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


# ============================================================
# 组合模式 —— 叶子节点
# ============================================================
class LeafElement(UIElement):
    """叶子节点：只承载单个 UIComponent，不持有 children。"""

    def __init__(self, component: UIComponent, pack_config: dict = None):
        self.component = component
        self.pack_config = pack_config or {}

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
        return []

    def get_component(self):
        return self.component


# ============================================================
# 组合模式 —— 组合节点
# ============================================================
class CompositeElement(UIElement):
    """组合节点：可包含若干子节点。"""

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


# ============================================================
# 建造者模式 —— 产品
# ============================================================
class UIComposite:
    """产品：聚合 UIElement 树 + 持有根节点。"""

    def __init__(self):
        self._root: UIElement = None

    def set_root(self, root: UIElement):
        self._root = root

    def get_root(self) -> UIElement:
        return self._root

    def build(self, parent):
        if self._root is None:
            raise ValueError("UIComposite has no root element")
        return self._root.build(parent)

    def __str__(self) -> str:
        return f"UIComposite(root={self._root})"


# ============================================================
# 建造者模式 —— 抽象建造者
# ============================================================
class UIBuilder(ABC):
    """抽象建造者：定义分步构造 UI 复合树的统一接口。"""

    @abstractmethod
    def reset(self) -> 'UIBuilder':
        pass

    @abstractmethod
    def set_root(self, root_element: UIElement) -> 'UIBuilder':
        pass

    @abstractmethod
    def add_frame(self, component: UIComponent, pack_config: dict = None) -> 'UIBuilder':
        pass

    @abstractmethod
    def add_label(self, component: UIComponent, pack_config: dict = None) -> 'UIBuilder':
        pass

    @abstractmethod
    def add_button(self, component: UIComponent, pack_config: dict = None) -> 'UIBuilder':
        pass

    @abstractmethod
    def add_textbox(self, component: UIComponent, pack_config: dict = None) -> 'UIBuilder':
        pass

    @abstractmethod
    def end_frame(self) -> 'UIBuilder':
        pass

    @abstractmethod
    def get_product(self) -> UIComposite:
        pass


# ============================================================
# 建造者模式 —— 具体建造者
# ============================================================
class UICompositeBuilder(UIBuilder):
    """具体建造者：使用 UIElement 树作为内部表示，构造结束后产出 UIComposite 产品。"""

    def __init__(self):
        self._product = UIComposite()
        self._current_stack = []
        self.reset()

    def reset(self) -> 'UICompositeBuilder':
        self._product = UIComposite()
        self._current_stack = []
        return self

    def set_root(self, root_element: UIElement) -> 'UICompositeBuilder':
        self._product.set_root(root_element)
        self._current_stack = [root_element]
        return self

    def _add_child(self, child: UIElement) -> 'UICompositeBuilder':
        if not self._current_stack:
            raise RuntimeError("必须在 set_root 之后才能 add_*")
        self._current_stack[-1].add_child(child)
        return self

    def add_frame(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        frame = CompositeElement(component, pack_config)
        self._add_child(frame)
        self._current_stack.append(frame)
        return self

    def add_label(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        self._add_child(LeafElement(component, pack_config))
        return self

    def add_button(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        self._add_child(LeafElement(component, pack_config))
        return self

    def add_textbox(self, component: UIComponent, pack_config: dict = None) -> 'UICompositeBuilder':
        self._add_child(LeafElement(component, pack_config))
        return self

    def end_frame(self) -> 'UICompositeBuilder':
        if len(self._current_stack) > 1:
            self._current_stack.pop()
        return self

    def get_product(self) -> UIComposite:
        product = self._product
        self.reset()
        return product

    # 兼容老 API
    def build(self) -> CompositeElement:
        return self._product.get_root()


# ============================================================
# 建造者模式 —— 指挥者
# ============================================================
class UIDirector:
    """指挥者：定义标准聊天窗口的构造流程，调用方只关心流程不关心步骤细节。"""

    def __init__(self, builder: UIBuilder):
        self._builder = builder

    def set_builder(self, builder: UIBuilder):
        self._builder = builder

    def build_chat_window(self, components: dict) -> UIComposite:
        """
        构造标准聊天窗口的流程：
            1. reset + set_root
            2. 顶部 frame
            3. 聊天区 frame
            4. 底部 frame
            5. get_product
        """
        self._builder.reset()
        self._builder.set_root(components["root"])
        # 顶部
        self._builder.add_frame(components["top_frame"], components["top_frame_pack"])
        self._builder.add_label(components["friend_label"], components["friend_label_pack"])
        self._builder.end_frame()
        # 聊天区
        self._builder.add_frame(components["chat_frame"], components["chat_frame_pack"])
        self._builder.end_frame()
        # 输入区
        self._builder.add_frame(components["input_frame"], components["input_frame_pack"])
        self._builder.add_textbox(components["input_textbox"], components["input_textbox_pack"])
        self._builder.add_button(components["send_button"], components["send_button_pack"])
        self._builder.end_frame()
        return self._builder.get_product()
