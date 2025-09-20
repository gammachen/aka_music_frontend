#!/usr/bin/env python3
"""
LangChain 输出解析器实际使用指南
展示如何在真实项目中应用各种解析器
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re

# 导入简化版解析器
from output_parsers_simple import (
    StringOutputParser, BooleanOutputParser, ListOutputParser,
    JSONOutputParser, DatetimeOutputParser, RegexOutputParser,
    CustomerServiceBot, ProductExtractor, ResumeParser
)

# 数据模型定义
@dataclass
class Order:
    order_id: str
    customer_name: str
    items: List[str]
    total_amount: float
    status: str
    order_date: datetime
    shipping_address: Dict[str, str]

@dataclass
class Review:
    product_id: str
    customer_name: str
    rating: int
    comment: str
    sentiment: str
    keywords: List[str]
    review_date: datetime

@dataclass
class Meeting:
    title: str
    participants: List[str]
    start_time: datetime
    duration_minutes: int
    agenda: List[str]
    location: str

# 实际业务场景类
class ECommerceSystem:
    """电商系统 - 订单处理和商品评论"""
    
    def __init__(self):
        self.json_parser = JSONOutputParser()
        self.list_parser = ListOutputParser()
        self.datetime_parser = DatetimeOutputParser()
        self.price_regex = RegexOutputParser(r'￥?(\d+(?:\.\d+)?)', ['price'])
    
    def process_order_query(self, query: str) -> Dict[str, Any]:
        """处理订单查询"""
        # 模拟LLM响应
        llm_response = {
            "order_id": "ORD20240115001",
            "customer_name": "张三",
            "items": ["iPhone 15", "AirPods Pro", "手机壳"],
            "total_amount": 8999.00,
            "status": "已发货",
            "order_date": "2024-01-15 10:30:00",
            "shipping_address": {
                "province": "北京市",
                "city": "朝阳区",
                "district": "三里屯",
                "detail": "某某大厦1001室"
            }
        }
        
        order_data = self.json_parser.parse(json.dumps(llm_response))
        order_data['order_date'] = self.datetime_parser.parse(order_data['order_date'])
        
        return asdict(Order(**order_data))
    
    def analyze_product_review(self, review_text: str) -> Dict[str, Any]:
        """分析商品评论"""
        # 模拟LLM响应
        llm_response = {
            "product_id": "PROD12345",
            "customer_name": "李四",
            "rating": 5,
            "comment": "产品质量很好，物流很快，客服态度也很好！",
            "sentiment": "positive",
            "keywords": ["质量好", "物流快", "客服好"],
            "review_date": "2024-01-14 15:20:00"
        }
        
        review_data = self.json_parser.parse(json.dumps(llm_response))
        review_data['review_date'] = self.datetime_parser.parse(review_data['review_date'])
        
        return asdict(Review(**review_data))
    
    def extract_price_from_text(self, text: str) -> Optional[float]:
        """从文本中提取价格"""
        result = self.price_regex.parse(text)
        return float(result['price']) if result['price'] else None

class MeetingScheduler:
    """会议调度系统"""
    
    def __init__(self):
        self.json_parser = JSONOutputParser()
        self.datetime_parser = DatetimeOutputParser()
        self.participants_parser = ListOutputParser()
    
    def schedule_meeting(self, meeting_request: str) -> Dict[str, Any]:
        """安排会议"""
        # 模拟LLM响应
        llm_response = {
            "title": "产品发布会",
            "participants": ["张三", "李四", "王五", "赵六"],
            "start_time": "2024-01-16 14:00:00",
            "duration_minutes": 120,
            "agenda": ["项目介绍", "技术演示", "Q&A环节", "下一步计划"],
            "location": "会议室A"
        }
        
        meeting_data = self.json_parser.parse(json.dumps(llm_response))
        meeting_data['start_time'] = self.datetime_parser.parse(meeting_data['start_time'])
        
        return asdict(Meeting(**meeting_data))
    
    def parse_availability_query(self, query: str) -> Dict[str, Any]:
        """解析可用性查询"""
        # 模拟LLM响应
        llm_response = {
            "available_slots": [
                {"date": "2024-01-16", "time": "10:00"},
                {"date": "2024-01-16", "time": "14:00"},
                {"date": "2024-01-17", "time": "09:00"}
            ],
            "duration_options": [30, 60, 90, 120],
            "recommended_slot": {"date": "2024-01-16", "time": "14:00"}
        }
        
        return self.json_parser.parse(json.dumps(llm_response))

class FinancialAnalyzer:
    """财务分析系统"""
    
    def __init__(self):
        self.json_parser = JSONOutputParser()
        self.amount_parser = RegexOutputParser(r'￥?(\d+(?:\.\d+)?)', ['amount'])
        self.percentage_parser = RegexOutputParser(r'(\d+(?:\.\d+)?)%', ['percentage'])
    
    def analyze_expense_report(self, report_text: str) -> Dict[str, Any]:
        """分析费用报告"""
        # 模拟LLM响应
        llm_response = {
            "total_expenses": 15850.50,
            "categories": {
                "交通": 3500.00,
                "餐饮": 4200.50,
                "住宿": 6150.00,
                "其他": 2000.00
            },
            "period": "2024-01-01 至 2024-01-15",
            "status": "已审核",
            "notes": "费用合理，符合公司政策"
        }
        
        return self.json_parser.parse(json.dumps(llm_response))
    
    def extract_financial_data(self, text: str) -> Dict[str, float]:
        """提取财务数据"""
        amounts = re.findall(r'￥?(\d+(?:\.\d+)?)', text)
        percentages = re.findall(r'(\d+(?:\.\d+)?)%', text)
        
        return {
            "amounts": [float(a) for a in amounts],
            "percentages": [float(p) for p in percentages]
        }

class HealthTracker:
    """健康追踪系统"""
    
    def __init__(self):
        self.json_parser = JSONOutputParser()
        self.datetime_parser = DatetimeOutputParser()
        self.symptoms_parser = ListOutputParser()
    
    def parse_health_report(self, report_text: str) -> Dict[str, Any]:
        """解析健康报告"""
        # 模拟LLM响应
        llm_response = {
            "patient_name": "王五",
            "checkup_date": "2024-01-15 09:00:00",
            "vitals": {
                "blood_pressure": "120/80",
                "heart_rate": 72,
                "temperature": 36.5,
                "weight": 70.5
            },
            "symptoms": ["轻微头痛", "疲劳"],
            "recommendations": ["充足休息", "多喝水", "一周后复查"],
            "status": "良好"
        }
        
        health_data = self.json_parser.parse(json.dumps(llm_response))
        health_data['checkup_date'] = self.datetime_parser.parse(health_data['checkup_date'])
        
        return health_data
    
    def analyze_symptoms(self, symptoms_text: str) -> Dict[str, Any]:
        """分析症状"""
        # 模拟LLM响应
        llm_response = {
            "possible_conditions": ["感冒", "过敏"],
            "severity": "轻微",
            "urgency": "低",
            "advice": "观察24小时，如症状加重请就医"
        }
        
        return self.json_parser.parse(json.dumps(llm_response))

class EducationPlatform:
    """教育平台"""
    
    def __init__(self):
        self.json_parser = JSONOutputParser()
        self.list_parser = ListOutputParser()
        self.datetime_parser = DatetimeOutputParser()
    
    def generate_study_plan(self, requirements: str) -> Dict[str, Any]:
        """生成学习计划"""
        # 模拟LLM响应
        llm_response = {
            "student_name": "小明",
            "subject": "Python编程",
            "duration_weeks": 12,
            "weekly_hours": 10,
            "topics": [
                "Python基础语法", "数据类型", "控制流", "函数", 
                "面向对象", "文件操作", "异常处理", "模块和包"
            ],
            "start_date": "2024-01-20 09:00:00",
            "target_level": "中级",
            "assessment_methods": ["每周练习", "项目作业", "期末考试"]
        }
        
        plan_data = self.json_parser.parse(json.dumps(llm_response))
        plan_data['start_date'] = self.datetime_parser.parse(plan_data['start_date'])
        
        return plan_data
    
    def evaluate_assignment(self, assignment_text: str) -> Dict[str, Any]:
        """评估作业"""
        # 模拟LLM响应
        llm_response = {
            "assignment_title": "Python基础练习",
            "student_name": "小红",
            "score": 85,
            "feedback": "代码结构清晰，逻辑正确，但可以增加更多注释",
            "improvements": ["添加函数文档字符串", "使用更有意义的变量名", "增加异常处理"],
            "completion_date": "2024-01-15 16:30:00",
            "status": "已通过"
        }
        
        evaluation_data = self.json_parser.parse(json.dumps(llm_response))
        evaluation_data['completion_date'] = self.datetime_parser.parse(evaluation_data['completion_date'])
        
        return evaluation_data

class DataValidationSystem:
    """数据验证系统"""
    
    def __init__(self):
        self.json_parser = JSONOutputParser()
        self.email_regex = RegexOutputParser(r'\S+@\S+\.\S+', ['email'])
        self.phone_regex = RegexOutputParser(r'1[3-9]\d{9}', ['phone'])
    
    def validate_user_registration(self, user_data: str) -> Dict[str, Any]:
        """验证用户注册信息"""
        # 模拟LLM响应
        llm_response = {
            "username": "zhangsan123",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
            "validation_results": {
                "username": {"valid": True, "message": "用户名可用"},
                "email": {"valid": True, "message": "邮箱格式正确"},
                "phone": {"valid": True, "message": "手机号格式正确"}
            },
            "suggestions": ["密码强度可以加强", "建议绑定邮箱验证"]
        }
        
        return self.json_parser.parse(json.dumps(llm_response))
    
    def validate_api_response(self, response_text: str) -> Dict[str, Any]:
        """验证API响应格式"""
        # 模拟LLM响应
        llm_response = {
            "status": "success",
            "data": {"user_id": 123, "name": "张三"},
            "message": "操作成功",
            "code": 200,
            "timestamp": "2024-01-15 14:30:00"
        }
        
        return self.json_parser.parse(json.dumps(llm_response))

# 实际应用演示器
class RealWorldApplicationDemo:
    """实际应用演示器"""
    
    def __init__(self):
        self.ecommerce = ECommerceSystem()
        self.meeting = MeetingScheduler()
        self.finance = FinancialAnalyzer()
        self.health = HealthTracker()
        self.education = EducationPlatform()
        self.validation = DataValidationSystem()
    
    def run_ecommerce_demo(self):
        """运行电商系统演示"""
        print("=== 电商系统演示 ===")
        
        # 订单查询
        order_result = self.ecommerce.process_order_query("查询我的订单状态")
        print("订单信息:")
        print(json.dumps(order_result, indent=2, default=str, ensure_ascii=False))
        
        # 商品评论分析
        review_text = "这个产品真的很棒！质量好，物流快，客服态度也很好"
        review_result = self.ecommerce.analyze_product_review(review_text)
        print("\n评论分析:")
        print(json.dumps(review_result, indent=2, default=str, ensure_ascii=False))
        
        # 价格提取
        text_with_price = "iPhone 15售价￥8999，现在有优惠"
        price = self.ecommerce.extract_price_from_text(text_with_price)
        print(f"\n提取的价格: ￥{price}")
    
    def run_meeting_demo(self):
        """运行会议系统演示"""
        print("\n=== 会议系统演示 ===")
        
        meeting_request = "安排一个产品发布会，参与人员包括张三、李四、王五"
        meeting_result = self.meeting.schedule_meeting(meeting_request)
        print("会议安排:")
        print(json.dumps(meeting_result, indent=2, default=str, ensure_ascii=False))
        
        availability = self.meeting.parse_availability_query("查看明天下午的可用时间段")
        print("\n可用时间段:")
        print(json.dumps(availability, indent=2, ensure_ascii=False))
    
    def run_finance_demo(self):
        """运行财务系统演示"""
        print("\n=== 财务系统演示 ===")
        
        expense_report = "本月费用总计15850.50元，其中交通费3500元，餐饮费4200.50元，住宿费6150元，其他费用2000元"
        expense_result = self.finance.analyze_expense_report(expense_report)
        print("费用分析:")
        print(json.dumps(expense_result, indent=2, ensure_ascii=False))
        
        financial_text = "收入增长15%，支出减少8%，净利润￥50000"
        financial_data = self.finance.extract_financial_data(financial_text)
        print("\n财务数据提取:")
        print(json.dumps(financial_data, indent=2, ensure_ascii=False))
    
    def run_health_demo(self):
        """运行健康系统演示"""
        print("\n=== 健康系统演示 ===")
        
        health_report = "王五，体检日期2024-01-15，血压120/80，心率72，体温36.5度，体重70.5公斤"
        health_result = self.health.parse_health_report(health_report)
        print("健康报告:")
        print(json.dumps(health_result, indent=2, ensure_ascii=False))
        
        symptoms = "轻微头痛，感觉有点疲劳"
        symptoms_result = self.health.analyze_symptoms(symptoms)
        print("\n症状分析:")
        print(json.dumps(symptoms_result, indent=2, ensure_ascii=False))
    
    def run_education_demo(self):
        """运行教育系统演示"""
        print("\n=== 教育系统演示 ===")
        
        requirements = "小明想学习Python编程，希望12周内达到中级水平"
        study_plan = self.education.generate_study_plan(requirements)
        print("学习计划:")
        print(json.dumps(study_plan, indent=2, ensure_ascii=False))
        
        assignment = "小红完成了Python基础练习作业"
        evaluation = self.education.evaluate_assignment(assignment)
        print("\n作业评估:")
        print(json.dumps(evaluation, indent=2, ensure_ascii=False))
    
    def run_validation_demo(self):
        """运行验证系统演示"""
        print("\n=== 验证系统演示 ===")
        
        user_data = "用户名zhangsan123，邮箱zhangsan@example.com，手机号13800138000"
        validation_result = self.validation.validate_user_registration(user_data)
        print("用户注册验证:")
        print(json.dumps(validation_result, indent=2, ensure_ascii=False))
        
        api_response = "状态success，数据包含用户ID123和姓名张三"
        api_validation = self.validation.validate_api_response(api_response)
        print("\nAPI响应验证:")
        print(json.dumps(api_validation, indent=2, ensure_ascii=False))
    
    def run_all_demos(self):
        """运行所有演示"""
        self.run_ecommerce_demo()
        self.run_meeting_demo()
        self.run_finance_demo()
        self.run_health_demo()
        self.run_education_demo()
        self.run_validation_demo()

# 配置和工具类
class ConfigurationManager:
    """配置管理器"""
    
    def __init__(self):
        self.configs = {}
    
    def save_application_config(self, app_name: str, config: Dict[str, Any]):
        """保存应用配置"""
        filename = f"{app_name}_config.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"配置已保存到 {filename}")
    
    def load_application_config(self, app_name: str) -> Dict[str, Any]:
        """加载应用配置"""
        filename = f"{app_name}_config.json"
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

class ErrorHandler:
    """错误处理工具"""
    
    @staticmethod
    def safe_parse(parser, text: str, default: Any = None) -> Any:
        """安全解析，失败返回默认值"""
        try:
            return parser.parse(text)
        except Exception as e:
            print(f"解析错误: {e}")
            return default
    
    @staticmethod
    def validate_data_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """验证数据结构"""
        return all(field in data for field in required_fields)

# 性能监控器
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = []
    
    def measure_parser_performance(self, parser, test_data: List[str]) -> Dict[str, float]:
        """测量解析器性能"""
        import time
        
        start_time = time.time()
        success_count = 0
        
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
            "total_tests": len(test_data),
            "success_rate": success_count / len(test_data),
            "total_time": total_time,
            "avg_time_per_test": total_time / len(test_data)
        }
        
        self.metrics.append(result)
        return result
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        return {
            "total_parsers": len(self.metrics),
            "overall_performance": {
                "avg_success_rate": sum(m['success_rate'] for m in self.metrics) / len(self.metrics),
                "total_time": sum(m['total_time'] for m in self.metrics),
                "fastest_parser": min(self.metrics, key=lambda x: x['avg_time_per_test'])
            },
            "detailed_metrics": self.metrics
        }

# 主函数
if __name__ == "__main__":
    print("LangChain 输出解析器实际使用指南")
    print("=" * 60)
    
    # 创建演示器
    demo = RealWorldApplicationDemo()
    
    # 运行所有实际应用演示
    demo.run_all_demos()
    
    # 配置管理
    config_manager = ConfigurationManager()
    
    # 保存各个系统的配置
    ecommerce_config = {
        "system": "电商系统",
        "parsers": ["JSONOutputParser", "DatetimeOutputParser", "RegexOutputParser"],
        "features": ["订单处理", "评论分析", "价格提取"],
        "data_models": ["Order", "Review"]
    }
    
    meeting_config = {
        "system": "会议调度系统",
        "parsers": ["JSONOutputParser", "DatetimeOutputParser", "ListOutputParser"],
        "features": ["会议安排", "可用性查询", "日程管理"],
        "data_models": ["Meeting"]
    }
    
    # 保存配置
    config_manager.save_application_config("ecommerce", ecommerce_config)
    config_manager.save_application_config("meeting", meeting_config)
    
    # 性能测试
    monitor = PerformanceMonitor()
    
    test_data = [
        '{"name": "test", "value": 123}',
        '2024-01-15 10:30:00',
        'item1,item2,item3',
        'true',
        'Hello World'
    ]
    
    parsers = [
        JSONOutputParser(),
        DatetimeOutputParser(),
        ListOutputParser(),
        StringOutputParser(),
        BooleanOutputParser()
    ]
    
    print("\n=== 性能测试结果 ===")
    for parser in parsers:
        result = monitor.measure_parser_performance(parser, test_data)
        print(f"{result['parser_type']}: {result['avg_time_per_test']:.6f}s, 成功率: {result['success_rate']:.2%}")
    
    # 生成性能报告
    performance_report = monitor.generate_performance_report()
    
    with open("performance_report.json", 'w', encoding='utf-8') as f:
        json.dump(performance_report, f, indent=2, ensure_ascii=False)
    
    print("\n性能报告已保存到 performance_report.json")
    print("\n所有实际应用演示已完成！")
    print("输出解析器已成功应用于：")
    print("- 电商系统（订单处理、评论分析）")
    print("- 会议调度系统（会议安排、可用性查询）")
    print("- 财务系统（费用分析、数据提取）")
    print("- 健康系统（健康报告、症状分析）")
    print("- 教育系统（学习计划、作业评估）")
    print("- 验证系统（用户注册、API响应验证）")