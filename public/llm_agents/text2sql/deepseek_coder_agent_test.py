#!/usr/bin/env python3
import json
import requests
import re
import sys
import time
import os
from time import sleep

# Ollama API 配置
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-coder:1.3b"

# 评估配置
MAX_TEST_CASES = 5  # 限制测试用例数量，避免耗时过长
TIMEOUT = 30  # 请求超时时间（秒）


def extract_question(input_text):
    """从 input 字段中提取问题"""
    # 查找问题部分，问题通常在 "Generate a SQL query that answers the question `" 和 "`" 之间
    question_pattern = r"question `([^`]+)`"
    match = re.search(question_pattern, input_text)
    if match:
        return match.group(1).strip()
    
    # 如果没有找到，尝试查找其他可能的问题模式
    # 例如问题直接在 "### Input:\n" 之后
    input_pattern = r"### Input:\n(.*?)### Response" 
    match = re.search(input_pattern, input_text, re.DOTALL)
    if match:
        input_content = match.group(1).strip()
        # 尝试从 input_content 中提取问题
        question_start = input_content.find('`')
        question_end = input_content.rfind('`')
        if question_start != -1 and question_end != -1 and question_start < question_end:
            return input_content[question_start + 1:question_end].strip()
    
    return "无法提取问题"


def extract_schema(input_text):
    """从 input 字段中提取数据库 schema"""
    schema_pattern = r"this string:\n([\s\S]*?)### Response"
    match = re.search(schema_pattern, input_text)
    if match:
        return match.group(1).strip()
    return "无法提取 schema"


def generate_sql_with_ollama(question, schema):
    """通过 Ollama API 生成 SQL 查询"""
    # 构建提示，告知模型返回纯 SQL 查询，不包含其他文本
    prompt = f"""
You are a SQL expert. Convert the following question into a SQL query based on the given database schema.

### Database Schema:
{schema}

### Question:
{question}

### Instructions:
- Generate ONLY the SQL query, no explanations.
- Do not include any markdown formatting like ```sql or ```.
- Use proper SQL syntax compatible with Sqlite.
- Use table aliases to prevent ambiguity when needed.
- Make sure the SQL query correctly answers the question.
    """
    
    # 构建请求体
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a SQL expert who generates accurate SQL queries."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        if "message" in result and "content" in result["message"]:
            # 清理响应内容，移除可能的 markdown 格式
            sql_query = result["message"]["content"].strip()
            sql_query = re.sub(r'^```sql|```$', '', sql_query, flags=re.MULTILINE).strip()
            return sql_query
        else:
            return f"API 响应格式错误: {result}"
            
    except requests.exceptions.RequestException as e:
        return f"请求失败: {str(e)}"


def compare_sql_queries(actual, expected):
    """比较两个 SQL 查询的相似性"""
    # 基本的文本清理和比较
    def clean_sql(sql):
        # 转换为小写
        sql = sql.lower()
        # 去除多余空格和换行
        sql = re.sub(r'\s+', ' ', sql)
        # 去除分号
        sql = sql.rstrip(';')
        return sql.strip()
    
    cleaned_actual = clean_sql(actual)
    cleaned_expected = clean_sql(expected)
    
    # 计算相似度分数（简单实现）
    # 实际应用中可以使用更复杂的 SQL 解析和比较方法
    if cleaned_actual == cleaned_expected:
        return 1.0, "完全匹配"
    elif any(keyword in cleaned_actual for keyword in ["select", "from", "where", "join", "order"]):
        # 检查主要关键词是否存在
        return 0.5, "部分匹配 - 包含主要 SQL 关键词"
    else:
        return 0.0, "不匹配"


def main():
    # 加载数据（处理 JSON Lines 格式）
    data = []
    try:
        with open("dusql/llm_train_en.json", 'r', encoding='utf-8') as f:
            # 读取每一行作为单独的 JSON 对象
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        sample = json.loads(line)
                        data.append(sample)
                    except json.JSONDecodeError as e:
                        print(f"警告: 第 {line_number} 行 JSON 解析失败: {str(e)}")
                        continue
    except Exception as e:
        print(f"加载数据失败: {str(e)}")
        sys.exit(1)
    
    if not data:
        print("没有加载到有效的测试数据")
        sys.exit(1)
    
    print(f"找到 {len(data)} 个训练样本")
    print(f"将使用前 {min(MAX_TEST_CASES, len(data))} 个样本进行测试")
    print(f"正在连接 Ollama 服务 ({OLLAMA_API_URL})，使用模型: {MODEL_NAME}\n")
    
    # 测试结果统计
    total_score = 0
    results = []
    
    # 遍历测试用例
    for i, sample in enumerate(data[:MAX_TEST_CASES]):
        try:
            input_text = sample.get("input", "")
            expected_output = sample.get("output", "")
            
            if not input_text or not expected_output:
                print(f"跳过测试用例 {i+1}: 缺少 input 或 output 字段")
                continue
            
            # 提取问题和 schema
            question = extract_question(input_text)
            schema = extract_schema(input_text)
            
            print(f"测试用例 {i+1}/{min(MAX_TEST_CASES, len(data))}:")
            print(f"问题: {question}")
            
            # 生成 SQL 查询
            start_time = time.time()
            actual_output = generate_sql_with_ollama(question, schema)
            end_time = time.time()
            
            print(f"生成耗时: {end_time - start_time:.2f} 秒")
            print(f"模型输出: {actual_output}")
            print(f"期望输出: {expected_output}")
            
            # 比较结果
            score, comment = compare_sql_queries(actual_output, expected_output)
            total_score += score
            
            print(f"评估结果: {score:.2f} - {comment}\n")
            
            # 保存结果
            results.append({
                "test_case": i+1,
                "question": question,
                "actual_output": actual_output,
                "expected_output": expected_output,
                "score": score,
                "comment": comment,
                "time": end_time - start_time
            })
            
            # 休眠 3 秒
            sleep(3)
            
        except Exception as e:
            print(f"处理测试用例 {i+1} 时出错: {str(e)}\n")
            continue
    
    # 输出汇总结果
    if results:
        average_score = total_score / len(results)
        print("\n=== 测试汇总 ===")
        print(f"测试用例总数: {len(results)}")
        print(f"平均得分: {average_score:.2f}")
        print("================")
        
        # 保存详细结果到文件
        try:
            with open("ollama_test_results.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print("详细结果已保存到 ollama_test_results.json")
        except Exception as e:
            print(f"保存结果失败: {str(e)}")
            
        # 打印结果
        from print import slow_print_file
        slow_print_file("ollama_test_results.json")
    else:
        print("没有成功处理任何测试用例")


if __name__ == "__main__":
    main()