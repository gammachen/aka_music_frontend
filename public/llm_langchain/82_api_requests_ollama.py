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
    """企业级Mock API服务"""
    
    def __init__(self, port=8000):
        self.app = Flask(__name__)
        self.port = port
        self.setup_routes()
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self):
        """生成模拟数据"""
        return {
            "employees": {
                "张三": {
                    "name": "张三",
                    "department": "技术部",
                    "annual_leave": 15,
                    "used_leave": 7,
                    "remaining_leave": 8,
                    "sick_leave": 5,
                    "maternity_leave_eligible": True
                },
                "李四": {
                    "name": "李四",
                    "department": "市场部", 
                    "annual_leave": 12,
                    "used_leave": 3,
                    "remaining_leave": 9,
                    "maternity_leave_eligible": False
                }
            },
            "suppliers": {
                "electronics": [
                    {
                        "name": "华强北电子",
                        "contact": "13800138001",
                        "rating": 4.8,
                        "products": ["手机配件", "电脑配件"],
                        "status": "active"
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
                    """
                }
            }
        }
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/api/employees/<employee_name>/leave-balance', methods=['GET'])
        def get_employee_leave(employee_name):
            employee = self.mock_data["employees"].get(employee_name)
            if not employee:
                return jsonify({"error": "员工不存在"}), 404
            return jsonify(employee)
        
        @self.app.route('/api/suppliers', methods=['GET'])
        def get_suppliers():
            category = request.args.get('category', 'all')
            return jsonify({
                "suppliers": self.mock_data["suppliers"],
                "category": category
            })
        
        @self.app.route('/api/policies/<policy_type>', methods=['GET'])
        def get_policy(policy_type):
            policy = self.mock_data["policies"].get(policy_type)
            if not policy:
                return jsonify({"error": "政策不存在"}), 404
            return jsonify(policy)
    
    def start_server(self):
        """启动服务器"""
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

# ==================== LLMRequestsChain实现 ====================

class OllamaLLMRequestsChain:
    """兼容Ollama的LLMRequestsChain"""
    
    def __init__(self, llm, prompt_template):
        self.llm = llm
        self.prompt_template = prompt_template
        self.llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    
    def invoke(self, inputs):
        """执行链式调用"""
        query = inputs["query"]
        url = inputs["url"]
        
        # 获取API数据
        response = requests.get(url)
        api_data = response.json()
        
        # 构建提示
        prompt = self.prompt_template.format(
            query=query,
            api_response=json.dumps(api_data, ensure_ascii=False, indent=2)
        )
        
        # 调用LLM
        result = self.llm.invoke(prompt)
        return {"output": result}

class EnterpriseSmartAssistant:
    """企业智能助手"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.llm = Ollama(model="gpt-3.5-turbo:latest", temperature=0.3)
        self.setup_chains()
    
    def setup_chains(self):
        """设置各种查询链"""
        
        # 员工查询链
        employee_prompt = PromptTemplate(
            input_variables=["query", "api_response"],
            template="""基于API响应回答员工假期问题：

问题：{query}
API响应：{api_response}

请用简洁的中文回答，包含关键数字。"""
        )
        self.employee_chain = OllamaLLMRequestsChain(self.llm, employee_prompt)
        
        # 政策查询链  
        policy_prompt = PromptTemplate(
            input_variables=["query", "api_response"],
            template="""基于API响应解释政策：

问题：{query}
政策内容：{api_response}

请用通俗易懂的中文解释政策要点。"""
        )
        self.policy_chain = OllamaLLMRequestsChain(self.llm, policy_prompt)
        
        # 供应商查询链
        supplier_prompt = PromptTemplate(
            input_variables=["query", "api_response"],
            template="""基于API响应提供供应商信息：

问题：{query}
供应商信息：{api_response}

请用中文列出供应商详细信息。"""
        )
        self.supplier_chain = OllamaLLMRequestsChain(self.llm, supplier_prompt)
    
    def query_employee_leave(self, employee_name):
        """查询员工假期"""
        return self.employee_chain.invoke({
            "query": f"查询{employee_name}的假期余额",
            "url": f"{self.base_url}/api/employees/{employee_name}/leave-balance"
        })
    
    def query_maternity_policy(self):
        """查询产假政策"""
        return self.policy_chain.invoke({
            "query": "产假政策是什么",
            "url": f"{self.base_url}/api/policies/maternity"
        })
    
    def query_suppliers(self, category="electronics"):
        """查询供应商"""
        return self.supplier_chain.invoke({
            "query": f"查询{category}类别的供应商",
            "url": f"{self.base_url}/api/suppliers?category={category}"
        })

# ==================== 演示 ====================

def main():
    """主程序"""
    
    print("🚀 LLMRequestsChain企业智能助手演示")
    print("=" * 50)
    
    # 启动Mock服务器
    mock_api = MockEnterpriseAPI()
    server_thread = threading.Thread(target=mock_api.start_server, daemon=True)
    server_thread.start()
    time.sleep(3)
    print("✅ Mock服务器已启动")
    
    # 初始化助手
    assistant = EnterpriseSmartAssistant()
    
    # 演示查询
    print("\n=== 智能查询演示 ===")
    
    # 1. 员工假期查询
    print("\n1️⃣ 员工假期查询：")
    result = assistant.query_employee_leave("张三")
    print(f"结果：{result['output']}")
    
    # 2. 产假政策查询
    print("\n2️⃣ 产假政策查询：")
    result = assistant.query_maternity_policy()
    print(f"结果：{result['output']}")
    
    # 3. 供应商查询
    print("\n3️⃣ 供应商查询：")
    result = assistant.query_suppliers("electronics")
    print(f"结果：{result['output']}")
    
    print("\n✅ 演示完成！")

if __name__ == "__main__":
    main()