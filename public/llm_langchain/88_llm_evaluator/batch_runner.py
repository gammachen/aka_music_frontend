"""
批量评估运行器
支持大规模数据集的自动化评估
"""

import json
import asyncio
import pandas as pd
from typing import Dict, List, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
from evaluator_system import EvaluationSuite
from custom_evaluators import CustomEvaluationSuite

class BatchEvaluator:
    """批量评估器 - 处理大规模数据集的评估"""
    
    def __init__(self, max_workers: int = 3, batch_size: int = 10):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.evaluation_suite = EvaluationSuite()
        self.custom_suite = CustomEvaluationSuite()
    
    def load_dataset(self, file_path: str) -> Dict[str, Dict[str, Any]]:
        """加载数据集"""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                return {f"row_{i}": row.to_dict() for i, row in df.iterrows()}
            else:
                raise ValueError("不支持的文件格式")
        except Exception as e:
            print(f"加载数据集失败: {e}")
            return {}
    
    def save_results(self, results: Dict[str, Any], file_path: str):
        """保存评估结果"""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            elif file_path.endswith('.csv'):
                # 转换为DataFrame并保存
                flat_results = []
                for key, value in results.items():
                    flat_result = {"id": key}
                    flat_result.update(value)
                    flat_results.append(flat_result)
                
                df = pd.DataFrame(flat_results)
                df.to_csv(file_path, index=False, encoding='utf-8')
            else:
                raise ValueError("不支持的文件格式")
            
            print(f"结果已保存到: {file_path}")
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def run_single_evaluation(self, 
                           case_id: str, 
                           case_data: Dict[str, Any],
                           llm_factory: Callable[[str], str],
                           evaluation_type: str = "string") -> Dict[str, Any]:
        """运行单个评估"""
        try:
            start_time = time.time()
            
            # 运行模型或链
            prediction = llm_factory(case_data["input"])
            
            # 根据评估类型进行评估
            if evaluation_type == "string":
                eval_result = self.evaluation_suite.string_evaluator.evaluate_correctness(
                    case_data["input"],
                    prediction,
                    case_data.get("reference")
                )
                evaluation = {
                    "score": eval_result.score,
                    "reasoning": eval_result.reasoning,
                    "passed": eval_result.passed
                }
            elif evaluation_type == "custom":
                # 运行自定义评估
                custom_results = self.custom_suite.run_custom_evaluation(
                    [case_data],
                    selected_evaluators=["length", "keywords", "semantic"]
                )
                evaluation = custom_results.get("case_1", {})
            else:
                evaluation = {"error": "不支持的评估类型"}
            
            end_time = time.time()
            
            return {
                "input": case_data["input"],
                "prediction": prediction,
                "reference": case_data.get("reference", ""),
                "evaluation": evaluation,
                "processing_time": end_time - start_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "case_id": case_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def run_batch_evaluation(self,
                           dataset: Dict[str, Dict[str, Any]],
                           llm_factory: Callable[[str], str],
                           evaluation_type: str = "string",
                           output_file: str = None) -> Dict[str, Any]:
        """运行批量评估"""
        
        results = {}
        failed_cases = []
        
        print(f"开始批量评估，共 {len(dataset)} 个测试用例...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_case = {
                executor.submit(
                    self.run_single_evaluation, 
                    case_id, 
                    case_data, 
                    llm_factory,
                    evaluation_type
                ): case_id 
                for case_id, case_data in dataset.items()
            }
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_case):
                case_id = future_to_case[future]
                try:
                    result = future.result()
                    results[case_id] = result
                    completed += 1
                    
                    if "error" in result:
                        failed_cases.append(case_id)
                    
                    if completed % self.batch_size == 0:
                        print(f"已完成 {completed}/{len(dataset)} 个测试用例")
                        
                except Exception as e:
                    results[case_id] = {"error": str(e)}
                    failed_cases.append(case_id)
                    completed += 1
        
        # 计算统计信息
        successful_results = [r for r in results.values() if "error" not in r]
        if successful_results:
            avg_score = sum(r["evaluation"]["score"] if isinstance(r["evaluation"], dict) 
                          else r["evaluation"].score for r in successful_results) / len(successful_results)
            avg_time = sum(r["processing_time"] for r in successful_results) / len(successful_results)
        else:
            avg_score = 0
            avg_time = 0
        
        summary = {
            "total_cases": len(dataset),
            "successful_cases": len(successful_results),
            "failed_cases": len(failed_cases),
            "success_rate": len(successful_results) / len(dataset) if dataset else 0,
            "average_score": avg_score,
            "average_processing_time": avg_time,
            "failed_case_ids": failed_cases,
            "timestamp": datetime.now().isoformat()
        }
        
        final_results = {
            "summary": summary,
            "results": results
        }
        
        if output_file:
            self.save_results(final_results, output_file)
        
        return final_results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成评估报告"""
        
        summary = results["summary"]
        
        report = f"""
# 批量评估报告

## 执行摘要
- **总测试用例**: {summary['total_cases']}
- **成功用例**: {summary['successful_cases']}
- **失败用例**: {summary['failed_cases']}
- **成功率**: {summary['success_rate']:.2%}
- **平均得分**: {summary['average_score']:.2f}
- **平均处理时间**: {summary['average_processing_time']:.2f}秒
- **执行时间**: {summary['timestamp']}

## 详细结果

"""
        
        for case_id, result in results["results"].items():
            if "error" in result:
                report += f"### {case_id}\n**状态**: ❌ 失败\n**错误**: {result['error']}\n\n"
            else:
                eval_data = result["evaluation"]
                if isinstance(eval_data, dict):
                    score = eval_data.get("score", 0)
                    reasoning = eval_data.get("reasoning", "")
                else:
                    score = getattr(eval_data, 'score', 0)
                    reasoning = getattr(eval_data, 'reasoning', "")
                
                status = "✅ 通过" if (isinstance(eval_data, dict) and eval_data.get("passed")) or getattr(eval_data, 'passed', False) else "❌ 未通过"
                
                report += f"### {case_id}\n"
                report += f"**状态**: {status}\n"
                report += f"**输入**: {result.get('input', 'N/A')}\n"
                report += f"**预测**: {result.get('prediction', 'N/A')}\n"
                report += f"**参考**: {result.get('reference', 'N/A')}\n"
                report += f"**得分**: {score:.2f}\n"
                report += f"**推理**: {reasoning}\n"
                report += f"**处理时间**: {result.get('processing_time', 0):.2f}秒\n\n"
        
        return report

def create_sample_dataset():
    """创建示例数据集"""
    
    dataset = {
        "qa_001": {
            "input": "中国的首都是哪里？",
            "reference": "北京"
        },
        "qa_002": {
            "input": "2+2等于多少？",
            "reference": "4"
        },
        "qa_003": {
            "input": "太阳从哪个方向升起？",
            "reference": "东方"
        },
        "qa_004": {
            "input": "一年有多少个月？",
            "reference": "12"
        },
        "qa_005": {
            "input": "水的化学式是什么？",
            "reference": "H2O"
        }
    }
    
    # 保存示例数据集
    with open("sample_dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print("示例数据集已保存到 sample_dataset.json")
    return dataset

def create_llm_factory():
    """创建LLM工厂函数"""
    from langchain.llms import Ollama
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    
    llm = Ollama(model="gpt-3.5-turbo", temperature=0.1)
    
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""请简洁准确地回答以下问题：
        
        问题: {input}
        回答: """
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    def factory(input_text: str) -> str:
        return chain.run(input=input_text).strip()
    
    return factory

def main():
    """主函数 - 运行完整的批量评估流程"""
    
    # 创建批量评估器
    batch_eval = BatchEvaluator(max_workers=2, batch_size=2)
    
    # 创建或加载数据集
    try:
        dataset = batch_eval.load_dataset("sample_dataset.json")
        if not dataset:
            dataset = create_sample_dataset()
    except FileNotFoundError:
        dataset = create_sample_dataset()
    
    # 创建LLM工厂
    llm_factory = create_llm_factory()
    
    print("开始运行批量评估...")
    
    # 运行批量评估
    results = batch_eval.run_batch_evaluation(
        dataset=dataset,
        llm_factory=llm_factory,
        evaluation_type="string",
        output_file="batch_evaluation_results.json"
    )
    
    # 生成报告
    report = batch_eval.generate_report(results)
    
    with open("evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n评估完成！")
    print(f"结果摘要:")
    print(f"- 总用例: {results['summary']['total_cases']}")
    print(f"- 成功: {results['summary']['successful_cases']}")
    print(f"- 失败: {results['summary']['failed_cases']}")
    print(f"- 平均得分: {results['summary']['average_score']:.2f}")
    print(f"- 成功率: {results['summary']['success_rate']:.1%}")
    
    print("\n文件已生成:")
    print("- batch_evaluation_results.json (详细结果)")
    print("- evaluation_report.md (评估报告)")

if __name__ == "__main__":
    main()