"""
LangChain ExampleSelector 实际使用指南
包含真实场景下的代码示例和最佳实践
"""

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class SelectorType(Enum):
    """选择器类型枚举"""
    SEMANTIC = "semantic"
    LENGTH = "length"
    DIVERSITY = "diversity"
    KEYWORD = "keyword"
    HYBRID = "hybrid"

@dataclass
class Example:
    """示例数据结构"""
    input: str
    output: str
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "input": self.input,
            "output": self.output,
            "metadata": self.metadata or {}
        }

class RealWorldExampleSelector:
    """真实场景示例选择器"""
    
    def __init__(self):
        self.examples = []
        self.cache = {}
    
    def load_examples(self, examples: List[Example]) -> None:
        """加载示例数据"""
        self.examples = examples
        self.cache = {}
    
    def semantic_similarity_select(
        self, 
        query: str, 
        max_examples: int = 3
    ) -> List[Example]:
        """基于语义相似度选择"""
        
        if not self.examples:
            return []
        
        # 简单的TF-IDF相似度计算
        query_words = set(query.lower().split())
        scored_examples = []
        
        for example in self.examples:
            example_words = set(example.input.lower().split())
            
            if query_words and example_words:
                intersection = len(query_words.intersection(example_words))
                union = len(query_words.union(example_words))
                similarity = intersection / union
            else:
                similarity = 0.0
            
            scored_examples.append((similarity, example))
        
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [example for _, example in scored_examples[:max_examples]]
    
    def length_optimized_select(
        self, 
        query: str, 
        max_examples: int = 3,
        max_total_length: int = 1000
    ) -> List[Example]:
        """基于长度优化选择"""
        
        query_length = len(query)
        available_length = max_total_length - query_length
        
        # 按长度排序，优先选择短的
        examples_with_length = []
        for example in self.examples:
            example_length = len(example.input) + len(example.output)
            examples_with_length.append((example_length, example))
        
        examples_with_length.sort(key=lambda x: x[0])
        
        selected = []
        total_length = 0
        
        for length, example in examples_with_length:
            if total_length + length <= available_length and len(selected) < max_examples:
                selected.append(example)
                total_length += length
        
        return selected

class CustomerServiceBot:
    """客服机器人示例"""
    
    def __init__(self):
        self.selector = RealWorldExampleSelector()
        self._load_customer_service_examples()
    
    def _load_customer_service_examples(self):
        """加载客服示例"""
        examples = [
            Example(
                "我的订单什么时候发货？",
                "您好！您的订单通常在付款后24-48小时内发货。您可以登录账户查看实时物流信息。",
                {"category": "shipping", "priority": "high"}
            ),
            Example(
                "如何申请退款？",
                "退款流程：1) 进入订单详情 2) 点击申请退款 3) 选择退款原因 4) 提交申请。我们会在1-3个工作日处理。",
                {"category": "refund", "priority": "high"}
            ),
            Example(
                "商品有质量问题怎么办？",
                "非常抱歉！我们提供7天无理由退换货。请拍照联系客服，我们会优先为您处理。",
                {"category": "quality", "priority": "high"}
            ),
            Example(
                "忘记密码怎么重置？",
                "重置密码：1) 点击登录页面的'忘记密码' 2) 输入注册邮箱 3) 接收验证码 4) 设置新密码。",
                {"category": "account", "priority": "medium"}
            ),
            Example(
                "会员积分有什么用？",
                "积分可抵扣现金，100积分=1元。在结算时选择使用积分即可。积分有效期为获得之日起1年。",
                {"category": "membership", "priority": "low"}
            ),
            Example(
                "如何联系人工客服？",
                "人工客服时间：工作日9:00-18:00。您可以在APP内点击'联系客服'，或拨打400-123-4567。",
                {"category": "contact", "priority": "medium"}
            )
        ]
        self.selector.load_examples(examples)
    
    def respond(self, user_input: str, use_semantic: bool = True) -> str:
        """生成客服回复"""
        
        if use_semantic:
            selected_examples = self.selector.semantic_similarity_select(user_input, max_examples=2)
        else:
            selected_examples = self.selector.length_optimized_select(user_input, max_examples=2)
        
        if not selected_examples:
            return "您好！我理解您的问题，让我为您详细解答..."
        
        # 构建上下文
        context = "根据类似问题的处理经验：\n"
        for example in selected_examples:
            context += f"- 用户问：{example.input}\n"
            context += f"- 我们答：{example.output}\n\n"
        
        # 这里可以集成LLM生成回复
        # 简化版本：返回最相似的示例回复
        return selected_examples[0].output

class CodeGenerationAssistant:
    """代码生成助手"""
    
    def __init__(self):
        self.selector = RealWorldExampleSelector()
        self._load_code_examples()
    
    def _load_code_examples(self):
        """加载代码示例"""
        examples = [
            Example(
                "写一个Python函数计算斐波那契数列",
                """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# 测试
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")""",
                {"language": "python", "category": "algorithm", "difficulty": "easy"}
            ),
            Example(
                "创建一个Python类实现栈",
                """class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        return self.items.pop() if self.items else None
    
    def peek(self):
        return self.items[-1] if self.items else None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# 使用示例
stack = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # 输出: 2""",
                {"language": "python", "category": "data_structure", "difficulty": "medium"}
            ),
            Example(
                "实现快速排序算法",
                """def quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# 测试
numbers = [3, 6, 8, 10, 1, 2, 1]
print(quicksort(numbers))  # 输出: [1, 1, 2, 3, 6, 8, 10]""",
                {"language": "python", "category": "algorithm", "difficulty": "hard"}
            ),
            Example(
                "读取CSV文件并分析数据",
                """import pandas as pd
import matplotlib.pyplot as plt

def analyze_csv(filename):
    # 读取CSV文件
    df = pd.read_csv(filename)
    
    # 基本信息
    print("数据形状:", df.shape)
    print("列名:", df.columns.tolist())
    print("缺失值:\n", df.isnull().sum())
    
    # 统计描述
    print("统计描述:\n", df.describe())
    
    # 绘制直方图
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        df[numeric_cols].hist(figsize=(12, 8))
        plt.tight_layout()
        plt.savefig('data_analysis.png')
        plt.show()

# 使用
analyze_csv('data.csv')""",
                {"language": "python", "category": "data_analysis", "difficulty": "medium"}
            )
        ]
        self.selector.load_examples(examples)
    
    def generate_code(self, requirement: str, style: str = "concise") -> str:
        """生成代码"""
        
        if style == "concise":
            selected = self.selector.length_optimized_select(requirement, max_examples=1, max_total_length=500)
        else:
            selected = self.selector.semantic_similarity_select(requirement, max_examples=2)
        
        if not selected:
            return "# 请提供更具体的需求描述"
        
        # 返回最相关的代码示例
        return selected[0].output

class UsageAnalyzer:
    """使用分析器"""
    
    def __init__(self):
        self.usage_stats = []
    
    def analyze_performance(
        self, 
        selector_type: str, 
        test_queries: List[str], 
        examples: List[Example]
    ) -> Dict[str, Any]:
        """分析选择器性能"""
        
        selector = RealWorldExampleSelector()
        selector.load_examples(examples)
        
        results = {
            "selector_type": selector_type,
            "total_queries": len(test_queries),
            "average_latency": 0.0,
            "examples_used": set(),
            "query_examples": []
        }
        
        total_time = 0
        
        for query in test_queries:
            start_time = time.time()
            
            if selector_type == "semantic":
                selected = selector.semantic_similarity_select(query)
            elif selector_type == "length":
                selected = selector.length_optimized_select(query)
            else:
                selected = selector.semantic_similarity_select(query)
            
            latency = time.time() - start_time
            total_time += latency
            
            for example in selected:
                results["examples_used"].add(example.input)
            
            results["query_examples"].append({
                "query": query,
                "selected_count": len(selected),
                "latency": latency,
                "examples": [ex.input for ex in selected]
            })
        
        results["average_latency"] = total_time / len(test_queries)
        results["unique_examples_used"] = len(results["examples_used"])
        
        return results

def main():
    """主函数演示"""
    
    print("=== LangChain ExampleSelector 实际使用演示 ===\n")
    
    # 1. 客服机器人演示
    print("1. 客服机器人示例")
    print("-" * 50)
    
    bot = CustomerServiceBot()
    
    test_queries = [
        "我的快递什么时候到？",
        "如何退货？",
        "商品有问题怎么办？",
        "忘记密码了"
    ]
    
    for query in test_queries:
        response = bot.respond(query)
        print(f"用户：{query}")
        print(f"客服：{response}")
        print()
    
    # 2. 代码生成演示
    print("2. 代码生成助手示例")
    print("-" * 50)
    
    assistant = CodeGenerationAssistant()
    
    code_queries = [
        "写一个Python函数计算阶乘",
        "实现二叉树遍历",
        "读取JSON文件"
    ]
    
    for query in code_queries:
        code = assistant.generate_code(query)
        print(f"需求：{query}")
        print(f"代码：\n{code}")
        print("-" * 30)
    
    # 3. 性能分析
    print("3. 性能分析")
    print("-" * 50)
    
    analyzer = UsageAnalyzer()
    
    # 测试数据
    test_examples = [
        Example("测试1", "结果1"),
        Example("测试2", "结果2"),
        Example("测试3", "结果3"),
        Example("测试4", "结果4"),
    ]
    
    test_queries = ["查询1", "查询2", "查询3"]
    
    semantic_result = analyzer.analyze_performance("semantic", test_queries, test_examples)
    length_result = analyzer.analyze_performance("length", test_queries, test_examples)
    
    print("语义选择器性能:")
    print(f"  平均延迟: {semantic_result['average_latency']:.4f}s")
    print(f"  使用示例数: {semantic_result['unique_examples_used']}")
    
    print("长度选择器性能:")
    print(f"  平均延迟: {length_result['average_latency']:.4f}s")
    print(f"  使用示例数: {length_result['unique_examples_used']}")
    
    # 4. 导出配置
    config = {
        "use_cases": [
            {
                "name": "customer_service",
                "description": "智能客服机器人",
                "examples_count": 6,
                "selector": "semantic"
            },
            {
                "name": "code_generation", 
                "description": "代码生成助手",
                "examples_count": 4,
                "selector": "hybrid"
            }
        ],
        "best_practices": [
            "根据场景选择合适的selector类型",
            "定期更新示例库",
            "监控选择延迟和准确性",
            "使用缓存优化性能"
        ]
    }
    
    with open("example_selector_usage_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("\n配置已导出到 example_selector_usage_config.json")

if __name__ == "__main__":
    main()