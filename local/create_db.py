import sqlite3

# Run this code to create "data.db" database, then "signals", "pairs" and "stocks" tables
# To reset the current db, delete the old db and run this code again

# SIGNALS table includes the trading signals and relevant information explained as follows:
# (* for webhook)
# (** for webhook required, webhook also requires a 'passphrase' key which is not recorded in the database)

# rowid: SQLite adds an implicit column called rowid as 64-bit signed integer if WITHOUT ROWID option is not specified.
#        'rowid' is used as the key that uniquely identifies the rows in the table, works faster than using primary key.
# timestamp: DEFAULT TIMESTAMP in GMT
# **ticker: TEXT such as ""NYSE:MA" or
#           TEXT such as "NYSE:MA-1.6*NYSE:V" to be split into stock tickers and hedge amount as (MA,V,1.6)
# **order_action: "buy" or "sell" as TEXT
# **order_contracts: number of contracts to trade as NUMERIC
# **order_price: trigger price (stock price or pair price) of the trading signal as NUMERIC
# **mar_pos: market position as TEXT after the trade is executed
# **mar_pos_size: market position size as NUMERIC (after the order is fulfilled)
# **pre_mar_pos: market position as TEXT before the trade is executed
# **pre_mar_pos_size: market position size as NUMERIC (before the order is fulfilled)
# *order_comment: comment as TEXT
# *order_status: order status such as "filled", "waiting" etc. as TEXT

# Below values to be added later:
# ticker_type: "single" or "pair" as TEXT
# stk_ticker1: stock 1 symbol parsed from ticker as TEXT
# stk_ticker2: stock 2 symbol parsed from ticker as TEXT (if ticker_type is "pair")
# hedge_param: hedge parameter parsed from ticker as NUMERIC (if ticker_type is "pair")
# order_id1: order id created by trading API for stock 1 as NUMERIC
# order_id2: order id created by trading API for stock 2 as NUMERIC (if ticker_type is "pair")
# stk_price1: fill price of order_id1 as NUMERIC
# stk_price2: fill price of order_id2 as NUMERIC (if ticker_type is "pair")
# fill_price: fill price (stock price or pair price) of the trade as NUMERIC
# slip: difference btw order_price and fill_price AS NUMERIC
# error_msg: warnings or error messages kept as TEXT

# SQLite adds an implicit column called rowid as 64-bit signed integer if WITHOUT ROWID option is not specified.
# 'rowid' is used as the key that uniquely identifies the rows in the table, mainly because it is faster than using a
# primary key.

# PAIRS table includes the pair codes and relevant information explained as follows:
# name: name of the pair such as "MA-V" as TEXT
# hedge: hedge parameter of pair as NUMERIC
# status: to define the pair trade is active (1) or passive (0) as INTEGER (BOOLEAN)

# STOCKS table includes the stock codes and relevant information explained as follows:
# symbol: ticker symbol of the stock as TEXT
# prixch: primary exchange to trade as TEXT
# secxch: secondary exchange to trade as TEXT
# active: to define if single trade is active (1) or not (0) as INTEGER (BOOLEAN).
#        If active (1) then trade as single stock, if not (0) then check pair status

# TODO: complete comments
# USERS table includes ...


connection = sqlite3.connect('../data.db')

try:
    cursor = connection.cursor()

    create_signals = """
            CREATE TABLE IF NOT EXISTS signals (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                ticker TEXT,
                order_action TEXT,
                order_contracts NUMERIC,
                order_price NUMERIC,
                mar_pos TEXT,
                mar_pos_size NUMERIC,
                pre_mar_pos TEXT,
                pre_mar_pos_size NUMERIC,
                order_comment TEXT,
                order_status TEXT
            )
        """
    # ticker_type TEXT,
    # stk_ticker1 TEXT,
    # stk_ticker2 TEXT,
    # hedge_param NUMERIC,
    # order_id1 NUMERIC,
    # order_id2 NUMERIC,
    # stk_price1 NUMERIC,
    # stk_price2 NUMERIC,
    # fill_price NUMERIC,
    # slip NUMERIC,
    # error_msg TEXT

    cursor.execute(create_signals)

    # TODO: you can include stock names and a foreign key. do you need it?
    create_pairs = "CREATE TABLE IF NOT EXISTS pairs (name TEXT PRIMARY KEY, hedge NUMERIC, status INTEGER)"

    cursor.execute(create_pairs)

    create_stocks = "CREATE TABLE IF NOT EXISTS stocks (symbol TEXT PRIMARY KEY, prixch TEXT, secxch TEXT, " \
                    "active INTEGER) "

    cursor.execute(create_stocks)

    # TODO: is it possible to encrypt the password?
    create_users = "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)"

    # TODO: create master password here?

    cursor.execute(create_users)

    print('tables (for signals, pairs, stocks, users) are created')

    query = "INSERT INTO {table} VALUES(?, ?),(?, ?)".format(table='users')

    cursor.execute(query, ("admin", "123", "user1", "123"))

    connection.commit()

    print('admin and user1 is created')

except sqlite3.Error as error:
    print('Error occurred during db creation - ', error)

finally:
    if connection:
        connection.close()
        print('SQLite Connection closed')
