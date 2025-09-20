# LangChain Prompt模板技术全栈实施方案

## 概述

在LangChain生态系统中，Prompt模板是连接用户意图与AI模型能力的核心桥梁。本文档将深入探讨LangChain中Prompt模板的设计理念、实现模式、高级特性和最佳实践。

## 1. Prompt模板核心架构

### 1.1 基础概念

LangChain中的Prompt模板是一个可参数化的文本模板系统，它允许开发者创建可复用、可组合的提示词结构。

#### 核心组件
- **PromptTemplate**: 基础字符串模板
- **ChatPromptTemplate**: 对话消息模板
- **FewShotPromptTemplate**: 少样本学习模板
- **PipelinePromptTemplate**: 管道组合模板

### 1.2 模板类型矩阵

| 模板类型 | 适用场景 | 特点 | 复杂度 |
|---------|---------|------|--------|
| PromptTemplate | 单轮问答 | 简单字符串替换 | ⭐ |
| ChatPromptTemplate | 多轮对话 | 消息角色管理 | ⭐⭐ |
| FewShotPromptTemplate | 上下文学习 | 示例驱动 | ⭐⭐⭐ |
| PipelinePromptTemplate | 复杂流程 | 模板组合 | ⭐⭐⭐⭐ |

## 2. Prompt模板设计模式

### 2.1 模板变量设计

```python
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional
import re

class AdvancedPromptTemplate:
    """高级Prompt模板类，支持复杂变量处理和验证"""
    
    def __init__(
        self,
        template: str,
        input_variables: list,
        validate_template: bool = True,
        custom_validators: Optional[Dict[str, callable]] = None
    ):
        self.template = template
        self.input_variables = input_variables
        self.validate_template = validate_template
        self.custom_validators = custom_validators or {}
        
        if validate_template:
            self._validate_template()
    
    def _validate_template(self):
        """验证模板格式和变量"""
        # 检查变量格式
        template_vars = set(re.findall(r'\{(\w+)\}', self.template))
        input_vars = set(self.input_variables)
        
        if template_vars != input_vars:
            raise ValueError(f"模板变量不匹配: 模板={template_vars}, 输入={input_vars}")
    
    def format(self, **kwargs) -> str:
        """格式化模板，支持自定义验证"""
        # 验证必需变量
        missing_vars = set(self.input_variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"缺少必需变量: {missing_vars}")
        
        # 自定义验证
        for var, validator in self.custom_validators.items():
            if var in kwargs:
                validator(kwargs[var])
        
        return self.template.format(**kwargs)
```

### 2.2 动态模板生成

```python
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage, AIMessage

class DynamicPromptBuilder:
    """动态Prompt构建器"""
    
    @staticmethod
    def build_qa_prompt(
        context: str = "",
        examples: list = None,
        include_history: bool = True
    ) -> ChatPromptTemplate:
        """构建问答Prompt"""
        
        messages = [
            SystemMessage(content="你是一个专业的AI助手，请根据提供的上下文回答问题。"),
        ]
        
        if examples:
            for ex in examples:
                messages.extend([
                    HumanMessage(content=ex["question"]),
                    AIMessage(content=ex["answer"])
                ])
        
        if context:
            messages.append(SystemMessage(content=f"上下文: {context}"))
        
        if include_history:
            messages.append(MessagesPlaceholder(variable_name="history"))
        
        messages.append(HumanMessage(content="{question}"))
        
        return ChatPromptTemplate.from_messages(messages)
    
    @staticmethod
    def build_chain_of_thought_prompt(
        problem: str,
        steps: list = None
    ) -> PromptTemplate:
        """构建思维链Prompt"""
        
        template_parts = [
            "请逐步分析以下问题：",
            "问题: {problem}",
            ""
        ]
        
        if steps:
            template_parts.append("请按照以下步骤思考：")
            for i, step in enumerate(steps, 1):
                template_parts.append(f"{i}. {step}")
        
        template_parts.extend([
            "",
            "请展示你的完整思考过程："
        ])
        
        template = "\n".join(template_parts)
        return PromptTemplate(
            template=template,
            input_variables=["problem"] + ([f"step_{i}" for i in range(len(steps))] if steps else [])
        )
```

## 3. 高级模板特性

### 3.1 条件模板渲染

```python
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional
import jinja2

class ConditionalPromptTemplate:
    """条件渲染Prompt模板"""
    
    def __init__(self, template_str: str):
        self.env = jinja2.Environment()
        self.template = self.env.from_string(template_str)
    
    def render(self, **kwargs) -> str:
        """基于条件渲染模板"""
        return self.template.render(**kwargs)

# 使用示例
conditional_template = ConditionalPromptTemplate("""
{% if use_examples %}
以下是一些示例：
{% for example in examples %}
问题: {{ example.question }}
答案: {{ example.answer }}
{% endfor %}
{% endif %}

{% if context %}
上下文信息：
{{ context }}
{% endif %}

用户问题：{{ question }}
""")
```

### 3.2 模板继承与组合

```python
from langchain.prompts import PipelinePromptTemplate, PromptTemplate
from typing import List, Dict

class TemplateComposer:
    """模板组合器"""
    
    @staticmethod
    def create_document_qa_pipeline() -> PipelinePromptTemplate:
        """创建文档问答管道模板"""
        
        # 子模板定义
        context_template = """文档内容：
{document_content}

相关段落：
{relevant_sections}"""
        
        instruction_template = """基于提供的文档内容，请回答以下问题。
如果信息在文档中找不到，请明确说明。

问题：{question}"""
        
        format_template = """请按照以下格式回答：
答案：[你的答案]
置信度：[高/中/低]
相关段落：[引用相关段落]"""
        
        # 创建子提示词
        context_prompt = PromptTemplate(
            template=context_template,
            input_variables=["document_content", "relevant_sections"]
        )
        
        instruction_prompt = PromptTemplate(
            template=instruction_template,
            input_variables=["question"]
        )
        
        format_prompt = PromptTemplate(
            template=format_template,
            input_variables=[]
        )
        
        # 组合模板
        full_template = """{context}

{instruction}

{format}"""
        
        return PipelinePromptTemplate(
            final_prompt=PromptTemplate(
                template=full_template,
                input_variables=["context", "instruction", "format"]
            ),
            pipeline_prompts=[
                ("context", context_prompt),
                ("instruction", instruction_prompt),
                ("format", format_prompt)
            ]
        )
```

## 4. Prompt模板验证与测试

### 4.1 模板验证框架

```python
from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class PromptValidator:
    """Prompt模板验证器"""
    
    def __init__(self):
        self.rules = {
            'max_length': 4000,
            'forbidden_words': ['机密', '密码', '密钥'],
            'required_patterns': [
                r'\{[^}]+\}'  # 必须有模板变量
            ]
        }
    
    def validate(self, template: str, variables: Dict[str, Any]) -> ValidationResult:
        """验证模板和变量"""
        errors = []
        warnings = []
        
        # 长度检查
        if len(template) > self.rules['max_length']:
            errors.append(f"模板过长: {len(template)} > {self.rules['max_length']}")
        
        # 敏感词检查
        for word in self.rules['forbidden_words']:
            if word in template.lower():
                warnings.append(f"发现敏感词: {word}")
        
        # 变量检查
        template_vars = set(re.findall(r'\{([^}]+)\}', template))
        provided_vars = set(variables.keys())
        
        missing_vars = template_vars - provided_vars
        extra_vars = provided_vars - template_vars
        
        if missing_vars:
            errors.append(f"缺少变量: {missing_vars}")
        
        if extra_vars:
            warnings.append(f"多余变量: {extra_vars}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

### 4.2 模板测试套件

```python
import unittest
from typing import Dict, Any
from langchain.prompts import PromptTemplate

class PromptTemplateTestSuite:
    """Prompt模板测试套件"""
    
    def __init__(self):
        self.test_cases = []
    
    def add_test_case(
        self,
        name: str,
        template: str,
        variables: Dict[str, Any],
        expected_output: str,
        description: str = ""
    ):
        """添加测试用例"""
        self.test_cases.append({
            'name': name,
            'template': template,
            'variables': variables,
            'expected_output': expected_output,
            'description': description
        })
    
    def run_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        results = {}
        
        for case in self.test_cases:
            try:
                prompt = PromptTemplate(
                    template=case['template'],
                    input_variables=list(case['variables'].keys())
                )
                
                actual_output = prompt.format(**case['variables'])
                results[case['name']] = actual_output == case['expected_output']
                
            except Exception as e:
                results[case['name']] = False
                print(f"测试 {case['name']} 失败: {str(e)}")
        
        return results
```

## 5. Prompt模板优化策略

### 5.1 性能优化

```python
import time
from functools import lru_cache
from typing import Dict, Any
from langchain.prompts import PromptTemplate

class OptimizedPromptTemplate:
    """性能优化的Prompt模板"""
    
    def __init__(self, template: str, input_variables: list):
        self.template = template
        self.input_variables = input_variables
        self.prompt = PromptTemplate(
            template=template,
            input_variables=input_variables
        )
    
    @lru_cache(maxsize=1000)
    def format_cached(self, **kwargs) -> str:
        """带缓存的格式化"""
        return self.prompt.format(**kwargs)
    
    def format_batch(self, batch_inputs: List[Dict[str, Any]]) -> List[str]:
        """批量格式化"""
        return [self.format_cached(**inputs) for inputs in batch_inputs]
    
    def profile_format(self, **kwargs) -> Dict[str, float]:
        """性能分析"""
        start_time = time.time()
        result = self.format(**kwargs)
        end_time = time.time()
        
        return {
            'result': result,
            'format_time': end_time - start_time,
            'template_size': len(self.template)
        }
```

### 5.2 A/B测试框架

```python
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ABTestResult:
    """A/B测试结果"""
    template_a: str
    template_b: str
    a_score: float
    b_score: float
    winner: str
    timestamp: datetime

class PromptABTester:
    """Prompt A/B测试器"""
    
    def __init__(self):
        self.results = []
    
    def run_test(
        self,
        template_a: str,
        template_b: str,
        test_data: List[Dict[str, Any]],
        evaluator_func
    ) -> ABTestResult:
        """运行A/B测试"""
        
        scores = {'a': 0, 'b': 0}
        
        for data in test_data:
            # 随机分配模板
            use_a = random.choice([True, False])
            
            if use_a:
                prompt = PromptTemplate(template=template_a, input_variables=list(data.keys()))
                score = evaluator_func(prompt.format(**data))
                scores['a'] += score
            else:
                prompt = PromptTemplate(template=template_b, input_variables=list(data.keys()))
                score = evaluator_func(prompt.format(**data))
                scores['b'] += score
        
        # 计算平均分
        avg_a = scores['a'] / len(test_data)
        avg_b = scores['b'] / len(test_data)
        
        winner = 'a' if avg_a > avg_b else 'b'
        
        result = ABTestResult(
            template_a=template_a,
            template_b=template_b,
            a_score=avg_a,
            b_score=avg_b,
            winner=winner,
            timestamp=datetime.now()
        )
        
        self.results.append(result)
        return result
```

## 6. LangChain集成示例

### 6.1 与LLM链集成

```python
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate

class LangChainPromptIntegration:
    """LangChain Prompt集成示例"""
    
    @staticmethod
    def create_qa_chain():
        """创建问答链"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""你是一个专业的问答助手。
            请基于提供的上下文回答问题，如果信息不足请明确说明。
            
            回答格式：
            答案：[你的答案]
            置信度：[高/中/低]
            依据：[引用的相关段落]"""),
            HumanMessage(content="""上下文：
            {context}
            
            问题：{question}""")
        ])
        
        llm = ChatOpenAI(temperature=0.7)
        
        return LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True
        )
    
    @staticmethod
    def create_summarization_chain():
        """创建摘要链"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""你是一个专业的文本摘要专家。
            请根据要求对文本进行摘要，保持关键信息完整。
            
            摘要要求：
            - 长度：{summary_length}
            - 风格：{summary_style}
            - 重点：{focus_areas}"""),
            HumanMessage(content="""需要摘要的文本：
            {text}""")
        ])
        
        llm = ChatOpenAI(temperature=0.3)
        
        return LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True
        )
```

### 6.2 与RAG系统集成

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

class RAGPromptTemplate:
    """RAG系统Prompt模板"""
    
    @staticmethod
    def create_rag_qa_prompt():
        """创建RAG问答Prompt"""
        
        template = """使用以下上下文片段来回答最后的问题。
        如果你不知道答案，就说你不知道，不要试图编造答案。
        
        上下文：
        {context}
        
        问题：{question}
        
        有用的答案："""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    @staticmethod
    def create_rag_chain(vectorstore):
        """创建RAG链"""
        
        prompt = RAGPromptTemplate.create_rag_qa_prompt()
        
        return RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
```

## 7. 最佳实践与建议

### 7.1 模板设计原则

1. **清晰性**：模板变量命名要直观
2. **可维护性**：使用模板继承和组合
3. **性能**：使用缓存和批量处理
4. **安全性**：验证输入和输出
5. **可测试性**：设计可测试的模板

### 7.2 常见陷阱

- 避免过度复杂的模板嵌套
- 注意模板变量的命名冲突
- 处理好敏感信息的脱敏
- 考虑多语言支持的需求

### 7.3 监控与维护

```python
class PromptTemplateMonitor:
    """Prompt模板监控器"""
    
    def __init__(self):
        self.usage_stats = {}
        self.error_logs = []
    
    def track_usage(self, template_name: str, usage_data: Dict):
        """追踪模板使用情况"""
        if template_name not in self.usage_stats:
            self.usage_stats[template_name] = {
                'usage_count': 0,
                'avg_response_time': 0,
                'error_count': 0
            }
        
        stats = self.usage_stats[template_name]
        stats['usage_count'] += 1
        stats['avg_response_time'] = (
            (stats['avg_response_time'] * (stats['usage_count'] - 1) + usage_data.get('response_time', 0))
            / stats['usage_count']
        )
        
        if usage_data.get('error'):
            stats['error_count'] += 1
            self.error_logs.append({
                'template': template_name,
                'error': usage_data['error'],
                'timestamp': datetime.now()
            })
```

## 总结

LangChain的Prompt模板系统提供了强大而灵活的提示词管理能力。通过合理的设计模式、验证机制和优化策略，可以构建出高效、可维护的AI应用。关键在于理解业务需求，选择合适的模板类型，并建立完善的测试和监控体系。

---

*本文档基于LangChain 0.1.x版本编写，后续版本可能会有API变化，请以官方文档为准。*