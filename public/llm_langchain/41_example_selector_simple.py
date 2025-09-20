"""
LangChain ExampleSelector 简化实现
修复了哈希问题的版本
"""

import json
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Example:
    """示例数据结构"""
    input: str
    output: str
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def __hash__(self):
        return hash((self.input, self.output, str(self.metadata)))

class BaseExampleSelector(ABC):
    """示例选择器基类"""
    
    def __init__(self, examples: List[Example] = None):
        self.examples = examples or []
        self.metrics = {
            "selection_count": 0,
            "avg_latency": 0.0
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
    
    def get_stats(self) -> Dict[str, Any]:
        """获取选择器统计信息"""
        return {
            "total_examples": len(self.examples),
            **self.metrics
        }

class SemanticSelector(BaseExampleSelector):
    """语义相似度选择器"""
    
    def __init__(self, examples: List[Example] = None):
        super().__init__(examples)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
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
        
        # 计算相似度并排序
        similarities = []
        for example in self.examples:
            similarity = self._calculate_similarity(query, example.input)
            similarities.append((similarity, example))
        
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # 选择top-k
        selected = [example for _, example in similarities[:max_examples]]
        
        # 更新指标
        latency = time.time() - start_time
        self.metrics["selection_count"] += 1
        self.metrics["avg_latency"] = (
            (self.metrics["avg_latency"] * (self.metrics["selection_count"] - 1) + latency) 
            / self.metrics["selection_count"]
        )
        
        return selected

class LengthSelector(BaseExampleSelector):
    """基于长度的选择器"""
    
    def __init__(self, examples: List[Example] = None, max_length: int = 200):
        super().__init__(examples)
        self.max_length = max_length
    
    def _get_length(self, text: str) -> int:
        """获取文本长度"""
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
        
        # 计算可用长度
        query_length = self._get_length(query)
        available_length = self.max_length - query_length
        
        # 按长度排序
        examples_with_length = []
        for example in self.examples:
            example_text = f"{example.input} {example.output}"
            length = self._get_length(example_text)
            examples_with_length.append((length, example))
        
        examples_with_length.sort(key=lambda x: x[0])
        
        # 选择不超出长度限制的示例
        selected = []
        total_length = 0
        
        for length, example in examples_with_length:
            if total_length + length <= available_length and len(selected) < max_examples:
                selected.append(example)
                total_length += length
        
        # 更新指标
        latency = time.time() - start_time
        self.metrics["selection_count"] += 1
        self.metrics["avg_latency"] = (
            (self.metrics["avg_latency"] * (self.metrics["selection_count"] - 1) + latency) 
            / self.metrics["selection_count"]
        )
        
        return selected

class DiversitySelector(BaseExampleSelector):
    """多样性选择器"""
    
    def __init__(self, examples: List[Example] = None):
        super().__init__(examples)
    
    def _get_diversity_score(self, candidate: Example, selected: List[Example]) -> float:
        """计算多样性分数"""
        if not selected:
            return 1.0
        
        # 与已选示例的最小相似度
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
        """选择多样性高的示例"""
        
        start_time = time.time()
        query = str(input_variables.get("input", ""))
        
        if not self.examples:
            return []
        
        # 计算相关性分数
        query_words = set(query.lower().split())
        scored_examples = []
        
        for example in self.examples:
            example_words = set(example.input.lower().split())
            relevance = len(query_words.intersection(example_words)) / len(query_words.union(example_words))
            scored_examples.append((relevance, example))
        
        # 按相关性排序
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        
        # 使用贪心算法选择多样性高的示例
        selected = []
        candidates = scored_examples[:max_examples * 2]
        
        for _ in range(min(max_examples, len(candidates))):
            best_score = -1
            best_example = None
            
            for relevance, example in candidates:
                if example in selected:
                    continue
                
                diversity_score = self._get_diversity_score(example, selected)
                combined_score = 0.7 * relevance + 0.3 * diversity_score
                
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

class HybridSelector(BaseExampleSelector):
    """混合选择器"""
    
    def __init__(self, examples: List[Example] = None):
        super().__init__(examples)
        self.semantic_selector = SemanticSelector(examples)
        self.length_selector = LengthSelector(examples)
        self.diversity_selector = DiversitySelector(examples)
    
    def select_examples(
        self, 
        input_variables: Dict[str, Any], 
        max_examples: int = 4
    ) -> List[Example]:
        """综合多种策略"""
        
        start_time = time.time()
        
        # 获取各选择器的结果
        semantic_results = self.semantic_selector.select_examples(input_variables, max_examples)
        length_results = self.length_selector.select_examples(input_variables, max_examples)
        diversity_results = self.diversity_selector.select_examples(input_variables, max_examples)
        
        # 合并结果并去重
        all_examples = semantic_results + length_results + diversity_results
        seen = set()
        unique_examples = []
        
        for example in all_examples:
            if example.input not in seen:
                unique_examples.append(example)
                seen.add(example.input)
        
        # 按相关性排序并选择
        query = str(input_variables.get("input", ""))
        query_words = set(query.lower().split())
        
        final_scores = []
        for example in unique_examples:
            example_words = set(example.input.lower().split())
            relevance = len(query_words.intersection(example_words)) / len(query_words.union(example_words))
            final_scores.append((relevance, example))
        
        final_scores.sort(key=lambda x: x[0], reverse=True)
        selected = [example for _, example in final_scores[:max_examples]]
        
        # 更新指标
        latency = time.time() - start_time
        self.metrics["selection_count"] += 1
        self.metrics["avg_latency"] = (
            (self.metrics["avg_latency"] * (self.metrics["selection_count"] - 1) + latency) 
            / self.metrics["selection_count"]
        )
        
        return selected

class ExampleDatasets:
    """示例数据集"""
    
    @staticmethod
    def get_examples() -> List[Example]:
        """获取综合示例"""
        return [
            Example("什么是机器学习？", "机器学习是AI的分支，让计算机从数据中学习"),
            Example("如何学习Python？", "从基础语法开始，做小项目，持续实践"),
            Example("Python有哪些应用？", "Web开发、数据分析、AI、自动化脚本等"),
            Example("什么是深度学习？", "基于神经网络的机器学习方法"),
            Example("如何调试代码？", "使用print、断点、日志和调试器"),
            Example("什么是API？", "应用程序接口，用于不同软件间的通信"),
            Example("如何写测试？", "使用unittest、pytest等测试框架"),
            Example("什么是版本控制？", "使用Git等工具管理代码变更"),
        ]

class DemoRunner:
    """演示运行器"""
    
    def __init__(self):
        examples = ExampleDatasets.get_examples()
        self.selectors = {
            "语义选择器": SemanticSelector(examples),
            "长度选择器": LengthSelector(examples, max_length=150),
            "多样性选择器": DiversitySelector(examples),
            "混合选择器": HybridSelector(examples)
        }
    
    def run_demo(self):
        """运行演示"""
        
        print("=== LangChain ExampleSelector 技术演示 ===\n")
        
        test_queries = [
            "什么是人工智能？",
            "如何学习编程？",
            "Python是什么？",
            "如何调试程序？"
        ]
        
        for query in test_queries:
            print(f"查询：{query}")
            print("-" * 40)
            
            for name, selector in self.selectors.items():
                selected = selector.select_examples({"input": query}, max_examples=2)
                
                print(f"{name}:")
                for i, example in enumerate(selected, 1):
                    print(f"  {i}. {example.input} -> {example.output}")
                
                stats = selector.get_stats()
                print(f"   延迟: {stats['avg_latency']:.3f}s")
                print()
        
        # 性能对比
        print("=== 性能对比 ===")
        for name, selector in self.selectors.items():
            stats = selector.get_stats()
            print(f"{name}: 示例数={stats['total_examples']}, 平均延迟={stats['avg_latency']:.3f}s")

if __name__ == "__main__":
    demo = DemoRunner()
    demo.run_demo()