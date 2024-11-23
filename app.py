import streamlit as st
import pandas as pd
from PIL import Image
import os
from datetime import datetime
from data_importer import ArtworkImporter
from color_analyzer import ColorAnalyzer
import plotly.express as px
import plotly.graph_objects as go
from psychological_analyzer import PsychologicalAnalyzer

class ArtworkAnalysisUI:
    def __init__(self):
        self.importer = ArtworkImporter()
        
    def setup_page(self):
        st.set_page_config(
            page_title="幼儿美术作品分析系统",
            page_icon="🎨",
            layout="wide"
        )
        st.title("幼儿美术作品色彩分析系统")
        
    def show_sidebar(self):
        st.sidebar.title("功能导航")
        return st.sidebar.radio(
            "选择功能:",
            ["数据录入", "作品查看", "数据分析", "心理映射", "统计报告"]
        )
        
    def data_input_page(self):
        st.header("数据录入")
        
        # 创建两列布局
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("儿童信息")
            child_data = {
                'age': st.number_input("年龄", min_value=2, max_value=7),
                'gender': st.selectbox("性别", ["男", "女"]),
                'location': st.text_input("地域"),
                'education_setting': st.selectbox(
                    "教育环境",
                    ["公立幼儿园", "私立幼儿园", "其他"]
                )
            }
        
        with col2:
            st.subheader("作品信息")
            artwork_data = {
                'creation_date': st.date_input("创作日期"),
                'medium': st.selectbox(
                    "创作媒介",
                    ["水彩", "蜡笔", "彩笔", "混合媒介", "其他"]
                ),
                'artwork_theme': st.text_input("作品主题"),
                'creation_setting': st.selectbox(
                    "创作环境",
                    ["课堂", "家庭", "其他"]
                ),
                'emotional_state': st.selectbox(
                    "创作时情绪",
                    ["开心", "平静", "兴奋", "其他"]
                )
            }
        
        st.subheader("上传作品图片")
        uploaded_file = st.file_uploader("选择图片文件", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            # 显预览图
            image = Image.open(uploaded_file)
            st.image(image, caption="作品预览", use_container_width=True)
            
            # 保存临时文件
            temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            image.save(temp_path)
            
            if st.button("提交数据"):
                try:
                    # 导入数据
                    result = self.importer.import_complete_record(
                        child_data,
                        artwork_data,
                        temp_path
                    )
                    
                    if result['success']:
                        st.success("数据导入成功！")
                        st.json(result)
                    else:
                        st.error(f"导入失败: {result['error']}")
                        
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    def view_artwork_page(self):
        st.header("作品浏览")
        
        # 创建过滤器
        with st.expander("筛选条件"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                age_range = st.slider("年龄范围", 2, 7, (2, 7))
                gender = st.multiselect("性别", ["男", "女"])
                
            with col2:
                medium = st.multiselect(
                    "创作媒介",
                    ["水彩", "蜡笔", "彩笔", "混合媒介", "其他"]
                )
                location = st.text_input("地域")
                
            with col3:
                date_range = st.date_input(
                    "创作日期范围",
                    value=[datetime.now().date(), datetime.now().date()]
                )
                education = st.multiselect(
                    "教育环境",
                    ["公立幼儿园", "私立幼儿园", "其他"]
                )
        
        # 获取作品数据
        artworks = self.importer.get_all_artworks()
        
        if not artworks:
            st.info("暂无作品数据")
            return
        
        # 显示作品网格
        cols = st.columns(3)
        for idx, artwork in enumerate(artworks):
            with cols[idx % 3]:
                try:
                    # 显示图片
                    if os.path.exists(artwork['image_path']):
                        image = Image.open(artwork['image_path'])
                        st.image(image, use_container_width=True)
                    else:
                        st.error("图片文件不存在")
                    
                    # 显示作品信息
                    with st.expander("作品详情"):
                        st.write(f"创作日期: {artwork['creation_date']}")
                        st.write(f"创作媒介: {artwork['medium']}")
                        st.write(f"作品主题: {artwork['artwork_theme']}")
                        st.write(f"创作者年龄: {artwork['age']}岁")
                        st.write(f"创作者性别: {artwork['gender']}")
                        st.write(f"地域: {artwork['location']}")
                        st.write(f"教育环境: {artwork['education_setting']}")
                        
                        # 添加分析按钮
                        if st.button(f"分析作品 #{artwork['artwork_id']}", key=f"analyze_{artwork['artwork_id']}"):
                            st.session_state.selected_artwork = artwork
                            st.session_state.page = "数据分析"
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"显示作品出错: {e}")
    
    def analysis_page(self):
        st.header("数据分析")
        
        if 'selected_artwork' not in st.session_state:
            st.warning("请先从作品浏览页面选择要分析的作品")
            return
        
        artwork = st.session_state.selected_artwork
        
        # 创建分析器实例
        analyzer = ColorAnalyzer()
        
        # 显示原始图片
        if os.path.exists(artwork['image_path']):
            image = Image.open(artwork['image_path'])
            st.image(image, caption="原始作品", use_container_width=True)
            
            # 分析色彩
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("主要色彩分析")
                dominant_colors = analyzer.extract_dominant_colors(artwork['image_path'])
                
                # 显示色彩比例
                for color, percentage in dominant_colors:
                    st.markdown(
                        f'<div style="background-color: {color}; '
                        f'width: {percentage*100}%; height: 30px; '
                        f'margin: 5px 0; border-radius: 5px;"></div>',
                        unsafe_allow_html=True
                    )
                    st.write(f"比例: {percentage*100:.1f}%")
            
            with col2:
                st.subheader("色彩心理分析")
                psychology = analyzer.analyze_color_psychology(dominant_colors)
                
                st.write("情绪特征:")
                for emotion, weight in psychology['emotions']:
                    st.write(f"- {emotion}: {weight*100:.1f}%")
                
                st.write("性格特征:")
                for trait, weight in psychology['traits']:
                    st.write(f"- {trait}: {weight*100:.1f}%")
            
            # 显示分布图
            st.subheader("色彩分布可视化")
            fig = analyzer.generate_visualization(artwork['image_path'])
            st.plotly_chart(fig, use_container_width=True)
            
            # 分析报告
            st.subheader("分析报告")
            distribution = analyzer.analyze_color_distribution(artwork['image_path'])
            
            # 使用plotly绘制分布图
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=distribution['hue_distribution'], name='色相分布'))
            fig.update_layout(title="色相分布直方图")
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("无法加载图片文件")
    
    def psychological_mapping_page(self):
        st.header("心理映射解读")
        
        if 'selected_artwork' not in st.session_state:
            st.warning("请先从作品浏览页面选择要分析的作品")
            return
        
        artwork = st.session_state.selected_artwork
        
        # 创建分析器实例
        color_analyzer = ColorAnalyzer()
        psych_analyzer = PsychologicalAnalyzer()
        
        if os.path.exists(artwork['image_path']):
            # 显示原始图片
            image = Image.open(artwork['image_path'])
            st.image(image, caption="分析作品", use_container_width=True)
            
            # 获取色彩数据
            dominant_colors = color_analyzer.extract_dominant_colors(artwork['image_path'])
            
            # 分析色彩模式
            color_patterns = psych_analyzer.analyze_color_patterns(dominant_colors)
            
            # 提取心理特征
            psychological_traits = psych_analyzer.extract_psychological_traits(
                color_patterns,
                artwork
            )
            
            # 生成建议
            recommendations = psych_analyzer.generate_recommendations(psychological_traits)
            
            # 显示分析结果
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("心理特征分析")
                
                # 显示特征得分
                for trait, score in psychological_traits.items():
                    st.markdown(f"### {trait.title()}")
                    st.progress(score)
                    st.write(f"得分: {score:.2f}")
                    
                    # 显示特征详情
                    with st.expander("查看详情"):
                        st.write("典型表现：")
                        for indicator in psych_analyzer.personality_traits[trait]['indicators']:
                            st.write(f"- {indicator}")
                        
                        st.write("兴趣倾向：")
                        for interest in psych_analyzer.personality_traits[trait]['interests']:
                            st.write(f"- {interest}")
                        
                        st.write("发展潜能：")
                        for potential in psych_analyzer.personality_traits[trait]['development']:
                            st.write(f"- {potential}")
            
            with col2:
                st.subheader("教育建议")
                
                # 显示建议
                for i, recommendation in enumerate(recommendations, 1):
                    st.write(f"{i}. {recommendation}")
                
                # 添加注意事项
                st.info("""
                注意事项：
                1. 本分析结果仅供参考
                2. 建议结合孩子实际情况
                3. 可以咨询专业教师获取更多建议
                """)
        
        else:
            st.error("无法加载图片文件")
    
    def report_page(self):
        st.header("统计报告")
        
        # 获取所有作品数据
        artworks = self.importer.get_all_artworks()
        
        if not artworks:
            st.info("暂无数据可供分析")
            return
        
        # 创建分析器实例
        analyzer = ColorAnalyzer()
        
        # 1. 基础统计
        st.subheader("1. 基础统计信息")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("作品总数", len(artworks))
            
            # 性别分布
            gender_counts = {}
            for artwork in artworks:
                gender = artwork['gender']
                gender_counts[gender] = gender_counts.get(gender, 0) + 1
            
            fig_gender = go.Figure(data=[go.Pie(
                labels=list(gender_counts.keys()),
                values=list(gender_counts.values()),
                hole=.3
            )])
            fig_gender.update_layout(title="性别分布")
            st.plotly_chart(fig_gender, use_container_width=True)
        
        with col2:
            # 年龄分布
            ages = [artwork['age'] for artwork in artworks]
            fig_age = go.Figure(data=[go.Histogram(x=ages, nbinsx=6)])
            fig_age.update_layout(title="年龄分布")
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col3:
            # 教育环境分布
            education_counts = {}
            for artwork in artworks:
                edu = artwork['education_setting']
                education_counts[edu] = education_counts.get(edu, 0) + 1
            
            fig_edu = go.Figure(data=[go.Pie(
                labels=list(education_counts.keys()),
                values=list(education_counts.values()),
                hole=.3
            )])
            fig_edu.update_layout(title="教育环境分布")
            st.plotly_chart(fig_edu, use_container_width=True)
        
        # 2. 色彩分析统计
        st.subheader("2. 色彩分析统计")
        
        # 收集所有作品的色彩数据
        all_colors = []
        color_emotions = []
        color_traits = []
        
        for artwork in artworks:
            if os.path.exists(artwork['image_path']):
                # 提取主要色彩
                dominant_colors = analyzer.extract_dominant_colors(artwork['image_path'])
                all_colors.extend([color for color, _ in dominant_colors])
                
                # 分析色彩心理
                psychology = analyzer.analyze_color_psychology(dominant_colors)
                color_emotions.extend([emotion for emotion, _ in psychology['emotions']])
                color_traits.extend([trait for trait, _ in psychology['traits']])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 主要色彩使用频率
            color_counts = {}
            for color in all_colors:
                color_counts[color] = color_counts.get(color, 0) + 1
            
            fig_colors = go.Figure(data=[go.Bar(
                x=list(color_counts.keys()),
                y=list(color_counts.values()),
                marker_color=list(color_counts.keys())
            )])
            fig_colors.update_layout(title="主要色彩使用频率")
            st.plotly_chart(fig_colors, use_container_width=True)
        
        with col2:
            # 情绪特征分布
            emotion_counts = {}
            for emotion in color_emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            fig_emotions = go.Figure(data=[go.Bar(
                x=list(emotion_counts.keys()),
                y=list(emotion_counts.values())
            )])
            fig_emotions.update_layout(title="情绪特征分布")
            st.plotly_chart(fig_emotions, use_container_width=True)
        
        # 3. 创作环境分析
        st.subheader("3. 创作环境分析")
        
        # 按环境分组的色彩使用
        env_colors = {}
        for artwork in artworks:
            env = artwork['education_setting']
            if env not in env_colors:
                env_colors[env] = []
            
            if os.path.exists(artwork['image_path']):
                dominant_colors = analyzer.extract_dominant_colors(artwork['image_path'])
                env_colors[env].extend([color for color, _ in dominant_colors])
        
        # 创建环境-色彩分布图
        env_color_data = []
        for env, colors in env_colors.items():
            color_counts = {}
            for color in colors:
                color_counts[color] = color_counts.get(color, 0) + 1
            
            for color, count in color_counts.items():
                env_color_data.append({
                    'environment': env,
                    'color': color,
                    'count': count
                })
        
        if env_color_data:
            df = pd.DataFrame(env_color_data)
            fig_env_colors = px.bar(
                df,
                x='environment',
                y='count',
                color='color',
                title="不同教育环境下的色彩使用"
            )
            st.plotly_chart(fig_env_colors, use_container_width=True)
        
        # 4. 时间趋势分析
        st.subheader("4. 时间趋势分析")
        
        # 按时间排序的作品数量
        artwork_dates = [artwork['creation_date'] for artwork in artworks]
        fig_timeline = go.Figure(data=[go.Histogram(x=artwork_dates)])
        fig_timeline.update_layout(title="作品创作时间分布")
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # 5. 综合分析报告
        st.subheader("5. 综合分析报告")
        
        # 计算一些关键指标
        total_artworks = len(artworks)
        avg_age = sum(ages) / len(ages) if ages else 0
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "无"
        
        st.write(f"""
        ### 主要发现：
        
        1. 数据概况
        - 总计分析了 {total_artworks} 件作品
        - 创作者平均年龄为 {avg_age:.1f} 岁
        - 最常见的情绪表达是 "{most_common_emotion}"
        
        2. 色彩使用特点
        - 主要使用的色彩为 {", ".join(list(color_counts.keys())[:3])}
        - 色彩情绪表达多样，包含 {len(emotion_counts)} 种不同情绪
        
        3. 教育环境影响
        - 不同教育环境下的色彩使用呈现出明显差异
        - 各环境下的创作数量分布相对 {max(education_counts.values())/min(education_counts.values()):.1f} 倍差异
        
        4. 建议
        - 可以针对不同年龄段设计差异化的美术教育方案
        - 建议关注色彩使用与情绪表达的关联
        - 可以进一步研究教育环境对创作的影响
        """)
    
    def run(self):
        self.setup_page()
        page = self.show_sidebar()
        
        if page == "数据录入":
            self.data_input_page()
        elif page == "作品查看":
            self.view_artwork_page()
        elif page == "数据分析":
            self.analysis_page()
        elif page == "心理映射":
            self.psychological_mapping_page()
        elif page == "统计报告":
            self.report_page()

if __name__ == "__main__":
    app = ArtworkAnalysisUI()
    app.run() 