"""
LangChain ExampleSelector 完整实现库
包含所有类型的示例选择器实现
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from collections import defaultdict
import hashlib

# 简化的依赖导入（实际使用时需要安装对应包）
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
# from transformers import GPT2TokenizerFast

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

class BaseExampleSelector(ABC):
    """示例选择器基类"""
    
    def __init__(self, examples: List[Example] = None):
        self.examples = examples or []
        self.metrics = {
            "selection_count": 0,
            "avg_latency": 0.0,
            "cache_hits": 0
        }
    
    @abstractmethod
    def select_examples(
        self, 
        input_variables: Dict[str, Any], 
        max_examples: int = 4
    ) -> List[Example]:
        """选择最优示例"""
        pass
    
    def add_example(self, example: Example) -> None:
        """添加新示例"""
        self.examples.append(example)
    
    def remove_example(self, index: int) -> None:
        """移除示例"""
        if 0 <= index < len(self.examples):
            self.examples.pop(index)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取选择器统计信息"""
        return {
            "total_examples": len(self.examples),
            **self.metrics
        }

class SimpleSemanticSelector(BaseExampleSelector):
    """简化版语义相似度选择器"""
    
    def __init__(self, examples: List[Example] = None):
        super().__init__(examples)
        self.similarity_cache = {}
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简化版）"""
        # 使用简单的Jaccard相似度
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0
    
    def select_examples(
        self, 
        input_variables: Dict[str, Any], 
        max_examples: int = 4
    ) -> List[Example]:
        """基于相似度选择示例"""
        
        start_time = time.time()
        query = str(input_variables.get("input", ""))
        
        if not self.examples:
            return []
        
        # 计算所有相似度
        similarities = []
        for idx, example in enumerate(self.examples):
            cache_key = hashlib.md5(f"{query}_{example.input}".encode()).hexdigest()
            
            if cache_key in self.similarity_cache:
                similarity = self.similarity_cache[cache_key]
                self.metrics["cache_hits"] += 1
            else:
                example_text = f"{example.input} {example.output}"
                similarity = self._calculate_similarity(query, example_text)
                self.similarity_cache[cache_key] = similarity
            
            similarities.append((similarity, idx))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # 选择top-k
        selected_indices = [idx for _, idx in similarities[:max_examples]]
        selected_examples = [self.examples[idx] for idx in selected_indices]
        
        # 更新指标
        latency = time.time() - start_time
        self.metrics["selection_count"] += 1
        self.metrics["avg_latency"] = (
            (self.metrics["avg_latency"] * (self.metrics["selection_count"] - 1) + latency) 
            / self.metrics["selection_count"]
        )
        
        return selected_examples

class LengthBasedSelector(BaseExampleSelector):
    """基于长度的选择器"""
    
    def __init__(self, examples: List[Example] = None, max_length: int = 1000):
        super().__init__(examples)
        self.max_length = max_length
        self.length_cache = {}
    
    def _estimate_length(self, text: str) -> int:
        """估算文本长度（字符数）"""
        return len(text)
    
    def select_examples(
        self, 
        input_variables: Dict[str, Any], 
        max_examples: int = 4
    ) -> List[Example]:
        """在长度限制内选择示例"""
        
        start_time = time.time()
        query = str(input_variables.get("input", ""))
        
        if not self.examples:
            return []
        
        # 计算输入长度
        input_length = self._estimate_length(query)
        available_length = self.max_length - input_length - 100  # 保留余量
        
        # 按长度排序（优先选择短的）
        examples_with_length = []
        for idx, example in enumerate(self.examples):
            example_text = f"Input: {example.input}\nOutput: {example.output}"
            length = self._estimate_length(example_text)
            examples_with_length.append((length, idx, example))
        
        examples_with_length.sort(key=lambda x: x[0])
        
        # 选择不超出长度限制的示例
        selected = []
        total_length = 0
        
        for length, idx, example in examples_with_length:
            if total_length + length <= available_length and len(selected) < max_examples:
                selected.append(example)
                total_length += length
            else:
                break
        
        # 更新指标
        latency = time.time() - start_time
        self.metrics["selection_count"] += 1
        self.metrics["avg_latency"] = (
            (self.metrics["avg_latency"] * (self.metrics["selection_count"] - 1) + latency) 
            / self.metrics["selection_count"]
        )
        
        return selected

class DiversityBasedSelector(BaseExampleSelector):
    """基于多样性的选择器"""
    
    def __init__(self, examples: List[Example] = None, diversity_weight: float = 0.5):
        super().__init__(examples)
        self.diversity_weight = diversity_weight
    
    def _calculate_diversity_score(
        self, 
        candidate: Example, 
        selected: List[Example]
    ) -> float:
        """计算多样性分数"""
        if not selected:
            return 1.0
        
        # 简单实现：与已选示例的输入相似度越低，多样性越高
        min_similarity = 1.0
        candidate_words = set(candidate.input.lower().split())
        
        for selected_example in selected:
            selected_words = set(selected_example.input.lower().split())
            
            if candidate_words and selected_words:
                similarity = len(candidate_words.intersection(selected_words)) / len(candidate_words.union(selected_words))
                min_similarity = min(min_similarity, similarity)
        
        return 1.0 - min_similarity
    
    def select_examples(
        self, 
        input_variables: Dict[str, Any], 
        max_examples: int = 4
    ) -> List[Example]:
        """选择多样性最大化的示例"""
        
        start_time = time.time()
        query = str(input_variables.get("input", ""))
        
        if not self.examples:
            return []
        
        # 计算相关性分数（简化版：关键词匹配）
        query_words = set(query.lower().split())
        scored_examples = []
        
        for idx, example in enumerate(self.examples):
            example_words = set(example.input.lower().split())
            relevance = len(query_words.intersection(example_words)) / len(query_words.union(example_words))
            scored_examples.append((relevance, idx, example))
        
        # 按相关性排序
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        
        # 使用贪心算法选择多样性高的示例
        selected = []
        remaining = scored_examples[:max_examples * 2]  # 扩展候选池
        
        for _ in range(min(max_examples, len(remaining))):
            best_score = -1
            best_example = None
            best_idx = -1
            
            for rel_score, idx, example in remaining:
                if example in selected:
                    continue
                
                diversity_score = self._calculate_diversity_score(example, selected)
                combined_score = (1 - self.diversity_weight) * rel_score + self.diversity_weight * diversity_score
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_example = example
            
            if best_example:
                selected.append(best_example)
        
        # 更新指标
        latency = time.time() - start_time
        self.metrics["selection_count"] += 1
        self.metrics["avg_latency"] = (
            (self.metrics["avg_latency"] * (self.metrics["selection_count"] - 1) + latency) 
            / self.metrics["selection_count"]
        )
        
        return selected

class KeywordBasedSelector(BaseExampleSelector):
    """基于关键词的选择器"""
    
    def __init__(self, examples: List[Example] = None, keywords: Dict[str, List[str]] = None):
        super().__init__(examples)
        self.keywords = keywords or {}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简化版：使用预定义关键词匹配
        text_lower = text.lower()
        found_keywords = []
        
        for keyword_list in self.keywords.values():
            for keyword in keyword_list:
                if keyword.lower() in text_lower:
                    found_keywords.append(keyword)
        
        return found_keywords
    
    def select_examples(
        self, 
        input_variables: Dict[str, Any], 
        max_examples: int = 4
    ) -> List[Example]:
        """基于关键词匹配选择示例"""
        
        start_time = time.time()
        query = str(input_variables.get("input", ""))
        
        if not self.examples:
            return []
        
        # 提取查询关键词
        query_keywords = self._extract_keywords(query)
        
        # 计算关键词匹配分数
        scored_examples = []
        for idx, example in enumerate(self.examples):
            example_keywords = self._extract_keywords(example.input)
            
            # 计算关键词重叠度
            overlap = len(set(query_keywords).intersection(set(example_keywords)))
            total = len(set(query_keywords).union(set(example_keywords)))
            score = overlap / total if total > 0 else 0.0
            
            scored_examples.append((score, idx, example))
        
        # 按分数排序
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        
        # 选择top-k
        selected_indices = [idx for _, idx, _ in scored_examples[:max_examples]]
        selected_examples = [self.examples[idx] for idx in selected_indices]
        
        # 更新指标
        latency = time.time() - start_time
        self.metrics["selection_count"] += 1
        self.metrics["avg_latency"] = (
            (self.metrics["avg_latency"] * (self.metrics["selection_count"] - 1) + latency) 
            / self.metrics["selection_count"]
        )
        
        return selected_examples

class HybridExampleSelector(BaseExampleSelector):
    """混合选择器 - 结合多种策略"""
    
    def __init__(
        self, 
        examples: List[Example] = None,
        strategies: Dict[str, float] = None
    ):
        super().__init__(examples)
        
        # 权重配置
        self.strategies = strategies or {
            "semantic": 0.4,
            "length": 0.3,
            "diversity": 0.3
        }
        
        # 初始化子选择器
        self.sub_selectors = {
            "semantic": SimpleSemanticSelector(examples),
            "length": LengthBasedSelector(examples),
            "diversity": DiversityBasedSelector(examples)
        }
    
    def select_examples(
        self, 
        input_variables: Dict[str, Any], 
        max_examples: int = 4
    ) -> List[Example]:
        """综合多种策略选择示例"""
        
        start_time = time.time()
        
        # 收集各策略的选择结果
        all_scores = defaultdict(list)
        
        for strategy_name, selector in self.sub_selectors.items():
            selected = selector.select_examples(input_variables, max_examples * 2)
            
            # 为每个示例分配策略分数
            for idx, example in enumerate(selected):
                score = (len(selected) - idx) / len(selected)  # 位置权重
                all_scores[strategy_name].append((example, score))
        
        # 计算综合分数
        example_scores = defaultdict(float)
        
        for strategy_name, weighted_examples in all_scores.items():
            weight = self.strategies[strategy_name]
            
            for example, score in weighted_examples:
                example_scores[example] += score * weight
        
        # 按综合分数排序
        sorted_examples = sorted(
            example_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # 去重并选择top-k
        seen_inputs = set()
        selected = []
        
        for example, _ in sorted_examples:
            if example.input not in seen_inputs and len(selected) < max_examples:
                selected.append(example)
                seen_inputs.add(example.input)
        
        # 更新指标
        latency = time.time() - start_time
        self.metrics["selection_count"] += 1
        self.metrics["avg_latency"] = (
            (self.metrics["avg_latency"] * (self.metrics["selection_count"] - 1) + latency) 
            / self.metrics["selection_count"]
        )
        
        return selected

class ExampleSelectorFactory:
    """示例选择器工厂"""
    
    @staticmethod
    def create_selector(
        selector_type: str, 
        examples: List[Example] = None,
        **kwargs
    ) -> BaseExampleSelector:
        """创建指定类型的选择器"""
        
        selectors = {
            "semantic": SimpleSemanticSelector,
            "length": LengthBasedSelector,
            "diversity": DiversityBasedSelector,
            "keyword": KeywordBasedSelector,
            "hybrid": HybridExampleSelector
        }
        
        if selector_type not in selectors:
            raise ValueError(f"Unsupported selector type: {selector_type}")
        
        selector_class = selectors[selector_type]
        return selector_class(examples, **kwargs)

class ExampleSelectorManager:
    """示例选择器管理器"""
    
    def __init__(self):
        self.selectors = {}
        self.performance_log = []
    
    def register_selector(
        self, 
        name: str, 
        selector: BaseExampleSelector
    ):
        """注册选择器"""
        self.selectors[name] = selector
    
    async def benchmark_selectors(
        self, 
        test_inputs: List[Dict[str, Any]],
        max_examples: int = 4
    ) -> Dict[str, Any]:
        """基准测试所有选择器"""
        
        results = {}
        
        for name, selector in self.selectors.items():
            start_time = time.time()
            
            all_selected = []
            for input_vars in test_inputs:
                selected = selector.select_examples(input_vars, max_examples)
                all_selected.extend(selected)
            
            total_time = time.time() - start_time
            avg_latency = total_time / len(test_inputs)
            
            results[name] = {
                "avg_latency": avg_latency,
                "total_examples": len(all_selected),
                "unique_examples": len(set(ex.input for ex in all_selected)),
                "stats": selector.get_stats()
            }
        
        return results

# 预定义示例数据集
class ExampleDatasets:
    """示例数据集"""
    
    @staticmethod
    def get_customer_service_examples() -> List[Example]:
        """客服示例"""
        return [
            Example(
                "我的订单什么时候发货？",
                "您好！您的订单通常在付款后24-48小时内发货。您可以通过订单号在我们的官网查询具体物流信息。"
            ),
            Example(
                "如何申请退款？",
                "退款申请很简单：1) 登录您的账户 2) 进入订单详情 3) 点击申请退款 4) 填写退款原因。我们会在3个工作日内处理。"
            ),
            Example(
                "收到的商品有质量问题怎么办？",
                "非常抱歉给您带来不便！我们提供7天无理由退换货服务。请拍照记录问题，联系我们的售后客服，我们会立即为您处理。"
            ),
            Example(
                "忘记密码了怎么重置？",
                "您可以通过以下步骤重置密码：1) 点击登录页面的'忘记密码' 2) 输入注册邮箱或手机号 3) 接收验证码 4) 设置新密码。"
            ),
            Example(
                "会员积分如何使用？",
                "会员积分可以在结账时直接抵扣现金，100积分=1元。在购物车页面选择'使用积分抵扣'即可。积分有效期为1年。"
            )
        ]
    
    @staticmethod
    def get_code_generation_examples() -> List[Example]:
        """代码生成示例"""
        return [
            Example(
                "写一个Python函数计算斐波那契数列",
                "def fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)"
            ),
            Example(
                "创建一个Python类实现栈数据结构",
                "class Stack:\n    def __init__(self):\n        self.items = []\n    \n    def push(self, item):\n        self.items.append(item)\n    \n    def pop(self):\n        return self.items.pop() if self.items else None\n    \n    def is_empty(self):\n        return len(self.items) == 0"
            ),
            Example(
                "实现快速排序算法",
                "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    \n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    \n    return quicksort(left) + middle + quicksort(right)"
            )
        ]
    
    @staticmethod
    def get_qa_examples() -> List[Example]:
        """问答示例"""
        return [
            Example(
                "什么是机器学习？",
                "机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习并改进性能，而无需明确编程。它包括监督学习、无监督学习和强化学习等方法。"
            ),
            Example(
                "Python和JavaScript有什么区别？",
                "Python主要用于后端开发、数据分析和AI，语法简洁优雅；JavaScript主要用于前端开发，实现网页交互，近年来也用于后端(Node.js)。Python是解释型语言，JavaScript是脚本语言。"
            ),
            Example(
                "如何学习编程？",
                "学习编程的建议：1) 选择一门入门语言（如Python）2) 从基础语法开始 3) 做小项目练习 4) 阅读优秀代码 5) 参与开源项目 6) 持续学习和实践"
            )
        ]

# 使用示例和测试
class ExampleSelectorDemo:
    """示例选择器演示"""
    
    def __init__(self):
        self.manager = ExampleSelectorManager()
        self._setup_selectors()
    
    def _setup_selectors(self):
        """设置各种选择器"""
        
        # 客服示例
        cs_examples = ExampleDatasets.get_customer_service_examples()
        self.manager.register_selector(
            "customer_service_semantic", 
            SimpleSemanticSelector(cs_examples)
        )
        self.manager.register_selector(
            "customer_service_length", 
            LengthBasedSelector(cs_examples, max_length=500)
        )
        
        # 代码示例
        code_examples = ExampleDatasets.get_code_generation_examples()
        self.manager.register_selector(
            "code_generation", 
            DiversityBasedSelector(code_examples)
        )
        
        # 问答示例
        qa_examples = ExampleDatasets.get_qa_examples()
        self.manager.register_selector(
            "qa_hybrid", 
            HybridExampleSelector(qa_examples)
        )
    
    async def run_demo(self):
        """运行演示"""
        
        print("=== LangChain ExampleSelector 演示 ===\n")
        
        # 测试用例
        test_cases = [
            {
                "selector": "customer_service_semantic",
                "input": {"input": "我的订单什么时候能到？"},
                "description": "客服场景 - 语义相似度"
            },
            {
                "selector": "customer_service_length",
                "input": {"input": "如何申请退款？"},
                "description": "客服场景 - 长度优化"
            },
            {
                "selector": "code_generation",
                "input": {"input": "写一个排序算法"},
                "description": "代码生成 - 多样性"
            },
            {
                "selector": "qa_hybrid",
                "input": {"input": "什么是人工智能？"},
                "description": "问答场景 - 混合策略"
            }
        ]
        
        for case in test_cases:
            print(f"测试场景：{case['description']}")
            print(f"用户输入：{case['input']['input']}")
            
            selector = self.manager.selectors[case['selector']]
            selected = selector.select_examples(case['input'], max_examples=2)
            
            print(f"选择示例数量：{len(selected)}")
            for i, example in enumerate(selected, 1):
                print(f"  {i}. 输入：{example.input[:50]}...")
                print(f"     输出：{example.output[:50]}...")
            
            stats = selector.get_stats()
            print(f"平均延迟：{stats['avg_latency']:.3f}s")
            print("-" * 50)
        
        # 基准测试
        print("\n=== 基准测试 ===")
        benchmark_inputs = [
            {"input": "测试问题1"},
            {"input": "测试问题2"},
            {"input": "测试问题3"}
        ]
        
        results = await self.manager.benchmark_selectors(benchmark_inputs)
        
        for name, result in results.items():
            print(f"{name}: {result['avg_latency']:.3f}s, {result['total_examples']} examples")
    
    def export_config(self, filename: str):
        """导出配置"""
        config = {
            "selectors": list(self.manager.selectors.keys()),
            "timestamp": datetime.now().isoformat(),
            "datasets": {
                "customer_service": len(ExampleDatasets.get_customer_service_examples()),
                "code_generation": len(ExampleDatasets.get_code_generation_examples()),
                "qa": len(ExampleDatasets.get_qa_examples())
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

# 主函数和测试
async def main():
    """主函数"""
    demo = ExampleSelectorDemo()
    await demo.run_demo()
    
    # 导出配置
    demo.export_config("example_selector_config.json")
    
    print("\n演示完成！配置已导出到 example_selector_config.json")

if __name__ == "__main__":
    asyncio.run(main())