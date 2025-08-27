from xpl_price_monitor import app

# Vercel에서 Flask 앱을 실행하기 위한 핸들러
def handler(request, context):
    return app(request, context)

# Flask 앱을 직접 export
app.debug = False
