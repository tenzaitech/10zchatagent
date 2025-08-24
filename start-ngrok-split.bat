@echo off
echo 🌐 Starting ngrok for split services...
echo Chatbot: https://tenzai-chat.ap.ngrok.io
echo Order: https://tenzai-order.ap.ngrok.io
ngrok start --all --config ngrok.yml