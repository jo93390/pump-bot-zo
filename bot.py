import requests
import time
import os
from threading import Thread

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def fake_web_server():
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running")
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

def get_new_tokens():
    url = "https://api.geckoterminal.com/api/v2/networks/solana/new_pools"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            tokens = []
            for pool in data.get("data", [])[:15]:
                attrs = pool.get("attributes", {})
                market_cap = attrs.get("market_cap", {}).get("usd", 0)
                if 5000 < market_cap < 50000:
                    tokens.append({
                        "name": attrs.get("name", "?"),
                        "symbol": attrs.get("symbol", "?"),
                        "price": attrs.get("price_usd", "?"),
                        "market_cap": market_cap,
                        "url": f"https://www.geckoterminal.com/solana/pools/{pool['id']}"
                    })
            return tokens
    except Exception as e:
        print(f"Erreur Gecko: {e}")
    return []

send("🔥 Bot Pump Fun (Gecko) actif – petits caps 5k-50k$")
Thread(target=fake_web_server).start()

seen = set()
while True:
    try:
        tokens = get_new_tokens()
        for t in tokens:
            key = t["symbol"] + str(t["market_cap"])
            if key not in seen:
                seen.add(key)
                msg = f"🚨 NOUVEAU TOKEN FRAIS\n📛 {t['name']} ({t['symbol']})\n💰 ${t['price']}\n🎩 Market Cap: ${t['market_cap']:,.0f}\n🔗 {t['url']}"
                send(msg)
        time.sleep(20)
    except Exception as e:
        time.sleep(30)
