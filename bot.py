import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(e)

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
seen = set()

while True:
    try:
        tokens = get_new_tokens()
        for t in tokens:
            key = t["symbol"]
            if key not in seen:
                seen.add(key)
                if float(t["liquidity"]) < 50000:
                    continue
                msg = f"🚨 {t['name']} ({t['symbol']})\n💰 ${t['price']}\n💧 ${t['liquidity']}\n🔗 {t['url']}"
                send(msg)
        time.sleep(60)
    except:
        time.sleep(60)
