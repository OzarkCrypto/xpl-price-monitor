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

# Flask 앱 import (에러 발생 시 상세 정보 표시)
try:
    from hyperliquid_binance_gap_server import app
    print("✅ Flask app imported successfully", file=sys.stderr)
except Exception as e:
    import traceback
    error_msg = f"❌ Import failed: {str(e)}\n\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
    
    # 에러 핸들러 Flask 앱 생성
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"<h1>Application Error</h1><pre>{error_msg}</pre>", 500
    
    @app.route('/api/<path:path>')
    def api_error(path):
        return {"error": str(e), "traceback": traceback.format_exc()}, 500
