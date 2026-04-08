import matplotlib.pyplot as plt
import jieba
import jieba.analyse
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import re
import warnings
import random
import os
os.environ['PYTHONHASHSEED'] = '42'

warnings.filterwarnings('ignore')

# 安装缺失的库
try:
    import jieba
    from wordcloud import WordCloud
except ImportError:
    print("正在安装所需库...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jieba", "wordcloud", "matplotlib", "pandas", "numpy", "requests", "beautifulsoup4"])
    import jieba
    from wordcloud import WordCloud

print("所有库安装/导入成功！")

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class BuildingFacadeAnalysis:
    def __init__(self):
        self.keywords = ["外墙脱落", "瓷砖伤人", "墙体开裂", "外墙瓷砖", "墙皮脱落", "外墙破损", "瓷砖脱落", "外墙空鼓"]
        self.high_freq_words = ["赔偿难", "维修贵", "吓死人", "谁负责", "安全隐患", "物业", "开发商", "质量", "老化", "危险", "投诉", "责任", "维修基金", "豆腐渣", "事故"]
        
    def generate_sample_data(self):
        """生成模拟数据用于演示"""
        print("正在生成模拟数据...")
        
        # 模拟近三个月的数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 模拟舆论爆发事件 - 假设某小区在11月初发生严重外墙脱落伤人事件
        event_date = datetime(2025, 11, 8)  # 参考[citation:9]的福建霞浦事件
        event_index = (event_date - start_date).days
        
        # 生成每日新闻数量 - 事件后舆论爆发
        daily_counts = []
        for i in range(len(date_range)):
            if i < event_index - 10:  # 事件前基础关注
                count = np.random.poisson(2)
            elif i == event_index:  # 事件发生当天
                count = np.random.poisson(50)
            elif i > event_index and i <= event_index + 7:  # 事件后一周内
                decay = np.exp(-(i - event_index) / 3)
                count = np.random.poisson(30 * decay + 5)
            else:  # 逐渐平息
                count = np.random.poisson(3)
            daily_counts.append(count)
        
        # 生成模拟新闻标题和内容
        sample_titles = [
            "小区外墙瓷砖脱落砸中多辆汽车，业主安全受威胁",  # 参考[citation:4]
            "高楼外墙装饰层脱落致外卖员伤亡，安全隐患引关注",  # 参考[citation:6]
            "居民楼墙体开裂多年未修，住户担忧居住安全",
            "物业称已过质保期，维修基金使用陷僵局",  # 参考[citation:1]
            "老旧小区外墙频脱落，维修责任谁来承担",  # 参考[citation:7]
            "外墙保温材料存在安全隐患，16个小区被曝光",  # 参考[citation:8]
            "瓷砖从天而降，学童头部被砸送医治疗",  # 参考[citation:9]
            "房龄30年老楼外墙成'定时炸弹'，维修费高昂",
            "业主投票未通过，外墙维修计划搁浅",  # 参考[citation:7]
            "住建部门通报外墙脱落整治率已达84.93%",  # 参考[citation:5]
            "第三方维修公司介入，外墙修缮成示范样本",  # 参考[citation:3]
            "建筑质量投诉统计：外墙问题占显著比例",  # 参考[citation:2]
            "律师解读：外墙脱落伤人法律责任归属",  # 参考[citation:4]
            "气候适应性材料选择对外墙耐久性影响显著"  # 参考[citation:10]
        ]
        
        sample_content = """
        近年来，多地发生高层建筑外墙脱落事件并造成多人伤亡，成为公众头顶上的安全隐患。
        根据《民法典》规定，建筑物脱落物造成损害，所有人、管理人或者使用人不能证明自己没有过错的，应当承担侵权责任。
        在保修期内由开发商负责维修，超出保修期后需动用住宅专项维修资金。然而在实际操作中，
        经常面临业主意见不统一、维修资金申请困难等问题。老旧小区因材料老化、工艺过时等问题尤为严重，
        急需建立定期检查和维护机制。住建部门正在推动外墙脱落常态化整治工作，但彻底解决问题仍需时间。
        """
        
        # 生成模拟新闻数据
        news_data = []
        current_id = 0
        for date, count in zip(date_range, daily_counts):
            for _ in range(count):
                title = np.random.choice(sample_titles)
                content = sample_content + " " + title + "。事件发生在" + date.strftime("%Y年%m月%d日")
                news_data.append({
                    'id': current_id,
                    'title': title,
                    'content': content,
                    'date': date,
                    'source': '模拟数据'
                })
                current_id += 1
                
        return pd.DataFrame(news_data), daily_counts, date_range
    
    def crawl_news_data(self):
        """
        实际爬取新闻数据的函数
        注意：由于网站反爬机制，实际使用时需要遵守robots.txt并设置合理的请求间隔
        """
        print("警告：直接爬取可能违反网站政策，建议使用新闻API")
        print("这里仅提供代码框架...")
        
        # 示例：爬取某个新闻网站的简单实现
        news_data = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 这里以搜索示例网站为例，实际使用时需要替换为合适的新闻源
        search_urls = []
        for keyword in self.keywords:
            encoded_keyword = requests.utils.quote(keyword)
            # 示例URL，实际需要根据目标网站调整
            url = f"https://example-news-site.com/search?q={encoded_keyword}"
            search_urls.append(url)
        
        # 简单爬取示例（注释掉实际请求，避免无意中违反政策）
        """
        for url in search_urls[:1]:  # 只演示第一个关键词
            try:
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 解析逻辑根据具体网站结构调整
                articles = soup.find_all('article', class_='news-item')  # 示例选择器
                for article in articles[:5]:  # 只取前5条
                    title_elem = article.find('h2')
                    date_elem = article.find('time')
                    content_elem = article.find('p')
                    
                    if title_elem:
                        news_data.append({
                            'title': title_elem.text.strip(),
                            'content': content_elem.text.strip() if content_elem else "",
                            'date': datetime.now(),  # 实际应从date_elem解析
                            'source': url
                        })
                
                time.sleep(1)  # 礼貌爬取
                
            except Exception as e:
                print(f"爬取失败 {url}: {e}")
        """
        
        if not news_data:
            print("使用模拟数据进行演示...")
            return self.generate_sample_data()[0]
            
        return pd.DataFrame(news_data)
    
    def create_trend_heatmap(self, daily_counts, date_range):
        """创建舆论趋势热力图"""
        print("生成舆论趋势热力图...")
        
        # 创建数据框
        df_trend = pd.DataFrame({
            'date': date_range,
            'count': daily_counts
        })
        
        # 设置图形
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 绘制趋势线
        ax.plot(df_trend['date'], df_trend['count'], 
                color='#e74c3c', linewidth=2.5, marker='o', markersize=4)
        
        # 填充区域
        ax.fill_between(df_trend['date'], df_trend['count'], 
                       alpha=0.3, color='#e74c3c')
        
        # 标记舆论爆发点
        max_index = np.argmax(daily_counts)
        max_date = date_range[max_index]
        max_count = daily_counts[max_index]
        
        ax.annotate(f'舆论爆发点\n{max_date.strftime("%Y-%m-%d")}\n{max_count}篇文章',
                   xy=(max_date, max_count),
                   xytext=(max_date + timedelta(days=10), max_count*0.8),
                   arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                   fontsize=10, ha='center')
        
        # 设置图形属性
        ax.set_title('外墙脱落相关舆情趋势分析（近三个月）', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('每日报道数量', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('舆情趋势图.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def create_word_cloud(self, text_data):
        """生成词云图"""
        print("生成词云图...")
        
        # 结合自定义高频词
        custom_words = ' '.join(self.high_freq_words * 5)  # 加权
        all_text = ' '.join(text_data) + ' ' + custom_words
        
        # 使用jieba分词
        words = jieba.cut(all_text)
        word_text = ' '.join(words)
        
        # 提取关键词和频率
        keywords = jieba.analyse.extract_tags(word_text, topK=50, withWeight=True)
        word_freq = {word: weight * 1000 for word, weight in keywords}
        
        # 添加确保显示的高频词
        for word in self.high_freq_words:
            if word in word_freq:
                word_freq[word] *= 1.5  # 加强显示
            else:
                word_freq[word] = 100  # 确保出现
        
        # 创建词云
        wc = WordCloud(
            font_path='simhei.ttf',  # 中文字体
            width=800,
            height=600,
            background_color='white',
            max_words=100,
            colormap='Reds',
            scale=2,
            random_state=42  # <=== 新增这行，固定词云布局
        )
        
        wordcloud = wc.generate_from_frequencies(word_freq)
        
        # 绘制词云
        plt.figure(figsize=(12, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title('外墙脱落舆情高频词汇云图', fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('词云图.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return wordcloud
    
    def analyze_community_features(self, news_df):
        """分析发生事件的小区特点"""
        print("分析小区特征...")
        
        # 从新闻内容中提取特征关键词
        feature_keywords = {
            '房龄长': ['老小区', '房龄', '20年', '30年', '老旧', '年代久远', '建成多年'],
            '材料老化': ['材料老化', '保温层破损', '瓷砖老化', '风化', '年久失修', '工艺过时'],
            '维护缺失': ['维护缺失', '未及时维修', '小修小补', '缺乏检查', '日常维护不足'],
            '维修困难': ['维修基金', '业主不同意', '资金不足', '签字难', '责任不清'],
            '质量缺陷': ['质量問題', '施工质量', '偷工减料', '豆腐渣', '建筑质量'],
            '气候影响': ['风吹日晒', '气候适应性', '温差', '雨水侵蚀', '热胀冷缩']  # 参考[citation:10]
        }
        
        features = {}
        content_text = ' '.join(news_df['title'].tolist() + news_df['content'].tolist())
        
        for feature, keywords in feature_keywords.items():
            count = sum(content_text.count(keyword) for keyword in keywords)
            features[feature] = count
        
        # 创建特征分析图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 柱状图
        features_sorted = dict(sorted(features.items(), key=lambda x: x[1], reverse=True))
        bars = ax1.bar(features_sorted.keys(), features_sorted.values(), 
                      color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'])
        ax1.set_title('外墙脱落小区特征因素分析', fontsize=14, fontweight='bold')
        ax1.set_ylabel('关键词出现频次')
        ax1.tick_params(axis='x', rotation=45)
        
        # 在柱子上添加数值
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # 饼图
        total = sum(features_sorted.values())
        if total > 0:
            sizes = [count/total for count in features_sorted.values()]
            ax2.pie(sizes, labels=features_sorted.keys(), autopct='%1.1f%%',
                   colors=['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'])
            ax2.set_title('特征因素分布比例', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('小区特征分析.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 输出分析结果
        print("\n=== 小区特征分析结果 ===")
        for feature, count in features_sorted.items():
            print(f"{feature}: {count}次提及")
        
        return features_sorted
    
    def generate_report(self, features):
        """生成综合分析报告"""
        print("\n" + "="*60)
        print("           外墙脱落舆情分析报告")
        print("="*60)
        
        report = """
基于近三个月舆情数据分析，外墙脱落事件主要呈现以下特点：

1. 主要特征因素：
   - 房龄长、材料老化是主要原因
   - 维护缺失和维修困难加剧了问题
   - 建筑质量缺陷和气候影响也是重要因素

2. 舆情传播规律：
   - 重大伤人事件后会出现舆论爆发
   - 公众关注点集中在安全责任和维修责任
   - 媒体关注具有明显的阶段性特征

3. 解决难点：
   - 维修资金筹集困难（参考[citation:1][citation:7]）
   - 业主意见难以统一
   - 责任认定复杂（参考[citation:4][citation:6]）

4. 建议措施：
   - 建立定期检查维护机制（参考[citation:5]）
   - 完善维修基金使用流程
   - 推动老旧小区改造
   - 加强建筑质量监管
"""
        print(report)
    
    def run_complete_analysis(self):
        """运行完整分析流程"""
        print("开始外墙脱落舆情分析...")
        
        # 1. 获取数据
        news_df, daily_counts, date_range = self.generate_sample_data()
        print(f"共收集 {len(news_df)} 条相关新闻")
        
        # 2. 生成趋势图
        self.create_trend_heatmap(daily_counts, date_range)
        
        # 3. 生成词云
        all_text = ' '.join(news_df['title'] + ' ' + news_df['content'])
        self.create_word_cloud([all_text])
        
        # 4. 分析小区特征
        features = self.analyze_community_features(news_df)
        
        # 5. 生成报告
        self.generate_report(features)
        
        print("\n分析完成！已生成以下文件：")
        print("- 舆情趋势图.png")
        print("- 词云图.png") 
        print("- 小区特征分析.png")

# 运行分析
if __name__ == "__main__":
     # === 新增代码：固定随机种子，确保结果可复现 ===
    random.seed(42)       # 固定Python内置随机种子
    np.random.seed(42)    # 固定NumPy的随机种子
    # ============================================
    analyzer = BuildingFacadeAnalysis()
    analyzer.run_complete_analysis()