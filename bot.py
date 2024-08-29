import requests
import os
from telegram import Update # type: ignore
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler # type: ignore
from datetime import datetime, timedelta 
from aiohttp import web # type: ignore

BOT_TOKEN = os.environ['BOT_TOKEN']
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST', 'your_host_here')  # e.g., 'https://yourapp.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response()

def getrasp(startDate, endDate):
    rasp = requests.get(f"https://www.usue.ru/schedule/?t=0.01851820357425471&action=show&startDate={startDate.strftime('%d.%m.%Y')}&endDate={endDate.strftime('%d.%m.%Y')}&group=%D0%98%D0%92%D0%A2-24-1")
    rjson = rasp.json()
    output = []
    for day in rjson:
        out = f"{day['weekDay']} {day['date']}"
        day["pairs"] = day["pairs"][:8]
        for pair in day["pairs"]:
            if pair['schedulePairs']:
                out += f"\n\n{pair['time']} {pair['N']} пара: {pair['schedulePairs'][0]['subject']} {pair['schedulePairs'][0]['aud']}"
            else:
                out += f"\n\n{pair['time']} {pair['N']} пара: "
        out += '\n'
        output.append(out)
    megaout = ""
    for i in output:
        megaout += i
        megaout += "\n—————————————————————————————————\n"
    return megaout

def logger(update):
    with open("logs.txt", "a+", encoding="UTF-8") as f:
        f.write(f"[{update.effective_user.first_name} | @{update.effective_user.username} | {update.message.date.astimezone()}]   {update.message.text} \n ——————————————— \n")

async def rasp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger(update)
    if context.args:
        try:
            startDate = datetime.strptime(context.args[0], "%d.%m.%Y")
            endDate = startDate + timedelta(days=int(context.args[1]))
            print(startDate, endDate)
        except:
            print("damn bro")
            startDate = datetime.today()
            endDate = startDate + timedelta(days=7)
    else:
        startDate = datetime.today()
        endDate = startDate + timedelta(days=7)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Расписание \n{getrasp(startDate, endDate)}", parse_mode="MarkdownV2")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger(update)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    echo_handler = MessageHandler(filters.TEXT and (~filters.COMMAND), echo)
    rasp_handler = CommandHandler('rasp', rasp)

    application.add_handler(echo_handler)
    application.add_handler(rasp_handler)

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8443)),
        webhook_url=WEBHOOK_URL
    )

    web.run_app(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8443)))
