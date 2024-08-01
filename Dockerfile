FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential python3-dev libmagic-dev

RUN mkdir -p /apps/FileBox
WORKDIR /apps/FileBox
COPY . /apps/FileBox

RUN pip install -r requirements.txt
CMD ["python3", "run.py"]
