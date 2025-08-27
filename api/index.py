from xpl_price_monitor import app

# Vercel serverless function entry point
if __name__ == '__main__':
    app.run()

# Flask 앱을 직접 export
app.debug = False
