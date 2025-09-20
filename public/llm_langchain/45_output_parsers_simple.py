#!/usr/bin/env python3
"""
LangChain 输出解析器简化实现库
修复递归问题，专注于核心功能演示
"""

import json
import re
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime
from dataclasses import dataclass

# 基础解析器类
class BaseOutputParser:
    def parse(self, text: str) -> Any:
        raise NotImplementedError

class StringOutputParser(BaseOutputParser):
    """字符串解析器"""
    def parse(self, text: str) -> str:
        return text.strip()

class BooleanOutputParser(BaseOutputParser):
    """布尔值解析器"""
    def __init__(self):
        self.true_values = {"true", "yes", "1", "是", "对", "正确", "真"}
        self.false_values = {"false", "no", "0", "否", "错", "错误", "假"}
    
    def parse(self, text: str) -> bool:
        text_lower = text.strip().lower()
        if any(val in text_lower for val in self.true_values):
            return True
        elif any(val in text_lower for val in self.false_values):
            return False
        return len(text_lower) > 0

class ListOutputParser(BaseOutputParser):
    """列表解析器"""
    def __init__(self, separator: str = ","):
        self.separator = separator
    
    def parse(self, text: str) -> List[str]:
        items = [item.strip() for item in text.split(self.separator)]
        return [item for item in items if item]

class JSONOutputParser(BaseOutputParser):
    """JSON解析器"""
    def parse(self, text: str) -> Dict[str, Any]:
        cleaned = re.sub(r'```json\s*|\s*```', '', text.strip())
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # 尝试修复常见格式问题
            cleaned = cleaned.replace("'", '"')
            try:
                return json.loads(cleaned)
            except:
                raise ValueError(f"无效的JSON格式: {e}")

class DatetimeOutputParser(BaseOutputParser):
    """日期时间解析器"""
    def __init__(self, format_str: str = "%Y-%m-%d %H:%M:%S"):
        self.format_str = format_str
    
    def parse(self, text: str) -> datetime:
        text = text.strip()
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"无法解析日期: {text}")

class RegexOutputParser(BaseOutputParser):
    """正则表达式解析器"""
    def __init__(self, pattern: str, keys: List[str]):
        self.pattern = re.compile(pattern)
        self.keys = keys
    
    def parse(self, text: str) -> Dict[str, str]:
        match = self.pattern.search(text)
        if match:
            return dict(zip(self.keys, match.groups()))
        return {key: "" for key in self.keys}

# 数据模型
@dataclass
class Person:
    name: str
    age: int
    email: str
    skills: List[str]

@dataclass
class Product:
    name: str
    price: float
    category: str
    features: List[str]
    in_stock: bool

# 枚举类型
class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# 实际应用场景
class CustomerServiceBot:
    """客服机器人"""
    def __init__(self):
        self.sentiment_parser = self._create_sentiment_parser()
        self.list_parser = ListOutputParser()
    
    def _create_sentiment_parser(self):
        """创建情感解析器"""
        class SentimentParser(BaseOutputParser):
            def parse(self, text: str) -> Sentiment:
                positive_words = {"好", "棒", "满意", "喜欢", "优秀"}
                negative_words = {"差", "不好", "失望", "问题", "投诉"}
                
                text_lower = text.lower()
                
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count > neg_count:
                    return Sentiment.POSITIVE
                elif neg_count > pos_count:
                    return Sentiment.NEGATIVE
                else:
                    return Sentiment.NEUTRAL
        
        return SentimentParser()
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """分析用户查询"""
        sentiment = self.sentiment_parser.parse(query)
        keywords = self.list_parser.parse("退款,订单,物流,客服,质量")
        relevant_keywords = [kw for kw in keywords if kw in query]
        
        return {
            "query": query,
            "sentiment": sentiment.value,
            "keywords": relevant_keywords,
            "response": self._generate_response(sentiment, relevant_keywords)
        }
    
    def _generate_response(self, sentiment: Sentiment, keywords: List[str]) -> str:
        """生成响应"""
        if sentiment == Sentiment.POSITIVE:
            return "感谢您的反馈！我们很高兴您对服务满意。"
        elif sentiment == Sentiment.NEGATIVE:
            return "非常抱歉给您带来不便，我们会立即处理您的问题。"
        else:
            return "感谢您的咨询，请问有什么可以帮助您的？"

class ProductExtractor:
    """产品信息提取器"""
    def __init__(self):
        self.json_parser = JSONOutputParser()
        self.price_parser = RegexOutputParser(r'(\d+(?:\.\d+)?)元?', ['price'])
    
    def extract_from_description(self, description: str) -> Dict[str, Any]:
        """从描述中提取产品信息"""
        # 模拟LLM响应
        mock_response = {
            "name": "iPhone 15",
            "category": "智能手机",
            "features": ["A17芯片", "4800万像素", "钛合金机身"],
            "in_stock": True
        }
        
        product_info = self.json_parser.parse(json.dumps(mock_response))
        
        # 提取价格
        price_match = self.price_parser.parse(description)
        if price_match['price']:
            product_info['price'] = float(price_match['price'])
        
        return product_info

class ResumeParser:
    """简历解析器"""
    def __init__(self):
        self.json_parser = JSONOutputParser()
    
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """解析简历文本"""
        # 模拟LLM响应
        mock_response = {
            "name": "张三",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
            "skills": ["Python", "机器学习", "数据分析"],
            "experience": [
                {
                    "company": "科技公司",
                    "position": "高级开发工程师",
                    "duration": "2020-2024"
                }
            ],
            "education": [
                {
                    "school": "北京大学",
                    "degree": "硕士",
                    "major": "计算机科学"
                }
            ]
        }
        
        return self.json_parser.parse(json.dumps(mock_response))

# 演示运行器
class DemoRunner:
    """演示运行器"""
    def __init__(self):
        self.cs_bot = CustomerServiceBot()
        self.product_extractor = ProductExtractor()
        self.resume_parser = ResumeParser()
    
    def run_basic_parsers(self):
        """运行基础解析器演示"""
        print("=== 基础解析器演示 ===")
        
        # 字符串解析
        parser = StringOutputParser()
        print("字符串:", parser.parse("  Hello World  "))
        
        # 布尔值解析
        bool_parser = BooleanOutputParser()
        print("布尔值1:", bool_parser.parse("yes"))
        print("布尔值2:", bool_parser.parse("false"))
        
        # 列表解析
        list_parser = ListOutputParser()
        print("列表:", list_parser.parse("apple, banana, orange"))
        
        # JSON解析
        json_parser = JSONOutputParser()
        json_text = '{"name": "张三", "age": 25, "skills": ["Python", "Java"]}'
        print("JSON:", json_parser.parse(json_text))
        
        # 日期时间解析
        dt_parser = DatetimeOutputParser()
        print("日期时间:", dt_parser.parse("2024-01-15 10:30:00"))
    
    def run_regex_parser(self):
        """运行正则表达式解析器"""
        print("\n=== 正则表达式解析器演示 ===")
        
        regex_parser = RegexOutputParser(
            pattern=r"姓名：(\w+)，年龄：(\d+)岁，邮箱：(\S+)",
            keys=["name", "age", "email"]
        )
        
        text = "姓名：李四，年龄：28岁，邮箱：lisi@example.com"
        result = regex_parser.parse(text)
        print("提取信息:", result)
    
    def run_customer_service_demo(self):
        """运行客服机器人演示"""
        print("\n=== 客服机器人演示 ===")
        
        queries = [
            "这个产品质量很好，我很满意！",
            "服务态度太差了，我要投诉",
            "请问订单什么时候能发货？"
        ]
        
        for query in queries:
            result = self.cs_bot.analyze_query(query)
            print(f"查询: {query}")
            print(f"情感: {result['sentiment']}")
            print(f"关键词: {result['keywords']}")
            print(f"回复: {result['response']}")
            print("-" * 40)
    
    def run_product_extraction_demo(self):
        """运行产品信息提取演示"""
        print("\n=== 产品信息提取演示 ===")
        
        descriptions = [
            "iPhone 15 Pro售价8999元，配备A17芯片，4800万像素相机，现货供应",
            "MacBook Air M2售价9999元，13.6英寸显示屏，超长续航，轻薄便携"
        ]
        
        for desc in descriptions:
            product = self.product_extractor.extract_from_description(desc)
            print(f"描述: {desc}")
            print(f"产品信息: {product}")
            print("-" * 40)
    
    def run_resume_parsing_demo(self):
        """运行简历解析演示"""
        print("\n=== 简历解析演示 ===")
        
        resume_text = """
        张三，计算机科学硕士，5年Python开发经验。
        邮箱：zhangsan@example.com，电话：13800138000。
        技能：Python、机器学习、数据分析、Web开发。
        工作经历：2020-2024在科技公司担任高级开发工程师。
        教育背景：北京大学计算机科学硕士。
        """
        
        resume = self.resume_parser.parse_resume(resume_text)
        print("解析的简历信息:")
        print(json.dumps(resume, indent=2, ensure_ascii=False))
    
    def run_all_demos(self):
        """运行所有演示"""
        self.run_basic_parsers()
        self.run_regex_parser()
        self.run_customer_service_demo()
        self.run_product_extraction_demo()
        self.run_resume_parsing_demo()

# 配置管理
class ConfigManager:
    def save_config(self, name: str, config: Dict[str, Any]):
        """保存配置"""
        with open(f"{name}_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def load_config(self, name: str) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(f"{name}_config.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

# 性能测试
class PerformanceTester:
    def test_parser_speed(self, parser: BaseOutputParser, test_cases: List[str]) -> Dict[str, float]:
        """测试解析器速度"""
        import time
        
        start_time = time.time()
        for case in test_cases:
            try:
                parser.parse(case)
            except:
                pass  # 忽略错误，专注性能
        
        end_time = time.time()
        
        return {
            "parser_type": type(parser).__name__,
            "total_time": end_time - start_time,
            "avg_time_per_case": (end_time - start_time) / len(test_cases)
        }

if __name__ == "__main__":
    print("LangChain 输出解析器简化实现")
    print("=" * 50)
    
    demo = DemoRunner()
    demo.run_all_demos()
    
    # 性能测试
    tester = PerformanceTester()
    test_cases = ["true", "hello", '{"a":1}', "item1,item2"]
    
    parsers = [
        StringOutputParser(),
        BooleanOutputParser(),
        JSONOutputParser(),
        ListOutputParser()
    ]
    
    print("\n=== 性能测试结果 ===")
    for parser in parsers:
        result = tester.test_parser_speed(parser, test_cases)
        print(f"{result['parser_type']}: {result['avg_time_per_case']:.6f}s/用例")
    
    # 保存配置
    config = ConfigManager()
    config.save_config("simple_parsers", {
        "version": "1.0.0",
        "parsers": [
            "StringOutputParser", "BooleanOutputParser", "ListOutputParser",
            "JSONOutputParser", "DatetimeOutputParser", "RegexOutputParser"
        ],
        "applications": [
            "客服机器人", "产品信息提取", "简历解析", "数据验证"
        ]
    })
    
    print("\n配置已保存到 simple_parsers_config.json")