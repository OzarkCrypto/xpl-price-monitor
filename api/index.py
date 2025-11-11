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
except Exception as e:
    # 에러 발생 시 상세 정보와 함께 에러 Flask 앱 생성
    import traceback
    from flask import Flask
    
    error_app = Flask(__name__)
    error_details = f"""
    <h1>Vercel Deployment Error</h1>
    <h2>Error: {str(e)}</h2>
    <pre>{traceback.format_exc()}</pre>
    <hr>
    <p>Project root: {project_root}</p>
    <p>Python path: {sys.path}</p>
    <p>Current dir: {os.getcwd()}</p>
    <p>Files in project root: {os.listdir(project_root) if os.path.exists(project_root) else 'N/A'}</p>
    """
    
    @error_app.route('/')
    def error():
        return error_details, 500
    
    @error_app.route('/api/<path:path>')
    def api_error(path):
        return {"error": str(e), "traceback": traceback.format_exc()}, 500
    
    app = error_app
