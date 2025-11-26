import pandas as pd
import numpy as np
import requests
from PIL import Image
from io import BytesIO
from sklearn.cluster import KMeans
from collections import Counter
import time

# 擴充版顏色庫（33 種顏色）
colors = {
    "黑色": (0, 0, 0),
    "白色": (255, 255, 255),
    "深灰色": (85, 85, 85),
    "灰色": (128, 128, 128),
    "淺灰色": (192, 192, 192),
    "紅色": (255, 0, 0),
    "深紅色": (139, 0, 0),
    "粉紅色": (255, 192, 203),
    "淡粉色": (255, 228, 225),
    "橘色": (255, 165, 0),
    "黃色": (255, 255, 0),
    "金色": (255, 215, 0),
    "淺黃色": (255, 255, 224),
    "綠色": (0, 128, 0),
    "淺綠色": (144, 238, 144),
    "深綠色": (0, 100, 0),
    "軍綠色": (107, 142, 35),
    "藍色": (0, 0, 255),
    "淺藍色": (173, 216, 230),
    "深藍色": (0, 0, 139),
    "天藍色": (135, 206, 235),
    "牛仔藍": (0, 102, 204),
    "紫色": (128, 0, 128),
    "淺紫色": (221, 160, 221),
    "深紫色": (75, 0, 130),
    "咖啡色": (139, 69, 19),
    "褐色": (165, 42, 42),
    "米色": (245, 245, 220),
    "卡其色": (240, 230, 140),
    "橄欖色": (128, 128, 0),
    "青色": (0, 255, 255),
    "洋紅色": (255, 0, 255),
    "酒紅色": (128, 0, 32),
}

def get_closest_color(rgb):
    """找到最接近的顏色名稱"""
    min_dist = float('inf')
    closest_name = "未知"
    r, g, b = rgb
    
    for name, (cr, cg, cb) in colors.items():
        dist = np.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        if dist < min_dist:
            min_dist = dist
            closest_name = name
            
    return closest_name

def identify_color_from_url(url, max_retries=3):
    """
    改進版顏色辨識：降低白色/黑色的檢測閾值，更容易辨識淺色和深色衣服
    """
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=20, headers=headers)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content)).convert('RGB')
                img.thumbnail((200, 200))
                
                # 先檢查整體圖片
                data_full = np.array(img)
                pixels_full = data_full.reshape(-1, 3).astype(float)
                mean_rgb = np.mean(pixels_full, axis=0)
                std_rgb = np.std(pixels_full, axis=0)
                
                # 🔧 更嚴格的白色檢測：提高到 230（只檢測真正純白）
                # 標準差降到 35（顏色變化要非常小）
                if np.mean(mean_rgb) > 230 and np.mean(std_rgb) < 35:
                    # 再確認：至少 70% 的像素亮度 > 220
                    bright_count = np.sum(np.mean(pixels_full, axis=1) > 220)
                    if bright_count / len(pixels_full) > 0.70:
                        return "白色"
                
                # 🔧 調整黑色檢測：降到 55（比原本更嚴格）
                if np.mean(mean_rgb) < 55 and np.mean(std_rgb) < 30:
                    # 再確認：至少 70% 的像素亮度 < 65
                    dark_count = np.sum(np.mean(pixels_full, axis=1) < 65)
                    if dark_count / len(pixels_full) > 0.70:
                        return "黑色"
                
                # 裁切中心區域
                w, h = img.size
                left, top = w * 0.25, h * 0.25
                right, bottom = w * 0.75, h * 0.75
                img_crop = img.crop((left, top, right, bottom))
                
                data = np.array(img_crop)
                pixels = data.reshape(-1, 3).astype(float)
                
                # 極簡背景過濾：只過濾「極度」白和「極度」黑
                very_white_mask = (pixels[:, 0] > 250) & (pixels[:, 1] > 250) & (pixels[:, 2] > 250)
                very_white_mask &= (np.max(pixels, axis=1) - np.min(pixels, axis=1) < 10)
                
                very_black_mask = (pixels[:, 0] < 10) & (pixels[:, 1] < 10) & (pixels[:, 2] < 10)
                
                valid_mask = ~(very_white_mask | very_black_mask)
                object_pixels = pixels[valid_mask]
                
                if len(object_pixels) < 50:
                    object_pixels = pixels
                
                # 過濾後再次檢查
                avg_filtered = np.mean(object_pixels, axis=0)
                std_filtered = np.std(object_pixels, axis=0)
                
                # 🔧 更嚴格的白色檢測：> 220
                if np.mean(avg_filtered) > 220 and np.mean(std_filtered) < 40:
                    return "白色"
                
                # 🔧 更嚴格的黑色檢測：< 45
                if np.mean(avg_filtered) < 45 and np.mean(std_filtered) < 30:
                    return "黑色"
                
                # K-means 聚類
                n_clusters = min(3, len(object_pixels))
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                kmeans.fit(object_pixels)
                
                labels = kmeans.labels_
                label_counts = Counter(labels)
                
                # 找出最主要的顏色
                dominant_cluster = label_counts.most_common(1)[0][0]
                dominant_color = kmeans.cluster_centers_[dominant_cluster]
                
                # 🔧 最後檢查：更嚴格的閾值
                if np.mean(dominant_color) > 220:
                    return "白色"
                if np.mean(dominant_color) < 50:
                    return "黑色"
                
                color_name = get_closest_color(dominant_color)
                
                # Debug 輸出
                top_2_colors = label_counts.most_common(2)
                color_info = []
                for cluster_id, count in top_2_colors:
                    rgb = kmeans.cluster_centers_[cluster_id]
                    name = get_closest_color(rgb)
                    percent = (count / len(labels)) * 100
                    color_info.append(f"{name}({percent:.0f}%)")
                print(f"  顏色分析: {' + '.join(color_info)}")
                
                return color_name
            else:
                if attempt < max_retries - 1:
                    print(f"  ⚠️  下載失敗，重試中...")
                    time.sleep(2)
                    continue
                else:
                    print(f"  ❌ 無法下載圖片")
                    return "下載失敗"
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️  錯誤: {e}，重試中...")
                time.sleep(2)
                continue
            else:
                print(f"  ❌ 處理失敗: {e}")
                return "處理失敗"
    
    return "未指定"

# 主程式
if __name__ == "__main__":
    csv_path = 'init/uniqlo_175.csv'
    output_path = 'init/uniqlo_175_colored.csv'
    
    print("開始辨識顏色，共 230 件商品...")
    print("=" * 55)
    
    df = pd.read_csv(csv_path)
    total = len(df)
    
    # 載入已有的進度（如果存在）
    try:
        df_existing = pd.read_csv(output_path)
        # 確保 color 欄位存在
        if 'color' in df_existing.columns:
            df['color'] = df_existing['color']
            print(f"📂 載入已有進度，繼續處理...")
        else:
            df['color'] = '未指定'
    except FileNotFoundError:
        df['color'] = '未指定'
    
    # 逐一處理每件商品
    for idx, row in df.iterrows():
        # 如果已經有顏色且不是「未指定」，跳過
        if pd.notna(row.get('color')) and row['color'] not in ['未指定', '下載失敗', '處理失敗']:
            continue
        
        print(f"[{idx+1}/{total}] {row['name']}")
        
        # 辨識顏色
        color = identify_color_from_url(row['image_url'])
        df.at[idx, 'color'] = color
        print(f"  ✅ 辨識結果: {color}\n")
        
        # 每 25 筆存檔一次
        if (idx + 1) % 25 == 0:
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"💾 已儲存前 {idx+1} 件的進度")
    
    # 最終存檔
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print("=" * 55)
    print(f"✅ 完成！結果已儲存至 {output_path}")
    print(f"總共處理: {total} 件商品\n")
    
    # 統計結果
    print("顏色統計：")
    print(df['color'].value_counts())
    print(f"\n辨識到 {df['color'].nunique()} 種不同顏色\n")
    
    # 顯示前 10 筆
    print("前 10 筆結果預覽：")
    print(df[['name', 'color']].head(10))
