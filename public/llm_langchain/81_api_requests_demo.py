#!/usr/bin/env python3
"""
API链和LLMRequestsChain完整演示脚本
包含：
1. 自定义RESTful Mock服务
2. LLMRequestsChain集成
3. 企业智能助手实现
4. 供应商查询、用户权限、假期管理等功能

运行前请确保安装：
pip install langchain langchain-openai flask requests
"""

import json
import time
import threading
from flask import Flask, jsonify, request
from langchain.chains import LLMRequestsChain, LLMChain
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate
import requests

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
                    "id": "EMP001",
                    "name": "张三",
                    "department": "技术部",
                    "position": "高级工程师",
                    "annual_leave": 15,
                    "used_leave": 7,
                    "remaining_leave": 8,
                    "sick_leave": 5,
                    "maternity_leave_eligible": True
                },
                "李四": {
                    "id": "EMP002", 
                    "name": "李四",
                    "department": "市场部",
                    "position": "销售经理",
                    "annual_leave": 12,
                    "used_leave": 3,
                    "remaining_leave": 9,
                    "sick_leave": 3,
                    "maternity_leave_eligible": False
                },
                "王五": {
                    "id": "EMP003",
                    "name": "王五", 
                    "department": "人事部",
                    "position": "HR专员",
                    "annual_leave": 10,
                    "used_leave": 2,
                    "remaining_leave": 8,
                    "sick_leave": 4,
                    "maternity_leave_eligible": True
                }
            },
            "users": {
                "user123": {
                    "id": "user123",
                    "username": "admin",
                    "permissions": [
                        "read:all",
                        "write:all", 
                        "delete:all",
                        "admin:access"
                    ],
                    "role": "超级管理员"
                },
                "user456": {
                    "id": "user456", 
                    "username": "manager",
                    "permissions": [
                        "read:departments",
                        "write:own_department",
                        "approve:leave_requests"
                    ],
                    "role": "部门经理"
                },
                "user789": {
                    "id": "user789",
                    "username": "employee", 
                    "permissions": [
                        "read:own_profile",
                        "apply:leave",
                        "view:payslip"
                    ],
                    "role": "普通员工"
                }
            },
            "suppliers": {
                "electronics": [
                    {
                        "id": "SUP001",
                        "name": "华强北电子",
                        "category": "electronics",
                        "contact": "13800138001",
                        "rating": 4.8,
                        "products": ["手机配件", "电脑配件", "电子元件"],
                        "status": "active"
                    },
                    {
                        "id": "SUP002",
                        "name": "深圳科技",
                        "category": "electronics", 
                        "contact": "13900139002",
                        "rating": 4.5,
                        "products": ["智能硬件", "物联网设备"],
                        "status": "active"
                    }
                ],
                "food": [
                    {
                        "id": "SUP003",
                        "name": "绿色食品",
                        "category": "food",
                        "contact": "13700137003",
                        "rating": 4.7,
                        "products": ["有机蔬菜", "健康食品"],
                        "status": "active"
                    }
                ]
            },
            "policies": {
                "maternity": {
                    "title": "产假政策",
                    "content": """
                    1. 基础产假：女职工生育享受98天产假，其中产前可以休假15天
                    2. 难产增加：难产的，增加产假15天
                    3. 多胞胎：生育多胞胎的，每多生育1个婴儿增加产假15天
                    4. 晚育奖励：符合晚育条件的，增加产假30天
                    5. 陪产假：男职工享受15天陪产假
                    6. 工资待遇：产假期间工资照发，不影响福利待遇
                    """,
                    "effective_date": "2024-01-01",
                    "applicable_to": "全体正式员工"
                },
                "annual_leave": {
                    "title": "年假政策",
                    "content": """
                    1. 工作满1年不满10年的：年假5天
                    2. 工作满10年不满20年的：年假10天  
                    3. 工作满20年以上的：年假15天
                    4. 国家法定节假日不计入年假
                    5. 年假需在当年内使用完毕，最多可延期至次年3月
                    """,
                    "effective_date": "2024-01-01",
                    "applicable_to": "全体正式员工"
                }
            }
        }
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/api/employees/<employee_name>/leave-balance', methods=['GET'])
        def get_employee_leave(employee_name):
            """获取员工假期余额"""
            employee = self.mock_data["employees"].get(employee_name)
            if not employee:
                return jsonify({"error": "员工不存在"}), 404
            
            return jsonify({
                "employee": employee_name,
                "annual_leave": employee["annual_leave"],
                "used_leave": employee["used_leave"], 
                "remaining_leave": employee["remaining_leave"],
                "sick_leave": employee["sick_leave"],
                "maternity_leave_eligible": employee["maternity_leave_eligible"]
            })
        
        @self.app.route('/api/users/<user_id>/permissions', methods=['GET'])
        def get_user_permissions(user_id):
            """获取用户权限列表"""
            user = self.mock_data["users"].get(user_id)
            if not user:
                return jsonify({"error": "用户不存在"}), 404
            
            return jsonify({
                "user_id": user_id,
                "username": user["username"],
                "role": user["role"],
                "permissions": user["permissions"],
                "permission_count": len(user["permissions"])
            })
        
        @self.app.route('/api/suppliers', methods=['GET'])
        def get_suppliers():
            """获取所有供应商"""
            name = request.args.get('name')
            category = request.args.get('category')
            
            if name:
                # 按名称搜索
                results = []
                for cat_suppliers in self.mock_data["suppliers"].values():
                    for supplier in cat_suppliers:
                        if name.lower() in supplier["name"].lower():
                            results.append(supplier)
                return jsonify({"suppliers": results, "count": len(results)})
            
            elif category:
                # 按类别查询
                suppliers = self.mock_data["suppliers"].get(category, [])
                return jsonify({"category": category, "suppliers": suppliers, "count": len(suppliers)})
            
            else:
                # 返回所有供应商
                all_suppliers = []
                for cat_suppliers in self.mock_data["suppliers"].values():
                    all_suppliers.extend(cat_suppliers)
                return jsonify({"suppliers": all_suppliers, "count": len(all_suppliers)})
        
        @self.app.route('/api/suppliers/category/<category>', methods=['GET'])
        def get_suppliers_by_category(category):
            """按类别获取供应商"""
            suppliers = self.mock_data["suppliers"].get(category, [])
            return jsonify({
                "category": category,
                "suppliers": suppliers,
                "count": len(suppliers)
            })
        
        @self.app.route('/api/policies/<policy_type>', methods=['GET'])
        def get_policy(policy_type):
            """获取政策信息"""
            policy = self.mock_data["policies"].get(policy_type)
            if not policy:
                return jsonify({"error": "政策不存在"}), 404
            
            return jsonify(policy)
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """健康检查"""
            return jsonify({"status": "healthy", "timestamp": time.time()})
    
    def start_server(self):
        """启动服务器"""
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

# ==================== LLMRequestsChain集成 ====================

class EnterpriseSmartAssistant:
    """企业智能助手 - LLMRequestsChain实现"""
    
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
        
        请用简洁明了的中文回答，包含关键数字和要点。
        如果数据为空或错误，请礼貌地告知用户。"""
        
        self.employee_chain = LLMRequestsChain(
            llm_chain=LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    input_variables=["query", "requests_result"],
                    template=employee_template
                )
            ),
            verbose=True
        )
        
        # 政策查询链
        policy_template = """根据API响应解释相关政策。
        
        用户问题: {query}
        政策内容: {requests_result}
        
        请用通俗易懂的中文解释政策要点，分条列出关键信息。
        如果政策不存在，请说明并提供相关建议。"""
        
        self.policy_chain = LLMRequestsChain(
            llm_chain=LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    input_variables=["query", "requests_result"],
                    template=policy_template
                )
            ),
            verbose=True
        )
        
        # 供应商查询链
        supplier_template = """根据API响应提供供应商信息。
        
        用户问题: {query}
        供应商信息: {requests_result}
        
        请用清晰的中文列出供应商信息，包括名称、联系方式、评分和产品。
        如果找不到匹配的供应商，请提供建议。"""
        
        self.supplier_chain = LLMRequestsChain(
            llm_chain=LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    input_variables=["query", "requests_result"],
                    template=supplier_template
                )
            ),
            verbose=True
        )
    
    def query_employee_leave(self, employee_name):
        """查询员工假期信息"""
        try:
            return self.employee_chain.invoke({
                "query": f"查询{employee_name}的假期余额",
                "url": f"{self.base_url}/api/employees/{employee_name}/leave-balance"
            })
        except Exception as e:
            return {"output": f"查询失败：{str(e)}"}
    
    def query_maternity_policy(self):
        """查询产假政策"""
        try:
            return self.policy_chain.invoke({
                "query": "查询公司的产假政策",
                "url": f"{self.base_url}/api/policies/maternity"
            })
        except Exception as e:
            return {"output": f"查询失败：{str(e)}"}
    
    def query_annual_leave_policy(self):
        """查询年假政策"""
        try:
            return self.policy_chain.invoke({
                "query": "查询公司的年假政策",
                "url": f"{self.base_url}/api/policies/annual_leave"
            })
        except Exception as e:
            return {"output": f"查询失败：{str(e)}"}
    
    def query_user_permissions(self, user_id):
        """查询用户权限列表"""
        try:
            return self.employee_chain.invoke({
                "query": f"查询用户{user_id}的权限列表",
                "url": f"{self.base_url}/api/users/{user_id}/permissions"
            })
        except Exception as e:
            return {"output": f"查询失败：{str(e)}"}
    
    def query_suppliers(self, category=None, name=None):
        """查询供应商信息"""
        try:
            if name:
                url = f"{self.base_url}/api/suppliers?name={name}"
                query = f"按名称搜索供应商：{name}"
            elif category:
                url = f"{self.base_url}/api/suppliers/category/{category}"
                query = f"查询{category}类别的供应商"
            else:
                url = f"{self.base_url}/api/suppliers"
                query = "查询所有供应商"
            
            return self.supplier_chain.invoke({
                "query": query,
                "url": url
            })
        except Exception as e:
            return {"output": f"查询失败：{str(e)}"}

# ==================== 测试和演示 ====================

def start_mock_server():
    """启动Mock服务器（在后台线程）"""
    mock_api = MockEnterpriseAPI(port=8000)
    server_thread = threading.Thread(target=mock_api.start_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # 等待服务器启动
    print("✅ Mock服务器已启动在 http://localhost:8000")
    return mock_api

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:8000"
    
    print("\n=== 测试API端点 ===")
    
    # 健康检查
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ 健康检查: {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False
    
    # 测试员工查询
    try:
        response = requests.get(f"{base_url}/api/employees/张三/leave-balance")
        print(f"✅ 员工假期查询: {response.json()}")
    except Exception as e:
        print(f"❌ 员工查询失败: {e}")
    
    return True

def demonstrate_llm_requests_chain():
    """演示LLMRequestsChain功能"""
    
    print("\n=== LLMRequestsChain企业智能助手演示 ===")
    
    # 初始化助手
    assistant = EnterpriseSmartAssistant(base_url="http://localhost:8000")
    
    # 演示各种查询
    print("\n1️⃣ 员工假期查询：")
    result = assistant.query_employee_leave("张三")
    print(f"   {result['output']}")
    
    print("\n2️⃣ 产假政策查询：")
    result = assistant.query_maternity_policy()
    print(f"   {result['output']}")
    
    print("\n3️⃣ 年假政策查询：")
    result = assistant.query_annual_leave_policy()
    print(f"   {result['output']}")
    
    print("\n4️⃣ 用户权限查询：")
    result = assistant.query_user_permissions("user123")
    print(f"   {result['output']}")
    
    print("\n5️⃣ 供应商类别查询：")
    result = assistant.query_suppliers(category="electronics")
    print(f"   {result['output']}")
    
    print("\n6️⃣ 供应商名称搜索：")
    result = assistant.query_suppliers(name="华强北")
    print(f"   {result['output']}")

# ==================== 主程序 ====================

def main():
    """主程序入口"""
    
    print("🚀 LLMRequestsChain企业智能助手演示")
    print("=" * 50)
    
    # 启动Mock服务器
    mock_api = start_mock_server()
    
    # 测试API端点
    if not test_api_endpoints():
        print("❌ API测试失败，请检查服务")
        return
    
    # 演示LLMRequestsChain
    demonstrate_llm_requests_chain()
    
    print("\n✅ 演示完成！")
    print("\n📋 可用API端点：")
    print("  - GET /api/employees/{name}/leave-balance")
    print("  - GET /api/users/{id}/permissions") 
    print("  - GET /api/suppliers")
    print("  - GET /api/suppliers/category/{category}")
    print("  - GET /api/policies/{type}")
    print("  - GET /api/health")

if __name__ == "__main__":
    main()