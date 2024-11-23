import os
import json
import sqlite3
from datetime import datetime
from PIL import Image
import shutil

class ArtworkImporter:
    def __init__(self, db_path='artwork_database.db'):
        self.db_path = db_path
        self.raw_images_dir = 'data/raw_images'
        self.processed_images_dir = 'data/processed_images'
        
        # 确保必要的目录存在
        for directory in [self.raw_images_dir, self.processed_images_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def connect_db(self):
        return sqlite3.connect(self.db_path)
    
    def validate_image(self, image_path):
        """验证图片文件"""
        try:
            with Image.open(image_path) as img:
                # 获取图片信息
                width, height = img.size
                format = img.format
                return True, f"{width}x{height}", format
        except Exception as e:
            return False, str(e), None
    
    def import_child_data(self, child_data):
        """导入儿童信息"""
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO children (age, gender, location, education_setting)
                VALUES (?, ?, ?, ?)
            ''', (
                child_data['age'],
                child_data['gender'],
                child_data['location'],
                child_data['education_setting']
            ))
            child_id = cursor.lastrowid
            conn.commit()
            return child_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def import_artwork(self, artwork_data, image_path):
        """导入艺术作品"""
        # 验证图片
        is_valid, dimensions, format = self.validate_image(image_path)
        if not is_valid:
            raise ValueError(f"Invalid image: {dimensions}")
        
        # 生成新的文件名和路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"artwork_{timestamp}.{format.lower()}"
        new_image_path = os.path.join(self.processed_images_dir, new_filename)
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(new_image_path), exist_ok=True)
            
            # 复制图片到processed目录
            shutil.copy2(image_path, new_image_path)
            
            # 插入作品数据
            cursor.execute('''
                INSERT INTO artworks (
                    child_id, creation_date, image_path, dimensions,
                    medium, artwork_theme, creation_setting, emotional_state
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                artwork_data['child_id'],
                artwork_data['creation_date'],
                new_image_path,
                dimensions,
                artwork_data['medium'],
                artwork_data['artwork_theme'],
                artwork_data['creation_setting'],
                artwork_data['emotional_state']
            ))
            
            artwork_id = cursor.lastrowid
            conn.commit()
            return artwork_id
            
        except Exception as e:
            conn.rollback()
            if os.path.exists(new_image_path):
                os.remove(new_image_path)
            raise e
        finally:
            conn.close()

    def import_complete_record(self, child_data, artwork_data, image_path):
        """导入完整记录（包括儿童信息和作品）"""
        try:
            # 导入儿童信息
            child_id = self.import_child_data(child_data)
            
            # 添加child_id到artwork数据
            artwork_data['child_id'] = child_id
            
            # 导入作品信息
            artwork_id = self.import_artwork(artwork_data, image_path)
            
            return {
                'success': True,
                'child_id': child_id,
                'artwork_id': artwork_id,
                'message': '数据导入成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '数据导入失败'
            } 

    def get_all_artworks(self, filters=None):
        """获取所有作品数据"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    a.artwork_id,
                    a.image_path,
                    a.creation_date,
                    a.medium,
                    a.artwork_theme,
                    a.emotional_state,
                    c.age,
                    c.gender,
                    c.location,
                    c.education_setting
                FROM artworks a
                JOIN children c ON a.child_id = c.child_id
            '''
            
            if filters:
                # TODO: 添加过滤条件
                pass
            
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        
        except Exception as e:
            print(f"Error fetching artworks: {e}")
            return []
        finally:
            conn.close()