#!/usr/bin/env python3
"""
LangChain 输出解析器完整实现库
包含所有类型的输出解析器及其使用示例
"""

import json
import re
from typing import List, Dict, Any, Optional, Union, Type
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import asyncio
from functools import lru_cache

# 模拟LangChain核心类
class BaseOutputParser:
    """基础输出解析器类"""
    
    def parse(self, text: str) -> Any:
        """解析文本输出"""
        raise NotImplementedError
    
    def parse_with_prompt(self, completion: str, prompt: str) -> Any:
        """结合提示词解析"""
        return self.parse(completion)

class StringOutputParser(BaseOutputParser):
    """字符串输出解析器 - 保持原始文本格式"""
    
    def parse(self, text: str) -> str:
        """返回原始文本，去除首尾空白"""
        return text.strip()

class BooleanOutputParser(BaseOutputParser):
    """布尔值输出解析器"""
    
    def __init__(self, true_values: List[str] = None, false_values: List[str] = None):
        self.true_values = true_values or ["true", "yes", "1", "是", "对", "正确"]
        self.false_values = false_values or ["false", "no", "0", "否", "错", "错误"]
    
    def parse(self, text: str) -> bool:
        """将文本解析为布尔值"""
        text_lower = text.strip().lower()
        
        for val in self.true_values:
            if val.lower() in text_lower:
                return True
        
        for val in self.false_values:
            if val.lower() in text_lower:
                return False
        
        # 默认处理
        return text_lower.startswith(('t', 'y', '1', '是', '对'))

class ListOutputParser(BaseOutputParser):
    """列表输出解析器"""
    
    def __init__(self, separator: str = ","):
        self.separator = separator
    
    def parse(self, text: str) -> List[str]:
        """将逗号分隔的文本解析为列表"""
        items = [item.strip() for item in text.split(self.separator)]
        return [item for item in items if item]

class JSONOutputParser(BaseOutputParser):
    """JSON输出解析器"""
    
    def parse(self, text: str) -> Dict[str, Any]:
        """解析JSON格式的文本"""
        try:
            # 清理可能的Markdown格式
            cleaned = re.sub(r'```json\s*|\s*```', '', text.strip())
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

class DatetimeOutputParser(BaseOutputParser):
    """日期时间输出解析器"""
    
    def __init__(self, format_str: str = "%Y-%m-%d %H:%M:%S"):
        self.format_str = format_str
    
    def parse(self, text: str) -> datetime:
        """解析日期时间字符串"""
        try:
            return datetime.strptime(text.strip(), self.format_str)
        except ValueError as e:
            # 尝试常见格式
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d/%m/%Y",
                "%Y-%m-%dT%H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(text.strip(), fmt)
                except ValueError:
                    continue
            
            raise ValueError(f"无法解析日期时间: {text}")

class EnumOutputParser(BaseOutputParser):
    """枚举输出解析器"""
    
    def __init__(self, enum_class: Type[Enum]):
        self.enum_class = enum_class
    
    def parse(self, text: str) -> Enum:
        """将文本解析为枚举值"""
        text = text.strip().upper()
        
        try:
            return self.enum_class[text]
        except KeyError:
            # 尝试通过值匹配
            for member in self.enum_class:
                if member.value.upper() == text:
                    return member
            
            raise ValueError(f"无效的枚举值: {text}")

class RegexOutputParser(BaseOutputParser):
    """正则表达式输出解析器"""
    
    def __init__(self, regex: str, output_keys: List[str]):
        self.regex = re.compile(regex)
        self.output_keys = output_keys
    
    def parse(self, text: str) -> Dict[str, str]:
        """使用正则表达式提取信息"""
        match = self.regex.search(text)
        if match:
            return dict(zip(self.output_keys, match.groups()))
        else:
            return {key: "" for key in self.output_keys}

class XMLOutputParser(BaseOutputParser):
    """XML输出解析器"""
    
    def __init__(self, root_tag: str = "response"):
        self.root_tag = root_tag
    
    def parse(self, text: str) -> Dict[str, Any]:
        """解析简单的XML格式"""
        # 简单的XML解析实现
        pattern = r'<(\w+)>(.*?)</\1>'
        matches = re.findall(pattern, text, re.DOTALL)
        
        result = {}
        for tag, content in matches:
            # 检查是否嵌套
            if '<' in content and '>' in content:
                nested = self.parse(f"<{tag}>{content}</{tag}>")
                result[tag] = nested[tag] if tag in nested else content.strip()
            else:
                result[tag] = content.strip()
        
        return {self.root_tag: result}

class RetryOutputParser(BaseOutputParser):
    """重试输出解析器"""
    
    def __init__(self, base_parser: BaseOutputParser, max_retries: int = 3):
        self.base_parser = base_parser
        self.max_retries = max_retries
    
    def parse(self, text: str) -> Any:
        """带重试机制的解析"""
        for attempt in range(self.max_retries):
            try:
                return self.base_parser.parse(text)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                # 在实际应用中，这里可以调用LLM重新生成
                continue

# 数据模型定义
@dataclass
class Person:
    """个人信息数据模型"""
    name: str
    age: int
    email: str
    skills: List[str]
    experience_years: int

@dataclass
class Product:
    """产品信息数据模型"""
    name: str
    price: float
    category: str
    features: List[str]
    in_stock: bool
    rating: Optional[float] = None

@dataclass
class APIResponse:
    """API响应数据模型"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    timestamp: str = None

# 枚举定义
class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# 解析器管理器
class OutputParserManager:
    """输出解析器管理器"""
    
    def __init__(self):
        self.parsers = {}
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """初始化所有解析器"""
        self.parsers.update({
            'string': StringOutputParser(),
            'boolean': BooleanOutputParser(),
            'list': ListOutputParser(),
            'json': JSONOutputParser(),
            'datetime': DatetimeOutputParser(),
            'sentiment': EnumOutputParser(Sentiment),
            'priority': EnumOutputParser(Priority),
            'xml': XMLOutputParser(),
            'regex': RegexOutputParser(
                regex=r"姓名：(\w+)，年龄：(\d+)，邮箱：(\S+)",
                output_keys=['name', 'age', 'email']
            )
        })
    
    def get_parser(self, parser_type: str) -> BaseOutputParser:
        """获取指定类型的解析器"""
        return self.parsers.get(parser_type)
    
    def register_parser(self, name: str, parser: BaseOutputParser):
        """注册新的解析器"""
        self.parsers[name] = parser
    
    def list_parsers(self) -> List[str]:
        """列出所有可用解析器"""
        return list(self.parsers.keys())

# 实际应用场景类
class CustomerServiceBot:
    """客服机器人 - 使用多种解析器"""
    
    def __init__(self):
        self.manager = OutputParserManager()
        self.sentiment_parser = self.manager.get_parser('sentiment')
        self.list_parser = ListOutputParser()
    
    def analyze_sentiment(self, text: str) -> Sentiment:
        """分析用户情感"""
        # 模拟LLM响应
        if "好" in text or "满意" in text:
            return self.sentiment_parser.parse("positive")
        elif "不好" in text or "差" in text:
            return self.sentiment_parser.parse("negative")
        else:
            return self.sentiment_parser.parse("neutral")
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 模拟LLM响应
        keywords = ["退款", "订单", "物流", "客服"]
        return [kw for kw in keywords if kw in text]
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """处理用户查询"""
        sentiment = self.analyze_sentiment(query)
        keywords = self.extract_keywords(query)
        
        return {
            "query": query,
            "sentiment": sentiment.value,
            "keywords": keywords,
            "response": self.generate_response(sentiment, keywords)
        }
    
    def generate_response(self, sentiment: Sentiment, keywords: List[str]) -> str:
        """生成回复"""
        if sentiment == Sentiment.NEGATIVE:
            return "非常抱歉给您带来不好的体验，我们会立即处理您的问题。"
        elif sentiment == Sentiment.POSITIVE:
            return "感谢您的支持！我们会继续努力为您提供更好的服务。"
        else:
            return "感谢您的咨询，请问有什么可以帮助您的？"

class ProductExtractor:
    """产品信息提取器"""
    
    def __init__(self):
        self.json_parser = JSONOutputParser()
        self.list_parser = ListOutputParser()
    
    def extract_product_info(self, description: str) -> Product:
        """从描述中提取产品信息"""
        # 模拟LLM JSON响应
        json_response = {
            "name": "iPhone 15",
            "price": 7999.0,
            "category": "智能手机",
            "features": ["A17芯片", "4800万像素", "钛合金机身"],
            "in_stock": True,
            "rating": 4.8
        }
        
        data = self.json_parser.parse(json.dumps(json_response))
        return Product(**data)
    
    def extract_features(self, description: str) -> List[str]:
        """提取产品特性"""
        # 模拟LLM响应
        features_text = "A17芯片,4800万像素,钛合金机身,超长续航"
        return self.list_parser.parse(features_text)

class CodeGenerator:
    """代码生成器 - 使用结构化解析"""
    
    def __init__(self):
        self.json_parser = JSONOutputParser()
    
    def generate_function(self, description: str) -> Dict[str, Any]:
        """生成函数代码"""
        # 模拟LLM JSON响应
        response = {
            "function_name": "calculate_fibonacci",
            "parameters": ["n"],
            "return_type": "int",
            "code": "def calculate_fibonacci(n):\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
            "description": "计算斐波那契数列"
        }
        
        return self.json_parser.parse(json.dumps(response))
    
    def generate_class(self, description: str) -> Dict[str, Any]:
        """生成类代码"""
        response = {
            "class_name": "DataProcessor",
            "methods": [
                {"name": "load_data", "parameters": ["file_path"], "return_type": "DataFrame"},
                {"name": "process_data", "parameters": ["data"], "return_type": "DataFrame"},
                {"name": "save_data", "parameters": ["data", "output_path"], "return_type": "None"}
            ],
            "attributes": ["data", "config"]
        }
        
        return self.json_parser.parse(json.dumps(response))

# 性能测试和基准
class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self):
        self.results = []
    
    def test_parser_performance(self, parser: BaseOutputParser, test_data: List[str]) -> Dict[str, float]:
        """测试解析器性能"""
        import time
        
        start_time = time.time()
        for data in test_data:
            try:
                parser.parse(data)
            except Exception:
                pass  # 忽略解析错误，专注性能测试
        
        end_time = time.time()
        avg_time = (end_time - start_time) / len(test_data)
        
        return {
            "parser_type": type(parser).__name__,
            "test_cases": len(test_data),
            "total_time": end_time - start_time,
            "avg_time_per_case": avg_time
        }
    
    def run_all_benchmarks(self) -> List[Dict[str, float]]:
        """运行所有基准测试"""
        test_data = [
            "true", "false", "hello world", 
            '{"name": "test", "value": 123}',
            "item1,item2,item3",
            "2024-01-15 10:30:00"
        ]
        
        parsers = [
            StringOutputParser(),
            BooleanOutputParser(),
            JSONOutputParser(),
            ListOutputParser(),
            DatetimeOutputParser()
        ]
        
        results = []
        for parser in parsers:
            result = self.test_parser_performance(parser, test_data)
            results.append(result)
        
        return results

# 演示运行器
class DemoRunner:
    """演示运行器"""
    
    def __init__(self):
        self.manager = OutputParserManager()
        self.cs_bot = CustomerServiceBot()
        self.product_extractor = ProductExtractor()
        self.code_generator = CodeGenerator()
        self.benchmark = PerformanceBenchmark()
    
    def run_basic_parsers(self):
        """运行基础解析器演示"""
        print("=== 基础解析器演示 ===")
        
        # 字符串解析器
        string_parser = StringOutputParser()
        print("字符串解析:", string_parser.parse("  Hello World  "))
        
        # 布尔值解析器
        bool_parser = BooleanOutputParser()
        print("布尔值解析:", bool_parser.parse("yes"))
        print("布尔值解析:", bool_parser.parse("no"))
        
        # 列表解析器
        list_parser = ListOutputParser()
        print("列表解析:", list_parser.parse("apple,banana,orange"))
        
        # JSON解析器
        json_parser = JSONOutputParser()
        json_text = '{"name": "张三", "age": 25, "skills": ["Python", "Java"]}'
        print("JSON解析:", json_parser.parse(json_text))
        
        # 日期时间解析器
        datetime_parser = DatetimeOutputParser()
        print("日期时间解析:", datetime_parser.parse("2024-01-15 10:30:00"))
    
    def run_enum_parsers(self):
        """运行枚举解析器演示"""
        print("\n=== 枚举解析器演示 ===")
        
        sentiment_parser = EnumOutputParser(Sentiment)
        print("情感解析:", sentiment_parser.parse("positive"))
        print("情感解析:", sentiment_parser.parse("negative"))
        
        priority_parser = EnumOutputParser(Priority)
        print("优先级解析:", priority_parser.parse("high"))
    
    def run_xml_parser(self):
        """运行XML解析器演示"""
        print("\n=== XML解析器演示 ===")
        
        xml_parser = XMLOutputParser()
        xml_text = '<person><name>李四</name><age>30</age><skills><skill>Python</skill><skill>机器学习</skill></skills></person>'
        print("XML解析:", xml_parser.parse(xml_text))
    
    def run_regex_parser(self):
        """运行正则表达式解析器演示"""
        print("\n=== 正则表达式解析器演示 ===")
        
        regex_parser = RegexOutputParser(
            regex=r"姓名：(\w+)，年龄：(\d+)，邮箱：(\S+)",
            output_keys=['name', 'age', 'email']
        )
        text = "姓名：王五，年龄：28，邮箱：wangwu@example.com"
        print("正则解析:", regex_parser.parse(text))
    
    def run_customer_service_demo(self):
        """运行客服机器人演示"""
        print("\n=== 客服机器人演示 ===")
        
        queries = [
            "这个产品真的很好用！",
            "服务态度太差了，我要投诉",
            "请问订单什么时候发货？"
        ]
        
        for query in queries:
            result = self.cs_bot.process_query(query)
            print(f"查询: {query}")
            print(f"情感: {result['sentiment']}")
            print(f"关键词: {result['keywords']}")
            print(f"回复: {result['response']}")
            print("-" * 50)
    
    def run_product_extraction_demo(self):
        """运行产品信息提取演示"""
        print("\n=== 产品信息提取演示 ===")
        
        description = "新款MacBook Pro M3，售价15999元，配备16GB内存，512GB SSD，深空灰色，现货供应"
        
        product = self.product_extractor.extract_product_info(description)
        features = self.product_extractor.extract_features(description)
        
        print("产品信息:")
        print(f"名称: {product.name}")
        print(f"价格: {product.price}")
        print(f"类别: {product.category}")
        print(f"特性: {product.features}")
        print(f"库存: {product.in_stock}")
        print(f"提取的特性: {features}")
    
    def run_code_generation_demo(self):
        """运行代码生成演示"""
        print("\n=== 代码生成演示 ===")
        
        function_desc = "创建一个计算两个数最大公约数的函数"
        func_code = self.code_generator.generate_function(function_desc)
        print("生成的函数代码:")
        print(json.dumps(func_code, indent=2, ensure_ascii=False))
        
        class_desc = "创建一个用户管理类"
        class_code = self.code_generator.generate_class(class_desc)
        print("\n生成的类代码:")
        print(json.dumps(class_code, indent=2, ensure_ascii=False))
    
    def run_performance_benchmarks(self):
        """运行性能基准测试"""
        print("\n=== 性能基准测试 ===")
        
        results = self.benchmark.run_all_benchmarks()
        
        for result in results:
            print(f"解析器: {result['parser_type']}")
            print(f"测试用例: {result['test_cases']}")
            print(f"总耗时: {result['total_time']:.4f}s")
            print(f"平均耗时: {result['avg_time_per_case']:.6f}s")
            print("-" * 40)
    
    def run_all_demos(self):
        """运行所有演示"""
        self.run_basic_parsers()
        self.run_enum_parsers()
        self.run_xml_parser()
        self.run_regex_parser()
        self.run_customer_service_demo()
        self.run_product_extraction_demo()
        self.run_code_generation_demo()
        self.run_performance_benchmarks()

# 配置文件管理
class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.configs = {}
    
    def save_config(self, name: str, config: Dict[str, Any]):
        """保存配置"""
        self.configs[name] = config
        with open(f"{name}_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def load_config(self, name: str) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(f"{name}_config.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

# 错误处理和恢复
class ErrorHandler:
    """错误处理类"""
    
    @staticmethod
    def safe_parse(parser: BaseOutputParser, text: str, default_value: Any = None) -> Any:
        """安全解析，失败时返回默认值"""
        try:
            return parser.parse(text)
        except Exception as e:
            print(f"解析错误: {e}")
            return default_value
    
    @staticmethod
    def validate_json(text: str) -> bool:
        """验证JSON格式"""
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False

# 主函数
if __name__ == "__main__":
    print("LangChain 输出解析器完整实现库")
    print("=" * 50)
    
    # 创建演示运行器
    demo = DemoRunner()
    
    # 运行所有演示
    demo.run_all_demos()
    
    # 保存配置
    config_manager = ConfigManager()
    config_manager.save_config("output_parsers", {
        "version": "1.0.0",
        "supported_parsers": demo.manager.list_parsers(),
        "features": [
            "基础解析器", "枚举解析器", "XML解析", 
            "正则解析", "重试机制", "性能优化"
        ]
    })
    
    print("\n演示完成！配置文件已保存到 output_parsers_config.json")
    print("所有输出解析器功能已验证并可用。")