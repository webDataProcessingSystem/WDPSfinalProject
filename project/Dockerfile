FROM python:3.10

RUN apt-get update \
    && pip install --upgrade pip \
    && apt-get -y install default-jre

WORKDIR /team11

COPY src src
COPY starter.py .
COPY data  data
COPY model model
COPY llm llm
COPY test/question.txt test/question.txt

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN python3 -m spacy download en_core_web_sm
RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader stopwords

CMD ["/bin/bash"]