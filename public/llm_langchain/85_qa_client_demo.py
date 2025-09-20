#!/usr/bin/env python3
"""
Conversational QA服务客户端演示
演示如何使用ConversationalRetrievalChain服务
"""

import requests
import json
import time
from typing import Dict, List, Any

class QAClient:
    """问答服务客户端"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def create_session(self) -> str:
        """创建新会话"""
        response = requests.post(f"{self.base_url}/api/sessions")
        data = response.json()
        if data["success"]:
            return data["session_id"]
        else:
            raise Exception(data["error"])
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """获取所有会话"""
        response = requests.get(f"{self.base_url}/api/sessions")
        return response.json()["sessions"]
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话历史"""
        response = requests.get(f"{self.base_url}/api/sessions/{session_id}/history")
        return response.json()["history"]
    
    def ask_question(self, session_id: str, question: str) -> Dict[str, Any]:
        """提问"""
        response = requests.post(
            f"{self.base_url}/api/ask",
            json={"session_id": session_id, "question": question}
        )
        return response.json()
    
    def add_knowledge_text(self, texts: List[str], metadatas: List[Dict] = None) -> bool:
        """添加文本知识"""
        data = {"texts": texts}
        if metadatas:
            data["metadatas"] = metadatas
        
        response = requests.post(f"{self.base_url}/api/knowledge", json=data)
        return response.json()["success"]
    
    def add_knowledge_file(self, file_path: str) -> bool:
        """添加文件知识"""
        response = requests.post(
            f"{self.base_url}/api/knowledge",
            json={"file_path": file_path}
        )
        return response.json()["success"]


def interactive_demo():
    """交互式演示"""
    
    print("🤖 Conversational QA服务交互式演示")
    print("=" * 50)
    
    client = QAClient()
    
    # 检查服务状态
    if not client.health_check():
        print("❌ 服务未启动，请先运行: python 84_conversational_qa_service.py")
        return
    
    print("✅ 服务连接成功")
    
    # 创建或选择会话
    try:
        sessions = client.get_sessions()
        if sessions:
            print("\n📋 现有会话:")
            for i, session in enumerate(sessions, 1):
                print(f"  {i}. {session['session_id'][:8]}... (创建于 {session['created_at']})")
            
            choice = input("\n选择会话(序号)或按Enter创建新会话: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(sessions):
                session_id = sessions[int(choice) - 1]["session_id"]
            else:
                session_id = client.create_session()
                print(f"✅ 创建新会话: {session_id}")
        else:
            session_id = client.create_session()
            print(f"✅ 创建新会话: {session_id}")
            
    except Exception as e:
        print(f"❌ 会话创建失败: {e}")
        return
    
    # 添加示例知识（如果没有的话）
    try:
        # 检查是否需要添加知识
        response = client.ask_question(session_id, "什么是LangChain？")
        if "API请求失败" in response.get("answer", ""):
            print("📚 添加示例知识...")
            
            knowledge = [
                "LangChain是一个用于开发大语言模型应用的框架，提供了链式调用、记忆、代理等功能。",
                "ConversationalRetrievalChain是LangChain中的对话检索链，结合了对话记忆和文档检索功能。",
                "Chroma是一个开源的向量数据库，专门用于存储和检索文本嵌入向量，支持高效的相似度搜索。",
                "SQLite是一个轻量级的嵌入式关系型数据库，不需要独立的服务器进程，适合小型应用。",
                "Flask是一个轻量级的Python Web框架，使用Werkzeug工具箱和Jinja2模板引擎。",
                "向量嵌入是将文本转换为数值向量的技术，使得计算机可以理解和比较文本的语义相似度。",
                "会话记忆是指在对话系统中保存用户和AI历史对话的能力，使对话具有上下文连贯性。",
                "RESTful API是一种基于HTTP协议的API设计风格，使用标准的HTTP方法进行资源操作。"
            ]
            
            client.add_knowledge_text(knowledge)
            print("✅ 示例知识添加成功")
            
    except Exception as e:
        print(f"⚠️ 知识添加跳过: {e}")
    
    # 交互式问答
    print("\n💬 开始对话（输入 'quit' 退出，'history' 查看历史）")
    print("=" * 50)
    
    while True:
        try:
            question = input("\n❓ 你的问题: ").strip()
            
            if question.lower() == 'quit':
                break
            elif question.lower() == 'history':
                history = client.get_history(session_id)
                print("\n📋 对话历史:")
                for msg in history:
                    role = "👤 用户" if msg["role"] == "user" else "🤖 AI"
                    print(f"  {role}: {msg['content']}")
                continue
            elif not question:
                continue
            
            # 提问
            print("🤔 思考中...")
            response = client.ask_question(session_id, question)
            
            if response["success"]:
                print(f"💡 回答: {response['answer']}")
                
                # 显示来源文档（如果有）
                sources = response.get("source_documents", [])
                if sources:
                    print("\n📖 参考来源:")
                    for i, source in enumerate(sources[:3], 1):
                        content = source["content"][:100] + "..." if len(source["content"]) > 100 else source["content"]
                        print(f"  {i}. {content}")
            else:
                print(f"❌ 回答失败: {response['error']}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 请求错误: {e}")
    
    print("\n👋 感谢使用！")


def batch_demo():
    """批量测试演示"""
    
    print("🧪 批量测试演示")
    print("=" * 50)
    
    client = QAClient()
    
    if not client.health_check():
        print("❌ 服务未启动")
        return
    
    # 创建会话
    session_id = client.create_session()
    print(f"✅ 创建会话: {session_id}")
    
    # 添加测试知识
    knowledge = [
        "国家图书馆位于北京市海淀区中关村南大街，是中国最大的图书馆，提供借阅、咨询、展览等服务。",
        "故宫博物院是在紫禁城基础上建立的博物馆，收藏了明清两代的皇家文物和艺术品。",
        "图书馆的借阅规则：普通图书可借30天，期刊可借7天，逾期需缴纳滞纳金。",
        "博物馆的数字化展览让观众可以通过网络虚拟参观展厅，360度观看文物细节。",
        "古籍善本是图书馆的珍贵馆藏，包括宋版书、元版书等，具有重要历史和文化价值。",
        "考古发掘出土的文物经过清理、修复后，会在博物馆展出，让观众了解历史文化。",
        "图书馆的参考咨询服务帮助读者查找资料、解答问题，可通过现场、电话或网络咨询。",
        "博物馆的教育活动包括讲座、工作坊、亲子活动等，让公众更好地了解文化遗产。"
    ]

    client.add_knowledge_text(knowledge)
    print("✅ 添加图书馆与博物馆知识成功")
    
    # 批量提问
    questions = [
        "国家图书馆是什么时候建立的？",
        "故宫博物院有哪些著名的文物？",
        "上海图书馆的特色收藏是什么？",
        "中国国家博物馆的主要展览有哪些？",
        "如何在线查询图书馆的图书？"
    ]

    print("\n📝 开始图书馆与博物馆问答:")
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. {question}")
        try:
            response = client.ask_question(session_id, question)
            if response["success"]:
                print(f"   回答: {response['answer']}")
            else:
                print(f"   错误: {response['error']}")
        except Exception as e:
            print(f"   请求失败: {e}")
        
        time.sleep(1)
    
    # 显示会话历史
    print("\n📋 完整对话历史:")
    history = client.get_history(session_id)
    for msg in history:
        role = "👤 用户" if msg["role"] == "user" else "🤖 AI"
        print(f"  {role}: {msg['content']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        batch_demo()
    else:
        interactive_demo()