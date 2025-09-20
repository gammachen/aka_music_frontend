import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseChatMessageHistory, BaseMessage
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# 配置常量
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "chroma_db")

# 全局存储用户的对话链
user_chains: Dict[str, ConversationChain] = {}

# 设置OpenAI API Key - 请替换为您的实际API密钥
os.environ["OPENAI_API_KEY"] = "sk-your-openai-api-key-here"

class ChromaMessageHistory(BaseChatMessageHistory):
    """使用Chroma向量数据库存储对话历史的自定义实现"""
    
    def __init__(
        self,
        session_id: str,
        client: chromadb.PersistentClient,
        collection_name: str = "chat_history"
    ):
        self.session_id = session_id
        self.client = client
        
        # 创建或获取集合
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_message(self, message: BaseMessage) -> None:
        """添加消息到Chroma"""
        try:
            message_dict = {
                "type": message.type,
                "content": message.content
            }
            
            self.collection.add(
                documents=[message.content],
                metadatas=[{"type": message.type, "timestamp": str(datetime.now())}],
                ids=[str(uuid.uuid4())]
            )
        except Exception as e:
            print(f"Error adding message to Chroma: {e}")
    
    def clear(self) -> None:
        """清空所有消息"""
        try:
            # 获取所有文档ID并删除
            results = self.collection.get()
            if results and "ids" in results and results["ids"]:
                self.collection.delete(ids=results["ids"])
        except Exception as e:
            print(f"Error clearing Chroma collection: {e}")
    
    @property
    def messages(self) -> List[BaseMessage]:
        """获取所有消息"""
        try:
            results = self.collection.get()
            messages = []
            
            if results and "documents" in results and results["documents"]:
                for doc, metadata in zip(results["documents"], results["metadatas"]):
                    msg_type = metadata.get("type", "human")
                    if msg_type == "human":
                        messages.append(HumanMessage(content=doc))
                    elif msg_type == "ai":
                        messages.append(AIMessage(content=doc))
            
            return messages
        except Exception as e:
            print(f"Error getting messages from Chroma: {e}")
            return []
    
    def get_recent_messages(self, limit: int = 10) -> List[BaseMessage]:
        """获取最近的消息"""
        all_messages = self.messages
        return all_messages[-limit:] if len(all_messages) > limit else all_messages


def get_memory_for_user(user_id: str) -> ConversationBufferMemory:
    """为用户获取或创建记忆"""
    chroma_history = ChromaMessageHistory(user_id)
    
    memory = ConversationBufferMemory(
        chat_memory=chroma_history,
        memory_key="chat_history",
        return_messages=True,
        input_key="input",
        output_key="response"
    )
    
    return memory


def get_chain_for_user(user_id: str) -> ConversationChain:
    """为指定用户创建或获取对话链"""
    if user_id in user_chains:
        return user_chains[user_id]
    
    # 创建用户特定的Chroma存储
    user_persist_directory = os.path.join(CHROMA_PERSIST_DIRECTORY, user_id)
    os.makedirs(user_persist_directory, exist_ok=True)
    
    chroma_client = chromadb.PersistentClient(path=user_persist_directory)
    
    # 创建消息历史
    message_history = ChromaMessageHistory(
        session_id="default_session",
        client=chroma_client,
        collection_name="chat_history"
    )
    
    # 创建内存
    memory = ConversationBufferMemory(
        memory_key="history",
        chat_memory=message_history,
        return_messages=True
    )
    
    # 创建对话链
    llm = ChatOpenAI(
        temperature=0.7,
        model_name="gpt-3.5-turbo",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # 使用正确的prompt模板
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "你是一个友好的AI助手，可以记住之前的对话内容。"
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=True
    )
    
    user_chains[user_id] = chain
    return chain


class MemoryManager:
    """管理用户记忆的高级类"""
    
    def __init__(self):
        self.base_directory = CHROMA_PERSIST_DIRECTORY
    
    def get_user_client(self, user_id: str) -> chromadb.PersistentClient:
        """获取用户特定的Chroma客户端"""
        user_persist_directory = os.path.join(self.base_directory, user_id)
        os.makedirs(user_persist_directory, exist_ok=True)
        return chromadb.PersistentClient(path=user_persist_directory)
    
    def get_user_memory(self, user_id: str) -> ConversationBufferMemory:
        """获取用户的对话记忆"""
        client = self.get_user_client(user_id)
        
        message_history = ChromaMessageHistory(
            session_id="default_session",
            client=client,
            collection_name="chat_history"
        )
        
        return ConversationBufferMemory(
            memory_key="history",
            chat_memory=message_history,
            return_messages=True
        )
    
    def clear_user_memory(self, user_id: str) -> bool:
        """清空用户的对话记忆"""
        try:
            client = self.get_user_client(user_id)
            message_history = ChromaMessageHistory(
                session_id="default_session",
                client=client,
                collection_name="chat_history"
            )
            message_history.clear()
            return True
        except Exception as e:
            print(f"Error clearing user memory: {e}")
            return False
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的历史对话"""
        try:
            client = self.get_user_client(user_id)
            message_history = ChromaMessageHistory(
                session_id="default_session",
                client=client,
                collection_name="chat_history"
            )
            
            messages = message_history.messages[-limit:] if len(message_history.messages) > limit else message_history.messages
            
            return [
                {
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []