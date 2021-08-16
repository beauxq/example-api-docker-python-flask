from typing import Dict, Tuple, TypedDict, Union
from requests import get
from time import time
from flask import Flask, jsonify, Response, request, make_response, Request


app = Flask(__name__)

class RateCache:
    currencies = {
        "USD",
        "GBP",
        "EUR"
    }

    def __init__(self) -> None:
        self._rates = {c: 0.0 for c in RateCache.currencies}
        self._last_update = 0.0
        self._valid = False

    def _update_rates(self) -> bool:
        """
        updates rates from freecurrencyapi.net

        returns whether rates are valid values received from freecurrencyapi.net
        """
        now = time()
        # "You are allowed to submit 10 requests per hour without authentication."
        if now - self._last_update > 420:
            self._last_update = now
            print("checking for update to exchange rates")
            res = get("https://freecurrencyapi.net/api/v1/rates")
            if res.status_code == 200:
                try:
                    values: Dict[str, float] = next(iter(res.json()['data'].values()))
                    for currency in RateCache.currencies:
                        if currency == "EUR":
                            # this freecurrencyapi.net uses EUR as the base
                            self._rates[currency] = 1.0
                            continue    
                        if type(values[currency]) is not float:
                            raise TypeError("value for currency wasn't float")
                        self._rates[currency] = values[currency]
                    self._valid = True
                except (TypeError, KeyError) as e:
                    print("freecurrencyapi.net didn't give expected data format")
                    print(e)
                    print(res.json())
                    self._valid = False
            else:
                print("freecurrencyapi.net didn't give status code 200")
                print(res.status_code)
                print(res.content)
                # valid doesn't change
        return self._valid
    
    def rate(self, from_code: str, to_code: str) -> float:
        """
        returns the conversion rate

        returns 0.0 if the rate is not available
        (bad codes or server not available)
        """
        if (from_code in RateCache.currencies
        and to_code in RateCache.currencies
        and self._update_rates()):
            return self._rates[to_code] / self._rates[from_code]
        else:
            return 0.0

rate_cache = RateCache()
            

@app.route('/test')
def test() -> Response:
    return jsonify({'message': 'test successful'})


@app.route('/test/<string:name>')
def test_name(name: str) -> Response:
    return jsonify({'message': 'test successful for {}'.format(name)})


CurrencyJsonifiable = TypedDict('CurrencyJsonifiable', {
    "from": str,
    "to": str,
    "rate": float,
    "amount": float,
    "converted": float
}, total=False)
# TODO: in Python 3.10, remove total=False and use `NotRequired` on amount and converted

def get_rate(request: Request) -> Tuple[float, Union[Response, CurrencyJsonifiable]]:
    """
    returns the rate and a dictionary that can be jsonified to a response

    if there's a problem, returns 0.0 and the problem response
    """
    from_param = request.args.get('from')
    to_param = request.args.get('to')
    if from_param is None or to_param is None:
        return 0.0, make_response("this endpoint requires `from` and `to` parameters", 400)
    from_param = from_param.upper()
    to_param = to_param.upper()
    if from_param not in RateCache.currencies or to_param not in RateCache.currencies:
        return 0.0, make_response(f"valid currencies are {RateCache.currencies}", 400)
    rate = rate_cache.rate(from_param, to_param)
    if rate == 0.0:
        return 0.0, make_response("unable to get exchange rates", 503) 
    return rate, {
        "from": from_param,
        "to": to_param,
        "rate": rate
    }


@app.route('/rate')
def rate() -> Response:
    _, res = get_rate(request)
    if isinstance(res, Response):
        return res
    else:
        return jsonify(res)    


@app.route('/convert')
def convert() -> Response:
    rate, res = get_rate(request)
    if isinstance(res, Response):
        return res

    amount = request.args.get('amount', type=float)
    if amount is None:
        return make_response("this endpoint requires `from` and `to` and `amount` parameters", 400)
    
    res["amount"] = amount
    res["converted"] = round(amount * rate, 2)
    return jsonify(res)
