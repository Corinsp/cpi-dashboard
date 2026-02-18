FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0