# ~/Desktop/stylerec/config.py

# --- MySQL 連線設定 ---
# 這是您在 docker-compose.yml 中設定的資訊
DB_HOST = 'localhost'
DB_PORT = 3306 
DB_USER = 'user'
# 將此密碼替換成您在 docker-compose.yml 中設定的實際密碼
DB_PASSWORD = 'password' 
DB_DATABASE = 'style_rec_db' 

# 其他 Flask 設定
SECRET_KEY = 'your_super_secret_key'