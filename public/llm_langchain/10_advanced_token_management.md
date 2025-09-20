# 高级Token管理策略与最佳实践

## 目录
1. [Token成本控制框架](#token成本控制框架)
2. [智能缓存策略](#智能缓存策略)
3. [动态模型选择](#动态模型选择)
4. [Prompt压缩技术](#prompt压缩技术)
5. [上下文窗口优化](#上下文窗口优化)
6. [生产环境监控](#生产环境监控)
7. [成本优化案例研究](#成本优化案例研究)

---

## Token成本控制框架

### 1.1 分层成本模型

```python
class TokenCostTier:
    """分层Token成本模型"""
    
    TIERS = {
        "tier_1": {
            "max_daily_cost": 5.0,
            "allowed_models": ["gpt-3.5-turbo"],
            "max_tokens_per_request": 1000,
            "priority": "low"
        },
        "tier_2": {
            "max_daily_cost": 20.0,
            "allowed_models": ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
            "max_tokens_per_request": 4000,
            "priority": "medium"
        },
        "tier_3": {
            "max_daily_cost": 100.0,
            "allowed_models": ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"],
            "max_tokens_per_request": 8000,
            "priority": "high"
        }
    }
```

### 1.2 智能预算分配

```python
class SmartBudgetAllocator:
    """智能预算分配器"""
    
    def __init__(self, total_budget: float):
        self.total_budget = total_budget
        self.allocated_budgets = {}
    
    def allocate_by_priority(self, requests: List[Dict]) -> Dict:
        """按优先级分配预算"""
        
        # 优先级权重
        weights = {
            "critical": 0.5,
            "high": 0.3,
            "medium": 0.15,
            "low": 0.05
        }
        
        allocations = {}
        for request in requests:
            priority = request.get("priority", "medium")
            weight = weights.get(priority, 0.1)
            allocations[request["id"]] = self.total_budget * weight
        
        return allocations
```

---

## 智能缓存策略

### 2.1 多级缓存架构

```python
class TokenCacheManager:
    """多级Token缓存管理器"""
    
    def __init__(self):
        self.l1_cache = {}  # 内存缓存
        self.l2_cache = {}  # Redis缓存
        self.l3_cache = {}  # 数据库缓存
    
    def cache_key(self, text: str, model: str, temperature: float) -> str:
        """生成缓存键"""
        import hashlib
        content = f"{text}_{model}_{temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_response(self, key: str) -> Optional[str]:
        """获取缓存响应"""
        
        # L1 缓存
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # L2 缓存
        if key in self.l2_cache:
            response = self.l2_cache[key]
            self.l1_cache[key] = response  # 提升到L1
            return response
        
        # L3 缓存
        if key in self.l3_cache:
            response = self.l3_cache[key]
            self.l2_cache[key] = response  # 提升到L2
            return response
        
        return None
```

### 2.2 语义缓存策略

```python
class SemanticCache:
    """基于语义的缓存系统"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.threshold = similarity_threshold
        self.cache = []
    
    def find_similar(self, query: str, embeddings) -> Optional[str]:
        """查找语义相似的缓存"""
        
        query_embedding = embeddings.embed_query(query)
        
        for cached_item in self.cache:
            similarity = self.cosine_similarity(
                query_embedding, 
                cached_item["embedding"]
            )
            
            if similarity > self.threshold:
                return cached_item["response"]
        
        return None
    
    def cosine_similarity(self, vec1, vec2) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude = (sum(a * a for a in vec1) ** 0.5) * (sum(b * b for b in vec2) ** 0.5)
        return dot_product / magnitude if magnitude > 0 else 0
```

---

## 动态模型选择

### 3.1 智能模型路由器

```python
class SmartModelRouter:
    """智能模型路由器"""
    
    def __init__(self):
        self.routing_rules = {
            "simple_qa": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 500,
                "criteria": [
                    "问题长度 < 100字",
                    "无复杂推理",
                    "标准问答格式"
                ]
            },
            "complex_analysis": {
                "model": "gpt-4",
                "max_tokens": 2000,
                "criteria": [
                    "需要深度分析",
                    "多步骤推理",
                    "专业领域知识"
                ]
            },
            "code_generation": {
                "model": "gpt-4-turbo",
                "max_tokens": 4000,
                "criteria": [
                    "包含代码",
                    "需要调试",
                    "性能优化"
                ]
            }
        }
    
    def route_request(self, text: str, context: Dict) -> Dict:
        """智能路由请求"""
        
        # 特征提取
        features = self.extract_features(text, context)
        
        # 匹配路由规则
        for route_type, rules in self.routing_rules.items():
            if self.matches_criteria(features, rules["criteria"]):
                return {
                    "model": rules["model"],
                    "max_tokens": rules["max_tokens"],
                    "route_type": route_type,
                    "estimated_cost": self.estimate_cost(text, rules["model"])
                }
        
        # 默认路由
        return {
            "model": "gpt-3.5-turbo",
            "max_tokens": 1000,
            "route_type": "default",
            "estimated_cost": self.estimate_cost(text, "gpt-3.5-turbo")
        }
    
    def extract_features(self, text: str, context: Dict) -> Dict:
        """提取文本特征"""
        
        return {
            "length": len(text),
            "has_code": "```" in text or "def " in text,
            "complexity_words": sum(1 for word in ["分析", "推理", "深度", "复杂"] if word in text),
            "question_type": self.detect_question_type(text),
            "context_length": len(context.get("history", ""))
        }
    
    def detect_question_type(self, text: str) -> str:
        """检测问题类型"""
        
        if any(word in text for word in ["为什么", "如何", "解释", "说明"]):
            return "explanation"
        elif any(word in text for word in ["代码", "程序", "函数"]):
            return "code"
        elif any(word in text for word in ["比较", "区别", "优缺点"]):
            return "comparison"
        else:
            return "general"
```

---

## Prompt压缩技术

### 4.1 智能Prompt压缩

```python
class PromptCompressor:
    """智能Prompt压缩器"""
    
    def __init__(self):
        self.compression_techniques = {
            "remove_redundancy": True,
            "summarize_context": True,
            "extract_keywords": True,
            "format_optimization": True
        }
    
    def compress_prompt(self, prompt: str, max_tokens: int) -> str:
        """压缩Prompt到指定Token数"""
        
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
        current_tokens = len(encoding.encode(prompt))
        
        if current_tokens <= max_tokens:
            return prompt
        
        # 逐步压缩
        compressed = prompt
        
        # 1. 移除冗余信息
        if self.compression_techniques["remove_redundancy"]:
            compressed = self.remove_redundant_info(compressed)
        
        # 2. 上下文摘要
        if self.compression_techniques["summarize_context"]:
            compressed = self.summarize_context(compressed)
        
        # 3. 关键词提取
        if self.compression_techniques["extract_keywords"]:
            compressed = self.extract_keywords(compressed)
        
        # 4. 格式优化
        if self.compression_techniques["format_optimization"]:
            compressed = self.optimize_format(compressed)
        
        return compressed
    
    def remove_redundant_info(self, text: str) -> str:
        """移除冗余信息"""
        
        redundant_patterns = [
            r"实际上[,，]",
            r"简单来说[,，]",
            r"事实上[,，]",
            r"正如我们所知[,，]",
            r"需要指出的是[,，]"
        ]
        
        import re
        for pattern in redundant_patterns:
            text = re.sub(pattern, "", text)
        
        return text
    
    def summarize_context(self, text: str) -> str:
        """摘要长上下文"""
        
        # 识别长段落并进行摘要
        paragraphs = text.split('\n\n')
        summarized = []
        
        for para in paragraphs:
            if len(para) > 200:
                # 简单摘要策略：保留前50字和后50字
                summary = para[:50] + "..." + para[-50:] if len(para) > 100 else para
                summarized.append(summary)
            else:
                summarized.append(para)
        
        return '\n\n'.join(summarized)
    
    def extract_keywords(self, text: str) -> str:
        """提取关键词"""
        
        # 简单的关键词提取
        keywords = ["重要", "关键", "核心", "主要", "必须", "需要"]
        
        for keyword in keywords:
            if keyword in text:
                # 在关键词前后添加强调标记
                text = text.replace(keyword, f"**{keyword}**")
        
        return text
    
    def optimize_format(self, text: str) -> str:
        """优化格式减少Token"""
        
        # 替换长格式为短格式
        replacements = {
            "人工智能": "AI",
            "机器学习": "ML",
            "深度学习": "DL",
            "自然语言处理": "NLP",
            "大型语言模型": "LLM"
        }
        
        for long_form, short_form in replacements.items():
            text = text.replace(long_form, short_form)
        
        return text
```

---

## 上下文窗口优化

### 5.1 滑动窗口策略

```python
class SlidingContextWindow:
    """滑动上下文窗口管理器"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.context_history = []
    
    def add_to_context(self, text: str, importance_score: float = 1.0):
        """添加到上下文"""
        
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        tokens = len(encoding.encode(text))
        
        self.context_history.append({
            "text": text,
            "tokens": tokens,
            "importance": importance_score,
            "timestamp": datetime.now()
        })
        
        # 维护窗口大小
        self._maintain_window_size()
    
    def _maintain_window_size(self):
        """维护窗口大小"""
        
        total_tokens = sum(item["tokens"] for item in self.context_history)
        
        while total_tokens > self.max_tokens and self.context_history:
            # 移除重要性最低的内容
            min_importance_item = min(
                self.context_history, 
                key=lambda x: (x["importance"], x["timestamp"])
            )
            self.context_history.remove(min_importance_item)
            total_tokens = sum(item["tokens"] for item in self.context_history)
    
    def get_context_string(self) -> str:
        """获取当前上下文字符串"""
        
        return "\n".join(item["text"] for item in self.context_history)
```

---

## 生产环境监控

### 6.1 实时监控仪表板

```python
class ProductionTokenMonitor:
    """生产环境Token监控器"""
    
    def __init__(self):
        self.metrics = {
            "total_cost": 0.0,
            "request_count": 0,
            "error_count": 0,
            "cache_hit_rate": 0.0,
            "average_latency": 0.0
        }
        self.alerts = []
    
    def record_request(self, cost: float, latency: float, cached: bool = False):
        """记录请求"""
        
        self.metrics["total_cost"] += cost
        self.metrics["request_count"] += 1
        
        if not cached:
            self.metrics["cache_hit_rate"] = (
                (self.metrics["cache_hit_rate"] * (self.metrics["request_count"] - 1) + 0) /
                self.metrics["request_count"]
            )
        else:
            self.metrics["cache_hit_rate"] = (
                (self.metrics["cache_hit_rate"] * (self.metrics["request_count"] - 1) + 1) /
                self.metrics["request_count"]
            )
        
        self.metrics["average_latency"] = (
            (self.metrics["average_latency"] * (self.metrics["request_count"] - 1) + latency) /
            self.metrics["request_count"]
        )
        
        # 检查警报条件
        self._check_alerts()
    
    def _check_alerts(self):
        """检查警报条件"""
        
        # 成本警报
        if self.metrics["total_cost"] > 100:
            self.alerts.append({
                "type": "cost",
                "message": f"日成本超过$100: ${self.metrics['total_cost']:.2f}",
                "severity": "high"
            })
        
        # 错误率警报
        if self.metrics["request_count"] > 0:
            error_rate = self.metrics["error_count"] / self.metrics["request_count"]
            if error_rate > 0.1:
                self.alerts.append({
                    "type": "error_rate",
                    "message": f"错误率过高: {error_rate:.1%}",
                    "severity": "medium"
                })
```

---

## 成本优化案例研究

### 7.1 电商客服系统优化

**原始成本结构：**
- 月API调用：50,000次
- 平均成本：$0.02/次
- 月度成本：$1,000

**优化策略：**
1. **缓存策略**：缓存常见问题，命中率60%
2. **模型降级**：80%请求使用GPT-3.5-turbo
3. **Prompt优化**：平均减少30%token

**优化后成本：**
- 缓存节省：$600 (60% × $1,000)
- 模型降级节省：$240 (80% × $300 × 0.8)
- Prompt优化节省：$120 (30% × $400)
- **总节省：$960 (96%)**

### 7.2 内容创作平台优化

**原始成本结构：**
- 日生成文章：1,000篇
- 平均长度：2,000 tokens
- 日成本：$40

**优化策略：**
1. **批量处理**：合并相似请求
2. **模板化**：使用预设模板
3. **质量分级**：不同质量要求使用不同模型

**优化后成本：**
- 批量处理节省：30% ($12/天)
- 模板化节省：40% ($16/天)
- 质量分级节省：20% ($8/天)
- **总节省：$36/天 (90%)**

---

## 最佳实践清单

### 开发阶段
- [ ] 实施Token预算限制
- [ ] 建立缓存机制
- [ ] 设置监控警报
- [ ] 创建成本仪表板
- [ ] 制定降级策略

### 部署阶段
- [ ] 配置自动扩展
- [ ] 设置负载均衡
- [ ] 启用日志记录
- [ ] 配置错误处理
- [ ] 建立回退机制

### 运维阶段
- [ ] 每日成本审查
- [ ] 性能指标监控
- [ ] 用户行为分析
- [ ] 定期优化评估
- [ ] 成本控制培训

---

## 工具集成指南

### 快速开始

```bash
# 安装依赖
pip install tiktoken matplotlib seaborn pandas redis

# 运行示例
python token_cost_calculator.py
python token_visualization.py
```

### 配置文件示例

```yaml
# token_config.yaml
token_management:
  daily_budget: 50.0
  default_model: "gpt-3.5-turbo"
  cache_ttl: 3600
  
alerts:
  cost_threshold: 80
  error_rate_threshold: 5
  
optimization:
  enable_caching: true
  enable_compression: true
  enable_routing: true
```

通过实施这些高级Token管理策略，企业级应用可以实现90%以上的成本优化，同时保持服务质量。