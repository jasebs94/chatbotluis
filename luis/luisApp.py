from botbuilder.core import TurnContext,ActivityHandler,MessageFactory,UserState,CardFactory
from botbuilder.ai.luis import LuisApplication,LuisPredictionOptions,LuisRecognizer
import json
from weather.weatherApp import WeatherInformation
from config.config_reader import ConfigReader
from botbuilder.ai.qna import QnAMaker, QnAMakerEndpoint
from botbuilder.schema import ChannelAccount,HeroCard,CardImage,CardAction,ActionTypes,SuggestedActions
from logger.logger import Log
from flask import session,render_template
class LuisConnect(ActivityHandler):
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        self.luis_app_id=self.configuration['LUIS_APP_ID']
        self.luis_endpoint_key = self.configuration['LUIS_ENDPOINT_KEY']
        self.luis_endpoint = self.configuration['LUIS_ENDPOINT']
        self.luis_app = LuisApplication(self.luis_app_id,self.luis_endpoint_key,self.luis_endpoint)
        self.luis_options = LuisPredictionOptions(include_all_intents=True,include_instance_data=True)
        self.luis_recognizer = LuisRecognizer(application=self.luis_app,prediction_options=self.luis_options,include_api_results=True)
        self.qna_knowledge_base_id=self.configuration["QNA_KNOWLEDGEBASE_ID"]
        self.qna_endpoint_key=self.configuration["QNA_ENDPOINT_KEY"]
        self.qna_host=self.configuration["QNA_ENDPOINT_HOST"]
        self.qna_maker = QnAMaker(QnAMakerEndpoint(knowledge_base_id=self.qna_knowledge_base_id,endpoint_key=self.qna_endpoint_key,host=self.qna_host))
        self.log=Log()
        self.IntentIdentified=False
        self.intent='none'
        self.stat='init'
        self.city=""
        self.score=""
        # session['IntentIdentified']=False
        # session['state']="init"
        # session['intent']='none'
 
    def welcome(self):
         return "Hi How can I help you?"
         
    async def __send_intro_card(self, turn_context: TurnContext):
        card = HeroCard(
            title="Welcome to Bot Framework!",
            text="Welcome to Welcome Users bot sample! This Introduction card "
            "is a great way to introduce your Bot to the user and suggest "
            "some things to get them started. We use this opportunity to "
            "recommend a few next steps for learning more creating and deploying bots.",
            images=[CardImage(url="https://aka.ms/bf-welcome-card-image")],
            buttons=[
                CardAction(
                    type=ActionTypes.open_url,
                    title="Get an overview",
                    text="Get an overview",
                    display_text="Get an overview",
                    value="https://docs.microsoft.com/en-us/azure/bot-service/?view=azure-bot-service-4.0",
                ),
                CardAction(
                    type=ActionTypes.open_url,
                    title="Ask a question",
                    text="Ask a question",
                    display_text="Ask a question",
                    value="https://stackoverflow.com/questions/tagged/botframework",
                ),
                CardAction(
                    type=ActionTypes.open_url,
                    title="Learn how to deploy",
                    text="Learn how to deploy",
                    display_text="Learn how to deploy",
                    value="https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-howto-deploy-azure?view=azure-bot-service-4.0",
                ),
            ],
        )

        return await turn_context.send_activity(
            MessageFactory.attachment(CardFactory.hero_card(card))
        )

    def _process_input(self, text: str):
            color_text = "is the best color, I agree."

            if text == "red":
                return f"Red {color_text}"

            if text == "yellow":
                return f"Yellow {color_text}"

            if text == "blue":
                return f"Blue {color_text}"

            return "Please select a color from the suggested action choices"
        
        
    async def _send_suggested_actions(self, turn_context: TurnContext):
            """
            Creates and sends an activity with suggested actions to the user. When the user
            clicks one of the buttons the text value from the "CardAction" will be displayed
            in the channel just as if the user entered the text. There are multiple
            "ActionTypes" that may be used for different situations.
            """

            reply = MessageFactory.text("Confirm the option")

            reply.suggested_actions = SuggestedActions(
                actions=[
                    CardAction(title="YES", type=ActionTypes.im_back, value="YES"),
                    CardAction(title="NO", type=ActionTypes.im_back, value="NO"),
                ]
            )

            return await turn_context.send_activity(reply)
            
             
            
        

    async def on_message_activity(self,turn_context:TurnContext):
        # weather_info=WeatherInformation()
        # print("new session :",session)
        print("1",self.IntentIdentified)
        print("turn_context",turn_context.activity.text)
        if self.IntentIdentified==False:
            luis_result = await self.luis_recognizer.recognize(turn_context)
            result = luis_result.properties["luisResult"]
            print(str(result.intents[0]))
            intentDetails = json.loads((str(result.intents[0])).replace("'", "\""))
            intent = intentDetails.get('intent')
            score = intentDetails.get('score')
            print(intent)
            print(score)
            self.IntentIdentified=True
            self.intent=intent
            self.score=score
        if self.intent == "Welcome" and self.score > 0.5:
            #bot_reply = "Hi How can I help you?"
            #bot_reply = self.welcome()
            await self.__send_intro_card(turn_context)
            bot_reply = ""
            self.IntentIdentified=False 
        elif self.intent == "BookFlight" and self.score > 0.5:
            if self.stat == 'init':
                print(str(result.entities[0]))
                json_str = json.loads((str(result.entities[0])).replace("'", "\""))
                #weather=weather_info.get_weather_info(json_str.get('entity'))
                self.city = json_str.get('entity')
                bot_reply = "should I book a flight to " + self.city +"."
                await turn_context.send_activity(f"{bot_reply}")
                print("1")
                #await self._send_suggested_actions(turn_context)
                print("2")
                text = turn_context.activity.text.lower()
                print("text",text)
                #response_text = self._process_input(text)
                #await turn_context.send_activity(MessageFactory.text(response_text))
                self.stat = 'bookFlight'
                bot_reply = ""
                return await self._send_suggested_actions(turn_context)
            elif self.stat == 'bookFlight':
                if turn_context.activity.text == "YES":
                    bot_reply = "Booked a flight to " + self.city +"."
                    self.stat = 'init'
                else:
                    bot_reply = "cancelled booking procedure."
                    self.stat = 'init'
            self.log.write_log(sessionID='session1',log_message="Bot Says: "+str(bot_reply))
            self.IntentIdentified=False
        elif self.score < 0.5:
            # The actual call to the QnA Maker service.
             bot_reply = ""
             response = await self.qna_maker.get_answers(turn_context)
             if response and len(response) > 0:
               await turn_context.send_activity(MessageFactory.text(response[0].answer))
             else:
               await turn_context.send_activity("No QnA Maker answers were found.")
        await turn_context.send_activity(f"{bot_reply}")
          
          
    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello How can I help you!")