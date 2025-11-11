"""
Vercel 서버리스 함수
Flask 앱을 Vercel 서버리스 함수로 래핑
Vercel Python 런타임은 Flask 앱을 자동으로 감지합니다
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
from hyperliquid_binance_gap_server import app

# Vercel은 Flask 앱 객체를 자동으로 감지합니다
# app 객체를 그대로 export하면 됩니다
