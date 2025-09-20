import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('chroma_db', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 启动AI对话系统...")
    print("📱 访问 http://127.0.0.1:5000 开始使用")
    print("📝 请先注册账号，然后登录开始对话")
    
    app.run(debug=True, host='0.0.0.0', port=5000)