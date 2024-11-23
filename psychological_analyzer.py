import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

class PsychologicalAnalyzer:
    def __init__(self):
        # 心理特征映射字典
        self.personality_traits = {
            'artistic': {
                'indicators': ['色彩丰富', '构图创新', '细节表达'],
                'interests': ['艺术创作', '音乐表演', '手工制作'],
                'development': ['艺术潜能', '创造力', '审美能力']
            },
            'logical': {
                'indicators': ['规则排列', '对称构图', '色彩规整'],
                'interests': ['拼图游戏', '积木搭建', '数字游戏'],
                'development': ['逻辑思维', '空间认知', '规律理解']
            },
            'social': {
                'indicators': ['人物场景', '互动元素', '温暖色调'],
                'interests': ['角色扮演', '团队游戏', '故事创作'],
                'development': ['社交能力', '情感表达', '合作意识']
            },
            'explorative': {
                'indicators': ['新颖元素', '大胆用色', '实验性表达'],
                'interests': ['科学实验', '探索活动', '自然观察'],
                'development': ['探索精神', '创新思维', '学习兴趣']
            }
        }
        
        # 教育建议模板
        self.education_suggestions = {
            'artistic': [
                "建议参加美术兴趣班，培养艺术创作能力",
                "可以尝试多种艺术形式，如绘画、手工、音乐等",
                "鼓励自由创作，培养独特的艺术表达方式"
            ],
            'logical': [
                "可以通过积木、拼图等游戏培养逻辑思维",
                "引导观察生活中的规律和秩序",
                "参与数学、科学相关的活动"
            ],
            'social': [
                "鼓励参加集体创作活动",
                "通过艺术创作表达情感和想法",
                "创造更多与他人互动的机会"
            ],
            'explorative': [
                "支持尝试新的创作方式和材料",
                "鼓励大胆实验和创新",
                "结合科学探索活动进行创作"
            ]
        }
    
    def analyze_color_patterns(self, artwork_data):
        """分析色彩使用模式"""
        # 提取色彩特征
        colors = np.array([self._hex_to_rgb(color) for color, _ in artwork_data])
        
        # 标准化数据
        scaler = StandardScaler()
        colors_scaled = scaler.fit_transform(colors)
        
        # 聚类分析
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(colors_scaled)
        
        return clusters
    
    def extract_psychological_traits(self, color_patterns, artwork_metadata):
        """提取心理特征"""
        traits = {}
        
        # 分析色彩模式
        color_variety = len(set(color_patterns))
        color_harmony = self._calculate_color_harmony(color_patterns)
        
        # 分析创作特征
        creation_features = {
            'medium': artwork_metadata['medium'],
            'theme': artwork_metadata['artwork_theme'],
            'emotional_state': artwork_metadata['emotional_state']
        }
        
        # 匹配性格特征
        for trait_type, trait_info in self.personality_traits.items():
            score = self._calculate_trait_score(
                color_variety,
                color_harmony,
                creation_features,
                trait_info
            )
            traits[trait_type] = score
        
        return traits
    
    def generate_recommendations(self, psychological_traits):
        """生成教育建议"""
        recommendations = []
        
        # 找出最显著的特征
        dominant_traits = sorted(
            psychological_traits.items(),
            key=lambda x: x[1],
            reverse=True
        )[:2]
        
        for trait, score in dominant_traits:
            if score > 0.5:  # 设置阈值
                recommendations.extend(self.education_suggestions[trait])
        
        return recommendations
    
    def _hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB值"""
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    
    def _calculate_color_harmony(self, color_patterns):
        """计算色彩和谐度"""
        # TODO: 实现色彩和谐度计算
        return 0.5
    
    def _calculate_trait_score(self, color_variety, color_harmony, features, trait_info):
        """计算特征得分"""
        score = 0
        
        # 基于色彩多样性
        if color_variety >= 3:
            score += 0.3
        
        # 基于色彩和谐度
        score += color_harmony * 0.3
        
        # 基于创作特征
        if any(indicator.lower() in features['theme'].lower() 
               for indicator in trait_info['indicators']):
            score += 0.2
        
        # 基于情绪状态
        if features['emotional_state'] in ['开心', '兴奋']:
            score += 0.2
        
        return min(score, 1.0)  # 确保得分不超过1 