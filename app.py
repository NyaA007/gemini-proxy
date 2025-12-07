from flask import Flask, request, jsonify
import requests
import random
import os

app = Flask(__name__)

# 你的API密钥（共10个，5个旧的 + 5个新的）
API_KEYS = [
    # 旧的5个密钥
    "AIzaSyCHeiybyzsycc4E4w4updI_vyIs2sWjfvU",
    "AIzaSyBVmvlMmMjBL6KBLBUSGSGv5Nr5i-cNGCI",
    "AIzaSyAo1QC_AjP0ar3EUH9fNATdaFt0TSYCqJo",
    "AIzaSyDYEuWwquFr34NpLJhRPM7burIaagKSJVE",
    "AIzaSyA0f3cvCTzEQGEJRJY8aWDdu4f1dB1b3rA",
    
    # 新的5个密钥
    "AIzaSyAzDjrvFnesAz9SVXTjw9yFXMYEJ0NXBRs",
    "AIzaSyCM_HGmia2FglB0IY_c7ASsN5T0nPhQkD0",
    "AIzaSyCrVlImdVowrTTaSaFe0rIOL5Ppe7KSZXQ",
    "AIzaSyCU6ysWkiHDqu1iX7777SKxdxT18VRqZHA",
    "AIzaSyCYTL_W0swQ9pKVYdWf21DoxuZD4rzBMVw"
]

@app.route('/')
def home():
    return '''
    <h1>✅ Gemini API 代理运行成功！</h1>
    <p>使用方法：</p>
    <ul>
        <li><strong>GET /</strong> - 本页面</li>
        <li><strong>POST /chat</strong> - 聊天接口</li>
        <li><strong>GET /health</strong> - 健康检查</li>
    </ul>
    <p>示例请求：</p>
    <pre>
curl -X POST https://你的网址.zeabur.app/chat \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "你好"}'
    </pre>
    '''

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "Gemini API Proxy",
        "keys_count": len(API_KEYS)
    })

@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "需要JSON数据"}), 400
        
        prompt = data.get('prompt', '你好')
        model = data.get('model', 'gemini-pro')
        
        # 随机选择一个API密钥
        api_key = random.choice(API_KEYS)
        
        # 构建Gemini API请求
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        params = {"key": api_key}
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # 添加可选参数
        if 'temperature' in data:
            payload['generationConfig'] = {'temperature': data['temperature']}
        
        # 发送请求
        response = requests.post(url, params=params, json=payload, timeout=30)
        
        # 检查响应
        if response.status_code == 200:
            return jsonify(response.json())
        elif response.status_code in [403, 429]:
            # 密钥可能被限制，可以在这里添加重试逻辑
            return jsonify({
                "error": "API限制",
                "message": "当前密钥可能达到限制，请稍后重试",
                "status_code": response.status_code
            }), 429
        else:
            return jsonify({
                "error": "API请求失败",
                "status_code": response.status_code,
                "message": response.text[:200]
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)