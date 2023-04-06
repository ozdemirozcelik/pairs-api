"""
Test Factory to make fake objects for testing
"""
import datetime as dt
import pytz
import factory
from factory.fuzzy import BaseFuzzyAttribute
import string
import random
from services.models.tickers import TickerModel
from services.models.pairs import PairModel
from services.models.signals import SignalModel
from services.models.users import UserModel
from services.models.account import AccountModel
from services.models.session import SessionModel

sec_types = ["STK", "CASH", "CRYPTO"]
xch_types = ["SMART", "NASDAQ", "NYSE", "ISLAND", "BYX"]
cur_types = ["USD", "EUR", "CAD"]
ord_types = ["RELATIVE", "MARKET", "LIMIT"]
ord_act_types = ["buy", "sell"]
mar_pos_types = ["flat", "short", "long"]
ticker_types = ["pair", "single"]


class FuzzyPairName(BaseFuzzyAttribute):
    def __init__(
        self, length=7, prefix="", suffix="", infix="-", chars=string.ascii_letters
    ):
        super().__init__()
        self.prefix = prefix
        self.suffix = suffix
        self.infix = infix
        self.length = min(3, length)
        self.chars = tuple(chars)  # Unroll iterators

    def fuzz(self):
        chars1 = [
            factory.random.randgen.choice(self.chars) for _i in range(self.length // 2)
        ]
        chars2 = [
            factory.random.randgen.choice(self.chars) for _i in range(self.length // 2)
        ]
        return (
            self.prefix + "".join(chars1) + self.infix + "".join(chars2) + self.suffix
        )


class FuzzySignalTicker(BaseFuzzyAttribute):
    def __init__(self, infix1="-", infix2="*"):
        super().__init__()
        self.infix1 = infix1
        self.infix2 = infix2
        self.chars = tuple(string.ascii_letters)  # Unroll iterators

    def fuzz(self):
        hedge = str(round(random.uniform(1, 5), 2))
        chars1 = [factory.random.randgen.choice(self.chars) for _i in range(3)]
        chars2 = [factory.random.randgen.choice(self.chars) for _i in range(3)]
        return "".join(chars1) + self.infix1 + hedge + self.infix2 + "".join(chars2)


class UserFactory(factory.Factory):
    """Creates fake Users"""

    class Meta:
        """Persistent class for factory"""

        model = UserModel

    username = factory.fuzzy.FuzzyText(length=6, chars=string.ascii_letters, prefix="")
    password = factory.fuzzy.FuzzyText(length=6, chars=string.ascii_letters, prefix="")


class TickerFactory(factory.Factory):
    """Creates fake Tickers"""

    class Meta:
        """Persistent class for factory"""

        model = TickerModel

    symbol = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_letters, prefix="")
    sectype = factory.fuzzy.FuzzyChoice(choices=sec_types)
    xch = factory.fuzzy.FuzzyChoice(choices=xch_types)
    prixch = factory.fuzzy.FuzzyChoice(choices=xch_types)
    currency = factory.fuzzy.FuzzyChoice(choices=cur_types)
    active = 0
    order_type = factory.fuzzy.FuzzyChoice(choices=ord_types)
    active_pos = factory.fuzzy.FuzzyInteger(low=0, high=100, step=1)
    active_pnl = factory.fuzzy.FuzzyInteger(low=-100, high=100, step=1)
    active_cost = factory.fuzzy.FuzzyDecimal(low=10.0, high=100.0, precision=2)


class PairFactory(factory.Factory):
    """Creates fake Pairs"""

    class Meta:
        """Persistent class for factory"""

        model = PairModel

    name = FuzzyPairName(length=7, infix="-")
    hedge = factory.fuzzy.FuzzyDecimal(low=0.8, high=4.0, precision=1)
    status = 0
    ticker1 = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_letters, prefix="")
    ticker2 = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_letters, prefix="")
    notes = factory.fuzzy.FuzzyText(length=15, chars=string.ascii_letters, prefix="")
    contracts = factory.fuzzy.FuzzyInteger(low=5, high=100, step=1)
    act_price = factory.fuzzy.FuzzyDecimal(low=-10.0, high=10.0, precision=3)
    sma = factory.fuzzy.FuzzyDecimal(low=-5.0, high=5.0, precision=3)
    sma_dist = factory.fuzzy.FuzzyDecimal(low=-2.0, high=2.0, precision=3)
    std = factory.fuzzy.FuzzyDecimal(low=0.0, high=3.0, precision=3)


class SignalFactory(factory.Factory):
    """Creates fake Signals"""

    class Meta:
        """Persistent class for factory"""

        model = SignalModel

    timestamp = factory.fuzzy.FuzzyDateTime(
        start_dt=dt.datetime(2022, 1, 1, tzinfo=pytz.UTC)
    )
    ticker = FuzzySignalTicker(infix1="-", infix2="*")
    order_action = factory.fuzzy.FuzzyChoice(choices=ord_act_types)
    order_contracts = factory.fuzzy.FuzzyInteger(low=5, high=100, step=1)
    order_price = factory.fuzzy.FuzzyDecimal(low=-10.0, high=10.0, precision=3)
    mar_pos = factory.fuzzy.FuzzyChoice(choices=mar_pos_types)
    mar_pos_size = factory.fuzzy.FuzzyInteger(low=5, high=100, step=1)
    pre_mar_pos = factory.fuzzy.FuzzyChoice(choices=mar_pos_types)
    pre_mar_pos_size = factory.fuzzy.FuzzyInteger(low=5, high=100, step=1)
    order_comment = factory.fuzzy.FuzzyText(
        length=15, chars=string.ascii_letters, prefix=""
    )
    order_status = factory.fuzzy.FuzzyText(
        length=15, chars=string.ascii_letters, prefix=""
    )
    ticker_type = factory.fuzzy.FuzzyChoice(choices=ticker_types)
    ticker1 = factory.fuzzy.FuzzyText(length=3, chars=string.ascii_letters, prefix="")
    ticker2 = factory.fuzzy.FuzzyText(length=3, chars=string.ascii_letters, prefix="")
    hedge_param = factory.fuzzy.FuzzyDecimal(low=0.8, high=4.0, precision=1)
    order_id1 = factory.fuzzy.FuzzyInteger(low=5, high=100, step=1)
    order_id2 = factory.fuzzy.FuzzyInteger(low=5, high=100, step=1)
    price1 = factory.fuzzy.FuzzyDecimal(low=10.0, high=100.0, precision=3)
    price2 = factory.fuzzy.FuzzyDecimal(low=10.0, high=100.0, precision=3)
    fill_price = factory.fuzzy.FuzzyDecimal(low=-10.0, high=10.0, precision=3)
    slip = factory.fuzzy.FuzzyDecimal(low=-1.0, high=1.0, precision=3)
    error_msg = factory.fuzzy.FuzzyText(
        length=15, chars=string.ascii_letters, prefix=""
    )
    status_msg = factory.fuzzy.FuzzyText(
        length=15, chars=string.ascii_letters, prefix=""
    )


class AccountFactory(factory.Factory):
    """Creates fake Tickers"""

    class Meta:
        """Persistent class for factory"""

        model = AccountModel

    timestamp = factory.fuzzy.FuzzyDateTime(
        start_dt=dt.datetime(2022, 1, 1, tzinfo=pytz.UTC)
    )
    AvailableFunds = factory.fuzzy.FuzzyDecimal(low=0.0, high=10000.0, precision=2)
    BuyingPower = factory.fuzzy.FuzzyDecimal(low=0.0, high=30000.0, precision=2)
    DailyPnL = factory.fuzzy.FuzzyDecimal(low=-1000.0, high=1000.0, precision=2)
    GrossPositionValue = factory.fuzzy.FuzzyDecimal(low=0.0, high=25000.0, precision=2)
    MaintMarginReq = factory.fuzzy.FuzzyDecimal(low=0.0, high=10000.0, precision=2)
    NetLiquidation = factory.fuzzy.FuzzyDecimal(low=0.0, high=30000.0, precision=2)
    RealizedPnL = factory.fuzzy.FuzzyDecimal(low=-1000.0, high=1000.0, precision=2)
    UnrealizedPnL = factory.fuzzy.FuzzyDecimal(low=-1000.0, high=1000.0, precision=2)


class SessionFactory(factory.Factory):
    """Creates fake Tickers"""

    class Meta:
        """Persistent class for factory"""

        model = SessionModel

    value = factory.fuzzy.FuzzyText(length=20, chars=string.ascii_letters, prefix="")
    expiry = factory.fuzzy.FuzzyDateTime(
        start_dt=dt.datetime(2022, 1, 1, tzinfo=pytz.UTC)
    )
