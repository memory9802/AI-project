"""
評分權重推薦系統 - 核心服務模組

功能:
1. 帶權重的商品推薦查詢
2. 評分提交與更新
3. 用戶評分記錄查詢
4. 商品統計資料查詢
"""

from database import get_db_cursor
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# ===========================
# 1. 推薦查詢功能
# ===========================

def get_weighted_recommendations(
    user_id: int,
    item_source: str = 'items',
    limit: int = 20,
    exclude_rated: bool = True,
    min_rating: Optional[float] = None,
    category: Optional[str] = None
) -> List[Dict]:
    """
    取得帶權重的商品推薦列表
    
    Args:
        user_id: 用戶 ID
        item_source: 商品來源 ('items' 或 'user_wardrobe')
        limit: 返回數量限制
        exclude_rated: 是否排除已評分商品
        min_rating: 最低平均評分過濾
        category: 商品類別過濾
    
    Returns:
        商品列表 (包含權重分數)
    """
    try:
        with get_db_cursor() as cursor:
            # 根據來源選擇對應的視圖
            if item_source == 'items':
                view_name = 'v_items_with_ratings'
            else:
                view_name = 'v_wardrobe_with_ratings'
            
            # 視圖中的主鍵列都是 'id'
            id_column = 'id'
            
            # 基礎查詢
            query = f"""
                SELECT *
                FROM {view_name}
                WHERE 1=1
            """
            params = []
            
            # 排除已評分商品
            if exclude_rated:
                query += f"""
                    AND {id_column} NOT IN (
                        SELECT item_id 
                        FROM rating 
                        WHERE user_id = %s AND item_source = %s
                    )
                """
                params.extend([user_id, item_source])
            
            # 最低評分過濾
            if min_rating is not None:
                query += " AND avg_rating >= %s"
                params.append(min_rating)
            
            # 類別過濾 (僅適用於 items)
            if category and item_source == 'items':
                query += " AND productDisplayName LIKE %s"
                params.append(f"%{category}%")
            
            # 排序: 優先 final_score,其次 avg_rating
            query += """
                ORDER BY 
                    final_score DESC,
                    avg_rating DESC,
                    rating_count DESC
                LIMIT %s
            """
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            logger.info(f"找到 {len(results)} 件推薦商品 (來源: {item_source})")
            return results
            
    except Exception as e:
        logger.error(f"取得推薦商品失敗: {str(e)}")
        raise


def get_recommendations_comparison(
    user_id: int,
    item_source: str = 'items',
    limit: int = 10
) -> Dict[str, List[Dict]]:
    """
    比較無權重與有權重的推薦結果
    
    用於測試和展示權重系統的效果
    
    Returns:
        {
            'without_weight': [...],  # 無權重推薦
            'with_weight': [...]      # 有權重推薦
        }
    """
    try:
        with get_db_cursor() as cursor:
            # 無權重推薦 (純按平均分排序)
            if item_source == 'items':
                view_name = 'v_items_with_ratings'
            else:
                view_name = 'v_wardrobe_with_ratings'
            
            # 視圖中的主鍵列都是 'id'
            id_column = 'id'
            
            # 無權重查詢
            query_without = f"""
                SELECT *
                FROM {view_name}
                WHERE {id_column} NOT IN (
                    SELECT item_id 
                    FROM rating 
                    WHERE user_id = %s AND item_source = %s
                )
                ORDER BY avg_rating DESC, rating_count DESC
                LIMIT %s
            """
            cursor.execute(query_without, [user_id, item_source, limit])
            without_weight = cursor.fetchall()
            
            # 有權重查詢
            query_with = f"""
                SELECT *
                FROM {view_name}
                WHERE {id_column} NOT IN (
                    SELECT item_id 
                    FROM rating 
                    WHERE user_id = %s AND item_source = %s
                )
                ORDER BY final_score DESC, avg_rating DESC
                LIMIT %s
            """
            cursor.execute(query_with, [user_id, item_source, limit])
            with_weight = cursor.fetchall()
            
            return {
                'without_weight': without_weight,
                'with_weight': with_weight
            }
            
    except Exception as e:
        logger.error(f"推薦比較失敗: {str(e)}")
        raise


# ===========================
# 2. 評分提交功能
# ===========================

def submit_rating(
    user_id: int,
    item_id: int,
    item_source: str,
    rating_value: int,
    review_text: Optional[str] = None
) -> Tuple[bool, str]:
    """
    提交或更新評分
    
    Args:
        user_id: 用戶 ID
        item_id: 商品 ID
        item_source: 商品來源 ('items' 或 'user_wardrobe')
        rating_value: 評分值 (1-5)
        review_text: 評論文字 (可選)
    
    Returns:
        (成功與否, 訊息)
    """
    # 驗證評分值
    if not 1 <= rating_value <= 5:
        return False, "評分必須在 1-5 之間"
    
    # 驗證 item_source
    if item_source not in ('items', 'user_wardrobe'):
        return False, "item_source 必須是 'items' 或 'user_wardrobe'"
    
    try:
        with get_db_cursor() as cursor:
            # 檢查商品是否存在
            if item_source == 'items':
                cursor.execute("SELECT id FROM items WHERE id = %s", [item_id])
            else:
                cursor.execute("SELECT id FROM user_wardrobe WHERE id = %s", [item_id])
            
            if not cursor.fetchone():
                return False, f"商品不存在 (ID: {item_id}, 來源: {item_source})"
            
            # 使用 INSERT ... ON DUPLICATE KEY UPDATE
            query = """
                INSERT INTO rating (user_id, item_source, item_id, rating_value, review_text)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    rating_value = VALUES(rating_value),
                    review_text = VALUES(review_text),
                    updated_at = CURRENT_TIMESTAMP
            """
            cursor.execute(query, [user_id, item_source, item_id, rating_value, review_text])
            
            logger.info(f"評分提交成功: user={user_id}, item={item_id}, source={item_source}, rating={rating_value}")
            return True, "評分提交成功"
            
    except Exception as e:
        logger.error(f"評分提交失敗: {str(e)}")
        return False, f"評分提交失敗: {str(e)}"


def delete_rating(user_id: int, item_id: int, item_source: str) -> Tuple[bool, str]:
    """
    刪除評分
    
    Args:
        user_id: 用戶 ID
        item_id: 商品 ID
        item_source: 商品來源
    
    Returns:
        (成功與否, 訊息)
    """
    try:
        with get_db_cursor() as cursor:
            query = """
                DELETE FROM rating
                WHERE user_id = %s AND item_id = %s AND item_source = %s
            """
            cursor.execute(query, [user_id, item_id, item_source])
            
            if cursor.rowcount > 0:
                logger.info(f"評分刪除成功: user={user_id}, item={item_id}, source={item_source}")
                return True, "評分刪除成功"
            else:
                return False, "找不到該評分記錄"
                
    except Exception as e:
        logger.error(f"評分刪除失敗: {str(e)}")
        return False, f"評分刪除失敗: {str(e)}"


# ===========================
# 3. 用戶評分查詢
# ===========================

def get_user_ratings(
    user_id: int,
    item_source: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """
    取得用戶的評分記錄
    
    Args:
        user_id: 用戶 ID
        item_source: 商品來源過濾 (可選)
        limit: 返回數量限制
    
    Returns:
        評分記錄列表
    """
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT 
                    r.id,
                    r.user_id,
                    r.item_source,
                    r.item_id,
                    r.rating_value,
                    r.review_text,
                    r.created_at,
                    r.updated_at
                FROM rating r
                WHERE r.user_id = %s
            """
            params = [user_id]
            
            if item_source:
                query += " AND r.item_source = %s"
                params.append(item_source)
            
            query += " ORDER BY r.updated_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            logger.info(f"找到 {len(results)} 筆評分記錄 (user_id={user_id})")
            return results
            
    except Exception as e:
        logger.error(f"取得用戶評分失敗: {str(e)}")
        raise


def get_user_rating_summary(user_id: int) -> Dict:
    """
    取得用戶評分摘要統計
    
    Returns:
        {
            'total_ratings': 總評分數,
            'items_ratings': items 評分數,
            'wardrobe_ratings': user_wardrobe 評分數,
            'avg_rating': 平均評分,
            'rating_distribution': {1: 數量, 2: 數量, ...}
        }
    """
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT 
                    COUNT(*) as total_ratings,
                    SUM(CASE WHEN item_source = 'items' THEN 1 ELSE 0 END) as items_ratings,
                    SUM(CASE WHEN item_source = 'user_wardrobe' THEN 1 ELSE 0 END) as wardrobe_ratings,
                    AVG(rating_value) as avg_rating,
                    SUM(CASE WHEN rating_value = 1 THEN 1 ELSE 0 END) as rating_1,
                    SUM(CASE WHEN rating_value = 2 THEN 1 ELSE 0 END) as rating_2,
                    SUM(CASE WHEN rating_value = 3 THEN 1 ELSE 0 END) as rating_3,
                    SUM(CASE WHEN rating_value = 4 THEN 1 ELSE 0 END) as rating_4,
                    SUM(CASE WHEN rating_value = 5 THEN 1 ELSE 0 END) as rating_5
                FROM rating
                WHERE user_id = %s
            """
            cursor.execute(query, [user_id])
            result = cursor.fetchone()
            
            if result:
                return {
                    'total_ratings': result['total_ratings'],
                    'items_ratings': result['items_ratings'],
                    'wardrobe_ratings': result['wardrobe_ratings'],
                    'avg_rating': float(result['avg_rating']) if result['avg_rating'] else 0.0,
                    'rating_distribution': {
                        1: result['rating_1'],
                        2: result['rating_2'],
                        3: result['rating_3'],
                        4: result['rating_4'],
                        5: result['rating_5']
                    }
                }
            else:
                return {
                    'total_ratings': 0,
                    'items_ratings': 0,
                    'wardrobe_ratings': 0,
                    'avg_rating': 0.0,
                    'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                }
                
    except Exception as e:
        logger.error(f"取得用戶評分摘要失敗: {str(e)}")
        raise


# ===========================
# 4. 商品統計查詢
# ===========================

def get_item_stats(item_id: int, item_source: str) -> Optional[Dict]:
    """
    取得商品的評分統計資料
    
    Args:
        item_id: 商品 ID
        item_source: 商品來源
    
    Returns:
        統計資料 dict 或 None
    """
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT *
                FROM item_stats
                WHERE item_id = %s AND item_source = %s
            """
            cursor.execute(query, [item_id, item_source])
            result = cursor.fetchone()
            
            if result:
                logger.info(f"取得商品統計: item={item_id}, source={item_source}")
            
            return result
            
    except Exception as e:
        logger.error(f"取得商品統計失敗: {str(e)}")
        raise


def get_top_rated_items(
    item_source: str = 'items',
    limit: int = 10,
    min_rating_count: int = 3
) -> List[Dict]:
    """
    取得高評分商品列表
    
    Args:
        item_source: 商品來源
        limit: 返回數量
        min_rating_count: 最少評分次數 (避免評分過少的商品)
    
    Returns:
        高評分商品列表
    """
    try:
        with get_db_cursor() as cursor:
            if item_source == 'items':
                view_name = 'v_items_with_ratings'
            else:
                view_name = 'v_wardrobe_with_ratings'
            
            query = f"""
                SELECT *
                FROM {view_name}
                WHERE rating_count >= %s
                ORDER BY avg_rating DESC, rating_count DESC
                LIMIT %s
            """
            cursor.execute(query, [min_rating_count, limit])
            results = cursor.fetchall()
            
            logger.info(f"找到 {len(results)} 件高評分商品")
            return results
            
    except Exception as e:
        logger.error(f"取得高評分商品失敗: {str(e)}")
        raise


# ===========================
# 5. 輔助函數
# ===========================

def check_user_rated(user_id: int, item_id: int, item_source: str) -> Optional[Dict]:
    """
    檢查用戶是否已評分該商品
    
    Returns:
        評分記錄 dict 或 None
    """
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT *
                FROM rating
                WHERE user_id = %s AND item_id = %s AND item_source = %s
            """
            cursor.execute(query, [user_id, item_id, item_source])
            return cursor.fetchone()
            
    except Exception as e:
        logger.error(f"檢查評分狀態失敗: {str(e)}")
        raise


def get_rating_statistics() -> Dict:
    """
    取得全站評分統計
    
    Returns:
        全站統計資料
    """
    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT 
                    COUNT(*) as total_ratings,
                    COUNT(DISTINCT user_id) as total_users,
                    COUNT(DISTINCT CONCAT(item_source, '-', item_id)) as total_items,
                    AVG(rating_value) as avg_rating,
                    SUM(CASE WHEN item_source = 'items' THEN 1 ELSE 0 END) as items_count,
                    SUM(CASE WHEN item_source = 'user_wardrobe' THEN 1 ELSE 0 END) as wardrobe_count
                FROM rating
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            return {
                'total_ratings': result['total_ratings'],
                'total_users': result['total_users'],
                'total_items': result['total_items'],
                'avg_rating': float(result['avg_rating']) if result['avg_rating'] else 0.0,
                'items_count': result['items_count'],
                'wardrobe_count': result['wardrobe_count']
            }
            
    except Exception as e:
        logger.error(f"取得全站統計失敗: {str(e)}")
        raise
