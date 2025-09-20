#!/usr/bin/env python3
"""
快速测试Chain示例脚本
"""

from langchain_ollama import OllamaLLM as Ollama

def test_ollama_connection():
    """测试Ollama连接"""
    try:
        llm = Ollama(
            model="gpt-3.5-turbo:latest",
            base_url="http://localhost:11434"
        )
        
        # 简单测试
        response = llm.invoke("你好，这是一个测试")
        print("✅ Ollama连接成功")
        print(f"测试响应: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Ollama连接失败: {e}")
        print("请确保:")
        print("1. Ollama服务已启动: ollama serve")
        print("2. 模型已安装: ollama pull gpt-3.5-turbo:latest")
        return False

if __name__ == "__main__":
    print("🔍 测试Ollama连接...")
    test_ollama_connection()