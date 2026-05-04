import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="AI选股神器",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局变量
MARKET_INDEXES = {
    'sh': {'name': '上证指数', 'code': 'sh000001', 'color': '#EF4444'},
    'sz': {'name': '深证成指', 'code': 'sz399001', 'color': '#22C55E'},
    'cy': {'name': '创业板指', 'code': 'sz399006', 'color': '#3B82F6'},
    'hs': {'name': '恒生指数', 'code': 'hkHSI', 'color': '#A855F7'},
    'us': {'name': '纳斯达克', 'code': 'IXIC', 'color': '#F59E0B'}
}

# Mock数据 - 模拟股票数据
def get_mock_stock_data(code, days=60):
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
    base_price = np.random.uniform(10, 100)
    returns = np.random.normal(0, 0.01, days)
    prices = base_price * (1 + returns).cumprod()
    volumes = np.random.randint(1000000, 5000000, days)
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices * (1 - np.random.uniform(0, 0.01, days)),
        'close': prices,
        'high': prices * (1 + np.random.uniform(0, 0.015, days)),
        'low': prices * (1 - np.random.uniform(0, 0.015, days)),
        'volume': volumes
    })
    return df

# Mock数据 - 获取市场概览
def get_market_overview():
    return {
        'sh': {'最新价': 3205.68, '涨跌幅': 0.45},
        'sz': {'最新价': 10523.45, '涨跌幅': 0.78},
        'cy': {'最新价': 2156.78, '涨跌幅': 1.12},
        'hs': {'最新价': 17856.32, '涨跌幅': -0.35},
        'us': {'最新价': 15234.67, '涨跌幅': 0.89}
    }

# 计算市场情绪指数
def get_market_sentiment_index():
    market_data = get_market_overview()
    sh_change = market_data['sh']['涨跌幅']
    
    if sh_change > 2:
        sentiment = 85
    elif sh_change > 1:
        sentiment = 70
    elif sh_change > 0:
        sentiment = 58
    elif sh_change > -1:
        sentiment = 45
    elif sh_change > -2:
        sentiment = 30
    else:
        sentiment = 15
    
    return sentiment

# 获取行业轮动数据
def get_sector_rotation():
    return [
        {"name": "科技", "hot_score": 85, "trend": "上升", "reason": "AI、半导体持续火热"},
        {"name": "医药", "hot_score": 72, "trend": "上升", "reason": "创新药政策利好"},
        {"name": "新能源", "hot_score": 68, "trend": "震荡", "reason": "产业链调整中"},
        {"name": "消费", "hot_score": 55, "trend": "下降", "reason": "复苏不及预期"},
        {"name": "金融", "hot_score": 48, "trend": "震荡", "reason": "利率政策观望"},
        {"name": "周期", "hot_score": 42, "trend": "下降", "reason": "需求疲软"}
    ]

# 计算MACD指标
def calculate_macd(df, short=12, long=26, signal=9):
    df['EMA12'] = df['close'].ewm(span=short, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=long, adjust=False).mean()
    df['DIF'] = df['EMA12'] - df['EMA26']
    df['DEA'] = df['DIF'].ewm(span=signal, adjust=False).mean()
    df['MACD'] = 2 * (df['DIF'] - df['DEA'])
    return df

# 计算风险收益比
def calculate_risk_reward(df):
    latest_close = df['close'].iloc[-1]
    high_60 = df['high'].max()
    low_60 = df['low'].min()
    
    support = low_60 + (latest_close - low_60) * 0.2
    resistance = high_60
    stop_loss = latest_close - (latest_close - support)
    target = latest_close + (resistance - latest_close) * 1.5
    
    if (latest_close - stop_loss) > 0:
        rr_ratio = (target - latest_close) / (latest_close - stop_loss)
    else:
        rr_ratio = 1.0
    
    avg_volume = df['volume'].mean()
    volatility = (high_60 - low_60) / low_60 * 100
    
    return {
        'current': latest_close,
        'support': support,
        'resistance': resistance,
        'stop_loss': stop_loss,
        'target': target,
        'risk_reward_ratio': round(rr_ratio, 2),
        'avg_volume': avg_volume,
        'volatility': round(volatility, 2)
    }

# 获取模拟新闻数据
def get_news_data():
    return [
        {"title": "央行宣布下调存款准备金率0.25个百分点", "source": "财经头条", "time": "2小时前", "sentiment": "positive", "content": "此举将释放长期资金约5000亿元，有利于降低实体经济融资成本。"},
        {"title": "AI芯片需求持续火爆，龙头企业订单爆满", "source": "科技日报", "time": "3小时前", "sentiment": "positive", "content": "英伟达、AMD等公司财报超预期，AI芯片市场需求持续增长。"},
        {"title": "新能源汽车销量同比下降5%", "source": "证券时报", "time": "4小时前", "sentiment": "negative", "content": "受补贴退坡影响，新能源车市场增长放缓。"},
        {"title": "多地出台房地产支持政策", "source": "经济观察报", "time": "5小时前", "sentiment": "neutral", "content": "各地优化限购政策，市场观望情绪浓厚。"},
        {"title": "半导体产业迎政策利好，国产替代加速", "source": "中国证券报", "time": "6小时前", "sentiment": "positive", "content": "国家大基金持续加码，半导体产业链迎来发展机遇。"},
        {"title": "美联储宣布维持利率不变", "source": "华尔街日报", "time": "7小时前", "sentiment": "neutral", "content": "美联储维持当前利率水平，市场预期年内或有降息。"},
        {"title": "消费复苏不及预期，零售数据低于市场预期", "source": "第一财经", "time": "8小时前", "sentiment": "negative", "content": "居民消费意愿仍待提振，内需复苏任重道远。"},
        {"title": "量子计算取得重大突破", "source": "科技前沿", "time": "9小时前", "sentiment": "positive", "content": "我国量子计算原型机实现新突破，算力提升100倍。"}
    ]

# 获取模拟基金数据
def get_fund_data():
    return [
        {"name": "科技创新混合", "code": "008638", "type": "混合型", "return_1y": 28.5, "return_3y": 65.2, "max_drawdown": -18.5, "volatility": 22.3, "sharpe": 1.85, "manager": "张经理", "manager_exp": 12, "scale": 156.8},
        {"name": "新能源优选", "code": "009865", "type": "股票型", "return_1y": 15.2, "return_3y": 42.8, "max_drawdown": -25.3, "volatility": 28.6, "sharpe": 1.25, "manager": "李经理", "manager_exp": 8, "scale": 98.5},
        {"name": "稳健价值混合", "code": "005678", "type": "混合型", "return_1y": 12.8, "return_3y": 38.5, "max_drawdown": -12.2, "volatility": 15.8, "sharpe": 1.65, "manager": "王经理", "manager_exp": 15, "scale": 234.2},
        {"name": "医疗健康精选", "code": "007890", "type": "股票型", "return_1y": 22.3, "return_3y": 58.6, "max_drawdown": -21.8, "volatility": 24.5, "sharpe": 1.52, "manager": "陈经理", "manager_exp": 10, "scale": 178.6},
        {"name": "消费升级主题", "code": "004567", "type": "混合型", "return_1y": 8.5, "return_3y": 28.3, "max_drawdown": -15.6, "volatility": 18.2, "sharpe": 1.38, "manager": "赵经理", "manager_exp": 11, "scale": 145.3}
    ]

# 获取AI推荐股票
def get_ai_recommendations():
    return [
        {"code": "600519", "name": "贵州茅台", "reason": "业绩稳健，估值合理，长期投资价值凸显", "signal": "买入", "confidence": 85, "pe": 28.5, "pb": 6.8, "roe": 25.3},
        {"code": "000858", "name": "五粮液", "reason": "高端白酒需求稳定，渠道改革成效显著", "signal": "买入", "confidence": 78, "pe": 22.3, "pb": 5.2, "roe": 20.1},
        {"code": "300750", "name": "宁德时代", "reason": "动力电池龙头，技术领先，产能扩张有序", "signal": "观望", "confidence": 72, "pe": 45.8, "pb": 8.5, "roe": 18.6},
        {"code": "000001", "name": "平安银行", "reason": "零售转型成效显著，资产质量稳步改善", "signal": "买入", "confidence": 75, "pe": 9.2, "pb": 1.3, "roe": 14.5},
        {"code": "601318", "name": "中国平安", "reason": "寿险改革推进中，估值处于历史低位", "signal": "观望", "confidence": 68, "pe": 12.5, "pb": 1.8, "roe": 12.3}
    ]

# 尾盘选股策略
def get_closing_screen_results():
    return [
        {"code": "600123", "name": "XX科技", "type": "模式3", "reason": "尾盘小幅拉升，成交量放大，MACD金叉", "score": 92},
        {"code": "002345", "name": "XX制造", "type": "模式4", "reason": "先涨后回落，但未跌破均线，承接力强", "score": 85},
        {"code": "300456", "name": "XX生物", "type": "模式3", "reason": "尾盘拉升3%，量比1.8，换手率7.2%", "score": 88},
        {"code": "600789", "name": "XX电子", "type": "模式6", "reason": "符合筛选条件，5日线金叉30日线", "score": 90},
        {"code": "000123", "name": "XX能源", "type": "模式1", "reason": "尾盘跌破开盘价，主力出逃迹象", "score": 25}
    ]

# 技术分析预测
def analyze_stock_prediction(df):
    latest_close = df['close'].iloc[-1]
    df = calculate_macd(df)
    latest_dif = df['DIF'].iloc[-1]
    latest_dea = df['DEA'].iloc[-1]
    latest_macd = df['MACD'].iloc[-1]
    
    # 计算均线
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA10'] = df['close'].rolling(10).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    df['MA60'] = df['close'].rolling(60).mean()
    
    ma5 = df['MA5'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    ma60 = df['MA60'].iloc[-1]
    
    score = 50
    
    # MACD信号
    if latest_dif > latest_dea and latest_macd > 0:
        score += 20
    elif latest_dif < latest_dea and latest_macd < 0:
        score -= 20
    
    # 均线信号
    if latest_close > ma5 > ma20 > ma60:
        score += 15
    elif latest_close < ma5 < ma20 < ma60:
        score -= 15
    
    # 趋势判断
    recent_trend = df['close'].pct_change().tail(10).mean()
    if recent_trend > 0.005:
        score += 10
    elif recent_trend < -0.005:
        score -= 10
    
    # 成交量判断
    recent_volume = df['volume'].tail(5).mean()
    avg_volume = df['volume'].mean()
    if recent_volume > avg_volume * 1.3:
        score += 5
    
    if score >= 75:
        return {"signal": "入仓", "score": score, "reason": f"MACD金叉({round(latest_dif,2)}>{round(latest_dea,2)})，均线多头排列，建议买入"},
    elif score >= 55:
        return {"signal": "观望", "score": score, "reason": f"指标信号混杂，{'' if latest_dif > latest_dea else 'MACD死叉,'}均线{'' if latest_close > ma20 else '下方,'}建议观望"},
    else:
        return {"signal": "平仓", "score": score, "reason": f"MACD死叉({round(latest_dif,2)}<{round(latest_dea,2)})，均线空头排列，建议减仓或平仓"}

# 页面：大盘概览
def page_market_overview():
    st.title("📊 大盘概览")
    
    market_data = get_market_overview()
    sentiment = get_market_sentiment_index()
    sectors = get_sector_rotation()
    
    # 指数卡片
    cols = st.columns(5)
    for i, (key, info) in enumerate(MARKET_INDEXES.items()):
        data = market_data.get(key, {'最新价': 0, '涨跌幅': 0})
        with cols[i]:
            st.info(f"**{info['name']}**")
            st.metric(
                value=f"{data['最新价']:,.2f}",
                delta=f"{data['涨跌幅']:+.2f}%",
                delta_color="normal"
            )
    
    # 市场情绪指数
    st.subheader("📈 市场情绪指数")
    sentiment_emoji = "😀" if sentiment >= 70 else "😊" if sentiment >= 50 else "😐" if sentiment >= 30 else "😟"
    st.markdown(f"## {sentiment_emoji} 当前情绪指数: **{sentiment}**")
    
    # 情绪分布
    bull_ratio = sentiment / 100
    bear_ratio = 1 - bull_ratio
    fig = go.Figure(data=[go.Pie(
        labels=['看多', '看空'],
        values=[bull_ratio, bear_ratio],
        hole=0.6,
        marker_colors=['#22C55E', '#EF4444'],
        textinfo='label+percent'
    )])
    fig.update_layout(height=250)
    st.plotly_chart(fig, width='stretch')
    
    # 行业轮动
    st.subheader("🏢 行业轮动图谱")
    sector_df = pd.DataFrame(sectors)
    fig = go.Figure(data=[go.Bar(
        x=sector_df['name'],
        y=sector_df['hot_score'],
        marker_color=sector_df['trend'].map({'上升': '#22C55E', '震荡': '#F59E0B', '下降': '#EF4444'})
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, width='stretch')
    
    # 行业详情
    for sector in sectors:
        trend_color = {'上升': 'green', '震荡': 'orange', '下降': 'red'}[sector['trend']]
        st.write(f"- **{sector['name']}** (热度: {sector['hot_score']}分) - <span style='color:{trend_color}'>{sector['trend']}</span>: {sector['reason']}", unsafe_allow_html=True)
    
    # AI操作建议
    st.subheader("🤖 AI操作建议")
    if sentiment >= 70:
        st.success("**建议：积极做多**\n\n市场情绪高涨，可关注科技、AI等热门板块，适当提高仓位。")
    elif sentiment >= 50:
        st.info("**建议：谨慎观望**\n\n市场情绪中性，建议等待明确信号，控制仓位在50%-70%。")
    else:
        st.warning("**建议：防御为主**\n\n市场情绪低迷，建议降低仓位，关注防御性板块如消费、医药。")

# 页面：技术分析
def page_technical_analysis():
    st.title("📈 技术分析")
    
    stock_code = st.text_input("输入股票代码", value="", placeholder="例如: 600519")
    
    if stock_code:
        df = get_mock_stock_data(stock_code)
        df = calculate_macd(df)
        risk_reward = calculate_risk_reward(df)
        prediction = analyze_stock_prediction(df)
        
        # K线图
        st.subheader("K线图")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
        
        # 蜡烛图
        fig.add_trace(go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K线'
        ), row=1, col=1)
        
        # 均线
        fig.add_trace(go.Scatter(x=df['date'], y=df['close'].rolling(5).mean(), name='MA5', line=dict(color='red', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['date'], y=df['close'].rolling(20).mean(), name='MA20', line=dict(color='blue', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['date'], y=df['close'].rolling(60).mean(), name='MA60', line=dict(color='green', width=1)), row=1, col=1)
        
        # 成交量
        fig.add_trace(go.Bar(x=df['date'], y=df['volume'], name='成交量'), row=2, col=1)
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, width='stretch')
        
        # MACD分析
        st.subheader("📊 MACD深度分析")
        fig_macd = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.6, 0.4])
        
        fig_macd.add_trace(go.Scatter(x=df['date'], y=df['DIF'], name='DIF', line=dict(color='blue')), row=1, col=1)
        fig_macd.add_trace(go.Scatter(x=df['date'], y=df['DEA'], name='DEA', line=dict(color='red')), row=1, col=1)
        
        colors = ['red' if val < 0 else 'green' for val in df['MACD']]
        fig_macd.add_trace(go.Bar(x=df['date'], y=df['MACD'], name='MACD', marker_color=colors), row=2, col=1)
        
        fig_macd.update_layout(height=300)
        st.plotly_chart(fig_macd, width='stretch')
        
        # 风险收益分析
        st.subheader("🎯 风险收益分析")
        risk_cols = st.columns(4)
        with risk_cols[0]:
            st.info(f"**支撑位**\n\n{risk_reward['support']:.2f}")
        with risk_cols[1]:
            st.info(f"**压力位**\n\n{risk_reward['resistance']:.2f}")
        with risk_cols[2]:
            st.info(f"**止损位**\n\n{risk_reward['stop_loss']:.2f}")
        with risk_cols[3]:
            st.info(f"**目标价**\n\n{risk_reward['target']:.2f}")
        
        st.metric("风险收益比", risk_reward['risk_reward_ratio'])
        st.metric("波动率", f"{risk_reward['volatility']}%")
        
        # 操作建议
        st.subheader("📌 操作建议")
        signal_color = {'入仓': 'green', '观望': 'orange', '平仓': 'red'}[prediction['signal']]
        st.markdown(f"### <span style='color:{signal_color}'>{prediction['signal']}</span> (置信度: {prediction['score']}%)", unsafe_allow_html=True)
        st.write(f"**分析依据：** {prediction['reason']}")

# 页面：市场新闻
def page_market_news():
    st.title("📰 市场新闻")
    
    news_data = get_news_data()
    
    # 情绪分布
    sentiment_counts = pd.Series([n['sentiment'] for n in news_data]).value_counts()
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index.map({'positive': '利好', 'negative': '利空', 'neutral': '中性'}),
        values=sentiment_counts.values,
        hole=0.6,
        marker_colors=['#22C55E', '#EF4444', '#9CA3AF']
    )])
    fig.update_layout(height=250)
    st.plotly_chart(fig, width='stretch')
    
    # 情绪解读
    st.subheader("💬 情绪解读")
    positive_ratio = sentiment_counts.get('positive', 0) / len(news_data)
    if positive_ratio > 0.5:
        st.success("当前市场情绪偏乐观，利好消息占主导，可适当关注相关板块机会。")
    elif positive_ratio > 0.3:
        st.info("当前市场情绪中性，多空消息交织，建议保持观望态度。")
    else:
        st.warning("当前市场情绪偏悲观，利空消息较多，建议谨慎操作。")
    
    # 资讯筛选
    filter_option = st.selectbox("筛选类型", ["全部", "只看利好", "只看利空"])
    
    filtered_news = news_data
    if filter_option == "只看利好":
        filtered_news = [n for n in news_data if n['sentiment'] == 'positive']
    elif filter_option == "只看利空":
        filtered_news = [n for n in news_data if n['sentiment'] == 'negative']
    
    # 新闻列表
    for news in filtered_news:
        border_color = {'positive': '#22C55E', 'negative': '#EF4444', 'neutral': '#9CA3AF'}[news['sentiment']]
        tag = {'positive': '📈 利好', 'negative': '📉 利空', 'neutral': '⚖️ 中性'}[news['sentiment']]
        
        st.markdown(f"""
        <div style='border-left: 4px solid {border_color}; padding-left: 12px; margin-bottom: 12px;'>
            <span style='font-size: 14px; color: {border_color};'>{tag}</span>
            <h4>{news['title']}</h4>
            <p style='color: #6B7280; font-size: 14px;'>{news['content']}</p>
            <p style='color: #9CA3AF; font-size: 12px;'>{news['source']} · {news['time']}</p>
        </div>
        """, unsafe_allow_html=True)

# 页面：AI推荐
def page_ai_recommendation():
    st.title("🤖 AI智能推荐")
    
    recommendations = get_ai_recommendations()
    
    for stock in recommendations:
        signal_color = {'买入': '#22C55E', '观望': '#F59E0B', '卖出': '#EF4444'}[stock['signal']]
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"""
            <div style='text-align: center; padding: 16px; background: #F9FAFB; border-radius: 8px;'>
                <p style='font-size: 18px; font-weight: bold;'>{stock['code']}</p>
                <p style='font-size: 14px; color: #6B7280;'>{stock['name']}</p>
                <p style='font-size: 24px; font-weight: bold; color: {signal_color};'>{stock['signal']}</p>
                <p style='font-size: 12px; color: #9CA3AF;'>置信度: {stock['confidence']}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='padding: 16px;'>
                <h4>📊 推荐理由</h4>
                <p>{stock['reason']}</p>
                <div style='display: flex; gap: 20px; margin-top: 16px;'>
                    <span>PE: {stock['pe']}</span>
                    <span>PB: {stock['pb']}</span>
                    <span>ROE: {stock['roe']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    # 投资建议说明
    st.subheader("📚 投资建议说明")
    st.write("""
    **买入信号**：基本面优秀，估值合理，技术面看涨，风险收益比良好
    
    **观望信号**：存在一定不确定性，需要等待更明确的信号
    
    **卖出/减仓信号**：基本面恶化或估值过高，技术面看空
    
    ⚠️ 以上仅为AI分析建议，不构成投资建议。投资有风险，入市需谨慎。
    """)

# 页面：基金推荐
def page_fund_recommendation():
    st.title("💰 基金推荐")
    
    fund_data = get_fund_data()
    
    for fund in fund_data:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.info(f"""
            **{fund['name']}**\n
            代码: {fund['code']}\n
            类型: {fund['type']}\n
            规模: {fund['scale']}亿
            """)
        
        with col2:
            st.write(f"**基金经理**: {fund['manager']} ({fund['manager_exp']}年经验)")
            
            metrics_cols = st.columns(4)
            with metrics_cols[0]:
                st.metric("近1年收益", f"{fund['return_1y']}%")
            with metrics_cols[1]:
                st.metric("近3年收益", f"{fund['return_3y']}%")
            with metrics_cols[2]:
                st.metric("最大回撤", f"{fund['max_drawdown']}%")
            with metrics_cols[3]:
                st.metric("夏普比率", fund['sharpe'])
        
        # 风险收益评估
        reward_risk_ratio = fund['return_3y'] / abs(fund['max_drawdown'])
        if reward_risk_ratio > 3:
            st.success(f"✅ 风险收益比优秀 ({reward_risk_ratio:.2f})，适合积极型投资者")
        elif reward_risk_ratio > 2:
            st.info(f"⚠️ 风险收益比适中 ({reward_risk_ratio:.2f})，适合稳健型投资者")
        else:
            st.warning(f"❌ 风险收益比较低 ({reward_risk_ratio:.2f})，需谨慎")
        
        st.markdown("---")
    
    # 基金学习园地
    st.subheader("📚 基金学习园地")
    st.write("""
    **夏普比率**：衡量每承担一单位风险所获得的超额收益，越高越好
    
    **最大回撤**：衡量基金净值从最高点到最低点的最大跌幅，越小越好
    
    **收益风险比**：总收益与最大回撤的比值，大于2为良好，大于3为优秀
    """)
    
    # 投资小贴士
    st.subheader("💡 投资小贴士")
    st.write("""
    - **长期持有**：基金适合长期投资，建议持有周期至少3年
    - **定投策略**：定期定额投资可以平滑市场波动
    - **分散配置**：不要把所有资金投入单一基金
    - **关注费率**：低费率基金长期收益更有优势
    """)

# 页面：尾盘选股
def page_closing_screen():
    st.title("🕐 尾盘选票")
    
    st.subheader("📋 选股模式说明")
    st.write("""
    **模式1**: 尾盘半小时先涨后回落跌破开盘价 → 主力抢跑，后续大概率大跌 ⚠️
    
    **模式2**: 尾盘半小时先跌后反弹但未过开盘价 → 主力做多意愿弱，第二天大概率低开 ⚠️
    
    **模式3**: 尾盘半小时小幅拉升(≤3%)，均线上方震荡，成交量放大 → 第二天大概率有动作，甚至涨停 🎯
    
    **模式4**: 尾盘半小时先涨后回落但未跌破均线 → 承接力强，第二天有冲高机会 📈
    
    **模式5**: 尾盘半小时持续震荡无亮点 → 洗盘阶段，可暂时观望 ⏳
    
    **模式6**: 筛选涨幅3%-5%，量比>1，换手率5%-10%，市值50-200亿，5日线金叉30日线的标的 ✅
    """)
    
    # 选股结果
    st.subheader("🔍 今日选股结果")
    results = get_closing_screen_results()
    
    for stock in results:
        if stock['score'] >= 80:
            bg_color = '#ECFDF5'
            border_color = '#22C55E'
            tag = '强烈推荐'
        elif stock['score'] >= 60:
            bg_color = '#FFFBEB'
            border_color = '#F59E0B'
            tag = '关注'
        else:
            bg_color = '#FEF2F2'
            border_color = '#EF4444'
            tag = '规避'
        
        st.markdown(f"""
        <div style='background: {bg_color}; border-left: 4px solid {border_color}; padding: 16px; margin-bottom: 12px;'>
            <span style='background: {border_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;'>{tag}</span>
            <span style='margin-left: 12px;'>模式{stock['type'][-1]}</span>
            <h4>{stock['code']} {stock['name']}</h4>
            <p style='color: #6B7280;'>{stock['reason']}</p>
            <p style='color: {border_color}; font-weight: bold;'>综合评分: {stock['score']}分</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("⚠️ 尾盘选股结果仅供参考，实际操作请结合自身风险承受能力。")

# 主程序
def main():
    st.sidebar.title("📈 AI选股神器")
    
    pages = {
        "大盘概览": page_market_overview,
        "技术分析": page_technical_analysis,
        "市场新闻": page_market_news,
        "AI推荐": page_ai_recommendation,
        "基金推荐": page_fund_recommendation,
        "尾盘选票": page_closing_screen
    }
    
    selected_page = st.sidebar.radio("选择功能", list(pages.keys()))
    
    pages[selected_page]()
    
    st.sidebar.markdown("---")
    st.sidebar.info("⚠️ 投资有风险，入市需谨慎\n\n本系统仅供学习参考，不构成投资建议")

if __name__ == "__main__":
    main()