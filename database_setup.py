import sqlite3
import os

def create_database():
    # 连接到数据库（如果不存在则创建）
    conn = sqlite3.connect('artwork_database.db')
    cursor = conn.cursor()
    
    # 创建儿童信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS children (
        child_id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER NOT NULL,
        gender TEXT,
        location TEXT,
        education_setting TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建艺术作品表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artworks (
        artwork_id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_id INTEGER,
        creation_date DATE,
        image_path TEXT NOT NULL,
        dimensions TEXT,
        medium TEXT,
        artwork_theme TEXT,
        creation_setting TEXT,
        emotional_state TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (child_id) REFERENCES children (child_id)
    )
    ''')
    
    # 创建色彩分析表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS color_analysis (
        analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artwork_id INTEGER,
        dominant_colors TEXT,  # JSON格式存储色彩数据
        color_distribution TEXT,  # JSON格式存储分布数据
        color_combinations TEXT,  # JSON格式存储搭配数据
        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (artwork_id) REFERENCES artworks (artwork_id)
    )
    ''')
    
    # 创建心理映射表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS psychological_mappings (
        mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artwork_id INTEGER,
        emotional_indicators TEXT,  # JSON格式存储情绪指标
        personality_traits TEXT,    # JSON格式存储性格特征
        analysis_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (artwork_id) REFERENCES artworks (artwork_id)
    )
    ''')
    
    conn.commit()
    conn.close()

def create_directory_structure():
    # 创建必要的目录结构
    directories = [
        'data/raw_images',
        'data/processed_images',
        'data/color_analysis'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    create_database()
    create_directory_structure()
    print("数据库和目录结构创建完成！") 