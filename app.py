from flask import Flask, request, jsonify
import requests
import random
import os
import time

app = Flask(__name__)

# 你的Gemini API密钥（10个）
API_KEYS = [
    "AIzaSyCHeiybyzsycc4E4w4updI_vyIs2sWjfvU",
    "AIzaSyBVmvlMmMjBL6KBLBUSGSGv5Nr5i-cNGCI",
    "AIzaSyAo1QC_AjP0ar3EUH9fNATdaFt0TSYCqJo",
    "AIzaSyDYEuWwquFr34NpLJhRPM7burIaagKSJVE",
    "AIzaSyA0f3cvCTzEQGEJRJY8aWDdu4f1dB1b3rA",
    "AIzaSyAzDjrvFnesAz9SVXTjw9yFXMYEJ0NXBRs",
    "AIzaSyCM_HGmia2FglB0IY_c7ASsN5T0nPhQkD0",
    "AIzaSyCrVlImdVowrTTaSaFe0rIOL5Ppe7KSZXQ",
    "AIzaSyCU6ysWkiHDqu1iX7777SKxdxT18VRqZHA",
    "AIzaSyCYTL_W0swQ9pKVYdWf21DoxuZD4rzBMVw"
]

@app.route('/')
def home():
    return '''
    <h1>✅ Gemini代理（astrbot专用版）</h1>
    <p><strong>astrbot配置：</strong></p>
    <pre>
    API类型: OpenAI
    API地址: https://nyaa.zeabur.app/v1
    API密钥: sk-123456（随便填）
    模型: gemini-pro
    </pre>
    <p>或直接使用：</p>
    <pre>
    API地址: https://nyaa.zeabur.app/v1/chat/completions
    </pre>
    '''

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "Gemini Proxy for astrbot",
        "keys_count": len(API_KEYS)
    })

@app.route('/v1/chat/completions', methods=['POST'])
def openai_compatible():
    """OpenAI兼容接口 - astrbot使用这个"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "需要JSON数据"}), 400
        
        # 提取消息（OpenAI格式）
        messages = data.get('messages', [])
        prompt = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if content:
                prompt += f"{role}: {content}\n"
        
        # 如果没有messages，尝试其他字段
        if not prompt:
            prompt = data.get('prompt', '你好')
        
        # 随机选择Gemini API密钥
        api_key = random.choice(API_KEYS)
        
        # 调用Gemini API
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        params = {"key": api_key}
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # 发送请求到Gemini
        response = requests.post(url, params=params, json=payload, timeout=30)
        
        # 处理响应
        if response.status_code == 200:
            result = response.json()
            reply_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # 转换为OpenAI格式
            return jsonify({
                "id": f"chatcmpl-{random.randint(100000, 999999)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gemini-pro",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(prompt),
                    "completion_tokens": len(reply_text),
                    "total_tokens": len(prompt) + len(reply_text)
                }
            })
        else:
            return jsonify({
                "error": {
                    "message": f"Gemini API错误: {response.status_code}",
                    "type": "api_error",
                    "details": response.text[:200]
                }
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "internal_error"
            }
        }), 500

@app.route('/v1/models', methods=['GET'])
def list_models():
    """返回支持的模型列表（OpenAI兼容）"""
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": "gemini-pro",
                "object": "model",
                "created": 1686935000,
                "owned_by": "google"
            }
        ]
    })

# 保留旧接口（可选）
@app.route('/chat', methods=['POST'])
def simple_chat():
    """简单聊天接口（兼容旧版）"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '你好')
        
        # 重定向到OpenAI接口
        return openai_compatible()
    except:
        return jsonify({"error": "请使用/v1/chat/completions接口"}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
