# LISTO AI — Deploy (R$0, 10 min)

## Passo 1: Cloudflare Pages (frontend)
1. Acesse `dash.cloudflare.com` → login
2. **Workers & Pages** → **Create application** → **Pages**
3. **Connect to Git** → conecte GitHub → repo `gabrieltetereodf-ops/listo-ai`
4. Preencha:
   - Project name: **listo-ai**
   - Production branch: **main**
   - Build command: *(deixe vazio)*
   - Output directory: **.**
   - Base directory: **listo**
5. **Save and Deploy** → seu site estará em `https://listo-ai.pages.dev`

## Passo 2: Render.com (backend Python grátis)
1. Acesse `dashboard.render.com` → **Sign Up / Log In**
2. **New +** → **Web Service**
3. Conecte ao repo **gabrieltetereodf-ops/listo-ai**
4. Preencha:
   - **Name:** listo-ai-backend
   - **Region:** US West
   - **Root Directory:** listo
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
5. Clique **Advanced** → **Add Environment Variable**:
   - `PORT` = `8000`
   - `STRIPE_SECRET_KEY` = cole sua chave secreta do Stripe Dashboard → API Keys
6. **Deploy Web Service**

## Passo 3: Conectar front ao backend
No deploy automático, o `config.js` serve a URL correta via proxy. Se precisar ajustar:
```javascript
window.LISTO_API = 'https://listo-ai-backend.onrender.com';
```

## Pronto ✅
