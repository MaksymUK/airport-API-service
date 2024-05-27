# Airport API Service
This is a simple API service that provides information about airports, flights, crews and airplanes. It also can track sold tickets for each flight.

## Install using GitHUB
1. Clone the repository
```bash
git clone https://github.com/MaksymUK/airport-API-service.git
```
2. Change the directory
```bash
cd airport-API-service
```
3. Set up and activate the virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```
4. Install the requirements
```bash
pip install -r requirements.txt
```
5. Set database settings in the environment variables
```bash
set DB_HOST=<your db hostname>
set DB_NAME=<your db name>
set DB_USER=<your db username>
set DB_PASSWORD=<your db user password>
set SECRET_KEY=<your secret key>
```
6. Run the server
```bash
python manage.py migrate
python manage.py runserver
```

## Run with Docker
Docker should be installed.
```bash
docker-compose build
docker-compose up
```
## Getting access
- create user via /api/v1/user/register/
- get access token via /api/v1/user/token/
