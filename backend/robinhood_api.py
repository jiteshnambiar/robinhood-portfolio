import getpass
import json
import urllib

import requests


class RobinhoodAPI:

    endpoints = {
        #"login": "https://api.robinhood.com/api-token-auth/",
        "login": "https://api.robinhood.com/oauth2/token/",
        "investment_profile": "https://api.robinhood.com/user/investment_profile/",
        "accounts": "https://api.robinhood.com/accounts/",
        "ach_iav_auth": "https://api.robinhood.com/ach/iav/auth/",
        "ach_relationships": "https://api.robinhood.com/ach/relationships/",
        "ach_transfers": "https://api.robinhood.com/ach/transfers/",
        "applications": "https://api.robinhood.com/applications/",
        "dividends": "https://api.robinhood.com/dividends/",
        "edocuments": "https://api.robinhood.com/documents/",
        "instruments": "https://api.robinhood.com/instruments/",
        "margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
        "markets": "https://api.robinhood.com/markets/",
        "notifications": "https://api.robinhood.com/notifications/",
        "orders": "https://api.robinhood.com/orders/",
        "password_reset": "https://api.robinhood.com/password_reset/request/",
        "portfolios": "https://api.robinhood.com/portfolios/",
        "positions": "https://api.robinhood.com/positions/",
        "quotes": "https://api.robinhood.com/quotes/",
        "historicals": "https://api.robinhood.com/quotes/historicals/",
        "document_requests": "https://api.robinhood.com/upload/document_requests/",
        "user": "https://api.robinhood.com/user/",
        "watchlists": "https://api.robinhood.com/watchlists/",
        "news": "https://api.robinhood.com/midlands/news/"
    }

    session = None

    username = None

    password = None

    headers = None

    auth_token = None


    ##############################
    #Logging in and initializing
    ##############################

    def __init__(self):
        self.session = requests.session()
        try:
            self.session.proxies = urllib.getproxies()  # py2
        except:
            self.session.proxies = urllib.request.getproxies()  # py3
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.0.0",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
        }
        self.session.headers = self.headers

    def login_prompt(self):
        """Prompts user for username and password and calls login()."""
        username = raw_input("Username: ")
        password = getpass.getpass()
        return self.login(username=username, password=password)

    def login(self, username, password, mfa_code=None):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code
        # fields = { 'password' : self.password, 'username' : self.username, 'mfa_code': self.mfa_code }
        # fields = { 'password' : self.password, 'username' : self.username }

        if mfa_code:
            fields = {'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
                      'expires_in': 86400,
                      'grant_type': 'password',
                      'password': self.password,
                      'scope': 'internal',
                      'username': self.username,
                      'mfa_code': self.mfa_code}
        else:
            fields = {'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
                      'expires_in': 86400,
                      'grant_type': 'password',
                      'password': self.password,
                      'scope': 'internal',
                      'username': self.username}
        try:
            data = urllib.urlencode(fields)  # py2
        except:
            data = urllib.parse.urlencode(fields)  # py3

        res = self.session.post(self.endpoints['login'], data=data)
        res = res.json()
        try:
            # self.auth_token = res['token']
            self.auth_token = res['access_token']
        except KeyError:
            return res
        # self.headers['Authorization'] = 'Token '+self.auth_token
        self.headers['Authorization'] = 'Bearer ' + self.auth_token
        return True

    ##############################
    # GET DATA 
    ##############################

    def investment_profile(self):
        self.session.get(self.endpoints['investment_profile'])

    def instruments(self, stock=None):
        res = self.session.get(
            self.endpoints['instruments'],
            params={'query': stock.upper()})
        res = res.json()
        return res['results']

    def quote_data(self, stock=None):
        # Prompt for stock if not entered
        if stock is None:
            stock = raw_input("Symbol: ")
        url = str(self.endpoints['quotes']) + str(stock) + "/"
        # Check for validity of symbol
        try:
            res = requests.get(url).json()
            if len(res) > 0:
                return res
            else:
                raise NameError("Invalid Symbol: " + stock)
        except (ValueError):
            raise NameError("Invalid Symbol: " + stock)

    def get_quote(self, stock=None):
        data = self.quote_data(stock)
        return data["symbol"]

    def get_symbol_by_instrument(self, url=None):
        return requests.get(url).json()['symbol']

    def get_name_by_instrument(self, url=None):
        return requests.get(url).json()['name']

    def get_historical_quotes(self, symbol, interval, span, bounds='regular'):
        # Valid combination
        # interval = 5minute | 10minute + span = day, week
        # interval = day + span = year
        # interval = week
        # bounds can be 'regular' for regular hours or 'extended' for extended hours
        res = self.session.get(
            self.endpoints['historicals'],
            params={
                'symbols': ','.join(symbol).upper(),
                'interval': interval, 'span': span, 'bounds': bounds
            })
        return res.json()

    def get_news(self, symbol):
        return self.session.get(self.endpoints['news']+symbol.upper()+"/").json()

    def print_quote(self, stock=None):
        data = self.quote_data(stock)
        print(data["symbol"] + ": $" + data["last_trade_price"])

    def print_quotes(self, stocks):
        for i in range(len(stocks)):
            self.print_quote(stocks[i])

    def ask_price(self, stock=None):
        return float(self.quote_data(stock)['ask_price'])

    def ask_size(self, stock=None):
        return float(self.quote_data(stock)['ask_size'])

    def bid_price(self, stock=None):
        return float(self.quote_data(stock)['bid_price'])

    def bid_size(self, stock=None):
        return float(self.quote_data(stock)['bid_size'])

    def last_trade_price(self, stock=None):
        return float(self.quote_data(stock)['last_trade_price'])

    def previous_close(self, stock=None):
        return float(self.quote_data(stock)['previous_close'])

    def previous_close_date(self, stock=None):
        return self.quote_data(stock)['previous_close_date']

    def adjusted_previous_close(self, stock=None):
        return float(self.quote_data(stock)['adjusted_previous_close'])

    def symbol(self, stock=None):
        return self.quote_data(stock)['symbol']

    def last_updated_at(self, stock=None):
        return self.quote_data(stock)['updated_at']

    def get_account(self):
        res = self.session.get(self.endpoints['accounts'])
        res = res.json()
        return res['results'][0]

    def get_url(self,url):
        return self.session.get(url).json()

    ##############################
    # PORTFOLIOS DATA
    ##############################

    def portfolios(self):
        """Returns the user's portfolio data."""
        return self.session.get(
            self.endpoints['portfolios']).json()['results'][0]

    def adjusted_equity_previous_close(self):
        return float(self.portfolios()['adjusted_equity_previous_close'])

    def equity(self):
        return float(self.portfolios()['equity'])

    def equity_previous_close(self):
        return float(self.portfolios()['equity_previous_close'])

    def excess_margin(self):
        return float(self.portfolios()['excess_margin'])

    def extended_hours_equity(self):
        return float(self.portfolios()['extended_hours_equity'])

    def extended_hours_market_value(self):
        return float(self.portfolios()['extended_hours_market_value'])

    def last_core_equity(self):
        return float(self.portfolios()['last_core_equity'])

    def last_core_market_value(self):
        return float(self.portfolios()['last_core_market_value'])

    def market_value(self):
        return float(self.portfolios()['market_value'])

    def order_history(self):
        return self.session.get(self.endpoints['orders']).json()

    def dividends(self):
        return self.session.get(self.endpoints['dividends']).json()

    ##############################
    # POSITIONS DATA
    ##############################

    def positions(self):
        """Returns the user's positions data."""
        return self.session.get(self.endpoints['positions']).json()

    def securities_owned(self):
        """
        Returns a list of symbols of securities of which there are more
        than zero shares in user's portfolio.
        """
        positions = self.positions()
        securities = []
        for position in positions['results']:
            quantity = float(position['quantity'])
            if quantity > 0:
                securities.append(
                    self.session.get(position['instrument']).json()['symbol'])
        return securities
