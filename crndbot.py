from datetime import datetime
from whatsapp_api_client_python import API as API

from pickle import TRUE
from urllib import response
import requests
import sys
import base64
import json
from requests.exceptions import ConnectTimeout
import time
import asyncio
import os
import random
import array

# For Green API
ID_INSTANCE = '1101812945'
API_TOKEN_INSTANCE = '9b9fbd117f8b4d8686bf10e8adf5eb9ca76d95d725b04c0295'

greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)

import xmlrpc.client

url = "https://fsm-demo.helpbots.sg"
db = "fsm-demo.helpbots.sg"
username = 'admin'
password = 'Admin@1234'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))


uid = common.authenticate(db, username, password, {})
global feeds
feeds=[]

global contactid
global customerpassword
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
def create_contact_odoo(jsondata):
    new_request = models.execute_kw(db, uid, password, 'res.partner', 'create', [jsondata])
    print("new request:", new_request)
    return new_request

def create_crm_lead_odoo(jsondata):
    new_request = models.execute_kw(db, uid, password, 'crm.lead', 'create', [jsondata])
    print("new request:", new_request)
    return new_request
def create_request_odoo(jsondata):
    new_request = models.execute_kw(db, uid, password, 'request.request', 'create', [jsondata])
    print(new_request)
    return new_request

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
def create_response(fileName):
    message_array = ["1. Report a fault on a PC", "2. Report a fault on a printer", "3. Report a fault on the Internet"]
    selected_message_array = ["1. Report a fault on a PC (Selected)", "2. Report a fault on a printer (Selected)", "3. Report a fault on the Internet (Selected)"]
    
    request_descriptionlist = []
    
    with open(fileName) as f:
        data = json.load(f)
        listdata = data['data']
        print(listdata)
    for list in listdata:
        if 'Request Description' in list:
            request_description = list['Request Description']
            if ',' in request_description: 
                split_request_description = request_description.split(",")
                for split in split_request_description:
                    request_descriptionlist.append(split)
            else:         
                request_descriptionlist.append(request_description)
    body = "Is there anything else you want to request? Please send *ONE* number to select the request type.\n"
    print(request_descriptionlist)
    print(type(request_descriptionlist))
    if "1" in request_descriptionlist:
        body += selected_message_array[0] +"\n"
    else: 
        body +=message_array[0] +"\n"
    if "2" in request_descriptionlist:
        body += selected_message_array[1] +"\n"
    else: 
        body +=message_array[1] +"\n"
    if "3" in request_descriptionlist:
        body += selected_message_array[2] +"\n"
    else: 
        body +=message_array[2] +"\n"
    
    body += "4. Finish the request\n5. Restart the whole process"
    return body


def generate_password():
    MAX_LEN = 12
    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] 
    LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                        'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                        'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                        'z']
    
    UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                        'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q',
                        'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                        'Z']
    
    SYMBOLS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>',
            '*', '(', ')', '<']
    
    # combines all the character arrays above to form one array
    COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS + SYMBOLS
    
    # randomly select at least one character from each character set above
    rand_digit = random.choice(DIGITS)
    rand_upper = random.choice(UPCASE_CHARACTERS)
    rand_lower = random.choice(LOCASE_CHARACTERS)
    rand_symbol = random.choice(SYMBOLS)
    
    # combine the character randomly selected above
    # at this stage, the password contains only 4 characters but
    # we want a 12-character password
    temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol
    
    
    # now that we are sure we have at least one character from each
    # set of characters, we fill the rest of
    # the password length by selecting randomly from the combined
    # list of character above.
    for x in range(MAX_LEN - 4):
        temp_pass = temp_pass + random.choice(COMBINED_LIST)
    
        # convert temporary password into array and shuffle to
        # prevent it from having a consistent pattern
        # where the beginning of the password is predictable
        temp_pass_list = array.array('u', temp_pass)
        random.shuffle(temp_pass_list)
    
    # traverse the temporary password array and append the chars
    # to form the password
    password = ""
    for x in temp_pass_list:
            password = password + x
    return password
# def main():
#     greenAPI.webhooks.startReceivingNotifications(onEvent)     
#     return
def execute(incoming_msg,customer_name,customer_phone):
    responded = False
    phone = customer_phone.split("@")[0]
    fileName = customer_name + "_" + phone + "-crnd.json"
    mainfileName = customer_name + "_" + phone + "_main.json"
    if os.path.exists(fileName):
            if os.stat(fileName).st_size != 0 :
                with open(fileName) as f:
                    data = json.load(f)
                    currentstatus = data['status']                    
            else:
                currentstatus = -1
                json_saving_status(fileName,-1)
        

    if os.path.exists(fileName) == False:
        currentstatus = -1
        json_saving_status(fileName,-1)
    
    print(customer_phone)
    global feeds
    global contactid
    global customerpassword
    print("message received")
    multipleoption = False

    if os.path.exists(fileName):
        if os.stat(fileName).st_size != 0 :
            with open(fileName) as f:
                data = json.load(f)
                currentstatus = data['status']
            if currentstatus == 6:
                global feeds
                feeds.clear()
                json_saving_status(fileName,-1)
        else:
            json_saving_status(fileName,-1)
        
    else:
        json_saving_status(fileName,-1)

    if 'start-crnd' in incoming_msg:
        json_saving_status(fileName,0)
        reply = "Hi " + customer_name +"! Welcome to Salmon.sg ticketing system chatbot\nPlease send *ONE* number to select what you want to do.\n1. Create a new request\n2. Cancel"
        send_response(customer_phone,reply)
        responded = True

    if os.path.exists(fileName):
        if os.stat(fileName).st_size != 0 :
            with open(fileName) as f:
                data = json.load(f)
                currentstatus = data['status']
            
    if currentstatus == -1:
        reply = "Hello Friends! Welcome to Salmon.sg\nIf you want to start our CRND Chatbot please enter *start* or *hi* or *hello*."
        send_response(customer_phone,reply)
        responded = True

    
    if currentstatus == 0 and "1" in incoming_msg:
        new_request = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[['phone','=',customer_phone]]],{'fields': ['id']})
        if len(new_request) >0:
            for item in new_request:
                if 'id' in item:
                    global contactid
                    contactid =  item['id']
                    print("contact ID: "+str(contactid))
            req_name_string = "Please send *ONE* number to select the request type.\n1. Report a fault on a PC\n2. Report a fault on a printer\n3. Report a fault on the Internet"
            json_saving_status(fileName,3)
        else:
            req_name_string = "Please provide your *Full Name* (Eg. John Tan)"
            json_saving_status(fileName, 1)
        send_response(customer_phone,req_name_string)
        responded = True
    if currentstatus == 0 and "2" in incoming_msg:
        reply="Thank you for using our service, salmon.sg!"
        send_response(customer_phone,reply)
        json_saving_status(fileName, -1)
        responded = True
    elif currentstatus  != 0:
        if currentstatus == 1:
            reply="Please enter *Email* (Eg. abc@example.com)"
            send_response(customer_phone,reply)
            #DO SOMETHINGS
            json_saving(fileName,'Name',incoming_msg,2)
            responded = True
        if currentstatus == 2 and "@" in incoming_msg:                        
            #DO SOMETHINGS                
            json_saving(fileName,'Email',incoming_msg,3)
            for item in data['data']:
                if 'Name' in item:
                    customername=item['Name']
            new_request = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[['name', '=', customername],['login','=',incoming_msg]]],{'fields': ['id']})
            if len(new_request) >0:
                for item in new_request:
                    if 'id' in item:
                        contactid =  item['id']
                        print(contactid)
            else:    
                customerpassword = generate_password()
                jsondata ={
                    'name': customername,
                    'login': incoming_msg,
                    'phone': customer_phone,
                    'password': customerpassword,
                    'email': incoming_msg
                }
                new_request = models.execute_kw(db, uid, password, 'res.users', 'create', [jsondata])                            
                contactid = new_request
                replypassword="Your new account detail is:\nUsername: " + incoming_msg+"\nPassword: " + customerpassword +"\nPlease change your password as soon as possible."
                send_response(customer_phone,replypassword)
                
            reply="Please send *ONE* number to select the request type\n1. Report a fault on a PC\n2. Report a fault on a printer\n3. Report a fault on the Internet\n4. Finish the request\n5. Restart the whole process"
            send_response(customer_phone,reply)
            responded = True
        if currentstatus == 2 and "@" not in incoming_msg:
            reply="Please send an email that is in the correct format (abc@example.com)"
            send_response(customer_phone,reply)
            json_saving_status(fileName, -1)
            responded = True
        if currentstatus == 3:
            seperated_incoming_msg = incoming_msg.split(',')
            print(seperated_incoming_msg)
            for word in seperated_incoming_msg:
                if len(word) > 1:
                    multipleoption = True
            if multipleoption == False:
                if '1' in incoming_msg or '2' in incoming_msg or '3' in incoming_msg:       
                    print(currentstatus)
                    print("start status 3")                
                    json_saving(fileName,'Request Description',incoming_msg,4)
                    reply=create_response(fileName)
                    send_response(customer_phone,reply)
                    print("currentstatus: " + str(currentstatus))
                    #DO SOMETHINGS                    
                    responded = True    
        if currentstatus == 4 and '4' not in incoming_msg and '5' not in incoming_msg:  
            seperated_incoming_msg = incoming_msg.split(',')
            print(seperated_incoming_msg)
            for word in seperated_incoming_msg:
                if len(word) > 1:
                    multipleoption = True
            if multipleoption == False:
                print(currentstatus)
                print("start status 4")
                json_saving(fileName,'Request Description',incoming_msg,4)
                reply=create_response(fileName)
                print("status 4")
                send_response(customer_phone,reply)
                print('end status 4')
                print("currentstatus: " + str(currentstatus))
                #DO SOMETHINGS
                
                responded = True
        
        elif currentstatus == 4 and '4' in incoming_msg and '5' in incoming_msg:
            seperated_incoming_msg = incoming_msg.split(',')
            print(seperated_incoming_msg)
            for word in seperated_incoming_msg:
                if len(word) > 1:
                    multipleoption = True
            if multipleoption == False:
                reply="You can only choose either option 4 or option 5 at the same time, please try again.\n Please send *ONE* number to select the request type.\n1. Report a fault on a PC\n2. Report a fault on a printer\n3. Report a fault on the Internet\n4. Finish the request\n5. Restart the whole process"
                send_response(customer_phone,reply)
                #DO SOMETHINGS
                json_saving(fileName,'Request Description',"",4)
                responded = True
            
        else:
            if currentstatus == 4 and '5' in incoming_msg:
                seperated_incoming_msg = incoming_msg.split(',')
                print(seperated_incoming_msg)
                for word in seperated_incoming_msg:
                    if len(word) > 1:
                        multipleoption = True
                if multipleoption == False:
                    reply= "Hi " + customer_name +"! Welcome to Salmon.sg ticketing system chatbot\nPlease send *ONE* number to select what you want to do.\n1. Create a new request\n2. Cancel"
                    send_response(customer_phone,reply)
                    #DO SOMETHINGS                        
                    feeds.clear()
                    print(feeds)
                    json_saving_status(fileName,0)
                    responded = True
            if currentstatus == 4 and '4' in incoming_msg:     
                seperated_incoming_msg = incoming_msg.split(',')
                print(seperated_incoming_msg)
                for word in seperated_incoming_msg:
                    if len(word) > 1:
                        multipleoption = True
                if multipleoption == False:                  
                    des = ""        
                    json_saving(fileName,'Request Description',incoming_msg,5)            
                    for item in data['data']:
                        if 'Request Description' in item:
                            if ',' in item['Request Description']:
                                word = item['Request Description'].split(",")
                                for option in word:
                                    if option == '1':
                                        des += 'Request a fault on a PC<br>'
                                    if option == '2':
                                        des += 'Request a fault on a Printer<br>'
                                    if option == '3':
                                        des += 'Request a fault on the Internet<br>'     
                            else:
                                if item['Request Description'] == '1':
                                    des += 'Request a fault on a PC<br>'
                                if item['Request Description'] == '2':
                                    des += 'Request a fault on a Printer<br>'
                                if item['Request Description'] == '3':
                                    des += 'Request a fault on the Internet<br>'
                    print(des)
                    new_partner = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[['id', '=', contactid]]],{'fields': ['partner_id']})
                    partnerid = new_partner[0]['partner_id'][0]
                    send_data = {
                        'type_id':1,
                        'request_text': des,
                        'partner_id': partnerid
                    }
                    order_id = create_request_odoo(send_data)
                    link = "https://fsm-demo.helpbots.sg/requests/request/" + str(order_id)
                    reply = "Thank you for your submission, your request number is "+ str(order_id) +"\nHere's the link to your request: "+ link +"\nPlease send *ONE* number to select what you want to do next.\n1. Create a new request\n2. End the session\n3. Reset your account detail\n\n9. Contact Us if you are interested in our other services"
                    send_response(customer_phone,reply)
                    feeds.clear()
                    print(feeds)                    
                    responded = True
        if currentstatus == 5 and incoming_msg == '1':
            reply="Please send *ONE* number to select the request type\n1. Report a fault on a PC\n2. Report a fault on a printer\n3. Report a fault on the Internet"
            send_response(customer_phone,reply)
            #DO SOMETHINGS
            feeds.clear()
            print(feeds)
            json_saving_status(fileName,3)                        
            responded = True
        if currentstatus == 5 and incoming_msg == '2':
            reply="Hello "+customer_name+"! Welcome to Salmon.sg chatbot.\nPlease send *ONE number* to select the bot you want to do.\n1. Time Attendance chatbot\n2. Checklist Chatbot \n3. Ticketing System Chatbot\n4. Quiz Chatbot\n5. Repeating Order Chatbot\n6. Cancel"
            send_response(customer_phone,reply)
            #DO SOMETHINGS
            json_saving_status(mainfileName,0)
            os.remove(fileName)                      
            responded = True
        if currentstatus == 5 and incoming_msg == '3':
            reply="If you can, please search on the previous conversation for your account detail\nIf you want to reset your account detail, go to https://ticketing-demo.salmon.sg/web/login and click on *reset password*, we will send you an email to reset your password.\nPlease send *ONE* number to select what you want to do next.\n1. Create a new request\n2. End the session"
            send_response(customer_phone,reply)
            #DO SOMETHINGS
            
            json_saving_status(fileName,0)                        
            responded = True
            
        if currentstatus == 5 and incoming_msg == "9":
            reply = "Please enter your *company's name*"
            send_response(customer_phone,reply)
            json_saving_status(fileName,12)
            responded = True
        if currentstatus == 12:
            reply = "Please enter the product that you're interested in:\n1. WhatsApp Feedback System\n2. WhatsApp to Customer Service System\n3. WhatsApp to Ticketing System\n4. WhatsApp to Field Service Management System\n5. WhatsApp to Spreadsheet"
            send_response(customer_phone,reply)
            
            json_saving(fileName,"Company",incoming_msg,13)
            responded = True
        if currentstatus == 13:
            reply =   "Thank you for your interest with salmon.sg, we will contact you soon.\nSend *start* if you want to create a new request"
            send_response(customer_phone,reply)
            
            with open(fileName) as f:
                data = json.load(f)
                listdata = data['data']
            for item in listdata:
                if 'Company' in item:
                    usercompany = item['Company']
            if incoming_msg == "1":
                product_interested = "WhatsApp Feedback System"
            elif incoming_msg == "2":
                product_interested = "WhatsApp to Customer Service System"
            elif incoming_msg == "3":
                product_interested = "WhatsApp to Ticketing System"
            elif incoming_msg == "4":
                product_interested = "WhatsApp to Field Service Management System"
            elif incoming_msg == "5":
                product_interested = " WhatsApp to Spreadsheet"
            userdata = {
                'name': customer_name,
                'phone': customer_phone,
                'comment' : "company Name:" + usercompany +"\n Prouct Interested: " + product_interested
                }
            partner_id = create_contact_odoo(userdata)
            send_data = {
                    'name': customer_name + " Lead",
                    'partner_id': partner_id,
                    'contact_name' : customer_name,
                    'phone': customer_phone,
                    'description' : "company Name:" + usercompany +"\n Prouct Interested: " + product_interested
                }
            print(send_data)
            create_crm_lead_odoo(send_data)
            json_saving(fileName,"Product Interested",incoming_msg,14)
            responded = True
    print(currentstatus)
    print(responded)    
    if not responded:
        #message.body('Incorrect request format. Please enter in the correct format')
        reply= "Invalid input, please send the correct option provided."
        send_response(customer_phone,reply)
    return        
# def onEvent(typeWebhook, body):
    
#     if typeWebhook == 'incomingMessageReceived':
#         sender_data, message_data = onIncomingMessageReceived(body)
#         print(sender_data,'\n', message_data)
#         customer_phone = sender_data['sender']
#         phone = customer_phone.split("@")[0]
#         print(phone)
#         customer_name = sender_data['senderName']
#         fileName = customer_name + "_" + phone + "-crnd.json"
#         msg_type = message_data['typeMessage']
#         print(msg_type)
#         responded = False
#         if msg_type == "incoming_msgMessage":
#             print(message_data)
#             incoming_msg = message_data['incoming_msgMessageData']['incoming_msgMessage'].lower()
#             responded = False
#         if  msg_type == "textMessage":
#             incoming_msg = message_data['textMessageData']['textMessage'].lower()
#         if  msg_type == "extendedTextMessage":
#             print(message_data)
#             incoming_msg = message_data['extendedTextMessageData']['text'].lower()    
#         if os.path.exists(fileName):
#             if os.stat(fileName).st_size != 0 :
#                 with open(fileName) as f:
#                     data = json.load(f)
#                     currentstatus = data['status']                    
#             else:
#                 currentstatus = -1
#                 json_saving_status(fileName,-1)
        

#         if os.path.exists(fileName) == False:
#             currentstatus = -1
#             json_saving_status(fileName,-1)
       
#         print(customer_phone)
#         global feeds
#         global contactid
#         global customerpassword
#         print("message received")
#         multipleoption = False

#         if os.path.exists(fileName):
#             if os.stat(fileName).st_size != 0 :
#                 with open(fileName) as f:
#                     data = json.load(f)
#                     currentstatus = data['status']
#                 if currentstatus == 5:
#                     global feeds
#                     feeds.clear()
#                     json_saving_status(fileName,-1)
#             else:
#                 json_saving_status(fileName,-1)
            
#         else:
#             json_saving_status(fileName,-1)

#         if 'hello' in incoming_msg or 'hi' in incoming_msg or 'start' in incoming_msg:
#             json_saving_status(fileName,0)
#             reply = "Hi " + customer_name +"! Welcome to Salmon.sg ticketing system chatbot\nPlease send *ONE* number to select what you want to do.\n1. Create a new request\n2. Cancel"
#             send_response(customer_phone,reply)
#             responded = True

#         if os.path.exists(fileName):
#             if os.stat(fileName).st_size != 0 :
#                 with open(fileName) as f:
#                     data = json.load(f)
#                     currentstatus = data['status']
                
#         if currentstatus == -1:
#             reply = "Hello Friends! Welcome to Salmon.sg\nIf you want to start our CRND Chatbot please enter *start* or *hi* or *hello*."
#             send_response(customer_phone,reply)
#             responded = True

        
#         if currentstatus == 0 and "1" in incoming_msg:
#             new_request = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[['phone','=',customer_phone]]],{'fields': ['id']})
#             if len(new_request) >0:
#                 for item in new_request:
#                     if 'id' in item:
#                         global contactid
#                         contactid =  item['id']
#                         print("contact ID: "+str(contactid))
#                 req_name_string = "Please send *ONE* number to select the request type.\n1. Report a fault on a PC\n2. Report a fault on a printer\n3. Report a fault on the Internet"
#                 json_saving_status(fileName,3)
#             else:
#                 req_name_string = "Please provide your *Full Name* (Eg. John Tan)"
#                 json_saving_status(fileName, 1)
#             send_response(customer_phone,req_name_string)
#             responded = True
#         if currentstatus == 0 and "2" in incoming_msg:
#             reply="Thank you for using our service, salmon.sg!"
#             send_response(customer_phone,reply)
#             json_saving_status(fileName, -1)
#             responded = True
#         elif currentstatus  != 0:
#             if currentstatus == 1:
#                 reply="Please enter *Email* (Eg. abc@example.com)"
#                 send_response(customer_phone,reply)
#                 #DO SOMETHINGS
#                 json_saving(fileName,'Name',incoming_msg,2)
#                 responded = True
#             if currentstatus == 2 and "@" in incoming_msg:                        
#                 #DO SOMETHINGS                
#                 json_saving(fileName,'Email',incoming_msg,3)
#                 for item in data['data']:
#                     if 'Name' in item:
#                         customername=item['Name']
#                 new_request = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[['name', '=', customername],['login','=',incoming_msg]]],{'fields': ['id']})
#                 if len(new_request) >0:
#                     for item in new_request:
#                         if 'id' in item:
#                             contactid =  item['id']
#                             print(contactid)
#                 else:    
#                     customerpassword = generate_password()
#                     jsondata ={
#                         'name': customername,
#                         'login': incoming_msg,
#                         'phone': customer_phone,
#                         'password': customerpassword,
#                         'email': incoming_msg
#                     }
#                     new_request = models.execute_kw(db, uid, password, 'res.users', 'create', [jsondata])                            
#                     contactid = new_request
#                     replypassword="Your new account detail is:\nUsername: " + incoming_msg+"\nPassword: " + customerpassword +"\nPlease change your password as soon as possible."
#                     send_response(customer_phone,replypassword)
                    
#                 reply="Please send *ONE* number to select the request type\n1. Report a fault on a PC\n2. Report a fault on a printer\n3. Report a fault on the Internet\n4. Finish the request\n5. Restart the whole process"
#                 send_response(customer_phone,reply)
#                 responded = True
#             if currentstatus == 2 and "@" not in incoming_msg:
#                 reply="Please send an email that is in the correct format (abc@example.com)"
#                 send_response(customer_phone,reply)
#                 json_saving_status(fileName, -1)
#                 responded = True
#             if currentstatus == 3:
#                 seperated_incoming_msg = incoming_msg.split(',')
#                 print(seperated_incoming_msg)
#                 for word in seperated_incoming_msg:
#                     if len(word) > 1:
#                         multipleoption = True
#                 if multipleoption == False:
#                     if '1' in incoming_msg or '2' in incoming_msg or '3' in incoming_msg:       
#                         print(currentstatus)
#                         print("start status 3")                
#                         json_saving(fileName,'Request Description',incoming_msg,4)
#                         reply=create_response(fileName)
#                         send_response(customer_phone,reply)
#                         print("currentstatus: " + str(currentstatus))
#                         #DO SOMETHINGS                    
#                         responded = True    
#             if currentstatus == 4 and '4' not in incoming_msg and '5' not in incoming_msg:  
#                 seperated_incoming_msg = incoming_msg.split(',')
#                 print(seperated_incoming_msg)
#                 for word in seperated_incoming_msg:
#                     if len(word) > 1:
#                         multipleoption = True
#                 if multipleoption == False:
#                     print(currentstatus)
#                     print("start status 4")
#                     json_saving(fileName,'Request Description',incoming_msg,4)
#                     reply=create_response(fileName)
#                     print("status 4")
#                     send_response(customer_phone,reply)
#                     print('end status 4')
#                     print("currentstatus: " + str(currentstatus))
#                     #DO SOMETHINGS
                    
#                     responded = True
            
#             elif currentstatus == 4 and '4' in incoming_msg and '5' in incoming_msg:
#                 seperated_incoming_msg = incoming_msg.split(',')
#                 print(seperated_incoming_msg)
#                 for word in seperated_incoming_msg:
#                     if len(word) > 1:
#                         multipleoption = True
#                 if multipleoption == False:
#                     reply="You can only choose either option 4 or option 5 at the same time, please try again.\n Please send *ONE* number to select the request type.\n1. Report a fault on a PC\n2. Report a fault on a printer\n3. Report a fault on the Internet\n4. Finish the request\n5. Restart the whole process"
#                     send_response(customer_phone,reply)
#                     #DO SOMETHINGS
#                     json_saving(fileName,'Request Description',"",4)
#                     responded = True
                
#             else:
#                 if currentstatus == 4 and '5' in incoming_msg:
#                     seperated_incoming_msg = incoming_msg.split(',')
#                     print(seperated_incoming_msg)
#                     for word in seperated_incoming_msg:
#                         if len(word) > 1:
#                             multipleoption = True
#                     if multipleoption == False:
#                         reply= "Hi " + customer_name +"! Welcome to Salmon.sg ticketing system chatbot\nPlease send *ONE* number to select what you want to do.\n1. Create a new request\n2. Cancel"
#                         send_response(customer_phone,reply)
#                         #DO SOMETHINGS                        
#                         feeds.clear()
#                         print(feeds)
#                         json_saving_status(fileName,0)
#                         responded = True
#                 if currentstatus == 4 and '4' in incoming_msg:     
#                     seperated_incoming_msg = incoming_msg.split(',')
#                     print(seperated_incoming_msg)
#                     for word in seperated_incoming_msg:
#                         if len(word) > 1:
#                             multipleoption = True
#                     if multipleoption == False:                  
#                         des = ""
#                         json_saving(fileName,'Request Description',incoming_msg,5)
#                         for item in data['data']:
#                             if 'Request Description' in item:
#                                 if ',' in item['Request Description']:
#                                     word = item['Request Description'].split(",")
#                                     for option in word:
#                                         if option == '1':
#                                             des += 'Request a fault on a PC<br>'
#                                         if option == '2':
#                                             des += 'Request a fault on a Printer<br>'
#                                         if option == '3':
#                                             des += 'Request a fault on the Internet<br>'     
#                                 else:
#                                     if item['Request Description'] == '1':
#                                         des += 'Request a fault on a PC<br>'
#                                     if item['Request Description'] == '2':
#                                         des += 'Request a fault on a Printer<br>'
#                                     if item['Request Description'] == '3':
#                                         des += 'Request a fault on the Internet<br>'
#                         print(des)
#                         new_partner = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[['id', '=', contactid]]],{'fields': ['partner_id']})
#                         partnerid = new_partner[0]['partner_id'][0]
#                         send_data = {
#                             'type_id':1,
#                             'request_text': des,
#                             'partner_id': partnerid
#                         }
#                         order_id = create_request_odoo(send_data)
#                         link = "https://fsm-demo.helpbots.sg/requests/request/" + str(order_id)
#                         reply = "Thank you for your submission, your request number is "+ str(order_id) +"\nHere's the link to your request: "+ link +"\nPlease send *ONE* number to select what you want to do next.\n1. Create a new request\n2. End the session\n3. Reset your account detail\n\n9. Contact Us if you are interested in our other services"
#                         send_response(customer_phone,reply)
#                         feeds.clear()
#                         print(feeds)
#                         responded = True
#             if currentstatus == 5 and incoming_msg == '1':
#                 reply="Please send *ONE* number to select the request type\n1. Report a fault on a PC\n2. Report a fault on a printer\n3. Report a fault on the Internet"
#                 send_response(customer_phone,reply)
#                 #DO SOMETHINGS
#                 feeds.clear()
#                 print(feeds)
#                 json_saving_status(fileName,3)                        
#                 responded = True
#             if currentstatus == 5 and incoming_msg == '2':
#                 reply="Hello {customer_name}! Welcome to Salmon.sg chatbot.\nPlease send *ONE number* to select the bot you want to do.\n1. Time Attendance chatbot\n2. Checklist Chatbot \n3. Ticketing System Chatbot\n4. Quiz Chatbot\n5. Repeating Order Chatbot\n6. Cancel"
#                 send_response(customer_phone,reply)
#                 #DO SOMETHINGS
#                 os.remove(fileName)                      
#                 responded = True
#             if currentstatus == 5 and incoming_msg == '3':
#                 reply="If you can, please search on the previous conversation for your account detail\nIf you want to reset your account detail, go to https://ticketing-demo.salmon.sg/web/login and click on *reset password*, we will send you an email to reset your password.\nPlease send *ONE* number to select what you want to do next.\n1. Create a new request\n2. End the session"
#                 send_response(customer_phone,reply)
#                 #DO SOMETHINGS
                
#                 json_saving_status(fileName,0)                        
#                 responded = True
                
#             if currentstatus == 5 and incoming_msg == "9":
#                 reply = "Please enter your *company's name*"
#                 send_response(customer_phone,reply)
#                 json_saving_status(fileName,12)
#                 responded = True
#             if currentstatus == 12:
#                 reply = "Please enter the product that you're interested in:\n1. WhatsApp Feedback System\n2. WhatsApp to Customer Service System\n3. WhatsApp to Ticketing System\n4. WhatsApp to Field Service Management System\n5. WhatsApp to Spreadsheet"
#                 send_response(customer_phone,reply)
                
#                 json_saving(fileName,"Company",incoming_msg,13)
#                 responded = True
#             if currentstatus == 13:
#                 reply =   "Thank you for your interest with salmon.sg, we will contact you soon.\nSend *start* if you want to create a new request"
#                 send_response(customer_phone,reply)
                
#                 with open(fileName) as f:
#                     data = json.load(f)
#                     listdata = data['data']
#                 for item in listdata:
#                     if 'Company' in item:
#                         usercompany = item['Company']
#                 if incoming_msg == "1":
#                     product_interested = "WhatsApp Feedback System"
#                 elif incoming_msg == "2":
#                     product_interested = "WhatsApp to Customer Service System"
#                 elif incoming_msg == "3":
#                     product_interested = "WhatsApp to Ticketing System"
#                 elif incoming_msg == "4":
#                     product_interested = "WhatsApp to Field Service Management System"
#                 elif incoming_msg == "5":
#                     product_interested = " WhatsApp to Spreadsheet"
#                 userdata = {
#                     'name': customer_name,
#                     'phone': customer_phone,
#                     'comment' : "company Name:" + usercompany +"\n Prouct Interested: " + product_interested
#                     }
#                 partner_id = create_contact_odoo(userdata)
#                 send_data = {
#                         'name': customer_name + " Lead",
#                         'partner_id': partner_id,
#                         'contact_name' : customer_name,
#                         'phone': customer_phone,
#                         'description' : "company Name:" + usercompany +"\n Prouct Interested: " + product_interested
#                     }
#                 print(send_data)
#                 create_crm_lead_odoo(send_data)
#                 json_saving(fileName,"Product Interested",incoming_msg,14)
#                 responded = True
#         print(currentstatus)
#         print(responded)    
#         if not responded:
#             #message.body('Incorrect request format. Please enter in the correct format')
#             reply= "Invalid input, please send the correct option provided."
#             send_response(customer_phone,reply)
#     return        
   
# def onIncomingMessageReceived(body):
#     idMessage = body['idMessage']
#     eventDate = datetime.fromtimestamp(body['timestamp'])
#     senderData = body['senderData']
#     messageData = body['messageData']
#     return senderData, messageData



# if __name__ == "__main__":
#    main()