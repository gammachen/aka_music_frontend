#!/usr/bin/env python3
"""
LangChain输出解析器完整实现库
修复了datetime序列化问题，包含所有实际应用场景
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# 自定义JSON编码器处理datetime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# 基础数据模型
@dataclass
class Order:
    order_id: str
    customer_name: str
    items: List[str]
    total_amount: float
    status: str
    order_date: datetime

@dataclass
class Product:
    name: str
    price: float
    category: str
    features: List[str]
    rating: float

@dataclass
class CustomerReview:
    sentiment: str
    keywords: List[str]
    rating: int
    summary: str

@dataclass
class Meeting:
    title: str
    date: datetime
    attendees: List[str]
    agenda: List[str]
    duration: int

@dataclass
class FinancialReport:
    revenue: float
    expenses: float
    profit: float
    margin: float
    quarter: str

@dataclass
class HealthRecord:
    patient_id: str
    symptoms: List[str]
    diagnosis: str
    medications: List[str]
    follow_up: datetime

# 解析器类型枚举
class ParserType(Enum):
    STRING = "string"
    BOOLEAN = "boolean"
    JSON = "json"
    LIST = "list"
    DATETIME = "datetime"
    REGEX = "regex"

# 基础解析器接口
class BaseOutputParser:
    """所有解析器的基类"""
    
    def parse(self, text: str) -> Any:
        raise NotImplementedError
    
    def get_format_instructions(self) -> str:
        return "请提供有效的输出格式"

class StringOutputParser(BaseOutputParser):
    """字符串解析器 - 基础文本清理"""
    
    def parse(self, text: str) -> str:
        return text.strip()
    
    def get_format_instructions(self) -> str:
        return "返回纯文本格式"

class BooleanOutputParser(BaseOutputParser):
    """布尔值解析器 - 支持多语言"""
    
    def __init__(self):
        self.true_values = {"true", "yes", "是", "对", "正确", "真", "1", "t", "y"}
        self.false_values = {"false", "no", "否", "错", "错误", "假", "0", "f", "n"}
    
    def parse(self, text: str) -> bool:
        text_lower = text.strip().lower()
        if text_lower in self.true_values:
            return True
        elif text_lower in self.false_values:
            return False
        else:
            raise ValueError(f"无法解析布尔值: {text}")
    
    def get_format_instructions(self) -> str:
        return "返回true/false或yes/no"

class JSONOutputParser(BaseOutputParser):
    """JSON解析器 - 支持Markdown清理"""
    
    def parse(self, text: str) -> Dict[str, Any]:
        # 清理Markdown格式
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # 尝试修复常见JSON错误
            try:
                # 替换单引号为双引号
                fixed = cleaned.replace("'", '"')
                return json.loads(fixed)
            except:
                raise ValueError(f"无效的JSON格式: {e}")
    
    def get_format_instructions(self) -> str:
        return "返回有效的JSON格式"

class ListOutputParser(BaseOutputParser):
    """列表解析器 - 支持多种分隔符"""
    
    def __init__(self, separator: str = None):
        self.separator = separator
    
    def parse(self, text: str) -> List[str]:
        text = text.strip()
        
        # 尝试JSON解析
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed]
        except:
            pass
        
        # 分隔符检测
        separators = [self.separator] if self.separator else [",", ";", "、", "和", "以及"]
        
        for sep in separators:
            if sep in text:
                items = text.split(sep)
                return [item.strip() for item in items if item.strip()]
        
        # 单个项目
        return [text.strip()] if text.strip() else []
    
    def get_format_instructions(self) -> str:
        return "返回列表格式，使用逗号或分号分隔"

class DatetimeOutputParser(BaseOutputParser):
    """日期时间解析器 - 支持多种格式"""
    
    def parse(self, text: str) -> datetime:
        text = text.strip()
        
        # 常见格式
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d",
            "%Y年%m月%d日 %H点%M分",
            "%Y年%m月%d日",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"无法解析日期时间: {text}")
    
    def get_format_instructions(self) -> str:
        return "返回标准日期时间格式(YYYY-MM-DD HH:MM:SS)"

class RegexOutputParser(BaseOutputParser):
    """正则表达式解析器"""
    
    def __init__(self, pattern: str, group_names: List[str] = None):
        self.pattern = re.compile(pattern)
        self.group_names = group_names or []
    
    def parse(self, text: str) -> Dict[str, str]:
        matches = self.pattern.findall(text)
        if not matches:
            return {}
        
        if isinstance(matches[0], tuple):
            # 多个捕获组
            result = {}
            for i, name in enumerate(self.group_names):
                if i < len(matches[0]):
                    result[name] = matches[0][i]
            return result
        else:
            # 单个捕获组
            if self.group_names:
                return {self.group_names[0]: matches[0]}
            return {"match": matches[0]}
    
    def get_format_instructions(self) -> str:
        return f"匹配正则表达式: {self.pattern.pattern}"

# 解析器管理器
class ParserManager:
    """解析器注册和管理"""
    
    def __init__(self):
        self.parsers = {}
        self.register_default_parsers()
    
    def register_default_parsers(self):
        self.parsers[ParserType.STRING] = StringOutputParser()
        self.parsers[ParserType.BOOLEAN] = BooleanOutputParser()
        self.parsers[ParserType.JSON] = JSONOutputParser()
        self.parsers[ParserType.LIST] = ListOutputParser()
        self.parsers[ParserType.DATETIME] = DatetimeOutputParser()
    
    def register_parser(self, name: str, parser: BaseOutputParser):
        self.parsers[name] = parser
    
    def get_parser(self, name: str) -> BaseOutputParser:
        return self.parsers.get(name)

# 实际应用场景实现
class ECommerceSystem:
    """电商系统 - 订单和产品处理"""
    
    def __init__(self):
        self.json_parser = JSONOutputParser()
        self.list_parser = ListOutputParser()
        self.price_parser = RegexOutputParser(r'￥?(\d+(?:\.\d+)?)', ['price'])
    
    def parse_order(self, llm_response: str) -> Order:
        """解析订单信息"""
        data = self.json_parser.parse(llm_response)
        
        return Order(
            order_id=data.get('order_id', str(uuid.uuid4())),
            customer_name=data.get('customer_name', '未知用户'),
            items=self.list_parser.parse(str(data.get('items', []))),
            total_amount=float(data.get('total_amount', 0)),
            status=data.get('status', '待处理'),
            order_date=datetime.now()
        )
    
    def parse_product(self, llm_response: str) -> Product:
        """解析产品信息"""
        data = self.json_parser.parse(llm_response)
        
        return Product(
            name=data.get('name', '未命名产品'),
            price=float(data.get('price', 0)),
            category=data.get('category', '未分类'),
            features=self.list_parser.parse(str(data.get('features', []))),
            rating=float(data.get('rating', 0))
        )

class CustomerServiceBot:
    """客服机器人"""
    
    def __init__(self):
        self.sentiment_parser = StringOutputParser()
        self.keyword_parser = ListOutputParser()
    
    def analyze_sentiment(self, message: str) -> CustomerReview:
        """分析用户消息情感"""
        # 模拟LLM响应
        llm_response = json.dumps({
            "sentiment": "positive",
            "keywords": ["满意", "快速", "推荐"],
            "rating": 5,
            "summary": "用户对服务很满意"
        })
        
        data = JSONOutputParser().parse(llm_response)
        
        return CustomerReview(
            sentiment=data.get('sentiment', 'neutral'),
            keywords=data.get('keywords', []),
            rating=int(data.get('rating', 3)),
            summary=data.get('summary', '')
        )

class MeetingScheduler:
    """会议调度系统"""
    
    def __init__(self):
        self.datetime_parser = DatetimeOutputParser()
        self.list_parser = ListOutputParser()
    
    def parse_meeting(self, llm_response: str) -> Meeting:
        """解析会议信息"""
        data = JSONOutputParser().parse(llm_response)
        
        return Meeting(
            title=data.get('title', '未命名会议'),
            date=self.datetime_parser.parse(data.get('date', str(datetime.now()))),
            attendees=self.list_parser.parse(str(data.get('attendees', []))),
            agenda=self.list_parser.parse(str(data.get('agenda', []))),
            duration=int(data.get('duration', 60))
        )

class FinancialAnalyzer:
    """财务分析系统"""
    
    def __init__(self):
        self.amount_parser = RegexOutputParser(r'(\d+(?:\.\d+)?)(?:万|亿)?', ['amount'])
        self.percentage_parser = RegexOutputParser(r'(\d+(?:\.\d+)?)%', ['percentage'])
    
    def parse_report(self, llm_response: str) -> FinancialReport:
        """解析财务报告"""
        data = JSONOutputParser().parse(llm_response)
        
        return FinancialReport(
            revenue=float(data.get('revenue', 0)),
            expenses=float(data.get('expenses', 0)),
            profit=float(data.get('profit', 0)),
            margin=float(data.get('margin', 0)),
            quarter=data.get('quarter', 'Q1')
        )

class HealthTracker:
    """健康追踪系统"""
    
    def __init__(self):
        self.symptom_parser = ListOutputParser()
        self.medication_parser = ListOutputParser()
    
    def parse_health_record(self, llm_response: str) -> HealthRecord:
        """解析健康记录"""
        data = JSONOutputParser().parse(llm_response)
        
        return HealthRecord(
            patient_id=data.get('patient_id', str(uuid.uuid4())),
            symptoms=self.symptom_parser.parse(str(data.get('symptoms', []))),
            diagnosis=data.get('diagnosis', '待诊断'),
            medications=self.medication_parser.parse(str(data.get('medications', []))),
            follow_up=datetime.now()
        )

# 性能测试工具
class PerformanceTester:
    """性能测试器"""
    
    def __init__(self):
        self.results = []
    
    def test_parser(self, parser: BaseOutputParser, test_data: List[str], iterations: int = 100) -> Dict[str, Any]:
        """测试解析器性能"""
        import time
        
        start_time = time.time()
        success_count = 0
        
        for _ in range(iterations):
            for data in test_data:
                try:
                    parser.parse(data)
                    success_count += 1
                except Exception:
                    pass
        
        end_time = time.time()
        total_time = end_time - start_time
        
        result = {
            "parser_type": type(parser).__name__,
            "total_operations": iterations * len(test_data),
            "successful_operations": success_count,
            "total_time_seconds": total_time,
            "average_time_per_operation": total_time / (iterations * len(test_data)),
            "success_rate": success_count / (iterations * len(test_data))
        }
        
        self.results.append(result)
        return result
    
    def save_results(self, filename: str):
        """保存测试结果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

# 演示运行器
class DemoRunner:
    """演示运行器"""
    
    def __init__(self):
        self.ecommerce = ECommerceSystem()
        self.customer_service = CustomerServiceBot()
        self.meeting_scheduler = MeetingScheduler()
        self.financial_analyzer = FinancialAnalyzer()
        self.health_tracker = HealthTracker()
        self.performance_tester = PerformanceTester()
    
    def run_all_demos(self):
        """运行所有演示"""
        print("=== LangChain 输出解析器完整演示 ===\n")
        
        # 1. 电商系统演示
        print("1. 电商系统演示:")
        order_response = '{"order_id": "ORD-2024-001", "customer_name": "张三", "items": ["iPhone 15", "AirPods"], "total_amount": 8999.0, "status": "已发货"}'
        order = self.ecommerce.parse_order(order_response)
        print(f"订单信息: {json.dumps(asdict(order), ensure_ascii=False, indent=2, cls=DateTimeEncoder)}")
        
        product_response = '{"name": "MacBook Pro", "price": 12999, "category": "笔记本电脑", "features": ["M3芯片", "16GB内存", "512GB SSD"], "rating": 4.8}'
        product = self.ecommerce.parse_product(product_response)
        print(f"产品信息: {json.dumps(asdict(product), ensure_ascii=False, indent=2)}")
        
        # 2. 客服机器人演示
        print("\n2. 客服机器人演示:")
        review = self.customer_service.analyze_sentiment("服务很好，物流很快！")
        print(f"情感分析: {json.dumps(asdict(review), ensure_ascii=False, indent=2)}")
        
        # 3. 会议调度演示
        print("\n3. 会议调度演示:")
        meeting_response = '{"title": "产品发布会", "date": "2024-03-15 14:00:00", "attendees": ["李四", "王五", "赵六"], "agenda": ["开场介绍", "产品展示", "Q&A环节"], "duration": 120}'
        meeting = self.meeting_scheduler.parse_meeting(meeting_response)
        print(f"会议信息: {json.dumps(asdict(meeting), ensure_ascii=False, indent=2, cls=DateTimeEncoder)}")
        
        # 4. 财务分析演示
        print("\n4. 财务分析演示:")
        report_response = '{"revenue": 1000000, "expenses": 600000, "profit": 400000, "margin": 40, "quarter": "Q1 2024"}'
        report = self.financial_analyzer.parse_report(report_response)
        print(f"财务报告: {json.dumps(asdict(report), ensure_ascii=False, indent=2)}")
        
        # 5. 健康追踪演示
        print("\n5. 健康追踪演示:")
        health_response = '{"patient_id": "P-001", "symptoms": ["头痛", "发烧", "咳嗽"], "diagnosis": "普通感冒", "medications": ["退烧药", "止咳糖浆"]}'
        health = self.health_tracker.parse_health_record(health_response)
        print(f"健康记录: {json.dumps(asdict(health), ensure_ascii=False, indent=2, cls=DateTimeEncoder)}")
        
        # 6. 性能测试
        print("\n6. 性能测试:")
        test_data = [
            '{"name": "test1", "value": 100}',
            '{"items": ["a", "b", "c"]}',
            'true',
            'hello world',
            '2024-01-15 10:30:00'
        ]
        
        parsers = [
            JSONOutputParser(),
            StringOutputParser(),
            BooleanOutputParser(),
            ListOutputParser(),
            DatetimeOutputParser()
        ]
        
        for parser in parsers:
            result = self.performance_tester.test_parser(parser, test_data, 50)
            print(f"{result['parser_type']}: 平均时间 {result['average_time_per_operation']:.6f}s, 成功率 {result['success_rate']:.2%}")
        
        # 保存配置
        self.performance_tester.save_results('final_parsers_performance.json')
        print("\n性能测试结果已保存到 final_parsers_performance.json")

if __name__ == "__main__":
    runner = DemoRunner()
    runner.run_all_demos()