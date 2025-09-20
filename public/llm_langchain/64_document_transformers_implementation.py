#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain文档转换器完整实现
包含所有核心转换器的生产级实现
"""

import os
import re
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import ast
import tiktoken

# 模拟Document类
@dataclass
class Document:
    page_content: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# 基础异常类
class DocumentTransformerError(Exception):
    """文档转换器基础异常"""
    pass

# =============================================================================
# 核心文本分割器实现
# =============================================================================

class CharacterTextSplitter:
    """字符级文本分割器"""
    
    def __init__(
        self,
        separator: str = "\n\n",
        chunk_size: int = 4000,
        chunk_overlap: int = 200,
        length_function: callable = len,
        is_separator_regex: bool = False
    ):
        self.separator = separator
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
        self.is_separator_regex = is_separator_regex
    
    def split_text(self, text: str) -> List[str]:
        """分割文本"""
        if self.length_function(text) <= self.chunk_size:
            return [text]
        
        # 处理分隔符
        if self.is_separator_regex:
            splits = re.split(self.separator, text)
        else:
            splits = text.split(self.separator)
        
        # 合并小片段
        chunks = []
        current_chunk = ""
        separator_len = len(self.separator) if not self.is_separator_regex else 0
        
        for split in splits:
            if self.length_function(current_chunk + split) <= self.chunk_size:
                current_chunk += split + self.separator
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip(self.separator))
                current_chunk = split + self.separator
        
        if current_chunk:
            chunks.append(current_chunk.rstrip(self.separator))
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档"""
        result = []
        for doc in documents:
            texts = self.split_text(doc.page_content)
            for i, text in enumerate(texts):
                new_doc = Document(
                    page_content=text,
                    metadata={
                        **doc.metadata,
                        'chunk_index': i,
                        'total_chunks': len(texts),
                        'splitter_type': 'CharacterTextSplitter'
                    }
                )
                result.append(new_doc)
        return result

class TokenTextSplitter:
    """Token级文本分割器"""
    
    def __init__(
        self,
        encoding_name: str = "cl100k_base",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """基于token的分割"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档"""
        result = []
        for doc in documents:
            texts = self.split_text(doc.page_content)
            for i, text in enumerate(texts):
                new_doc = Document(
                    page_content=text,
                    metadata={
                        **doc.metadata,
                        'chunk_index': i,
                        'total_chunks': len(texts),
                        'token_count': len(self.encoding.encode(text)),
                        'splitter_type': 'TokenTextSplitter'
                    }
                )
                result.append(new_doc)
        return result

class RecursiveCharacterTextSplitter:
    """递归字符文本分割器"""
    
    def __init__(
        self,
        separators: Optional[List[str]] = None,
        chunk_size: int = 4000,
        chunk_overlap: int = 200,
        length_function: callable = len
    ):
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
    
    def split_text(self, text: str) -> List[str]:
        """递归分割文本"""
        return self._split_text(text, self.separators)
    
    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """递归分割核心算法"""
        if self.length_function(text) <= self.chunk_size:
            return [text]
        
        for separator in separators:
            if separator == "":
                # 字符级分割
                return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
            
            splits = text.split(separator)
            if len(splits) > 1:
                chunks = []
                current_chunk = ""
                
                for split in splits:
                    if self.length_function(current_chunk + separator + split) <= self.chunk_size:
                        if current_chunk:
                            current_chunk += separator + split
                        else:
                            current_chunk = split
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        
                        # 处理大段落
                        if self.length_function(split) > self.chunk_size:
                            remaining_chunks = self._split_text(split, separators[separators.index(separator)+1:])
                            chunks.extend(remaining_chunks)
                            current_chunk = ""
                        else:
                            current_chunk = split
                
                if current_chunk:
                    chunks.append(current_chunk)
                
                return chunks
        
        return [text]
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档"""
        result = []
        for doc in documents:
            texts = self.split_text(doc.page_content)
            for i, text in enumerate(texts):
                new_doc = Document(
                    page_content=text,
                    metadata={
                        **doc.metadata,
                        'chunk_index': i,
                        'total_chunks': len(texts),
                        'splitter_type': 'RecursiveCharacterTextSplitter'
                    }
                )
                result.append(new_doc)
        return result

class MarkdownTextSplitter:
    """Markdown文本分割器"""
    
    def __init__(
        self,
        chunk_size: int = 2000,
        chunk_overlap: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """保持Markdown结构的分割"""
        # 识别Markdown结构
        sections = self._parse_markdown_sections(text)
        
        chunks = []
        current_chunk = ""
        
        for section in sections:
            section_text = section['content']
            section_size = len(section_text)
            
            if len(current_chunk + section_text) <= self.chunk_size:
                current_chunk += section_text
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 处理大段落
                if section_size > self.chunk_size:
                    # 在段落内继续分割
                    sub_chunks = self._split_large_section(section_text)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = section_text
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _parse_markdown_sections(self, text: str) -> List[Dict[str, Any]]:
        """解析Markdown结构"""
        sections = []
        lines = text.split('\n')
        
        current_section = {"type": "text", "content": "", "level": 0}
        
        for line in lines:
            line = line.strip()
            
            # 检测标题
            if line.startswith('#'):
                if current_section["content"].strip():
                    sections.append(current_section)
                
                level = line.count('#', 0, line.find(' ')) or line.count('#')
                title = line.lstrip('#').strip()
                
                current_section = {
                    "type": "heading",
                    "content": line + '\n',
                    "level": level,
                    "title": title
                }
            
            # 检测代码块
            elif line.startswith('```'):
                if current_section["content"].strip():
                    sections.append(current_section)
                
                current_section = {
                    "type": "code_block",
                    "content": line + '\n',
                    "level": 0
                }
            
            else:
                current_section["content"] += line + '\n'
        
        if current_section["content"].strip():
            sections.append(current_section)
        
        return sections
    
    def _split_large_section(self, text: str) -> List[str]:
        """大段落内分割"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= self.chunk_size:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档"""
        result = []
        for doc in documents:
            texts = self.split_text(doc.page_content)
            for i, text in enumerate(texts):
                new_doc = Document(
                    page_content=text,
                    metadata={
                        **doc.metadata,
                        'chunk_index': i,
                        'total_chunks': len(texts),
                        'splitter_type': 'MarkdownTextSplitter'
                    }
                )
                result.append(new_doc)
        return result

# =============================================================================
# 代码专用分割器
# =============================================================================

class PythonCodeTextSplitter:
    """Python代码专用分割器"""
    
    def __init__(
        self,
        chunk_size: int = 1500,
        chunk_overlap: int = 150
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, code: str) -> List[str]:
        """基于代码结构的分割"""
        try:
            tree = ast.parse(code)
            blocks = self._extract_code_blocks(code, tree)
            
            chunks = []
            current_chunk = ""
            
            for block in blocks:
                block_text = block['content']
                if len(current_chunk + block_text) <= self.chunk_size:
                    current_chunk += block_text + '\n\n'
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    
                    # 处理大代码块
                    if len(block_text) > self.chunk_size:
                        sub_chunks = self._split_large_block(block_text)
                        chunks.extend(sub_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = block_text + '\n\n'
            
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            return chunks
            
        except SyntaxError:
            # 语法错误时降级到字符分割
            return RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            ).split_text(code)
    
    def _extract_code_blocks(self, code: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """提取代码结构"""
        lines = code.split('\n')
        blocks = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno - 1
                end_line = node.end_lineno or start_line + 1
                content = '\n'.join(lines[start_line:end_line])
                
                blocks.append({
                    'type': 'function',
                    'name': node.name,
                    'content': content,
                    'start_line': start_line,
                    'end_line': end_line,
                    'docstring': ast.get_docstring(node) or ''
                })
            
            elif isinstance(node, ast.ClassDef):
                start_line = node.lineno - 1
                end_line = node.end_lineno or start_line + 1
                content = '\n'.join(lines[start_line:end_line])
                
                blocks.append({
                    'type': 'class',
                    'name': node.name,
                    'content': content,
                    'start_line': start_line,
                    'end_line': end_line,
                    'methods': [method.name for method in node.body if isinstance(method, ast.FunctionDef)]
                })
        
        return sorted(blocks, key=lambda x: x['start_line'])
    
    def _split_large_block(self, text: str) -> List[str]:
        """大代码块分割"""
        lines = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk + line) <= self.chunk_size:
                current_chunk += line + '\n'
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档"""
        result = []
        for doc in documents:
            texts = self.split_text(doc.page_content)
            for i, text in enumerate(texts):
                new_doc = Document(
                    page_content=text,
                    metadata={
                        **doc.metadata,
                        'chunk_index': i,
                        'total_chunks': len(texts),
                        'splitter_type': 'PythonCodeTextSplitter'
                    }
                )
                result.append(new_doc)
        return result

# =============================================================================
# 性能优化工具
# =============================================================================

class SplitQualityEvaluator:
    """分割质量评估器"""
    
    def __init__(self):
        self.metrics = {}
    
    def evaluate_splits(self, original_text: str, chunks: List[str]) -> Dict[str, float]:
        """评估分割质量"""
        scores = {
            'semantic_coherence': self._calculate_semantic_coherence(chunks),
            'size_uniformity': self._calculate_size_uniformity(chunks),
            'boundary_naturalness': self._calculate_boundary_naturalness(original_text, chunks),
            'compression_ratio': len(''.join(chunks)) / len(original_text)
        }
        return scores
    
    def _calculate_semantic_coherence(self, chunks: List[str]) -> float:
        """计算语义连贯性"""
        if len(chunks) < 2:
            return 1.0
        
        # 简单的重叠词计算
        scores = []
        for i in range(1, len(chunks)):
            prev_words = set(chunks[i-1].lower().split())
            curr_words = set(chunks[i].lower().split())
            
            if prev_words and curr_words:
                overlap = len(prev_words.intersection(curr_words))
                score = overlap / max(len(prev_words), len(curr_words))
                scores.append(score)
        
        return np.mean(scores) if scores else 0.0
    
    def _calculate_size_uniformity(self, chunks: List[str]) -> float:
        """计算大小均匀性"""
        sizes = [len(chunk) for chunk in chunks]
        if len(sizes) <= 1:
            return 1.0
        
        mean_size = np.mean(sizes)
        std_size = np.std(sizes)
        
        # 变异系数越小越均匀
        cv = std_size / mean_size if mean_size > 0 else 0
        return max(0, 1 - cv)
    
    def _calculate_boundary_naturalness(self, original: str, chunks: List[str]) -> float:
        """计算边界自然度"""
        # 检查是否在句子边界分割
        boundaries = []
        current_pos = 0
        
        for chunk in chunks[:-1]:  # 除了最后一个chunk
            boundary_pos = current_pos + len(chunk)
            
            # 检查是否在句子结束
            if boundary_pos < len(original):
                next_char = original[boundary_pos]
                is_sentence_end = next_char in '.!?'
                boundaries.append(1.0 if is_sentence_end else 0.0)
            
            current_pos = boundary_pos
        
        return np.mean(boundaries) if boundaries else 0.0

class DistributedDocumentProcessor:
    """分布式文档处理器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_documents_parallel(
        self, 
        documents: List[Document], 
        splitter
    ) -> List[Document]:
        """并行处理文档"""
        # 将文档分组
        batch_size = max(1, len(documents) // self.max_workers)
        batches = [documents[i:i+batch_size] for i in range(0, len(documents), batch_size)]
        
        # 并行处理
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(self.executor, self._process_batch, batch, splitter)
            for batch in batches
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 合并结果
        all_chunks = []
        for batch_result in results:
            all_chunks.extend(batch_result)
        
        return all_chunks
    
    def _process_batch(self, documents: List[Document], splitter) -> List[Document]:
        """处理单个批次"""
        chunks = []
        for doc in documents:
            doc_chunks = splitter.split_documents([doc])
            chunks.extend(doc_chunks)
        return chunks

# =============================================================================
# 实际应用示例
# =============================================================================

class EnterpriseDocumentProcessor:
    """企业级文档处理器"""
    
    def __init__(self):
        self.splitters = {
            'txt': RecursiveCharacterTextSplitter(
                chunk_size=4000,
                chunk_overlap=400,
                separators=["\n\n", "\n", ". ", " ", ""]
            ),
            'md': MarkdownTextSplitter(
                chunk_size=2000,
                chunk_overlap=200
            ),
            'py': PythonCodeTextSplitter(
                chunk_size=1500,
                chunk_overlap=150
            )
        }
        self.evaluator = SplitQualityEvaluator()
    
    def process_file(self, file_path: str, file_type: str = None) -> Dict[str, Any]:
        """处理单个文件"""
        if file_type is None:
            file_type = file_path.split('.')[-1].lower()
        
        if file_type not in self.splitters:
            file_type = 'txt'
        
        # 读取文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
        
        # 创建文档
        doc = Document(
            page_content=content,
            metadata={
                'source': file_path,
                'file_type': file_type,
                'file_size': len(content),
                'processed_at': datetime.now().isoformat()
            }
        )
        
        # 分割文档
        splitter = self.splitters[file_type]
        chunks = splitter.split_documents([doc])
        
        # 评估质量
        chunk_texts = [chunk.page_content for chunk in chunks]
        quality_scores = self.evaluator.evaluate_splits(content, chunk_texts)
        
        return {
            'original_document': doc,
            'chunks': chunks,
            'chunk_count': len(chunks),
            'quality_scores': quality_scores,
            'processing_summary': {
                'file_path': file_path,
                'file_type': file_type,
                'original_length': len(content),
                'avg_chunk_size': np.mean([len(chunk.page_content) for chunk in chunks]),
                'processing_time': datetime.now().isoformat()
            }
        }
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """处理整个目录"""
        results = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                try:
                    result = self.process_file(file_path)
                    results.append(result)
                    print(f"✓ 处理完成: {filename} -> {len(result['chunks'])} 个分块")
                except Exception as e:
                    print(f"✗ 处理失败: {filename} - {str(e)}")
        
        return results

# =============================================================================
# 演示和测试
# =============================================================================

class DocumentTransformerDemo:
    """文档转换器演示类"""
    
    def __init__(self):
        self.processor = EnterpriseDocumentProcessor()
    
    def create_sample_documents(self) -> List[Document]:
        """创建示例文档"""
        documents = []
        
        # 示例1：技术文档
        tech_doc = Document(
            page_content="""
            # LangChain技术文档
            
            ## 概述
            LangChain是一个用于构建基于大语言模型的应用程序的框架。
            
            ## 核心组件
            
            ### 1. 模型I/O
            LangChain提供了标准化的接口来与各种语言模型交互。
            
            ### 2. 数据连接
            支持多种数据源和文档格式的加载和处理。
            
            ## 应用场景
            适用于问答系统、聊天机器人、文档分析等多种场景。
            """,
            metadata={'source': 'tech_doc.md', 'type': 'markdown'}
        )
        
        # 示例2：Python代码
        python_code = Document(
            page_content="""
            def calculate_similarity(text1: str, text2: str) -> float:
            \"\"\"计算文本相似度\"\"\"
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            
            return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            class DocumentProcessor:
                def __init__(self, chunk_size: int = 1000):
                    self.chunk_size = chunk_size
                
                def process(self, text: str) -> List[str]:
                    return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
            """,
            metadata={'source': 'example.py', 'type': 'python'}
        )
        
        # 示例3：普通文本
        plain_text = Document(
            page_content="""
            人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
            
            该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
            
            可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。人工智能可以对人的意识、思维的信息过程的模拟。
            
            人工智能不是人的智能，但能像人那样思考、也可能超过人的智能。人工智能是一门极富挑战性的科学，从事这项工作的人必须懂得计算机知识、心理学和哲学。
            """,
            metadata={'source': 'plain_text.txt', 'type': 'text'}
        )
        
        documents.extend([tech_doc, python_code, plain_text])
        return documents
    
    def run_performance_benchmark(self) -> Dict[str, Any]:
        """运行性能基准测试"""
        documents = self.create_sample_documents()
        
        # 测试不同的分割器
        splitters = {
            'Character': CharacterTextSplitter(chunk_size=1000, chunk_overlap=100),
            'Token': TokenTextSplitter(chunk_size=200, chunk_overlap=20),
            'Recursive': RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100,
                separators=["\n\n", "\n", ". ", " ", ""]
            ),
            'Markdown': MarkdownTextSplitter(chunk_size=500, chunk_overlap=50),
            'PythonCode': PythonCodeTextSplitter(chunk_size=800, chunk_overlap=80)
        }
        
        results = {}
        evaluator = SplitQualityEvaluator()
        
        for splitter_name, splitter in splitters.items():
            print(f"\n🧪 测试分割器: {splitter_name}")
            
            splitter_results = []
            for doc in documents:
                start_time = datetime.now()
                chunks = splitter.split_documents([doc])
                end_time = datetime.now()
                
                processing_time = (end_time - start_time).total_seconds()
                
                # 评估质量
                chunk_texts = [chunk.page_content for chunk in chunks]
                quality_scores = evaluator.evaluate_splits(doc.page_content, chunk_texts)
                
                result = {
                    'document_type': doc.metadata.get('type', 'unknown'),
                    'original_length': len(doc.page_content),
                    'chunk_count': len(chunks),
                    'avg_chunk_size': np.mean([len(c.page_content) for c in chunks]),
                    'processing_time': processing_time,
                    'quality_scores': quality_scores
                }
                
                splitter_results.append(result)
            
            results[splitter_name] = splitter_results
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成测试报告"""
        report = []
        report.append("=" * 60)
        report.append("LangChain文档转换器性能测试报告")
        report.append("=" * 60)
        
        for splitter_name, splitter_results in results.items():
            report.append(f"\n📊 {splitter_name} 分割器")
            report.append("-" * 40)
            
            for result in splitter_results:
                report.append(f"文档类型: {result['document_type']}")
                report.append(f"原文长度: {result['original_length']} 字符")
                report.append(f"分块数量: {result['chunk_count']}")
                report.append(f"平均分块大小: {result['avg_chunk_size']:.1f} 字符")
                report.append(f"处理时间: {result['processing_time']:.3f} 秒")
                report.append(f"质量评分: {json.dumps(result['quality_scores'], indent=2, ensure_ascii=False)}")
                report.append("")
        
        return "\n".join(report)

def main():
    """主函数演示"""
    print("🚀 LangChain文档转换器完整实现演示")
    print("=" * 50)
    
    # 创建演示实例
    demo = DocumentTransformerDemo()
    
    # 运行性能基准测试
    print("\n📈 运行性能基准测试...")
    benchmark_results = demo.run_performance_benchmark()
    
    # 生成报告
    report = demo.generate_report(benchmark_results)
    print(report)
    
    # 保存结果
    with open('document_transformer_benchmark.json', 'w', encoding='utf-8') as f:
        json.dump(benchmark_results, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 测试完成！结果已保存到 document_transformer_benchmark.json")
    
    # 实际文件处理示例
    print("\n📁 实际文件处理示例")
    
    # 创建示例文件
    os.makedirs('sample_docs', exist_ok=True)
    
    # 创建示例文件
    with open('sample_docs/sample.md', 'w', encoding='utf-8') as f:
        f.write("""
# 示例Markdown文档

## 第一部分
这是一个关于LangChain的示例文档。

### 子部分1
包含一些技术细节和代码示例。

## 第二部分
讨论了实际应用场景。

### 子部分2
提供了使用建议和最佳实践。
""")
    
    with open('sample_docs/sample.py', 'w', encoding='utf-8') as f:
        f.write("""
def hello_world():
    \"\"\"打印问候语\"\"\"
    print("Hello, World!")

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
""")
    
    # 处理示例目录
    processor = EnterpriseDocumentProcessor()
    results = processor.process_directory('sample_docs')
    
    print(f"\n✅ 处理了 {len(results)} 个文件")
    for result in results:
        summary = result['processing_summary']
        print(f"文件: {summary['file_path']}")
        print(f"分块数: {result['chunk_count']}")
        print(f"平均分块大小: {summary['avg_chunk_size']:.1f} 字符")
        print("-" * 30)

if __name__ == "__main__":
    main()