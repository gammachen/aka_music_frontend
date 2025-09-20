# LangChain代码升级指南

## 升级内容

本次升级将原有的LangChain代码从旧版本升级到最新版本，并替换OpenAI API为本地Ollama模型。

## 主要变更

### 1. 依赖包更新
- **旧版本**: `langchain` (包含所有组件)
- **新版本**: 
  - `langchain-ollama`: 官方Ollama集成
  - `langchain-core`: 核心功能
  - `langchain_ollama.OllamaLLM`: Ollama模型支持

### 2. 模型替换
- **旧模型**: OpenAI GPT-3.5-turbo-instruct (需要API密钥)
- **新模型**: 本地Ollama gpt-3.5-turbo:latest (完全本地运行)

### 3. 链式调用更新
- **旧方式**: `SimpleSequentialChain` (已弃用)
- **新方式**: `SequentialChain` (支持更灵活的输入输出)

## 安装和配置步骤

### 1. 安装Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# 从 https://ollama.ai 下载安装程序
```

### 2. 启动Ollama服务
```bash
# 启动服务
ollama serve

# 在另一个终端拉取模型
ollama pull gpt-3.5-turbo:latest
```

### 3. 安装Python依赖
```bash
pip install -r requirements.txt
```

### 4. 运行测试
```bash
# 先检查环境
python test_ollama_setup.py

# 运行主程序
python sequential_chain_test.py
```

## 代码使用示例

### 基本用法
```python
from sequential_chain_test import run_story_generator

# 使用默认标题
run_story_generator()

# 使用自定义标题
run_story_generator("AI觉醒的程序员")
```

### 高级用法
```python
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

# 创建自定义链
llm = Ollama(model="gpt-3.5-turbo:latest")
prompt = PromptTemplate.from_template("请写一篇关于{topic}的文章")
chain = LLMChain(llm=llm, prompt=prompt)

result = chain.invoke({"topic": "人工智能"})
print(result["text"])
```

## 故障排除

### 常见问题

1. **Ollama服务未启动**
   ```
   错误: Connection refused
   解决: 运行 `ollama serve`
   ```

2. **模型未找到**
   ```
   错误: model "gpt-3.5-turbo:latest" not found
   解决: 运行 `ollama pull gpt-3.5-turbo:latest`
   ```

3. **端口冲突**
   ```
   错误: address already in use
   解决: 检查是否有其他Ollama实例运行
   ```

### 性能优化

- **内存**: 确保至少有8GB可用内存
- **CPU**: 多核CPU可以提升响应速度
- **存储**: 模型文件约4GB，确保有足够磁盘空间

## 模型选择

除了gpt-3.5-turbo，Ollama还支持多种模型：

```bash
# 其他可选模型
ollama pull llama2:7b          # Llama 2
ollama pull mistral:7b         # Mistral
ollama pull codellama:7b       # 代码生成
ollama pull vicuna:7b          # Vicuna
```

在代码中只需修改model参数即可：
```python
ollama_model = Ollama(model="mistral:7b")
```