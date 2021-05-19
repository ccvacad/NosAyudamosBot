import os
import sys
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)
from helper import gsheet_helper

TOKEN = os.getenv("TOKEN")
MODE = os.getenv("MODE")
gsconn = gsheet_helper()

# Stages
FIRST, SECOND = range(2)
ASISTENCIAS = {
    "jur": "Asistencia Jurídica",
    "sal": "Asistencia Salud mental y física",
    "otr": "Asistencia Otras ayudas"
}

def start(update: Update, _:CallbackContext) -> int:
    keyboard = [
        [
            InlineKeyboardButton("Jurídica", callback_data="jur"),
            InlineKeyboardButton("Salud mental y física", callback_data="sal")
        ],
        [
            InlineKeyboardButton("Otras ayudas", callback_data="otr")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    tiosButtons = InlineKeyboardMarkup([[InlineKeyboardButton("El chat de los tíos y tías", callback_data="chat#1#True")]])
    update.message.reply_text(f"""*Nos ayudamos* 

*Directorio Nacional de Asistencia*

Directorio de personas naturales y colectivos que han ofrecido asistencia gratuita en diversos temas a las personas afectadas durante el Paro Nacional 2021 en Colombia\.

¿Necesitas apoyo?

Consulta el directorio de asistencia\.""", parse_mode="MarkdownV2", reply_markup=reply_markup)
    update.message.reply_text(f"""*El chat de los tíos y tías*

Aquí encontrarás recursos que explican de forma didáctica y certera lo que está sucediendo en el país y algunas temáticas asociadas\. Ideal para los chats con familiares que necesitan un poco más de información\.""", 
    reply_markup=tiosButtons, parse_mode="MarkdownV2")
    return FIRST

def asistencia(update: Update, _:CallbackContext) -> int:
    update = update.callback_query
    update.answer()
    items = gsconn.get_cities()
    keyboard = []
    for i in items:
        i = "Otras" if i == "En cualquier ubicación" else i
        keyboard.append([InlineKeyboardButton(i, callback_data='{"category": "'+ update.data +'", "city": "' + i + '"}' )])
    keyboard.append([InlineKeyboardButton("Todas", callback_data='{"category": "'+ update.data +'", "city": "Todas"}' )])
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data='cancelar')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(f"*{ASISTENCIAS[update.data]}*", parse_mode="MarkdownV2", reply_markup=reply_markup)
    
    return SECOND

def resultado(update: Update, _:CallbackContext) -> int:
    update = update.callback_query
    update.answer()
    message = (json.loads(update.data))
    message["city"] = "En cualquier ubicación" if message["city"] == "Otras" else message["city"]
    items = gsconn.get_asistencia( message["category"]) if message["city"] == "Todas" else gsconn.get_asistencia(message["category"], message["city"],)
    update.edit_message_text(
        text=f"*{ASISTENCIAS[message['category']]} en  {message['city']}*", parse_mode="MarkdownV2")
    for index, row in items.iterrows():
        name = row["NAME"].replace(".", "\.").replace("-", "\-").replace(")", "\)").replace("(", "\(")
        description = str(row["DESCRIPTION"]).replace(".", "\.").replace("-", "\-").replace(")", "\)").replace("(", "\(")
        contact = str(row["CONTACT"]).replace(".", "\.").replace("-", "\-").replace(")", "\)").replace("(", "\(")
        update.message.reply_text(f"""
                *{name}*
{description}
        _{contact}_
        """, parse_mode="MarkdownV2")
    
    update.message.reply_text(f"""Seleccione de nuevo alguna opción o /start para volver a iniciar y mantener los resultados""")
    return FIRST

def chat(update: Update, _:CallbackContext) -> int:
    update = update.callback_query
    update.answer()
    keyboard = [[]]
    items = gsconn.get_chat()
    pages = len(items)
    page = int(update.data.split('#')[1])
    if page > 1:
        previus_page = page - 1
        keyboard[0].append(InlineKeyboardButton("<<", callback_data='chat#1#False'))
        keyboard[0].append(InlineKeyboardButton("<", callback_data='chat#' + str(previus_page) + '#False'))
    keyboard[0].append(InlineKeyboardButton(page, callback_data='chat#' + str(page) + '#False'))
    if page < pages:
        next_page =  page + 1
        keyboard[0].append(InlineKeyboardButton(">", callback_data='chat#' + str(next_page) + '#False'))
        keyboard[0].append(InlineKeyboardButton(">>", callback_data='chat#' + str(pages) + '#False'))
    
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data='cancelar')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    name = items[page-1]['NAME'].replace(".", "\.").replace("-", "\-").replace(")", "\)").replace("(", "\(")
    description =  items[page-1]['DESCRIPTION'].replace(".", "\.").replace("-", "\-").replace(")", "\)").replace("(", "\(")
    url = items[page-1]['LINK'].replace(".", "\.").replace("-", "\-").replace(")", "\)").replace("(", "\(")
    if update.data.split('#')[2] == "True":
        update.message.reply_text(f"""*El chat de los tíos y tías*
        
    *{name}*

    [{description}]({url})
    
    """, parse_mode="MarkdownV2", reply_markup=reply_markup)
    else:
        update.edit_message_text(f"""*El chat de los tíos y tías*
        
    *{name}*

    [{description}]({url})
    
    """, parse_mode="MarkdownV2", reply_markup=reply_markup)

    return FIRST

def cancelar(update: Update, _:CallbackContext) -> int:
    update = update.callback_query
    update.answer()
    update.message.reply_text(f"""Seleccione de nuevo alguna opción o /start para volver a iniciar y mantener los resultados""")
    return FIRST


def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                CallbackQueryHandler(start, pattern='^' + "start" + '$'),
                CallbackQueryHandler(asistencia, pattern='^' + "jur" + '$'),
                CallbackQueryHandler(asistencia, pattern='^' + "sal" + '$'),
                CallbackQueryHandler(asistencia, pattern='^' + "otr" + '$'),
                CallbackQueryHandler(chat, pattern='^chat#'),
                CallbackQueryHandler(cancelar, pattern='cancelar')
            ],
            SECOND: [
                CallbackQueryHandler(resultado, pattern='^' + '{"category": "jur", "city": '),
                CallbackQueryHandler(resultado, pattern='^' + '{"category": "sal", "city": '),
                CallbackQueryHandler(resultado, pattern='^' + '{"category": "otr", "city": '),
                CallbackQueryHandler(cancelar, pattern='cancelar')
            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)

    if MODE == "dev":
        updater.start_polling()
        updater.idle()
    elif MODE == "prod":
        PORT = int(os.environ.get("PORT", "443"))
        print("--------->", PORT)
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
        updater.idle()
        # updater.bot.set_webhook(f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
    else:
        print("No se especifico MODE")
        sys.exit()

if __name__ == '__main__':
    main()