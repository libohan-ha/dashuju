from data_importer import ArtworkImporter

# 创建导入器实例
importer = ArtworkImporter()

# 准备儿童数据
child_data = {
    'age': 5,
    'gender': '女',
    'location': '北京',
    'education_setting': '公立幼儿园'
}

# 准备作品数据
artwork_data = {
    'creation_date': '2024-03-21',
    'medium': '水彩',
    'artwork_theme': '家庭',
    'creation_setting': '课堂',
    'emotional_state': '开心'
}

# 导入数据
result = importer.import_complete_record(
    child_data,
    artwork_data,
    'path/to/your/image.jpg'
)

print(result) 