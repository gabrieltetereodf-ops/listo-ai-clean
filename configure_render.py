"""
LISTO AI - Configuração para Render.com (hosting gratuito)
"""
import os

# Esta funcao deve ser chamada durante deploy (Render injeta env vars)
def configure_for_render():
    """Prepara o ambiente para hospedagem no Render."""
    
    # Verifica se tem chave Stripe configurada via env var
    stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")
    
    if not stripe_key:
        print("⚠️ AVISO: STRIPE_SECRET_KEY nao definida.")
        print("   Sem ela, o checkout roda em modo simulado (R$0).")
        print("   Para cobrar de verdade:")
        print("   1. Vá ao Render → Settings → Environment Variables")
        print("   2. Adicione STRIPE_SECRET_KEY com valor:")
        print(f"      sk_test_51TxD4d...  (ou a chave real production)")
        print("   3. Redeploy do serviço")
        return False
    
    # Se chegou aqui, Stripe está configurado
    print(f"✅ Stripe configured (key starts with: {stripe_key[:8]}...)")
    print("   ⚠️ Nota: para cobrar em BRL (R$), crie Products/Prices no Stripe Dashboard:")
    print("   1. Stripe Dashboard → Products → Create Product")
    print("   2. Nome: LISTO Pro, Preço: R$49/mês (BRL ou USD ~$9)")
    print("   3. Copie o price_id e use no checkout real")
    print("   4. Para agora: modo simulado funciona p/ testar o fluxo completo")
    return True

if __name__ == "__main__":
    configure_for_render()
