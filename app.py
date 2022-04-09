from flask import Flask, render_template
from flask_restful import Api
from resources.pairs import PairRegister, PairList, Pair
from resources.signals import SignalWebhook, SignalList, Signal
from resources.stocks import StocksRegister, StockRegister, StockList, Stock
import requests

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True  # to allow flask propagating exception even if debug is set to false

if __name__ == '__main__':  # to avoid duplicate calls to app.run
    app.run(debug=True)  # important to mention debug=True

api = Api(app)

api.add_resource(SignalWebhook, '/v1/webhook')
api.add_resource(SignalList, '/v1/signals/<string:number_of_items>')
api.add_resource(Signal, '/v1/signal/<string:rowid>')

api.add_resource(PairRegister, '/v1/regpair')
api.add_resource(PairList, '/v1/pairs/<string:number_of_items>')
api.add_resource(Pair, '/v1/pair/<string:name>')

api.add_resource(StocksRegister, '/v1/regstocks')
api.add_resource(StockRegister, '/v1/regstock')
api.add_resource(StockList, '/v1/stocks/<string:number_of_items>')
api.add_resource(Stock, '/v1/stock/<string:symbol>')

# server_url = "http://127.0.0.1:5000/"
server_url = "https://api-pairs.herokuapp.com/"


@app.get('/')
def dashboard():
    server_url_read = server_url + "v1/signals/0"

    # response = requests.get(server_url_read, timeout=5)
    response = requests.get(server_url_read)

    signals = response.json()['signals']

    return render_template('dashboard.html', signals=signals)


@app.get('/apitest')
def apitest():
    return render_template('apitest.html')
