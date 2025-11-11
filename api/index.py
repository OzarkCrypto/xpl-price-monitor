"""
Vercel 서버리스 함수
Flask 앱을 Vercel 서버리스 함수로 래핑
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Vercel 환경 변수 설정
os.environ['VERCEL'] = '1'
os.environ['DISABLE_BACKGROUND_MONITOR'] = '1'

# Flask 앱 import
try:
    from hyperliquid_binance_gap_server import app
except ImportError as e:
    # Import 실패 시 에러 핸들러
    from flask import Flask
    import traceback
    
    app = Flask(__name__)
    
    error_details = f"Import Error: {str(e)}\n\n{traceback.format_exc()}"
    
    @app.route('/')
    def error():
        return f"<pre>{error_details}</pre>", 500
    
    @app.route('/api/<path:path>')
    def api_error(path):
        return f"<pre>{error_details}</pre>", 500
except Exception as e:
    # 기타 에러
    from flask import Flask
    import traceback
    
    app = Flask(__name__)
    
    error_details = f"Error: {str(e)}\n\n{traceback.format_exc()}"
    
    @app.route('/')
    def error():
        return f"<pre>{error_details}</pre>", 500
    
    @app.route('/api/<path:path>')
    def api_error(path):
        return f"<pre>{error_details}</pre>", 500
