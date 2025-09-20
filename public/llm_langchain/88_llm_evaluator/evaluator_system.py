"""
LangChain评估系统 - 基于Ollama本地模型
支持字符串评估、比较评估和轨迹评估
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 使用新的导入方式
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain.evaluation import load_evaluator
from langchain.evaluation import EvaluatorType
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseMessage, HumanMessage, AIMessage

# 加载环境变量
load_dotenv()

@dataclass
class EvaluationResult:
    """评估结果数据结构"""
    score: float
    reasoning: str
    passed: bool
    metadata: Dict[str, Any] = None

class OllamaStringEvaluator:
    """字符串评估器 - 评估单个字符串输出的质量"""
    
    def __init__(self, model_name: str = None, base_url: str = None):
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "gpt-3.5-turbo")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # 初始化Ollama LLM
        self.llm = Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=0
        )
    
    def evaluate_correctness(self, 
                           input_text: str, 
                           prediction: str, 
                           reference: Optional[str] = None) -> EvaluationResult:
        """评估回答的正确性"""
        try:
            if reference:
                # 使用labeled_criteria评估器当有参考时
                evaluator = load_evaluator(
                    "labeled_criteria",
                    llm=self.llm,
                    criteria="correctness"
                )
                
                result = evaluator.evaluate_strings(
                    input=input_text,
                    prediction=prediction,
                    reference=reference
                )
            else:
                # 使用criteria评估器当无参考时
                evaluator = load_evaluator(
                    "criteria",
                    llm=self.llm,
                    criteria="correctness"
                )
                
                result = evaluator.evaluate_strings(
                    input=input_text,
                    prediction=prediction
                )
            
            return EvaluationResult(
                score=result.get('score', 0),
                reasoning=result.get('reasoning', ''),
                passed=result.get('score', 0) > 0.5,
                metadata={"type": "correctness", "has_reference": reference is not None}
            )
        except Exception as e:
            return EvaluationResult(
                score=0,
                reasoning=f"评估失败: {str(e)}",
                passed=False,
                metadata={"error": str(e)}
            )
    
    def evaluate_friendliness(self, 
                           input_text: str, 
                           prediction: str) -> EvaluationResult:
        """评估回答的友好性"""
        try:
            evaluator = load_evaluator(
                "criteria",
                llm=self.llm,
                criteria="conciseness"
            )
            
            result = evaluator.evaluate_strings(
                input=input_text,
                prediction=prediction
            )
            
            return EvaluationResult(
                score=result.get('score', 0),
                reasoning=result.get('reasoning', ''),
                passed=result.get('score', 0) > 0.5,
                metadata={"type": "friendliness"}
            )
        except Exception as e:
            return EvaluationResult(
                score=0,
                reasoning=f"评估失败: {str(e)}",
                passed=False,
                metadata={"error": str(e)}
            )

class OllamaComparisonEvaluator:
    """比较评估器 - 比较两个输出的优劣"""
    
    def __init__(self, model_name: str = None, base_url: str = None):
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "gpt-3.5-turbo")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.llm = Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=0
        )
    
    def compare_outputs(self, 
                       input_text: str,
                       prediction_a: str,
                       prediction_b: str) -> Dict[str, Any]:
        """比较两个输出的优劣"""
        try:
            evaluator = load_evaluator(
                "pairwise_string",
                llm=self.llm
            )
            
            result = evaluator.evaluate_string_pairs(
                input=input_text,
                prediction=prediction_a,
                prediction_b=prediction_b
            )
            
            return {
                "winner": result.get('value', 'tie'),
                "reasoning": result.get('reasoning', ''),
                "preference": "A" if result.get('value') == 'A' else "B" if result.get('value') == 'B' else "tie"
            }
        except Exception as e:
            return {
                "winner": "error",
                "reasoning": f"比较失败: {str(e)}",
                "error": str(e)
            }

class OllamaTrajectoryEvaluator:
    """轨迹评估器 - 评估代理的多步骤决策过程"""
    
    def __init__(self, model_name: str = None, base_url: str = None):
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "gpt-3.5-turbo")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.llm = Ollama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=0
        )
    
    def evaluate_trajectory(self,
                          input_text: str,
                          final_output: str,
                          intermediate_steps: List[Dict[str, Any]],
                          expected_trajectory: List[Dict[str, Any]] = None) -> EvaluationResult:
        """评估代理的决策轨迹"""
        try:
            # 创建评估提示
            evaluation_prompt = PromptTemplate(
                input_variables=["input", "output", "steps", "expected"],
                template="""
                评估以下代理的决策过程：
                
                用户输入: {input}
                最终输出: {output}
                中间步骤: {steps}
                
                {expected}
                
                请评估：
                1. 代理是否选择了正确的工具？
                2. 是否正确解析了工具输出？
                3. 整个过程是否合理高效？
                
                请给出0-1的评分和详细解释。
                """
            )
            
            eval_chain = LLMChain(llm=self.llm, prompt=evaluation_prompt)
            
            expected_str = f"预期步骤: {expected_trajectory}" if expected_trajectory else "无预期步骤"
            
            result = eval_chain.run({
                "input": input_text,
                "output": final_output,
                "steps": json.dumps(intermediate_steps, ensure_ascii=False, indent=2),
                "expected": expected_str
            })
            
            # 解析结果（简化版）
            score = 0.8 if "正确" in result or "合理" in result else 0.3
            
            return EvaluationResult(
                score=score,
                reasoning=result,
                passed=score > 0.5,
                metadata={
                    "type": "trajectory",
                    "steps_count": len(intermediate_steps),
                    "has_expected": expected_trajectory is not None
                }
            )
        except Exception as e:
            return EvaluationResult(
                score=0,
                reasoning=f"轨迹评估失败: {str(e)}",
                passed=False,
                metadata={"error": str(e)}
            )

class EvaluationSuite:
    """评估套件 - 管理多个评估任务"""
    
    def __init__(self):
        self.string_evaluator = OllamaStringEvaluator()
        self.comparison_evaluator = OllamaComparisonEvaluator()
        self.trajectory_evaluator = OllamaTrajectoryEvaluator()
        self.results = []
    
    def run_string_evaluation(self, 
                           test_cases: List[Dict[str, str]],
                           criteria: str = "correctness") -> List[EvaluationResult]:
        """运行字符串评估"""
        results = []
        
        for case in test_cases:
            if criteria == "correctness":
                result = self.string_evaluator.evaluate_correctness(
                    case["input"],
                    case["prediction"],
                    case.get("reference")
                )
            elif criteria == "friendliness":
                result = self.string_evaluator.evaluate_friendliness(
                    case["input"],
                    case["prediction"]
                )
            else:
                result = EvaluationResult(
                    score=0,
                    reasoning=f"不支持的评估标准: {criteria}",
                    passed=False
                )
            
            results.append(result)
        
        return results
    
    def run_comparison_evaluation(self,
                               test_cases: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """运行比较评估"""
        results = []
        
        for case in test_cases:
            result = self.comparison_evaluator.compare_outputs(
                case["input"],
                case["prediction_a"],
                case["prediction_b"]
            )
            results.append(result)
        
        return results
    
    def run_batch_evaluation(self,
                          dataset: Dict[str, Dict[str, Any]],
                          llm_or_chain_factory) -> Dict[str, Any]:
        """批量评估数据集"""
        results = {}
        
        for key, data in dataset.items():
            try:
                # 运行模型或链
                prediction = llm_or_chain_factory(data["input"])
                
                # 评估结果
                eval_result = self.string_evaluator.evaluate_correctness(
                    data["input"],
                    prediction,
                    data.get("reference")
                )
                
                results[key] = {
                    "input": data["input"],
                    "prediction": prediction,
                    "reference": data.get("reference"),
                    "evaluation": eval_result
                }
            except Exception as e:
                results[key] = {
                    "error": str(e)
                }
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str):
        """保存评估结果"""
        # 转换EvaluationResult为可序列化格式
        serializable_results = {}
        
        for key, value in results.items():
            if isinstance(value, dict) and "evaluation" in value:
                eval_obj = value["evaluation"]
                if isinstance(eval_obj, EvaluationResult):
                    value["evaluation"] = {
                        "score": eval_obj.score,
                        "reasoning": eval_obj.reasoning,
                        "passed": eval_obj.passed,
                        "metadata": eval_obj.metadata
                    }
            serializable_results[key] = value
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 测试评估系统
    suite = EvaluationSuite()
    
    # 测试字符串评估
    test_cases = [
        {
            "input": "地球上最大的海洋是什么？",
            "prediction": "太平洋",
            "reference": "太平洋"
        },
        {
            "input": "法国的首都是哪里？",
            "prediction": "巴黎",
            "reference": "巴黎"
        }
    ]
    
    print("运行字符串评估测试...")
    results = suite.run_string_evaluation(test_cases)
    for i, result in enumerate(results):
        print(f"测试 {i+1}: 得分={result.score}, 通过={result.passed}")
        print(f"推理: {result.reasoning}")
        print("-" * 50)