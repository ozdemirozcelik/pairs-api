"""
Routes and functions used for the frontend demo
"""
import os
from app import app, configs
from flask import render_template, request, flash, redirect, url_for
from models.signals import SignalModel
from models.tickers import TickerModel
from models.account import AccountModel
from models.pairs import PairModel
from models.session import SessionModel
from datetime import datetime
from datetime import timedelta
import pytz
from pytz import timezone
import pandas as pd
import yfinance as yf


@app.route("/")
def home():
    return redirect("/dashboard")


@app.get("/dashboard")
def dashboard():
    # (flask-session-change) Flask sessions may not be persistent in Heroku
    # consider disabling below for Heroku

    ##
    # if session.get("token") is None:
    #     session["token"] = None
    #
    # if session["token"] == "yes_token":
    #     items = SignalModel.get_rows(str(50))
    # else:
    #     items = SignalModel.get_rows(str(5))
    #     flash("Login to see more!", "login_for_more")
    #
    # signals = [item.json() for item in items]
    ##

    # consider enabling below for Heroku:
    # this method uses a simple custom session table created in the database

    access_token = request.cookies.get("access_token")

    SessionModel.delete_expired()  # clean expired session data

    if access_token:
        simplesession = SessionModel.find_by_value(access_token[-10:])
    else:
        simplesession = None

    if simplesession:
        items = SignalModel.get_rows(str(20))

    else:
        items = SignalModel.get_rows(str(5))
        flash("Login to see more rows!", "login_for_more")

    signals = [item.json() for item in items]

    return render_template(
        "dash.html",
        signals=signals,
        title="DASHBOARD",
        tab1="tab active",
        tab2="tab",
        tab3="tab",
        tab4="tab",
    )


@app.get("/list")
def dashboard_list():
    # (flask-session-change) Flask sessions may not be persistent in Heroku
    # consider disabling below for Heroku

    ##
    # selected_ticker = request.args.get('ticker_webhook')

    # if session.get("token") is None:
    #     session["token"] = None
    #
    # if session["token"] == "yes_token":
    #     items = SignalModel.get_list_ticker(selected_ticker,"0")
    # else:
    #     items = SignalModel.get_list_ticker(selected_ticker,"5")
    #     flash("Login to see more!", "login_for_more")
    #
    # signals = [item.json() for item in items]
    ##

    # consider enabling below for Heroku:
    # this method uses a simple custom session table created in the database

    # get form submission
    selected_ticker = request.args.get("ticker_webhook")
    selected_trade_type = request.args.get("tradetype")
    start_date_selected = request.args.get("start_date")
    end_date_selected = request.args.get("end_date")

    date_format = "%Y-%m-%d"

    try:
        start_date = start_date_selected.split(".")[
            0
        ]  # clean the timezone info if necessary
        start_date = datetime.strptime(
            start_date, date_format
        )  # convert string to timestamp
        end_date = end_date_selected.split(".")[
            0
        ]  # clean the timezone info if necessary
        end_date = datetime.strptime(
            end_date, date_format
        )  # convert string to timestamp
        end_date = end_date + timedelta(
            days=1
        )  # Add 1 day to "%Y-%m-%d" 00:00:00 to reach end of day

    except Exception as e:
        print("Error occurred - ", e)
        start_date = datetime.now(tz=pytz.utc) - timedelta(days=1)
        date_now = datetime.now(tz=pytz.utc)
        date_now_formatted = date_now.strftime(date_format)  # format as string
        start_date = datetime.strptime(
            date_now_formatted, date_format
        )  # convert to timestamp
        end_date = start_date + timedelta(days=1)  # Today end of day

    access_token = request.cookies.get("access_token")

    SessionModel.delete_expired()  # clean expired session data

    if access_token:
        simplesession = SessionModel.find_by_value(access_token[-10:])
    else:
        simplesession = None

    if selected_ticker:

        slip_dic = SignalModel.get_avg_slip(selected_ticker, start_date, end_date)

        if simplesession:
            items = SignalModel.get_list_ticker_dates(
                selected_ticker, "0", start_date, end_date
            )
        else:
            items = SignalModel.get_list_ticker_dates(
                selected_ticker, "5", start_date, end_date
            )
            flash("Login to see more rows!", "login_for_more")
    else:
        return render_template(
            "list.html",
            title="LIST SIGNALS",
            tab2="tab active",
            tab1="tab",
            tab3="tab",
            tab4="tab",
        )

    signals = [item.json() for item in items]

    slip_buy = "?"
    slip_sell = "?"
    slip_avg = "?"

    if slip_dic["buy"]:
        slip_buy = str(round(slip_dic["buy"], 5))
    if slip_dic["sell"]:
        slip_sell = str(round(slip_dic["sell"], 5))
    if slip_dic["avg"]:
        slip_avg = str(round(slip_dic["avg"], 5))

    return render_template(
        "list.html",
        signals=signals,
        title="LIST SIGNALS",
        tab1="tab",
        tab2="tab active",
        tab3="tab",
        tab4="tab",
        start_date=start_date,
        end_date=end_date - timedelta(days=1),
        selected_ticker=selected_ticker,
        selected_trade_type=selected_trade_type,
        slip_buy=slip_buy,
        slip_sell=slip_sell,
        slip_avg=slip_avg,
    )


@app.get("/positions")
def positions():
    # (flask-session-change) Flask sessions may not be persistent in Heroku
    # consider disabling below for Heroku

    ##
    # if session.get("token") is None:
    #     session["token"] = None
    #
    # if session["token"] == "yes_token":
    #     items = SignalModel.get_rows(str(50))
    # else:
    #     items = SignalModel.get_rows(str(5))
    #     flash("Login to see more!", "login_for_more")
    #
    # signals = [item.json() for item in items]
    ##

    # consider enabling below for Heroku:
    # this method uses a simple custom session table created in the database

    access_token = request.cookies.get("access_token")

    SessionModel.delete_expired()  # clean expired session data

    if access_token:
        simplesession = SessionModel.find_by_value(access_token[-10:])
    else:
        simplesession = None

    pnl = {
        "rowid": "NA",
    }

    if simplesession:
        active_tickers = TickerModel.get_active_tickers(str(20))
        active_pairs = PairModel.get_active_pairs(str(20))
        acc_pnl = AccountModel.get_rows(str(1))

        # having index problems with heroku deployment with the following.
        # len() doesn't work.
        # if acc_pnl[0]:
        #     pnl = acc_pnl[0].json()

        # using this instead:
        try:
            pnl = acc_pnl[0].json()
        except IndexError:
            pass

    else:
        active_tickers = TickerModel.get_active_tickers(str(3))
        active_pairs = PairModel.get_active_pairs(str(3))

        flash("Login to see PNL details", "login_for_pnl")
        flash("Login to see more positions!", "login_for_more")

    pair_pos_all = []
    sum_act_sma = 0

    for pair in active_pairs:
        pair_pos_all.append(
            {
                "pair": pair.json(),
                "ticker1": TickerModel.find_by_symbol(pair.ticker1).json(),
                "ticker2": TickerModel.find_by_symbol(pair.ticker2).json(),
            }
        )

        if pair.status == 1 and pair.sma_dist:
            act_pos = TickerModel.find_by_symbol(pair.ticker1).active_pos
            sum_act_sma = sum_act_sma + pair.sma_dist * act_pos

    # pair_pairs_ticker = []
    #
    # for item in active_pairs:
    #     pair_pairs_ticker.append(TickerModel.find_by_symbol(item.ticker1).json())
    #     pair_pairs_ticker.append(TickerModel.find_by_symbol(item.ticker2).json())

    other_pos = [item.json() for item in active_tickers]

    resolution = "5m"
    tickersfile = "tickers_" + resolution.upper() + ".csv"

    # TODO: os.path changes depending on the server. use a better method
    # if os.path.exists("app"):
    #     tickersfile = "app/tickers_" + resolution.upper() + ".csv"

    if os.path.exists(tickersfile):
        prices = pd.read_csv(tickersfile, index_col="time")
        last_price_update = prices.index[-1]
    else:
        last_price_update = ""

    print(last_price_update)

    # TODO: add ceiling to the account history

    return render_template(
        "pos.html",
        pair_pos_all=pair_pos_all,
        other_pos=other_pos,
        pnl=pnl,
        sum_act_sma=sum_act_sma,
        last_price_update=last_price_update,
        title="POSITIONS",
        tab1="tab",
        tab2="tab",
        tab3="tab active",
        tab4="tab",
    )


@app.get("/watchlist")
def watchlist():
    access_token = request.cookies.get("access_token")

    SessionModel.delete_expired()  # clean expired session data

    if access_token:
        simplesession = SessionModel.find_by_value(access_token[-10:])
    else:
        simplesession = None

    if simplesession:
        # watchlist_tickers = TickerModel.get_watchlist_tickers(str(40))
        watchlist_pairs = PairModel.get_watchlist_pairs(str(40))

    else:
        # watchlist_tickers = TickerModel.get_watchlist_tickers(str(5))
        watchlist_pairs = PairModel.get_watchlist_pairs(str(5))

        flash("Login to update!", "login_to_update")
        flash("Login to see more!", "login_for_more")

    pair_pos_all = []

    for pair in watchlist_pairs:
        pair_pos_all.append(
            {
                "pair": pair.json(),
                "ticker1": TickerModel.find_by_symbol(pair.ticker1).json(),
                "ticker2": TickerModel.find_by_symbol(pair.ticker2).json(),
            }
        )

    # other_pos = [item.json() for item in watchlist_tickers]

    resolution = "5m"
    tickersfile = "watchlist_" + resolution.upper() + ".csv"

    # TODO: os.path changes depending on the server. use a better method
    if os.path.exists(tickersfile):
        prices = pd.read_csv(tickersfile, index_col="time")
        last_price_update = prices.index[-1]
    else:
        last_price_update = ""

    print(last_price_update)

    return render_template(
        "watch.html",
        pair_pos_all=pair_pos_all,
        last_price_update=last_price_update,
        title="WATCHLIST",
        tab1="tab",
        tab2="tab",
        tab3="tab",
        tab4="tab active",
    )


@app.get("/setup")
def setup():
    # (flask-session-change) session may not be persistent in Heroku
    # consider disabling below for Heroku

    ##
    # if session.get("token") is None:
    #     session["token"] = None
    #
    # if session["token"] == "yes_token":
    #     return render_template("setup.html")
    # else:
    #     # show login message and bo back to dashboard
    #     flash("Please login!","login")
    #     return redirect(url_for('dashboard'))
    ##

    # consider enabling below for Heroku:
    # this method does not confirm the session on the server side
    # JWT tokens are still needed for API, so no need to worry

    access_token = request.cookies.get("access_token")

    if access_token:
        return render_template("setup.html")
    else:
        # show login message and bo back to dashboard
        flash("Please login!", "login")
        return redirect(url_for("dashboard"))


@app.get("/sma")
def calculate_sma_dist():
    try:
        calculate_sma_distance()
    except Exception as e:
        print("***Calculate Err***")
        print(e)

    return redirect(url_for("positions"))


@app.get("/update_watchlist")
def update_watchlist():
    try:
        calculate_watchlist()
    except Exception as e:
        print("***Calculate Err***")
        print(e)

    return redirect(url_for("watchlist"))


# TEMPLATE FILTERS BELOW:

# check if the date is today's date
@app.template_filter("iftoday")
def iftoday(value):
    date_format = "%Y-%m-%d %H:%M:%S"
    value = value.split(".")[0]  # clean the timezone info if necessary
    date_signal = datetime.strptime(value, date_format)  # convert string to timestamp

    date_now = datetime.now(tz=pytz.utc)
    date_now_formatted = date_now.strftime(date_format)  # format as string
    date_now_final = datetime.strptime(
        date_now_formatted, date_format
    )  # convert to timestamps

    if (date_now_final.day == date_signal.day) and (
        date_now_final.month == date_signal.month
    ):
        return True
    else:
        return False


# edit the timezone to display at the dashboard, default from UTC to PCT
@app.template_filter("pct_time")
def pct_time(value, fromzone="UTC"):
    date_format = "%Y-%m-%d %H:%M:%S"
    value = value.split(".")[0]  # clean the timezone info if necessary
    date_signal = datetime.strptime(value, date_format)  # convert string to timestamp
    if fromzone == "EST":
        date_signal_utc = date_signal.replace(
            tzinfo=pytz.timezone("US/Eastern")
        )  # add tz info
    else:
        date_signal_utc = date_signal.replace(tzinfo=pytz.UTC)  # add tz info
    date_pct = date_signal_utc.astimezone(timezone("US/Pacific"))  # change tz
    date_final = date_pct.strftime(date_format)  # convert to str

    if value is None:
        return ""
    return date_final


# calculate time difference in minutes, default is from UTC
@app.template_filter("timediff")
def timediff(value, fromzone="UTC"):
    date_format = "%Y-%m-%d %H:%M:%S"

    try:
        value = value.split(".")[0]  # clean the timezone info if necessary

        date_signal = datetime.strptime(
            value, date_format
        )  # convert string to timestamp

        if fromzone == "EST":
            date_now = datetime.now(tz=pytz.timezone("US/Eastern"))
        else:
            date_now = datetime.now(tz=pytz.utc)

        date_now_formatted = date_now.strftime(date_format)  # format as string
        date_now_final = datetime.strptime(
            date_now_formatted, date_format
        )  # convert to timestamp

        date_diff = (date_now_final - date_signal).total_seconds() / 60.0

    except Exception as e:
        print("Error occurred - ", e)
        return ""

    return round(date_diff)


# SMA Calculation


def SMA(values, n):
    sma = pd.Series(values).rolling(n).mean()
    std = (
        pd.Series(values).rolling(n).std(ddof=1)
    )  # default ddof=1, sample standard deviation, divide by (n-1)
    return sma, std


def download_data(tickerStrings, int_per, file_name):
    print(tickerStrings)

    df_list = list()

    for key in int_per:
        for ticker in tickerStrings:
            data = yf.download(
                ticker, group_by="Ticker", period=int_per[key], interval=key
            )
            data["ticker"] = ticker
            data.index.names = ["time"]

            df_list.append(data)

        # combine all dataframes into a single dataframe
        df_download = pd.concat(df_list)

        # save to csv
        df_download.to_csv(file_name + "_" + key.upper() + ".csv")

        df_list = []


def calculate_sma(pairs, file_name="tickers"):
    print("***Calculate SMA***")
    resolution_sma = "1d"
    int_per_sma = {resolution_sma: "3mo"}  # define interval and corresponding period

    tickerStrings_sma = []

    for pair in pairs:
        tickerStrings_sma.append(pair.ticker1)
        tickerStrings_sma.append(pair.ticker2)

    download_data(tickerStrings_sma, int_per_sma, file_name)

    alltickersfile_sma = file_name + "_" + resolution_sma.upper() + ".csv"
    df_sma = pd.read_csv(alltickersfile_sma)

    for pair in pairs:

        df_sorted_sma = df_sma.set_index(["ticker", "time"]).sort_index()  # set indexes
        df1_sorted_sma = df_sorted_sma.xs(pair.ticker2)  # the first ticker
        df2_sorted_sma = df_sorted_sma.xs(pair.ticker1)  # the second ticker

        df1_sma = pair.hedge * df1_sorted_sma
        df_spread_sma = df2_sorted_sma.subtract(df1_sma).round(5)

        df_spread_sma["sma_20"], df_spread_sma["std"] = SMA(df_spread_sma.Close, 20)

        if resolution_sma.upper() == "1H":
            df_spread_sma["sma_20d"], df_spread_sma["std"] = SMA(
                df_spread_sma.Close, 20 * 7
            )  # add 20d sma for 1H only

        pair.sma = round(df_spread_sma.iloc[-1, :]["sma_20"], 5)
        pair.std = round(df_spread_sma.iloc[-1, :]["std"], 5)
        pair.update()


def calculate_price(pairs, file_name="tickers"):
    print("***Calculate Price***")
    resolution = "5m"
    int_per = {resolution: "1d"}  # define interval and corresponding period

    tickerStrings = []

    for pair in pairs:
        tickerStrings.append(pair.ticker1)
        tickerStrings.append(pair.ticker2)

    download_data(tickerStrings, int_per, file_name)

    alltickersfile = file_name + "_" + resolution.upper() + ".csv"
    df = pd.read_csv(alltickersfile)

    for pair in pairs:

        df_sorted = df.set_index(["ticker", "time"]).sort_index()  # set indexes
        df1_sorted = df_sorted.xs(pair.ticker1)  # the first ticker
        df2_sorted = df_sorted.xs(pair.ticker2)  # the second ticker

        ticker1_price = df1_sorted.iloc[-1, :]["Close"]
        ticker2_price = df2_sorted.iloc[-1, :]["Close"]

        pair.act_price = round(ticker1_price - ticker2_price * pair.hedge, 4)
        pair.update()

        # print(pair.act_price)

        if pair.sma:
            pair.sma_dist = round(pair.sma - pair.act_price, 4)
        else:
            pair.sma_dist = 0

        pair.update()


def calculate_sma_distance():
    with app.app_context():  # being executed outside the app context

        session_start = configs.get("EXCHANGE", "SESSION_START")
        session_end = configs.get("EXCHANGE", "SESSION_END")
        session_extension_min = int(configs.get("EXCHANGE", "SESSION_EXTENSION_MIN"))
        exchange_timezone = configs.get("EXCHANGE", "EXCHANGE_TIMEZONE")
        date_format = "%H:%M:%S"

        date_now = datetime.now(tz=pytz.timezone(exchange_timezone))
        date_now_formatted = date_now.strftime(date_format)  # format as string
        date_now_final = datetime.strptime(
            date_now_formatted, date_format
        )  # convert to timestamps

        weekday = date_now.isoweekday()
        print("Day of the week: ", str(weekday))

        session_start_final = datetime.strptime(
            session_start, date_format
        )  # convert to timestamps
        session_end_final = datetime.strptime(
            session_end, date_format
        )  # convert to timestamps

        since_start = date_now_final - session_start_final
        until_end = session_end_final - date_now_final

        print("Since start: ", since_start)
        print("Until end: ", until_end)

        if (
            int(weekday) < 6
            and since_start > -timedelta(minutes=session_extension_min)
            and until_end > -timedelta(minutes=session_extension_min)
        ):

            active_pairs_sma = PairModel.get_active_pairs(str(20))

            print("***Calculate Start***")
            try:
                calculate_sma(active_pairs_sma)
                calculate_price(active_pairs_sma)
                print("***Calculate End***")
            except Exception as e:
                print("***Calculate Err***")
                print(e)
        else:
            print("***No Calculation***")


def calculate_watchlist():
    with app.app_context():  # being executed outside the app context

        watchlist_pairs = PairModel.get_watchlist_pairs(str(40))

        print("***Calculate Watchlist Start***")
        try:
            calculate_sma(watchlist_pairs, "watchlist")
            calculate_price(watchlist_pairs, "watchlist")
            print("***Calculate End***")
        except Exception as e:
            print("***Calculate Err***")
            print(e)


# scheduler for email notifications and sma calculation below

from apscheduler.schedulers.background import BackgroundScheduler


@app.before_first_request
def init_scheduler():

    # details: https://betterprogramming.pub/introduction-to-apscheduler-86337f3bb4a6
    scheduler = BackgroundScheduler()
    # Check if email notifications are enabled for waiting/problematic orders
    if configs.getboolean("EMAIL", "ENABLE_EMAIL_NOTIFICATIONS"):
        import notify

        scheduler.add_job(
            notify.warning_email_context,
            "interval",
            seconds=int(configs.get("EMAIL", "MAIL_CHECK_PERIOD")),
        )
    # Check if enabled to calculate pair price distance to SMA (20 days moving average)
    if configs.getboolean("SMA", "ENABLE_SMA_CALC"):
        scheduler.add_job(
            calculate_sma_distance,
            "interval",
            minutes=int(configs.get("SMA", "SMA_CALC_PERIOD")),
        )

    scheduler.start()
    # sched.shutdown()
