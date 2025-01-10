# WhatsApp Chatbot for appointment scheduling with OTP Verification and Dialogflow Integration

This project implements a chatbot using Flask, Twilio, Google Dialogflow, and MongoDB. The chatbot handles WhatsApp messages, detects user intent, sends OTPs for verification, and manages appointments using MongoDB.

## Features

- **WhatsApp Message Handling**: Receives messages from users via Twilio's WhatsApp API.
- **Dialogflow Integration**: Detects user intents and extracts entities such as names, emails, and registration numbers.
- **OTP Verification**: Sends OTP to users via email for verification purposes.
- **Appointment Scheduling**: Dynamically schedules appointments and avoids conflicts using MongoDB.
- **Media File Handling**: Downloads and processes media files sent by users.
- **MongoDB Integration**: Stores user data and conversation history for personalized responses.

## Prerequisites

1. Python 3.x installed on your system.
2. Google Cloud Dialogflow project credentials (`agent22-9ntj-22db7b9d5eb5.json`).
3. MongoDB database connection string.
4. Twilio account with a WhatsApp-enabled phone number.
5. Gmail account for sending OTPs.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rituraj-sys/Retrieval-Based-Chatbot.git
   cd Retrieval-Based-Chatbot
