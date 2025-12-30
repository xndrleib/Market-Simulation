from market_simulation.order_book import OrderBook
from market_simulation.types import Order


def test_order_book_matching_market_order():
    book = OrderBook()

    sell_order = Order(
        id=1,
        time=0,
        agent_id=10,
        side="SELL",
        price=101.0,
        quantity=5,
        is_market=False,
    )
    trades = book.process_order(sell_order)
    assert trades == []
    assert len(book.asks) == 1

    buy_order = Order(
        id=2,
        time=1,
        agent_id=11,
        side="BUY",
        price=None,
        quantity=3,
        is_market=True,
    )
    trades = book.process_order(buy_order)
    assert len(trades) == 1
    trade = trades[0]
    assert trade.price == 101.0
    assert trade.quantity == 3
    assert trade.buy_agent == 11
    assert trade.sell_agent == 10

    assert len(book.asks) == 1
    assert book.asks[0].quantity == 2


def test_order_book_limit_not_crossing():
    book = OrderBook()

    sell_order = Order(
        id=1,
        time=0,
        agent_id=10,
        side="SELL",
        price=105.0,
        quantity=5,
        is_market=False,
    )
    book.process_order(sell_order)

    buy_order = Order(
        id=2,
        time=1,
        agent_id=11,
        side="BUY",
        price=100.0,
        quantity=5,
        is_market=False,
    )
    trades = book.process_order(buy_order)
    assert trades == []
    assert len(book.asks) == 1
    assert len(book.bids) == 1
