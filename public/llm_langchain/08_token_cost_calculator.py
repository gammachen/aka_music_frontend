#!/usr/bin/env python3
"""
Token成本计算与优化工具
提供精确的API调用成本估算和优化建议
"""

import tiktoken
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class TokenCost:
    """Token成本数据结构"""
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    timestamp: str

class TokenCostCalculator:
    """高级Token成本计算器"""
    
    def __init__(self):
        self.pricing = {
            "gpt-3.5-turbo": {
                "input": 0.0015,
                "output": 0.002,
                "context_window": 4096
            },
            "gpt-3.5-turbo-16k": {
                "input": 0.003,
                "output": 0.004,
                "context_window": 16384
            },
            "gpt-4": {
                "input": 0.03,
                "output": 0.06,
                "context_window": 8192
            },
            "gpt-4-turbo": {
                "input": 0.01,
                "output": 0.03,
                "context_window": 128000
            },
            "gpt-4-32k": {
                "input": 0.06,
                "output": 0.12,
                "context_window": 32768
            }
        }
    
    def calculate_cost(self, text: str, model: str, 
                      estimated_output_ratio: float = 0.5) -> TokenCost:
        """计算文本处理成本"""
        
        if model not in self.pricing:
            raise ValueError(f"不支持的模型: {model}")
        
        encoding = tiktoken.encoding_for_model(model)
        input_tokens = len(encoding.encode(text))
        output_tokens = int(input_tokens * estimated_output_ratio)
        
        pricing = self.pricing[model]
        input_cost = (input_tokens * pricing["input"]) / 1000
        output_cost = (output_tokens * pricing["output"]) / 1000
        
        return TokenCost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
            timestamp=datetime.now().isoformat()
        )
    
    def analyze_conversation(self, messages: List[Dict[str, str]], 
                           model: str) -> Dict:
        """分析对话成本"""
        
        encoding = tiktoken.encoding_for_model(model)
        
        total_input_tokens = 0
        total_output_tokens = 0
        
        # 计算输入token
        for message in messages:
            if message.get("role") in ["user", "system"]:
                total_input_tokens += len(encoding.encode(message.get("content", "")))
            elif message.get("role") == "assistant":
                total_output_tokens += len(encoding.encode(message.get("content", "")))
        
        cost = self.calculate_cost_from_tokens(total_input_tokens, total_output_tokens, model)
        
        return {
            "conversation_cost": cost,
            "message_count": len(messages),
            "average_cost_per_message": cost.total_cost / len(messages),
            "context_usage_ratio": total_input_tokens / self.pricing[model]["context_window"]
        }
    
    def calculate_cost_from_tokens(self, input_tokens: int, 
                                 output_tokens: int, model: str) -> TokenCost:
        """从token数量计算成本"""
        
        if model not in self.pricing:
            raise ValueError(f"不支持的模型: {model}")
        
        pricing = self.pricing[model]
        input_cost = (input_tokens * pricing["input"]) / 1000
        output_cost = (output_tokens * pricing["output"]) / 1000
        
        return TokenCost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
            timestamp=datetime.now().isoformat()
        )

class TokenOptimizer:
    """Token优化工具"""
    
    def __init__(self):
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.optimization_rules = {
            "remove_redundant_words": ["实际上", "基本上", "事实上", "简单来说"],
            "shorten_phrases": {
                "人工智能": "AI",
                "机器学习": "ML",
                "深度学习": "DL",
                "大型语言模型": "LLM",
                "自然语言处理": "NLP"
            },
            "eliminate_filler": ["嗯", "啊", "那个", "就是说"]
        }
    
    def optimize_text(self, text: str) -> Dict:
        """优化文本减少token使用"""
        
        original_tokens = len(self.encoding.encode(text))
        original_length = len(text)
        
        # 应用优化规则
        optimized_text = text
        
        # 替换长短语
        for long_phrase, short_phrase in self.optimization_rules["shorten_phrases"].items():
            optimized_text = optimized_text.replace(long_phrase, short_phrase)
        
        # 移除冗余词
        for redundant in self.optimization_rules["remove_redundant_words"]:
            optimized_text = optimized_text.replace(redundant, "")
        
        # 移除填充词
        for filler in self.optimization_rules["eliminate_filler"]:
            optimized_text = optimized_text.replace(filler, "")
        
        optimized_tokens = len(self.encoding.encode(optimized_text))
        
        return {
            "original_text": text,
            "optimized_text": optimized_text,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "token_reduction": original_tokens - optimized_tokens,
            "reduction_percentage": ((original_tokens - optimized_tokens) / original_tokens) * 100,
            "character_reduction": original_length - len(optimized_text)
        }
    
    def generate_summary_tokens(self, text: str, max_tokens: int) -> str:
        """生成指定token数量的摘要"""
        
        encoding = self.encoding
        tokens = encoding.encode(text)
        
        if len(tokens) <= max_tokens:
            return text
        
        # 保留开头和结尾
        half_tokens = max_tokens // 2
        selected_tokens = tokens[:half_tokens] + tokens[-half_tokens:]
        
        return encoding.decode(selected_tokens)

class TokenBudgetManager:
    """Token预算管理器"""
    
    def __init__(self, daily_budget: float = 10.0):
        self.daily_budget = daily_budget
        self.daily_usage = []
        self.calculator = TokenCostCalculator()
    
    def track_usage(self, cost: TokenCost):
        """记录token使用情况"""
        self.daily_usage.append(cost)
    
    def get_daily_summary(self) -> Dict:
        """获取每日使用摘要"""
        
        if not self.daily_usage:
            return {"total_cost": 0, "remaining_budget": self.daily_budget}
        
        total_cost = sum(cost.total_cost for cost in self.daily_usage)
        remaining_budget = self.daily_budget - total_cost
        
        model_usage = {}
        for cost in self.daily_usage:
            if cost.model not in model_usage:
                model_usage[cost.model] = {"count": 0, "cost": 0}
            model_usage[cost.model]["count"] += 1
            model_usage[cost.model]["cost"] += cost.total_cost
        
        return {
            "total_cost": total_cost,
            "remaining_budget": remaining_budget,
            "usage_percentage": (total_cost / self.daily_budget) * 100,
            "model_usage": model_usage,
            "recommendations": self._generate_recommendations(total_cost)
        }
    
    def _generate_recommendations(self, current_cost: float) -> List[str]:
        """生成使用建议"""
        recommendations = []
        
        usage_percentage = (current_cost / self.daily_budget) * 100
        
        if usage_percentage > 80:
            recommendations.append("预算即将耗尽，建议使用更经济的模型")
            recommendations.append("考虑使用gpt-3.5-turbo替代gpt-4")
            recommendations.append("优化提示词减少token使用")
        elif usage_percentage > 50:
            recommendations.append("预算使用过半，建议监控后续使用")
        else:
            recommendations.append("预算充足，可正常使用")
        
        return recommendations

# 实际应用示例
if __name__ == "__main__":
    # 初始化工具
    calculator = TokenCostCalculator()
    optimizer = TokenOptimizer()
    budget_manager = TokenBudgetManager(daily_budget=5.0)
    
    # 测试文本
    test_texts = [
        "人工智能正在通过机器学习和深度学习技术改变我们的世界。",
        "AI is revolutionizing the world through machine learning and deep learning technologies.",
        "请详细解释什么是自然语言处理以及它在现代AI系统中的应用场景。"
    ]
    
    print("=== Token成本分析 ===")
    
    for text in test_texts:
        # 计算成本
        cost = calculator.calculate_cost(text, "gpt-3.5-turbo")
        
        # 优化文本
        optimization = optimizer.optimize_text(text)
        
        # 计算优化后成本
        optimized_cost = calculator.calculate_cost(
            optimization["optimized_text"], 
            "gpt-3.5-turbo"
        )
        
        print(f"\n原文: {text[:50]}...")
        print(f"原始token: {cost.input_tokens}, 成本: ${cost.total_cost:.4f}")
        print(f"优化后token: {optimized_cost.input_tokens}, 成本: ${optimized_cost.total_cost:.4f}")
        print(f"节省: {optimization['reduction_percentage']:.1f}%")
        
        # 记录预算使用
        budget_manager.track_usage(cost)
    
    # 生成每日报告
    summary = budget_manager.get_daily_summary()
    print(f"\n=== 每日预算报告 ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))