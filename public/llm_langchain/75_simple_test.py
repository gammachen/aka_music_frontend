#!/usr/bin/env python3
"""
简化测试版本，快速验证Ollama集成
"""

import warnings
warnings.filterwarnings('ignore')

try:
    from langchain_ollama import OllamaLLM as Ollama
    print("✅ langchain_community 导入成功")
    
    # 测试基础连接
    llm = Ollama(
        model="gpt-3.5-turbo:latest",
        base_url="http://localhost:11434",
        temperature=0.7,
        num_predict=50  # 限制输出长度以加快测试
    )
    
    print("✅ Ollama模型初始化成功")
    
    # 快速测试
    result = llm.invoke("你好，请用一句话介绍孙悟空")
    print("✅ 模型调用成功")
    print("结果:", result)
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请运行: pip install langchain-community")
    
except Exception as e:
    print(f"❌ 运行错误: {e}")
    print("请确保:")
    print("1. Ollama服务正在运行: ollama serve")
    print("2. 模型已拉取: ollama pull gpt-3.5-turbo:latest")