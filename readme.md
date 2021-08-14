an example currency conversion api
==================================

gets rate information from:
https://freecurrencyapi.net/

For simplicity of the example, supports only these currencies:

`"USD", "EUR", "GBP"`

(uses ISO 4217 codes)


Setup
-----

Assuming you have a working Docker installation, you should be able to just run:

`docker-compose up`

to start the app. It should be accessible on port 5000 of your docker machine's IP address.

endpoints
---------

- `/rate` a GET endpoint to get a currency rate
    - Requires parameters `from` and `to`.
    - Returns the conversion rate from `from` to `to` as a floating point number.
    - The rate is the value of 1 unit of `from` in `to`.
    - The return value is a JSON object restating the request parameters and the rate.
        - `{
            from: string,
            to: string,
            rate: float
        }`

- `/convert` a GET endpoint that converts a value in one currency to another
    - Requires parameters `from` and `to` and `amount`.
    - Returns an amount in the `from` currency, converted to an amount in the `to` currency.
    - The return value is a JSON object restating the request parameters and the `converted` amount and the `rate` used in the conversion.
        - `{
            from: string,
            to: string,
            rate: float,
            amount: float,
            converted: float
        }`
    - The `converted` amount is rounded to 2 decimal points.
