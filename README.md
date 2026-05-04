# 🤖 AI选股神器

一个基于 Streamlit 的智能股票分析和推荐系统。

## ✨ 功能特点

### 📊 大盘概览
- 实时行情监控（上证指数、深证成指、创业板指）
- 市场情绪指数分析
- 行业轮动图谱
- 多空情绪分布

### 📈 技术分析
- K线与均线系统分析
- MACD指标深度解析
- 成交量分析
- 风险收益比计算
- AI智能预测

### 📰 市场新闻
- 实时资讯采集
- 情感分析（利好/中性/利空）
- 情绪分布可视化

### 🤖 AI推荐
- 多维度股票评分
- 行业轮动分析
- 风险收益评估
- 操作建议生成

### 💰 基金推荐
- 基金综合评分
- 夏普比率分析
- 基金经理评价
- 投资建议

### 🔚 尾盘选票
- 6种尾盘选股策略
- 智能形态识别

## 🚀 快速开始

### 环境要求
- Python 3.10+
- pip

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
streamlit run app.py
```

### 访问应用
打开浏览器访问：http://localhost:8501

## 📁 项目结构
```
ai-stock-picker/
├── app.py              # 主应用文件
├── requirements.txt    # 依赖列表
├── .streamlit/
│   └── config.toml     # Streamlit配置
└── README.md           # 说明文档
```

## 🛠️ 技术栈
- **框架**: Streamlit
- **数据**: AkShare
- **可视化**: Plotly
- **数据分析**: Pandas, NumPy

## 🌐 部署

### Streamlit Share
1. 将代码推送到 GitHub
2. 访问 https://share.streamlit.io
3. 填写仓库信息并部署

### Docker
```bash
docker build -t ai-stock-picker .
docker run -p 8501:8501 ai-stock-picker
```

## ⚠️ 风险提示
本系统仅供辅助决策参考，不构成任何投资建议。投资有风险，入市需谨慎。

## 📝 更新日志
- v1.0: 初始版本
- v1.1: 新增AI推荐升级、风险收益分析
- v1.2: 新增尾盘选票功能

## 📧 联系方式
如有问题或建议，欢迎反馈！