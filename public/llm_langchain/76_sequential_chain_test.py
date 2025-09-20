# 升级后的代码：使用最新LangChain版本和本地Ollama模型
from langchain_ollama import OllamaLLM as Ollama
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
import warnings
warnings.filterwarnings('ignore')

# 配置Ollama模型
ollama_model = Ollama(
    model="gpt-3.5-turbo:latest",
    base_url="http://localhost:11434",  # Ollama默认地址
    temperature=0.9,
    num_predict=1024  # 相当于max_tokens
)

# 创建编剧链
script_prompt_tpl = PromptTemplate.from_template(
    '''你是一个优秀的编剧。请使用你丰富的想象力根据给定的标题编写一个故事概要。
    
    标题: {title}
    
    要求：
    1. 故事要有趣且富有创意
    2. 包含冲突和转折
    3. 适合改编成短视频
    4. 字数控制在300字以内
    
    故事概要:'''
)

script_chain = LLMChain(
    llm=ollama_model,
    prompt=script_prompt_tpl,
    output_key="story"
)

# 创建广告链
adv_prompt_tpl = PromptTemplate.from_template(
    '''你是一个优秀的广告写手。请根据故事概要，写一段简短但有吸引力的广告词。
    
    故事概要: {story}
    
    要求：
    1. 广告词不超过50字
    2. 要有悬念和吸引力
    3. 适合社交媒体传播
    
    广告词:'''
)

# 为广告链使用稍微低一点的temperature
adv_ollama_model = Ollama(
    model="gpt-3.5-turbo:latest",
    base_url="http://localhost:11434",
    temperature=0.6,  # 降低随机性，使广告词更精炼
    num_predict=128   # 限制输出长度
)

adv_chain = LLMChain(
    llm=adv_ollama_model,
    prompt=adv_prompt_tpl,
    output_key="advertisement"
)

# 使用SequentialChain替代已弃用的SimpleSequentialChain
chain = SequentialChain(
    chains=[script_chain, adv_chain],
    input_variables=["title"],
    output_variables=["story", "advertisement"],
    verbose=True
)

# 运行示例
def run_story_generator(title="在杭州的‘西湖遇见敦煌’的艺术空间’"):
    """运行故事生成器"""
    try:
        result = chain.invoke({"title": title})
        
        print("=" * 50)
        print("🎬 故事标题:", title)
        print("=" * 50)
        print("📖 故事概要:")
        print(result["story"])
        print("=" * 50)
        print("📢 广告词:")
        print(result["advertisement"])
        print("=" * 50)
        
        return result
        
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        print("请确保Ollama服务正在运行: ollama serve")
        print("并确认已拉取模型: ollama pull gpt-3.5-turbo:latest")
        return None

# 主程序入口
if __name__ == "__main__":
    # 测试运行
    run_story_generator("在杭州的‘西湖遇见敦煌’的艺术空间’")
    
    # 也可以自定义标题
    # run_story_generator("AI觉醒的程序员")