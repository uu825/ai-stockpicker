import os
import sys

os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_PORT"] = "3000"
os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit.web import cli as stcli

def handler(event, context):
    """Vercel handler function"""
    sys.argv = ["streamlit", "run", "app.py", "--server.port=3000", "--server.headless=true"]
    try:
        stcli.main()
        return {"statusCode": 200}
    except SystemExit:
        return {"statusCode": 200}

if __name__ == "__main__":
    handler(None, None)