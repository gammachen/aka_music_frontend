#!/usr/bin/env python3
"""
LangChain Chain 示例脚本 - 基于Ollama本地模型
基于79_chain.md文档构建的5种Chain演示
使用本地Ollama的gpt-3.5-turbo:latest模型
"""

import os
import json
from typing import List, Dict, Any
from langchain_ollama import OllamaLLM as Ollama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.chains import LLMChain, SequentialChain
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_extraction_chain
from langchain.chains import LLMMathChain

def setup_ollama_model():
    """初始化Ollama模型"""
    return Ollama(
        model="gpt-3.5-turbo:latest",
        base_url="http://localhost:11434",
        temperature=0.7
    )

class LangChainExamples:
    """LangChain示例类"""
    
    def __init__(self):
        self.llm = setup_ollama_model()
        
    def example_1_router_chain(self):
        """示例1：路由链 - 智能客服问题分类"""
        print("\n🧩 示例1：路由链 - 智能客服问题分类")
        print("-" * 50)
        
        # 定义提示模板
        flower_care_template = """你是一个经验丰富的园丁，擅长解答关于养花育花的问题。
                                下面是需要你来回答的问题:
                                {input}"""

        flower_deco_template = """你是一位网红插花大师，擅长解答关于鲜花装饰的问题。
                                下面是需要你来回答的问题:
                                {input}"""

        # 构建提示信息列表
        prompt_infos = [
            {
                "key": "flower_care",
                "description": "适合回答关于鲜花护理的问题",
                "template": flower_care_template,
            },
            {
                "key": "flower_decoration",
                "description": "适合回答关于鲜花装饰的问题",
                "template": flower_deco_template,
            }
        ]

        # 构建目标链字典
        chain_map = {}
        for info in prompt_infos:
            prompt = PromptTemplate(template=info['template'], input_variables=["input"])
            chain = LLMChain(llm=self.llm, prompt=prompt)
            chain_map[info["key"]] = chain

        # 构建路由链
        destinations = [f"{p['key']}: {p['description']}" for p in prompt_infos]
        router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations="\n".join(destinations))
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
            output_parser=RouterOutputParser(),
        )
        router_chain = LLMRouterChain.from_llm(self.llm, router_prompt)

        # 构建默认链
        default_prompt = PromptTemplate(template="{input}", input_variables=["input"])
        default_chain = LLMChain(llm=self.llm, prompt=default_prompt)

        # 路由函数
        def route_question(question):
            try:
                destination_info = router_chain.invoke({"input": question})
                destination = destination_info.get("destination", "default")
                
                if destination in chain_map:
                    return chain_map[destination].invoke({"input": question})
                else:
                    return default_chain.invoke({"input": question})
            except Exception as e:
                print(f"路由链执行错误: {e}")
                return default_chain.invoke({"input": question})

        # 测试用例
        test_questions = [
            "玫瑰花应该多久浇一次水？",
            "婚礼现场用玫瑰花和满天星怎么搭配？",
            "向日葵适合放在卧室吗？"
        ]
        
        for question in test_questions:
            print(f"\n问题: {question}")
            try:
                result = route_question(question)
                print(f"回答: {result.get('text', str(result))}")
            except Exception as e:
                print(f"执行失败: {e}")

    def example_2_sequential_chain(self):
        """示例2：顺序链 - 用户评论分析与多语言回复"""
        print("\n🔄 示例2：顺序链 - 用户评论分析与多语言回复")
        print("-" * 50)
        
        # 设置较低temperature以保证准确性
        llm = Ollama(
            model="gpt-3.5-turbo:latest",
            base_url="http://localhost:11434",
            temperature=0.3
        )
        
        # 子链1：将中文评论翻译成英文
        prompt_z2e = PromptTemplate.from_template("将下面的中文评论翻译为英文：\n\n{ch_review}")
        chain_z2e = LLMChain(llm=llm, prompt=prompt_z2e, output_key="en_review")

        # 子链2：总结英文评论
        prompt_es = PromptTemplate.from_template("Can you summarize the following review in 1 sentence: \n\n{en_review}")
        chain_es = LLMChain(llm=llm, prompt=prompt_es, output_key="summary")

        # 子链3：识别评论原语言
        prompt_lang = PromptTemplate.from_template("下面的评论使用的是什么语言？:\n\n{ch_review}")
        chain_lang = LLMChain(llm=llm, prompt=prompt_lang, output_key="language")

        # 子链4：用原语言生成回复
        prompt_reply = PromptTemplate.from_template(
            "使用指定语言编写对以下摘要的后续回复：\n\n摘要：{summary}\n\n语言：{language}"
        )
        chain_reply = LLMChain(llm=llm, prompt=prompt_reply, output_key="orig_reply")

        # 子链5：将回复翻译成中文
        prompt_e2z = PromptTemplate.from_template("将下面的文本翻译为中文：\n\n{orig_reply}")
        chain_e2z = LLMChain(llm=llm, prompt=prompt_e2z, output_key="ch_reply")

        # 构建顺序链
        overall_chain = SequentialChain(
            chains=[chain_z2e, chain_es, chain_lang, chain_reply, chain_e2z],
            input_variables=["ch_review"],
            output_variables=["en_review", "summary", "language", "orig_reply", "ch_reply"],
            verbose=True
        )

        # 测试
        chinese_review = "宫崎骏以往的作品剧作工整、形式统一，而且大多能让观众提炼出向善向美的中心思想。"
        
        try:
            result = overall_chain.invoke({"ch_review": chinese_review})
            print(f"原始评论: {chinese_review}")
            print(f"英文翻译: {result['en_review']}")
            print(f"摘要: {result['summary']}")
            print(f"语言: {result['language']}")
            print(f"原语言回复: {result['orig_reply']}")
            print(f"中文回复: {result['ch_reply']}")
        except Exception as e:
            print(f"顺序链执行错误: {e}")

    def example_3_document_chain(self):
        """示例3：文档问答链 - 基于文档的智能问答"""
        print("\n📊 示例3：文档问答链 - 基于文档的智能问答")
        print("-" * 50)
        
        # 初始化模型
        llm = Ollama(
            model="gpt-3.5-turbo:latest",
            base_url="http://localhost:11434",
            temperature=0.1
        )
        
        # 构建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "根据提供的上下文: {context} \n\n 回答问题: {input}"),
        ])

        # 构建文档链
        document_chain = create_stuff_documents_chain(llm, prompt)

        # 准备文档
        docs = [
            Document(page_content="杰西喜欢红色，但不喜欢黄色"),
            Document(page_content="贾马尔喜欢绿色，有一点喜欢红色"),
            Document(page_content="玛丽喜欢粉色和红色")
        ]

        # 测试用例
        questions = [
            "大家喜欢什么颜色?",
            "谁喜欢红色？",
            "杰西喜欢什么颜色？"
        ]
        
        for question in questions:
            print(f"\n问题: {question}")
            try:
                result = document_chain.invoke({"input": question, "context": docs})
                print(f"回答: {result}")
            except Exception as e:
                print(f"执行失败: {e}")

    def example_4_extraction_chain(self):
        """示例4：信息提取链 - 从文本中提取结构化信息"""
        print("\n🔍 示例4：信息提取链 - 从文本中提取结构化信息")
        print("-" * 50)
        
        # 设置较低temperature以保证准确性
        llm = Ollama(
            model="gpt-3.5-turbo:latest",
            base_url="http://localhost:11434",
            temperature=0
        )
        
        # 定义提取模式
        schema = {
            "properties": {
                "name": {"type": "string"},
                "height": {"type": "integer"},
                "hair_color": {"type": "string"},
            },
            "required": ["name", "height"],
        }

        # 创建提取链
        extraction_chain = create_extraction_chain(schema, llm)

        # 测试用例
        test_texts = [
            "亚历克斯身高 5 英尺。克劳迪娅比亚历克斯高 1 英尺，并且跳得比他更高。克劳迪娅是黑发女郎，亚历克斯是金发女郎。",
            "小明身高180厘米，小红身高165厘米，小明的头发是黑色的。",
            "张三和李四都是学生，张三身高175厘米，李四身高170厘米，张三的头发是棕色的。"
        ]
        
        for text in test_texts:
            print(f"\n文本: {text}")
            try:
                result = extraction_chain.invoke(text)
                print(f"提取结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except Exception as e:
                print(f"提取失败: {e}")

    def example_5_math_chain(self):
        """示例5：数学链 - 解决数学计算问题"""
        print("\n🧮 示例5：数学链 - 解决数学计算问题")
        print("-" * 50)
        
        # 初始化模型（数学问题需要准确性）
        llm = Ollama(
            model="gpt-3.5-turbo:latest",
            base_url="http://localhost:11434",
            temperature=0
        )
        
        # 创建数学链
        llm_math_chain = LLMMathChain.from_llm(llm)

        # 测试用例
        math_questions = [
            "100 * 20 + 100的结果是多少？",
            "计算圆的面积，如果半径是5厘米。请使用3.14作为圆周率。",
            "一个长方形的长是12米，宽是8米，求面积和周长。",
            "解方程：2x + 5 = 15"
        ]
        
        for question in math_questions:
            print(f"\n问题: {question}")
            try:
                result = llm_math_chain.invoke(question)
                print(f"答案: {result.get('answer', str(result))}")
            except Exception as e:
                print(f"计算失败: {e}")

    def run_all_examples(self):
        """运行所有示例"""
        print("🚀 LangChain Chain 示例演示")
        print("=" * 60)
        print("使用本地Ollama的gpt-3.5-turbo:latest模型")
        print("=" * 60)
        
        # 检查Ollama服务
        try:
            test_response = self.llm.invoke("Hello")
            print("✅ Ollama服务连接正常")
        except Exception as e:
            print(f"❌ Ollama服务连接失败: {e}")
            print("请确保Ollama服务已启动: ollama serve")
            return
        
        # 运行所有示例
        try:
            self.example_1_router_chain()
        except Exception as e:
            print(f"路由链示例失败: {e}")
            
        try:
            self.example_2_sequential_chain()
        except Exception as e:
            print(f"顺序链示例失败: {e}")
            
        try:
            self.example_3_document_chain()
        except Exception as e:
            print(f"文档链示例失败: {e}")
            
        try:
            self.example_4_extraction_chain()
        except Exception as e:
            print(f"提取链示例失败: {e}")
            
        try:
            self.example_5_math_chain()
        except Exception as e:
            print(f"数学链示例失败: {e}")

if __name__ == "__main__":
    # 安装必要的依赖
    try:
        import langchain_ollama
        import langchain_core
        import langchain
    except ImportError:
        print("请安装必要的依赖:")
        print("pip install langchain-ollama langchain-core langchain")
        exit(1)
    
    # 运行示例
    examples = LangChainExamples()
    examples.run_all_examples()