from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from google.cloud import dialogflow_v2 as dialogflow
from pymongo import MongoClient
import requests
import json
import uuid
import os
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "agent22-9ntj-22db7b9d5eb5.json"
client = MongoClient('mongodb+srv://riturajpandey0:helloworld12@cluster0.eblupqj.mongodb.net/')
db = client['chat_db']  # Assuming 'chat_db' is your main database
project_id = 'agent22-9ntj'
language_code = 'en'

def detect_intent_text(project_id, session_id, text, language_code):
    global response
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if not text:
        return None, None

    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)


    try:
        response = session_client.detect_intent(
            session=session, query_input=query_input
        )
        
        return response.query_result.fulfillment_text, response.query_result.output_contexts, response.query_result.parameters.get('email', None), response.query_result.parameters.get('given-name', None), response.query_result.parameters.get('number', None), response.query_result.intent.display_name
    except Exception as e:
        print(f"Error in detect_intent_text: {e}")
        return None, None

import re

# Define a regular expression pattern to match common greetings
GREETING_PATTERN = r'\b(hi|hello|hey|halo|helo|hlw|hii|hallo|hiiiiiiiiiii|hlo)\b'

def generate_otp():
    global sent_otp
    sent_otp = str(random.randint(1000, 9999))
    return sent_otp


def send_otp_email(email, otp):
    sender_email = "riturajpandey.739@gmail.com"  
    receiver_email = email
    password = "hzhefhtsvfbfbsvy"  

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "OTP for Confirmation"

    body = f"Your OTP for confirmation is: {otp}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


@app.route("/", methods=["GET","POST"])

def webhook():
    global response_text
    # global gmailid
    data = request.form
    # print(data)
    profile_name = data.get('ProfileName', '')  

    img_ur = data.get('MediaUrl0', '')

    auth_token = 'e75518c9a196b1db4cffb2e80d3b3099'  
    account_sid = 'AC1081794ca1a70d62999b9b9ddff62e01'  
    auth = (account_sid, auth_token)

    if img_ur:
        response = requests.get(img_ur, auth=auth)

        if response.status_code == 200:
            with open("downloaded_media.jpg", "wb") as f:
                f.write(response.content)
            print("Media file downloaded successfully.")
        else:
            print("Failed to download media file. Status code:", response.status_code)
            print("Response text:", response.text)

    if 'From' not in request.values:
        return 'Invalid request', 400

    incoming_msg = request.values.get('Body', '')
    sender_phone_number = request.values.get('From', '').split(":")[1]

    collection = db[sender_phone_number]

    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

    text = incoming_msg
    language_code = "en"

    response_text, output_contexts, gmaill, Name, Registration_number, display_name = detect_intent_text(project_id, session_id, text, language_code)
    # print(display_name)
    if display_name == 'book ride - custom - custom':
       send_otp()

    if response_text is None:
        response_text = "I'm sorry, I couldn't understand that."

    if output_contexts:
        session['context'] = output_contexts[0].name

    all_documents = collection.find()
    # print(all)
    naam = []
    numb = []

    global gmailid
    gmailid = []
    # global gmailid
    # global naam
    message_data={}
    for doc in all_documents:
        if 'Name' in doc and doc['Name'] is not None:
            naam = [doc['Name']]
        if 'Registration_number' in doc and doc['Registration_number'] is not None:
            numb = [doc['Registration_number']]
        # if 'gmail' in doc and doc['gmail'] is not None:
        #     gmailid = [doc['gmail']][-1]
        
    if len(naam) >= 2:
        naam = naam[:-2]
    
    if re.search(GREETING_PATTERN, incoming_msg.lower()):
        # If user is registered and previous response was not "Thank you", greet the user with their name
        if naam and "Thank you" not in message_data.get('bot_response', ''):
            
            response_text = f'''Hi {naam[-1]} welcome back!
What can I do for you?'''
           
    message_data = {
        'timestamp': str(datetime.now()),
        'sender_phone_number': sender_phone_number,
        'ProfileName': profile_name,
        'incoming_msg': incoming_msg,
        'bot_response': response_text,
        'gmail': gmaill,
        'Name': Name,
        'Registration_number': Registration_number
    }
    
    collection.insert_one(message_data)

    all_documents1 = collection.find()

    for doc in all_documents1:
        if 'gmail' in doc and doc['gmail'] is not None:
            gmailid = [doc['gmail']][-1]
    # print(gmailid)


    #Sending otp to the user and verifying it.
    if display_name=='book ride - custom - custom - custom': 
        print(sent_otp)
        if incoming_msg==sent_otp:
            appointment_time = schedule_appointment()
            while not appointment_time:  # If no appointment available for tomorrow, try for day after tomorrow
                appointment_time = schedule_appointment()
            global filter_criteria
            filter_criteria = {"Registration_number": Registration_number}

            response_text = f"Congratulations, your appointment has been scheduled for {appointment_time}"
            print(response_text)
            # filter_criteria = {"Registration_number": Registration_number}
            message_data = {
            'timestamp': str(datetime.now()),
            'sender_phone_number': sender_phone_number,
            'ProfileName': profile_name,
            'incoming_msg': incoming_msg,
            'bot_response': response_text,
            'gmail': gmaill,
            'Name': Name,
            'Registration_number': Registration_number
        }
            collection.insert_one(message_data)
            # collection.update_one(filter_criteria, {"$set": {"bot_response": response_text}})
            # print(sent_otp)
        else:
            # print(sent_otp)
            response_text = "Incorrect OTP, enter again"

    resp = MessagingResponse()
    resp.message(response_text)

    return str(resp), 200


def send_otp():
    otp = generate_otp()
    session['otp'] = otp
    send_otp_email(gmailid, otp)
    return "OTP Sent"


def schedule_appointment():
    next_available_time = find_next_available_time()

    if next_available_time:
        return next_available_time.strftime("%Y-%m-%d %H:%M")
    else:
        # Try scheduling for day after tomorrow
        return find_next_available_time(tomorrow=False)


def find_next_available_time(tomorrow=True):
    current_time = datetime.now()
    
    if tomorrow:
        appointment_time = current_time.replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        if current_time.weekday() == 5:  # If today is Saturday
            appointment_time = current_time.replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=2)
        else:
            appointment_time = current_time.replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)

    while appointment_time.weekday() == 6:  # Skip Sunday
        appointment_time += timedelta(days=1)

    while appointment_time.hour < 17:
        existing_appointment = False
        for collection_name in db.list_collection_names():
            if db[collection_name].find_one({"time": appointment_time}):
                existing_appointment = True
                break

        if existing_appointment:
            appointment_time += timedelta(minutes=30)
        else:
            for collection_name in db.list_collection_names():
                db[collection_name].insert_one({"time": appointment_time})
            return appointment_time

    return None

@app.route("/home")
def home():
    return "<h2>hello</h2>"
     

if __name__ == "__main__":
    app.run(debug=True)
