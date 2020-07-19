# Python IoT Data Integrity Example Code
Example source code for Europython 2020 talk by George Zisopoulos and Theofanis Petkos.

## Requirements
Docker (> 19.03) and docker-compose (> 3.7) are required to run the python-ingest from a container.

## Pre Installation Notes
* First of all clone this [repo](https://github.com/thepetk/python-ingest) (Ingest module) and make its image on your machine. Please check readme.md file [here](https://github.com/thepetk/python-ingest)

* Create a root project folder and get inside. On linux and Mac OS:
```
mkdir your_folders_name
cd your_folders_name
```
* Clone project's source code from gihub.

### Installation
* Create database on PostgreSQL:
```
>>> CREATE DATABASE dt_db;
```
* Also make sure that ingest_db is up. If not please run again python-ingest installation.

* Create venv on project folder and install requirements:
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```
* Run necessary db migrations. Do not forget to change the sqlalchemy.url on alembic.ini file
```
$ alembic upgrade head 
```
* Go to .env file inside config folder and change environment variable values according to your credentials.

* Now you can deploy your 3 services (RabbitMQ, Python-Ingest and Python-IoT-Data-Integrity) with:
```
make install
```

## Usage

* After successful deploy of containers you can check the functionality via socketing. For example you can send below json to 2006 port from terminal:
```
{ "device_number": "86915304265485", "event_code": "4002", "message_date": "2020\/02\/05 12:18:28", "latitude": "37.9815116", "longitude": "23.7315200" }
```
* Save above text to event file
* Run on linux:
```
cat event | ncat '127.0.0.1' 2006
```
* Run on Mac OS 
```
cat event | nc '127.0.0.1' 2006
```

## Contributing

Pull requests are welcome. Feel free to take this code for your own project.

## Troubleshooting

For any problems please open an issue to my repo.

Best regards,
### Theofanis A. Petkos, Software Engineer.
### George T. Zisopoulos, Software Engineer.
