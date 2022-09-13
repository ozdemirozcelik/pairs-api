# Pairs-API v3 for trading stocks (single or pairs), deployed on Heroku & Dreamhost

Version 3 of the Flask-RESTful API.

(Latest Release: v3.1)

Built from the ground-up with Flask-RESTful & Flask-SQLAlchemy & Flask-JWT-Extended.
Configured to be used with SQLite3 for local use.

A working demo is deployed in Heroku with PostgreSQL:

https://api-pairs-v3.herokuapp.com/


# Additions to v2

- additional API resources
- functionality to create server side sessions
- functionality to work with TradingView webhooks (Release V3.O)
- demo improvements:
  - new dashboard
  - list view for signals
- functionality to work with Interactive Brokers TWS API (Release V3.1)
  - Check my repository: [PAIRS-IBKR](https://github.com/ozdemirozcelik/pairs-ibkr)
  
# Use Cases

With Pairs-API v3 you can:
- catch webhooks from trading platforms or signal generators
- list, save, update and delete stocks/pairs, order and price details with API calls
- enable and disable stocks and pairs for active trading
- use access tokens for authentication purposes with login system backend
- TODO: send real time orders to exchange (possibly via Interactive Brokers)

# Requirements

* flask~=2.0.2
* Flask-RESTful~=0.3.9
* Flask-JWT-Extended~=4.4.0
* flask-sqlalchemy~=2.5.1
* flask-session~=0.4.0
* pyjwt~=2.4.0
* pytz~=2022.1
* uwsgi~=2.0.20 (for Heroku deployment only)
* psycopg2~=2.9.3 (for Heroku Postgres deployment only)

# Installation
(commands in parentheses for anaconda prompt)

### clone git repository:
```bash
$ git clone https://github.com/ozdemirozcelik/pairs-api-v3.git
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

IMPORTANT: check the need of using 'uwsgi' and 'psycopg2' from the requirements.txt before installing.
These are mainly used for Heroku and Heroku Postgres.

(windows: change -if necessary- version declarations from 'flask~=2.0.2'' to 'flask==2.0.2')

````
$ pip install -r requirements.txt
(conda install --file requirements.txt)
````
SQLAlchemy should take care of database creation. 

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


# Demo Configuration

### app.py
### resources/users.py

Demo is using custom created session management for server side sessions.
If you want to use flask session, search and enable rows marked with "(flask-session-change)".
Flask sessions may not be persistent in Heroku, works fine in local.

### templates/setup.html

If the app is deployed remotely, a proxy will be activated to bypass CORS limitations.
Proxy is set to "https://api-pairs-cors.herokuapp.com/" by default.
Check if you need the following lines before deployment:

```javascript
(base.html)(setup.html)
if (server_url != "http://127.0.0.1:5000/") {
    const updatedURL = server_url.replace(/^https:\/\//i, 'http://');
    var proxy_url = "https://api-pairs-cors.herokuapp.com/";
    server_url = proxy_url + updatedURL;
```

Check [Heroku deployment](#heroku-deployment) to learn for more about using your own proxy server.

# Resources

Resources defined with flask_restful are:

```python
api.add_resource(SignalWebhook, "/v3/webhook")
api.add_resource(SignalPrice, "/v3/price")
api.add_resource(SignalList, "/v3/signals/<string:number_of_items>")
api.add_resource(SignalListStatus,"/v3/signals/status/<string:order_status>/<string:number_of_items>")
api.add_resource(SignalListTicker, "/v3/signals/ticker/<string:ticker_name>/<string:number_of_items>")
api.add_resource(Signal, "/v3/signal/<string:rowid>")

api.add_resource(PairRegister, "/v3/regpair")
api.add_resource(PairList, "/v3/pairs/<string:number_of_items>")
api.add_resource(Pair, "/v3/pair/<string:name>")

api.add_resource(StockRegister, "/v3/regstock")
api.add_resource(StockList, "/v3/stocks/<string:number_of_items>")
api.add_resource(Stock, "/v3/stock/<string:symbol>")

api.add_resource(UserRegister, "/v3/reguser")
api.add_resource(UserList, "/v3/users/<string:number_of_users>")
api.add_resource(User, "/v3/user/<string:username>")
api.add_resource(UserLogin, "/v3/login")
api.add_resource(UserLogout, "/v3/logout")
api.add_resource(TokenRefresh, "/v3/refresh")
```

# Request & Response Examples

POSTMAN collection can be found under "local" folder.

### POST request to register a single stock:
```python
'http://api-pairs-v3.herokuapp.com/v3/regstock'
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
'http://api-pairs-v3.herokuapp.com/v3/regstock'
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
'http://api-pairs-v3.herokuapp.com/v3/stocks/0'
```

### GET request to receive certain number of stocks (for exp: 50):
```python
'http://api-pairs-v3.herokuapp.com/v3/stocks/2'
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
'http://api-pairs-v3.herokuapp.com/v3/stock/AAPL'
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
'http://api-pairs-v3.herokuapp.com/v3/stock/AAPL'
```
Response:
```json
{
    "message": "Item deleted"
}
```

### POST request to register a pair:
```python
'http://api-pairs-v3.herokuapp.com/v3/regpair'
```
Request Body:
```json
{
    "ticker1": "MA",
    "ticker2": "V",
    "hedge": 1.3,
    "status": 0
}
```

Response:
```json
{
    "message": "'pair' created successfully."
}
```

### PUT request to update a pair:
```python
'http://api-pairs-v3.herokuapp.com/v3/regpair'
```
Request Body:
```json
{
    "name": "MA-V",
    "ticker1": "MA",
    "ticker2": "V",
    "hedge": 1.4,
    "status": 1
}
```

Response:
```json
{
    "name": "MA-V",
    "ticker1": "MA",
    "ticker2": "V",
    "hedge": 1.4,
    "status": 1,
    "notes": null
}
```

### POST request to register a webhook signal:
```python
'http://api-pairs-v3.herokuapp.com/v3/webhook'
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

### GET request to get a list of signals with certain trade status
```python
'http://api-pairs-v3.herokuapp.com/v3/signals/status/waiting/2'
```
Response:
```json
{
    "signals": [
        {
            "rowid": 34,
            "timestamp": "2022-05-27 00:24:17",
            "ticker": "NMFC-0.72*NASDAQ:ROIC",
            "order_action": "buy",
            "order_contracts": 100,
            "order_price": -0.01,
            "mar_pos": "long",
            "mar_pos_size": 100,
            "pre_mar_pos": "flat",
            "pre_mar_pos_size": 0,
            "order_comment": "Enter Long(...)",
            "order_status": "waiting",
            "ticker_type": "pair",
            "stk_ticker1": "NMFC",
            "stk_ticker2": "ROIC",
            "hedge_param": 0.72,
            "order_id1": null,
            "order_id2": null,
            "stk_price1": null,
            "stk_price2": null,
            "fill_price": null,
            "slip": null,
            "error_msg": null
        },
        {
            "rowid": 27,
            "timestamp": "2022-05-26 21:16:49",
            "ticker": "NMFC-0.72*NASDAQ:ROIC",
            "order_action": "buy",
            "order_contracts": 100,
            "order_price": -0.01,
            "mar_pos": "long",
            "mar_pos_size": 100,
            "pre_mar_pos": "flat",
            "pre_mar_pos_size": 0,
            "order_comment": "Enter Long(...)",
            "order_status": "waiting",
            "ticker_type": "pair",
            "stk_ticker1": "NMFC",
            "stk_ticker2": "ROIC",
            "hedge_param": 0.72,
            "order_id1": null,
            "order_id2": null,
            "stk_price1": null,
            "stk_price2": null,
            "fill_price": null,
            "slip": null,
            "error_msg": null
        }
    ]
}
```
### POST request to update order price and status by order id
```python
'http://api-pairs-v3.herokuapp.com/v3/signal/updateorder'
```

````
"cancel":true  to cancel order
"partial":true  to update partially filled "order_contracts" amount
````

Request Body:
```json
{
    "passphrase": "webhook",
    "order_id": 945,
    "stk_price": 100.756,
    "cancel":false,
    "partial": false,
    "order_contracts": 0
}
```

Response:
(fill_price & slip is calculated automatically)
```json
{
    "rowid": 47,
    "ticker": "MA-3*V",
    "order_action": "buy",
    "order_contracts": 20,
    "order_price": -2.0,
    "mar_pos": "long",
    "mar_pos_size": 20,
    "pre_mar_pos": "flat",
    "pre_mar_pos_size": 0,
    "order_comment": "Enter Long",
    "order_status": "filled",
    "ticker_type": "pair",
    "stk_ticker1": "MA",
    "stk_ticker2": "V",
    "hedge_param": 3.0,
    "order_id1": 944,
    "order_id2": 945,
    "stk_price1": 300.1,
    "stk_price2": 100.756,
    "fill_price": -2.168,
    "slip": 0.168,
    "error_msg": null
}
```

### POST request to login with a user
```python
'http://api-pairs-v3.herokuapp.com/v3/login'
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

# Status Codes

Pairs-API v3 returns the following status codes:

| Status Code | Description             |
| :--- |:------------------------|
| 200 | `OK`                    |
| 201 | `CREATED`               |
| 400 | `BAD REQUEST`           |
| 404 | `NOT FOUND`             |
| 500 | `INTERNAL SERVER ERROR` |


# Heroku Deployment:

Download and install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).

Clone repository, login to Heroku, add git remote and push:
````
$ git clone https://github.com/ozdemirozcelik/pairs-api-v3.git
$ heroku login
$ heroku git:remote -a api-pairs-v3
$ git push heroku main
````

To enable PostgreSQL in your Heroku account:
- go to Resources in your Heroku account and install 'Heroku Postgres'
- go to Settings->Config Vars
- copy 'DATABASE_URL' value which should look like 'postgres://sdfyebdbfbf..'
- add a new system variable 'DATABASE_URL_SQLALCHEMY' and paste the value
- change 'postgre' to 'postgresql' and save, it should look like: 'postgresql://sdfyebdbfbf..'


See the links below to add CORS headers to the proxied request:

https://github.com/Rob--W/cors-anywhere

https://dev.to/imiebogodson/fixing-the-cors-error-by-hosting-your-own-proxy-on-heroku-3lcb

# DreamHost Shared Hosting Deployment:

Please follow the instructions here:

[DreamHost Shared Hosting Deployment](readmemore/DreamHost.md)

# TradingView as the signal generator:

You can use below template for TradingView to send a POST request as soon as an alert is triggered.

webhook URL should be:  '{URL_OF_YOUR_API}/v3/webhook'

(local\webhook.json)
````json
{
    "passphrase": "webhook",
    "ticker": "{{ticker}}",
    "order_action": "{{strategy.order.action}}",
    "order_contracts": {{strategy.order.contracts}},
    "order_price": {{strategy.order.price}},
    "mar_pos": "{{strategy.market_position}}",
    "mar_pos_size": {{strategy.market_position_size}},
    "pre_mar_pos": "{{strategy.prev_market_position}}",
    "pre_mar_pos_size": {{strategy.prev_market_position_size}},
    "order_comment": "{{strategy.order.comment}}"
}
````

# Demo:

https://api-pairs-v3.herokuapp.com/

# Using with Interactive Brokers

Recommended to be used with Interactive Brokers.
Check my repository: [PAIRS-IBKR](https://github.com/ozdemirozcelik/pairs-ibkr)

# Acknowledgements
snippets:
* [Sort a List](https://w3schools.com/howto/howto_js_sort_list.asp)
* [Table Display](http://jsfiddle.net/DaS39)
* [jQuery input filter](https://jsfiddle.net/KarmaProd/hw8j34f2/4/)
* [JavaScript Countdown Timer](https://www.w3schools.com/howto/howto_js_countdown.asp)
* [Tooltip](http://css-tricks.com/snippets/css/css-triangle)


# Contributing

Pull requests are welcome.




