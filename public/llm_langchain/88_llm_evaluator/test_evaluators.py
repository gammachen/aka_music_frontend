"""
测试评估器功能
"""

import asyncio
from evaluator_system import OllamaStringEvaluator, OllamaComparisonEvaluator, OllamaTrajectoryEvaluator
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def test_string_evaluator():
    """测试字符串评估器"""
    print("=== 测试字符串评估器 ===")
    
    evaluator = OllamaStringEvaluator()
    
    # 测试正确性评估
    result = evaluator.evaluate_correctness(
        input_text="2+2等于多少？",
        prediction="2+2=4",
        reference="4"
    )
    
    print(f"正确性评估结果:")
    print(f"得分: {result.score}")
    print(f"通过: {result.passed}")
    print(f"推理: {result.reasoning}")
    print()

def test_comparison_evaluator():
    """测试比较评估器"""
    print("=== 测试比较评估器 ===")
    
    evaluator = OllamaComparisonEvaluator()
    
    result = evaluator.compare_outputs(
        input_text="什么是机器学习？",
        prediction_a="机器学习是人工智能的一个子领域，专注于让计算机从数据中学习。",
        prediction_b="机器学习就是让计算机通过大量数据训练，学会自己做出决策和预测的技术。"
    )
    
    print(f"比较结果:")
    print(f"获胜者: {result['winner']}")
    print(f"推理: {result['reasoning']}")
    print()

def test_trajectory_evaluator():
    """测试轨迹评估器"""
    print("=== 测试轨迹评估器 ===")
    
    evaluator = OllamaTrajectoryEvaluator()
    
    # 模拟代理的决策轨迹
    trajectory = [
        {
            "tool": "Calculator",
            "tool_input": "3**2",
            "tool_output": "9"
        },
        {
            "tool": "Calculator", 
            "tool_input": "9*4",
            "tool_output": "36"
        }
    ]
    
    result = evaluator.evaluate_trajectory(
        input_text="计算3的平方乘以4",
        final_output="36",
        intermediate_steps=trajectory
    )
    
    print(f"轨迹评估结果:")
    print(f"得分: {result.score}")
    print(f"通过: {result.passed}")
    print(f"推理: {result.reasoning}")
    print()

def test_batch_evaluation():
    """测试批量评估"""
    print("=== 批量评估测试 ===")
    
    evaluator = OllamaStringEvaluator()
    
    # 测试数据集
    test_cases = [
        {
            "input": "2+2等于多少？",
            "prediction": "2 + 2 等于 4。",
            "reference": "4",
            "id": "math_q1"
        },
        {
            "input": "中国的首都是哪里？",
            "prediction": "中国的首都是北京。",
            "reference": "北京",
            "id": "geo_q1"
        }
    ]
    
    print("批量评估结果:")
    for case in test_cases:
        result = evaluator.evaluate_correctness(
            input_text=case["input"],
            prediction=case["prediction"],
            reference=case["reference"]
        )
        
        print(f"{case['id']}:")
        print(f"  输入: {case['input']}")
        print(f"  预测: {case['prediction']}")
        print(f"  参考: {case['reference']}")
        print(f"  得分: {result.score}")
        print(f"  通过: {result.passed}")
        print()

def create_example_llm_chain():
    """创建示例LLM链用于测试"""
    llm = Ollama(model="gpt-3.5-turbo", temperature=0.7)
    
    prompt = PromptTemplate(
        input_variables=["question"],
        template="请回答以下问题：{question}"
    )
    
    return LLMChain(llm=llm, prompt=prompt)

if __name__ == "__main__":
    try:
        test_string_evaluator()
        test_comparison_evaluator() 
        test_trajectory_evaluator()
        test_batch_evaluation()
        
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print("请检查:")
        print("1. Ollama服务是否运行: ollama serve")
        print("2. gpt-3.5-turbo模型是否可用: ollama pull gpt-3.5-turbo")
        print("3. 网络连接是否正常")