# ~/Desktop/stylerec/app.py (部分程式碼)

from flask import Flask, render_template, request, jsonify
from data_processor import get_clothing_summary_for_llm, TEST_USER_ID
from config import SECRET_KEY # 匯入您的 SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
# ... 您的其他設定和路由 ...

# --- 測試路由：檢查資料庫連線與 LLM Prompt 生成 ---
# 這是為了讓您在瀏覽器或 Postman 中測試後端數據處理是否正確
@app.route('/recommend_test', methods=['GET'])
def recommend_test():
    """
    模擬使用者輸入，從資料庫抓取數據並產生 LLM 提示。
    """
    # 模擬從 Chatbot 介面獲取的用戶輸入
    user_occasion = request.args.get('occasion', '休閒逛街')
    user_temp = request.args.get('temp', '25度')
    
    # 課綱：自訂函數、模組與套件 (呼叫 data_processor 模組的函數)
    llm_prompt, json_data = get_clothing_summary_for_llm(
        user_id=TEST_USER_ID, 
        current_occasion=user_occasion, 
        current_temp_range=user_temp
    )
    
    # 回傳給前端或用於接下來的 LLM API 呼叫
    return jsonify({
        "status": "success",
        "user_id": TEST_USER_ID,
        "llm_prompt_text": llm_prompt,
        "clothing_list_json": json_data
    })

if __name__ == '__main__':
    app.run(debug=True)