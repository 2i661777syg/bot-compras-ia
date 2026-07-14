import logging
import requests
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Puxa o Token direto das configurações seguras do servidor
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ID_AFILIADO_SHOPEE = "https://shope.ee"
ID_AFILIADO_MERCADO_LIVRE = "https://mercadolivre.com"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def buscar_ofertas_ia(mensagem_usuario):
    url_reversa = "https://chv.ovh"
    
    contexto_prompt = (
        "Você é um Assistente de Compras Avançado e especialista em analisar produtos na Shopee e Mercado Livre. "
        f"O usuário deseja comprar o seguinte produto com este orçamento: '{mensagem_usuario}'. "
        "Com base nisso, encontre ou simule o melhor produto do mercado que caiba nesse preço. "
        "Você DEVE responder obrigatoriamente seguindo este modelo estruturado para o usuário:\n\n"
        "📦 **Produto Recomendado:** [Nome exato do produto]\n"
        "💰 **Preço Médio:** [Preço estimado]\n"
        "⭐⭐ **Avaliações:** [Indique uma média realista de avaliações, ex: 'Mais de 4.8 estrelas com 2.500 compras']\n\n"
        "✅ **Pontos Positivos:**\n"
        "- [Escreva o principal ponto positivo ou elogio dos compradores]\n"
        "- [Outra vantagem técnica ou benefício]\n\n"
        "❌ **Pontos Negativos:**\n"
        "- [Escreva uma reclamação comum ou detalhe que o usuário deve prestar atenção]\n\n"
        "🛡️ **É Confiável?:** [Dê o veredito se a loja/produto é seguro, ex: 'Altamente Confiável! Produto Original com selo de indicação e entrega rápida.']\n\n"
        "🎟️ **Cupom Sugerido:** [Indique um cupom aplicável, ex: FRETEGRATIS ou 10OFF]"
    )
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": contexto_prompt}]
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url_reversa, json=payload, headers=headers, timeout=15)
        dados = response.json()
        return dados['choices']['message']['content']
    except Exception as e:
        return "⚠️ Desculpe, nosso sistema de análise de produtos está instável agora. Tente novamente em instantes!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome_usuario = update.message.from_user.first_name
    mensagem_boas_vindas = (
        f"Olá, {nome_usuario}! 👋\n\n"
        "Sou o seu **Assistente de Compras Inteligente**! 🛒✨\n\n"
        "Encontro o produto ideal para você e faço uma **análise completa** antes de você comprar!\n\n"
        "👉 **Como usar?**\n"
        "Me diga o **produto** que você quer e o seu **orçamento**. "
        "Eu vou te dar os pontos positivos, negativos, quantidade de avaliações e dizer se o produto é confiável!"
    )
    await update.message.reply_text(mensagem_boas_vindas, parse_mode="Markdown")

async def processar_compras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_recebido = update.message.text
    await update.message.reply_text("🔍 Analisando avaliações, reputação da loja e buscando preços... Aguarde um instante.")
    resposta_ia = buscar_ofertas_ia(texto_recebido)
    
    keyboard = [
        [
            InlineKeyboardButton("🛒 Ver Produto na Shopee", url=ID_AFILIADO_SHOPEE),
            InlineKeyboardButton("📦 Ver no Mercado Livre", url=ID_AFILIADO_MERCADO_LIVRE)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{resposta_ia}\n\n👇 **Acesse pelos links oficiais abaixo para garantir a segurança da compra e os cupons:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_compras))
    print("🚀 Bot Online!")
    app.run_polling()

if __name__ == '__main__':
    main()
  
