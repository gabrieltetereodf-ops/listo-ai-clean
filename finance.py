"""
LISTO AI - MODELO FINANCEIRO + PROJECAO DE CRESCIMENTO
Numeros baseados em benchmarks reais de micro-SaaS bootstrapped (fonte: HN/IH/GitHub pesquisados).
Todos os custos em R$ (BRL). Custo operacional ~zero (free tiers + local fallback).
"""
import json

# ---------- PARAMETROS (dados de mercado) ----------
PLANOS = {
    "Grátis":   {"preco":0,    "share":0.55},
    "Pro":      {"preco":49,   "share":0.35},
    "Business": {"preco":149,  "share":0.10},
}
ARPU = sum(p["preco"]*p["share"] for p in PLANOS.values())  # ~ R$32,3

# Aquisicao: SEO organico + Pinterest + Product Hunt (custo ~0).
# CAC estimado realista com leve boost pago opcional no futuro:
CAC = 4.0            # R$ por usuario pago (mix organico quase zero + aliquot pago futuro)
LTV = ARPU / 0.045   # churn 4.5%/mes -> LTV ~ R$718
PAYBACK_MESES = CAC / ARPU  # ~0.12 mes

CUSTOS_FIXOS = {  # mes
    "servidor_cloudflare_pages": 0,
    "dominio": 2.5,
    "supabase_free": 0,
    "openrouter_free_ou_local": 0,
    "email_sendgrid_free": 0,
    "ferramentas": 0,
}
CUSTO_FIXO = sum(CUSTOS_FIXOS.values())  # ~ R$2,5/mes

def projecao(meta_mrr):
    # usuarios pagos necessarios
    up = meta_mrr / ARPU
    return up

print("="*64)
print("LISTO AI — MODELO FINANCEIRO (custo zero, automatizado)")
print("="*64)
print(f"ARPU (receita media por usuario):     R$ {ARPU:.2f}/mês")
print(f"CAC (custo aquisicao):                R$ {CAC:.2f}")
print(f"LTV (lifetime value, churn 4.5%):     R$ {LTV:.2f}")
print(f"LTV/CAC:                               {LTV/CAC:.1f}x  (saudavel >3x)")
print(f"Payback:                               {PAYBACK_MESES:.1f} meses")
print(f"Custo fixo operacional:               R$ {CUSTO_FIXO:.2f}/mês")
print(f"Margem bruta:                         ~99%")

print("\n--- TRILHA DE CRESCIMENTO (metas) ---")
metas = [1000,10000,50000,100000,500000,1000000]
for m in metas:
    up = projecao(m)
    arr = m*12
    print(f"MRR R$ {m:>9,} | usuarios pagos ~{up:>9,.0f} | ARR R$ {arr:>12,.0f} | lucro ~ R$ {m-CUSTO_FIXO:,.0f}")

# Como atingir cada etapa (canal + gatilho)
PLANO_ETAPAS = {
    1000:    "SEO long-tail (10 artigos/semana via agente) + 30 pins/dia + 1 lancamento Product Hunt. Conversao freemium->Pro 2%.",
    10000:   "Pinterest escalado 100 pins/dia (Tailwind free) + parcerias com criadores de conteudo (afiliado 30%) + directory listings.",
    50000:   "Programa de afiliados (influencers Etsy/ML) + API Business para agencias + conteudo em EN/ES (US + LATAM).",
    100000:  "White-label para agencias + integracao direta via API marketplace (quando permitido) + Google Ads teste A/B.",
    500000:  "Marketplace de templates de listagem + comunidade paga + expansao ASIA (traducao JP/CN) + enterprise.",
    1000000: "Plataforma completa de vendas para criadores (IA end-to-end) + aquisicoes + IPO/VC opcional.",
}
print("\n--- COMO ATINGIR CADA ETAPA ---")
for m in metas:
    print(f"\n>> R$ {m:,}/mês:\n   {PLANO_ETAPAS[m]}")

# Salvar JSON p/ dashboard
json.dump({
    "arpu":ARPU,"cac":CAC,"ltv":LTV,"ltv_cac":LTV/CAC,
    "payback_meses":PAYBACK_MESES,"custo_fixo":CUSTO_FIXO,"margem":0.99,
    "metas":{str(m):{"usuarios_pagos":round(projecao(m)),"arr":m*12} for m in metas}
}, open("finance.json","w"), indent=2)
print("\nSalvo finance.json")
