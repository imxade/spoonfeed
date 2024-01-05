FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD [ "streamlit", "run", "main.py", "--server.port=5000", "--server.address=0.0.0.0" ]
