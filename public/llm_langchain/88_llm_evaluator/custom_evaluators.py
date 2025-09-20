"""
自定义评估器示例
展示如何创建和使用自定义评估器
"""

import json
import re
from typing import Dict, Any, List
from evaluator_system import EvaluationResult
from langchain_community.llms import Ollama
from langchain.evaluation import StringEvaluator
from langchain.schema import Document
import numpy as np

class LengthEvaluator:
    """文本长度评估器"""
    
    def __init__(self, min_length: int = 10, max_length: int = 200):
        self.min_length = min_length
        self.max_length = max_length
    
    def evaluate_strings(self, prediction: str, reference: str = None, input: str = None) -> EvaluationResult:
        """评估文本长度是否在合理范围内"""
        length = len(prediction)
        
        if length < self.min_length:
            score = 0.3
            reasoning = f"文本过短（{length}字符），应至少{self.min_length}字符"
        elif length > self.max_length:
            score = 0.5
            reasoning = f"文本过长（{length}字符），应不超过{self.max_length}字符"
        else:
            score = 1.0
            reasoning = f"文本长度合适（{length}字符）"
        
        return EvaluationResult(
            score=score,
            reasoning=reasoning,
            passed=score >= 0.7
        )

class KeywordEvaluator:
    """关键词检查评估器"""
    
    def __init__(self, required_keywords: List[str] = None, prohibited_keywords: List[str] = None):
        self.required_keywords = required_keywords or []
        self.prohibited_keywords = prohibited_keywords or []
    
    def evaluate_strings(self, prediction: str, reference: str = None, input: str = None) -> EvaluationResult:
        """检查是否包含必需关键词且不包含禁止关键词"""
        prediction_lower = prediction.lower()
        
        # 检查必需关键词
        missing_keywords = []
        for keyword in self.required_keywords:
            if keyword.lower() not in prediction_lower:
                missing_keywords.append(keyword)
        
        # 检查禁止关键词
        found_prohibited = []
        for keyword in self.prohibited_keywords:
            if keyword.lower() in prediction_lower:
                found_prohibited.append(keyword)
        
        if missing_keywords:
            score = 0.2
            reasoning = f"缺少必需关键词: {', '.join(missing_keywords)}"
        elif found_prohibited:
            score = 0.1
            reasoning = f"包含禁止关键词: {', '.join(found_prohibited)}"
        else:
            score = 1.0
            reasoning = "关键词检查通过"
        
        return EvaluationResult(
            score=score,
            reasoning=reasoning,
            passed=score >= 0.7
        )

class JsonFormatEvaluator:
    """JSON格式验证评估器"""
    
    def __init__(self, required_keys: List[str] = None):
        self.required_keys = required_keys or []
    
    def evaluate_strings(self, prediction: str, reference: str = None, input: str = None) -> EvaluationResult:
        """验证JSON格式是否正确"""
        try:
            data = json.loads(prediction)
            
            # 检查必需键
            missing_keys = []
            for key in self.required_keys:
                if key not in data:
                    missing_keys.append(key)
            
            if missing_keys:
                score = 0.3
                reasoning = f"JSON缺少必需键: {', '.join(missing_keys)}"
            else:
                score = 1.0
                reasoning = "JSON格式正确"
                
        except json.JSONDecodeError as e:
            score = 0.0
            reasoning = f"JSON格式错误: {str(e)}"
        
        return EvaluationResult(
            score=score,
            reasoning=reasoning,
            passed=score >= 0.7
        )

class SemanticSimilarityEvaluator:
    """语义相似度评估器"""
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.llm = Ollama(model="gpt-3.5-turbo", temperature=0)
    
    def evaluate_strings(self, prediction: str, reference: str = None, input: str = None) -> EvaluationResult:
        """评估预测与参考的语义相似度"""
        if not reference:
            return EvaluationResult(
                score=0.5,
                reasoning="无参考文本，无法进行语义相似度评估",
                passed=False
            )
        
        # 使用简单的提示评估语义相似度
        prompt = f"""
        请评估以下两个文本的语义相似度（0-1分）：
        
        文本1: {prediction}
        文本2: {reference}
        
        请只回答一个数字（0-1之间），表示相似度。
        """
        
        try:
            response = self.llm.invoke(prompt)
            # 提取数字
            numbers = re.findall(r'[0-9]+\.?[0-9]*', response)
            if numbers:
                score = float(numbers[0])
                if score > 1.0:
                    score = 1.0
                elif score < 0.0:
                    score = 0.0
            else:
                score = 0.5
            
            reasoning = f"语义相似度: {score:.2f}"
            
            return EvaluationResult(
                score=score,
                reasoning=reasoning,
                passed=score >= self.threshold
            )
            
        except Exception as e:
            return EvaluationResult(
                score=0.0,
                reasoning=f"评估失败: {str(e)}",
                passed=False
            )

class CustomEvaluationSuite:
    """自定义评估套件"""
    
    def __init__(self):
        self.evaluators = {
            "length": LengthEvaluator(min_length=5, max_length=100),
            "keywords": KeywordEvaluator(
                required_keywords=["人工智能", "机器学习"],
                prohibited_keywords=["垃圾", "废话"]
            ),
            "json": JsonFormatEvaluator(required_keys=["answer"]),
            "semantic": SemanticSimilarityEvaluator(threshold=0.6)
        }
    
    def evaluate_single(self, 
                       prediction: str, 
                       reference: str = None, 
                       input: str = None,
                       evaluator_types: List[str] = None) -> Dict[str, EvaluationResult]:
        """使用指定的评估器评估单个预测"""
        if evaluator_types is None:
            evaluator_types = list(self.evaluators.keys())
        
        results = {}
        for eval_type in evaluator_types:
            if eval_type in self.evaluators:
                try:
                    evaluator = self.evaluators[eval_type]
                    results[eval_type] = evaluator.evaluate_strings(
                        prediction=prediction,
                        reference=reference,
                        input=input
                    )
                except Exception as e:
                    results[eval_type] = EvaluationResult(
                        score=0.0,
                        reasoning=f"评估器 {eval_type} 失败: {str(e)}",
                        passed=False
                    )
        
        return results
    
    def evaluate_batch(self, 
                      test_cases: List[Dict[str, Any]],
                      evaluator_types: List[str] = None) -> Dict[str, Dict[str, EvaluationResult]]:
        """批量评估多个测试用例"""
        results = {}
        
        for case in test_cases:
            case_id = case.get("id", f"case_{len(results)}")
            results[case_id] = self.evaluate_single(
                prediction=case["prediction"],
                reference=case.get("reference"),
                input=case.get("input"),
                evaluator_types=evaluator_types
            )
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str):
        """保存评估结果到文件"""
        import json
        
        # 转换结果为可序列化的格式
        serializable_results = {}
        for case_id, eval_results in results.items():
            serializable_results[case_id] = {}
            for eval_type, result in eval_results.items():
                serializable_results[case_id][eval_type] = {
                    "score": result.score,
                    "passed": result.passed,
                    "reasoning": result.reasoning
                }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到 {filename}")

# 测试函数
def test_custom_evaluators():
    """测试自定义评估器"""
    print("=== 测试自定义评估器 ===")
    
    suite = CustomEvaluationSuite()
    
    # 测试用例
    test_cases = [
        {
            "id": "case_1",
            "input": "什么是人工智能？",
            "prediction": "人工智能是模拟人类智能的技术，包括机器学习、深度学习等子领域。",
            "reference": "人工智能是模拟人类智能的技术"
        },
        {
            "id": "case_2",
            "input": "请提供JSON格式的回答",
            "prediction": '{"answer": "人工智能是模拟人类智能的技术", "confidence": 0.9}',
            "reference": "人工智能是模拟人类智能的技术"
        },
        {
            "id": "case_3",
            "input": "简短回答",
            "prediction": "AI",
            "reference": "人工智能"
        }
    ]
    
    # 运行批量评估
    results = suite.evaluate_batch(test_cases)
    
    # 打印结果
    for case_id, eval_results in results.items():
        case = next(tc for tc in test_cases if tc["id"] == case_id)
        print(f"\n## {case_id}")
        print(f"- 输入: {case['input']}")
        print(f"- 预测: {case['prediction']}")
        print(f"- 参考: {case['reference']}")
        
        print("### 评估结果:")
        for eval_type, result in eval_results.items():
            print(f"- **{eval_type}**:")
            print(f"  - 得分: {result.score:.2f}")
            print(f"  - 通过: {'是' if result.passed else '否'}")
            print(f"  - 推理: {result.reasoning}")
    
    # 保存结果
    suite.save_results(results, "custom_evaluation_results.json")
    
    # 生成Markdown报告
    with open("custom_evaluation_report.md", "w", encoding="utf-8") as f:
        f.write("# 自定义评估器测试报告\n\n")
        for case_id, eval_results in results.items():
            case = next(tc for tc in test_cases if tc["id"] == case_id)
            f.write(f"## {case_id}\n\n")
            f.write(f"- **输入**: {case['input']}\n")
            f.write(f"- **预测**: {case['prediction']}\n")
            f.write(f"- **参考**: {case['reference']}\n\n")
            f.write("### 评估结果\n\n")
            
            for eval_type, result in eval_results.items():
                f.write(f"#### {eval_type}\n")
                f.write(f"- **得分**: {result.score:.2f}\n")
                f.write(f"- **通过**: {'是' if result.passed else '否'}\n")
                f.write(f"- **推理**: {result.reasoning}\n\n")
    
    print("结果已保存到 custom_evaluation_results.json 和 custom_evaluation_report.md")

if __name__ == "__main__":
    test_custom_evaluators()