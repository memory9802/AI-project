#!/usr/bin/env python3
"""測試 Gemini API Key 是否有效"""

import os
import requests

# 從 .env 讀取 API Key
def read_env():
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

env = read_env()
API_KEY = env.get('LLM_API_KEY')

print(f"🔑 測試 API Key: {API_KEY[:10]}...{API_KEY[-10:]}")
print()

# 測試多個模型版本
models = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
]

for model in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "你好,請用繁體中文回答:1+1等於多少?"
            }]
        }]
    }
    
    print(f"📡 測試模型: {model}")
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"   ✅ 成功! 回應: {text[:50]}...")
            print(f"   👍 建議使用此模型: {model}")
            break
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', '未知錯誤')
            print(f"   ❌ 失敗 ({response.status_code}): {error_msg}")
            
    except Exception as e:
        print(f"   ❌ 異常: {str(e)}")
    
    print()

print("\n" + "="*60)
print("💡 解決方案:")
print("1. 到 https://aistudio.google.com/app/apikey 檢查 API Key 狀態")
print("2. 確認 API Key 已啟用")
print("3. 檢查配額使用情況: https://ai.dev/usage")
print("4. 如果免費配額用完,需要等待重置或升級方案")
