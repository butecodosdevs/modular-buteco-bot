FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y chromium chromium-driver fonts-liberation libnss3 libasound2 libatk-bridge2.0-0 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libfreetype6 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libx11-6 libx11-xcb1 libxcb1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install python-dotenv

COPY . .

CMD ["python", "bot.py"]

