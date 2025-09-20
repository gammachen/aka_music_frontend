"""
PartialPromptTemplate与自定义提示词模板高级实现
包含PartialPromptTemplate、自定义模板引擎、动态模板生成器等高级特性
"""

import re
import json
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache, partial
from abc import ABC, abstractmethod
import jinja2

from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    FewShotPromptTemplate,
    PipelinePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import BaseMessage, SystemMessage, HumanMessage, AIMessage


@dataclass
class PartialVariable:
    """部分变量定义"""
    name: str
    value: Any
    is_required: bool = True
    validator: Optional[Callable] = None
    description: str = ""


class PartialPromptTemplate:
    """
    PartialPromptTemplate实现
    支持部分变量预填充，延迟绑定剩余变量
    """
    
    def __init__(
        self,
        template: str,
        input_variables: List[str],
        partial_variables: Dict[str, Any] = None,
        validate_template: bool = True
    ):
        self.template = template
        self.input_variables = input_variables
        self.partial_variables = partial_variables or {}
        self.validate_template = validate_template
        
        if validate_template:
            self._validate()
    
    def _validate(self):
        """验证模板"""
        template_vars = set(re.findall(r'\{([^}]+)\}', self.template))
        defined_vars = set(self.input_variables)
        
        if template_vars != defined_vars:
            raise ValueError(f"变量不匹配: 模板={template_vars}, 定义={defined_vars}")
    
    def partial(self, **kwargs) -> 'PartialPromptTemplate':
        """创建新的部分模板"""
        new_partial = self.partial_variables.copy()
        new_partial.update(kwargs)
        
        # 更新剩余变量
        remaining_vars = [
            var for var in self.input_variables
            if var not in new_partial
        ]
        
        return PartialPromptTemplate(
            template=self.template,
            input_variables=remaining_vars,
            partial_variables=new_partial,
            validate_template=self.validate_template
        )
    
    def format(self, **kwargs) -> str:
        """格式化完整模板"""
        all_vars = self.partial_variables.copy()
        all_vars.update(kwargs)
        
        missing_vars = set(self.input_variables) - set(all_vars.keys())
        if missing_vars:
            raise ValueError(f"缺少变量: {missing_vars}")
        
        return self.template.format(**all_vars)
    
    def format_partial(self, **kwargs) -> Tuple[str, List[str]]:
        """部分格式化，返回格式化文本和剩余变量"""
        formatted = self.template
        remaining_vars = []
        
        all_vars = self.partial_variables.copy()
        all_vars.update(kwargs)
        
        for var_name in self.input_variables:
            if var_name in all_vars:
                formatted = formatted.replace(f"{{{var_name}}}", str(all_vars[var_name]))
            else:
                remaining_vars.append(var_name)
        
        return formatted, remaining_vars
    
    def get_remaining_variables(self) -> List[str]:
        """获取剩余未填充的变量"""
        return [
            var for var in self.input_variables
            if var not in self.partial_variables
        ]
    
    def is_complete(self) -> bool:
        """检查是否所有变量都已填充"""
        return len(self.get_remaining_variables()) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "template": self.template,
            "input_variables": self.input_variables,
            "partial_variables": self.partial_variables,
            "validate_template": self.validate_template
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PartialPromptTemplate':
        """从字典创建"""
        return cls(**data)


class DynamicTemplateEngine:
    """动态模板引擎"""
    
    def __init__(self):
        self.env = jinja2.Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )
        self.custom_filters = {}
        self.custom_globals = {}
        self._setup_defaults()
    
    def _setup_defaults(self):
        """设置默认过滤器和全局变量"""
        self.add_filter('upper', lambda x: str(x).upper())
        self.add_filter('lower', lambda x: str(x).lower())
        self.add_filter('title', lambda x: str(x).title())
        self.add_filter('truncate', lambda x, length=50: str(x)[:length] + '...' if len(str(x)) > length else str(x))
        self.add_filter('json', lambda x: json.dumps(x, ensure_ascii=False))
    
    def add_filter(self, name: str, func: Callable):
        """添加自定义过滤器"""
        self.custom_filters[name] = func
        self.env.filters[name] = func
    
    def add_global(self, name: str, value: Any):
        """添加全局变量"""
        self.custom_globals[name] = value
        self.env.globals[name] = value
    
    def render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """渲染Jinja2模板"""
        template = self.env.from_string(template_str)
        return template.render(**context)
    
    def create_conditional_template(self, base_template: str, conditions: Dict[str, str]) -> str:
        """创建条件模板"""
        conditional_parts = []
        
        for condition, template_part in conditions.items():
            conditional_parts.append(f"{{% if {condition} %}}{template_part}{{% endif %}}")
        
        return base_template + "\n".join(conditional_parts)


class CustomPromptTemplate(ABC):
    """自定义提示词模板基类"""
    
    @abstractmethod
    def format(self, **kwargs) -> str:
        """格式化模板"""
        pass
    
    @abstractmethod
    def get_input_variables(self) -> List[str]:
        """获取输入变量"""
        pass


class FunctionCallTemplate(CustomPromptTemplate):
    """函数调用模板"""
    
    def __init__(self, function_name: str, parameters: Dict[str, str], description: str = ""):
        self.function_name = function_name
        self.parameters = parameters
        self.description = description
    
    def format(self, **kwargs) -> str:
        """格式化为函数调用格式"""
        params = {}
        for param_name, param_desc in self.parameters.items():
            if param_name in kwargs:
                params[param_name] = kwargs[param_name]
            else:
                raise ValueError(f"缺少参数: {param_name}")
        
        return f"调用函数 {self.function_name} 参数: {json.dumps(params, ensure_ascii=False)}"
    
    def get_input_variables(self) -> List[str]:
        return list(self.parameters.keys())


class ChainOfThoughtTemplate(CustomPromptTemplate):
    """思维链模板"""
    
    def __init__(self, problem_statement: str, steps: List[str]):
        self.problem_statement = problem_statement
        self.steps = steps
    
    def format(self, **kwargs) -> str:
        """格式化为思维链"""
        formatted_steps = []
        for i, step in enumerate(self.steps, 1):
            formatted_step = step.format(**kwargs)
            formatted_steps.append(f"{i}. {formatted_step}")
        
        return f"""问题：{self.problem_statement.format(**kwargs)}

让我们一步一步思考：
{chr(10).join(formatted_steps)}

最终答案："""
    
    def get_input_variables(self) -> List[str]:
        variables = re.findall(r'\{([^}]+)\}', self.problem_statement)
        for step in self.steps:
            variables.extend(re.findall(r'\{([^}]+)\}', step))
        return list(set(variables))


class MultiLanguageTemplate(CustomPromptTemplate):
    """多语言模板"""
    
    def __init__(self, templates: Dict[str, str], default_language: str = "zh"):
        self.templates = templates
        self.default_language = default_language
    
    def format(self, language: str = None, **kwargs) -> str:
        """根据语言格式化模板"""
        lang = language or self.default_language
        
        if lang not in self.templates:
            lang = self.default_language
        
        template = self.templates[lang]
        return template.format(**kwargs)
    
    def get_input_variables(self) -> List[str]:
        all_vars = []
        for template in self.templates.values():
            all_vars.extend(re.findall(r'\{([^}]+)\}', template))
        return list(set(all_vars))
    
    def add_language(self, language: str, template: str):
        """添加新语言模板"""
        self.templates[language] = template
    
    def remove_language(self, language: str):
        """移除语言模板"""
        if language in self.templates and language != self.default_language:
            del self.templates[language]


class AdaptiveTemplate(CustomPromptTemplate):
    """自适应模板"""
    
    def __init__(self, base_template: str, adaptations: Dict[str, Callable]):
        self.base_template = base_template
        self.adaptations = adaptations
    
    def format(self, **kwargs) -> str:
        """根据上下文自适应格式化"""
        context = kwargs.copy()
        
        # 应用适应性调整
        for var_name, adapter_func in self.adaptations.items():
            if var_name in context:
                context[var_name] = adapter_func(context[var_name], context)
        
        return self.base_template.format(**context)
    
    def get_input_variables(self) -> List[str]:
        return list(set(re.findall(r'\{([^}]+)\}', self.base_template)))


class TemplateComposer:
    """模板组合器"""
    
    def __init__(self):
        self.templates = {}
        self.composition_rules = {}
    
    def register_template(self, name: str, template: CustomPromptTemplate):
        """注册模板"""
        self.templates[name] = template
    
    def compose(self, template_names: List[str], separator: str = "\n\n") -> CustomPromptTemplate:
        """组合多个模板"""
        
        class ComposedTemplate(CustomPromptTemplate):
            def __init__(self, templates: List[CustomPromptTemplate], separator: str):
                self.templates = templates
                self.separator = separator
            
            def format(self, **kwargs) -> str:
                results = []
                for template in self.templates:
                    try:
                        result = template.format(**kwargs)
                        results.append(result)
                    except Exception as e:
                        results.append(f"[模板执行错误: {str(e)}]")
                return self.separator.join(results)
            
            def get_input_variables(self) -> List[str]:
                all_vars = []
                for template in self.templates:
                    all_vars.extend(template.get_input_variables())
                return list(set(all_vars))
        
        selected_templates = [self.templates[name] for name in template_names if name in self.templates]
        return ComposedTemplate(selected_templates, separator)


class TemplateRegistry:
    """模板注册中心"""
    
    def __init__(self):
        self.registry = {}
        self.metadata = {}
        self.usage_stats = {}
    
    def register(self, name: str, template: Union[PartialPromptTemplate, CustomPromptTemplate], 
                 category: str = "general", tags: List[str] = None):
        """注册模板"""
        self.registry[name] = template
        self.metadata[name] = {
            "category": category,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "type": type(template).__name__
        }
        self.usage_stats[name] = {"usage_count": 0, "last_used": None}
    
    def get(self, name: str) -> Optional[Union[PartialPromptTemplate, CustomPromptTemplate]]:
        """获取模板"""
        return self.registry.get(name)
    
    def list_templates(self, category: str = None) -> List[str]:
        """列出模板"""
        if category:
            return [name for name, meta in self.metadata.items() if meta["category"] == category]
        return list(self.registry.keys())
    
    def search(self, query: str) -> List[str]:
        """搜索模板"""
        results = []
        query_lower = query.lower()
        
        for name, meta in self.metadata.items():
            if (query_lower in name.lower() or 
                any(query_lower in tag.lower() for tag in meta["tags"]) or
                query_lower in meta["category"].lower()):
                results.append(name)
        
        return results
    
    def format_template(self, name: str, **kwargs) -> str:
        """格式化模板"""
        if name not in self.registry:
            raise ValueError(f"模板不存在: {name}")
        
        template = self.registry[name]
        result = template.format(**kwargs)
        
        # 更新使用统计
        self.usage_stats[name]["usage_count"] += 1
        self.usage_stats[name]["last_used"] = datetime.now().isoformat()
        
        return result
    
    def export_registry(self, filename: str):
        """导出注册表"""
        export_data = {
            "registry": {
                name: {
                    "template": template.to_dict() if hasattr(template, 'to_dict') else str(template),
                    "metadata": self.metadata[name],
                    "usage_stats": self.usage_stats[name]
                }
                for name, template in self.registry.items()
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)


# 使用示例和演示
class TemplateDemo:
    """模板演示类"""
    
    @staticmethod
    def demo_partial_template():
        """演示PartialPromptTemplate"""
        print("=== PartialPromptTemplate 演示 ===")
        
        # 创建基础模板
        base_template = PartialPromptTemplate(
            template="你好 {name}，欢迎来到 {place}！今天是 {day}。",
            input_variables=["name", "place", "day"]
        )
        
        # 创建部分模板
        partial_template = base_template.partial(place="LangChain世界", day="美好的一天")
        
        print("剩余变量:", partial_template.get_remaining_variables())
        print("是否完整:", partial_template.is_complete())
        
        # 格式化
        result = partial_template.format(name="小明")
        print("格式化结果:", result)
        
        # 部分格式化
        formatted, remaining = partial_template.format_partial(name="小红")
        print("部分格式化:", formatted)
        print("剩余变量:", remaining)
    
    @staticmethod
    def demo_dynamic_template():
        """演示动态模板"""
        print("\n=== 动态模板引擎演示 ===")
        
        engine = DynamicTemplateEngine()
        
        # 添加自定义过滤器
        engine.add_filter('reverse', lambda x: str(x)[::-1])
        engine.add_filter('word_count', lambda x: len(str(x).split()))
        
        # 渲染模板
        template = """
        原始文本: {{ text }}
        反转文本: {{ text|reverse }}
        单词数量: {{ text|word_count }}
        大写: {{ text|upper }}
        截断: {{ text|truncate(20) }}
        """
        
        context = {"text": "Hello LangChain Prompt Templates"}
        result = engine.render_template(template, context)
        print(result)
    
    @staticmethod
    def demo_custom_templates():
        """演示自定义模板"""
        print("\n=== 自定义模板演示 ===")
        
        # 函数调用模板
        function_template = FunctionCallTemplate(
            function_name="calculate_discount",
            parameters={
                "original_price": "商品原价",
                "discount_rate": "折扣率",
                "member_level": "会员等级"
            }
        )
        
        result = function_template.format(
            original_price=100,
            discount_rate=0.8,
            member_level="VIP"
        )
        print("函数调用模板:", result)
        
        # 思维链模板
        cot_template = ChainOfThoughtTemplate(
            problem_statement="如何优化{system_name}的性能?",
            steps=[
                "首先分析{system_name}的当前性能瓶颈",
                "然后考虑使用{optimization_method}进行优化",
                "最后评估优化后的性能提升{expected_improvement}%"
            ]
        )
        
        cot_result = cot_template.format(
            system_name="LangChain应用",
            optimization_method="缓存优化",
            expected_improvement=50
        )
        print("思维链模板:", cot_result)
    
    @staticmethod
    def demo_multilingual_template():
        """演示多语言模板"""
        print("\n=== 多语言模板演示 ===")
        
        multilingual_template = MultiLanguageTemplate({
            "zh": "你好 {name}，欢迎来到我们的平台！",
            "en": "Hello {name}, welcome to our platform!",
            "ja": "こんにちは {name}さん、私たちのプラットフォームへようこそ！"
        })
        
        for lang in ["zh", "en", "ja"]:
            result = multilingual_template.format(language=lang, name="用户")
            print(f"{lang}: {result}")
    
    @staticmethod
    def demo_registry():
        """演示模板注册中心"""
        print("\n=== 模板注册中心演示 ===")
        
        registry = TemplateRegistry()
        
        # 注册各种模板
        registry.register(
            "greeting", 
            PartialPromptTemplate(
                template="你好 {name}，欢迎来到 {place}！",
                input_variables=["name", "place"]
            ),
            category="greeting",
            tags=["welcome", "personal"]
        )
        
        registry.register(
            "qa",
            FunctionCallTemplate(
                function_name="answer_question",
                parameters={"question": "用户问题", "context": "上下文信息"}
            ),
            category="qa",
            tags=["help", "support"]
        )
        
        # 搜索模板
        results = registry.search("greeting")
        print("搜索结果:", results)
        
        # 使用模板
        greeting_result = registry.format_template("greeting", name="小明", place="LangChain")
        print("使用结果:", greeting_result)


# 高级模板工厂
class AdvancedTemplateFactory:
    """高级模板工厂"""
    
    @staticmethod
    def create_rag_template_with_context() -> PartialPromptTemplate:
        """创建带上下文的RAG模板"""
        return PartialPromptTemplate(
            template="""基于以下上下文回答问题：

上下文信息：
{context}

问题：{question}

回答要求：
1. 仅基于提供的上下文
2. 如果信息不存在，明确说明
3. 引用相关段落
4. 保持回答简洁准确

答案：""",
            input_variables=["context", "question"]
        )
    
    @staticmethod
    def create_code_review_template() -> AdaptiveTemplate:
        """创建自适应代码审查模板"""
        
        def adapt_code_block(code: str, context: Dict) -> str:
            """适应代码块格式"""
            language = context.get("language", "text")
            return f"```{language}\n{code}\n```"
        
        def adapt_severity(severity: str, context: Dict) -> str:
            """适应严重性描述"""
            severity_map = {
                "low": "轻微",
                "medium": "中等",
                "high": "严重",
                "critical": "致命"
            }
            return severity_map.get(severity.lower(), "未知")
        
        return AdaptiveTemplate(
            base_template="""代码审查报告：

代码：{code_block}

语言：{language}
严重性：{severity_level}

审查结果：{review_result}
""",
            adaptations={
                "code_block": adapt_code_block,
                "severity_level": adapt_severity
            }
        )
    
    @staticmethod
    def create_conversation_template() -> ChainOfThoughtTemplate:
        """创建对话思维链模板"""
        return ChainOfThoughtTemplate(
            problem_statement="用户说：{user_message}",
            steps=[
                "理解用户的意图：{user_message}",
                "分析当前对话状态：{conversation_state}",
                "生成合适的回复：{response_style}",
                "确保回复符合{personality}的性格特点"
            ]
        )


if __name__ == "__main__":
    """运行演示"""
    
    # 运行所有演示
    TemplateDemo.demo_partial_template()
    TemplateDemo.demo_dynamic_template()
    TemplateDemo.demo_custom_templates()
    TemplateDemo.demo_multilingual_template()
    TemplateDemo.demo_registry()
    
    # 使用高级工厂
    print("\n=== 高级工厂演示 ===")
    
    # RAG模板
    rag_template = AdvancedTemplateFactory.create_rag_template_with_context()
    rag_partial = rag_template.partial(context="LangChain是一个强大的LLM应用框架")
    rag_result = rag_partial.format(question="LangChain的主要功能是什么？")
    print("RAG结果:", rag_result)
    
    # 代码审查模板
    review_template = AdvancedTemplateFactory.create_code_review_template()
    review_result = review_template.format(
        code="print('Hello World')",
        language="python",
        severity="high",
        review_result="代码缺少错误处理"
    )
    print("审查结果:", review_result)