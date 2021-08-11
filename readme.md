an example currency conversion api
==================================

gets rate information from:
https://freecurrencyapi.net/


Setup
-----

Assuming you have a working Docker installation, you should be able to just run:

`docker-compose up`

to start the app. It should be accessible on port 5000 of your docker machine's IP address.

endpoints
---------

- `/rate` a GET endpoint to get a currency rate
    - Returns the conversion rate from `from` to `to` as a floating point number.
    - The rate is the value of 1 unit of `from` in `to`.
    - The return value is a JSON object restating the request parameters and the rate.

- `/convert` a GET endpoint that converts a value in one currency to another
    - returns an amount in one currency, converted to an amount in another currency.
    - The return value is a JSON object restating the request parameters and the converted amount.
    - The converted amount is rounded to 2 decimal points.
