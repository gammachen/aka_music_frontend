# ADALA Agent 快速参考卡片

## 🚀 快速开始

### 基础创建
```python
from adala.agents import Agent
from adala.environments import StaticEnvironment
from adala.skills import LinearSkillSet, TransformSkill

# 最简创建
agent = Agent(
    skills=LinearSkillSet(skills=[TransformSkill()]),
    environment=StaticEnvironment(df=data)
)
```

### 运行模式
```python
# 同步执行
predictions = agent.run()

# 异步执行
import asyncio
results = asyncio.run(agent.arun())

# 带输入执行
predictions = agent.run(input=my_dataframe)
```

## 🔧 核心API

### 主要方法
| 方法 | 描述 | 参数 |
|------|------|------|
| `run()` | 同步执行 | `input`, `runtime`, `**kwargs` |
| `arun()` | 异步执行 | `input`, `runtime` |
| `learn()` | 启动学习 | `learning_iterations`, `accuracy_threshold`, `batch_size` |
| `arefine_skill()` | 异步技能优化 | `skill_name`, `input_variables`, `data` |

### 运行时选择
```python
# 获取运行时
runtime = agent.get_runtime('fast')
teacher = agent.get_teacher_runtime('teacher')
```

## 🎯 配置模板

### 多运行时配置
```python
agent = Agent(
    skills=LinearSkillSet(skills=[...]),
    runtimes={
        'fast': OpenAIChatRuntime(model='gpt-3.5-turbo'),
        'accurate': OpenAIChatRuntime(model='gpt-4'),
        'local': LiteLLMRuntime(model='ollama/llama2')
    },
    default_runtime='fast',
    teacher_runtimes={
        'teacher': OpenAIChatRuntime(model='gpt-4')
    }
)
```

### YAML配置
```yaml
# workflow.yml
skills:
  - name: classifier
    type: transform
    instructions: "Classify the sentiment"
    input_template: "Text: {text}"
    output_template: "Sentiment: {sentiment}"

# 使用配置
agent = create_agent_from_file('workflow.yml')
```

## 📊 学习参数

### 学习配置
```python
agent.learn(
    learning_iterations=3,      # 迭代次数
    accuracy_threshold=0.9,     # 准确率阈值
    batch_size=100,             # 批次大小
    num_feedbacks=50,           # 反馈数量
    runtime='fast',             # 执行运行时
    teacher_runtime='teacher'   # 教师运行时
)
```

## 🔍 调试技巧

### 日志查看
```python
# 启用详细日志
runtime = OpenAIChatRuntime(verbose=True)

# 查看技能改进
agent.learn(...)
# 会自动显示指令变更对比
```

### 性能监控
```python
# 成本估算
from adala.runtimes.base import CostEstimate
cost = runtime.estimate_cost(batch_size=100)
print(f"预估成本: ${cost.total_cost_usd}")
```

## 🚨 常见错误

### 运行时错误
```python
# 错误：运行时未找到
ValueError: Runtime "fast" not found
# 解决：检查 runtimes 字典

# 错误：异步运行时类型错误
ValueError: 必须使用 AsyncRuntime
# 解决：使用 AsyncRuntime 实例
```

### 环境错误
```python
# 错误：环境未设置
ValueError: input is None and no environment is set
# 解决：设置 environment 或提供 input
```

## 🔄 异步模式

### 流式处理
```python
async def stream_process():
    agent = Agent(...)
    
    # 持续处理直到数据耗尽
    await agent.arun()
    
    # 单批处理
    results = await agent.arun(input=data_batch)
    return results
```

### 错误处理
```python
async def safe_process():
    try:
        await agent.arun()
    except ValueError as e:
        print(f"配置错误: {e}")
    except Exception as e:
        print(f"运行时错误: {e}")
```

## 📈 最佳实践

### 1. 渐进式学习
```python
# 小批次开始
agent.learn(batch_size=10, learning_iterations=1)

# 验证后扩大规模
agent.learn(batch_size=100, learning_iterations=5)
```

### 2. 运行时选择
```python
# 开发阶段
agent = Agent(..., default_runtime='local')

# 生产阶段
agent = Agent(..., default_runtime='accurate')
```

### 3. 错误恢复
```python
# 保存状态
environment.save()

# 恢复状态
environment.restore()
```

## 🎛️ 环境集成

### 自定义环境
```python
from adala.environments.base import Environment

class MyEnvironment(Environment):
    def get_data_batch(self, batch_size):
        return self.fetch_from_api(batch_size)
    
    def get_feedback(self, skills, predictions):
        return self.validate_predictions(predictions)

# 使用自定义环境
agent = Agent(skills=..., environment=MyEnvironment())
```

## 🔧 故障排除

### 检查清单
- [ ] 运行时是否正确配置
- [ ] 环境是否已初始化
- [ ] 技能是否已定义
- [ ] 数据格式是否正确
- [ ] 权限是否足够

### 调试命令
```python
# 查看智能体状态
print(agent)  # 使用 __rich__ 格式化输出

# 检查技能状态
for name, skill in agent.skills.skills.items():
    print(f"{name}: {skill.instructions[:50]}...")

# 验证运行时
print(agent.runtimes.keys())
print(agent.teacher_runtimes.keys())
```

## 📚 相关资源

- [完整技术文档](./agent_architecture.md)
- [可视化图表](./agent_visualization.html)
- [深度技术分析](./agent_technical_analysis.md)