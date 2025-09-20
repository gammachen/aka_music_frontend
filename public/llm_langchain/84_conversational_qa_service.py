#!/usr/bin/env python3
"""
ConversationalRetrievalChain 问答服务完整实现
使用Chroma向量数据库存储问答数据，SQLite存储会话历史
Flask构建RESTful API服务
"""

import os
import json
import sqlite3
import threading
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from flask import Flask, request, jsonify
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document


class QAVectorStore:
    """向量数据存储管理"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        
        # 确保目录存在
        os.makedirs(persist_directory, exist_ok=True)
        
        # 初始化嵌入模型
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # 检查是否已有数据
        try:
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
            
            # 如果没有数据，添加一些示例
            if self.vectorstore._collection.count() == 0:
                self._add_initial_documents()
                
        except Exception:
            # 如果数据库不存在，创建并添加初始数据
            self._add_initial_documents()
    
    def _add_initial_documents(self):
        """添加初始文档"""
        initial_docs = [
            Document(
                page_content="国家图书馆是中国最大的综合性图书馆，成立于1909年，馆藏超过4000万册，包括古籍善本、民国文献、博士论文等重要资料。",
                metadata={"source": "library_info", "topic": "national_library"}
            ),
            Document(
                page_content="故宫博物院成立于1925年，是在明清两代皇宫基础上建立的博物馆，收藏文物超过186万件，包括绘画、陶瓷、玉器、青铜器等各类珍品。",
                metadata={"source": "museum_docs", "topic": "palace_museum"}
            ),
            Document(
                page_content="上海图书馆是中国第二大图书馆，馆藏超过5500万册，特色收藏包括家谱、碑帖、年画、名人手稿等，提供数字资源服务。",
                metadata={"source": "shanghai_library", "topic": "regional_library"}
            ),
            Document(
                page_content="中国国家博物馆位于天安门广场东侧，是世界上单体建筑面积最大的博物馆，收藏文物140余万件，展示中华文明5000年历史。",
                metadata={"source": "national_museum", "topic": "national_museum"}
            ),
            Document(
                page_content="图书馆借阅证办理流程：携带身份证到服务台填写申请表，缴纳押金后即可获得借阅证，可借阅图书10-20册，借期30天。",
                metadata={"source": "library_guide", "topic": "library_service"}
            ),
            Document(
                page_content="博物馆参观指南：建议提前预约，携带身份证件，参观时保持安静，禁止触摸文物，可使用语音导览或扫码获取展品信息。",
                metadata={"source": "museum_guide", "topic": "museum_service"}
            ),
            Document(
                page_content="古籍修复技术是图书馆的重要工作，包括纸张修补、字迹还原、装帧修复等，需要专业的修复师使用传统技艺和现代技术。",
                metadata={"source": "restoration_docs", "topic": "preservation"}
            ),
            Document(
                page_content="数字博物馆利用虚拟现实、增强现实等技术，让观众在线体验博物馆展览，360度观看文物细节，突破时空限制。",
                metadata={"source": "digital_museum", "topic": "digitalization"}
            )
        ]

        self.vectorstore = Chroma.from_documents(
            documents=initial_docs,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="library_museum_knowledge"
        )
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """添加文档到向量存储"""
        documents = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            metadata.update({"source": f"doc_{i}", "timestamp": datetime.now().isoformat()})
            documents.append(Document(page_content=text, metadata=metadata))
        
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
    
    def add_from_file(self, file_path: str):
        """从文件加载文档"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        
        # 文本分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        
        self.vectorstore.add_documents(splits)
        self.vectorstore.persist()
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """相似度搜索"""
        return self.vectorstore.similarity_search(query, k=k)
    
    def get_retriever(self):
        """获取检索器"""
        return self.vectorstore.as_retriever(search_kwargs={"k": 4})


class ConversationManager:
    """会话管理器 - 使用SQLite存储会话历史"""
    
    def __init__(self, db_path: str = "./qa_conversations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建消息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES conversations(session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO conversations (session_id) VALUES (?)",
            (session_id,)
        )
        
        conn.commit()
        conn.close()
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        
        # 更新会话时间
        cursor.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
            (session_id,)
        )
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """获取会话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (session_id, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        return [
            {"role": role, "content": content, "timestamp": timestamp}
            for role, content, timestamp in reversed(messages)
        ]
    
    def get_all_sessions(self) -> List[Dict]:
        """获取所有会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, created_at, updated_at 
            FROM conversations 
            ORDER BY updated_at DESC
        ''')
        
        sessions = cursor.fetchall()
        conn.close()
        
        return [
            {
                "session_id": session_id,
                "created_at": created_at,
                "updated_at": updated_at
            }
            for session_id, created_at, updated_at in sessions
        ]


class ConversationalQAService:
    """对话式问答服务"""
    
    def __init__(self):
        # 初始化模型
        self.llm = Ollama(
            model="gpt-3.5-turbo:latest",
            base_url="http://localhost:11434",
            temperature=0.7
        )
        
        # 初始化向量存储
        self.vector_store = QAVectorStore()
        
        # 初始化会话管理
        self.conversation_manager = ConversationManager()
        
        # 会话记忆存储
        self.memories = {}
    
    def create_chain(self, session_id: str) -> ConversationalRetrievalChain:
        """为会话创建对话链"""
        retriever = self.vector_store.get_retriever()
        
        # 创建或获取会话记忆
        if session_id not in self.memories:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            # 加载历史对话
            history = self.conversation_manager.get_conversation_history(session_id)
            for msg in history:
                if msg["role"] == "user":
                    memory.chat_memory.add_user_message(msg["content"])
                elif msg["role"] == "assistant":
                    memory.chat_memory.add_ai_message(msg["content"])
            
            self.memories[session_id] = memory
        
        # 创建对话链
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memories[session_id],
            return_source_documents=True,
            verbose=True
        )
        
        return chain
    
    def ask_question(self, session_id: str, question: str) -> Dict[str, Any]:
        """提问并获取回答"""
        try:
            # 创建对话链
            chain = self.create_chain(session_id)
            
            # 获取回答
            result = chain({"question": question})
            
            # 保存消息
            self.conversation_manager.add_message(session_id, "user", question)
            self.conversation_manager.add_message(session_id, "assistant", result["answer"])
            
            # 准备响应
            response = {
                "success": True,
                "session_id": session_id,
                "question": question,
                "answer": result["answer"],
                "source_documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result.get("source_documents", [])
                ]
            }
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    def add_knowledge(self, texts: List[str], metadatas: List[Dict] = None):
        """添加知识到向量存储"""
        self.vector_store.add_documents(texts, metadatas)
    
    def add_knowledge_from_file(self, file_path: str):
        """从文件添加知识"""
        self.vector_store.add_from_file(file_path)
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """获取会话历史"""
        return self.conversation_manager.get_conversation_history(session_id)
    
    def get_all_sessions(self) -> List[Dict]:
        """获取所有会话"""
        return self.conversation_manager.get_all_sessions()
    
    def create_new_session(self) -> str:
        """创建新会话"""
        return self.conversation_manager.create_session()


# ==================== Flask API服务 ====================

class QAServer:
    """Flask问答服务"""
    
    def __init__(self, host='0.0.0.0', port=5000):
        self.app = Flask(__name__)
        self.qa_service = ConversationalQAService()
        self.host = host
        self.port = port
        self.setup_routes()
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
        
        @self.app.route('/api/sessions', methods=['POST'])
        def create_session():
            """创建新会话"""
            try:
                session_id = self.qa_service.create_new_session()
                return jsonify({
                    "success": True,
                    "session_id": session_id,
                    "message": "会话创建成功"
                })
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/sessions', methods=['GET'])
        def get_sessions():
            """获取所有会话"""
            try:
                sessions = self.qa_service.get_all_sessions()
                return jsonify({"success": True, "sessions": sessions})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/sessions/<session_id>/history', methods=['GET'])
        def get_session_history(session_id):
            """获取会话历史"""
            try:
                history = self.qa_service.get_session_history(session_id)
                return jsonify({"success": True, "history": history})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/ask', methods=['POST'])
        def ask_question():
            """提问接口"""
            try:
                data = request.get_json()
                
                if not data or 'question' not in data:
                    return jsonify({"success": False, "error": "缺少问题参数"}), 400
                
                question = data['question']
                session_id = data.get('session_id')
                
                # 如果没有提供session_id，创建新会话
                if not session_id:
                    session_id = self.qa_service.create_new_session()
                
                result = self.qa_service.ask_question(session_id, question)
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/knowledge', methods=['POST'])
        def add_knowledge():
            """添加知识"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({"success": False, "error": "缺少数据"}), 400
                
                if 'texts' in data:
                    texts = data['texts']
                    metadatas = data.get('metadatas')
                    self.qa_service.add_knowledge(texts, metadatas)
                    return jsonify({"success": True, "message": "知识添加成功"})
                
                elif 'file_path' in data:
                    file_path = data['file_path']
                    self.qa_service.add_knowledge_from_file(file_path)
                    return jsonify({"success": True, "message": "文件知识添加成功"})
                
                else:
                    return jsonify({"success": False, "error": "缺少文本或文件路径"}), 400
                    
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
    
    def run(self):
        """运行服务"""
        print("🚀 启动Conversational QA服务...")
        print(f"📍 服务地址: http://{self.host}:{self.port}")
        print("📋 API文档:")
        print("  POST /api/sessions - 创建新会话")
        print("  GET  /api/sessions - 获取所有会话")
        print("  GET  /api/sessions/<id>/history - 获取会话历史")
        print("  POST /api/ask - 提问")
        print("  POST /api/knowledge - 添加知识")
        print("  GET  /health - 健康检查")
        
        self.app.run(host=self.host, port=self.port, debug=False)


# ==================== 测试和演示 ====================

def test_service():
    """测试服务"""
    
    # 启动服务
    server = QAServer(port=5001)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    time.sleep(3)  # 等待服务启动
    
    base_url = "http://localhost:5001"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health")
        print("✅ 健康检查通过")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return
    
    # 创建会话
    try:
        response = requests.post(f"{base_url}/api/sessions")
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ 创建会话: {session_id}")
    except Exception as e:
        print(f"❌ 创建会话失败: {e}")
        return
    
    # 添加测试知识
    test_knowledge = [
        "北京图书馆的前身是京师图书馆，成立于1912年，是中国最早的国立图书馆。",
        "台北故宫博物院收藏了从大陆运去的珍贵文物，包括翠玉白菜、肉形石等国宝。",
        "省级图书馆通常提供地方文献、家谱、古籍等特色馆藏，反映当地的文化历史。",
        "考古博物馆展示了从史前到近代的各种文物，帮助人们了解人类文明发展过程。",
        "图书馆的数字资源包括电子书、期刊数据库、学术论文等，可24小时在线访问。"
    ]

    try:
        response = requests.post(
            f"{base_url}/api/knowledge",
            json={"texts": test_knowledge}
        )
        print("✅ 添加图书馆与博物馆测试知识成功")
    except Exception as e:
        print(f"❌ 添加知识失败: {e}")
    
    # 测试问答
    test_questions = [
        "国家图书馆是什么时候建立的？",
        "故宫博物院收藏了哪些珍贵文物？",
        "如何办理图书馆借阅证？",
        "博物馆有哪些参观注意事项？",
        "图书馆和博物馆有什么区别？"
    ]

    for question in test_questions:
        try:
            response = requests.post(
                f"{base_url}/api/ask",
                json={
                    "session_id": session_id,
                    "question": question
                }
            )
            result = response.json()
            if result["success"]:
                print(f"\n❓ 问题: {question}")
                print(f"💡 回答: {result['answer']}")
            else:
                print(f"❌ 回答失败: {result['error']}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        time.sleep(1)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 运行测试模式...")
        test_service()
    else:
        print("🚀 启动服务模式...")
        server = QAServer()
        server.run()