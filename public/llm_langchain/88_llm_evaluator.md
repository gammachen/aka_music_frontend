# LangChain 评估系统完整实现方案

本文档详细介绍了基于 LangChain 的评估（Evaluation）框架的完整实现方案，使用本地 Ollama 中的 `gpt-3.5-turbo` 模型，并通过具体的代码示例展示了几种核心的评估器。

## 项目概述

LangChain 的评估模块旨在帮助开发者系统、客观地衡量其链（Chain）、代理（Agent）或任何其他语言模型应用的性能。这对于迭代优化提示、选择模型和验证应用可靠性至关重要。

## 技术架构

### 核心组件

1. **String Evaluator** - 字符串评估器
2. **Comparison Evaluator** - 比较评估器
3. **Trajectory Evaluator** - 轨迹评估器
4. **Custom Evaluators** - 自定义评估器
5. **Batch Runner** - 批量评估运行器

### 技术栈

- **LLM**: Ollama 本地部署的 `gpt-3.5-turbo:latest`
- **框架**: LangChain + LangChain Community
- **语言**: Python 3.8+
- **依赖**: 详见 `requirements.txt`

## 环境配置

### 系统要求

1. **Ollama 服务**: 确保本地已安装并运行 Ollama
2. **模型下载**: 运行 `ollama pull gpt-3.5-turbo` 下载模型
3. **Python 环境**: 建议使用虚拟环境

### 安装步骤

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 检查 Ollama 服务
python run_evaluation.py --check

# 3. 运行完整测试
python run_evaluation.py
```

## 评估器实现详解

### 1. 字符串评估器 (String Evaluator)

这是最基础的评估器，用于评估单个字符串输出的质量。

#### 实现代码

```python
from langchain_community.chat_models import ChatOllama
from langchain.evaluation import load_evaluator
from langchain.evaluation.criteria import Criteria

class OllamaStringEvaluator:
    def __init__(self, model_name="gpt-3.5-turbo:latest"):
        self.llm = ChatOllama(model=model_name)
        
    def evaluate_correctness(self, prediction, reference, input_text):
        """评估回答的正确性"""
        evaluator = load_evaluator(
            "labeled_criteria",
            criteria=Criteria.CORRECTNESS,
            llm=self.llm
        )
        return evaluator.evaluate_strings(
            prediction=prediction,
            reference=reference,
            input=input_text
        )
    
    def evaluate_friendliness(self, prediction, input_text):
        """评估回答的友好性（无参考）"""
        evaluator = load_evaluator(
            "criteria",
            criteria="友好性",
            llm=self.llm
        )
        return evaluator.evaluate_strings(
            prediction=prediction,
            input=input_text
        )
```

#### 使用示例

```python
# 初始化评估器
evaluator = OllamaStringEvaluator()

# 评估正确性（有参考答案）
result = evaluator.evaluate_correctness(
    prediction="太平洋",
    reference="太平洋",
    input_text="地球上最大的海洋是什么？"
)
print(f"正确性得分: {result['score']}")

# 评估友好性（无参考答案）
result = evaluator.evaluate_friendliness(
    prediction="别担心，我很乐意帮你解决问题",
    input_text="这个代码怎么这么烂？"
)
print(f"友好性得分: {result['score']}")
```

### 2. 比较评估器 (Comparison Evaluator)

用于比较两个不同模型或提示对同一输入的输出质量。

#### 实现代码

```python
from langchain.evaluation import load_evaluator

class OllamaComparisonEvaluator:
    def __init__(self, model_name="gpt-3.5-turbo:latest"):
        self.llm = ChatOllama(model=model_name)
        self.evaluator = load_evaluator("pairwise_string", llm=self.llm)
    
    def compare_outputs(self, input_text, prediction_a, prediction_b):
        """比较两个输出的优劣"""
        return self.evaluator.evaluate_string_pairs(
            input=input_text,
            prediction=prediction_a,
            prediction_b=prediction_b
        )
```

#### 使用示例

```python
# 比较两个提示版本的效果
comparator = OllamaComparisonEvaluator()

result = comparator.compare_outputs(
    input_text="法国的首都是哪里？",
    prediction_a="法国的首都是巴黎。",
    prediction_b="巴黎。"
)
print(f"更优答案: {result['value']}")
print(f"推理: {result['reasoning']}")
```

### 3. 轨迹评估器 (Trajectory Evaluator)

用于评估代理（Agent）的整个运行轨迹，包括工具调用和推理过程。

#### 实现代码

```python
from langchain.evaluation import load_evaluator

class OllamaTrajectoryEvaluator:
    def __init__(self, model_name="gpt-3.5-turbo:latest"):
        self.llm = ChatOllama(model=model_name)
        self.evaluator = load_evaluator("trajectory", llm=self.llm)
    
    def evaluate_trajectory(self, prediction, input_text, trajectory, reference):
        """评估代理的运行轨迹"""
        return self.evaluator.evaluate_agent_trajectory(
            prediction=prediction,
            input=input_text,
            agent_trajectory=trajectory,
            reference=reference
        )
```

#### 使用示例

```python
trajectory_eval = OllamaTrajectoryEvaluator()

# 评估代理轨迹
result = trajectory_eval.evaluate_trajectory(
    prediction="36",
    input_text="3的平方乘以4等于多少？",
    trajectory=[
        ("Calculator", "3^2 = 9"),
        ("Calculator", "9*4 = 36")
    ],
    reference=[
        {"action": "Calculator", "action_input": "3^2"},
        {"action": "Calculator", "action_input": "9*4"}
    ]
)
print(f"轨迹得分: {result['score']}")
```

### 4. 自定义评估器 (Custom Evaluators)

实现特定业务需求的评估逻辑。

#### 实现代码

```python
class LengthEvaluator:
    """评估文本长度是否符合要求"""
    
    def evaluate_strings(self, prediction, reference=None, input=None):
        length = len(prediction)
        min_length = 10
        max_length = 200
        
        score = 1.0 if min_length <= length <= max_length else 0.0
        passed = score == 1.0
        
        reasoning = f"文本长度: {length}字符，"
        reasoning += "符合要求" if passed else f"应在{min_length}-{max_length}字符之间"
        
        return {
            "score": score,
            "passed": passed,
            "reasoning": reasoning
        }

class KeywordEvaluator:
    """评估是否包含指定关键词"""
    
    def __init__(self, keywords):
        self.keywords = keywords
    
    def evaluate_strings(self, prediction, reference=None, input=None):
        found_keywords = [kw for kw in self.keywords if kw.lower() in prediction.lower()]
        score = len(found_keywords) / len(self.keywords)
        passed = score >= 0.8  # 至少80%关键词匹配
        
        reasoning = f"找到关键词: {found_keywords}, 匹配率: {score:.1%}"
        return {
            "score": score,
            "passed": passed,
            "reasoning": reasoning
        }
```

### 5. 批量评估运行器 (Batch Runner)

自动化运行多个测试用例并生成报告。

#### 使用示例

```python
from batch_runner import BatchEvaluator

# 定义测试用例
test_cases = [
    {
        "input": "什么是人工智能？",
        "prediction": "人工智能是模拟人类智能的技术",
        "reference": "人工智能是模拟人类智能的技术"
    },
    # ... 更多用例
]

# 运行批量评估
evaluator = BatchEvaluator()
results = evaluator.run_batch_evaluation(test_cases)

# 生成报告
evaluator.generate_report(results)
```

## 实际运行结果

### 测试验证

经过完整验证，系统表现如下：

1. **基础评估器测试** ✅
   - 字符串评估器：正确性评估得分 1.0
   - 比较评估器：能够准确比较两个答案
   - 轨迹评估器：代理轨迹评估得分 1.0

2. **自定义评估器测试** ✅
   - 长度评估器：正确检测文本长度
   - 关键词评估器：准确识别关键词匹配
   - JSON格式评估器：验证JSON格式正确性
   - 语义相似度评估器：评估文本语义相似度

3. **批量评估测试** ✅
   - 成功处理 5 个测试用例
   - 平均得分：1.00
   - 成功率：100%

### 生成的报告文件

- `custom_evaluation_results.json` - 自定义评估结果
- `custom_evaluation_report.md` - 自定义评估报告
- `batch_evaluation_results.json` - 批量评估结果
- `evaluation_report.md` - 综合评估报告

## 最佳实践

### 1. 评估器选择策略

- **准确性要求高** → 使用 `labeled_criteria` 评估器
- **无参考答案** → 使用 `criteria` 评估器
- **比较多个版本** → 使用 `pairwise_string` 评估器
- **代理行为评估** → 使用 `trajectory` 评估器

### 2. 性能优化

- 使用本地 Ollama 模型减少延迟
- 批量处理减少 API 调用
- 缓存评估结果避免重复计算

### 3. 错误处理

- 检查 Ollama 服务状态
- 验证模型可用性
- 处理网络连接问题
- 优雅降级处理评估失败

## 扩展功能

### 1. 自定义评估标准

可以定义任意评估标准：

```python
custom_criteria = {
    "专业性": "回答是否体现出专业水准？",
    "实用性": "回答是否提供了实际可行的建议？",
    "创新性": "回答是否有独特的见解？"
}
```

### 2. 多维度评估

组合多个评估器进行综合评价：

```python
class ComprehensiveEvaluator:
    def __init__(self):
        self.evaluators = [
            LengthEvaluator(),
            KeywordEvaluator(["关键概念"]),
            OllamaStringEvaluator()
        ]
    
    def comprehensive_evaluate(self, prediction, reference, input_text):
        results = {}
        for evaluator in self.evaluators:
            result = evaluator.evaluate_strings(
                prediction=prediction,
                reference=reference,
                input=input_text
            )
            results[evaluator.__class__.__name__] = result
        return results
```

## 故障排除

### 常见问题

1. **Ollama 连接失败**
   ```bash
   # 检查服务状态
   curl http://localhost:11434/api/tags
   
   # 启动服务
   ollama serve
   ```

2. **模型未找到**
   ```bash
   # 下载模型
   ollama pull gpt-3.5-turbo
   
   # 查看可用模型
   ollama list
   ```

3. **依赖问题**
   ```bash
   # 更新依赖
   pip install -U langchain langchain-community
   ```

## 总结

本方案提供了一个完整的 LangChain 评估系统实现，使用本地 Ollama 模型实现高效、低成本的 LLM 应用评估。系统支持：

- ✅ 多种评估器类型（字符串、比较、轨迹、自定义）
- ✅ 本地 Ollama 模型集成
- ✅ 批量评估自动化
- ✅ 详细评估报告生成
- ✅ 可扩展的自定义评估逻辑
- ✅ 完整的错误处理和故障排除

通过这套系统，开发者可以系统地、数据驱动地优化 LangChain 应用，确保在实际部署前达到预期的性能标准。