#!/usr/bin/env python3
"""
Token可视化监控工具
实时监控和分析token使用情况
"""

import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import json
from token_cost_calculator import TokenCostCalculator, TokenCost

class TokenVisualizer:
    """Token使用可视化工具"""
    
    def __init__(self):
        self.calculator = TokenCostCalculator()
        self.usage_history = []
        
    def add_usage_record(self, cost: TokenCost):
        """添加使用记录"""
        self.usage_history.append(cost)
    
    def generate_usage_chart(self, days: int = 7) -> str:
        """生成使用趋势图"""
        
        if not self.usage_history:
            return "无数据"
        
        # 按日期聚合数据
        df = pd.DataFrame([{
            'date': cost.timestamp[:10],
            'cost': cost.total_cost,
            'model': cost.model,
            'input_tokens': cost.input_tokens,
            'output_tokens': cost.output_tokens
        } for cost in self.usage_history])
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Token使用分析', fontsize=16, fontweight='bold')
        
        # 1. 每日成本趋势
        daily_cost = df.groupby('date')['cost'].sum()
        axes[0, 0].plot(daily_cost.index, daily_cost.values, marker='o', linewidth=2)
        axes[0, 0].set_title('每日API成本趋势')
        axes[0, 0].set_ylabel('成本 ($)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. 模型使用分布
        model_usage = df.groupby('model')['cost'].sum()
        axes[0, 1].pie(model_usage.values, labels=model_usage.index, autopct='%1.1f%%')
        axes[0, 1].set_title('模型使用成本分布')
        
        # 3. Token使用模式
        axes[1, 0].scatter(df['input_tokens'], df['output_tokens'], alpha=0.6)
        axes[1, 0].set_xlabel('输入Token')
        axes[1, 0].set_ylabel('输出Token')
        axes[1, 0].set_title('输入输出Token关系')
        
        # 4. 每小时使用分布
        hourly_cost = df.groupby(df['date'].str[11:13])['cost'].sum()
        axes[1, 1].bar(hourly_cost.index, hourly_cost.values)
        axes[1, 1].set_title('每小时使用分布')
        axes[1, 1].set_xlabel('小时')
        axes[1, 1].set_ylabel('成本 ($)')
        
        plt.tight_layout()
        
        # 保存图表
        filename = f"token_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def generate_model_comparison(self, text_samples: List[str]) -> str:
        """生成模型对比图"""
        
        models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        results = []
        
        for text in text_samples:
            for model in models:
                cost = self.calculator.calculate_cost(text, model)
                results.append({
                    'text': text[:30] + "...",
                    'model': model,
                    'cost': cost.total_cost,
                    'input_tokens': cost.input_tokens,
                    'output_tokens': cost.output_tokens
                })
        
        df = pd.DataFrame(results)
        
        # 创建对比图
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # 成本对比
        pivot_cost = df.pivot(index='text', columns='model', values='cost')
        pivot_cost.plot(kind='bar', ax=axes[0])
        axes[0].set_title('不同模型成本对比')
        axes[0].set_ylabel('成本 ($)')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Token效率对比
        pivot_tokens = df.pivot(index='text', columns='model', values='input_tokens')
        pivot_tokens.plot(kind='bar', ax=axes[1])
        axes[1].set_title('不同模型Token效率')
        axes[1].set_ylabel('输入Token数量')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        filename = f"model_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def generate_efficiency_report(self) -> Dict:
        """生成效率报告"""
        
        if not self.usage_history:
            return {"error": "无数据"}
        
        df = pd.DataFrame([{
            'timestamp': cost.timestamp,
            'cost': cost.total_cost,
            'model': cost.model,
            'input_tokens': cost.input_tokens,
            'output_tokens': cost.output_tokens,
            'efficiency': cost.output_tokens / max(cost.input_tokens, 1)
        } for cost in self.usage_history])
        
        report = {
            "总成本": df['cost'].sum(),
            "平均每次成本": df['cost'].mean(),
            "最高单次成本": df['cost'].max(),
            "总Token数": df['input_tokens'].sum() + df['output_tokens'].sum(),
            "平均效率": df['efficiency'].mean(),
            "最常用模型": df['model'].mode().iloc[0] if not df.empty else None,
            "成本趋势": "上升" if df['cost'].iloc[-5:].mean() > df['cost'].iloc[:-5].mean() else "下降",
            "优化建议": self._generate_efficiency_suggestions(df)
        }
        
        return report
    
    def _generate_efficiency_suggestions(self, df: pd.DataFrame) -> List[str]:
        """生成效率优化建议"""
        
        suggestions = []
        
        # 分析高成本请求
        high_cost_threshold = df['cost'].quantile(0.8)
        high_cost_count = len(df[df['cost'] > high_cost_threshold])
        
        if high_cost_count > len(df) * 0.2:
            suggestions.append("高成本请求比例过高，建议优化提示词")
        
        # 分析模型选择
        gpt4_usage = len(df[df['model'].str.contains('gpt-4')])
        total_usage = len(df)
        
        if gpt4_usage > total_usage * 0.5:
            suggestions.append("GPT-4使用比例过高，考虑使用GPT-3.5-turbo")
        
        # 分析效率
        low_efficiency = df[df['efficiency'] < 0.5]
        if len(low_efficiency) > len(df) * 0.3:
            suggestions.append("输出效率较低，建议简化提示词")
        
        return suggestions

class RealTimeTokenMonitor:
    """实时Token监控器"""
    
    def __init__(self, alert_threshold: float = 5.0):
        self.alert_threshold = alert_threshold
        self.current_usage = 0.0
        self.session_start = datetime.now()
        self.calculator = TokenCostCalculator()
    
    def track_request(self, text: str, model: str) -> Dict:
        """跟踪单次请求"""
        
        cost = self.calculator.calculate_cost(text, model)
        self.current_usage += cost.total_cost
        
        elapsed = (datetime.now() - self.session_start).total_seconds() / 3600
        hourly_rate = self.current_usage / max(elapsed, 0.001)
        
        alert = self.current_usage > self.alert_threshold
        
        return {
            "request_cost": cost.total_cost,
            "session_total": self.current_usage,
            "hourly_rate": hourly_rate,
            "alert": alert,
            "remaining_budget": max(self.alert_threshold - self.current_usage, 0),
            "estimated_remaining_time": (self.alert_threshold - self.current_usage) / max(hourly_rate, 0.001)
        }
    
    def reset_session(self):
        """重置会话"""
        self.current_usage = 0.0
        self.session_start = datetime.now()
    
    def get_session_summary(self) -> Dict:
        """获取会话摘要"""
        
        elapsed = (datetime.now() - self.session_start).total_seconds()
        
        return {
            "session_duration": str(timedelta(seconds=elapsed)),
            "total_cost": self.current_usage,
            "average_cost_per_minute": (self.current_usage * 60) / max(elapsed, 1),
            "budget_utilization": (self.current_usage / self.alert_threshold) * 100
        }

# 实际应用示例
if __name__ == "__main__":
    # 初始化工具
    visualizer = TokenVisualizer()
    monitor = RealTimeTokenMonitor(alert_threshold=1.0)
    
    # 模拟一些使用数据
    sample_texts = [
        "请解释什么是机器学习",
        "写一个Python函数来计算斐波那契数列",
        "分析当前市场趋势并提供投资建议",
        "翻译这段中文到英文",
        "生成一个关于人工智能的简短故事"
    ]
    
    print("=== Token使用监控示例 ===")
    
    for i, text in enumerate(sample_texts):
        # 模拟请求
        result = monitor.track_request(text, "gpt-3.5-turbo")
        
        print(f"\n请求 {i+1}: {text}")
        print(f"本次成本: ${result['request_cost']:.4f}")
        print(f"累计成本: ${result['session_total']:.4f}")
        
        if result['alert']:
            print("⚠️  预算警告：已接近预算上限")
        
        # 添加到可视化历史
        cost = visualizer.calculator.calculate_cost(text, "gpt-3.5-turbo")
        visualizer.add_usage_record(cost)
    
    # 生成报告
    report = visualizer.generate_efficiency_report()
    print(f"\n=== 效率报告 ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 会话摘要
    summary = monitor.get_session_summary()
    print(f"\n=== 会话摘要 ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))