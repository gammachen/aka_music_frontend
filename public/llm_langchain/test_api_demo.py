#!/usr/bin/env python3
"""
LLMRequestsChain快速测试脚本
"""

import json
import time
import threading
from flask import Flask, jsonify
from langchain.chains import LLMRequestsChain, LLMChain
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import requests

# 快速启动Mock服务器
app = Flask(__name__)

# Mock数据
MOCK_DATA = {
    "suppliers": [
        {
            "id": "SUP001",
            "name": "华强北电子",
            "category": "electronics",
            "contact": "13800138001",
            "rating": 4.8,
            "products": ["手机配件", "电脑配件"]
        }
    ],
    "policies": {
        "maternity": {
            "title": "产假政策",
            "content": "女职工生育享受98天产假，产前可休假15天"
        }
    }
}

@app.route('/api/suppliers')
def get_suppliers():
    return jsonify(MOCK_DATA["suppliers"])

@app.route('/api/policies/<policy_type>')
def get_policy(policy_type):
    policy = MOCK_DATA["policies"].get(policy_type)
    return jsonify(policy or {"error": "Policy not found"})

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

def start_server():
    """启动服务器"""
    app.run(host='0.0.0.0', port=8000, debug=False)

def test_llm_requests():
    """测试LLMRequestsChain"""
    
    # 设置LLM
    llm = OpenAI(temperature=0.3)
    
    # 创建请求链
    template = """基于API响应回答问题：
    
    问题：{query}
    API响应：{requests_result}
    
    请用中文回答："""
    
    chain = LLMRequestsChain(
        llm_chain=LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                input_variables=["query", "requests_result"],
                template=template
            )
        )
    )
    
    # 测试查询
    try:
        result = chain.invoke({
            "query": "查询供应商信息",
            "url": "http://localhost:8000/api/suppliers"
        })
        print("✅ 供应商查询结果：")
        print(result['output'])
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")

if __name__ == "__main__":
    # 启动服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    
    print("🚀 开始测试LLMRequestsChain...")
    test_llm_requests()