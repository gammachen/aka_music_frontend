#!/usr/bin/env python3
"""
测试脚本：验证AI对话系统的基本功能
"""

import requests
import json
import time
from urllib.parse import urljoin

class TestClient:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def register_user(self, username, email, password):
        """注册用户"""
        url = urljoin(self.base_url, '/register')
        data = {
            'username': username,
            'email': email,
            'password': password
        }
        
        try:
            response = self.session.post(url, data=data)
            print(f"注册响应: {response.status_code} - {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"注册失败: {e}")
            return False
    
    def login_user(self, username, password):
        """用户登录"""
        url = urljoin(self.base_url, '/login')
        data = {
            'username': username,
            'password': password
        }
        
        try:
            response = self.session.post(url, data=data)
            print(f"登录响应: {response.status_code} - {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"登录失败: {e}")
            return False
    
    def send_message(self, message):
        """发送消息"""
        url = urljoin(self.base_url, '/api/chat')
        data = {'message': message}
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"AI回复: {result.get('response', '无回复')}")
                return result
            else:
                print(f"发送消息失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"发送消息异常: {e}")
            return None
    
    def get_chat_history(self):
        """获取聊天历史"""
        url = urljoin(self.base_url, '/api/chat/history')
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                result = response.json()
                print(f"历史记录: {len(result.get('history', []))} 条")
                return result
            else:
                print(f"获取历史失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"获取历史异常: {e}")
            return None
    
    def clear_history(self):
        """清空历史"""
        url = urljoin(self.base_url, '/api/chat/clear')
        
        try:
            response = self.session.post(url)
            print(f"清空历史响应: {response.status_code} - {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"清空历史异常: {e}")
            return False

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始测试AI对话系统...")
    
    client = TestClient()
    
    # 测试1：注册用户
    print("\n📋 测试1: 用户注册")
    username = f"testuser_{int(time.time())}"
    email = f"{username}@example.com"
    password = "testpass123"
    
    if not client.register_user(username, email, password):
        print("❌ 注册失败，测试终止")
        return False
    
    # 测试2：用户登录
    print("\n🔐 测试2: 用户登录")
    if not client.login_user(username, password):
        print("❌ 登录失败，测试终止")
        return False
    
    # 测试3：发送消息
    print("\n💬 测试3: 发送消息")
    messages = [
        "你好，我是测试用户",
        "请介绍一下你自己",
        "今天天气怎么样？"
    ]
    
    for msg in messages:
        print(f"\n发送: {msg}")
        result = client.send_message(msg)
        if result:
            print("✅ 消息发送成功")
        else:
            print("❌ 消息发送失败")
        time.sleep(1)  # 避免API限制
    
    # 测试4：获取历史
    print("\n📜 测试4: 获取聊天历史")
    history = client.get_chat_history()
    if history:
        print(f"✅ 获取历史成功，共 {len(history.get('history', []))} 条记录")
    else:
        print("❌ 获取历史失败")
    
    # 测试5：清空历史
    print("\n🗑️ 测试5: 清空历史")
    if client.clear_history():
        print("✅ 清空历史成功")
    else:
        print("❌ 清空历史失败")
    
    print("\n🎉 测试完成！")
    return True

def check_server_status():
    """检查服务器状态"""
    try:
        response = requests.get("http://127.0.0.1:5000/login", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

if __name__ == "__main__":
    print("🔍 检查服务器状态...")
    
    if not check_server_status():
        print("❌ 服务器未启动，请先运行: python run.py")
        print("然后在另一个终端运行此测试脚本")
        exit(1)
    
    print("✅ 服务器已启动")
    test_basic_functionality()