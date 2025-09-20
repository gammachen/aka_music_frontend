"""
LangChain Prompt模板高级实现库
包含各种Prompt模板的设计模式、验证机制和高级特性
"""

import re
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import lru_cache, wraps
import hashlib
from enum import Enum

from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    FewShotPromptTemplate,
    PipelinePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    BaseMessage
)


class PromptType(Enum):
    """Prompt模板类型枚举"""
    SIMPLE = "simple"
    CHAT = "chat"
    FEW_SHOT = "few_shot"
    PIPELINE = "pipeline"
    CONDITIONAL = "conditional"
    DYNAMIC = "dynamic"


@dataclass
class TemplateVariable:
    """模板变量定义"""
    name: str
    type: str
    required: bool = True
    default: Any = None
    description: str = ""
    validator: Optional[Callable] = None


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any] = None


class TemplateValidator:
    """高级模板验证器"""
    
    def __init__(self):
        self.rules = {
            'max_length': 8000,
            'forbidden_patterns': [
                r'password|secret|key|token',
                r'<script.*?>.*?</script>',
                r'javascript:',
                r'data:text/html'
            ],
            'required_patterns': [
                r'\{[^}]+\}'  # 必须有模板变量
            ]
        }
    
    def validate_template(self, template: str) -> ValidationResult:
        """验证模板格式"""
        errors = []
        warnings = []
        
        # 长度检查
        if len(template) > self.rules['max_length']:
            errors.append(f"模板长度超限: {len(template)} > {self.rules['max_length']}")
        
        # 敏感内容检查
        for pattern in self.rules['forbidden_patterns']:
            if re.search(pattern, template, re.IGNORECASE):
                warnings.append(f"发现潜在敏感内容: {pattern}")
        
        # 必需模式检查
        has_required = any(re.search(pattern, template) for pattern in self.rules['required_patterns'])
        if not has_required:
            warnings.append("模板中没有发现变量占位符")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={'template_length': len(template)}
        )
    
    def validate_variables(self, template: str, variables: Dict[str, Any]) -> ValidationResult:
        """验证变量匹配"""
        errors = []
        warnings = []
        
        # 提取模板变量
        template_vars = set(re.findall(r'\{([^}]+)\}', template))
        provided_vars = set(variables.keys())
        
        # 检查缺失变量
        missing_vars = template_vars - provided_vars
        if missing_vars:
            errors.append(f"缺少变量: {missing_vars}")
        
        # 检查多余变量
        extra_vars = provided_vars - template_vars
        if extra_vars:
            warnings.append(f"多余变量: {extra_vars}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={
                'template_vars': list(template_vars),
                'provided_vars': list(provided_vars)
            }
        )


class AdvancedPromptTemplate:
    """高级Prompt模板类"""
    
    def __init__(
        self,
        template: str,
        variables: List[TemplateVariable],
        template_type: PromptType = PromptType.SIMPLE,
        metadata: Dict[str, Any] = None
    ):
        self.template = template
        self.variables = {var.name: var for var in variables}
        self.template_type = template_type
        self.metadata = metadata or {}
        self.validator = TemplateValidator()
        
        # 生成唯一ID
        self.id = hashlib.md5(template.encode()).hexdigest()[:8]
        self.created_at = datetime.now()
        
        # 验证模板
        self._validate()
    
    def _validate(self):
        """验证模板和变量"""
        # 验证模板格式
        template_result = self.validator.validate_template(self.template)
        if not template_result.is_valid:
            raise ValueError(f"模板验证失败: {template_result.errors}")
        
        # 验证变量定义
        template_vars = set(re.findall(r'\{([^}]+)\}', self.template))
        defined_vars = set(self.variables.keys())
        
        if template_vars != defined_vars:
            raise ValueError(f"变量定义不匹配: 模板={template_vars}, 定义={defined_vars}")
    
    def format(self, **kwargs) -> str:
        """格式化模板"""
        # 验证变量
        validation = self.validator.validate_variables(self.template, kwargs)
        if not validation.is_valid:
            raise ValueError(f"变量验证失败: {validation.errors}")
        
        # 处理默认值
        processed_kwargs = {}
        for var_name, var_def in self.variables.items():
            if var_name in kwargs:
                value = kwargs[var_name]
            elif var_def.default is not None:
                value = var_def.default
            else:
                raise ValueError(f"缺少必需变量: {var_name}")
            
            # 验证变量值
            if var_def.validator and value is not None:
                if not var_def.validator(value):
                    raise ValueError(f"变量验证失败: {var_name}={value}")
            
            processed_kwargs[var_name] = value
        
        return self.template.format(**processed_kwargs)
    
    @lru_cache(maxsize=1000)
    def format_cached(self, **kwargs) -> str:
        """带缓存的格式化"""
        # 将kwargs转换为可哈希的元组
        kwargs_tuple = tuple(sorted(kwargs.items()))
        return self.format(**dict(kwargs_tuple))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'template': self.template,
            'variables': [asdict(var) for var in self.variables.values()],
            'template_type': self.template_type.value,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedPromptTemplate':
        """从字典创建"""
        variables = [
            TemplateVariable(**var_data)
            for var_data in data['variables']
        ]
        
        template = cls(
            template=data['template'],
            variables=variables,
            template_type=PromptType(data['template_type']),
            metadata=data.get('metadata', {})
        )
        
        template.id = data.get('id', template.id)
        template.created_at = datetime.fromisoformat(data.get('created_at', template.created_at.isoformat()))
        
        return template


class ChatPromptBuilder:
    """对话Prompt构建器"""
    
    @staticmethod
    def create_system_prompt(content: str, variables: List[TemplateVariable] = None) -> SystemMessage:
        """创建系统提示"""
        if variables:
            template = AdvancedPromptTemplate(content, variables)
            return SystemMessage(content=template.template)
        return SystemMessage(content=content)
    
    @staticmethod
    def create_conversation_template(
        system_message: str,
        include_history: bool = True,
        include_context: bool = True
    ) -> ChatPromptTemplate:
        """创建对话模板"""
        
        messages = [
            SystemMessage(content=system_message)
        ]
        
        if include_context:
            messages.append(SystemMessage(content="上下文：{context}"))
        
        if include_history:
            messages.append(MessagesPlaceholder(variable_name="history"))
        
        messages.append(HumanMessage(content="{question}"))
        
        return ChatPromptTemplate.from_messages(messages)
    
    @staticmethod
    def create_few_shot_template(
        examples: List[Dict[str, str]],
        system_message: str,
        example_template: str = "问题：{input}\n答案：{output}",
        suffix: str = "问题：{input}\n答案："
    ) -> FewShotPromptTemplate:
        """创建少样本学习模板"""
        
        example_prompt = PromptTemplate(
            template=example_template,
            input_variables=["input", "output"]
        )
        
        return FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix=system_message,
            suffix=suffix,
            input_variables=["input"]
        )


class ConditionalPromptRenderer:
    """条件渲染器"""
    
    def __init__(self):
        self.conditions = {}
    
    def add_condition(
        self,
        condition_name: str,
        condition_func: Callable[[Dict[str, Any]], bool],
        template: str
    ):
        """添加条件模板"""
        self.conditions[condition_name] = {
            'func': condition_func,
            'template': template
        }
    
    def render(self, base_template: str, variables: Dict[str, Any]) -> str:
        """基于条件渲染模板"""
        final_template = base_template
        
        for name, condition in self.conditions.items():
            if condition['func'](variables):
                final_template += "\n" + condition['template']
        
        return final_template.format(**variables)


class PromptTemplateManager:
    """Prompt模板管理器"""
    
    def __init__(self):
        self.templates: Dict[str, AdvancedPromptTemplate] = {}
        self.categories: Dict[str, List[str]] = {}
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
    
    def register_template(
        self,
        name: str,
        template: AdvancedPromptTemplate,
        category: str = "general"
    ):
        """注册模板"""
        self.templates[name] = template
        
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(name)
        
        self.usage_stats[name] = {
            'usage_count': 0,
            'last_used': None,
            'avg_format_time': 0
        }
    
    def get_template(self, name: str) -> Optional[AdvancedPromptTemplate]:
        """获取模板"""
        return self.templates.get(name)
    
    def list_templates(self, category: str = None) -> List[str]:
        """列出模板"""
        if category:
            return self.categories.get(category, [])
        return list(self.templates.keys())
    
    def format_template(self, name: str, **kwargs) -> str:
        """格式化模板并记录使用"""
        if name not in self.templates:
            raise ValueError(f"模板不存在: {name}")
        
        start_time = time.time()
        result = self.templates[name].format(**kwargs)
        format_time = time.time() - start_time
        
        # 更新统计
        stats = self.usage_stats[name]
        stats['usage_count'] += 1
        stats['last_used'] = datetime.now()
        stats['avg_format_time'] = (
            (stats['avg_format_time'] * (stats['usage_count'] - 1) + format_time)
            / stats['usage_count']
        )
        
        return result
    
    def export_templates(self, filename: str):
        """导出模板到文件"""
        export_data = {
            'templates': {
                name: template.to_dict()
                for name, template in self.templates.items()
            },
            'categories': self.categories,
            'export_time': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    def import_templates(self, filename: str):
        """从文件导入模板"""
        with open(filename, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        for name, template_data in import_data['templates'].items():
            template = AdvancedPromptTemplate.from_dict(template_data)
            self.register_template(name, template)
        
        self.categories.update(import_data.get('categories', {}))
    
    def get_usage_report(self) -> Dict[str, Any]:
        """获取使用报告"""
        total_usage = sum(stats['usage_count'] for stats in self.usage_stats.values())
        
        return {
            'total_templates': len(self.templates),
            'total_usage': total_usage,
            'categories': {cat: len(templates) for cat, templates in self.categories.items()},
            'most_used': max(
                self.usage_stats.items(),
                key=lambda x: x[1]['usage_count']
            ) if self.usage_stats else None,
            'stats': self.usage_stats
        }


# 预定义模板库
class PromptTemplateLibrary:
    """预定义模板库"""
    
    @staticmethod
    def get_qa_template() -> AdvancedPromptTemplate:
        """问答模板"""
        return AdvancedPromptTemplate(
            template="""基于以下上下文回答问题：

上下文：
{context}

问题：{question}

要求：
1. 如果信息在上下文中，请直接引用
2. 如果信息不在上下文中，请明确说明
3. 保持回答简洁准确

答案：""",
            variables=[
                TemplateVariable("context", "string", required=True, description="上下文信息"),
                TemplateVariable("question", "string", required=True, description="用户问题")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"purpose": "question_answering", "version": "1.0"}
        )
    
    @staticmethod
    def get_summarization_template() -> AdvancedPromptTemplate:
        """摘要模板"""
        return AdvancedPromptTemplate(
            template="""请对以下文本进行摘要：

原文：
{text}

摘要要求：
- 长度：{length}字以内
- 风格：{style}
- 重点：{focus}

摘要：""",
            variables=[
                TemplateVariable("text", "string", required=True, description="原文本"),
                TemplateVariable("length", "integer", default=100, description="摘要长度"),
                TemplateVariable("style", "string", default="简洁", description="摘要风格"),
                TemplateVariable("focus", "string", default="重点", description="关注重点")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"purpose": "summarization", "version": "1.0"}
        )
    
    @staticmethod
    def get_code_generation_template() -> AdvancedPromptTemplate:
        """代码生成模板"""
        return AdvancedPromptTemplate(
            template="""请根据以下需求生成代码：

需求描述：
{requirements}

技术要求：
- 编程语言：{language}
- 框架：{framework}
- 功能：{functionality}

请提供：
1. 完整代码实现
2. 使用示例
3. 注意事项

代码：""",
            variables=[
                TemplateVariable("requirements", "string", required=True, description="功能需求"),
                TemplateVariable("language", "string", required=True, description="编程语言"),
                TemplateVariable("framework", "string", default="标准库", description="技术框架"),
                TemplateVariable("functionality", "string", required=True, description="具体功能")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"purpose": "code_generation", "version": "1.0"}
        )


# 使用示例和测试
if __name__ == "__main__":
    # 创建管理器
    manager = PromptTemplateManager()
    
    # 注册模板
    manager.register_template("qa", PromptTemplateLibrary.get_qa_template())
    manager.register_template("summarize", PromptTemplateLibrary.get_summarization_template())
    manager.register_template("code_gen", PromptTemplateLibrary.get_code_generation_template())
    
    # 使用模板
    result = manager.format_template(
        "qa",
        context="LangChain是一个用于构建LLM应用的框架",
        question="什么是LangChain？"
    )
    print("问答结果:", result)
    
    # 使用摘要模板
    summary = manager.format_template(
        "summarize",
        text="LangChain是一个强大的框架，用于构建基于大型语言模型的应用程序。它提供了丰富的工具和抽象，使得开发者能够更容易地创建复杂的AI应用。",
        length=50,
        style="简洁明了",
        focus="核心概念"
    )
    print("摘要结果:", summary)
    
    # 导出模板
    manager.export_templates("prompt_templates_export.json")
    
    # 使用报告
    report = manager.get_usage_report()
    print("使用报告:", json.dumps(report, ensure_ascii=False, indent=2))