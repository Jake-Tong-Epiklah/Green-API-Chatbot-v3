from datetime import datetime
from whatsapp_api_client_python import API as API
from checklistbot import main as checklistbot

from crndbot import execute as crndbot_with_para
from quizbot import main as quizbot
from repeatedbot import main as repeatedbot
from timeattendancebot import main as timeattendance

import os
import json

global feeds
feeds=[]

# For Green API
ID_INSTANCE = '1101812945'
API_TOKEN_INSTANCE = '9b9fbd117f8b4d8686bf10e8adf5eb9ca76d95d725b04c0295'

greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)
def json_saving(fileName, d_type, d_value,status):    
    with open(fileName, mode='w', encoding='utf-8') as feedsjson:
        entry = {d_type: d_value}           
        feeds.append(entry)
        feed = {'data': feeds, 'status': status}
        json.dump(feed, feedsjson)


def json_saving_status(filename, status):        
    with open(filename, mode='w', encoding='utf-8') as feedsjson:
        feed = {'data': [], 'status': status}
        json.dump(feed, feedsjson)

def send_response(chatId, body):
    greenAPI.sending.sendMessage(chatId, body)
    return
def main():
    greenAPI.webhooks.startReceivingNotifications(onEvent)

def onEvent(typeWebhook, body):
    if typeWebhook == 'incomingMessageReceived':
        sender_data, message_data = onIncomingMessageReceived(body)
        print(sender_data,'\n', message_data)
        customer_phone = sender_data['sender']
        phone = customer_phone.split("@")[0]
        # print(phone)
        customer_name = sender_data['senderName']
        fileName = customer_name + "_" + phone + "_main.json"
        msg_type = message_data['typeMessage']
        responded = False
        if msg_type == "textMessage":
            incoming_msg = message_data['textMessageData']['textMessage'].lower()
            if os.path.exists(fileName):
                if os.stat(fileName).st_size != 0 :
                    with open(fileName) as f:
                        data = json.load(f)
                        currentstatus = data['status']                    
                else:
                    currentstatus = -1
                    json_saving_status(fileName,-1)
            if os.path.exists(fileName):        
                if currentstatus == 1: 
                    with open(fileName) as f:
                        data = json.load(f)
                        listdata = data['data']
                        for list in listdata:
                            if 'Chosen bot' in list:
                                chosen_bot = list['Chosen bot']        


            if os.path.exists(fileName) == False:
                currentstatus = -1
                json_saving_status(fileName,-1)

            if incoming_msg == 'start' or incoming_msg == 'hi' or incoming_msg == 'hello':
                global feeds
                feeds.clear()              
                reply = f"Hello {customer_name}! Welcome to Salmon.sg chatbot.\nPlease send *ONE number* to select the bot you want to do.\n1. Time Attendance chatbot\n2. Checklist Chatbot \n3. Ticketing System Chatbot\n4. Quiz Chatbot\n5. Repeating Order Chatbot\n6. Cancel"        
                send_response(customer_phone, reply)
                responded = True
                json_saving_status(fileName,0)

            if currentstatus == 0 and incoming_msg == "1" :
                body = "Please send *start* or *hi* or *hello* to start using our bot"
                send_response(customer_phone,body)
                print("mainbot")
                #timeattendance()
                json_saving(fileName,"Chosen bot",incoming_msg,1)
                responded = True

            if currentstatus == 0 and incoming_msg == "2" :
                body = "Please send *start* or *hi* or *hello* to start using our bot"
                send_response(customer_phone,body)
                print("mainbot")
                checklistbot()
                json_saving(fileName,"Chosen bot",incoming_msg,1)
                responded = True
            if currentstatus == 0 and incoming_msg == "3" :
                body = "Please send *start-crnd* to start using our bot"
                send_response(customer_phone,body)
                json_saving(fileName,"Chosen bot",incoming_msg,1)
                print("mainbot")
                responded = True    
            if currentstatus == 0 and incoming_msg == "4" :
                body = "Please send *start* or *hi* or *hello* to start using our bot"
                send_response(customer_phone,body)
                json_saving(fileName,"Chosen bot",incoming_msg,1)
                print("mainbot")
                quizbot()
                responded = True    
            if currentstatus == 0 and incoming_msg == "5" :
                body = "Please send *start* or *hi* or *hello* to start using our bot"
                send_response(customer_phone,body)
                json_saving(fileName,"Chosen bot",incoming_msg,1)
                print("mainbot")
                repeatedbot()
                responded = True
        
            if currentstatus == 0 and incoming_msg == "6":
                reply = "Thanks for using our chatbot"
                send_response(customer_phone, reply)
                responded = True
            if currentstatus == 1:
                if chosen_bot == "3":
                    print("CRND Bot start")
                    crndbot_with_para(incoming_msg,customer_name,customer_phone)
                    responded = True
            if responded == False:
                reply= "Unrecognized input. Send a number in the list."
                send_response(customer_phone, reply)           
    

            


def onIncomingMessageReceived(body):
   idMessage = body['idMessage']
   eventDate = datetime.fromtimestamp(body['timestamp'])
   senderData = body['senderData']
   messageData = body['messageData']
   return senderData, messageData



if __name__ == "__main__":
   main()