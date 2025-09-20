#!/usr/bin/env python3
"""
LangChain中OpenAI与ChatOpenAI详细对比示例
包含核心差异、使用场景、最佳实践
"""

from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime

# =============================================================================
# 1. 基础配置和初始化
# =============================================================================

class LLMComparisonDemo:
    """LLM对比演示类"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # 初始化两种不同类型的LLM
        self.openai_llm = OpenAI(
            openai_api_key=api_key,
            model_name="text-davinci-003",  # 传统文本补全模型
            temperature=0.7,
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        self.chatopenai_llm = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-3.5-turbo",  # 对话优化模型
            temperature=0.7,
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        self.gpt4_chat = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-4",
            temperature=0.7,
            max_tokens=512
        )

# =============================================================================
# 2. OpenAI (文本补全) 详细示例
# =============================================================================

class OpenAIDemo:
    """OpenAI文本补全演示"""
    
    def __init__(self, llm: OpenAI):
        self.llm = llm
    
    def basic_completion(self, prompt: str) -> str:
        """基础文本补全"""
        result = self.llm.invoke(prompt)
        return result
    
    def advanced_prompt_template(self):
        """高级Prompt模板使用"""
        
        # 创建结构化Prompt模板
        prompt_template = PromptTemplate(
            input_variables=["topic", "style", "length"],
            template="""请用{style}的风格写一篇关于{topic}的文章，字数控制在{length}字左右。
            
            文章要求：
            1. 开头要有吸引力的引言
            2. 包含具体案例和数据
            3. 结尾要有深度思考
            
            开始写作：""",
        )
        
        # 使用模板生成内容
        formatted_prompt = prompt_template.format(
            topic="人工智能对未来工作的影响",
            style="专业学术",
            length="500"
        )
        
        response = self.llm.invoke(formatted_prompt)
        return response
    
    def few_shot_learning(self):
        """Few-shot学习示例"""
        
        few_shot_prompt = """
        将以下英文翻译成中文：
        
        示例1：
        English: Hello, how are you?
        Chinese: 你好，你怎么样？
        
        示例2：
        English: What's your name?
        Chinese: 你叫什么名字？
        
        示例3：
        English: The weather is nice today.
        Chinese: 今天天气很好。
        
        现在翻译：
        English: I love programming and AI.
        Chinese: """
        
        result = self.llm.invoke(few_shot_prompt)
        return result
    
    def text_analysis_chain(self):
        """文本分析链"""
        
        analysis_prompt = PromptTemplate(
            input_variables=["text"],
            template="""请对以下文本进行情感分析：
            
            文本：{text}
            
            分析维度：
            1. 情感倾向（正面/负面/中性）
            2. 情感强度（1-10分）
            3. 主要情感关键词
            4. 建议的回应方式
            
            请以JSON格式输出结果。"""
        )
        
        # 创建处理链
        chain = analysis_prompt | self.llm | StrOutputParser()
        
        # 测试文本
        test_text = "这个产品质量太差了，完全不符合描述，我要退货！"
        result = chain.invoke({"text": test_text})
        
        return result

# =============================================================================
# 3. ChatOpenAI (对话模式) 详细示例
# =============================================================================

class ChatOpenAIDemo:
    """ChatOpenAI对话演示"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def basic_chat(self, messages: List[Dict[str, str]]) -> str:
        """基础对话"""
        # 转换消息格式
        chat_messages = [
            HumanMessage(content=msg["content"]) if msg["role"] == "user"
            else AIMessage(content=msg["content"]) if msg["role"] == "assistant"
            else SystemMessage(content=msg["content"])
            for msg in messages
        ]
        
        result = self.llm.invoke(chat_messages)
        return result.content
    
    def role_based_conversation(self):
        """角色设定对话"""
        
        messages = [
            SystemMessage(content="""你是一个专业的Python编程导师。
            你的特点：
            - 耐心细致，循序渐进
            - 提供代码示例和详细解释
            - 鼓励学生动手实践
            - 用简单易懂的语言解释复杂概念
            """),
            HumanMessage(content="我想学习Python的装饰器，能详细解释一下吗？"),
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def multi_turn_conversation(self):
        """多轮对话示例"""
        
        # 对话历史
        conversation_history = [
            SystemMessage(content="你是一个旅游规划专家"),
            HumanMessage(content="我想去日本旅游"),
            AIMessage(content="太好了！日本是个美丽的国家。请问您计划去哪些城市？预算多少？出行时间是什么时候？"),
            HumanMessage(content="我想去东京和京都，预算2万人民币，计划樱花季去")
        ]
        
        response = self.llm.invoke(conversation_history)
        return response.content
    
    def structured_output_demo(self):
        """结构化输出示例"""
        
        class TravelPlan(BaseModel):
            """旅行计划结构化输出"""
            destinations: List[str] = Field(description="目的地列表")
            duration_days: int = Field(description="旅行天数")
            budget_usd: float = Field(description="预算（美元）")
            highlights: List[str] = Field(description="行程亮点")
            recommendations: List[str] = Field(description="推荐活动")
        
        parser = JsonOutputParser(pydantic_object=TravelPlan)
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="你是一个专业的旅行规划师"),
            HumanMessage(content="""请为以下需求制定详细的旅行计划：
            
            需求：想去欧洲旅行，预算3000美元，时间10天，喜欢历史文化和美食
            
            请以JSON格式输出详细的旅行计划。""")
        ])
        
        chain = prompt | self.llm | parser
        result = chain.invoke({})
        return result

# =============================================================================
# 4. 实际应用场景对比
# =============================================================================

class ApplicationComparison:
    """应用场景对比"""
    
    def __init__(self, openai_llm: OpenAI, chat_llm: ChatOpenAI):
        self.openai_llm = openai_llm
        self.chat_llm = chat_llm
    
    def content_generation_comparison(self, topic: str):
        """内容生成对比"""
        
        # OpenAI方式
        openai_prompt = f"请写一篇关于{topic}的简短文章，200字左右："
        openai_result = self.openai_llm.invoke(openai_prompt)
        
        # ChatOpenAI方式
        chat_messages = [
            SystemMessage(content="你是一个专业的内容创作者"),
            HumanMessage(content=f"请写一篇关于{topic}的简短文章，200字左右")
        ]
        chat_result = self.chat_llm.invoke(chat_messages)
        
        return {
            "openai_result": openai_result,
            "chat_result": chat_result.content,
            "comparison": "OpenAI更适合单轮文本补全，ChatOpenAI更适合对话式内容生成"
        }
    
    def code_generation_comparison(self, requirement: str):
        """代码生成对比"""
        
        # OpenAI方式
        code_prompt = f"""请根据以下需求生成Python代码：
        
        需求：{requirement}
        
        要求：
        1. 代码要有详细注释
        2. 包含错误处理
        3. 提供使用示例
        
        生成的代码："""
        
        openai_code = self.openai_llm.invoke(code_prompt)
        
        # ChatOpenAI方式
        chat_messages = [
            SystemMessage(content="你是一个经验丰富的Python开发专家"),
            HumanMessage(content=f"请根据以下需求生成Python代码：{requirement}")
        ]
        
        chat_code = self.chat_llm.invoke(chat_messages)
        
        return {
            "openai_code": openai_code,
            "chat_code": chat_code.content,
            "analysis": "ChatOpenAI在代码生成中通常提供更好的上下文理解"
        }

# =============================================================================
# 5. 高级特性对比
# =============================================================================

class AdvancedFeaturesDemo:
    """高级特性演示"""
    
    def __init__(self, openai_llm: OpenAI, chat_llm: ChatOpenAI):
        self.openai_llm = openai_llm
        self.chat_llm = chat_llm
    
    def streaming_comparison(self):
        """流式输出对比"""
        
        async def demo_streaming():
            # OpenAI流式输出（需要特殊处理）
            prompt = "请详细解释机器学习中的梯度下降算法"
            
            # ChatOpenAI流式输出
            messages = [
                SystemMessage(content="你是一个AI专家"),
                HumanMessage(content="请详细解释机器学习中的梯度下降算法")
            ]
            
            print("=== ChatOpenAI 流式输出 ===")
            async for chunk in self.chat_llm.astream(messages):
                print(chunk.content, end="", flush=True)
        
        return asyncio.run(demo_streaming())
    
    def function_calling_demo(self):
        """函数调用演示（仅ChatOpenAI支持）"""
        
        from langchain_core.tools import StructuredTool
        
        def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
            """获取天气信息"""
            return {
                "location": location,
                "temperature": 22,
                "unit": unit,
                "description": "晴朗"
            }
        
        # 绑定函数到ChatOpenAI
        chat_with_tools = self.chat_llm.bind_tools([get_weather])
        
        messages = [
            HumanMessage(content="北京今天天气怎么样？")
        ]
        
        response = chat_with_tools.invoke(messages)
        return response

# =============================================================================
# 6. 性能和使用成本对比
# =============================================================================

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.metrics = []
    
    def benchmark_models(self, test_prompts: List[str]):
        """模型性能基准测试"""
        
        import time
        
        results = []
        
        for prompt in test_prompts:
            # OpenAI测试
            start_time = time.time()
            openai_result = self.openai_llm.invoke(prompt)
            openai_time = time.time() - start_time
            
            # ChatOpenAI测试
            start_time = time.time()
            chat_result = self.chat_llm.invoke([HumanMessage(content=prompt)])
            chat_time = time.time() - start_time
            
            results.append({
                "prompt": prompt[:50] + "...",
                "openai_time": openai_time,
                "chat_time": chat_time,
                "openai_tokens": len(prompt) + len(openai_result),
                "chat_tokens": len(prompt) + len(chat_result.content)
            })
        
        return results

# =============================================================================
# 7. 最佳实践建议
# =============================================================================

class BestPractices:
    """最佳实践指南"""
    
    @staticmethod
    def when_to_use_openai():
        """何时使用OpenAI"""
        return {
            "适用场景": [
                "单轮文本生成任务",
                "需要精确控制输出格式",
                "传统文本补全场景",
                "与旧系统集成"
            ],
            "优势": [
                "简单直接",
                "兼容性好",
                "成本相对较低"
            ]
        }
    
    @staticmethod
    def when_to_use_chatopenai():
        """何时使用ChatOpenAI"""
        return {
            "适用场景": [
                "多轮对话系统",
                "需要角色设定",
                "复杂交互逻辑",
                "需要函数调用",
                "需要流式响应"
            ],
            "优势": [
                "对话上下文管理",
                "结构化消息格式",
                "支持高级功能",
                "更好的用户体验"
            ]
        }

# =============================================================================
# 8. 实际测试运行示例
# =============================================================================

def run_comparison_demo():
    """运行完整对比演示"""
    
    # 注意：实际运行需要设置OPENAI_API_KEY环境变量
    api_key = "your-openai-api-key"
    
    # 初始化演示环境
    demo_env = LLMComparisonDemo(api_key)
    
    # OpenAI演示
    openai_demo = OpenAIDemo(demo_env.openai_llm)
    print("=== OpenAI 文本补全演示 ===")
    print("基本补全:", openai_demo.basic_completion("人工智能的未来发展"))
    print("高级模板:", openai_demo.advanced_prompt_template())
    
    # ChatOpenAI演示
    chat_demo = ChatOpenAIDemo(demo_env.chatopenai_llm)
    print("\n=== ChatOpenAI 对话演示 ===")
    print("角色对话:", chat_demo.role_based_conversation())
    print("多轮对话:", chat_demo.multi_turn_conversation())
    
    # 应用场景对比
    app_compare = ApplicationComparison(demo_env.openai_llm, demo_env.chatopenai_llm)
    print("\n=== 内容生成对比 ===")
    print(app_compare.content_generation_comparison("区块链技术"))
    
    # 最佳实践建议
    print("\n=== 最佳实践 ===")
    print("OpenAI使用场景:", BestPractices.when_to_use_openai())
    print("ChatOpenAI使用场景:", BestPractices.when_to_use_chatopenai())

if __name__ == "__main__":
    # 运行演示
    run_comparison_demo()