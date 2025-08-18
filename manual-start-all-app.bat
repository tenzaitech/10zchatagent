@echo off
cd /d "C:\Users\pleam\OneDrive\Desktop\10zchatbot"
docker-compose up -d
cloudflared tunnel --config config.yml run