"""
LangChain Prompt模板实际应用示例
展示如何在真实项目中使用Prompt模板系统
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader

from prompt_templates import (
    PromptTemplateManager,
    PromptTemplateLibrary,
    AdvancedPromptTemplate,
    TemplateVariable,
    PromptType,
    ChatPromptBuilder
)


class CustomerServiceBot:
    """客服机器人示例"""
    
    def __init__(self):
        self.manager = PromptTemplateManager()
        self.llm = ChatOpenAI(temperature=0.7)
        self.memory = ConversationBufferMemory()
        self._setup_templates()
    
    def _setup_templates(self):
        """设置客服模板"""
        
        # 问候模板
        greeting_template = AdvancedPromptTemplate(
            template="""你是一个友好的客服助手{bot_name}。

客户信息：
- 姓名：{customer_name}
- 会员等级：{membership_level}
- 咨询类型：{inquiry_type}

请用温暖专业的语气问候客户，并询问如何帮助。""",
            variables=[
                TemplateVariable("bot_name", "string", default="小助手"),
                TemplateVariable("customer_name", "string", required=True),
                TemplateVariable("membership_level", "string", default="普通会员"),
                TemplateVariable("inquiry_type", "string", required=True)
            ],
            template_type=PromptType.CHAT,
            metadata={"category": "greeting", "version": "1.0"}
        )
        
        # 问题解答模板
        qa_template = AdvancedPromptTemplate(
            template="""作为客服助手，请基于以下信息回答客户问题：

知识库信息：
{knowledge_base}

客户历史：
{conversation_history}

当前问题：{question}

回答要求：
1. 使用礼貌友好的语气
2. 提供具体可行的解决方案
3. 如果无法解决，提供替代方案或转人工客服
4. 主动询问是否还有其他问题

回答：""",
            variables=[
                TemplateVariable("knowledge_base", "string", required=True),
                TemplateVariable("conversation_history", "string", default=""),
                TemplateVariable("question", "string", required=True)
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "qa", "version": "1.0"}
        )
        
        # 投诉处理模板
        complaint_template = AdvancedPromptTemplate(
            template="""处理客户投诉：

投诉内容：{complaint}
客户情绪：{emotion_level}
涉及产品：{product_name}

处理步骤：
1. 表达歉意和理解
2. 详细记录问题
3. 提供解决方案
4. 说明后续跟进

请给出专业的回复：""",
            variables=[
                TemplateVariable("complaint", "string", required=True),
                TemplateVariable("emotion_level", "string", default="一般"),
                TemplateVariable("product_name", "string", required=True)
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "complaint", "version": "1.0"}
        )
        
        # 注册模板
        self.manager.register_template("greeting", greeting_template, "customer_service")
        self.manager.register_template("qa", qa_template, "customer_service")
        self.manager.register_template("complaint", complaint_template, "customer_service")
    
    def greet_customer(self, customer_info: Dict[str, Any]) -> str:
        """问候客户"""
        greeting = self.manager.format_template("greeting", **customer_info)
        
        chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptBuilder.create_conversation_template(greeting)
        )
        
        return chain.run({})
    
    def answer_question(self, question: str, knowledge_base: str) -> str:
        """回答问题"""
        history = self.memory.load_memory_variables({}).get("history", "")
        
        prompt = self.manager.format_template(
            "qa",
            knowledge_base=knowledge_base,
            conversation_history=history,
            question=question
        )
        
        response = self.llm.predict(prompt)
        
        # 更新记忆
        self.memory.save_context(
            {"input": question},
            {"output": response}
        )
        
        return response
    
    def handle_complaint(self, complaint_data: Dict[str, Any]) -> str:
        """处理投诉"""
        prompt = self.manager.format_template("complaint", **complaint_data)
        
        response = self.llm.predict(prompt)
        
        # 记录投诉处理
        self._log_complaint(complaint_data, response)
        
        return response
    
    def _log_complaint(self, complaint_data: Dict[str, Any], response: str):
        """记录投诉处理日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'complaint_data': complaint_data,
            'response': response
        }
        
        with open('complaint_logs.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


class CodeReviewAssistant:
    """代码审查助手示例"""
    
    def __init__(self):
        self.manager = PromptTemplateManager()
        self.llm = ChatOpenAI(temperature=0.3)
        self._setup_templates()
    
    def _setup_templates(self):
        """设置代码审查模板"""
        
        # 代码分析模板
        analysis_template = AdvancedPromptTemplate(
            template="""请作为资深工程师审查以下代码：

代码语言：{language}
代码内容：
```{language}
{code}
```

审查重点：
- {focus_areas}

请从以下维度进行分析：
1. 代码质量
2. 性能优化
3. 安全性
4. 可读性
5. 最佳实践

请给出具体的改进建议：""",
            variables=[
                TemplateVariable("language", "string", required=True),
                TemplateVariable("code", "string", required=True),
                TemplateVariable("focus_areas", "string", default="通用审查")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "code_review", "version": "1.0"}
        )
        
        # 安全审查模板
        security_template = AdvancedPromptTemplate(
            template="""进行代码安全审查：

代码：
```{language}
{code}
```

已知漏洞类型：{vulnerability_types}

请识别：
1. 潜在的安全漏洞
2. 敏感信息泄露风险
3. 输入验证问题
4. 权限控制缺陷

安全报告：""",
            variables=[
                TemplateVariable("language", "string", required=True),
                TemplateVariable("code", "string", required=True),
                TemplateVariable("vulnerability_types", "string", default="SQL注入、XSS、CSRF")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "security_review", "version": "1.0"}
        )
        
        # 性能优化模板
        performance_template = AdvancedPromptTemplate(
            template="""分析代码性能：

代码片段：
```{language}
{code}
```

性能场景：{scenario}
数据规模：{data_scale}

请分析：
1. 时间复杂度
2. 空间复杂度
3. 瓶颈识别
4. 优化建议
5. 基准测试建议

性能分析报告：""",
            variables=[
                TemplateVariable("language", "string", required=True),
                TemplateVariable("code", "string", required=True),
                TemplateVariable("scenario", "string", required=True),
                TemplateVariable("data_scale", "string", default="中等规模")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "performance_review", "version": "1.0"}
        )
        
        self.manager.register_template("analysis", analysis_template, "code_review")
        self.manager.register_template("security", security_template, "code_review")
        self.manager.register_template("performance", performance_template, "code_review")
    
    def review_code(self, code_info: Dict[str, Any]) -> Dict[str, str]:
        """审查代码"""
        results = {}
        
        # 通用分析
        analysis_prompt = self.manager.format_template("analysis", **code_info)
        results['analysis'] = self.llm.predict(analysis_prompt)
        
        # 安全审查
        security_prompt = self.manager.format_template("security", **code_info)
        results['security'] = self.llm.predict(security_prompt)
        
        # 性能分析
        performance_prompt = self.manager.format_template("performance", **code_info)
        results['performance'] = self.llm.predict(performance_prompt)
        
        return results


class ContentCreationAssistant:
    """内容创作助手示例"""
    
    def __init__(self):
        self.manager = PromptTemplateManager()
        self.llm = ChatOpenAI(temperature=0.8)
        self._setup_templates()
    
    def _setup_templates(self):
        """设置内容创作模板"""
        
        # 博客文章模板
        blog_template = AdvancedPromptTemplate(
            template="""创作一篇博客文章：

主题：{topic}
目标读者：{audience}
文章长度：{length}
写作风格：{style}
关键词：{keywords}

文章结构：
1. 引人入胜的开头
2. 核心内容（分3-4个要点）
3. 实际案例或示例
4. 总结和行动建议

请创作完整的文章：""",
            variables=[
                TemplateVariable("topic", "string", required=True),
                TemplateVariable("audience", "string", default="技术从业者"),
                TemplateVariable("length", "string", default="中等长度"),
                TemplateVariable("style", "string", default="专业但易懂"),
                TemplateVariable("keywords", "string", default="")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "content_creation", "version": "1.0"}
        )
        
        # 产品描述模板
        product_description_template = AdvancedPromptTemplate(
            template="""为以下产品撰写描述：

产品名称：{product_name}
产品类型：{product_type}
目标用户：{target_users}
关键特性：{features}
价格区间：{price_range}

描述要求：
- 突出独特卖点
- 激发购买欲望
- SEO优化
- 适合电商平台

产品描述：""",
            variables=[
                TemplateVariable("product_name", "string", required=True),
                TemplateVariable("product_type", "string", required=True),
                TemplateVariable("target_users", "string", required=True),
                TemplateVariable("features", "string", required=True),
                TemplateVariable("price_range", "string", default="中等价位")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "content_creation", "version": "1.0"}
        )
        
        # 社交媒体帖子模板
        social_media_template = AdvancedPromptTemplate(
            template="""创作社交媒体内容：

平台：{platform}
内容主题：{theme}
目标互动：{interaction_goal}
品牌声音：{brand_voice}
话题标签：{hashtags}

内容要求：
- 符合平台特色
- 鼓励用户互动
- 包含号召性用语
- 适合病毒式传播

社交媒体内容：""",
            variables=[
                TemplateVariable("platform", "string", required=True),
                TemplateVariable("theme", "string", required=True),
                TemplateVariable("interaction_goal", "string", default="点赞和评论"),
                TemplateVariable("brand_voice", "string", default="年轻活力"),
                TemplateVariable("hashtags", "string", default="")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "content_creation", "version": "1.0"}
        )
        
        self.manager.register_template("blog", blog_template, "content_creation")
        self.manager.register_template("product_description", product_description_template, "content_creation")
        self.manager.register_template("social_media", social_media_template, "content_creation")
    
    def create_blog_post(self, blog_info: Dict[str, Any]) -> str:
        """创建博客文章"""
        prompt = self.manager.format_template("blog", **blog_info)
        return self.llm.predict(prompt)
    
    def create_product_description(self, product_info: Dict[str, Any]) -> str:
        """创建产品描述"""
        prompt = self.manager.format_template("product_description", **product_info)
        return self.llm.predict(prompt)
    
    def create_social_media_post(self, post_info: Dict[str, Any]) -> str:
        """创建社交媒体内容"""
        prompt = self.manager.format_template("social_media", **post_info)
        return self.llm.predict(prompt)


class RAGDocumentAssistant:
    """RAG文档助手示例"""
    
    def __init__(self, document_path: str):
        self.manager = PromptTemplateManager()
        self.llm = ChatOpenAI(temperature=0.7)
        self.document_path = document_path
        self.vectorstore = None
        self._setup_rag()
        self._setup_templates()
    
    def _setup_rag(self):
        """设置RAG系统"""
        # 加载文档
        loader = TextLoader(self.document_path, encoding='utf-8')
        documents = loader.load()
        
        # 文本分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # 创建向量存储
        embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings
        )
    
    def _setup_templates(self):
        """设置RAG模板"""
        
        # 文档问答模板
        doc_qa_template = AdvancedPromptTemplate(
            template="""基于提供的文档内容回答问题：

文档内容：
{context}

问题：{question}

回答要求：
1. 仅基于提供的文档内容
2. 如果信息不存在，明确说明
3. 引用相关段落
4. 提供页码或位置信息（如果有）

答案：""",
            variables=[
                TemplateVariable("context", "string", required=True),
                TemplateVariable("question", "string", required=True)
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "rag", "version": "1.0"}
        )
        
        # 文档摘要模板
        doc_summary_template = AdvancedPromptTemplate(
            template="""请对以下文档内容进行摘要：

文档内容：
{content}

摘要要求：
- 长度：{summary_length}
- 重点：{focus}
- 保留关键信息
- 适合快速阅读

摘要：""",
            variables=[
                TemplateVariable("content", "string", required=True),
                TemplateVariable("summary_length", "string", default="简短"),
                TemplateVariable("focus", "string", default="主要观点")
            ],
            template_type=PromptType.SIMPLE,
            metadata={"category": "rag", "version": "1.0"}
        )
        
        self.manager.register_template("doc_qa", doc_qa_template, "rag")
        self.manager.register_template("doc_summary", doc_summary_template, "rag")
    
    def query_document(self, question: str) -> str:
        """查询文档"""
        # 相似度搜索
        docs = self.vectorstore.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in docs])
        
        prompt = self.manager.format_template(
            "doc_qa",
            context=context,
            question=question
        )
        
        return self.llm.predict(prompt)
    
    def summarize_document(self, summary_config: Dict[str, Any]) -> str:
        """摘要文档"""
        # 获取文档内容
        docs = self.vectorstore.similarity_search("*", k=10)
        content = "\n".join([doc.page_content for doc in docs])
        
        summary_config["content"] = content
        prompt = self.manager.format_template("doc_summary", **summary_config)
        
        return self.llm.predict(prompt)


# 使用示例
if __name__ == "__main__":
    
    # 示例1：客服机器人
    print("=== 客服机器人示例 ===")
    cs_bot = CustomerServiceBot()
    
    # 问候客户
    greeting = cs_bot.greet_customer({
        "customer_name": "张先生",
        "membership_level": "VIP会员",
        "inquiry_type": "技术支持"
    })
    print("客服问候:", greeting)
    
    # 回答问题
    answer = cs_bot.answer_question(
        "如何重置密码？",
        "用户可以通过邮箱验证或手机验证码重置密码。具体步骤：1.点击登录页面的'忘记密码'..."
    )
    print("客服回答:", answer)
    
    # 示例2：代码审查助手
    print("\n=== 代码审查助手示例 ===")
    code_reviewer = CodeReviewAssistant()
    
    code_review = code_reviewer.review_code({
        "language": "python",
        "code": """
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
""",
        "focus_areas": "安全性和性能"
    })
    
    for category, result in code_review.items():
        print(f"{category.upper()}审查结果:")
        print(result)
        print("-" * 50)
    
    # 示例3：内容创作助手
    print("\n=== 内容创作助手示例 ===")
    content_creator = ContentCreationAssistant()
    
    # 创建博客文章
    blog_post = content_creator.create_blog_post({
        "topic": "LangChain Prompt模板最佳实践",
        "audience": "AI开发者",
        "length": "详细",
        "style": "技术深度",
        "keywords": "LangChain, Prompt工程, AI开发"
    })
    print("博客文章:", blog_post[:200] + "...")
    
    # 示例4：RAG文档助手
    print("\n=== RAG文档助手示例 ===")
    # 创建一个示例文档
    with open("sample_document.txt", "w", encoding="utf-8") as f:
        f.write("""
LangChain是一个用于开发由语言模型驱动的应用程序的框架。
它使得应用程序能够：
1. 具有上下文感知能力：将语言模型连接到上下文来源（提示指令、少量示例等）
2. 具有推理能力：依靠语言模型进行推理（关于如何根据提供的上下文进行回答）

主要组件包括：
- 模型I/O：与语言模型交互的接口
- 数据连接：与特定应用程序数据进行交互的接口
- 链：构建调用序列
- 代理：让链根据高级指令选择使用哪些工具
- 内存：在链的运行之间持久化应用程序状态
""")
    
    rag_assistant = RAGDocumentAssistant("sample_document.txt")
    
    # 查询文档
    answer = rag_assistant.query_document("LangChain的主要组件有哪些？")
    print("文档查询结果:", answer)
    
    # 清理示例文件
    import os
    if os.path.exists("sample_document.txt"):
        os.remove("sample_document.txt")