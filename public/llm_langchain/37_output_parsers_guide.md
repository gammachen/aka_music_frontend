# LangChain 输出解析器完整技术指南

## 概述

输出解析器(Output Parsers)是LangChain中的关键组件，负责将LLM的原始文本输出转换为结构化数据。它们解决了以下核心问题：

- **数据结构化**：将自由文本转换为程序可用的结构化数据
- **类型安全**：确保输出符合预期的数据类型和格式
- **错误处理**：优雅地处理格式不符或解析失败的情况
- **验证机制**：对输出数据进行实时验证和清洗

## 输出解析器分类与详解

### 1. 基础解析器

#### 1.1 StringOutputParser
**用途**：最简单的文本输出解析，保持原始格式

**应用场景**：
- 聊天机器人响应
- 创意写作输出
- 不需要结构化的纯文本场景

**代码示例**：
```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 基础字符串解析
parser = StrOutputParser()
llm = ChatOpenAI(temperature=0.7)

prompt = PromptTemplate.from_template("请用一句话描述{topic}")
chain = prompt | llm | parser

result = chain.invoke({"topic": "人工智能"})
print(result)  # 输出：人工智能是让机器具备人类智能的技术
```

#### 1.2 BooleanOutputParser
**用途**：将文本输出解析为布尔值

**应用场景**：
- 是非题回答
- 决策判断结果
- 开关状态确认

**代码示例**：
```python
from langchain.output_parsers import BooleanOutputParser

parser = BooleanOutputParser()
llm = ChatOpenAI()

prompt = PromptTemplate.from_template("
请判断以下陈述是否正确：{statement}
只回答true或false，不要解释
")

chain = prompt | llm | parser
result = chain.invoke({"statement": "地球是平的"})
print(result)  # 输出：False
```

### 2. 结构化解析器

#### 2.1 PydanticOutputParser
**用途**：将输出解析为Pydantic模型定义的复杂对象

**应用场景**：
- API响应格式化
- 数据库记录创建
- 配置文件生成

**代码示例**：
```python
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

class Person(BaseModel):
    name: str = Field(description="人物姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")
    skills: list[str] = Field(description="技能列表")

parser = PydanticOutputParser(pydantic_object=Person)

prompt = PromptTemplate(
    template="
    请根据描述提取人物信息：{description}
    \n{format_instructions}
    ",
    input_variables=["description"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | ChatOpenAI() | parser

result = chain.invoke({
    "description": "张三是一位28岁的软件工程师，精通Python、JavaScript和机器学习"
})

print(result)
# 输出：Person(name='张三', age=28, occupation='软件工程师', skills=['Python', 'JavaScript', '机器学习'])
```

#### 2.2 DatetimeOutputParser
**用途**：解析日期时间格式的输出

**应用场景**：
- 事件时间提取
- 预约系统
- 时间序列分析

**代码示例**：
```python
from langchain.output_parsers import DatetimeOutputParser
from datetime import datetime

parser = DatetimeOutputParser(format="%Y-%m-%d %H:%M:%S")

prompt = PromptTemplate.from_template("
请将以下时间描述转换为标准格式：{time_description}
格式：YYYY-MM-DD HH:MM:SS
")

chain = prompt | ChatOpenAI() | parser

result = chain.invoke({"time_description": "明天下午3点半"})
print(result)  # 输出：2024-01-16 15:30:00
```

#### 2.3 ListOutputParser
**用途**：将输出解析为列表格式

**应用场景**：
- 项目清单生成
- 关键词提取
- 选项列表创建

**代码示例**：
```python
from langchain.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()

prompt = PromptTemplate.from_template("
请列出{topic}的5个主要应用场景，用逗号分隔
")

chain = prompt | ChatOpenAI() | parser

result = chain.invoke({"topic": "人工智能"})
print(result)  # 输出：['自动驾驶', '医疗诊断', '金融风控', '智能客服', '内容推荐']
```

### 3. 枚举解析器

#### 3.1 EnumOutputParser
**用途**：将输出限制在预定义的枚举值中

**应用场景**：
- 分类标签分配
- 状态机转换
- 标准化选项选择

**代码示例**：
```python
from enum import Enum
from langchain.output_parsers import EnumOutputParser

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

parser = EnumOutputParser(enum=Sentiment)

prompt = PromptTemplate.from_template("
请分析以下文本的情感倾向：{text}
可选值：positive, negative, neutral
")

chain = prompt | ChatOpenAI() | parser

result = chain.invoke({"text": "这个产品真是太棒了！"})
print(result)  # 输出：Sentiment.POSITIVE
```

### 4. 复杂解析器

#### 4.1 StructuredOutputParser
**用途**：解析复杂的嵌套结构数据

**应用场景**：
- 复杂JSON数据生成
- 嵌套对象创建
- 多表关联数据

**代码示例**：
```python
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

response_schemas = [
    ResponseSchema(name="name", description="产品名称", type="string"),
    ResponseSchema(name="price", description="价格