"""
資料處理與合併 - 整合版
合併 Gemini 驗證結果、產生最終資料集、對比分析

輸入: 
  - init/uniqlo_175_colored.csv (原始資料+顏色辨識)
  - init/gemini_verification_complete.csv (Gemini驗證結果)
  
輸出:
  - init/gemini_results_only.csv (只有Gemini結果)
  - init/gemini_comparison.csv (對比原始vs Gemini)
  - init/final_dataset.csv (最終資料集)
"""

import pandas as pd
import numpy as np


def merge_gemini_results(original_csv: str, gemini_csv: str) -> pd.DataFrame:
    """
    合併原始資料和 Gemini 驗證結果
    
    Args:
        original_csv: 原始資料CSV
        gemini_csv: Gemini驗證結果CSV
        
    Returns:
        合併後的 DataFrame
    """
    df_original = pd.read_csv(original_csv)
    df_gemini = pd.read_csv(gemini_csv)
    
    # 確保兩個檔案的 SKU 對齊
    df_merged = df_original.merge(
        df_gemini[['sku', 'Gemini gender', 'Gemini category', 'Gemini clothing_type', 'Gemini length', 'Gemini color']],
        on='sku',
        how='left'
    )
    
    return df_merged


def create_gemini_only_dataset(df: pd.DataFrame, output_csv: str):
    """
    創建只包含 Gemini 結果的資料集
    
    Args:
        df: 合併後的 DataFrame
        output_csv: 輸出檔案路徑
    """
    gemini_df = df[['sku', 'name', 'Gemini gender', 'Gemini category', 
                     'Gemini clothing_type', 'Gemini length', 'Gemini color', 
                     'image_url']].copy()
    
    # 如果有 price，也加入
    if 'price' in df.columns:
        gemini_df['price'] = df['price']
    
    gemini_df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"✅ Gemini only 資料集已儲存: {output_csv}")
    print(f"   欄位: {', '.join(gemini_df.columns)}")
    print(f"   筆數: {len(gemini_df)}")


def create_comparison_dataset(df: pd.DataFrame, output_csv: str):
    """
    創建對比資料集（顯示差異）
    
    Args:
        df: 合併後的 DataFrame
        output_csv: 輸出檔案路徑
    """
    comparison_cols = ['sku', 'name']
    
    # 對比各欄位
    for col_base in ['gender', 'category', 'clothing_type', 'length', 'color']:
        if col_base in df.columns and f'Gemini {col_base}' in df.columns:
            comparison_cols.extend([col_base, f'Gemini {col_base}'])
            
            # 新增差異標記欄位
            diff_col = f'{col_base}_diff'
            df[diff_col] = df.apply(
                lambda row: '✓' if row[col_base] == row[f'Gemini {col_base}'] else '❌',
                axis=1
            )
            comparison_cols.append(diff_col)
    
    comparison_cols.append('image_url')
    
    comparison_df = df[comparison_cols].copy()
    comparison_df.to_csv(output_csv, index=False, encoding='utf-8')
    
    print(f"✅ 對比資料集已儲存: {output_csv}")
    print(f"   欄位: {', '.join(comparison_df.columns)}")


def generate_statistics(df: pd.DataFrame):
    """
    生成統計報告
    
    Args:
        df: 合併後的 DataFrame
    """
    print("\n" + "=" * 80)
    print("📊 驗證統計報告")
    print("=" * 80)
    
    total = len(df)
    print(f"\n總筆數: {total}")
    
    # 各欄位對比
    for col_base in ['gender', 'category', 'clothing_type', 'length', 'color']:
        col_gemini = f'Gemini {col_base}'
        
        if col_base not in df.columns or col_gemini not in df.columns:
            continue
        
        # 計算差異
        valid_rows = (df[col_gemini] != '-')
        differences = ((df[col_base] != df[col_gemini]) & valid_rows).sum()
        valid_count = valid_rows.sum()
        
        accuracy = (1 - differences / valid_count) * 100 if valid_count > 0 else 0
        
        print(f"\n{col_base}:")
        print(f"  有效筆數: {valid_count}")
        print(f"  差異筆數: {differences}")
        print(f"  準確率: {accuracy:.1f}%")
        
        # 顯示前5個不同的案例
        if differences > 0:
            diff_samples = df[((df[col_base] != df[col_gemini]) & valid_rows)][
                ['name', col_base, col_gemini]
            ].head(5)
            print(f"\n  差異範例:")
            for idx, row in diff_samples.iterrows():
                print(f"    - {row['name'][:30]}")
                print(f"      原始: {row[col_base]} | Gemini: {row[col_gemini]}")


def create_final_dataset(df: pd.DataFrame, output_csv: str, strategy: str = 'gemini'):
    """
    創建最終資料集
    
    Args:
        df: 合併後的 DataFrame
        output_csv: 輸出檔案路徑
        strategy: 選擇策略
            - 'gemini': 優先使用 Gemini 結果
            - 'original': 優先使用原始資料
            - 'hybrid': 混合策略（clothing_type用Gemini，color用原始）
    """
    final_df = df.copy()
    
    if strategy == 'gemini':
        # 使用 Gemini 結果覆蓋原始資料
        for col_base in ['gender', 'category', 'clothing_type', 'length', 'color']:
            col_gemini = f'Gemini {col_base}'
            if col_gemini in final_df.columns:
                final_df[col_base] = final_df[col_gemini].replace('-', final_df[col_base])
    
    elif strategy == 'hybrid':
        # 混合策略: clothing_type, gender, length 用 Gemini (準確率高)
        #          color 用原始 (Pantone格式)
        for col_base in ['gender', 'clothing_type', 'length']:
            col_gemini = f'Gemini {col_base}'
            if col_gemini in final_df.columns:
                final_df[col_base] = final_df[col_gemini].replace('-', final_df[col_base])
    
    # 保留最終需要的欄位
    final_cols = ['sku', 'name', 'gender', 'category', 'clothing_type', 'length', 'color', 'price', 'image_url']
    final_cols = [col for col in final_cols if col in final_df.columns]
    
    final_df = final_df[final_cols]
    final_df.to_csv(output_csv, index=False, encoding='utf-8')
    
    print(f"\n✅ 最終資料集已儲存: {output_csv}")
    print(f"   策略: {strategy}")
    print(f"   欄位: {', '.join(final_df.columns)}")
    print(f"   筆數: {len(final_df)}")


def main():
    """主程式流程"""
    print("=" * 80)
    print("🔄 資料處理與合併")
    print("=" * 80)
    
    # 1. 合併資料
    print("\n步驟 1: 合併原始資料與 Gemini 驗證結果")
    df_merged = merge_gemini_results(
        original_csv='init/uniqlo_175_colored.csv',
        gemini_csv='init/gemini_verification_complete.csv'
    )
    print(f"✅ 合併完成，共 {len(df_merged)} 筆")
    
    # 2. 創建 Gemini only 資料集
    print("\n步驟 2: 創建 Gemini 專屬資料集")
    create_gemini_only_dataset(df_merged, 'init/gemini_results_only.csv')
    
    # 3. 創建對比資料集
    print("\n步驟 3: 創建對比資料集")
    create_comparison_dataset(df_merged, 'init/gemini_comparison.csv')
    
    # 4. 生成統計報告
    print("\n步驟 4: 生成統計報告")
    generate_statistics(df_merged)
    
    # 5. 創建最終資料集 (混合策略)
    print("\n步驟 5: 創建最終資料集")
    create_final_dataset(df_merged, 'init/final_dataset.csv', strategy='hybrid')
    
    print("\n" + "=" * 80)
    print("✅ 所有處理完成")
    print("=" * 80)
    print("\n產出檔案:")
    print("  1. init/gemini_results_only.csv - Gemini驗證結果")
    print("  2. init/gemini_comparison.csv - 對比分析")
    print("  3. init/final_dataset.csv - 最終資料集")


if __name__ == '__main__':
    main()
