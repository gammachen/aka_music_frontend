#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PartialPromptTemplate与自定义模板测试脚本
简化版本 - 无需外部依赖
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# 简化版的PartialPromptTemplate实现
class SimplePartialPromptTemplate:
    """简化的部分提示词模板"""
    
    def __init__(self, template: str, input_variables: List[str]):
        self.template = template
        self.input_variables = input_variables
        self.partial_variables = {}
    
    def partial(self, **kwargs) -> 'SimplePartialPromptTemplate':
        """部分填充变量"""
        new_template = SimplePartialPromptTemplate(self.template, self.input_variables)
        new_template.partial_variables = {**self.partial_variables, **kwargs}
        return new_template
    
    def format(self, **kwargs) -> str:
        """格式化模板"""
        all_vars = {**self.partial_variables, **kwargs}
        
        # 简单的字符串替换
        result = self.template
        for key, value in all_vars.items():
            result = result.replace(f"{{{key}}}", str(value))
        
        return result
    
    def get_remaining_variables(self) -> List[str]:
        """获取剩余需要填充的变量"""
        filled_vars = set(self.partial_variables.keys())
        return [var for var in self.input_variables if var not in filled_vars]

class SimpleMultiLanguageTemplate:
    """简化的多语言模板"""
    
    def __init__(self, translations: Dict[str, str]):
        self.translations = translations
    
    def format(self, language: str, **kwargs) -> str:
        """根据语言格式化模板"""
        if language not in self.translations:
            language = "en"  # 默认英语
        
        template = self.translations[language]
        
        # 简单的字符串替换
        result = template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        
        return result

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results = []
    
    async def test_partial_templates(self):
        """测试部分模板功能"""
        print("=== 测试部分模板功能 ===")
        
        # 创建部分模板
        base = SimplePartialPromptTemplate(
            template="系统：{system}\n用户：{user}\n助手：{assistant}",
            input_variables=["system", "user", "assistant"]
        )
        
        # 链式部分填充
        step1 = base.partial(system="你是一个友好的助手")
        step2 = step1.partial(user="你好")
        
        # 最终填充
        result = step2.format(assistant="你好！很高兴为您服务")
        
        print(f"基础模板: {base.template}")
        print(f"步骤1部分填充: {step1.get_remaining_variables()}")
        print(f"步骤2部分填充: {step2.get_remaining_variables()}")
        print(f"最终结果: {result}")
        
        return {
            "test": "partial_templates",
            "result": result,
            "remaining_vars": step2.get_remaining_variables()
        }
    
    async def test_multilingual_templates(self):
        """测试多语言模板"""
        print("\n=== 测试多语言模板 ===")
        
        welcome_template = SimpleMultiLanguageTemplate({
            "zh": "你好 {name}，欢迎来到我们的平台！",
            "en": "Hello {name}, welcome to our platform!",
            "ja": "こんにちは {name}さん、私たちのプラットフォームへようこそ！"
        })
        
        results = {}
        for lang in ["zh", "en", "ja"]:
            result = welcome_template.format(language=lang, name="用户")
            results[lang] = result
            print(f"{lang}: {result}")
        
        return {
            "test": "multilingual",
            "results": results
        }
    
    async def test_customer_service_bot(self):
        """测试客服机器人"""
        print("\n=== 测试客服机器人 ===")
        
        # 客服模板
        greeting_template = SimplePartialPromptTemplate(
            template="你好 {customer_name}！我是客服助手。您的问题是：{question}",
            input_variables=["customer_name", "question"]
        )
        
        # 响应模板
        response_template = SimplePartialPromptTemplate(
            template="关于您的问题\"{question}\"，{response}",
            input_variables=["question", "response"]
        )
        
        # 模拟客服交互
        customer_name = "小明"
        question = "我的订单什么时候能收到？"
        
        greeting = greeting_template.format(customer_name=customer_name, question=question)
        response = response_template.format(
            question=question,
            response="您的订单预计3-5个工作日内送达。"
        )
        
        print(f"问候: {greeting}")
        print(f"回复: {response}")
        
        return {
            "test": "customer_service",
            "greeting": greeting,
            "response": response
        }
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("开始运行PartialPromptTemplate与自定义模板测试...\n")
        
        tests = [
            self.test_partial_templates,
            self.test_multilingual_templates,
            self.test_customer_service_bot
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                print(f"测试 {test.__name__} 失败: {e}")
                results.append({"test": test.__name__, "error": str(e)})
        
        # 保存结果
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "results": results
        }
        
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 测试完成 ===")
        print(f"总测试数: {len(results)}")
        print(f"结果已保存到 test_results.json")
        
        return output


async def main():
    """主函数"""
    runner = TestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())