#!/usr/bin/env python3
"""
测试Ollama设置和模型可用性的脚本
"""

import requests
import subprocess
import time
import os

def check_ollama_service():
    """检查Ollama服务是否运行"""
    try:
        response = requests.get("http://localhost:11434", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_model_available(model_name="gpt-3.5-turbo:latest"):
    """检查指定模型是否可用"""
    try:
        response = requests.post(
            "http://localhost:11434/api/show",
            json={"name": model_name},
            timeout=10
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def pull_model(model_name="gpt-3.5-turbo:latest"):
    """拉取模型"""
    print(f"正在拉取模型 {model_name}...")
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print("✅ 模型拉取成功")
            return True
        else:
            print(f"❌ 模型拉取失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ 模型拉取超时")
        return False
    except FileNotFoundError:
        print("❌ 未找到ollama命令，请确保已安装Ollama")
        return False

def start_ollama_service():
    """启动Ollama服务"""
    print("正在启动Ollama服务...")
    try:
        # 检查ollama命令是否存在
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
        
        # 在后台启动服务
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(3)  # 等待服务启动
        return check_ollama_service()
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ 未找到ollama命令或启动失败")
        return False

def main():
    """主函数：检查并设置Ollama环境"""
    print("🔍 检查Ollama环境...")
    
    # 检查服务
    if not check_ollama_service():
        print("🔄 Ollama服务未运行，尝试启动...")
        if not start_ollama_service():
            print("❌ 无法启动Ollama服务")
            print("请手动运行: ollama serve")
            return False
    else:
        print("✅ Ollama服务正在运行")
    
    # 检查模型
    model_name = "gpt-3.5-turbo:latest"
    if not check_model_available(model_name):
        print(f"🔄 模型 {model_name} 未找到，正在拉取...")
        if not pull_model(model_name):
            print("❌ 模型拉取失败")
            return False
    else:
        print(f"✅ 模型 {model_name} 可用")
    
    print("\n🎉 Ollama环境检查完成！")
    print("现在可以运行 sequential_chain_test.py 了")
    return True

if __name__ == "__main__":
    main()