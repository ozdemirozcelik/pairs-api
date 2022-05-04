# Pairs-API v2 for trading stocks (single or pairs), deployed on Heroku

Version 2 of the Flask-RESTful API.

Built from the ground-up with Flask-RESTful & Flask-SQLAlchemy & Flask-JWT-Extended.
Configured to be used with SQLite3 for local use.

Deployed in Heroku with PostgreSQL for testing purposes:

`http://api-pairs-v2.herokuapp.com`

Front-end demo for v2 (Javascript):

https://api-pairs-v2.herokuapp.com/apitest

The most recent version is available here:

https://api-pairs.herokuapp.com/apitest

# Use Cases

With Pairs-API v2 you can:
- list, save, update and delete stocks and pairs with API calls
- enable and disable stocks and pairs for active trading
- catch webhooks from trading platforms or signal generators
- use access tokens for authentication purposes with login system backend

# Requirements

* flask==2.0.2
* requests==2.24.0
* Flask-RESTful==0.3.9
* Flask-JWT-Extended==4.4.0
* flask-sqlalchemy==2.5.1
* pyjwt==2.3.0
* uwsgi (for Heroku deployment only)
* psycopg2 (for Heroku Postgres deployment only)

# Installation
(commands in parentheses for anaconda prompt)

### clone git repository:
```bash
$ git clone https://github.com/ozdemirozcelik/pairs-api-v2.git
````
### create and activate virtual environment:
````bash
$ pip install virtualenv
(conda install virtualenv)

$ mkdir pairs-api
md pairs-api (windows)

$ cd pairs-api

$ python -m venv pairs-env
(conda create --name pairs-env)

$ source pairs-env/bin/activate
.\pairs-env\scripts\activate (windows)
(conda activate pairs-env)
````
### install requirements:

IMPORTANT: you may need to delete line 'uwsgi' and 'psycopg2' from the requirements.txt before installing.
These are needed for Heroku deployment only.

(windows: change -if necessary- version declarations from 'requests~=2.24.0'' to 'requests==2.24.0')

````
$ pip install -r requirements.txt
(conda install --file requirements.txt)
````
SQLAlchemy normally takes care of the database creation. 
If you want to manually create the database:
````
$ rm data.db
delete data.db (windows)

$ python local/create_db.py
````
### run flask:
````
$ export FLASK_APP=app
$ export FLASK_ENV=development
$ set FLASK_DEBUG=1 
$ flask run

(windows)
set FLASK_APP=app
set FLASK_ENV=development
set FLASK_DEBUG=1 
flask run
````

browse to "http://127.0.0.1:5000/" to see the dashboard.

# Authorization

### webhooks
need a passphrase, by default it is set as 'webhook'; check signals.py:

```python
PASSPHRASE = 'webhook'
```

### default admin and a user
is created during database creation; check users.py::

```python
    @staticmethod
    def default_users():
        # Add Default Users
        if not UserModel.find_by_username("admin"):
            admin = UserModel("admin", "123")
            admin.insert()
        if not UserModel.find_by_username("user1"):
            user = UserModel("user1", "123")
            user.insert()
```

### resource authorization
needs currently set with Flask- JWT:

- no token required:
  - POST signal
  - GET stock & pair & signal
  - GET stocks & pairs
  
- optional token required: "@jwt_required(optional=True)":
  - GET signals (get more signals if token is available )
  
- fresh token required "@jwt_required(fresh=True)":
  - PUT, Delete signal
  - POST, PUT pair & stock

- admin rights & fresh token required "@jwt_required(fresh=True)":
  - DELETE signal & pair & stock
  - GET, POST, PUT, DELETE user



# Configuration

### app.py

If the app is deployed locally, you should set "run_at" variable to "local":

```python
run_at = "local"
# run_at = "remote"

# enable if running locally
server_url = "http://127.0.0.1:5000/"
```

You will need to use a proxy server to bypass CORS limitations if API is deployed remotely but to be tested locally:
```python
# disable if running locally
# test server url:
server_url = "http://api-pairs.herokuapp.com/"

# proxy to bypass CORS limitations
proxies = {
    'get': 'https://api-pairs-cors.herokuapp.com/'
    }

# disable if using locally:
response = requests.get(server_url_read, proxies=proxies, timeout=5)
```

### apitest.html

Same applies to front-end demo:

```python
//enable if using locally
var server_url = "http://127.0.0.1:5000/";

// // disable if using locally, test page with proxy to bypass CORS limitations
// var proxy_url = "https://api-pairs-cors.herokuapp.com/";
// var goto_url = "http://api-pairs.herokuapp.com/";
// var server_url = proxy_url + goto_url;
```

Check [Heroku deployment](#heroku-deployment) to learn for more about using your own proxy server.

# Resources

Resources defined with flask_restful are:

```python
api.add_resource(SignalWebhook, '/v2/webhook')
api.add_resource(SignalList, '/v2/signals/<string:number_of_items>')
api.add_resource(Signal, '/v2/signal/<string:rowid>')

api.add_resource(PairRegister, '/v2/regpair')
api.add_resource(PairList, '/v2/pairs/<string:number_of_items>')
api.add_resource(Pair, '/v2/pair/<string:name>')

api.add_resource(StockRegister, '/v2/regstock')
api.add_resource(StockList, '/v2/stocks/<string:number_of_items>')
api.add_resource(Stock, '/v2/stock/<string:symbol>')

api.add_resource(UserRegister, '/v2/reguser')
api.add_resource(UserList, '/v2/users/<string:number_of_users>')
api.add_resource(User, '/v2/user/<string:username>')
api.add_resource(UserLogin, '/v2/login')
api.add_resource(UserLogout, '/v2/logout')
api.add_resource(TokenRefresh, '/v2/refresh')
```

# Request & Response Examples

POSTMAN collection can be found under "local" folder.

### POST request to register a single stock:
```python
'http://api-pairs-v2.herokuapp.com/v2/regstock'
```
Request Body:
```json
{
    "symbol": "AAPL",
    "prixch": "SMART",
    "secxch": "NASDAQ",
    "active": 1
}
```

Response:
```json
{
    "message": "Stock created successfully."
}
```

### PUT request to update a single stock:
```python
'http://api-pairs-v2.herokuapp.com/v2/regstock'
```
Request Body:
```json
{
    "symbol": "AAPL",
    "prixch": "SMART",
    "secxch": "NASDAQ",
    "active": 1
}
```

Response:
```json
{
    "symbol": "AAPL",
    "prixch": "ISLAND",
    "secxch": "BYX",
    "active": 0
}
```



### GET request to get all stocks:
```python
'http://api-pairs-v2.herokuapp.com/v2/stocks/0'
```

### GET request to receive certain number of stocks (for exp: 50):
```python
'http://api-pairs-v2.herokuapp.com/v2/stocks/2'
```
Response:
```json
{
    "stocks": [
        {
            "symbol": "AAPL",
            "prixch": "SMART",
            "secxch": "NASDAQ",
            "active": 1
        },
        {
            "symbol": "DRH",
            "prixch": "SMART",
            "secxch": "SMART",
            "active": 1
        }
    ]
}
```

### GET request to get details of a certain stock:
```python
'http://api-pairs-v2.herokuapp.com/v2/stock/AAPL'
```

Response:
```json
{
    "symbol": "AAPL",
    "prixch": "SMART",
    "secxch": "NASDAQ",
    "active": 1
}
```
### DELETE request for a certain stock:
```python
'http://api-pairs-v2.herokuapp.com/v2/stock/AAPL'
```
Response:
```json
{
    "message": "Item deleted"
}
```

### POST request to register a webhook signal:
```python
'http://api-pairs-v2.herokuapp.com/v2/webhook'
```
Request Body:
```json
{
    "passphrase": "webhook",
    "ticker": "AAPL",
    "order_action": "buy",
    "order_contracts": "100",
    "order_price": "400.2",
    "mar_pos": "long",
    "mar_pos_size": "100",
    "pre_mar_pos": "flat",
    "pre_mar_pos_size": "0",
    "order_comment": " Enter Long",
    "order_status": "waiting"
}
```

Response:
```json
{
    "message": "Signal created successfully."
}
```

### POST request to login with a user
```python
'http://api-pairs-v2.herokuapp.com/v2/login'
```
Request Body (Token to expire in 30 min, default is 10 min):
```json
{
    "username": "user1",
    "password": "123",
    "expire":30
}
```
Response:
```json
{
    "access_token": "eyJ0eXAx...",
    "refresh_token": "eyJ0eXC...",
    "expire": 30
}
```


#### Test the demo application here:

https://api-pairs-v2.herokuapp.com/apitest

# Status Codes

Pairs-API v2 returns the following status codes:

| Status Code | Description             |
| :--- |:------------------------|
| 200 | `OK`                    |
| 201 | `CREATED`               |
| 400 | `BAD REQUEST`           |
| 404 | `NOT FOUND`             |
| 500 | `INTERNAL SERVER ERROR` |


# Heroku Deployment:

####TODO: Update with images & more detailed explanation

Download and install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).

Clone repository, login to Heroku, add git remote and push:
````
$ git clone https://github.com/ozdemirozcelik/pairs-api-v2.git
$ heroku login -i
$ heroku git:remote -a api-pairs-v2
$ git push heroku main
````

To enable PostgreSQL in your Heroku account:
- go to Resources in your Heroku account and install 'Heroku Postgres'
- go to Settings->Config Vars and you will see 'DATABASE_URL'
- copy 'DATABASE_URL' value which should look like 'postgres://sdfyebdbfbf..'
- add a new system variable 'DATABASE_URL_SQLALCHEMY' and paste the value
- change 'postgre' to 'postgresql' and save, it should look like: 'postgresql://sdfyebdbfbf..'


See the links below to add CORS headers to the proxied request:

https://github.com/Rob--W/cors-anywhere

https://dev.to/imiebogodson/fixing-the-cors-error-by-hosting-your-own-proxy-on-heroku-3lcb


# Demo:
(Automatic deploys are disabled)

https://api-pairs-v2.herokuapp.com/apitest

# Acknowledgements
snippets:
* [Sort a List](https://w3schools.com/howto/howto_js_sort_list.asp)
* [Table Display](http://jsfiddle.net/DaS39)
* [jQuery input filter](https://jsfiddle.net/KarmaProd/hw8j34f2/4/)
* [JavaScript Countdown Timer](https://www.w3schools.com/howto/howto_js_countdown.asp)

# Considerations

Considering for the next version:

- improve demo with live TradingView realtime webhooks
- send real time orders to exchange (possibly via Interactive Brokers)

# Contributing

Pull requests are welcome.




