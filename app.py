from flask import Flask, render_template
from flask_restful import Api
from resources.pairs import PairRegister, PairList, Pair
from resources.signals import SignalWebhook, SignalList, Signal
from resources.stocks import StockRegister, StockList, Stock
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

api.add_resource(StockRegister, '/v1/regstock')
api.add_resource(StockList, '/v1/stocks/<string:number_of_items>')
api.add_resource(Stock, '/v1/stock/<string:symbol>')

# enable if running locally
# server_url = "http://127.0.0.1:5000/"

# disable if running locally
# test server url:
server_url = "http://api-pairs.herokuapp.com/"

# proxy to bypass CORS limitations
proxies = {
    'get': 'https://api-pairs-cors.herokuapp.com/'
    }


@app.get('/')
def dashboard():
    server_url_read = server_url + "v1/signals/50"

    try:
        # disable if using locally:
        response = requests.get(server_url_read, proxies=proxies, timeout=10)

        # enable if using locally:
        # response = requests.get(server_url_read, timeout=5)

    except requests.Timeout:
        # back off and retry
        print(f'\n{time_str()} - timeout error')
        pass
    except requests.ConnectionError:
        print(f'\n{time_str()} - connection error')
        pass

    signals = response.json()['signals']

    return render_template('dashboard.html', signals=signals)


@app.get('/apitest')
def apitest():
    return render_template('apitest.html')
