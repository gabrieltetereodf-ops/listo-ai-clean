"""
LISTO AI - AGENDADOR DE AQUISICAO AUTONOMO (scheduler, R$0)
Roda diariamente o agente de conteudo (SEO + Pinterest) + publica resumo.
Sem n8n/Node: usa loop com sleep (ou agende via cron/WIndows Task Scheduler).
Mantem Dashboard KPI (data/kpi.json) atualizado.
"""
import os, json, time, datetime, subprocess, random

os.makedirs("data", exist_ok=True)
KPI = os.path.join("data", "kpi.json")

def run_content_agent():
    try:
        out = subprocess.run(["python", "automation/content_agent.py"], capture_output=True, text=True, timeout=120)
        return out.returncode == 0, out.stdout.strip()
    except Exception as e:
        return False, str(e)

def update_kpi(ok, note):
    k = json.load(open(KPI, encoding="utf-8")) if os.path.exists(KPI) else {"runs":[], "articles":0, "pins":0}
    k["runs"].append({"date": datetime.date.today().isoformat(), "ok": ok, "note": note})
    if ok:
        k["articles"] = k.get("articles",0)+1
        k["pins"] = k.get("pins",0)+3
    k["runs"] = k["runs"][-30:]
    json.dump(k, open(KPI,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

def daily():
    print(f"[{datetime.datetime.now()}] execucao diaria LISTO AI")
    ok, note = run_content_agent()
    update_kpi(ok, note)
    print("OK" if ok else "FALHA", note)

if __name__ == "__main__":
    # Modo daemon: roda 1x por dia. Para Windows agende via Task Scheduler chamando este script.
    # Para teste imediato, force 1 execucao:
    if os.environ.get("RUN_ONCE"):
        daily()
    else:
        daily()  # primeira execucao imediata; em prod, use loop:
        # while True:
        #     time.sleep(86400); daily()
