LangChain 中的各种预设 Chain 能帮我们轻松搭建处理复杂任务的流程。下面通过 5 个实际项目案例，带你看看它们怎么用，并提供代码示例。

# 🧩 一、路由链（RouterChain）：智能客服问题分类

**场景描述**：  
一个鲜花电商的智能客服系统需要处理两类问题：**鲜花养护**（如浇水、施肥）和**鲜花装饰**（如搭配、场地布置）。需要根据用户问题类型，自动路由给不同的专业模型处理。

**解决方案**：  
使用 `LLMRouterChain` 和 `MultiPromptChain` 构建路由链。路由器链分析输入问题，选择最合适的提示模板，然后将问题发送给对应的目标链处理。

**代码示例**：

```python
from langchain.llms import OpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE

# 1. 为不同场景定义提示模板
flower_care_template = """你是一个经验丰富的园丁，擅长解答关于养花育花的问题。
                        下面是需要你来回答的问题:
                        {input}"""

flower_deco_template = """你是一位网红插花大师，擅长解答关于鲜花装饰的问题。
                        下面是需要你来回答的问题:
                        {input}"""

# 2. 构建提示信息列表
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
    }]

# 3. 初始化语言模型
llm = OpenAI(temperature=0)

# 4. 构建目标链字典
chain_map = {}
for info in prompt_infos:
    prompt = PromptTemplate(template=info['template'], input_variables=["input"])
    chain = LLMChain(llm=llm, prompt=prompt)
    chain_map[info["key"]] = chain

# 5. 构建路由链
destinations = [f"{p['key']}: {p['description']}" for p in prompt_infos]
router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations="\n".join(destinations))
router_prompt = PromptTemplate(
    template=router_template,
    input_variables=["input"],
    output_parser=RouterOutputParser(),
)
router_chain = LLMRouterChain.from_llm(llm, router_prompt)

# 6. 构建默认链（处理未分类问题）
default_chain = LLMChain(llm=llm, prompt=PromptTemplate(template="{input}", input_variables=["input"]))

# 7. 使用路由链（这里简化了MultiPromptChain的调用逻辑）
# 实际项目中，可使用LangChain的MultiPromptChain类
def route_question(question):
    # 路由链决定目的地
    destination_info = router_chain.invoke(question)
    destination = destination_info["destination"]
    # 根据目的地选择链并调用
    if destination in chain_map:
        return chain_map[destination].invoke(question)
    else:
        return default_chain.invoke(question)

# 测试
care_result = route_question("玫瑰花应该多久浇一次水？")
print(care_result)
deco_result = route_question("婚礼现场用玫瑰花和满天星怎么搭配？")
print(deco_result)
```

# 🔄 二、顺序链（SequentialChain）：用户评论分析与多语言回复

**场景描述**：  
电商平台需要自动化处理多语言用户评论：先翻译成英语，总结摘要，识别原语言，再用原语言生成回复，最后将回复翻译成中文记录。

**解决方案**：  
使用 `SequentialChain` 将多个 `LLMChain` 连接起来，每个链处理特定步骤，并将输出作为输入传递给后续链。

**代码示例**：

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain

# 初始化模型
llm = ChatOpenAI(temperature=0.7)

# 子链1：将中文评论翻译成英文
prompt_z2e = ChatPromptTemplate.from_template("将下面的中文评论翻译为英文：\n\n{ch_review}")
chain_z2e = LLMChain(llm=llm, prompt=prompt_z2e, output_key="en_review")

# 子链2：总结英文评论
prompt_es = ChatPromptTemplate.from_template("Can you summarize the following review in 1 sentence: \n\n{en_review}")
chain_es = LLMChain(llm=llm, prompt=prompt_es, output_key="summary")

# 子链3：识别评论原语言
prompt_lang = ChatPromptTemplate.from_template("下面的评论使用的是什么语言？:\n\n{ch_review}")
chain_lang = LLMChain(llm=llm, prompt=prompt_lang, output_key="language")

# 子链4：用原语言生成回复
prompt_reply = ChatPromptTemplate.from_template(
    "使用指定语言编写对以下摘要的后续回复：\n\n摘要：{summary}\n\n语言：{language}"
)
chain_reply = LLMChain(llm=llm, prompt=prompt_reply, output_key="orig_reply")

# 子链5：将回复翻译成中文
prompt_e2z = ChatPromptTemplate.from_template("将下面的文本翻译为中文：\n\n{orig_reply}")
chain_e2z = LLMChain(llm=llm, prompt=prompt_e2z, output_key="ch_reply")

# 构建顺序链
overall_chain = SequentialChain(
    chains=[chain_z2e, chain_es, chain_lang, chain_reply, chain_e2z],
    input_variables=["ch_review"],
    output_variables=["en_review", "summary", "language", "orig_reply", "ch_reply"],
    verbose=True  # 显示详细执行过程
)

# 测试
chinese_review = "宫崎骏以往的作品剧作工整、形式统一，而且大多能让观众提炼出向善向美的中心思想。它们当然是美好的作品，但我却不能信任真空的、过度的美好。更不信任这是创作者灵魂的真实面。"
result = overall_chain.invoke(chinese_review)
print("最终中文回复:", result['ch_reply'])
```

# 📊 三、文档问答链（create_stuff_documents_chain）：基于文档的智能问答

**场景描述**：  
企业有大量内部文档（如产品手册、公司政策），希望构建一个问答系统，能根据提供的文档内容准确回答员工的问题。

**解决方案**：  
使用 `create_stuff_documents_chain`。它将提供的文档列表全部格式化成提示词，然后传递给 LLM 生成答案。**需要注意**确保所有文档内容总和不超过 LLM 的上下文窗口限制。

**代码示例**：

```python
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

# 初始化模型和提示模板
llm = ChatOpenAI(model="gpt-3.5-turbo")
prompt = ChatPromptTemplate.from_messages([
    ("system", "根据提供的上下文: {context} \n\n 回答问题: {input}"),
])

# 构建文档链
document_chain = create_stuff_documents_chain(llm, prompt)

# 准备文档（模拟从数据库或文件加载）
docs = [
    Document(page_content="杰西喜欢红色，但不喜欢黄色"),
    Document(page_content="贾马尔喜欢绿色，有一点喜欢红色"),
    Document(page_content="玛丽喜欢粉色和红色")
]

# 提问并传入文档作为上下文
question = "大家喜欢什么颜色?"
answer = document_chain.invoke({"input": question, "context": docs})
print(answer)
```

# 🔍 四、信息提取链（create_extraction_chain）：从文本中结构化提取信息

**场景描述**：  
从新闻稿、产品描述或用户反馈等非结构化文本中，自动化提取预定义的结构化信息（如人物属性、事件要素、产品规格）。

**解决方案**：  
使用 `create_extraction_chain` 并配合 OpenAI 的函数调用功能。定义一个 JSON Schema 来指定要提取的属性及其类型。

**代码示例**：

```python
from langchain.chains import create_extraction_chain
from langchain_openai import ChatOpenAI

# 定义要提取的信息模式（JSON Schema）
schema = {
    "properties": {
        "name": {"type": "string"},
        "height": {"type": "integer"},
        "hair_color": {"type": "string"},
    },
    "required": ["name", "height"],  # 必须提取的字段
}

# 输入文本
input_text = """亚历克斯身高 5 英尺。克劳迪娅比亚历克斯高 1 英尺，并且跳得比他更高。克劳迪娅是黑发女郎，亚历克斯是金发女郎。"""

# 初始化模型并创建提取链
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
extraction_chain = create_extraction_chain(schema, llm)

# 执行提取
result = extraction_chain.invoke(input_text)
print(result)
```

# 🧮 五、数学链（LLMMathChain）：解决数学计算问题

**场景描述**：  
教育类应用或数据分析工具需要处理用户输入的数学问题，并将自然语言描述的数学问题转换为可计算的表达式，最后给出答案和解析过程。

**解决方案**：  
使用 `LLMMathChain`。它将自然语言问题转换为数学表达式，然后使用 Python 的 `numexpr` 库安全地计算表达式结果。

**代码示例**：

```python
from langchain_openai import OpenAI
from langchain.chains import LLMMathChain

# 初始化模型和数学链
llm = OpenAI(temperature=0)  # 数学问题通常设置 temperature=0 以保证准确性
llm_math_chain = LLMMathChain.from_llm(llm)

# 执行数学计算
result = llm_math_chain.invoke("100 * 20 + 100的结果是多少？")
print(result)  # 输出: {'question': '100 * 20 + 100的结果是多少？', 'answer': 'Answer: 2100'}

# 也可以处理更复杂的问题
complex_result = llm_math_chain.invoke("计算圆的面积，如果半径是5厘米。请使用3.14作为圆周率。")
print(complex_result)
```

> ⚠️ **注意**：使用 `LLMMathChain` 需要先安装 `numexpr` 库：
> ```bash
> pip install numexpr
> ```

# 🔄 六、转换链（TransformChain）：数据格式转换与处理

**场景描述**：
在AI应用中经常需要将一种数据格式转换为另一种格式，或者对数据进行清洗、标准化处理。例如将用户输入的自然语言转换为SQL查询语句，将非结构化文本转换为标准JSON格式，或者将复杂的数据结构简化为更易处理的形式。

**解决方案**：
使用 `TransformChain` 可以在链式处理过程中插入自定义的数据转换逻辑。它接收输入数据，应用转换函数，然后输出转换后的数据，无缝集成到整个处理流程中。

**代码示例**：

```python
from langchain.chains import TransformChain, SequentialChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json
import re

# 初始化模型
llm = ChatOpenAI(temperature=0.3)

# 转换链1：清理用户输入
def clean_input(inputs):
    """清理和标准化用户输入"""
    text = inputs["raw_input"]
    # 移除多余空格和特殊字符
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return {"cleaned_input": cleaned}

cleaning_chain = TransformChain(
    input_variables=["raw_input"],
    output_variables=["cleaned_input"],
    transform=clean_input
)

# 转换链2：将自然语言转换为JSON格式
def text_to_json(inputs):
    """将自然语言描述转换为结构化JSON"""
    text = inputs["cleaned_input"]
    # 这里可以添加复杂的转换逻辑
    # 示例：提取关键信息并构建JSON
    json_structure = {
        "original_text": text,
        "length": len(text),
        "word_count": len(text.split()),
        "processed": True
    }
    return {"json_output": json.dumps(json_structure, ensure_ascii=False)}

json_transform_chain = TransformChain(
    input_variables=["cleaned_input"],
    output_variables=["json_output"],
    transform=text_to_json
)

# 使用转换链构建完整流程
full_chain = SequentialChain(
    chains=[cleaning_chain, json_transform_chain],
    input_variables=["raw_input"],
    output_variables=["json_output"],
    verbose=True
)

# 测试转换链
result = full_chain.invoke({
    "raw_input": "  这是一个需要清理的  用户输入文本，包含  多余空格和格式问题  "
})
print("转换结果:", result["json_output"])
```

**高级应用示例**：SQL查询生成

```python
# 转换链：将自然语言转换为SQL查询
def nl_to_sql(inputs):
    """自然语言转SQL查询"""
    nl_query = inputs["user_query"]
    table_schema = inputs["table_schema"]
    
    # 构建转换后的输入
    sql_prompt = f"""
    根据以下数据库表结构，将用户的自然语言查询转换为SQL语句：
    
    表结构：{table_schema}
    用户查询：{nl_query}
    
    请只返回SQL语句，不要添加解释。
    """
    
    return {"sql_prompt": sql_prompt}

sql_transform_chain = TransformChain(
    input_variables=["user_query", "table_schema"],
    output_variables=["sql_prompt"],
    transform=nl_to_sql
)

# 构建完整的SQL生成链
sql_generation_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        template="{sql_prompt}",
        input_variables=["sql_prompt"]
    ),
    output_key="sql_query"
)

# 组合成完整流程
sql_workflow = SequentialChain(
    chains=[sql_transform_chain, sql_generation_chain],
    input_variables=["user_query", "table_schema"],
    output_variables=["sql_query"],
    verbose=True
)

# 测试SQL生成
result = sql_workflow.invoke({
    "user_query": "查找所有价格大于100的商品",
    "table_schema": "products(id, name, price, category)"
})
print("生成的SQL:", result["sql_query"])
```

# 📝 七、总结链（SummarizeChain）：长文本智能摘要

**场景描述**：
在处理大量文本内容时（如新闻文章、研究报告、会议记录、长篇文档），需要快速提取核心要点和关键信息，生成简洁准确的摘要。这在内容管理、信息检索、知识管理等场景中尤为重要。

**解决方案**：
使用总结链可以将冗长的文本内容压缩为精炼的摘要。支持多种总结策略：
- **MapReduce**：将长文本分割成小块，分别总结后再合并
- **Refine**：逐步精炼，每次基于前一步的总结继续优化
- **Stuff**：一次性处理所有文本（适用于较短的文本）

**代码示例**：

```python
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# 初始化模型
llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")

# 示例：长文本总结
long_text = """
人工智能（AI）是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。人工智能可以对人的意识、思维的信息过程的模拟。
人工智能不是人的智能，但能像人那样思考、也可能超过人的智能。人工智能是一门极富挑战性的科学，从事这项工作的人必须懂得计算机知识、心理学和哲学。
人工智能是包括十分广泛的科学，它由不同的领域组成，如机器学习、计算机视觉等等。总的说来，人工智能研究的一个主要目标是使机器能够胜任一些通常需要人类智能才能完成的复杂工作。
"""

# 创建文档对象
doc = Document(page_content=long_text)

# 方法1：使用Stuff链（适合短文本）
chain_stuff = load_summarize_chain(llm, chain_type="stuff")
summary_stuff = chain_stuff.invoke([doc])
print("Stuff总结:", summary_stuff["output_text"])

# 方法2：使用MapReduce链（适合长文本）
chain_mapreduce = load_summarize_chain(llm, chain_type="map_reduce")
summary_mapreduce = chain_mapreduce.invoke([doc])
print("MapReduce总结:", summary_mapreduce["output_text"])

# 方法3：使用Refine链（逐步精炼）
chain_refine = load_summarize_chain(llm, chain_type="refine")
summary_refine = chain_refine.invoke([doc])
print("Refine总结:", summary_refine["output_text"])
```

**高级应用：多文档总结**

```python
# 处理多个相关文档
documents = [
    Document(page_content="苹果公司发布了新一代iPhone，采用了全新的A17芯片，性能提升显著。"),
    Document(page_content="新款iPhone的相机系统得到全面升级，支持更先进的夜间拍摄模式。"),
    Document(page_content="电池续航能力也有所提升，满足用户一整天的使用需求。"),
    Document(page_content="售价方面，新款iPhone起售价为999美元，比上一代略有上涨。")
]

# 创建总结链处理多个文档
multi_doc_chain = load_summarize_chain(llm, chain_type="map_reduce")
combined_summary = multi_doc_chain.invoke(documents)
print("多文档综合摘要:", combined_summary["output_text"])

# 自定义总结提示模板
custom_prompt = """
请根据以下内容生成一个简洁的摘要：

{context}

要求：
1. 提取关键信息点
2. 保持客观中立
3. 控制在50字以内

摘要："""

prompt = PromptTemplate(template=custom_prompt, input_variables=["context"])
custom_chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
custom_summary = custom_chain.invoke([doc])
print("自定义摘要:", custom_summary["output_text"])
```

# 💡 使用 LangChain Chain 的实用建议（2024升级版）

## 🎯 选型指南
1. **任务复杂度匹配**：
   - 简单任务：单个LLMChain
   - 中等复杂度：SequentialChain或TransformChain
   - 复杂决策：RouterChain
   - 文档处理：文档问答链+总结链组合

2. **性能优化策略**：
   - **批处理**：对相似任务使用批处理减少API调用
   - **缓存**：使用LangChain的缓存机制避免重复计算
   - **异步处理**：使用异步链提高并发性能
   - **流式响应**：对于长文本生成使用流式输出提升用户体验

## 🛠️ 开发最佳实践

1. **模块化设计**：
   ```python
   # 将常用链封装为可重用组件
   class TextProcessor:
       def __init__(self, llm):
           self.summarizer = load_summarize_chain(llm, chain_type="map_reduce")
           self.translator = LLMChain(...)  # 翻译链
           
       def process_document(self, text):
           # 组合多个链完成复杂任务
           summary = self.summarizer.invoke([Document(page_content=text)])
           translation = self.translator.invoke({"text": summary})
           return translation
   ```

2. **错误处理与重试**：
   ```python
   from langchain.chains.base import Chain
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
   def safe_chain_invoke(chain, inputs):
       return chain.invoke(inputs)
   ```

3. **监控与日志**：
   - 使用LangSmith进行链执行跟踪
   - 记录关键指标：延迟、token用量、成功率
   - 设置告警机制监控异常

4. **版本管理**：
   - 使用LangChain的序列化功能保存链配置
   - 建立提示词版本控制
   - 实施A/B测试评估不同链配置效果

## 🔧 常见陷阱与解决方案

1. **Token限制**：
   - 问题：文档链超出上下文长度
   - 解决：使用MapReduce策略或文本分割器

2. **响应格式**：
   - 问题：输出格式不一致
   - 解决：使用结构化输出解析器或函数调用

3. **性能瓶颈**：
   - 问题：顺序链处理时间过长
   - 解决：并行化独立任务，使用异步处理

4. **成本控制**：
   - 问题：API调用费用过高
   - 解决：实施缓存策略，优化提示词减少token用量

## 🚀 进阶组合模式

```python
# 构建复杂工作流的示例
class IntelligentDocumentProcessor:
    """智能文档处理工作流"""
    
    def __init__(self, llm):
        self.router = LLMRouterChain(...)  # 路由不同类型文档
        self.extractor = create_extraction_chain(...)  # 提取关键信息
        self.summarizer = load_summarize_chain(...)  # 生成摘要
        self.transformer = TransformChain(...)  # 格式转换
        
    def process_document(self, document, query=None):
        # 1. 路由到合适的处理链
        route = self.router.invoke({"input": document})
        
        # 2. 提取结构化信息
        extracted = self.extractor.invoke(document)
        
        # 3. 生成摘要
        summary = self.summarizer.invoke([Document(page_content=document)])
        
        # 4. 转换为标准格式
        final_result = self.transformer.invoke({
            "extracted": extracted,
            "summary": summary,
            "query": query
        })
        
        return final_result
```

# 🔗 八、API链（APIChain）：智能API调用与数据获取

**场景描述**：
在AI应用中，经常需要让大语言模型能够智能地调用外部API来获取实时数据、执行操作或与外部系统集成。例如查询天气信息、获取股票数据、调用企业内部服务、查询用户信息等。传统方式需要手动编写API调用逻辑，而API链可以让LLM自动决定何时以及如何调用API。

**解决方案**：
使用 `APIChain` 可以让LLM根据用户意图自动生成API调用，处理响应数据，并以自然语言形式返回结果。它支持RESTful API调用，可以处理认证、参数构建、响应解析等复杂逻辑。

**代码示例**：

```python
from langchain.chains import APIChain
from langchain_openai import OpenAI

# 初始化模型和API链
llm = OpenAI(temperature=0)

# 示例1：查询天气信息
weather_api_docs = """
BASE URL: https://api.openweathermap.org/data/2.5/

API文档:
- 获取当前天气: GET /weather?q={city}&appid={api_key}&units=metric
- 获取天气预报: GET /forecast?q={city}&appid={api_key}&units=metric
- 响应格式: JSON包含温度、湿度、天气描述等信息
"""

weather_chain = APIChain.from_llm_and_api_docs(
    llm=llm,
    api_docs=weather_api_docs,
    verbose=True
)

# 测试天气查询
result = weather_chain.invoke("北京现在的天气怎么样？")
print("天气信息:", result)
```

**高级应用：自定义API集成**

```python
# 示例2：集成多个API服务
class SmartAPIChain:
    def __init__(self, llm):
        self.llm = llm
        self.setup_chains()
    
    def setup_chains(self):
        # 供应商查询API
        supplier_docs = """
        BASE URL: http://localhost:8000/api
        
        端点说明:
        - GET /suppliers?name={name} - 按名称搜索供应商
        - GET /suppliers/{id} - 获取供应商详细信息
        - GET /suppliers/category/{category} - 按类别查询供应商
        """
        
        self.supplier_chain = APIChain.from_llm_and_api_docs(
            llm=self.llm,
            api_docs=supplier_docs,
            headers={"Authorization": "Bearer mock-token"},
            verbose=True
        )
    
    def query_suppliers(self, query):
        return self.supplier_chain.invoke(query)

# 使用示例
api_processor = SmartAPIChain(llm)
result = api_processor.query_suppliers("查找电子产品类别的供应商")
```

# 🌐 九、LLMRequestsChain：智能HTTP请求链

**场景描述**：
当需要让AI模型能够理解和执行HTTP请求，处理复杂的Web服务交互时，LLMRequestsChain提供了更灵活的解决方案。它可以处理GET、POST等各种HTTP方法，支持自定义headers、认证、参数处理等，适用于构建智能客服、数据查询助手等应用。

**解决方案**：
使用 `LLMRequestsChain` 可以让用户用自然语言描述他们想要的操作，AI会自动构建合适的HTTP请求，调用API，并解析返回的数据以自然语言形式呈现给用户。

**代码示例**：

```python
from langchain.chains import LLMRequestsChain
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

# 初始化模型
llm = OpenAI(temperature=0)

# 创建请求链模板
template = """在 >>> 和 <<< 之间是API的响应。
请根据用户的请求{query}，从响应中提取相关信息并以自然语言回答。

>>> {requests_result} <<<
请用中文回答用户的问题。"""

PROMPT = PromptTemplate(
    input_variables=["query", "requests_result"],
    template=template,
)

# 创建LLMRequestsChain
requests_chain = LLMRequestsChain(
    llm_chain=LLMChain(llm=llm, prompt=PROMPT),
    verbose=True
)

# 示例：查询用户信息
result = requests_chain.invoke({
    "query": "查询员工张三的剩余年假天数",
    "url": "http://localhost:8000/api/employees/张三/leave-balance"
})
print("查询结果:", result["output"])
```

**综合应用：智能企业助手**

```python
class EnterpriseSmartAssistant:
    """企业智能助手 - 整合多种API服务"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.llm = OpenAI(temperature=0.3)
        self.setup_chains()
    
    def setup_chains(self):
        """设置各种API调用链"""
        
        # 员工信息查询链
        employee_template = """根据API响应回答关于员工的问题。
        
        用户问题: {query}
        API响应: {requests_result}
        
        请以简洁明了的中文回答。"""
        
        self.employee_chain = LLMRequestsChain(
            llm_chain=LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    input_variables=["query", "requests_result"],
                    template=employee_template
                )
            )
        )
        
        # 政策查询链
        policy_template = """根据API响应解释相关政策。
        
        用户问题: {query}
        政策内容: {requests_result}
        
        请用通俗易懂的中文解释政策要点。"""
        
        self.policy_chain = LLMRequestsChain(
            llm_chain=LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    input_variables=["query", "requests_result"],
                    template=policy_template
                )
            )
        )
    
    def query_employee_leave(self, employee_name):
        """查询员工假期信息"""
        return self.employee_chain.invoke({
            "query": f"查询{employee_name}的假期余额",
            "url": f"{self.base_url}/api/employees/{employee_name}/leave-balance"
        })
    
    def query_maternity_policy(self):
        """查询产假政策"""
        return self.policy_chain.invoke({
            "query": "查询公司的产假政策",
            "url": f"{self.base_url}/api/policies/maternity"
        })
    
    def query_user_permissions(self, user_id):
        """查询用户权限列表"""
        return self.employee_chain.invoke({
            "query": f"查询用户{user_id}的权限列表",
            "url": f"{self.base_url}/api/users/{user_id}/permissions"
        })
    
    def query_suppliers(self, category=None, name=None):
        """查询供应商信息"""
        if name:
            url = f"{self.base_url}/api/suppliers?name={name}"
        elif category:
            url = f"{self.base_url}/api/suppliers/category/{category}"
        else:
            url = f"{self.base_url}/api/suppliers"
        
        return self.employee_chain.invoke({
            "query": "查询供应商信息",
            "url": url
        })

# 使用示例
assistant = EnterpriseSmartAssistant()

# 各种查询示例
print("=== 企业智能助手演示 ===")
print("员工假期查询:", assistant.query_employee_leave("张三"))
print("产假政策:", assistant.query_maternity_policy())
print("用户权限:", assistant.query_user_permissions("user123"))
print("供应商查询:", assistant.query_suppliers(category="electronics"))
```

# 📋 附录：完整代码实现

## A.1 80_chain_examples.py - 完整实现

```python
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
```

## A.2 82_api_requests_ollama.py - 完整实现

```python
#!/usr/bin/env python3
"""
使用Ollama的LLMRequestsChain完整演示
专为Ollama gpt-3.5-turbo:latest优化
"""

import json
import time
import threading
import requests
from flask import Flask, jsonify, request
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

# ==================== Mock RESTful服务 ====================

class MockEnterpriseAPI:
    """企业级Mock API服务 - 完整实现"""
    
    def __init__(self, port=8000):
        self.app = Flask(__name__)
        self.port = port
        self.setup_routes()
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self):
        """生成完整的模拟数据"""
        return {
            "employees": {
                "张三": {
                    "name": "张三",
                    "department": "技术部",
                    "position": "高级开发工程师",
                    "annual_leave": 15,
                    "used_leave": 7,
                    "remaining_leave": 8,
                    "sick_leave": 5,
                    "maternity_leave_eligible": True,
                    "join_date": "2020-03-15",
                    "salary": 25000
                },
                "李四": {
                    "name": "李四",
                    "department": "市场部",
                    "position": "市场经理", 
                    "annual_leave": 12,
                    "used_leave": 3,
                    "remaining_leave": 9,
                    "sick_leave": 5,
                    "maternity_leave_eligible": False,
                    "join_date": "2019-08-20",
                    "salary": 18000
                },
                "王五": {
                    "name": "王五",
                    "department": "人事部",
                    "position": "HR专员",
                    "annual_leave": 10,
                    "used_leave": 2,
                    "remaining_leave": 8,
                    "sick_leave": 3,
                    "maternity_leave_eligible": True,
                    "join_date": "2021-05-10",
                    "salary": 15000
                }
            },
            "suppliers": {
                "electronics": [
                    {
                        "id": 1,
                        "name": "华强北电子",
                        "contact": "13800138001",
                        "email": "huang@example.com",
                        "rating": 4.8,
                        "products": ["手机配件", "电脑配件", "数据线"],
                        "status": "active",
                        "address": "深圳市福田区华强北路",
                        "established": "2010"
                    },
                    {
                        "id": 2,
                        "name": "京东电子",
                        "contact": "400-606-5500",
                        "email": "jd@jd.com",
                        "rating": 4.9,
                        "products": ["手机", "电脑", "家电"],
                        "status": "active",
                        "address": "北京市大兴区",
                        "established": "2004"
                    }
                ],
                "food": [
                    {
                        "id": 3,
                        "name": "中粮集团",
                        "contact": "400-698-6666",
                        "email": "info@cofco.com",
                        "rating": 4.7,
                        "products": ["大米", "食用油", "面粉"],
                        "status": "active",
                        "address": "北京市朝阳区",
                        "established": "1949"
                    }
                ]
            },
            "policies": {
                "maternity": {
                    "title": "产假政策",
                    "content": """
                    1. 基础产假：女职工生育享受98天产假
                    2. 难产增加：难产增加15天
                    3. 多胞胎：每多1个婴儿增加15天
                    4. 陪产假：男职工享受15天陪产假
                    5. 产前检查：怀孕女职工产前检查算作劳动时间
                    """,
                    "effective_date": "2024-01-01",
                    "department": "人事部"
                },
                "annual_leave": {
                    "title": "年假政策",
                    "content": """
                    1. 工作满1-10年：5天年假
                    2. 工作满10-20年：10天年假
                    3. 工作满20年以上：15天年假
                    4. 年假可跨年累积，最多累积2年
                    """,
                    "effective_date": "2024-01-01",
                    "department": "人事部"
                }
            },
            "users": {
                "admin": {
                    "username": "admin",
                    "permissions": ["read", "write", "delete", "admin"],
                    "role": "管理员",
                    "last_login": "2024-01-15 09:30:00"
                },
                "user1": {
                    "username": "user1",
                    "permissions": ["read", "write"],
                    "role": "普通用户",
                    "last_login": "2024-01-14 16:45:00"
                }
            }
        }
    
    def setup_routes(self):
        """设置完整的API路由"""
        
        # 健康检查
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy", "timestamp": time.time()})
        
        # 员工相关API
        @self.app.route('/api/employees/<employee_name>/leave-balance', methods=['GET'])
        def get_employee_leave(employee_name):
            employee = self.mock_data["employees"].get(employee_name)
            if not employee:
                return jsonify({"error": "员工不存在"}), 404
            return jsonify({
                "success": True,
                "data": {
                    "name": employee["name"],
                    "department": employee["department"],
                    "annual_leave": employee["annual_leave"],
                    "used_leave": employee["used_leave"],
                    "remaining_leave": employee["remaining_leave"],
                    "sick_leave": employee["sick_leave"]
                }
            })
        
        @self.app.route('/api/employees/<employee_name>/profile', methods=['GET'])
        def get_employee_profile(employee_name):
            employee = self.mock_data["employees"].get(employee_name)
            if not employee:
                return jsonify({"error": "员工不存在"}), 404
            return jsonify({"success": True, "data": employee})
        
        # 供应商相关API
        @self.app.route('/api/suppliers', methods=['GET'])
        def get_suppliers():
            category = request.args.get('category')
            name = request.args.get('name')
            
            suppliers = []
            if category and category in self.mock_data["suppliers"]:
                suppliers = self.mock_data["suppliers"][category]
            elif name:
                # 搜索所有供应商
                for category_suppliers in self.mock_data["suppliers"].values():
                    suppliers.extend([s for s in category_suppliers if name.lower() in s["name"].lower()])
            else:
                # 返回所有供应商
                for category_suppliers in self.mock_data["suppliers"].values():
                    suppliers.extend(category_suppliers)
            
            return jsonify({
                "success": True,
                "data": suppliers,
                "count": len(suppliers)
            })
        
        @self.app.route('/api/suppliers/category/<category>', methods=['GET'])
        def get_suppliers_by_category(category):
            suppliers = self.mock_data["suppliers"].get(category, [])
            return jsonify({
                "success": True,
                "data": suppliers,
                "category": category,
                "count": len(suppliers)
            })
        
        # 政策相关API
        @self.app.route('/api/policies/<policy_type>', methods=['GET'])
        def get_policy(policy_type):
            policy = self.mock_data["policies"].get(policy_type)
            if not policy:
                return jsonify({"error": "政策不存在"}), 404
            return jsonify({"success": True, "data": policy})
        
        @self.app.route('/api/policies', methods=['GET'])
        def get_all_policies():
            return jsonify({
                "success": True,
                "data": self.mock_data["policies"],
                "count": len(self.mock_data["policies"])
            })
        
        # 用户权限API
        @self.app.route('/api/users/<username>/permissions', methods=['GET'])
        def get_user_permissions(username):
            user = self.mock_data["users"].get(username)
            if not user:
                return jsonify({"error": "用户不存在"}), 404
            return jsonify({
                "success": True,
                "data": {
                    "username": username,
                    "permissions": user["permissions"],
                    "role": user["role"]
                }
            })
    
    def start_server(self):
        """启动服务器"""
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

# ==================== LLMRequestsChain实现 ====================

class OllamaLLMRequestsChain:
    """兼容Ollama的LLMRequestsChain实现"""
    
    def __init__(self, llm, prompt_template):
        self.llm = llm
        self.prompt_template = prompt_template
        self.llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    
    def invoke(self, inputs):
        """执行链式调用"""
        query = inputs["query"]
        url = inputs["url"]
        
        try:
            # 获取API数据
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            api_data = response.json()
            
            # 构建提示
            prompt = self.prompt_template.format(
                query=query,
                api_response=json.dumps(api_data, ensure_ascii=False, indent=2)
            )
            
            # 调用LLM
            result = self.llm.invoke(prompt)
            return {"output": result, "success": True}
            
        except requests.exceptions.RequestException as e:
            return {
                "output": f"API请求失败: {str(e)}",
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "output": f"处理失败: {str(e)}",
                "success": False,
                "error": str(e)
            }

class EnterpriseSmartAssistant:
    """企业智能助手 - 完整实现"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.llm = Ollama(
            model="gpt-3.5-turbo:latest",
            base_url="http://localhost:11434",
            temperature=0.3
        )
        self.setup_chains()
    
    def setup_chains(self):
        """设置各种查询链"""
        
        # 员工查询链
        employee_prompt = PromptTemplate(
            input_variables=["query", "api_response"],
            template="""基于API响应回答员工假期问题：

问题：{query}
API响应：{api_response}

请用简洁的中文回答，包含关键数字和部门信息。

回答格式：
员工[姓名]在[部门]部门，
- 年假总天数：[X]天
- 已使用：[X]天  
- 剩余：[X]天
- 病假：[X]天

其他相关信息请一并说明。"""
        )
        self.employee_chain = OllamaLLMRequestsChain(self.llm, employee_prompt)
        
        # 政策查询链  
        policy_prompt = PromptTemplate(
            input_variables=["query", "api_response"],
            template="""基于API响应解释政策：

问题：{query}
政策内容：{api_response}

请用通俗易懂的中文解释政策要点，分点说明：

1. 政策适用范围
2. 具体规定内容
3. 申请流程（如有）
4. 注意事项

政策生效时间也请一并说明。"""
        )
        self.policy_chain = OllamaLLMRequestsChain(self.llm, policy_prompt)
        
        # 供应商查询链
        supplier_prompt = PromptTemplate(
            input_variables=["query", "api_response"],
            template="""基于API响应提供供应商信息：

问题：{query}
供应商信息：{api_response}

请用中文列出供应商详细信息：

📋 供应商列表：
{供应商信息}

📊 统计信息：
- 总供应商数量：[X]家
- 平均评分：[X]分
- 主要类别：[列出类别]

如有具体供应商，请提供联系方式和主营产品。"""
        )
        self.supplier_chain = OllamaLLMRequestsChain(self.llm, supplier_prompt)
        
        # 权限查询链
        permission_prompt = PromptTemplate(
            input_variables=["query", "api_response"],
            template="""基于API响应回答权限问题：

问题：{query}
权限信息：{api_response}

用户权限详情：
- 用户名：[用户名]
- 角色：[角色]
- 权限列表：
{权限列表}

权限说明：
- read: 读取权限
- write: 写入权限  
- delete: 删除权限
- admin: 管理权限

请根据实际权限给出使用建议。"""
        )
        self.permission_chain = OllamaLLMRequestsChain(self.llm, permission_prompt)
    
    def query_employee_leave(self, employee_name: str) -> Dict[str, Any]:
        """查询员工假期"""
        return self.employee_chain.invoke({
            "query": f"查询{employee_name}的假期余额",
            "url": f"{self.base_url}/api/employees/{employee_name}/leave-balance"
        })
    
    def query_employee_profile(self, employee_name: str) -> Dict[str, Any]:
        """查询员工档案"""
        return self.employee_chain.invoke({
            "query": f"查询{employee_name}的详细信息",
            "url": f"{self.base_url}/api/employees/{employee_name}/profile"
        })
    
    def query_maternity_policy(self) -> Dict[str, Any]:
        """查询产假政策"""
        return self.policy_chain.invoke({
            "query": "产假政策是什么",
            "url": f"{self.base_url}/api/policies/maternity"
        })
    
    def query_all_policies(self) -> Dict[str, Any]:
        """查询所有政策"""
        return self.policy_chain.invoke({
            "query": "查询所有政策",
            "url": f"{self.base_url}/api/policies"
        })
    
    def query_suppliers(self, category: str = None, name: str = None) -> Dict[str, Any]:
        """查询供应商"""
        if name:
            return self.supplier_chain.invoke({
                "query": f"查询名称为{name}的供应商",
                "url": f"{self.base_url}/api/suppliers?name={name}"
            })
        elif category:
            return self.supplier_chain.invoke({
                "query": f"查询{category}类别的供应商",
                "url": f"{self.base_url}/api/suppliers/category/{category}"
            })
        else:
            return self.supplier_chain.invoke({
                "query": "查询所有供应商",
                "url": f"{self.base_url}/api/suppliers"
            })
    
    def query_user_permissions(self, username: str) -> Dict[str, Any]:
        """查询用户权限"""
        return self.permission_chain.invoke({
            "query": f"查询用户{username}的权限",
            "url": f"{self.base_url}/api/users/{username}/permissions"
        })

# ==================== 完整演示程序 ====================

def run_complete_demo():
    """运行完整演示"""
    
    print("🚀 LLMRequestsChain企业智能助手完整演示")
    print("=" * 60)
    
    # 启动Mock服务器
    mock_api = MockEnterpriseAPI()
    server_thread = threading.Thread(target=mock_api.start_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # 等待服务器启动
    print("✅ Mock企业API服务器已启动")
    
    # 初始化助手
    assistant = EnterpriseSmartAssistant()
    
    # 演示各种查询
    demo_queries = [
        # 员工相关
        ("员工假期", lambda: assistant.query_employee_leave("张三")),
        ("员工档案", lambda: assistant.query_employee_profile("李四")),
        
        # 政策相关
        ("产假政策", lambda: assistant.query_maternity_policy()),
        ("所有政策", lambda: assistant.query_all_policies()),
        
        # 供应商相关
        ("电子供应商", lambda: assistant.query_suppliers(category="electronics")),
        ("食品供应商", lambda: assistant.query_suppliers(category="food")),
        ("所有供应商", lambda: assistant.query_suppliers()),
        
        # 权限相关
        ("管理员权限", lambda: assistant.query_user_permissions("admin")),
        ("普通用户权限", lambda: assistant.query_user_permissions("user1"))
    ]
    
    for query_name, query_func in demo_queries:
        print(f"\n📋 {query_name}查询:")
        try:
            result = query_func()
            if result["success"]:
                print(f"✅ 结果: {result['output']}")
            else:
                print(f"❌ 失败: {result['output']}")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
        
        time.sleep(1)  # 避免请求过快

if __name__ == "__main__":
    run_complete_demo()
```

通过以上升级内容和完整代码实现，你现在拥有一个包含9种核心链类型的完整LangChain实战指南。每个示例都提供了完整的可运行代码，可以直接复制使用并根据实际需求进行调整。

记住，链的真正威力在于它们的组合能力 - 通过巧妙地组合不同的链，可以解决几乎任何复杂的AI应用场景。建议先运行基础示例，理解每种链的核心概念，然后根据实际需求进行组合和创新。

## 🚀 快速开始指南

1. **安装依赖**:
```bash
pip install langchain langchain-ollama langchain-core flask requests
```

2. **启动Ollama服务**:
```bash
ollama serve
ollama pull gpt-3.5-turbo:latest
```

3. **运行示例**:
```bash
# 运行基础链示例
python 80_chain_examples.py

# 运行API链和LLMRequestsChain示例
python 82_api_requests_ollama.py
```

希望这些详细的代码和实现能帮助你快速掌握LangChain的各种链式应用！