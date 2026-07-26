# DEPLOY LISTO AI — R$0

## OPÇÃO A (recomendada, 5 min, sem cartão)
1. Crie um repositório no GitHub e suba esta pasta `listo/`.
2. **Frontend (grátis, CDN global):**
   - Cloudflare → Pages → "Connect to Git" → escolha o repo.
   - Build command: **(vazio)** · Output directory: **`.`**
   - O `index.html` vira site global em `https://listoai.pages.dev`.
3. **Backend (grátis):**
   - Render.com → New Web Service → conecte o repo.
   - Runtime: Python 3 · Start: `pip install -r requirements.txt && python app.py`
   - Env: `PORT=8011`.
   - Copie a URL (ex: `https://listoai.onrender.com`) e troque `127.0.0.1:8021` no frontend pelo domínio.
4. **Domínio próprio (opcional):** Cloudflare Registrar ~R$40/ano, ou use o `.pages.dev` grátis.

## OPÇÃO B (tudo Cloudflare, sem servidor)
Migrar `app.py` para Cloudflare Worker (functions/api/generate.js) — ver `deploy_cloudflare.py`.
Custo: R$0 até 100k requests/dia.

## Pagamentos reais (quando tiver tráfego)
- Defina `STRIPE_SECRET_KEY` e/ou `MERCADOPAGO_TOKEN` como Secrets (Render/Cloudflare).
- O endpoint `/api/checkout` passa do modo teste (simulado) para cobrança real.
- Webhook confirma pagamento e faz upgrade do plano (já implementado o upgrade local).

## Automação diária (conteúdo SEO + Pinterest)
- Linux/Mac: `crontab -e` → `0 8 * * * cd /caminho/listo && python scheduler.py`
- Windows: Task Scheduler → tarefa diária 08:00 chamando `python scheduler.py`.
- (Ou rode `python scheduler.py` em background — ele executa 1x/dia.)

## Verificação pós-deploy
- `curl https://SEU.pages.dev/` → HTTP 200
- `curl https://SEU-backend/api/health` → {"status":"ok"}
- Teste register → generate → checkout (modo teste ativa Pro).
