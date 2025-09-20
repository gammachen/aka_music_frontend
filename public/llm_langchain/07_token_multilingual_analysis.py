#!/usr/bin/env python3
"""
多语言Token效率深度分析
展示不同语言在GPT模型中的token使用效率
"""

import tiktoken
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class MultilingualTokenAnalyzer:
    """多语言Token分析器"""
    
    def __init__(self):
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
        # 测试文本：相同语义的不同语言表达
        self.test_texts = {
            "english": "Artificial intelligence is transforming the world through machine learning and deep learning technologies.",
            "chinese": "人工智能正在通过机器学习和深度学习技术改变世界。",
            "japanese": "人工知能は機械学習と深層学習技術を通じて世界を変革しています。",
            "korean": "인공지능은 기계 학습과 딥러닝 기술을 통해 세계를 변화시키고 있습니다.",
            "french": "L'intelligence artificielle transforme le monde grâce aux technologies d'apprentissage automatique et d'apprentissage profond.",
            "german": "Künstliche Intelligenz verändert die Welt durch Technologien des maschinellen Lernens und des Deep Learning.",
            "spanish": "La inteligencia artificial está transformando el mundo a través de tecnologías de aprendizaje automático y aprendizaje profundo.",
            "russian": "Искусственный интеллект преобразует мир с помощью технологий машинного обучения и глубокого обучения.",
            "emoji": "🤖 AI 🤖 is 🤖 transforming 🤖 the 🤖 world 🤖 through 🤖 ML 🤖"
        }
    
    def analyze_efficiency(self) -> pd.DataFrame:
        """分析各语言token效率"""
        results = []
        
        for language, text in self.test_texts.items():
            tokens = self.encoding.encode(text)
            decoded_tokens = [self.encoding.decode([t]) for t in tokens]
            
            analysis = {
                "language": language,
                "text": text,
                "char_count": len(text),
                "token_count": len(tokens),
                "byte_length": len(text.encode('utf-8')),
                "tokens_per_char": len(tokens) / len(text),
                "chars_per_token": len(text) / len(tokens),
                "compression_ratio": len(text.encode('utf-8')) / (len(tokens) * 4),
                "tokens": decoded_tokens
            }
            
            results.append(analysis)
        
        return pd.DataFrame(results)
    
    def visualize_efficiency(self, df: pd.DataFrame):
        """可视化token效率"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Token数量对比
        languages = [lang.capitalize() for lang in df['language']]
        token_counts = df['token_count']
        
        ax1.bar(languages, token_counts, color='skyblue')
        ax1.set_title('不同语言的Token数量对比', fontsize=14, pad=20)
        ax1.set_ylabel('Token数量')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 字符与Token比例
        ax2.scatter(df['char_count'], df['token_count'], 
                   s=df['chars_per_token']*50, alpha=0.7, color='coral')
        
        for i, lang in enumerate(df['language']):
            ax2.annotate(lang.capitalize(), 
                        (df['char_count'].iloc[i], df['token_count'].iloc[i]),
                        xytext=(5, 5), textcoords='offset points', fontsize=10)
        
        ax2.set_xlabel('字符数')
        ax2.set_ylabel('Token数')
        ax2.set_title('字符数 vs Token数关系', fontsize=14)
        
        # 3. 压缩效率
        ax3.bar(languages, df['compression_ratio'], color='lightgreen')
        ax3.set_title('压缩效率对比', fontsize=14, pad=20)
        ax3.set_ylabel('压缩比')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Token密度热力图
        efficiency_data = df[['language', 'tokens_per_char', 'chars_per_token']]
        sns.heatmap(efficiency_data.set_index('language').T, 
                   annot=True, fmt='.2f', cmap='YlOrRd', ax=ax4)
        ax4.set_title('Token密度热力图', fontsize=14)
        
        plt.tight_layout()
        plt.savefig('multilingual_token_efficiency.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self) -> str:
        """生成详细分析报告"""
        
        df = self.analyze_efficiency()
        
        report = f"""
# 多语言Token效率分析报告

## 执行摘要
- **测试时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试模型**: GPT-3.5-Turbo
- **测试文本长度**: 各语言语义相同

## 详细数据

{df.to_string(index=False)}

## 关键发现

### 1. Token效率排名（从低到高）
"""
        
        # 按token数量排序
        df_sorted = df.sort_values('token_count')
        
        for idx, row in df_sorted.iterrows():
            efficiency = "高" if row['chars_per_token'] > 3 else "中" if row['chars_per_token'] > 2 else "低"
            report += f"""
**{row['language'].capitalize()}**: 
- Token数: {row['token_count']}
- 字符/token比: {row['chars_per_token']:.2f}
- 效率等级: {efficiency}
"""
        
        report += f"""
### 2. 成本影响分析
- **最经济语言**: {df.loc[df['token_count'].idxmin(), 'language'].capitalize()}
- **最昂贵语言**: {df.loc[df['token_count'].idxmax(), 'language'].capitalize()}
- **成本差异**: {df['token_count'].max() / df['token_count'].min():.2f}x

### 3. 优化建议
"""
        
        # 生成优化建议
        high_efficiency = df[df['chars_per_token'] > 3]['language'].tolist()
        low_efficiency = df[df['chars_per_token'] <= 2]['language'].tolist()
        
        report += f"""
- **高效语言** ({', '.join([lang.capitalize() for lang in high_efficiency])}):
  适合长文本处理，成本效益好

- **低效语言** ({', '.join([lang.capitalize() for lang in low_efficiency])}):
  建议精简文本，使用缩写和简写

- **中文特殊处理**:
  每个汉字通常对应1个token，比英文单词更高效
"""
        
        return report

# 实际运行分析
if __name__ == "__main__":
    analyzer = MultilingualTokenAnalyzer()
    
    # 运行分析
    df = analyzer.analyze_efficiency()
    print("=== 多语言Token效率分析 ===")
    print(df[['language', 'char_count', 'token_count', 'chars_per_token']])
    
    # 生成报告
    report = analyzer.generate_report()
    print(report)
    
    # 可视化
    analyzer.visualize_efficiency(df)
    
    # 保存结果
    df.to_csv('multilingual_token_analysis.csv', index=False)
    with open('token_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)