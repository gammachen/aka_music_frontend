# BabyAGI Function Engine - 智能函数调用框架

## 🎯 项目概述

BabyAGI Function Engine 是一个革命性的智能函数调用框架，它将传统函数执行与AI驱动的智能决策完美结合。该框架通过动态函数注册、向量搜索、智能匹配和自动执行等核心机制，实现了函数的智能发现、选择和调用。

### 核心特性

- **🧠 智能函数发现**: 基于向量相似度的函数匹配系统
- **🔧 动态函数注册**: 运行时函数注册和版本管理
- **🤖 AI驱动决策**: 使用LLM进行函数选择和参数生成
- **⚡ 自动执行链**: 函数触发器和依赖关系自动处理
- **📊 完整生命周期**: 从注册到执行的完整追踪和日志

## 🏗️ 系统架构

### 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    BabyAGI Function Engine                    │
├─────────────────────────────────────────────────────────────┤
│  Dashboard Layer    │  API Layer      │  Core Engine Layer  │
│  ┌─────────────┐    │  ┌───────────┐  │  ┌──────────────┐ │
│  │   Web UI    │    │  │ REST API  │  │  │ Functionz    │ │
│  │  (Flask)    │    │  │Endpoints  │  │  │ Framework    │ │
│  └─────────────┘    │  └───────────┘  │  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│              Function Packs & Extensions                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Default   │  │    AI       │  │  Custom     │         │
│  │  Functions  │  │ Functions   │  │ Functions   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. Functionz Framework (`babyagi/functionz/`)

**核心模块**:
- `framework.py`: 主框架类，提供函数注册和执行接口
- `registration.py`: 函数注册和元数据管理
- `execution.py`: 函数执行引擎，处理依赖注入和生命周期

**数据库层**:
- `db/db_router.py`: 数据库路由，支持本地SQLite存储
- `db/local_db.py`: 本地数据库实现
- `db/models.py`: 数据模型定义

#### 2. 函数包系统 (`babyagi/functionz/packs/`)

**默认函数包**:
- `default/`: 核心函数集合
  - `ai_functions.py`: AI相关函数（嵌入、搜索、描述生成）
  - `function_calling_chat.py`: 智能聊天函数调用
  - `default_functions.py`: 基础工具函数

## 🚀 技术实现详解

### 1. 动态函数注册机制

#### 函数注册流程

```python
# 示例：注册一个函数
from functionz.core.framework import func

@func.register_function(
    metadata={
        "description": "获取天气信息",
        "tags": ["weather", "api"]
    },
    imports=["requests"],
    dependencies=["get_location"],
    triggers=["location_updated"],
    input_parameters=[
        {
            "name": "city",
            "type": "str",
            "description": "城市名称",
            "required": True
        }
    ],
    output_parameters=[
        {
            "name": "weather_data",
            "type": "dict",
            "description": "天气数据"
        }
    ]
)
def get_weather(city: str) -> dict:
    """获取指定城市的天气信息"""
    # 函数实现
    return {"temperature": 25, "condition": "sunny"}
```

#### 注册机制解析

**1. AST解析函数签名**

```python
# registration.py 中的关键代码
import ast

def _parse_function_parameters(self, code: str) -> List[Dict[str, Any]]:
    """解析函数参数"""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            params = []
            for arg in node.args.args:
                param_info = {
                    'name': arg.arg,
                    'type': 'Any',
                    'required': True
                }
                # 处理类型注解
                if arg.annotation:
                    param_info['type'] = ast.unparse(arg.annotation)
                params.append(param_info)
            return params
```

**2. 依赖注入系统**

```python
# execution.py 中的依赖解析
class FunctionExecutor:
    def _resolve_dependencies(self, function_version, local_scope, parent_log_id):
        """解析并注入函数依赖"""
        
        # 1. 处理外部包依赖
        for imp in function_imports:
            if imp['name'] not in local_scope:
                module = self._install_external_dependency(
                    imp['lib'] or imp['name'], 
                    imp['name']
                )
                local_scope[imp['name']] = module
        
        # 2. 处理函数依赖
        for dep_name in function_version.get('dependencies', []):
            if dep_name not in local_scope:
                dep_data = self.python_func.db.get_function(dep_name)
                self._resolve_dependencies(dep_data, local_scope, parent_log_id)
                
                # 动态执行依赖函数代码
                exec(dep_data['code'], local_scope)
                
                # 包装依赖函数以支持链式调用
                dep_func = local_scope[dep_name]
                local_scope[dep_name] = self._create_function_wrapper(
                    dep_func, dep_name, parent_log_id
                )
```

### 2. 智能函数调用机制

#### 向量搜索系统

**1. 函数嵌入生成**

```python
# ai_functions.py 中的嵌入机制
@func.register_function
def embed_function_description(function: str) -> None:
    """为函数描述生成向量嵌入"""
    
    # 1. 获取函数描述
    function_data = func.db.get_function(function)
    description = function_data.get('metadata', {}).get('description', '')
    
    # 2. 生成嵌入向量
    embedding = func.embed_input(description)
    
    # 3. 存储到CSV文件
    with open('function_embeddings.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([function, str(embedding)])
```

**2. 相似度搜索算法**

```python
@func.register_function
def find_similar_function(description: str, top_n: int = 3):
    """基于描述查找相似函数"""
    
    # 1. 嵌入用户描述
    input_embedding = func.embed_input(description)
    
    # 2. 计算余弦相似度
    from sklearn.metrics.pairwise import cosine_similarity
    similarities = cosine_similarity([input_embedding], stored_embeddings)
    
    # 3. 返回最相似的函数
    sorted_indices = np.argsort(similarities[0])[::-1]
    return [stored_functions[i] for i in sorted_indices[:top_n]]
```

#### AI驱动的函数选择

**1. 函数调用聊天系统**

```python
# function_calling_chat.py 中的智能调用
@func.register_function
def chat_with_functions(chat_history, available_function_names):
    """智能函数调用聊天系统"""
    
    # 1. 构建工具定义
    tools = []
    for func_name in available_function_names:
        function_data = get_function_wrapper(func_name)
        tool = {
            "type": "function",
            "function": {
                "name": function_data['name'],
                "description": function_data['metadata']['description'],
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        # 添加参数定义
        for param in function_data.get('input_parameters', []):
            tool['function']['parameters']['properties'][param['name']] = {
                "type": self._map_python_type_to_json(param['type']),
                "description": param.get('description', '')
            }
            if param.get('required', False):
                tool['function']['parameters']['required'].append(param['name'])
    
    # 2. 调用LLM进行函数选择
    response = litellm.completion(
        model=os.getenv('OPENAI_MODEL'),
        messages=chat_history,
        tools=tools,
        tool_choice="auto"
    )
    
    # 3. 执行选中的函数
    tool_calls = response['choices'][0]['message'].get('tool_calls', [])
    for tool_call in tool_calls:
        function_name = tool_call['function']['name']
        function_args = json.loads(tool_call['function']['arguments'])
        
        # 使用框架执行函数
        result = execute_function_wrapper(function_name, **function_args)
```

### 3. 函数生命周期管理

#### 版本控制系统

```python
# 数据库中的版本管理
class FunctionVersion(Base):
    __tablename__ = 'function_versions'
    
    id = Column(Integer, primary_key=True)
    function_id = Column(Integer, ForeignKey('functions.id'))
    version = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # 元数据存储
    function_metadata = Column(JSON)
    input_parameters = Column(JSON)
    output_parameters = Column(JSON)
    dependencies = relationship('Function', secondary='function_dependencies')
```

#### 触发器系统

```python
# 函数触发器机制
class TriggerManager:
    def add_trigger(self, triggered_function: str, triggering_function: str):
        """添加函数触发器"""
        with self.session_scope() as session:
            # 存储触发关系
            trigger = Trigger(
                triggered_function=triggered_function,
                triggering_function=triggering_function
            )
            session.add(trigger)
    
    def execute_triggers(self, function_name: str, output: Any, parent_log_id: int):
        """执行函数触发器"""
        triggered_functions = self.db.get_triggers_for_function(function_name)
        
        for triggered_func in triggered_functions:
            # 递归执行触发函数
            self.execute(
                triggered_func,
                output,  # 将上一个函数的输出作为参数
                parent_log_id=parent_log_id,
                triggered_by_log_id=parent_log_id
            )
```

### 4. 执行引擎详解

#### 安全执行环境

```python
class FunctionExecutor:
    def execute(self, function_name: str, *args, **kwargs):
        """安全执行函数"""
        
        # 1. 创建隔离的执行环境
        local_scope = {
            'func': self.python_func,  # 注入框架实例
            'parent_log_id': log_id,
            'datetime': datetime
        }
        
        # 2. 依赖注入
        self._resolve_dependencies(function_version, local_scope, log_id)
        
        # 3. 密钥注入（安全环境变量）
        self._inject_secret_keys(local_scope)
        
        # 4. 参数验证
        bound_args = self._bind_function_arguments(func, args, kwargs)
        self._validate_input_parameters(function_version, bound_args)
        
        # 5. 执行函数
        exec(function_version['code'], local_scope)
        result = local_scope[function_name](*bound_args.args, **bound_args.kwargs)
        
        # 6. 触发器执行
        self._execute_triggered_functions(function_name, result, log_id)
        
        return result
```

## 🛠️ 快速开始

### 环境配置

1. **克隆项目**
```bash
git clone <repository-url>
cd babyagi-agent-native/babyagi-main
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 复制并编辑.env文件
cp .env.example .env
# 编辑.env文件，设置API密钥
nano .env
```

### 基本使用

#### 1. 启动系统

```bash
python main.py
```

#### 2. 注册自定义函数

```python
from babyagi import func

@func.register_function(
    metadata={"description": "计算两个数的和"},
    input_parameters=[
        {"name": "a", "type": "int", "description": "第一个数"},
        {"name": "b", "type": "int", "description": "第二个数"}
    ]
)
def add_numbers(a: int, b: int) -> int:
    return a + b

# 执行函数
result = func.add_numbers(5, 3)
print(f"结果: {result}")  # 输出: 结果: 8
```

#### 3. 智能函数调用

```python
# 使用AI进行函数选择
from babyagi.functionz.packs.default.ai_functions import find_similar_function

# 查找相关函数
similar_funcs = find_similar_function("计算数学表达式", top_n=3)
print("相关函数:", similar_funcs)

# 使用聊天系统进行函数调用
from babyagi.functionz.packs.default.function_calling_chat import chat_with_functions

chat_history = [
    {"role": "user", "message": "帮我计算3乘以4的结果"}
]

result = chat_with_functions(
    chat_history=chat_history,
    available_function_names=["add_numbers", "multiply_numbers"]
)
print(result)  # AI会自动选择multiply_numbers函数并执行
```

#### 4. 函数触发器示例

```python
# 创建触发器函数
@func.register_function(
    metadata={"description": "当新用户注册时发送欢迎邮件"},
    triggers=["user_registered"]
)
def send_welcome_email(user_email: str):
    print(f"发送欢迎邮件到: {user_email}")
    return f"邮件已发送到 {user_email}"

# 注册新用户会触发send_welcome_email
@func.register_function(
    metadata={"description": "注册新用户"}
)
def register_user(email: str, name: str):
    # 注册用户逻辑
    print(f"注册用户: {name} ({email})")
    
    # 这个函数的输出会触发send_welcome_email
    return {"email": email, "name": name}
```

## 📊 API 文档

### REST API 端点

#### 1. 函数管理

```http
# 获取所有函数
GET /api/functions

# 获取特定函数
GET /api/functions/{function_name}

# 注册新函数
POST /api/functions
{
    "name": "function_name",
    "code": "def function_name(): ...",
    "metadata": {"description": "函数描述"}
}

# 更新函数
PUT /api/functions/{function_name}

# 删除函数
DELETE /api/functions/{function_name}
```

#### 2. 函数执行

```http
# 执行函数
POST /api/execute/{function_name}
{
    "args": ["arg1", "arg2"],
    "kwargs": {"key": "value"}
}
```

#### 3. 日志和监控

```http
# 获取执行日志
GET /api/logs
GET /api/logs/{log_id}

# 获取函数调用链
GET /api/logs/{log_id}/bundle
```

### WebSocket API

```javascript
// 实时函数执行
const ws = new WebSocket('ws://localhost:5000/ws/execute');

ws.onmessage = function(event) {
    const log = JSON.parse(event.data);
    console.log('执行日志:', log);
};

// 发送执行请求
ws.send(JSON.stringify({
    function: 'my_function',
    args: ['arg1', 'arg2'],
    kwargs: {key: 'value'}
}));
```

## 🔧 高级特性

### 1. 自定义函数包

创建自定义函数包：

```python
# my_package/custom_functions.py
from functionz.core.framework import func

@func.register_function(
    metadata={"description": "我的自定义函数"},
    package="my_package"
)
def my_custom_function():
    return "Hello from custom package!"

# 加载自定义包
func.load_functions("my_package/")
```

### 2. 环境变量管理

```python
# 设置密钥
func.db.add_secret_key("MY_API_KEY", "secret_value")

# 在函数中使用
@func.register_function(
    key_dependencies=["MY_API_KEY"]
)
def use_secret():
    api_key = os.getenv("MY_API_KEY")
    return f"使用密钥: {api_key}"
```

### 3. 性能优化

```python
# 批量函数注册
functions = [
    {"name": "func1", "code": "..."},
    {"name": "func2", "code": "..."}
]
for func_data in functions:
    func.register_function(**func_data)

# 缓存函数结果
@func.register_function(
    metadata={"cache_ttl": 300}  # 5分钟缓存
)
def cached_function():
    return expensive_computation()
```

## 🐛 调试和监控

### 1. 日志系统

```python
# 查看函数执行日志
logs = func.db.get_logs(function_name="my_function")
for log in logs:
    print(f"时间: {log['timestamp']}")
    print(f"参数: {log['params']}")
    print(f"结果: {log['output']}")
    print(f"耗时: {log['time_spent']}s")
```

### 2. 调试模式

```bash
# 启用调试日志
export DEBUG=true
python main.py

# 或者在代码中
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. 性能分析

```python
# 分析函数性能
import time

@func.register_function(
    metadata={"profile": True}
)
def profiled_function():
    start = time.time()
    result = do_work()
    elapsed = time.time() - start
    return {"result": result, "elapsed": elapsed}
```

## 📝 开发指南

### 1. 开发环境设置

```bash
# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/
```

### 2. 代码规范

```python
# 函数命名规范
@func.register_function(
    metadata={
        "description": "清晰的功能描述",
        "category": "数据处理"
    }
)
def process_data_with_validation(data: List[str]) -> Dict[str, Any]:
    """
    详细的函数文档字符串
    
    Args:
        data: 输入数据列表
        
    Returns:
        处理后的数据字典
        
    Raises:
        ValueError: 当数据格式无效时
    """
    if not data:
        raise ValueError("数据不能为空")
    
    # 实现逻辑
    return {"processed": data, "count": len(data)}
```

### 3. 测试用例

```python
# tests/test_functions.py
import pytest
from babyagi import func

def test_add_numbers():
    @func.register_function
    def add_numbers(a: int, b: int) -> int:
        return a + b
    
    result = func.add_numbers(2, 3)
    assert result == 5

def test_function_metadata():
    func_info = func.db.get_function("add_numbers")
    assert func_info["metadata"]["description"] is not None
```

## 🤝 贡献指南

### 1. 提交Issue

- 使用Issue模板
- 提供详细的复现步骤
- 包含相关日志和错误信息

### 2. 代码贡献

- Fork项目
- 创建功能分支 (`git checkout -b feature/amazing-feature`)
- 提交更改 (`git commit -m 'Add amazing feature'`)
- 推送到分支 (`git push origin feature/amazing-feature`)
- 创建Pull Request

### 3. 文档贡献

- 更新API文档
- 添加使用示例
- 完善README

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 支持与社区

- **GitHub Issues**: [提交问题](https://github.com/your-repo/issues)
- **Discussions**: [参与讨论](https://github.com/your-repo/discussions)
- **Discord**: [加入社区](https://discord.gg/your-server)
- **文档**: [完整文档](https://docs.babyagi-function-engine.com)

## 🏆 致谢

感谢以下项目和社区的支持：

- [LiteLLM](https://github.com/BerriAI/litellm) - 统一的LLM API
- [Sentence Transformers](https://www.sbert.net/) - 句子嵌入
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM框架

---

<div align="center">
  <p>
    <b>BabyAGI Function Engine</b> - 让函数调用更智能
  </p>
  <p>
    <a href="#快速开始">快速开始</a> •
    <a href="#api文档">API文档</a> •
    <a href="#开发指南">开发指南</a>
  </p>
</div>