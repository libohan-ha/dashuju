import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objects as go
from functools import lru_cache
import io

class ColorAnalyzer:
    def __init__(self):
        self.color_psychology = {
            'red': {
                'emotions': ['热情', '兴奋', '活力'],
                'traits': ['外向', '自信', '积极']
            },
            'blue': {
                'emotions': ['平静', '安宁', '稳定'],
                'traits': ['内向', '理性', '深思']
            },
            'yellow': {
                'emotions': ['快乐', '愉悦', '温暖'],
                'traits': ['乐观', '创造力', '友好']
            },
            'green': {
                'emotions': ['自然', '和谐', '生机'],
                'traits': ['平衡', '成长', '希望']
            },
            'purple': {
                'emotions': ['神秘', '浪漫', '高贵'],
                'traits': ['想象力', '艺术性', '敏感']
            }
        }
        self._cache = {}
    
    def _preprocess_image(self, image_path, max_size=800):
        """预处理图片：调整大小和格式"""
        with Image.open(image_path) as img:
            # 调整图片大小以提高性能
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 转换为numpy数组
            img_array = np.array(img)
            return img_array
    
    @lru_cache(maxsize=32)
    def extract_dominant_colors(self, image_path, n_colors=5):
        """提取主要色彩（带缓存）"""
        # 检查缓存
        cache_key = f"{image_path}_{n_colors}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 预处理图片
        image = self._preprocess_image(image_path)
        pixels = image.reshape(-1, 3)
        
        # 使用KMeans聚类
        kmeans = KMeans(
            n_clusters=n_colors,
            random_state=42,
            n_init=3,  # 减少初始化次数以提高性能
            max_iter=100  # 限制最大迭代次数
        )
        kmeans.fit(pixels)
        
        # 获取主要色彩
        colors = kmeans.cluster_centers_
        
        # 计算每个颜色的比例
        labels = kmeans.labels_
        counts = np.bincount(labels)
        percentages = counts / len(labels)
        
        # 将RGB值转换为十六进制颜色代码
        hex_colors = ['#%02x%02x%02x' % tuple(map(int, color)) for color in colors]
        
        # 存入缓存
        result = list(zip(hex_colors, percentages))
        self._cache[cache_key] = result
        return result
    
    @lru_cache(maxsize=32)
    def analyze_color_distribution(self, image_path):
        """分析色彩分布（带缓存）"""
        # 预处理图片
        image = self._preprocess_image(image_path)
        
        # 转换为HSV空间
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # 计算分布
        h, s, v = cv2.split(hsv)
        
        # 归一化
        hues = h.flatten() * 2  # 转换为角度
        saturations = s.flatten() / 255 * 100  # 转换为百分比
        values = v.flatten() / 255 * 100  # 转换为百分比
        
        return {
            'hue_distribution': hues.tolist(),
            'saturation_distribution': saturations.tolist(),
            'value_distribution': values.tolist()
        }
    
    def analyze_color_psychology(self, dominant_colors):
        """分析色彩心理特征"""
        # 初始化特征字典
        emotion_weights = {}
        trait_weights = {}
        
        # 将输入转换为元组以确保一致性
        dominant_colors = tuple(dominant_colors)
        
        # 遍历每个主要色彩
        for color, percentage in dominant_colors:
            # 找到最接近的基础色彩
            base_color = self.find_nearest_base_color(color)
            if base_color in self.color_psychology:
                # 为每个情绪特征累加权重
                for emotion in self.color_psychology[base_color]['emotions']:
                    if emotion in emotion_weights:
                        emotion_weights[emotion] = max(emotion_weights[emotion], percentage)
                    else:
                        emotion_weights[emotion] = percentage
                
                # 为每个性格特征累加权重
                for trait in self.color_psychology[base_color]['traits']:
                    if trait in trait_weights:
                        trait_weights[trait] = max(trait_weights[trait], percentage)
                    else:
                        trait_weights[trait] = percentage
        
        # 转换为列表格式，并按权重排序
        emotions = sorted(
            [(emotion, weight) for emotion, weight in emotion_weights.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        traits = sorted(
            [(trait, weight) for trait, weight in trait_weights.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'emotions': emotions,
            'traits': traits
        }
    
    def generate_visualization(self, image_path):
        """生成可视化分析图表"""
        # 使用缓存的主要色彩数据
        dominant_colors = self.extract_dominant_colors(image_path)
        
        # 创建饼图
        colors, percentages = zip(*dominant_colors)
        fig = go.Figure(data=[go.Pie(
            labels=[f'Color {i+1}' for i in range(len(colors))],
            values=percentages,
            marker=dict(colors=colors),
            hole=.3
        )])
        
        fig.update_layout(
            title="主要色彩分布",
            showlegend=True,
            height=400  # 减小图表高度以提高加载速度
        )
        
        return fig
    
    @staticmethod
    def find_nearest_base_color(hex_color):
        """找到最接近的基础色彩（使用预计算的颜色距离）"""
        def hex_to_rgb(hex_str):
            hex_str = hex_str.lstrip('#')
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        
        def color_distance(c1, c2):
            """计算两个RGB颜色之间的欧氏距离"""
            r1, g1, b1 = c1
            r2, g2, b2 = c2
            return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
        
        # 基础色彩映射（使用预计算的RGB值）
        base_colors = {
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'green': (0, 255, 0),
            'purple': (128, 0, 128)
        }
        
        # 将输入颜色转换为RGB
        input_rgb = hex_to_rgb(hex_color)
        
        # 计算与每个基础色彩的距离
        distances = {
            color_name: color_distance(input_rgb, rgb_value)
            for color_name, rgb_value in base_colors.items()
        }
        
        # 返回距离最近的基础色彩
        return min(distances.items(), key=lambda x: x[1])[0]