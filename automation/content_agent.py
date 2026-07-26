"""
LISTO AI - AGENTE DE CONTEUDO AUTONOMO (SEO + Pinterest)
Gera 1 artigo SEO + 3 ideias de Pin diariamente a partir de uma lista de nichos.
Sem custo (heuristica local) ou com OpenRouter free tier se OPENROUTER_API_KEY set.
Escreve em content/YYYY-MM-DD.md e content/pins.csv (pronto p/ agendar no n8n/buffer).
"""
import os, json, datetime, urllib.request

NICHE_KEYWORDS = [
    "caneca personalizada", "camiseta bordada", "adesivo sticker", "quadro decoracao",
    "artesanato presente", "produto digital planilha", "papelaria casamento",
    "pet acessorio", "vela aromatica", "caneca aniversario", "camisa time",
]

POST_IDEAS = [
    "Como criar {k} que vendem todos os dias (guia 2026)",
    "10 erros de SEO em {k} que matam suas vendas",
    "Titulos perfeitos para {k}: template copia-e-cola",
    "Como subir seu {k} no topo do Mercado Livre e Etsy",
    "{k}: as 14 tags que geram mais cliques",
]

def fallback_article(kw):
    return f"""# {kw.title()}: guia definitivo para vender mais em 2026

Você vende **{kw}** mas não aparece nas buscas? O problema quase sempre é o SEO da listagem.

## Por que a maioria erra
Vendedores descrevem o produto como *eles* pensam, não como o cliente busca. Quem compra digita termos como "{kw}", variações e intenção de compra.

## 3 passos para uma listagem que vende
1. **Título com a palavra-chave na frente** — ex: "{kw} personalizada presente".
2. **Descrição com benefícios + emojis** — scanável no celular.
3. **14 tags de cauda longa** — use ferramentas como LISTO AI para gerar em segundos.

## Tags sugeridas
{', '.join([kw, kw+' presente', kw+' personalizada', kw+' artesanal'])}

> Automatize tudo: LISTO AI gera título + descrição + tags em 10s, multi-marketplace.

*Publicado por LISTO AI · conteúdo gerado por agente autônomo.*
"""

def llm_article(kw):
    if not os.environ.get("OPENROUTER_API_KEY"): return None
    prompt = f"Write an SEO blog post in Portuguese about selling '{kw}' on Etsy/Mercado Livre. Include H2 headers, tips, and 14 tags. Return JSON {{title, body, tags:[]}}."
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps({"model":"qwen/qwen2.5-7b-instruct:free","messages":[{"role":"user","content":prompt}],"response_format":{"type":"json_object"}}).encode(),
            headers={"Authorization":f"Bearer {os.environ['OPENROUTER_API_KEY']}","Content-Type":"application/json","HTTP-Referer":"https://listoai.app"})
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(json.load(r)["choices"][0]["message"]["content"])
        return d
    except Exception:
        return None

def run():
    today = datetime.date.today().isoformat()
    os.makedirs("content", exist_ok=True)
    kw = NICHE_KEYWORDS[datetime.date.today().toordinal() % len(NICHE_KEYWORDS)]
    art = llm_article(kw) or {"title": f"{kw.title()}: guia definitivo para vender mais", "body": fallback_article(kw), "tags":[kw, kw+" presente", kw+" personalizada"]}
    path = f"content/{today}-{kw.replace(' ','-')}.md"
    with open(path,"w",encoding="utf-8") as f:
        f.write(f"# {art.get('title', kw)}\n\n{art.get('body','')}\n")
    # Pinterest pins (3)
    pins = []
    for i, tpl in enumerate(POST_IDEAS[:3]):
        pins.append({"date": today, "niche": kw, "pin_title": tpl.format(k=kw).title(),
                     "pin_desc": f"{tpl.format(k=kw)} 📌 Salve para depois! Veja como em listoai.app",
                     "link": "https://listoai.app"})
    import csv
    with open("content/pins.csv","a",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","niche","pin_title","pin_desc","link"])
        if f.tell()==0: w.writeheader()
        for p in pins: w.writerow(p)
    print(f"OK artigo -> {path}")
    print(f"OK {len(pins)} pins -> content/pins.csv")
    print("Titulo:", art.get("title"))

if __name__ == "__main__":
    run()
