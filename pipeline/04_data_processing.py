"""
資料處理與合併 - 整合版
合併 Gemini 驗證結果、產生最終資料集、對比分析

<<<<<<< HEAD
輸入:
  - init/uniqlo_175_colored.csv (原始資料+顏色辨識)
  - init/gemini_verification_complete.csv (Gemini驗證結果)

=======
輸入: 
  - init/uniqlo_175_colored.csv (原始資料+顏色辨識)
  - init/gemini_verification_complete.csv (Gemini驗證結果)
  
>>>>>>> memory9802/blueprints-success
輸出:
  - init/gemini_results_only.csv (只有Gemini結果)
  - init/gemini_comparison.csv (對比原始vs Gemini)
  - init/final_dataset.csv (最終資料集)
"""

import pandas as pd
import numpy as np


<<<<<<< HEAD
# ==================== 資料清理函數 ====================
def drop_duplicates_smart(df: pd.DataFrame) -> pd.DataFrame:
    """
    智能去重：保留第一筆，或保留最完整的資料

    Args:
        df: 原始 DataFrame

    Returns:
        去重後的 DataFrame
    """
    print("\n🧹 執行智能去重...")
    original_count = len(df)

    # 方法1: 按 SKU 去重，保留第一筆
    df_dedup = df.drop_duplicates(subset=["sku"], keep="first")

    removed_count = original_count - len(df_dedup)

    if removed_count > 0:
        print(f"   移除 {removed_count} 筆重複資料")
        print(f"   保留 {len(df_dedup)} 筆獨立商品")

        # 顯示被移除的 SKU
        duplicate_skus = df[df.duplicated(subset=["sku"], keep="first")][
            "sku"
        ].unique()
        print(f"   重複 SKU: {', '.join(duplicate_skus[:5])}")
    else:
        print(f"   ✓ 無重複資料")

    return df_dedup


def auto_fill_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    自動填補 NULL 的 category
    根據 clothing_type 或商品名稱推斷

    Args:
        df: 原始 DataFrame

    Returns:
        填補後的 DataFrame
    """
    print("\n🔧 自動填補 NULL category...")

    # 統計 NULL 數量
    null_count_before = (
        df["category"].isna().sum()
        + (df["category"] == "-").sum()
        + (df["category"] == "").sum()
    )

    if null_count_before == 0:
        print(f"   ✓ 無需填補")
        return df

    print(f"   發現 {null_count_before} 筆 NULL category")

    def infer_category(row):
        """根據 clothing_type 或 name 推斷 category"""
        # 如果 category 已有值且有效，不修改
        if pd.notna(row.get("category")) and row["category"] not in ["", "-"]:
            return row["category"]

        # 優先使用 clothing_type
        clothing_type = str(row.get("clothing_type", ""))
        name = str(row.get("name", ""))

        # 上衣類
        if any(
            x in clothing_type for x in ["上衣", "T恤", "襯衫", "衛衣", "POLO"]
        ):
            return "top"
        if any(
            x in name
            for x in [
                "T恤",
                "上衣",
                "襯衫",
                "外套",
                "衛衣",
                "POLO",
                "圓領",
                "V領",
            ]
        ):
            return "top"

        # 下身類
        if any(x in clothing_type for x in ["下身", "褲", "裙"]):
            return "bottom"
        if any(
            x in name for x in ["褲", "裙", "牛仔", "休閒褲", "長褲", "短褲"]
        ):
            return "bottom"

        # 外套類
        if any(x in name for x in ["外套", "夾克", "大衣", "風衣"]):
            return "outer"

        # 無法推斷，使用預設值
        return "top"  # 預設為 top (大部分商品是上衣)

    # 應用填補邏輯
    df["category"] = df.apply(infer_category, axis=1)

    # 統計填補後的 NULL 數量
    null_count_after = (
        df["category"].isna().sum()
        + (df["category"] == "-").sum()
        + (df["category"] == "").sum()
    )
    filled_count = null_count_before - null_count_after

    print(f"   ✓ 成功填補 {filled_count} 筆")
    if null_count_after > 0:
        print(f"   ⚠️  仍有 {null_count_after} 筆無法填補")

    return df


def merge_gemini_results(original_csv: str, gemini_csv: str) -> pd.DataFrame:
    """
    合併原始資料和 Gemini 驗證結果

    Args:
        original_csv: 原始資料CSV
        gemini_csv: Gemini驗證結果CSV

=======
def merge_gemini_results(original_csv: str, gemini_csv: str) -> pd.DataFrame:
    """
    合併原始資料和 Gemini 驗證結果
    
    Args:
        original_csv: 原始資料CSV
        gemini_csv: Gemini驗證結果CSV
        
>>>>>>> memory9802/blueprints-success
    Returns:
        合併後的 DataFrame
    """
    df_original = pd.read_csv(original_csv)
    df_gemini = pd.read_csv(gemini_csv)
<<<<<<< HEAD

    # 確保兩個檔案的 SKU 對齊
    df_merged = df_original.merge(
        df_gemini[
            [
                "sku",
                "Gemini gender",
                "Gemini category",
                "Gemini clothing_type",
                "Gemini length",
                "Gemini color",
            ]
        ],
        on="sku",
        how="left",
    )

=======
    
    # 確保兩個檔案的 SKU 對齊
    df_merged = df_original.merge(
        df_gemini[['sku', 'Gemini gender', 'Gemini category', 'Gemini clothing_type', 'Gemini length', 'Gemini color']],
        on='sku',
        how='left'
    )
    
>>>>>>> memory9802/blueprints-success
    return df_merged


def create_gemini_only_dataset(df: pd.DataFrame, output_csv: str):
    """
    創建只包含 Gemini 結果的資料集
<<<<<<< HEAD

=======
    
>>>>>>> memory9802/blueprints-success
    Args:
        df: 合併後的 DataFrame
        output_csv: 輸出檔案路徑
    """
<<<<<<< HEAD
    gemini_df = df[
        [
            "sku",
            "name",
            "Gemini gender",
            "Gemini category",
            "Gemini clothing_type",
            "Gemini length",
            "Gemini color",
            "image_url",
        ]
    ].copy()

    # 如果有 price，也加入
    if "price" in df.columns:
        gemini_df["price"] = df["price"]

    gemini_df.to_csv(output_csv, index=False, encoding="utf-8")
=======
    gemini_df = df[['sku', 'name', 'Gemini gender', 'Gemini category', 
                     'Gemini clothing_type', 'Gemini length', 'Gemini color', 
                     'image_url']].copy()
    
    # 如果有 price，也加入
    if 'price' in df.columns:
        gemini_df['price'] = df['price']
    
    gemini_df.to_csv(output_csv, index=False, encoding='utf-8')
>>>>>>> memory9802/blueprints-success
    print(f"✅ Gemini only 資料集已儲存: {output_csv}")
    print(f"   欄位: {', '.join(gemini_df.columns)}")
    print(f"   筆數: {len(gemini_df)}")


def create_comparison_dataset(df: pd.DataFrame, output_csv: str):
    """
    創建對比資料集（顯示差異）
<<<<<<< HEAD

=======
    
>>>>>>> memory9802/blueprints-success
    Args:
        df: 合併後的 DataFrame
        output_csv: 輸出檔案路徑
    """
<<<<<<< HEAD
    comparison_cols = ["sku", "name"]

    # 對比各欄位
    for col_base in ["gender", "category", "clothing_type", "length", "color"]:
        if col_base in df.columns and f"Gemini {col_base}" in df.columns:
            comparison_cols.extend([col_base, f"Gemini {col_base}"])

            # 新增差異標記欄位
            diff_col = f"{col_base}_diff"
            df[diff_col] = df.apply(
                lambda row: (
                    "✓" if row[col_base] == row[f"Gemini {col_base}"] else "❌"
                ),
                axis=1,
            )
            comparison_cols.append(diff_col)

    comparison_cols.append("image_url")

    comparison_df = df[comparison_cols].copy()
    comparison_df.to_csv(output_csv, index=False, encoding="utf-8")

=======
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
    
>>>>>>> memory9802/blueprints-success
    print(f"✅ 對比資料集已儲存: {output_csv}")
    print(f"   欄位: {', '.join(comparison_df.columns)}")


def generate_statistics(df: pd.DataFrame):
    """
    生成統計報告
<<<<<<< HEAD

=======
    
>>>>>>> memory9802/blueprints-success
    Args:
        df: 合併後的 DataFrame
    """
    print("\n" + "=" * 80)
    print("📊 驗證統計報告")
    print("=" * 80)
<<<<<<< HEAD

    total = len(df)
    print(f"\n總筆數: {total}")

    # 各欄位對比
    for col_base in ["gender", "category", "clothing_type", "length", "color"]:
        col_gemini = f"Gemini {col_base}"

        if col_base not in df.columns or col_gemini not in df.columns:
            continue

        # 計算差異
        valid_rows = df[col_gemini] != "-"
        differences = ((df[col_base] != df[col_gemini]) & valid_rows).sum()
        valid_count = valid_rows.sum()

        accuracy = (
            (1 - differences / valid_count) * 100 if valid_count > 0 else 0
        )

=======
    
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
        
>>>>>>> memory9802/blueprints-success
        print(f"\n{col_base}:")
        print(f"  有效筆數: {valid_count}")
        print(f"  差異筆數: {differences}")
        print(f"  準確率: {accuracy:.1f}%")
<<<<<<< HEAD

        # 顯示前5個不同的案例
        if differences > 0:
            diff_samples = df[((df[col_base] != df[col_gemini]) & valid_rows)][
                ["name", col_base, col_gemini]
=======
        
        # 顯示前5個不同的案例
        if differences > 0:
            diff_samples = df[((df[col_base] != df[col_gemini]) & valid_rows)][
                ['name', col_base, col_gemini]
>>>>>>> memory9802/blueprints-success
            ].head(5)
            print(f"\n  差異範例:")
            for idx, row in diff_samples.iterrows():
                print(f"    - {row['name'][:30]}")
<<<<<<< HEAD
                print(
                    f"      原始: {row[col_base]} | Gemini: {row[col_gemini]}"
                )


def create_final_dataset(
    df: pd.DataFrame, output_csv: str, strategy: str = "gemini"
):
    """
    創建最終資料集

=======
                print(f"      原始: {row[col_base]} | Gemini: {row[col_gemini]}")


def create_final_dataset(df: pd.DataFrame, output_csv: str, strategy: str = 'gemini'):
    """
    創建最終資料集
    
>>>>>>> memory9802/blueprints-success
    Args:
        df: 合併後的 DataFrame
        output_csv: 輸出檔案路徑
        strategy: 選擇策略
            - 'gemini': 優先使用 Gemini 結果
            - 'original': 優先使用原始資料
            - 'hybrid': 混合策略（clothing_type用Gemini，color用原始）
    """
    final_df = df.copy()
<<<<<<< HEAD

    # 🔥 新增: 智能去重
    final_df = drop_duplicates_smart(final_df)

    # 🔥 新增: 自動填補 NULL category
    final_df = auto_fill_category(final_df)

    if strategy == "gemini":
        # 使用 Gemini 結果覆蓋原始資料
        for col_base in [
            "gender",
            "category",
            "clothing_type",
            "length",
            "color",
        ]:
            col_gemini = f"Gemini {col_base}"
            if col_gemini in final_df.columns:
                final_df[col_base] = final_df[col_gemini].replace(
                    "-", final_df[col_base]
                )

    elif strategy == "hybrid":
        # 混合策略: clothing_type, gender, length 用 Gemini (準確率高)
        #          color 用原始 (Pantone格式)
        for col_base in ["gender", "clothing_type", "length"]:
            col_gemini = f"Gemini {col_base}"
            if col_gemini in final_df.columns:
                final_df[col_base] = final_df[col_gemini].replace(
                    "-", final_df[col_base]
                )

    # 保留最終需要的欄位
    final_cols = [
        "sku",
        "name",
        "gender",
        "category",
        "clothing_type",
        "length",
        "color",
        "price",
        "image_url",
    ]
    final_cols = [col for col in final_cols if col in final_df.columns]

    final_df = final_df[final_cols]
    final_df.to_csv(output_csv, index=False, encoding="utf-8")

=======
    
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
    
>>>>>>> memory9802/blueprints-success
    print(f"\n✅ 最終資料集已儲存: {output_csv}")
    print(f"   策略: {strategy}")
    print(f"   欄位: {', '.join(final_df.columns)}")
    print(f"   筆數: {len(final_df)}")


def main():
    """主程式流程"""
    print("=" * 80)
    print("🔄 資料處理與合併")
    print("=" * 80)
<<<<<<< HEAD

    # 1. 合併資料
    print("\n步驟 1: 合併原始資料與 Gemini 驗證結果")
    df_merged = merge_gemini_results(
        original_csv="init/uniqlo_175_colored.csv",
        gemini_csv="init/gemini_verification_complete.csv",
    )
    print(f"✅ 合併完成，共 {len(df_merged)} 筆")

    # 2. 創建 Gemini only 資料集
    print("\n步驟 2: 創建 Gemini 專屬資料集")
    create_gemini_only_dataset(df_merged, "init/gemini_results_only.csv")

    # 3. 創建對比資料集
    print("\n步驟 3: 創建對比資料集")
    create_comparison_dataset(df_merged, "init/gemini_comparison.csv")

    # 4. 生成統計報告
    print("\n步驟 4: 生成統計報告")
    generate_statistics(df_merged)

    # 5. 創建最終資料集 (混合策略)
    print("\n步驟 5: 創建最終資料集")
    create_final_dataset(
        df_merged, "init/final_dataset.csv", strategy="hybrid"
    )

=======
    
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
    
>>>>>>> memory9802/blueprints-success
    print("\n" + "=" * 80)
    print("✅ 所有處理完成")
    print("=" * 80)
    print("\n產出檔案:")
    print("  1. init/gemini_results_only.csv - Gemini驗證結果")
    print("  2. init/gemini_comparison.csv - 對比分析")
    print("  3. init/final_dataset.csv - 最終資料集")


<<<<<<< HEAD
if __name__ == "__main__":
=======
if __name__ == '__main__':
>>>>>>> memory9802/blueprints-success
    main()
