import asyncio
from telegram.ext import Application,CommandHandler,CallbackQueryHandler,ContextTypes, ConversationHandler,MessageHandler,filters
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
import logging

from config import config_load, config_salver

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def send_message(text):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

# Stages
START_MENU, QUEST_MENU,CHANCESYMBOL,CHANCETIMEFRAME,CHANCEEXCHANGE = 0,1,2,3,5
# Callback data
ONE, TWO, THREE, FOUR = 0,1,2,3


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Carrega configurações
    config = config_load()
    context.user_data['symbol'] = config['symbol']
    context.user_data['timeframe'] = config['timeframe']
    context.user_data['exchange'] = config['exchange']
    
    # Obtém informações do usuário de forma segura
    try:
        if update.message:
            user = update.message.from_user
            chat_id = update.message.chat.id
        elif update.callback_query:
            await update.callback_query.answer()  # Importante para callbacks
            user = update.callback_query.from_user
            chat_id = update.callback_query.message.chat.id
        else:
            logger.error("Update sem message ou callback_query")
            return ConversationHandler.END
            
        logger.info("User %s acessou o menu.", user.first_name)
    except Exception as e:
        logger.error(f"Erro ao obter user info: {e}")
        return ConversationHandler.END

    # Cria teclado
    keyboard = [
        [InlineKeyboardButton("🛠 Config", callback_data=str(ONE))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Mensagem personalizada com informações atuais
    text = (
        f"🏠 *Menu Principal*\n\n"
        f"⚙️ Configuração Atual:\n"
        f"• Ativo: `{context.user_data['symbol']}`\n"
        f"• Timeframe: `{context.user_data['timeframe']}`\n"
        f"• Exchange: `{context.user_data['exchange']}`"
    )

    # Envia ou edita a mensagem conforme o caso
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="MarkdownV2"
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="MarkdownV2"
            )
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return ConversationHandler.END

    return START_MENU

# Menu de Configuraçao
async def config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    
    keyboard = [
        [
            InlineKeyboardButton("Trocar Ativo", callback_data=str(ONE)),
            InlineKeyboardButton("Trocar Timeframe", callback_data=str(TWO)),
            InlineKeyboardButton("Trocar Exchange", callback_data=str(THREE))
        ],
        [InlineKeyboardButton("← Voltar", callback_data=str(FOUR))]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🛠 *Menu de Configuração*\n\n"
                                  "👀 *Monitoraçao Atual:*\n\n"
                                    f" *Ativo*: {context.user_data['symbol']}\n"
                                    f" *Timeframe*:{context.user_data['timeframe']}\n"
                                    f" *Exchange*:{context.user_data['exchange']}\n"
                                    "",
                                parse_mode="MarkdownV2"
                                , reply_markup=reply_markup)
    return QUEST_MENU

# Menu Configuraçao > Trocar Ativo
async def chanceSymbol_quest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Qual o Símbolo do Ativo que quer monitorar?")
    return CHANCESYMBOL

# Menu Configuraçao > Trocar Ativo > OK!  
async def chanceSymbol_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Símbolo inválido. Tente novamente.")
        return CHANCESYMBOL
        
    symbol = update.message.text.upper()
    context.user_data['symbol'] = symbol
    
    c=config_load()
    c['symbol'] = symbol
    config_salver(c)
    
    await update.message.reply_text(f"✅ Ativo configurado: {symbol}!")
    return await start(update,context)

# Menu Configuraçao > Trocar timeframe
async def chanceTimeframe_quest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Qual timeframe quer monitorar?\n"
                                    "*📊 Tabela de Timeframes* \n\n"
                                    "```\n"
                                    "┌──────────┬───────────────┐\n"
                                    "│ Símbolo  │ Descrição     │\n"
                                    "├──────────┼───────────────┤\n"
                                    "│ 1m       │ 1 minuto      │\n"
                                    "│ 2m       │ 2 minutos     │\n"
                                    "│ 5m       │ 5 minutos     │\n"
                                    "│ 15m      │ 15 minutos    │\n"
                                    "│ 4h       │ 4 horas       │\n"
                                    "│ 8h       │ 8 horas       │\n"
                                    "│ d        │ diário        │\n"
                                    "│ s        │ semanal       │\n"
                                    "└──────────┴───────────────┘\n"
                                    "```",
                                parse_mode="MarkdownV2")
    return CHANCETIMEFRAME

# Menu Configuraçao > Trocar timeframe > OK!  
async def chanceTimeframe_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Timeframe inválido. Tente novamente.")
        return CHANCETIMEFRAME
        
    timeframe = update.message.text
    context.user_data['timeframe'] = timeframe
    
    c=config_load()
    c['timeframe'] = timeframe
    config_salver(c)
    
    await update.message.reply_text(f"✅ Timeframe configurado: {timeframe}!")
    return await start(update, context)

# Menu Configuraçao > Trocar exchange
async def chanceExchange_quest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Qual exchange receber os dados?\n"
                                    "*📊 Tabela de Exchanges* \n\n"
                                    "```\n"
                                    "┌──────────┐\n"
                                    "│ Exchanges│\n"
                                    "├──────────┤\n"
                                    "│ bitget   │\n"
                                    "│ binance  │\n"
                                    "└──────────┘\n"
                                    "```",
                                parse_mode="MarkdownV2")
    return CHANCEEXCHANGE

# Menu Configuraçao > Trocar exchange > OK!  
async def chanceExchange_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Exchange inválido. Tente novamente.")
        return CHANCEEXCHANGE
        
    exchange = update.message.text
    context.user_data['exchange'] = exchange
    
    c=config_load()
    c['exchange'] = exchange
    config_salver(c)
    
    await update.message.reply_text(f"✅ Exchange configurado: {exchange}!")
    return await start(update, context)


def main() -> None:
    """Run the bot."""
    app = Application.builder().token(TOKEN).build()

   
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        START_MENU: [CallbackQueryHandler(config, pattern="^" + str(ONE) + "$")],
        QUEST_MENU: [
            CallbackQueryHandler(chanceSymbol_quest, pattern="^" + str(ONE) + "$"),
            CallbackQueryHandler(chanceTimeframe_quest, pattern="^" + str(TWO) + "$"),
            CallbackQueryHandler(chanceExchange_quest, pattern="^" + str(THREE) + "$"),
            CallbackQueryHandler(start, pattern="^" + str(FOUR) + "$")
        ],
        CHANCESYMBOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, chanceSymbol_response)],
        CHANCETIMEFRAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, chanceTimeframe_response)],
        CHANCEEXCHANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, chanceExchange_response)]
    },
    fallbacks=[CommandHandler('start', start)],
    # REMOVA per_message=False (deixe o padrão True)
)
        
    app.add_handler(conv_handler)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()