# LISTO AI

Micro-SaaS autônomo. Gerador de listagens SEO para marketplaces (Etsy, Mercado Livre, Amazon, Shopify).

- **Custo:** R$0/mês
- **Margem:** ~99%
- **Automação:** 95% por IA
- **Receita:** assinaturas Pro (R$49) e Business (R$149)/mês

## Stack
- Backend: Flask (Python) + CORS
- Front: HTML/CSS/JS + Three.js (3D glassmorphism)
- Infra: Cloudflare Pages (front) + Render.com (backend)
- Pagamento: Stripe + Mercado Pago (modo teste/simulado quando sem chaves)

## Setup local
```bash
pip install flask flask-cors
python app.py   # backend :8021
python serve.py  # front+proxy :8080
```

Ver `INSTRUOES_DEPLOY.md` para deploy produtivo R$0.
