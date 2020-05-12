from flask import Flask, request, Response,session,render_template
from flask_ngrok import run_with_ngrok
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, ConversationState,MemoryStorage,UserState
from botbuilder.schema import Activity
import asyncio
from luis.luisApp import LuisConnect
import os
from logger.logger import Log
import requests
from pymessenger import Bot
from aiohttp import web
from aiohttp.web import Request, Response, json_response


app = Flask(__name__)
#run_with_ngrok(app)
loop = asyncio.get_event_loop()
app.secret_key='12345qwert67890yuiop08641wryip9u8'
bot_settings = BotFrameworkAdapterSettings("", "")
bot_adapter = BotFrameworkAdapter(bot_settings)
ACCESS_TOKEN = "EAAQKRuNwM1kBANHWWYeZBcyScRhI0j7k187stkNMHBYXTzFavNcJaZAi3RvZCVaoNr0PChTEAIirnx9HPI40bduw4X8SzFrsEg9C2fzZAWmZAG2Rk7UimvE1KlZBdEe5RZAeSAQEW6ZBPFjZBZBgV9T1Em8dZCZAQySPSUQlZCGXu0Po6DAZDZD"
# Create MemoryStorage and state
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)
luis_bot_dialog = LuisConnect(CONVERSATION_STATE, USER_STATE)
bot = Bot(ACCESS_TOKEN)



@app.route("/api/messages", methods=["POST","GET"])
def messages():
    if request.method =='GET':
        token_sent = request.args.get("hub.verify_token")
        print("1")
        if token_sent == 'LUIS':
             return request.args.get("hub.challenge")
             print("2")
        return 'Invalid verification token'
    elif request.method =='POST':
        # data = request.get_json()
        # if data['object'] == "page":
            # entries = data['entry']

            # for entry in entries:
                # messaging = entry['messaging']

                # for messaging_event in messaging:

                    # sender = messaging_event['sender']['id']
                    # recipient = messaging_event['recipient']['id']

                    # if messaging_event.get('message'):
                        # if messaging_event['message'].get('text'):
                            # query = messaging_event['message']['text']
                            # bot.send_text_message(sender, query)
        # return "ok", 200
        async def messages(req: Request) -> Response:
            if "application/json" in req.headers["Content-Type"]:
                body = await req.json()
            else:
                return Response(status=415)

            activity = Activity().deserialize(body)
            auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

            response = await ADAPTER.process_activity(activity, auth_header, luis_bot_dialog.on_turn)
            if response:
                return json_response(data=response.body, status=response.status)
            return Response(status=201)
    else:
        if "application/json" in request.headers["content-type"]:
            log=Log()
            request_body = request.json
            print("request_body",request_body)
            user_says = Activity().deserialize(request_body)
            print("user_says",user_says)
            log.write_log(sessionID='session1',log_message="user says: "+str(user_says))
            authorization_header = (request.headers["Authorization"] if "Authorization" in request.headers else "")

            async def call_user_fun(turncontext):
               
                await luis_bot_dialog.on_turn(turncontext)

            task = loop.create_task(
                bot_adapter.process_activity(user_says, authorization_header, call_user_fun)
            )
            loop.run_until_complete(task)
            return ""
        else:
            return Response(status=406)  # status for Not Acceptable




if __name__ == '__main__':
    #app.run(port= 3978)
    app.run()
