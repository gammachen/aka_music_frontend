#!/usr/bin/env python3
"""
LangChain评估系统主启动脚本
基于Ollama本地模型的完整评估解决方案
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_ollama():
    """检查Ollama服务状态"""
    try:
        import requests
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            models = models_data.get("models", [])
            model_names = [m.get("name") for m in models]
            
            required_model = os.getenv("OLLAMA_MODEL", "gpt-3.5-turbo")
            full_model_name = f"{required_model}:latest"
            
            if full_model_name in model_names:
                print(f"✅ Ollama服务运行正常，找到模型: {full_model_name}")
                return True
            elif required_model in model_names:
                print(f"✅ Ollama服务运行正常，找到模型: {required_model}")
                return True
            else:
                print(f"⚠️  模型 {required_model} 未找到，可用模型: {model_names}")
                print(f"请运行: ollama pull {required_model}")
                
                # 使用第一个可用的模型作为备选
                if model_names:
                    selected_model = model_names[0]
                    print(f"使用备选模型: {selected_model}")
                    # 更新环境变量
                    os.environ["OLLAMA_MODEL"] = selected_model.replace(":latest", "")
                    return True
                else:
                    print("❌ 没有找到可用的模型")
                    return False
        else:
            print("❌ Ollama服务响应异常")
            return False
    except Exception as e:
        print(f"❌ 无法连接Ollama服务: {e}")
        print("请确保Ollama已启动: ollama serve")
        return False

def install_requirements():
    """安装依赖包"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def run_basic_tests():
    """运行基础测试"""
    try:
        from test_evaluators import test_string_evaluator
        
        print("\n" + "="*60)
        print("运行基础评估器测试...")
        print("="*60)
        
        test_string_evaluator()
        return True
        
    except Exception as e:
        print(f"❌ 基础测试失败: {e}")
        return False

def run_custom_evaluations():
    """运行自定义评估"""
    try:
        from custom_evaluators import test_custom_evaluators
        
        print("\n" + "="*60)
        print("运行自定义评估器测试...")
        print("="*60)
        
        test_custom_evaluators()
        return True
        
    except Exception as e:
        print(f"❌ 自定义评估失败: {e}")
        return False

def run_batch_evaluation():
    """运行批量评估"""
    try:
        from batch_runner import main as batch_main
        
        print("\n" + "="*60)
        print("运行批量评估...")
        print("="*60)
        
        batch_main()
        return True
        
    except Exception as e:
        print(f"❌ 批量评估失败: {e}")
        return False

def create_demo_dataset():
    """创建演示数据集"""
    demo_data = {
        "demo_qa": {
            "q1": {
                "input": "什么是机器学习？",
                "reference": "机器学习是人工智能的一个子领域，专注于开发能够从数据中学习并做出预测的算法和统计模型。"
            },
            "q2": {
                "input": "Python的主要特点是什么？",
                "reference": "Python的主要特点包括：简洁易读的语法、丰富的标准库、跨平台支持、动态类型系统、强大的第三方生态。"
            },
            "q3": {
                "input": "如何学习编程？",
                "reference": "学习编程的建议：1)选择一门语言开始；2)理解基础概念；3)动手实践项目；4)阅读优秀代码；5)参与开源社区。"
            }
        },
        "demo_comparison": {
            "c1": {
                "input": "解释什么是API",
                "prediction_a": "API是应用程序编程接口，允许不同软件系统之间进行通信。",
                "prediction_b": "API就是接口，让程序之间可以互相调用功能。"
            }
        }
    }
    
    with open("demo_dataset.json", "w", encoding="utf-8") as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 演示数据集已创建: demo_dataset.json")

def show_menu():
    """显示交互式菜单"""
    print("\n" + "="*60)
    print("LangChain评估系统 - 主菜单")
    print("="*60)
    print("1. 运行基础评估器测试")
    print("2. 运行自定义评估器测试")
    print("3. 运行批量评估")
    print("4. 创建演示数据集")
    print("5. 运行全部测试")
    print("0. 退出")
    print("-"*60)

def main():
    """主函数"""
    
    print("🚀 LangChain评估系统启动中...")
    
    # 检查环境
    if not check_ollama():
        return
    
    # 安装依赖
    if not install_requirements():
        return
    
    print("\n✅ 系统初始化完成")
    
    while True:
        show_menu()
        
        try:
            choice = input("\n请选择操作 [0-5]: ").strip()
            
            if choice == "1":
                run_basic_tests()
            elif choice == "2":
                run_custom_evaluations()
            elif choice == "3":
                run_batch_evaluation()
            elif choice == "4":
                create_demo_dataset()
            elif choice == "5":
                print("运行全部测试...")
                run_basic_tests()
                run_custom_evaluations()
                run_batch_evaluation()
            elif choice == "0":
                print("感谢使用！再见 👋")
                break
            else:
                print("❌ 无效选择，请重试")
                
        except KeyboardInterrupt:
            print("\n程序被中断")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    # 如果直接运行，检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            check_ollama()
        elif sys.argv[1] == "--install":
            install_requirements()
        elif sys.argv[1] == "--test":
            run_basic_tests()
        elif sys.argv[1] == "--batch":
            run_batch_evaluation()
        else:
            print("用法: python run_evaluation.py [--check|--install|--test|--batch]")
    else:
        main()