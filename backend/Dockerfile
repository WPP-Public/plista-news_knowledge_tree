# docker build -t 808236342497.dkr.ecr.eu-west-1.amazonaws.com/devml/opendigitalworld_backend .
# docker run -it -p 5000:5000 808236342497.dkr.ecr.eu-west-1.amazonaws.com/devml/opendigitalworld_backend:latest
# docker push  808236342497.dkr.ecr.eu-west-1.amazonaws.com/devml/opendigitalworld_backend:latest

FROM python:3.6-slim

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ADD ./*.py /src/

WORKDIR /src

EXPOSE 5000

ENTRYPOINT python /src/main.py


