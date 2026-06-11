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
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            tokens = []
            for pair in data.get("pairs", [])[:10]:
                tokens.append({
                    "name": pair["baseToken"]["name"],
                    "symbol": pair["baseToken"]["symbol"],
                    "price": pair.get("priceUsd", 0),
                    "liquidity": pair.get("liquidity", {}).get("usd", 0),
                    "url": pair["url"]
                })
            return tokens
    except:
        return []
    return []

send("🔥 Bot Pump Fun actif, Alpha.")

Thread(target=fake_web_server).start()

seen = set()
while True:
    try:
        tokens = get_new_tokens()
        for t in tokens:
            key = t["symbol"]
            if key not in seen:
                seen.add(key)
                if float(t["liquidity"]) < 7000:
                    continue
                msg = f"🚨 {t['name']} ({t['symbol']})\n💰 ${t['price']}\n💧 ${t['liquidity']}\n🔗 {t['url']}"
                send(msg)
        time.sleep(60)
    except:
        time.sleep(60)
