# Line - AI Chat Application

<div align="center">

**一个基于设计模式的现代化 AI 聊天应用**

*A Modern AI Chat Application Built with Design Patterns*

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.0+-green.svg)](https://customtkinter.tomschimansky.com/)
[![DeepSeek API](https://img.shields.io/badge/DeepSeek-API-orange.svg)](https://platform.deepseek.com/)

</div>

---

<div align="center">

![Application Screenshot](shoot.png)

*Line AI Chat Application Interface*

</div>

---

## 📖 项目描述 | Project Description

Line 是一个优雅的 AI 聊天客户端应用程序，模拟与前任女友的对话场景。项目采用多种经典设计模式，确保代码的可维护性、可扩展性和清晰度。

Line is an elegant AI chat client application that simulates conversation scenarios with an ex-girlfriend. The project employs multiple classic design patterns to ensure code maintainability, scalability, and clarity.

### ✨ 特性 | Features

- 🎨 **现代化 UI** - 基于 CustomTkinter 的深色主题界面
- 🤖 **AI 驱动** - 集成 DeepSeek API，提供智能对话能力
- 🏗️ **设计模式** - 应用 **12 种**设计模式，构建清晰的代码架构
- 💾 **数据持久化** - PostgreSQL 数据库存储聊天记录
- 🌐 **双语支持** - 完整的中英文文档和注释

---

## 🛠️ 技术栈 | Tech Stack

### 核心框架 | Core Framework
- **Python 3.12+** - 主要编程语言
- **CustomTkinter 5.0+** - 现代化 GUI 框架
- **Pillow** - 图像处理

### AI 与 API | AI & API
- **DeepSeek API** - AI 对话引擎
- **OpenAI SDK** - API 客户端库
- **python-dotenv** - 环境变量管理

### 数据库 | Database
- **PostgreSQL** - 关系型数据库
- **psycopg2** - PostgreSQL 适配器

### 设计模式 | Design Patterns

#### 创建型模式 (Creational Patterns) - 5 种
1. **单例模式 (Singleton)** - 主窗口、享元工厂 ⭐
2. **抽象工厂模式 (Abstract Factory)** - SQL 管理器创建
3. **简单工厂模式 (Simple Factory)** - 管理器工厂、日志格式化器工厂 ⭐
4. **工厂方法模式 (Factory Method)** - 日志策略创建 ⭐
5. **建造者模式 (Builder)** - UI 组合构建、数据对象构建

#### 结构型模式 (Structural Patterns) - 6 种
6. **桥接模式 (Bridge)** - UI 组件抽象 ⭐
7. **组合模式 (Composite)** - UI 组件树 ⭐
8. **装饰模式 (Decorator)** - UI 功能增强 ⭐
9. **外观模式 (Facade)** - 消息渲染外观 ⭐ NEW
10. **享元模式 (Flyweight)** - UI 对象缓存 ⭐ NEW
11. **代理模式 (Proxy)** - 应用程序启动代理 ⭐ NEW
12. **适配器模式 (Adapter)** - 日志记录器

#### 行为型模式 (Behavioral Patterns) - 1 种
13. **策略模式 (Strategy)** - 日志格式化策略 ⭐ NEW

---

## 📦 安装与配置 | Installation & Configuration

### 1. 环境要求 | Requirements

```bash
Python 3.12 或更高版本
PostgreSQL 12 或更高版本
```

### 2. 安装依赖 | Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量 | Configure Environment Variables

**重要：** 将 `.env.example` 文件重命名为 `.env`，并填写配置信息

**Important:** Rename `.env.example` to `.env` and fill in the configuration

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# API_KEY=your_api_key_here
# BASE_URL=https://api.deepseek.com
# MODEL=deepseek-reasoner
```

### 4. 数据库配置 | Database Configuration

#### WSL 环境配置 | WSL Environment Setup

**注意：** PostgreSQL 运行在 WSL (Windows Subsystem for Linux) 中

**Note:** PostgreSQL runs in WSL (Windows Subsystem for Linux)

```bash
# 1. 进入 WSL
wsl

# 2. 启动 PostgreSQL 服务
sudo service postgresql start

# 3. 切换到 postgres 用户
sudo -i -u postgres

# 4. 进入 PostgreSQL 命令行
psql
```

#### 数据库创建 | Database Creation

```sql
-- 创建数据库
CREATE DATABASE records;

-- 切换到数据库
\c records;

-- 创建聊天记录表
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- 创建索引以优化查询性能
CREATE INDEX idx_updated_at ON chat_messages(updated_at DESC);

-- 设置默认权限（如果需要）
GRANT ALL PRIVILEGES ON DATABASE records TO howxu;
GRANT ALL PRIVILEGES ON TABLE chat_messages TO howxu;
GRANT USAGE, SELECT ON SEQUENCE chat_messages_id_seq TO howxu;
```

#### 连接配置 | Connection Configuration

默认数据库连接参数（在 `server/sql.py` 中配置）：

Default database connection parameters (configured in `server/sql.py`):

```python
conn_params = {
    'host': '127.0.0.1',      # WSL 中的 PostgreSQL
    'port': '5432',           # 默认 PostgreSQL 端口
    'database': 'records',    # 数据库名称
    'user': 'howxu',          # 用户名
    'password': 'howxu'       # 密码
}
```

**重要提示：** 从 Windows 访问 WSL 中的 PostgreSQL，需要确保：

**Important:** To access PostgreSQL in WSL from Windows, ensure:

1. PostgreSQL 监听所有网络接口（修改 `postgresql.conf` 中的 `listen_addresses = '*'`）
2. 配置 `pg_hba.conf` 允许远程连接
3. WSL 防火墙允许 5432 端口

---

## 🚀 使用方法 | Usage

### 启动应用 | Start Application

```bash
python main.py
```

### 项目结构 | Project Structure

```
SheJiMode/
├── client/                 # 客户端 UI 模块
│   ├── window.py          # 主窗口（单例模式）
│   ├── ui_component.py    # UI 组件（桥接模式）⭐
│   ├── ui_composite.py    # UI 组合（组合模式）⭐
│   ├── ui_decorator.py    # UI 装饰器（装饰模式）⭐
│   ├── ui_facade.py       # UI 渲染外观（外观模式）⭐ NEW
│   └── ui_flyweight.py    # UI 享元工厂（享元模式）⭐ NEW
├── server/                # 服务端逻辑模块
│   ├── factory.py         # 管理器工厂（简单工厂模式）
│   ├── sql.py             # SQL 管理器（抽象工厂模式）
│   ├── data.py            # 数据管理（建造者模式）
│   ├── ai.py              # AI API 集成
│   ├── logger.py          # 日志适配器（适配器模式）
│   ├── log_strategy.py    # 日志策略（工厂方法模式）⭐ NEW
│   └── log_formatter_factory.py  # 日志格式化器工厂（简单工厂模式）⭐ NEW
├── resources/             # 资源文件
│   ├── icon.ico          # 应用图标
│   └── ta.png            # 头像图片
├── main.py               # 程序入口（代理模式）⭐ NEW
├── .env                  # 环境变量配置（需自行创建）
└── README.md             # 项目文档
```

---

## 📝 开发指南 | Development Guide

### 代码规范 | Code Style

- 遵循 PEP 8 编码规范
- 使用类型注解（Type Hints）
- 函数和类必须有清晰的文档字符串
- 保持单一职责原则

### 添加新的 UI 组件 | Adding New UI Components

使用桥接模式，在 `ui_component.py` 中添加：

```python
class NewComponent(UIComponent):
    def __init__(self, **kwargs):
        # 初始化参数
        pass
    
    def create(self, parent):
        # 创建组件
        pass
    
    def get_component(self):
        # 返回组件实例
        pass
```

### 添加新的装饰器 | Adding New Decorators

在 `ui_decorator.py` 中添加：

```python
class NewDecorator(UIDecorator):
    def build(self, parent):
        widget = super().build(parent)
        # 添加额外功能
        return widget
```

### 设计模式应用原则 | Design Pattern Principles

1. **不要过度设计** - 只在必要时使用设计模式
2. **保持简洁** - 优先选择最简单的解决方案
3. **可测试性** - 确保代码易于单元测试
4. **文档化** - 为复杂逻辑添加清晰的注释

---

## 🎨 设计模式详解 | Design Patterns Details

### 创建型模式 | Creational Patterns

#### 1. 单例模式 (Singleton)
**文件**: [`window.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/client/window.py#L21-L27), [`ui_flyweight.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/client/ui_flyweight.py#L9-L18)
```python
class MainWindow:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

#### 2. 抽象工厂模式 (Abstract Factory)
**文件**: [`sql.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/server/sql.py#L15-L30)
```python
class SQLManager(ABC):
    @abstractmethod
    def connect(self): pass
    @abstractmethod
    def save_new(self, sender, text): pass

class PostgreSQLFactory:
    def create_sql_manager(self, dataManager):
        return PostgreSQLManager(dataManager)
```

#### 3. 简单工厂模式 (Simple Factory)
**文件**: [`factory.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/server/factory.py#L5-L23), [`log_formatter_factory.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/server/log_formatter_factory.py#L10-L43)
```python
class LogFormatterFactory:
    @classmethod
    def create(cls, log_type: str) -> LogStrategy:
        return cls._strategies[log_type]()
```

#### 4. 工厂方法模式 (Factory Method)
**文件**: [`log_strategy.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/server/log_strategy.py#L7-L154)
```python
class LogStrategy(ABC):
    @abstractmethod
    def format(self, data: Any, max_length: int = 200) -> str: pass
    
    @abstractmethod
    def log(self, data: Any, prefix: str = "", max_length: int = 200): pass
```

#### 5. 建造者模式 (Builder)
**文件**: [`ui_composite.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/client/ui_composite.py#L68-L123)
```python
class UICompositeBuilder:
    def frame(self, **kwargs) -> 'UICompositeBuilder': ...
    def label(self, **kwargs) -> 'UICompositeBuilder': ...
    def button(self, **kwargs) -> 'UICompositeBuilder': ...
```

### 结构型模式 | Structural Patterns

#### 6. 桥接模式 (Bridge)
**文件**: [`ui_component.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/client/ui_component.py#L5-L10)

#### 7. 组合模式 (Composite)
**文件**: [`ui_composite.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/client/ui_composite.py#L5-L23)

#### 8. 装饰模式 (Decorator)
**文件**: [`ui_decorator.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/client/ui_decorator.py#L5-L24)

#### 9. 外观模式 (Facade) ⭐ NEW
**文件**: [`ui_facade.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/client/ui_facade.py#L8-L162)
```python
class ChatRendererFacade:
    def render_message(self, text: str, sender: str, avatar_image=None):
        """统一的渲染接口"""
        if sender == "me":
            self.message_renderer.render_send_message(text)
        elif sender == "ta":
            self.message_renderer.render_receive_message(text, avatar_image)
```

#### 10. 享元模式 (Flyweight) ⭐ NEW
**文件**: [`ui_flyweight.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/client/ui_flyweight.py#L6-L153)
```python
class UIFlyweightFactory:
    _flyweights = {}  # 缓存可复用的配置
    _image_cache = {}  # 缓存图片对象
    
    def get_circular_image(self, image_path: str, size: int = 40):
        # 缓存圆形头像图片
        cache_key = f"{image_path}_{size}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
```

#### 11. 代理模式 (Proxy) ⭐ NEW
**文件**: [`main.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/main.py#L7-L137)
```python
class ApplicationProxy(IApplication):
    def launch(self):
        self._pre_launch_checks()  # 启动前检查
        if self.real_app is None:
            self.real_app = RealApplication()
        self.real_app.launch()
```

#### 12. 适配器模式 (Adapter)
**文件**: [`logger.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/server/logger.py#L1-L18)

### 行为型模式 | Behavioral Patterns

#### 13. 策略模式 (Strategy) ⭐ NEW
**文件**: [`log_strategy.py`](file:///c:/Users/HowXu/Desktop/SchoolShit/SheJiMode/server/log_strategy.py)
```python
class APILogStrategy(LogStrategy): ...
class RequestLogStrategy(LogStrategy): ...
class ResponseLogStrategy(LogStrategy): ...
class DebugLogStrategy(LogStrategy): ...
```

---

## ⚠️ 注意事项 | Important Notes

### 安全警告 | Security Warning

- ⚠️ **切勿提交 `.env` 文件到版本控制系统**
- ⚠️ **Never commit `.env` file to version control**
- 确保 `.env` 文件已添加到 `.gitignore`
- Make sure `.env` is added to `.gitignore`

### 数据库连接 | Database Connection

#### WSL 特定配置 | WSL Specific Configuration

- ✅ 确保 WSL 中的 PostgreSQL 服务已启动：`sudo service postgresql start`
- ✅ 配置 PostgreSQL 监听所有接口（`/etc/postgresql/*/main/postgresql.conf`）：
  ```
  listen_addresses = '*'
  ```
- ✅ 配置客户端认证（`/etc/postgresql/*/main/pg_hba.conf`）：
  ```
  host    all             all             0.0.0.0/0               md5
  ```
- ✅ 重启 PostgreSQL 服务：`sudo service postgresql restart`
- ✅ 从 Windows 测试连接：
  ```bash
  psql -h 127.0.0.1 -U howxu -d records
  ```

#### 常规检查 | General Checks

- 确保 PostgreSQL 服务正在运行
- 检查数据库连接配置是否正确
- 验证数据库表结构是否完整
- 确认用户权限设置正确

### API 使用 | API Usage

- 注意 API 调用频率限制
- 合理控制 token 使用量
- 处理 API 错误和超时情况

### UI 组件 | UI Components

- 所有 UI 组件必须指定 `height` 或其他必要参数
- 避免传递 `None` 值给 customtkinter
- 使用装饰器模式添加功能，而非修改原有组件

---

## 🧪 测试 | Testing

```bash
# 运行单元测试
python -m pytest tests/

# 代码风格检查
flake8 .

# 类型检查
mypy .
```

---

## 📄 许可证 | License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 贡献 | Contributing

欢迎贡献代码！请遵循以下步骤：

Contributions are welcome! Please follow these steps:

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📬 联系方式 | Contact

如有问题或建议，请通过以下方式联系：

For questions or suggestions, please contact via:

- **项目仓库**: [GitHub Issues](https://github.com/HowXu/Line/issues)

---

<div align="center">

**Made with ❤️ using Design Patterns**

*感谢使用设计模式让代码更优雅！*

*Thank you for using design patterns to make code more elegant!*

</div>
