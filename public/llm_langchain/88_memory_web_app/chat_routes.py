from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from memory_manager import get_chain_for_user, MemoryManager, user_chains
import traceback

# 创建蓝图
chat_bp = Blueprint('chat', __name__)

# 创建MemoryManager实例
memory_manager = MemoryManager()

# 全局变量存储用户对话链
# 注意：在生产环境中应使用Redis或数据库来存储
user_chains = {}

@chat_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """处理聊天请求"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        user_id = str(current_user.id)
        
        # 获取或创建该用户的对话链
        if user_id not in user_chains:
            user_chains[user_id] = get_chain_for_user(user_id)
        
        chain = user_chains[user_id]
        
        # 运行对话链
        ai_response = chain.run(input=user_message)
        
        return jsonify({
            'response': ai_response,
            'user_message': user_message,
            'user_id': user_id
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Something went wrong. Please try again.'}), 500


@chat_bp.route('/api/chat/history')
@login_required
def get_chat_history():
    """获取用户的聊天历史"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = memory_manager.get_user_history(current_user.id, limit)
        
        return jsonify({
            'history': history,
            'total': len(history)
        })
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return jsonify({'history': [], 'total': 0})

@chat_bp.route('/api/chat/clear', methods=['POST'])
@login_required
def clear_chat_history():
    """清空用户的聊天历史"""
    try:
        success = memory_manager.clear_user_memory(current_user.id)
        
        if success:
            # 同时清空用户的对话链缓存
            if current_user.id in user_chains:
                del user_chains[current_user.id]
            
            return jsonify({
                'message': 'Chat history cleared successfully',
                'user_id': current_user.id
            })
        else:
            return jsonify({'error': 'Failed to clear chat history'}), 500
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return jsonify({'error': 'Failed to clear chat history'}), 500


@chat_bp.route('/api/chat/status', methods=['GET'])
@login_required
def get_chat_status():
    """获取聊天状态信息"""
    try:
        user_id = str(current_user.id)
        
        # 检查用户是否有活跃的对话链
        has_active_chain = user_id in user_chains
        
        # 获取对话历史摘要
        recent_messages = MemoryManager.get_conversation_summary(user_id, 3)
        
        return jsonify({
            'user_id': user_id,
            'has_active_chain': has_active_chain,
            'recent_messages_count': len(recent_messages),
            'recent_messages': recent_messages
        })
        
    except Exception as e:
        print(f"Error getting chat status: {e}")
        return jsonify({'error': 'Failed to get chat status'}), 500