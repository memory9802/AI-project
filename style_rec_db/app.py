# ~/Desktop/stylerec/app.py (最終版本 /recommend_test 路由)

from flask import Flask, request, jsonify
from data_processor import get_clothing_summary_for_llm, fetch_images_by_ids, TEST_USER_ID # 匯入新的函數
from llm_service import call_llm_api, parse_outfit_ids 
# ... 其他程式碼省略 ...

@app.route('/recommend_test', methods=['GET'])
def recommend_test():
    """
    完整的穿搭推薦流程：數據擷取 -> LLM 呼叫 -> ID 解析 -> 圖片路徑回傳
    """
    # 1. 接收用戶輸入
    user_occasion = request.args.get('occasion', '休閒逛街')
    user_temp = request.args.get('temp', '25度')
    
    # 2. 數據擷取與提示生成
    llm_prompt, _ = get_clothing_summary_for_llm(
        user_id=TEST_USER_ID, 
        current_occasion=user_occasion, 
        current_temp_range=user_temp
    )
    # ... 錯誤檢查省略 ...

    # 3. 呼叫 LLM API
    llm_response_text = call_llm_api(llm_prompt)
    
    # 4. 解析 LLM 回覆，提取推薦的 ID (e.g., [[2002, 2008, 2010], [2001, 2003, 2004]])
    outfit_ids_list = parse_outfit_ids(llm_response_text)
    
    if not outfit_ids_list:
         return jsonify({"status": "error", "message": "LLM 未能解析出推薦 ID。"}), 500

    # 5. 最終步驟：根據 ID 清單，獲取圖片路徑和詳細資訊
    final_recommendations = []
    
    for single_outfit_ids in outfit_ids_list:
        # 獲取單套穿搭中所有單品的細節
        item_details = fetch_images_by_ids(single_outfit_ids)
        
        final_recommendations.append({
            "outfit_items": item_details,
            "llm_advice": "請從原始 LLM 回覆中提取相應的搭配理由" # 這裡需要根據實際 LLM 回覆結構來解析
        })

    # 6. 回傳最終結果給前端 (Line Bot 或網頁)
    return jsonify({
        "status": "success",
        "input": {"occasion": user_occasion, "temp": user_temp},
        "llm_response": llm_response_text,
        "recommendations": final_recommendations,
    })

if __name__ == '__main__':
    app.run(debug=True)