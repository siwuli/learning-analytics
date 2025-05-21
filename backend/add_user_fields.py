"""
添加avatar和bio字段到用户表
"""
import sqlite3
import os

def add_columns():
    """添加avatar和bio字段到用户表"""
    # 获取数据库路径
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'learning_analytics.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 添加avatar字段
        if 'avatar' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar TEXT")
            print("已添加avatar字段")
        else:
            print("avatar字段已存在")
        
        # 添加bio字段
        if 'bio' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
            print("已添加bio字段")
        else:
            print("bio字段已存在")
        
        # 提交更改
        conn.commit()
        
        print("字段添加完成")
        return True
    except Exception as e:
        print(f"添加字段时出错: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    add_columns() 