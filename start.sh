# 部署脚本
#!/bin/bash

echo "🚀 AI选股神器部署脚本"

# 检查是否已安装 streamlit
if ! command -v streamlit &> /dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
fi

# 启动应用
echo "🌐 启动应用..."
streamlit run app.py --server.port 8501 --server.headless true

echo "✅ 应用已启动！"
echo "🔗 访问地址: http://localhost:8501"