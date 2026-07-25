# LISTO AI - Deploy Cloudflare Pages (R$0, SEM Node)
# Estrategia: Cloudflare Pages Functions (serverless em V8, linguagem nao importa p/ o estatico).
# O frontend (index.html) vira estatico. O backend Flask roda como Worker via adapter,
# OU (mais simples e 100% free) hospedamos o Flask em Railway/Render free e o front na Pages.
#
# OPÇÃO A (recomendada, R$0, 5 min):
#   1. Crie repo no GitHub com esta pasta.
#   2. Cloudflare Pages -> conecte o repo -> Framework: "None" / build: (vazio) -> output: ".".
#   3. O index.html é servido gratis globalmente (CDN).
#   4. Backend: use Render.com free (Python) -> aponte CORS para seu dominio Pages.
#
# OPÇÃO B (tudo Cloudflare, sem servidor): migrar app.py p/ Cloudflare Worker em JS.
#   Exemplo de functions/api/generate.js (stub gratuito, usa fallback local):
#
#   export async function onRequestPost({ request }) {
#     const { product, description, marketplace, lang } = await request.json();
#     const kws = (product+' '+description).toLowerCase().match(/[a-záàâãéèêíïóôõúüç]+/g)||[];
#     const title = `${product} | ${marketplace}`.slice(0,80);
#     const tags = [...new Set(kws)].slice(0,14);
#     return Response.json({ title, description: description, tags, seo_score: 80, engine:'cf-worker-local' });
#   }
#
# Para este MVP, mantemos Flask local + testamos. Deploy real sera Opçao A.
print("Veja instrucoes em DEPLOY.md (Opçao A: Pages + Render free).")
