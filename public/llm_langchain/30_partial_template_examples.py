"""
PartialPromptTemplate与自定义模板实际应用示例
展示在真实项目中的使用场景和最佳实践
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from partial_and_custom_templates import (
    PartialPromptTemplate,
    FunctionCallTemplate,
    ChainOfThoughtTemplate,
    MultiLanguageTemplate,
    AdaptiveTemplate,
    TemplateRegistry,
    DynamicTemplateEngine,
    AdvancedTemplateFactory,
    TemplateComposer
)


class CustomerServiceBot:
    """客服机器人 - 使用PartialPromptTemplate实现动态对话"""
    
    def __init__(self):
        self.registry = TemplateRegistry()
        self._setup_templates()
        self.conversation_history = []
    
    def _setup_templates(self):
        """设置客服模板"""
        
        # 基础问候模板
        greeting_template = PartialPromptTemplate(
            template="你好 {name}！我是客服助手，很高兴为您服务。请问有什么可以帮助您的？",
            input_variables=["name"]
        )
        
        # 问题分类模板
        classification_template = ChainOfThoughtTemplate(
            problem_statement="用户问题：{user_question}",
            steps=[
                "分析用户问题的类型：{question}",
                "判断问题紧急程度：{urgency}",
                "确定处理优先级：{priority}",
                "分配相应的解决方案：{solution_type}"
            ]
        )
        
        # 解决方案模板
        solution_template = AdaptiveTemplate(
            base_template="""
针对您的问题：{question}

问题分析：
- 问题类型：{problem_type}
- 紧急程度：{urgency_level}
- 预计解决时间：{estimated_time}

解决方案：
{solution_details}

后续跟进：{follow_up_action}
            """,
            adaptations={
                "urgency_level": lambda urgency, ctx: {
                    "low": "低优先级",
                    "medium": "中等优先级", 
                    "high": "高优先级",
                    "critical": "紧急处理"
                }.get(urgency, "中等优先级"),
                "estimated_time": lambda time, ctx: f"约{time}分钟" if time.isdigit() else time
            }
        )
        
        # 注册模板
        self.registry.register("greeting", greeting_template, "greeting", ["welcome", "customer_service"])
        self.registry.register("classification", classification_template, "analysis", ["problem_analysis"])
        self.registry.register("solution", solution_template, "solution", ["problem_solving"])
    
    async def handle_customer(self, user_name: str, user_question: str) -> Dict[str, Any]:
        """处理客户问题"""
        
        # 生成问候
        greeting = self.registry.format_template("greeting", name=user_name)
        
        # 问题分类
        classification = self.registry.format_template(
            "classification",
            user_question=user_question,
            question=user_question,
            urgency=self._analyze_urgency(user_question),
            priority=self._determine_priority(user_question),
            solution_type=self._determine_solution_type(user_question)
        )
        
        # 生成解决方案
        solution = self.registry.format_template(
            "solution",
            question=user_question,
            problem_type=self._classify_problem(user_question),
            urgency=self._analyze_urgency(user_question),
            estimated_time=self._estimate_time(user_question),
            solution_details=self._generate_solution(user_question),
            follow_up_action=self._determine_follow_up(user_question)
        )
        
        # 记录对话
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_name,
            "question": user_question,
            "response": {
                "greeting": greeting,
                "classification": classification,
                "solution": solution
            }
        })
        
        return {
            "greeting": greeting,
            "analysis": classification,
            "solution": solution,
            "conversation_id": len(self.conversation_history)
        }
    
    def _analyze_urgency(self, question: str) -> str:
        """分析问题紧急程度"""
        urgent_keywords = ["紧急", "立即", "马上", "重要", "严重", "崩溃"]
        for keyword in urgent_keywords:
            if keyword in question:
                return "high"
        return "medium"
    
    def _determine_priority(self, question: str) -> str:
        """确定处理优先级"""
        return "P1" if self._analyze_urgency(question) == "high" else "P2"
    
    def _determine_solution_type(self, question: str) -> str:
        """确定解决方案类型"""
        if "退款" in question:
            return "refund"
        elif "技术" in question:
            return "technical"
        elif "账户" in question:
            return "account"
        else:
            return "general"
    
    def _classify_problem(self, question: str) -> str:
        """问题分类"""
        return self._determine_solution_type(question)
    
    def _estimate_time(self, question: str) -> str:
        """估计解决时间"""
        problem_type = self._classify_problem(question)
        time_map = {
            "refund": "30",
            "technical": "60",
            "account": "15",
            "general": "10"
        }
        return time_map.get(problem_type, "30")
    
    def _generate_solution(self, question: str) -> str:
        """生成解决方案"""
        return "我们将立即处理您的问题，并为您提供详细的解决方案。"
    
    def _determine_follow_up(self, question: str) -> str:
        """确定后续跟进"""
        return "我们将在24小时内通过电话或邮件与您联系，确认问题是否已解决。"


class CodeGenerationAssistant:
    """代码生成助手 - 使用动态模板和思维链"""
    
    def __init__(self):
        self.engine = DynamicTemplateEngine()
        self._setup_custom_filters()
        self.template_composer = TemplateComposer()
        self._build_code_templates()
    
    def _setup_custom_filters(self):
        """设置自定义过滤器"""
        self.engine.add_filter('indent', lambda text, spaces=4: 
                             '\n'.join(' ' * spaces + line for line in text.split('\n')))
        self.engine.add_filter('add_docstring', lambda code, description: 
                             f'"""{description}"""\n\n{code}')
        self.engine.add_filter('add_type_hints', lambda func_def: 
                             func_def.replace('def ', 'def ') + ' -> None')
    
    def _build_code_templates(self):
        """构建代码模板"""
        
        # 函数定义模板
        function_template = PartialPromptTemplate(
            template="""def {function_name}({parameters}):
    \"\"\"
    {description}
    
    Args:
        {args_description}
        
    Returns:
        {return_description}
    \"\"\"
    {implementation}
""",
            input_variables=[
                "function_name", "parameters", "description", 
                "args_description", "return_description", "implementation"
            ]
        )
        
        # 类定义模板
        class_template = AdaptiveTemplate(
            base_template="""class {class_name}({base_classes}):
    \"\"\"
    {class_description}
    \"\"\"
    
    {attributes}
    
    {methods}
""",
            adaptations={
                "base_classes": lambda bases, ctx: ", ".join(bases) if isinstance(bases, list) else str(bases),
                "attributes": lambda attrs, ctx: "\n    ".join(attrs) if isinstance(attrs, list) else str(attrs),
                "methods": lambda methods, ctx: "\n\n    ".join(methods) if isinstance(methods, list) else str(methods)
            }
        )
        
        # 注册到组合器
        self.template_composer.register_template("function", function_template)
        self.template_composer.register_template("class", class_template)
    
    async def generate_function(self, spec: Dict[str, Any]) -> str:
        """生成函数代码"""
        
        # 使用思维链模板进行代码规划
        planning_template = ChainOfThoughtTemplate(
            problem_statement="需要生成一个{function_name}函数",
            steps=[
                "分析函数需求：{requirements}",
                "确定参数设计：{parameters}",
                "规划实现逻辑：{logic}",
                "考虑边界条件：{edge_cases}",
                "生成完整代码：{final_implementation}"
            ]
        )
        
        # 生成规划
        planning = planning_template.format(
            function_name=spec["name"],
            requirements=spec.get("requirements", "实现基本功能"),
            parameters=spec.get("parameters", ""),
            logic=spec.get("logic", "标准实现"),
            edge_cases=spec.get("edge_cases", "处理异常情况"),
            final_implementation="待生成"
        )
        
        # 使用函数模板生成代码
        function_template = self.template_composer.compose(["function"])
        code = function_template.format(**spec)
        
        return {
            "planning": planning,
            "code": code,
            "generated_at": datetime.now().isoformat()
        }
    
    async def generate_class(self, spec: Dict[str, Any]) -> str:
        """生成类代码"""
        
        # 使用动态模板引擎生成复杂类
        template = """class {class_name}({base_classes}):
    \"\"\"{class_description}\"\"\"
    
    def __init__(self, {init_params}):
{init_body}
    
    def __str__(self):
        return f"{class_name}({{self}})"
"""
        
        base_classes_str = ", ".join(spec.get("base_classes", ["object"]))
        init_params = spec.get("init_params", "**kwargs")
        init_body = spec.get("init_body", "        pass")
        
        result = template.format(
            class_name=spec["class_name"],
            base_classes=base_classes_str,
            class_description=spec.get("class_description", f"{spec['class_name']} class"),
            init_params=init_params,
            init_body=init_body
        )
        
        return {
            "code": result,
            "class_name": spec["class_name"],
            "generated_at": datetime.now().isoformat()
        }


class MultiLanguageSupport:
    """多语言支持系统 - 使用多语言模板"""
    
    def __init__(self):
        self.templates = {}
        self._setup_multilingual_templates()

    def _setup_multilingual_templates(self):
        """设置多语言模板"""

        # 用户界面模板
        self.welcome_templates = MultiLanguageTemplate({
            "zh": "欢迎 {username}！",
            "en": "Welcome {username}!",
            "ja": "{username}さん、ようこそ！"
        })
        
        self.loading_templates = MultiLanguageTemplate({
            "zh": "正在加载 {content}...",
            "en": "Loading {content}...",
            "ja": "{content}を読み込んでいます..."
        })
        
        self.error_templates = MultiLanguageTemplate({
            "zh": "发生错误：{error_message}",
            "en": "An error occurred: {error_message}",
            "ja": "エラーが発生しました：{error_message}"
        })
        
        self.success_templates = MultiLanguageTemplate({
            "zh": "操作成功完成！",
            "en": "Operation completed successfully!",
            "ja": "操作が正常に完了しました！"
        })
        
        self.notification_templates = MultiLanguageTemplate({
            "zh": "【{app_name}】{notification_type}通知",
            "en": "[{app_name}] {notification_type} Notification"
        })
    
    def _setup_multilingual_templates(self):
        """设置多语言模板"""
        
        # 用户界面模板
        self.welcome_templates = MultiLanguageTemplate({
            "zh": "欢迎 {username}！",
            "en": "Welcome {username}!",
            "ja": "{username}さん、ようこそ！"
        })
        
        self.loading_templates = MultiLanguageTemplate({
            "zh": "正在加载 {content}...",
            "en": "Loading {content}...",
            "ja": "{content}を読み込んでいます..."
        })
        
        self.error_templates = MultiLanguageTemplate({
            "zh": "发生错误：{error_message}",
            "en": "An error occurred: {error_message}",
            "ja": "エラーが発生しました：{error_message}"
        })
        
        self.success_templates = MultiLanguageTemplate({
            "zh": "操作成功完成！",
            "en": "Operation completed successfully!",
            "ja": "操作が正常に完了しました！"
        })
        
        self.notification_templates = MultiLanguageTemplate({
            "zh": "【{app_name}】{notification_type}通知",
            "en": "[{app_name}] {notification_type} Notification"
        })
    
    def get_ui_message(self, message_type: str, language: str, **kwargs) -> str:
        """获取UI消息"""
        template_map = {
            "welcome": self.welcome_templates,
            "loading": self.loading_templates,
            "error": self.error_templates,
            "success": self.success_templates
        }
        
        template = template_map.get(message_type)
        if template:
            return template.format(language=language, **kwargs)
        return f"Message not found: {message_type}"

    def get_notification_message(self, channel: str, language: str, **kwargs) -> str:
        """获取通知消息"""
        return self.notification_templates.format(language=language, **kwargs)


class TemplateTestingSuite:
    """模板测试套件"""
    
    def __init__(self):
        self.test_results = []
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        
        tests = [
            self.test_customer_service_bot,
            self.test_code_generation,
            self.test_multilingual_support,
            self.test_partial_templates,
            self.test_performance
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append({"test": test.__name__, "status": "passed", "result": result})
            except Exception as e:
                results.append({"test": test.__name__, "status": "failed", "error": str(e)})
        
        return {
            "total_tests": len(results),
            "passed": len([r for r in results if r["status"] == "passed"]),
            "failed": len([r for r in results if r["status"] == "failed"]),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def test_customer_service_bot(self) -> Dict[str, Any]:
        """测试客服机器人"""
        bot = CustomerServiceBot()
        
        test_cases = [
            {"name": "张三", "question": "我的订单什么时候发货？"},
            {"name": "李四", "question": "紧急：我的账户被锁定了！"},
            {"name": "王五", "question": "如何申请退款？"}
        ]
        
        results = []
        for case in test_cases:
            result = await bot.handle_customer(case["name"], case["question"])
            results.append(result)
        
        return {
            "test_type": "customer_service",
            "test_cases": len(test_cases),
            "results": results
        }
    
    async def test_code_generation(self) -> Dict[str, Any]:
        """测试代码生成"""
        assistant = CodeGenerationAssistant()
        
        spec = {
            "name": "calculate_fibonacci",
            "parameters": "n: int",
            "description": "计算斐波那契数列的第n个数",
            "args_description": "n: 要计算的斐波那契数的位置",
            "return_description": "第n个斐波那契数",
            "implementation": """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
            """
        }
        
        result = await assistant.generate_function(spec)
        
        return {
            "test_type": "code_generation",
            "function_name": spec["name"],
            "code_generated": bool(result["code"])
        }
    
    async def test_multilingual_support(self) -> Dict[str, Any]:
        """测试多语言支持"""
        support = MultiLanguageSupport()
        
        languages = ["zh", "en", "ja"]
        
        results = []
        for lang in languages:
            # 测试欢迎消息
            welcome = support.get_ui_message("welcome", lang, username="测试用户")
            
            # 测试加载消息
            loading = support.get_ui_message("loading", lang, content="系统数据")
            
            # 测试通知消息
            notification = support.get_notification_message(
                "email", lang, app_name="TestApp", notification_type="系统"
            )
            
            results.append({
                "language": lang,
                "welcome": welcome,
                "loading": loading,
                "notification": notification
            })
        
        return {
            "test_type": "multilingual",
            "languages_tested": languages,
            "messages_generated": len(results),
            "results": results
        }
    
    async def test_partial_templates(self) -> Dict[str, Any]:
        """测试部分模板"""
        
        # 创建部分模板链
        base = PartialPromptTemplate(
            template="系统：{system}\n用户：{user}\n助手：{assistant}",
            input_variables=["system", "user", "assistant"]
        )
        
        # 链式部分填充
        step1 = base.partial(system="你是一个友好的助手")
        step2 = step1.partial(user="你好")
        
        # 最终填充
        result = step2.format(assistant="你好！很高兴为您服务")
        
        return {
            "test_type": "partial_templates",
            "chain_length": 3,
            "final_result": result,
            "remaining_variables": step2.get_remaining_variables()
        }
    
    async def test_performance(self) -> Dict[str, Any]:
        """测试性能"""
        import time
        
        # 测试模板渲染性能
        template = PartialPromptTemplate(
            template="测试消息：{message}，时间：{timestamp}",
            input_variables=["message", "timestamp"]
        )
        
        start_time = time.time()
        
        # 批量渲染
        results = []
        for i in range(1000):
            result = template.format(
                message=f"测试消息{i}",
                timestamp=datetime.now().isoformat()
            )
            results.append(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "test_type": "performance",
            "iterations": 1000,
            "total_time": duration,
            "average_time_per_render": duration / 1000,
            "renders_per_second": 1000 / duration
        }


async def main():
    """主函数 - 运行所有示例"""
    
    print("=== PartialPromptTemplate与自定义模板示例 ===\n")
    
    # 1. 客服机器人示例
    print("1. 客服机器人示例")
    bot = CustomerServiceBot()
    customer_result = await bot.handle_customer("小明", "我的订单什么时候能收到？")
    print(f"客服响应: {json.dumps(customer_result, ensure_ascii=False, indent=2)}")
    
    # 2. 代码生成助手示例
    print("\n2. 代码生成助手示例")
    code_assistant = CodeGenerationAssistant()
    code_spec = {
        "name": "process_user_data",
        "parameters": "users: List[Dict[str, Any]]",
        "description": "处理用户数据并返回统计信息",
        "args_description": "users: 用户数据列表",
        "return_description": "包含统计信息的字典",
        "implementation": """
    stats = {
        "total_users": len(users),
        "active_users": sum(1 for u in users if u.get("is_active", False)),
        "average_age": sum(u.get("age", 0) for u in users) / len(users) if users else 0
    }
    return stats
        """
    }
    
    code_result = await code_assistant.generate_function(code_spec)
    print(f"代码生成结果:\n{code_result['code']}")
    
    # 3. 多语言支持示例
    print("\n3. 多语言支持示例")
    multilang = MultiLanguageSupport()
    for lang in ["zh", "en", "ja"]:
        welcome = multilang.get_ui_message("welcome", lang, username="国际用户")
        print(f"{lang}: {welcome}")
    
    # 4. 运行测试套件
    print("\n4. 运行测试套件")
    test_suite = TemplateTestingSuite()
    test_results = await test_suite.run_all_tests()
    
    print(f"测试总结:")
    print(f"- 总测试数: {test_results['total_tests']}")
    print(f"- 通过测试: {test_results['passed']}")
    print(f"- 失败测试: {test_results['failed']}")
    print(f"- 测试时间: {test_results['timestamp']}")
    
    # 5. 保存示例结果
    print("\n5. 保存示例结果")
    
    example_results = {
        "customer_service": customer_result,
        "code_generation": code_result,
        "multilingual_examples": {
            lang: multilang.get_ui_message("welcome", lang, username="示例用户")
            for lang in ["zh", "en", "ja"]
        },
        "test_results": test_results
    }
    
    with open("partial_template_examples_results.json", "w", encoding="utf-8") as f:
        json.dump(example_results, f, ensure_ascii=False, indent=2)
    
    print("示例结果已保存到 partial_template_examples_results.json")


if __name__ == "__main__":
    asyncio.run(main())