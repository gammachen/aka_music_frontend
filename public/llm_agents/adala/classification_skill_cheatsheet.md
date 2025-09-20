# ClassificationSkill 快速参考卡片

## 🚀 快速开始

### 最简示例
```python
from adala.skills.collection.classification import ClassificationSkill

# 创建分类器
skill = ClassificationSkill(
    labels=["positive", "negative", "neutral"]
)

# 使用示例
result = skill.apply(input_df, runtime)
```

## 📋 配置速查

### 核心参数
| 参数 | 类型 | 必需 | 示例 | 说明 |
|---|---|---|---|---|
| `labels` | List[str] | 可选* | `["A", "B", "C"]` | 分类标签列表 |
| `field_schema` | Dict | 可选* | 见下方 | JSON Schema配置 |
| `name` | str | 可选 | `"my_classifier"` | 技能名称 |
| `instructions` | str | 可选 | `"Classify text"` | 任务指令 |

*注：`labels` 和 `field_schema` 至少提供一个

### 模板配置
```python
skill = ClassificationSkill(
    labels=["spam", "ham"],
    input_template="Email: {text}",
    output_template="Classification: {predictions}",
    instructions="Classify emails as spam or legitimate"
)
```

## 🔧 常用模式

### 1. 情感分析
```python
sentiment = ClassificationSkill(
    name="sentiment",
    labels=["positive", "negative", "neutral"],
    instructions="Analyze sentiment of customer reviews"
)
```

### 2. 主题分类
```python
topics = ClassificationSkill(
    name="topics",
    labels=["tech", "sports", "politics", "entertainment"],
    instructions="Classify news articles by topic"
)
```

### 3. 垃圾邮件检测
```python
spam_detector = ClassificationSkill(
    field_schema={
        "predictions": {
            "type": "string",
            "enum": ["spam", "ham"],
            "description": "Email classification"
        }
    }
)
```

## ⚡ 高级用法

### 自定义Schema
```python
custom_schema = {
    "predictions": {
        "type": "string",
        "enum": ["urgent", "high", "medium", "low"],
        "description": "Priority level"
    },
    "confidence": {
        "type": "number",
        "minimum": 0,
        "maximum": 1
    }
}

skill = ClassificationSkill(field_schema=custom_schema)
```

### 异步处理
```python
import asyncio

async def classify_async():
    result = await skill.aapply(input_df, async_runtime)
    return result

# 运行
result = asyncio.run(classify_async())
```

## 🐛 调试技巧

### 启用详细日志
```python
skill = ClassificationSkill(
    labels=["A", "B"],
    verbose=True  # 显示详细输出
)
```

### 检查配置
```python
# 查看输入字段
print(skill.get_input_fields())

# 查看输出字段
print(skill.get_output_fields())

# 查看响应模型
print(skill.response_model)
```

## 📊 性能优化

### 批处理大小
```python
# 推荐设置
BATCH_SIZE = 50  # OpenAI推荐
runtime = OpenAIChatRuntime(batch_size=BATCH_SIZE)
```

### 并发控制
```python
# 异步并发
async_runtime = AsyncRuntime(
    max_concurrent=10,  # 控制并发数
    rate_limit=20       # 速率限制
)
```

## 🚨 常见错误

### 错误1: 配置缺失
```python
# ❌ 错误
skill = ClassificationSkill()

# ✅ 正确
skill = ClassificationSkill(labels=["A", "B"])
```

### 错误2: 模板变量不匹配
```python
# ❌ 错误
skill = ClassificationSkill(
    input_template="Text: {content}",  # 变量名不匹配
    labels=["A", "B"]
)

# ✅ 正确
skill = ClassificationSkill(
    input_template="Text: {input}",  # 使用{input}
    labels=["A", "B"]
)
```

### 错误3: 异步调用同步方法
```python
# ❌ 错误
result = skill.apply(input_df, async_runtime)

# ✅ 正确
result = await skill.aapply(input_df, async_runtime)
```

## 📈 监控指标

### 基础指标
```python
# 准确率计算
def calculate_accuracy(predictions, ground_truth):
    return (predictions == ground_truth).mean()

# 延迟监控
import time
start = time.time()
result = skill.apply(input_df, runtime)
latency = time.time() - start
```

### 成本估算
```python
# OpenAI token计数
def estimate_cost(texts, labels):
    # 每个标签约10 tokens
    # 每个输入文本tokens + 输出tokens
    return len(texts) * (avg_tokens + len(labels) * 10)
```

## 🔄 学习改进

### 基础改进
```python
# 收集反馈
feedback_df = InternalDataFrame({
    'predictions': ['A', 'B', 'A'],
    'predictions__fb': [None, 'Should be C', None]  # 用户反馈
})

# 改进技能
skill.improve(
    predictions=result_df,
    train_skill_output='predictions',
    feedback=feedback_df,
    runtime=runtime
)
```

### 异步改进
```python
# 高级异步改进
response = await skill.aimprove(
    teacher_runtime=runtime,
    target_input_variables=['input'],
    predictions=result_df
)
```

## 🎯 最佳实践

### 标签设计原则
1. **互斥性**: 每个样本只能属于一个类别
2. **完备性**: 覆盖所有可能情况
3. **清晰性**: 标签名称明确无歧义
4. **平衡性**: 各类别样本数量相对均衡

### 指令优化
```python
# 好的指令示例
instructions="""
Classify the sentiment of customer reviews into:
- positive: clearly positive sentiment
- negative: clearly negative sentiment  
- neutral: mixed or no clear sentiment

Examples:
"I love this product!" -> positive
"Terrible experience" -> negative
"It's okay" -> neutral
"""
```

## 🔍 故障排查

### 问题诊断清单
- [ ] 检查labels或field_schema是否正确配置
- [ ] 验证input_template变量是否匹配
- [ ] 确认runtime配置(API key, model等)
- [ ] 检查网络连接和API配额
- [ ] 查看详细日志输出

### 调试命令
```python
# 测试连接
runtime.test_connection()

# 检查配额
runtime.check_quota()

# 验证配置
skill.validate_response_model(skill.response_model)
```

---

## 📚 相关资源

- [完整技术文档](./classification_skill_analysis.md)
- [交互式可视化](./classification_skill_visualization.html)
- [ADALA官方文档](../README.md)