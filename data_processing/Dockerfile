# inspired from https://github.com/poteha/docker-nlp/blob/master/Dockerfile.cpu
FROM python:3.6-slim

RUN apt-get update && apt-get install -y unixodbc-dev gcc g++

ADD requirements.txt .
RUN pip install -r requirements.txt

RUN python -m nltk.downloader stopwords && python -m nltk.downloader punkt  && \
    python -m nltk.downloader averaged_perceptron_tagger

RUN python -c 'import flair; _ = flair.models.SequenceTagger.load("de-ner"); _ = flair.models.SequenceTagger.load("ner-fast")'

ADD *.py src/
ADD .env src/

WORKDIR src

ENTRYPOINT python /src/main.py