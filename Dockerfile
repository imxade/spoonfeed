FROM python:3.9
WORKDIR /usr/src/app
COPY . ./
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "streamlit", "run", "main.py", "--server.port=5000", "--server.address=0.0.0.0" ]
