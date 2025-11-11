"""
Vercel 서버리스 함수
Flask 앱을 Vercel 서버리스 함수로 래핑
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Flask 앱 import
from hyperliquid_binance_gap_server import app

# Vercel은 자동으로 Flask 앱을 감지합니다
# app 객체를 export하면 됩니다
