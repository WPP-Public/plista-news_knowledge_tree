# News Knowledge Tree

This repository contains the project to be able to visualize the news for your country and see what are the hot topic of the moment.

![Demo](images/example.gif)

if you want to know more there is the [presentation](https://docs.google.com/presentation/d/1_-y551WY2fo0FS7QD8gDgYopiVFbXQKbvAsD3NxZTxQ/edit?usp=sharing) for PyData Berlin on December 2019. 

## Run 

After downloading your project you will need to get a google news api [here](https://newsapi.org/docs) (They have a free tier). 
With ythe following script you will install all  
```bash
touch data_processing/.env
echo GOOGLE_NEWS_API=$YOUR_KEY_FROM_GOOGLE_NEWSAPI > data_processing/.env
```

To run the project you can just start docker compose
```bash
docker-compose up
```
Building the docker for the first time will take some time. it is normal :)

You will be able to open the front end in your browser [here](http://0.0.0.0:8080/)


## Install all dependencies

To install all the library you will need python 3.6 on you favorite environment. 

```bash
pip install -r backend/requirements.txt -r data_processing/requirements.txt
```

For the frontend you will need to have npm installed. 
```bash
cd frontend/graph
npm install
```

The best way to run the app is to use docker-compose. However if you really would like to run on you machine directly
 you can start the 2 flask apps with:
```bash
python backend/main.py
```
and
```bash
pyton data_processing/main.py
```
and for the frontend you will need:
```bash
cd frontend/graph
npm start
```
Be aware that we are using the service name as host in the code to call other services. You will need to update your 
`/etc/hosts` to resolve the dependency. 

