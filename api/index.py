"""
Vercel 서버리스 함수
Flask 앱을 Vercel 서버리스 함수로 래핑
Vercel 환경에서는 백그라운드 스레드 없이 요청 시마다 데이터를 가져옵니다.
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Vercel 환경 변수 확인
IS_VERCEL = os.environ.get('VERCEL') == '1'

if IS_VERCEL:
    # Vercel 환경: 백그라운드 스레드 없이 Flask 앱만 import
    # 백그라운드 모니터링은 비활성화
    os.environ['DISABLE_BACKGROUND_MONITOR'] = '1'

# Flask 앱 import
from hyperliquid_binance_gap_server import app

# Vercel은 자동으로 Flask 앱을 감지합니다
# app 객체를 export하면 됩니다
