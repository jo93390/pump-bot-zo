import requests
import time
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PUBLIC_RPC = "https://api.mainnet-beta.solana.com"
PUMP_FUN_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

# Seuil minimum de market cap en dollars (ex: 7000 $)
MIN_MARKET_CAP = 7000

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Erreur envoi:", e)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
def keep_alive():
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

def get_recent_pumpfun_signatures():
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [PUMP_FUN_PROGRAM, {"limit": 10}]
    }
    try:
        r = requests.post(PUBLIC_RPC, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            signatures = []
            for sig in data.get("result", []):
                signatures.append(sig["signature"])
            return signatures
    except Exception as e:
        print("Erreur scan signatures:", e)
    return []

def get_token_info_from_signature(signature):
    """
    Essaie de trouver le token correspondant à une signature
    via DexScreener (search par signature ou par créneau horaire)
    """
    try:
        # DexScreener permet de chercher par pair address, pas par signature
        # On va plutôt chercher les tokens récents et les matcher
        url = "https://api.dexscreener.com/latest/dex/search?q=solana"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for pair in data.get("pairs", []):
                # Vérifie si le token a été créé récemment (moins de 2 minutes)
                # DexScreener donne un timestamp "pairCreatedAt"
                created_at = pair.get("pairCreatedAt", 0)
                if created_at and (time.time() * 1000 - created_at) < 120000:  # 2 minutes
                    market_cap = float(pair.get("fdv", 0))  # Fully Diluted Value
                    if market_cap >= MIN_MARKET_CAP:
                        return {
                            "name": pair.get("baseToken", {}).get("name", "?"),
                            "symbol": pair.get("baseToken", {}).get("symbol", "?"),
                            "market_cap": market_cap,
                            "price": float(pair.get("priceUsd", 0)),
                            "url": pair.get("url", "")
                        }
    except Exception as e:
        print("Erreur DexScreener:", e)
    return None

seen = set()
def main_loop():
    global seen
    while True:
        try:
            sigs = get_recent_pumpfun_signatures()
            for sig in sigs:
                if sig not in seen:
                    seen.add(sig)
                    # On attend 30 secondes pour que DexScreener indexe le token
                    time.sleep(30)
                    token_info = get_token_info_from_signature(sig)
                    if token_info:
                        msg = (
                            f"🚨 **NOUVEAU TOKEN PUMP.FUN**\n\n"
                            f"📛 {token_info['name']} ({token_info['symbol']})\n"
                            f"💰 Prix : ${token_info['price']:.8f}\n"
                            f"🎩 Market Cap : ${token_info['market_cap']:,.0f}\n"
                            f"🔗 {token_info['url']}"
                        )
                    else:
                        msg = f"🚨 Nouveau token détecté (infos non disponibles)\n🔗 Signature : {sig}"
                    send_telegram(msg)
            time.sleep(15)
        except Exception as e:
            print("Erreur boucle:", e)
            time.sleep(60)

if __name__ == "__main__":
    send_telegram("🔥 Bot Pump.fun actif – Filtre Market Cap > 7000$")
    Thread(target=keep_alive).start()
    main_loop()
