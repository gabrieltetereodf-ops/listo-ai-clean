"""
LISTO AI - Servidor de desenvolvimento (front + proxy opcional)
Serve o front (index.html) e faz proxy das chamadas /api para o backend Flask.
Assim o usuario pode abrir no celular usando o IP da rede local.
Uso: python serve.py  (front na 8080, proxy -> 127.0.0.1:8021)
"""
import os, urllib.request
from http.server import SimpleHTTPRequestHandler, HTTPServer

BACKEND = "http://127.0.0.1:8021"
PORT = int(os.environ.get("PORT", 8080))

class H(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.startswith("/api/"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b""
            req = urllib.request.Request(BACKEND + self.path, data=body,
                headers={k: v for k, v in self.headers.items() if k.lower() not in ("host", "content-length")},
                method="POST")
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = r.read()
                self.send_response(r.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404); self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/"):
            req = urllib.request.Request(BACKEND + self.path,
                headers={k: v for k, v in self.headers.items() if k.lower() != "host"})
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = r.read()
                self.send_response(r.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_response(502); self.end_headers(); self.wfile.write(str(e).encode())
        elif self.path == "/config.js" or self.path.startswith("/config.js?"):
            # Config dinamico: aponta o front para o MESMO host:porta (proxy embutido).
            # Funciona no PC (localhost) e no celular (IP da rede) sem editar nada.
            host = self.headers.get("Host", f"127.0.0.1:{PORT}").split(":")[0]
            origin = f"http://{host}:{PORT}"
            js = f'window.LISTO_API = "{origin}";\n'
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(js.encode())
        else:
            super().do_GET()

    def log_message(self, *a): pass

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"LISTO front em http://0.0.0.0:{PORT}  (proxy -> {BACKEND})")
    HTTPServer(("0.0.0.0", PORT), H).serve_forever()
