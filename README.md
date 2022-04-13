# Pairs-API V1 for trading stocks (single or pairs), deployed on Heroku

Version 1 of the RESTful API built from the ground-up with Python.
Pairs-API catches and stores webhooks from trading platforms such as Tradingview.

Deployed in Heroku for testing purposes:

`http://api-pairs.herokuapp.com`

Front-end demo (Javascript):

https://api-pairs-test.herokuapp.com/apitest

# Use Cases

Pairs-API v1 can be a good starting point for developing trading bots. You can:
- list, save, update and delete stocks and pairs
- enable and disable stocks and pairs for active trading
- catch webhooks from trading platforms or signal generators

# Requirements
* requests~=2.24.0
* flask~=2.0.2
* Flask-RESTful
* uwsgi (for Heroku deployment only)

# Installation
(commands in parenthesis for anaconda prompt)

### clone git repository:
```bash
$ git clone https://github.com/ozdemirozcelik/pairs-api.git
````
### create and activate virtual environment:
````bash
$ pip install virtualenv
(conda install virtualenv)

$ mkdir pairs-api
md pairs-api (windows)

$ cd pairs-api

$ python -m venv pairs-api
(conda create --name pairs-api)

$ source pairs-api/bin/activate
.\pairs-api\scripts\activate (windows)
(conda activate pairs-api)
````
### install requirements:

IMPORTANT: delete line 'uwsgi' from the requirements.txt before installing.
uwsgi is needed for Heroku deployment only.

(anaconda prompt: change version declarations from 'requests~=2.24.0'' to 'requests=2.24.0')

````
$ pip install -r requirements.txt
(conda install --file requirements.txt)

$ rm data.db
delete data.db (windows)

$ python create_db.py
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

No authorization needed at the moment, webhooks need a passphrase, by default it is set as 'webhook'.
Check signals.py:

```python
PASSPHRASE = 'webhook'
```

# Configuration

### app.py

If the app is deployed locally, you should set server url to flask local deployment server:

```python
# enable if running locally
server_url = "http://127.0.0.1:5000/"

# enable if using locally:
response = requests.get(server_url_read, timeout=5)
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
api.add_resource(SignalWebhook, '/v1/webhook')
api.add_resource(SignalList, '/v1/signals/<string:number_of_items>')
api.add_resource(Signal, '/v1/signal/<string:rowid>')

api.add_resource(PairRegister, '/v1/regpair')
api.add_resource(PairList, '/v1/pairs/<string:number_of_items>')
api.add_resource(Pair, '/v1/pair/<string:name>')

api.add_resource(StockRegister, '/v1/regstock')
api.add_resource(StockList, '/v1/stocks/<string:number_of_items>')
api.add_resource(Stock, '/v1/stock/<string:symbol>')
```

# Request & Response Examples

POST request to register a single stock:
```python
'http://api-pairs.herokuapp.com/v1/regstock'
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

PUT request to update a single stock:
```python
'http://api-pairs.herokuapp.com/v1/regstock'
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



GET request to get all stocks:
```python
'http://api-pairs.herokuapp.com/v1/stocks/0'
```

GET request to receive certain number of stocks (for exp: 50):
```python
'http://api-pairs.herokuapp.com/v1/stocks/2'
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

GET request to get details of a certain stock:
```python
'http://api-pairs.herokuapp.com/v1/stock/AAPL'
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
DELETE request for a certain stock:
```python
'http://api-pairs.herokuapp.com/v1/stock/AAPL'
```
Response:
```json
{
    "message": "Item deleted"
}
```

PUT request to register a webhook signal:
```python
'http://api-pairs.herokuapp.com/v1/webhook'
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

Test the demo application for more:

https://api-pairs-test.herokuapp.com/apitest

# Status Codes

Pairs-API v1 returns the following status codes:

| Status Code | Description             |
| :--- |:------------------------|
| 200 | `OK`                    |
| 201 | `CREATED`               |
| 400 | `BAD REQUEST`           |
| 404 | `NOT FOUND`             |
| 500 | `INTERNAL SERVER ERROR` |


# Heroku Deployment:

This part is currently under review, it will be here soon.

# Demo:
(Automatic deploys are disabled)

https://api-pairs-test.herokuapp.com/apitest

# Acknowledgements
snippets:
* [Sort a List](https://w3schools.com/howto/howto_js_sort_list.asp)
* [Table Display](http://jsfiddle.net/DaS39)
* [jQuery input filter](https://jsfiddle.net/KarmaProd/hw8j34f2/4/)

# v2 Considerations

Considering for v2:
- simplify storage with SQLAlchemy
- add PostgreSQL
- add token refreshing and Flask-JWT-Extended
- serialize with Marshmallow
- improve demo with TradingView realtime webhooks

# Contributing

Pull requests are welcome.

# Help

This part is currently under review, it will be here soon.



