#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG vs 微调决策工具 - 简化版
用于帮助技术团队快速决策使用RAG还是微调
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum

class ScenarioType(Enum):
    KNOWLEDGE_QA = "知识问答"
    CUSTOMER_SERVICE = "客服系统"
    MEDICAL_DIAGNOSIS = "医疗诊断"
    FINANCIAL_ANALYSIS = "金融分析"
    CODE_GENERATION = "代码生成"
    CREATIVE_WRITING = "创意写作"

@dataclass
class ScenarioProfile:
    """场景配置文件"""
    name: str
    description: str
    data_size: str  # "小", "中", "大"
    update_frequency: str  # "低", "中", "高"
    accuracy_requirement: str  # "低", "中", "高"
    latency_requirement: str  # "宽松", "一般", "严格"
    domain_specificity: str  # "通用", "专业", "高度专业"
    cost_budget: str  # "低", "中", "高"
    
    def get_rag_score(self) -> int:
        """计算RAG适用性评分"""
        score = 0
        
        # 数据量越大，RAG越有优势
        if self.data_size == "大":
            score += 30
        elif self.data_size == "中":
            score += 20
        else:
            score += 10
            
        # 更新频率越高，RAG越有优势
        if self.update_frequency == "高":
            score += 25
        elif self.update_frequency == "中":
            score += 15
        else:
            score += 5
            
        # 延迟要求越宽松，RAG越有优势
        if self.latency_requirement == "宽松":
            score += 20
        elif self.latency_requirement == "一般":
            score += 15
        else:
            score += 5
            
        # 领域专业性越低，RAG越有优势
        if self.domain_specificity == "通用":
            score += 15
        elif self.domain_specificity == "专业":
            score += 10
        else:
            score += 5
            
        # 成本预算越低，RAG越有优势
        if self.cost_budget == "低":
            score += 10
        elif self.cost_budget == "中":
            score += 5
        else:
            score += 0
            
        return score
    
    def get_finetune_score(self) -> int:
        """计算微调适用性评分"""
        score = 0
        
        # 数据量适中时微调最佳
        if self.data_size == "中":
            score += 25
        elif self.data_size == "大":
            score += 20
        else:
            score += 15
            
        # 更新频率越低，微调越有优势
        if self.update_frequency == "低":
            score += 25
        elif self.update_frequency == "中":
            score += 15
        else:
            score += 5
            
        # 准确率要求越高，微调越有优势
        if self.accuracy_requirement == "高":
            score += 20
        elif self.accuracy_requirement == "中":
            score += 15
        else:
            score += 10
            
        # 领域专业性越高，微调越有优势
        if self.domain_specificity == "高度专业":
            score += 20
        elif self.domain_specificity == "专业":
            score += 15
        else:
            score += 5
            
        # 成本预算越高，微调越有优势
        if self.cost_budget == "高":
            score += 10
        elif self.cost_budget == "中":
            score += 5
        else:
            score += 0
            
        return score

class DecisionEngine:
    """决策引擎"""
    
    def __init__(self):
        self.scenarios = self._load_scenarios()
    
    def _load_scenarios(self) -> Dict[str, ScenarioProfile]:
        """加载预定义场景"""
        return {
            "电商客服": ScenarioProfile(
                name="电商客服系统",
                description="处理商品咨询、订单查询、退换货等",
                data_size="大",
                update_frequency="高",
                accuracy_requirement="中",
                latency_requirement="严格",
                domain_specificity="专业",
                cost_budget="中"
            ),
            "医疗诊断": ScenarioProfile(
                name="医疗诊断助手",
                description="辅助医生进行疾病诊断和治疗建议",
                data_size="中",
                update_frequency="中",
                accuracy_requirement="高",
                latency_requirement="一般",
                domain_specificity="高度专业",
                cost_budget="高"
            ),
            "金融风控": ScenarioProfile(
                name="金融风控系统",
                description="评估信贷风险、欺诈检测等",
                data_size="大",
                update_frequency="高",
                accuracy_requirement="高",
                latency_requirement="严格",
                domain_specificity="高度专业",
                cost_budget="高"
            ),
            "代码生成": ScenarioProfile(
                name="代码生成工具",
                description="根据需求生成高质量代码",
                data_size="中",
                update_frequency="中",
                accuracy_requirement="高",
                latency_requirement="一般",
                domain_specificity="专业",
                cost_budget="中"
            ),
            "智能问答": ScenarioProfile(
                name="通用问答系统",
                description="回答各类常识性问题",
                data_size="大",
                update_frequency="高",
                accuracy_requirement="中",
                latency_requirement="一般",
                domain_specificity="通用",
                cost_budget="低"
            ),
            "创意写作": ScenarioProfile(
                name="创意写作助手",
                description="协助创作文章、诗歌、广告文案等",
                data_size="小",
                update_frequency="低",
                accuracy_requirement="中",
                latency_requirement="宽松",
                domain_specificity="通用",
                cost_budget="低"
            )
        }
    
    def analyze_scenario(self, profile: ScenarioProfile) -> Dict:
        """分析场景并给出建议"""
        rag_score = profile.get_rag_score()
        finetune_score = profile.get_finetune_score()
        
        # 计算相对优势
        total = rag_score + finetune_score
        if total > 0:
            rag_ratio = (rag_score / total) * 100
            finetune_ratio = (finetune_score / total) * 100
        else:
            rag_ratio = finetune_ratio = 50
        
        # 决策逻辑
        if rag_score > finetune_score + 20:
            recommendation = "强烈建议使用RAG"
            reasoning = [
                "数据量大且更新频繁，RAG更适合动态知识",
                "成本相对较低，易于维护和扩展",
                "延迟要求可通过优化缓解"
            ]
        elif finetune_score > rag_score + 20:
            recommendation = "强烈建议使用微调"
            reasoning = [
                "准确率要求高，微调能提供更精准结果",
                "领域专业性强，需要深度定制",
                "数据相对稳定，适合一次性训练"
            ]
        else:
            recommendation = "建议混合使用"
            reasoning = [
                "两者各有优势，可结合使用",
                "RAG处理动态知识，微调处理核心能力",
                "通过路由机制动态选择"
            ]
        
        return {
            "scenario": profile.name,
            "rag_score": rag_score,
            "finetune_score": finetune_score,
            "rag_ratio": round(rag_ratio, 1),
            "finetune_ratio": round(finetune_ratio, 1),
            "recommendation": recommendation,
            "reasoning": reasoning
        }
    
    def compare_all_scenarios(self) -> List[Dict]:
        """比较所有预定义场景"""
        results = []
        for name, profile in self.scenarios.items():
            result = self.analyze_scenario(profile)
            results.append(result)
        return results
    
    def interactive_demo(self):
        """交互式演示"""
        print("=== RAG vs 微调决策工具 ===\n")
        
        # 显示所有预定义场景
        print("预定义场景:")
        for i, (name, profile) in enumerate(self.scenarios.items(), 1):
            print(f"{i}. {name} - {profile.description}")
        
        print("\n" + "="*50)
        
        # 分析所有场景
        results = self.compare_all_scenarios()
        
        print("\n决策结果:")
        print("-" * 80)
        for result in results:
            print(f"\n【{result['scenario']}】")
            print(f"RAG适用性: {result['rag_ratio']}% | 微调适用性: {result['finetune_ratio']}%")
            print(f"建议: {result['recommendation']}")
            print("理由:")
            for reason in result['reasoning']:
                print(f"  • {reason}")
        
        print("\n" + "="*50)
        print("技术实现建议:")
        print("1. RAG技术栈: LangChain + Chroma/Qdrant + OpenAI")
        print("2. 微调技术栈: LoRA/QLoRA + PEFT + Transformers")
        print("3. 混合架构: 路由层 + 并行处理 + 结果融合")

def main():
    """主函数"""
    engine = DecisionEngine()
    engine.interactive_demo()
    
    # 保存结果到JSON
    results = engine.compare_all_scenarios()
    with open('rag_finetune_decision_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n决策结果已保存到: rag_finetune_decision_results.json")

if __name__ == "__main__":
    main()