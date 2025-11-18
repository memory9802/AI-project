FROM python:3.11-slim

# 設定環境變數以支援 UTF-8
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=utf-8

WORKDIR /app


COPY . /app

RUN pip install --no-cache-dir \
    flask pymysql requests \
    langchain langchain-google-genai langchain-core langchain-community langchain-groq langchain-openai \
    cryptography
    
EXPOSE 5000

CMD ["python", "app.py"]
