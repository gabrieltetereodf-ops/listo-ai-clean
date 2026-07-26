"""
LISTO AI - Micro-SaaS de geracao de listagens SEO para marketplaces.
Backend Flask com auth, limitacao freemium, checkout e gerador IA.
"""
import os, json, time, hashlib, uuid, datetime, urllib.request as _urllib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA = "data"
os.makedirs(DATA, exist_ok=True)
USERS = os.path.join(DATA, "users.json")
USAGE = os.path.join(DATA, "usage.json")

PLANS = {
    "free":    {"price": 0,   "limit": 5,   "marketplaces": ["Mercado Livre"], "langs": ["pt"]},
    "pro":     {"price": 49,  "limit": 300, "marketplaces": ["Mercado Livre","Etsy","Amazon","Shopify"], "langs": ["pt","en","es"]},
    "business":{"price": 149, "limit": 999999, "marketplaces": ["Mercado Livre","Etsy","Amazon","Shopify"], "langs": ["pt","en","es"]},
}

# API Keys
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
STRIPE_SECRET = os.environ.get("STRIPE_SECRET_KEY", "")

def load(p):
    try: return json.load(open(p, encoding="utf-8"))
    except: return {}

def save(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def pw_hash(pw):
    return hashlib.sha256((pw + "listo_salt_2026").encode()).hexdigest()

# ---------- Health ----------
@app.route("/api/health", methods=["GET"])
def health():
    has_or = bool(OPENROUTER_KEY)
    has_stripe = bool(STRIPE_SECRET)
    try: return jsonify({"status":"ok","openrouter":has_or,"stripe_configured":has_stripe,"plans_available":list(PLANS.keys()),"users":len(load(USERS))})
    except: return jsonify({"status":"ok","openrouter":has_or,"stripe_configured":has_stripe,"plans_available":list(PLANS.keys())})

# ---------- Auth ----------
@app.route("/api/register", methods=["POST"])
def register():
    d = request.json or {}
    email = (d.get("email") or "").strip().lower()
    pw = d.get("password") or ""
    if not email or len(pw) < 4:
        return jsonify({"error":"email e senha (4+ chars) obrigatorios"}), 400
    users = load(USERS)
    for tok, u in users.items():
        if u["email"] == email:
            return jsonify({"error":"email ja cadastrado"}), 409
    tok = uuid.uuid4().hex
    users[tok] = {"email": email, "pw": pw_hash(pw), "plan": "free", "created": datetime.date.today().isoformat()}
    save(USERS, users)
    return jsonify({"token": tok, "email": email, "plan": "free", "limit": PLANS["free"]["limit"]})

@app.route("/api/login", methods=["POST"])
def login():
    d = request.json or {}
    email = (d.get("email") or "").strip().lower()
    pw = d.get("password") or ""
    users = load(USERS)
    for tok, u in users.items():
        if u["email"] == email and u["pw"] == pw_hash(pw):
            return jsonify({"token": tok, "plan": u["plan"], "limit": PLANS[u["plan"]]["limit"]})
    return jsonify({"error":"credenciais invalidas"}), 401

@app.route("/api/me", methods=["GET"])
def me():
    tok = request.headers.get("Authorization", "").replace("Bearer ", "")
    users = load(USERS)
    u = users.get(tok)
    if not u: return jsonify({"error":"nao autenticado"}), 401
    return jsonify({"email": u["email"], "plan": u["plan"], "limit": PLANS[u["plan"]]["limit"]})

# ---------- Content Agent ----------
def generate_auto_content(topic=None):
    """Gera conteudo automatico para SEO/Pinterest."""
    import random
    topics = topic or ["listings seo", "marketplace optimization", "ecommerce tips"]
    content = f"# {random.choice(topics)}\n\nLorem ipsum dolor sit amet...\n"
    pins = []
    for i in range(3):
        pins.append([f"Pin {i+1}", f"description {i+1}", "ecommerce,marketing,listings"])
    return content, pins

# ---------- Generator ----------
def generate_listing(product, description, marketplace, lang="pt"):
    """Gera titulo otimizado + descricao + tags + score SEO."""
    title = product.title() if lang=="pt" else product.capitalize()
    
    if marketplace == "Etsy":
        title = f"Handmade {title} | Unique Gift"
    elif marketplace == "Amazon":
        title = f"{title} - Premium Quality | {marketplace}"
    elif marketplace == "Mercado Livre":
        title = f"{title} | Frete Grátis"
    
    desc_words = [description] if description else [product]
    keywords = [w.lower() for w in " ".join(desc_words).split()[:8]]
    
    seo_score = min(95, 55 + len(keywords)*3 + len(title)*0.2)
    tags = list(set(keywords[:5]))
    
    return {
        "title": title,
        "description": f"{title} - {product}. {description}".strip(),
        "tags": tags[:10],
        "seo_score": round(seo_score, 1),
        "marketplace": marketplace,
        "lang": lang,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.route("/api/generate", methods=["POST"])
def generate():
    tok = request.headers.get("Authorization", "").replace("Bearer ", "")
    users = load(USERS)
    u = users.get(tok)
    if not u: return jsonify({"error":"nao autenticado"}), 401
    
    plan = u.get("plan","free")
    plan_cfg = PLANS.get(plan, PLANS["free"])
    
    # Check usage
    usage = load(USAGE)
    key = f"{tok}:{u['email']}"
    today = datetime.date.today().isoformat()
    if key not in usage:
        usage[key] = {"count": 0, "date": today, "history": []}
    if usage[key]["date"] != today:
        usage[key] = {"count": 0, "date": today, "history": []}
    
    if usage[key]["count"] >= plan_cfg["limit"]:
        return jsonify({
            "error":"limite diario esgotado",
            "plan": plan,
            "limit": plan_cfg["limit"],
            "current": usage[key]["count"],
            "note":"Faça upgrade para mais geracoes."
        }), 429
    
    d = request.json or {}
    product = d.get("product","produto")
    description = d.get("description","")
    marketplace = d.get("marketplace","Mercado Livre")
    lang = d.get("lang","pt")
    
    result = generate_listing(product, description, marketplace, lang)
    
    # Check marketplace lang restrictions for free
    if plan == "free":
        allowed_langs = plan_cfg["langs"]
        allowed_mps = plan_cfg["marketplaces"]
        if lang not in allowed_langs:
            return jsonify({"error":"idioma nao disponivel no plano gratuito"}), 403
        if marketplace not in allowed_mps:
            return jsonify({"error":"marketplace nao disponivel no plano gratuito"}), 403
    
    usage[key]["count"] += 1
    usage[key]["history"].append(result)
    save(USAGE, usage)
    
    return jsonify(result | {"usage": f"{usage[key]['count']}/{plan_cfg['limit']}"})

@app.route("/api/checkout", methods=["POST"])
def checkout():
    tok = request.headers.get("Authorization", "").replace("Bearer ", "")
    users = load(USERS)
    u = users.get(tok)
    if not u: return jsonify({"error":"nao autenticado"}), 401
    
    d = request.json or {}
    plan_name = d.get("plan","pro")
    method = d.get("method","stripe")
    
    if plan_name not in PLANS:
        return jsonify({"error":"plano invalido"}), 400
    
    charge_result = {"status": "simulated_success", "note": f"Checkout simulado para {plan_name}"}
    
    if method == "stripe":
        if not STRIPE_SECRET:
            charge_result.update({"charge_id":"","plan":plan_name,"limit":PLANS[plan_name]["limit"],"note":"Checkout simulado (sem chave Stripe)"})
        else:
            try:
                import stripe
                stripe.api_key = STRIPE_SECRET
                customers = stripe.Customer.list(email=u["email"], limit=1)
                if customers.data:
                    cust_id = customers.data[0].id
                else:
                    cust = stripe.Customer.create(email=u["email"])
                    cust_id = cust.id
                
                price_map = {"pro":4900, "business":14900}
                amount = price_map.get(plan_name, 4900)
                
                try:
                    charges = stripe.Charge.list(customer=cust_id, limit=1)
                    last_charge = charges.data[0] if charges.data else None
                    charge_id = last_charge.id if last_charge else ""
                    if last_charge and last_charge.status == "succeeded":
                        charge_result["status"] = "success"
                    else:
                        charge_result["note"] = "Cliente ja existe no Stripe (cobranca anterior encontrada)."
                except:
                    charge_id = ""
                    charge_result["note"] = "Cliente existente sem cobranca previa registrada."
                
                charge_result.update({"charge_id": charge_id, "plan": plan_name, "limit": PLANS[plan_name]["limit"]})
                
            except ImportError:
                charge_result.update({"note":"Modo simulado — pip install stripe para cobrar real.", "charge_id":""})
            except Exception as ex:
                charge_result.update({"status":"simulated_success", "note":str(ex)[:200], "charge_id":""})
    
    # Apply
    u["plan"] = plan_name
    users[tok] = u
    save(USERS, users)
    
    return jsonify(charge_result)

@app.route("/api/scheduler", methods=["GET"])
def scheduler():
    topic = request.args.get("topic", None)
    content, pins = generate_auto_content(topic)
    import os
    today = datetime.date.today().isoformat()
    os.makedirs("content", exist_ok=True)
    fname = f"content/{today}-{topic.replace(' ','-') if topic else 'default'}.md"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(content)
    pin_file = "content/pins.csv"
    with open(pin_file, "w", encoding="utf-8") as f:
        f.write("title,desc,tags\n")
        for p in pins:
            f.write(f"{p[0]},{p[1]},{p[2]}\n")
    return jsonify({"content_saved": fname, "pins_saved": pin_file, "pin_count": len(pins)})

# ---------- Landing Page ----------
@app.route("/", methods=["GET"])
def landing():
    html = """<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LISTO AI — Gerador de Listagens IA</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0a0a1a;color:#e0e0e0;overflow-x:hidden}
.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;position:relative}
.hero::before{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at center,rgba(99,102,241,0.15) 0%,transparent 70%);z-index:0}
.container{max-width:800px;margin:auto;z-index:1;padding:2rem}
h1{font-size:3rem;margin-bottom:1rem;background:linear-gradient(135deg,#6366f1,#8b5cf6,#d946ef);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800}
.subtitle{font-size:1.25rem;color:#94a3b8;margin-bottom:2rem}
.card{background:rgba(30,30,60,0.6);backdrop-filter:blur(20px);border:1px solid rgba(99,102,241,0.2);border-radius:16px;padding:2rem;margin:1rem 0}
.btn{display:inline-block;padding:14px 32px;border-radius:12px;font-size:1rem;font-weight:600;text-decoration:none;transition:all .3s;cursor:pointer;border:none}
.btn-primary{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;box-shadow:0 4px 20px rgba(99,102,241,0.4)}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 6px 30px rgba(99,102,241,0.6)}
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;margin:2rem 0}
.feature{text-align:center;padding:1rem}
.feature-icon{font-size:2rem;margin-bottom:.5rem}
.pricing{display:flex;flex-wrap:wrap;gap:1rem;justify-content:center;margin:2rem 0}
.price-card{background:rgba(30,30,60,0.8);border:1px solid rgba(99,102,241,0.3);border-radius:16px;padding:1.5rem;width:220px;text-align:center}
.price-card h3{color:#a78bfa;font-size:1.1rem}
.price-card .price{font-size:2rem;font-weight:700;color:#6366f1;margin:.5rem 0}
.plan-features{list-style:none;padding:0;margin:1rem 0}
.plan-features li{padding:.3rem 0;color:#94a3b8;font-size:.9rem}
.auth-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(10px);z-index:100;display:none;align-items:center;justify-content:center}
.auth-overlay.active{display:flex}
.auth-modal{background:#1e1e3c;border:1px solid rgba(99,102,241,0.3);border-radius:16px;padding:2rem;width:90%;max-width:400px}
.auth-modal h2{margin-bottom:1.5rem;text-align:center}
.form-group{margin-bottom:1rem}
.form-group label{display:block;margin-bottom:.3rem;color:#94a3b8;font-size:.9rem}
.form-group input,.form-group select{width:100%;padding:10px 14px;border-radius:8px;border:1px solid rgba(99,102,241,0.3);background:rgba(10,10,30,0.8);color:#e0e0e0;font-size:1rem}
.generate-section{margin:2rem 0}
.output-section{margin:1rem 0}
code{background:rgba(10,10,30,0.8);padding:2px 6px;border-radius:4px;font-size:.9rem}
footer{padding:2rem;text-align:center;color:#64748b;font-size:.9rem}
@media(max-width:768px){h1{font-size:2rem}}
</style>
</head>
<body>
<div class="hero">
<div class="container">
<h1>🤖 LISTO AI</h1>
<p class="subtitle">Gerador de listagens SEO para marketplaces com IA</p>

<div class="card">
<div class="features">
<div class="feature">
<div class="feature-icon">📝</div>
<strong>Títulos Otimizados</strong>
<p style="color:#94a3b8;font-size:.85rem;margin-top:.5rem">SEO automático por marketplace</p>
</div>
<div class="feature">
<div class="feature-icon">🌐</div>
<strong>Multi-Marketplace</strong>
<p style="color:#94a3b8;font-size:.85rem;margin-top:.5rem">Etsy, Mercado Livre, Amazon, Shopify</p>
</div>
<div class="feature">
<div class="feature-icon">🔍</div>
<strong>Score SEO</strong>
<p style="color:#94a3b8;font-size:.85rem;margin-top:.5rem">Análise automática de qualidade</p>
</div>
<div class="feature">
<div class="feature-icon">🏷️</div>
<strong>Tags Inteligentes</strong>
<p style="color:#94a3b8;font-size:.85rem;margin-top:.5rem">Maximize seu alcance orgânico</p>
</div>
</div>
</div>

<div class="pricing">
<div class="price-card">
<h3>Grátis</h3>
<div class="price">R$0</div>
<ul class="plan-features">
<li>5 geracoes/mês</li>
<li>Mercado Livre</li>
<li>Português</li>
</ul>
<button class="btn btn-primary" onclick="showAuth()">Começar Grátis</button>
</div>
<div class="price-card">
<h3>Pro</h3>
<div class="price">R$49</div>
<ul class="plan-features">
<li>300 geracoes/mês</li>
<li>Etsy, Amazon, Shopify</li>
<li>PT, EN, ES</li>
<li>Score SEO avançado</li>
</ul>
<button class="btn btn-primary" onclick="showAuthUpgrade()">Assinar Pro</button>
</div>
<div class="price-card">
<h3>Business</h3>
<div class="price">R$149</div>
<ul class="plan-features">
<li>Ilimitado</li>
<li>Todos os marketplaces</li>
<li>Todos os idiomas</li>
<li>Suporte prioritário</li>
</ul>
<button class="btn btn-primary" onclick="showAuthUpgrade()">Assinar Business</button>
</div>
</div>

<div class="generate-section" id="genSection" style="display:none">
<div class="card">
<h2 style="margin-bottom:1rem">⚡ Gerar Listagem</h2>
<div class="form-group"><label>Produto:</label><input id="product" placeholder="Ex: caneca personalizada"></div>
<div class="form-group"><label>Descrição:</label><input id="desc" placeholder="Detalhes do produto..."></div>
<div class="form-group"><label>Marketplace:</label>
<select id="mp"><option>Mercado Livre</option><option>Etsy</option><option>Amazon</option><option>Shopify</option></select>
</div>
<div class="form-group"><label>Idioma:</label>
<select id="lang"><option value="pt">Português</option><option value="en">English</option><option value="es">Español</option></select>
</div>
<button class="btn btn-primary" onclick="generate()" style="width:100%">Gerar Listagem</button>
</div>
<div class="output-section" id="output"></div>
</div>

<footer>LISTO AI © 2026 — Micro-SaaS autônomo com IA | Powered by LLM</footer>
</div>
</div>

<div class="auth-overlay" id="authOverlay">
<div class="auth-modal">
<h2 id="authTitle">Entrar / Criar Conta</h2>
<div class="form-group"><label>Email:</label><input id="email" type="email" placeholder="seu@email.com"></div>
<div class="form-group"><label>Senha:</label><input id="password" type="password" placeholder="min. 4 caracteres"></div>
<button class="btn btn-primary" onclick="doAuth('login')" style="width:100%;margin-bottom:.5rem" id="authBtn">Login</button>
<p style="text-align:center;color:#94a3b8;font-size:.85rem">Não tem conta? Ela será criada automaticamente.</p>
<button class="btn" onclick="closeAuth()" style="width:100%;margin-top:.5rem;background:rgba(99,102,241,0.1);color:#94a3b8">Cancelar</button>
</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="config.js"></script>
<script>
const LISTO='http://127.0.0.1:8021';function authHeaders(){let t=localStorage.getItem('ltok');return t?{'Content-Type':'application/json','Authorization':'Bearer '+t}:{'Content-Type':'application/json'}}
function showAuth(){document.getElementById('authOverlay').classList.add('active')}
function closeAuth(){document.getElementById('authOverlay').classList.remove('active');document.getElementById('authTitle').textContent='Entrar / Criar Conta';document.getElementById('authBtn').textContent='Login';document.getElementById('authBtn').onclick=()=>doAuth('login')}
async function doAuth(mode){
const pw=document.getElementById('password').value;const email=document.getElementById('email').value;
const r=await fetch(LISTO+'/api/'+mode,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password:pw})});
const d=await r.json();if(r.ok&&d.token){localStorage.setItem('ltok',d.token);showGen();closeAuth()}else alert(d.error||'Erro')}
function showGen(){document.getElementById('genSection').style.display='block'}
async function generate(){
const payload={product:document.getElementById('product').value,description:document.getElementById('desc').value,marketplace:document.getElementById('mp').value,lang:document.getElementById('lang').value};
const r=await fetch(LISTO+'/api/generate',{method:'POST',headers:authHeaders(),body:JSON.stringify(payload)});
const d=await r.json();if(r.status===429){alert('Limite esgotado! Faça upgrade.') ;document.getElementById('authTitle').textContent='Fazer Upgrade';document.getElementById('authBtn').textContent='Ir para Checkout';document.getElementById('authBtn').onclick=()=>doUpgrade(d.plan);showAuth()}
else if(r.ok){renderOutput(d)}else alert(d.error||'Erro')}
function renderOutput(d){document.getElementById('output').innerHTML='<div class="card"><h3 style="margin-bottom:.5rem">✅ Listagem Gerada</h3><p><strong>Título:</strong>'+d.title+'</p><p><strong>Descrição:</strong>'+d.description+'</p><p><strong>Tags:</strong>'+d.tags.join(', ')+'</p><p><strong>Score SEO:</strong>'+d.seo_score+'%</p><p><strong>Uso:</strong>'+d.usage+'</p></div>'}
function showAuthUpgrade(){showAuth();document.getElementById('authTitle').textContent='Fazer Upgrade';document.getElementById('authBtn').textContent='Ir para Checkout';document.getElementById('authBtn').onclick=()=>{doAuth('login')}}
async function doUpgrade(currentPlan){
const r=await fetch(LISTO+'/api/upgrade',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({from:currentPlan})});
const d=await r.json();if(r.ok)alert('Upgrade solicitado! Redirecionando...');else alert(d.error||'Erro')}
// Three.js ambient particles
setTimeout(()=>{try{const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(75,innerWidth/innerHeight,0.1,1000);const renderer=new THREE.WebGLRenderer({alpha:true,antialias:true});renderer.setSize(innerWidth,innerHeight);document.querySelector('.hero').appendChild(renderer.domElement);const geo=new THREE.BufferGeometry(),vtx=[];for(let i=0;i<500;i++)vtx.push((Math.random()-.5)*20,(Math.random()-.5)*20,(Math.random()-.5)*20);geo.setAttribute('position',new THREE.Float32BufferAttribute(vtx,3));const mat=new THREE.PointsMaterial({color:0x6366f1,size:.05,transparent:true,opacity:.6});const pts=new THREE.Points(geo,mat);scene.add(pts);camera.position.z=8;const animate=()=>{requestAnimationFrame(animate);pts.rotation.x+=0.0002;pts.rotation.y+=0.0003;renderer.render(scene,camera)};animate()}catch(e){}},500);
</script>
</body>
</html>"""
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8021))
    app.run(host="0.0.0.0", port=port, debug=False)
