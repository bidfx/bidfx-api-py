__all__ = ["Field"]


class Field:
    """
    Fields provides constants for the most commonly used price field names.
    """

    ASK = "Ask"
    """Price field containing the ask price.
    """
    ASK_END_SIZE = "AskEndSize"
    """Price field containing the ask size of the end leg of a swap or NDS.
    """
    ASK_EXCHANGE = "AskExchange"
    """Price field containing the exchange code from where the ask price has originated.
    """
    ASK_FORWARD_POINTS = "AskForwardPoints"
    """Price field containing the ask forward points of an FX forward.
    """
    ASK_ID = "AskID"
    """Price field containing the price ID of a quote of the ask side of an quote book.
    """
    ASK_LEVELS = "AskLevels"
    """Price field containing the number of market-depth levels of the ask side of an order book.
    """
    ASK_FIRM = "AskFirm"
    """Price field containing the firm (company) offering on the ask side of an order book.
    """
    ASK_SIZE = "AskSize"
    """Price field containing the ask size.
    """
    ASK_SPOT = "AskSpot"
    """Price field containing the ask spot rate associated with an FX forward.
    """
    ASK_TICK = "AskTick"
    """Price field containing the tick direction for the ask price relative to the previous price.
    """
    ASK_TIME = "AskTime"
    """Price field containing the time of the last change in the ask price.
    """
    BID = "Bid"
    """Price field containing the bid price.
    """
    BID_END_SIZE = "BidEndSize"
    """Price field containing the bid size of the end leg of a swap or NDS.
    """
    BID_EXCHANGE = "BidExchange"
    """Price field containing the exchange code from where the bid price has originated.
    """
    BID_FORWARD_POINTS = "BidForwardPoints"
    """Price field containing the bid forward points of an FX forward.
    """
    BID_ID = "BidID"
    """Price field containing the price ID of a quote of the bid side of an quote book.
    """
    BID_LEVELS = "BidLevels"
    """Price field containing the number of market-depth levels of the bid side of an order book.
    """
    BID_FIRM = "BidFirm"
    """Price field containing the firm (company) offering on the bid side of an order book.
    """
    BID_SIZE = "BidSize"
    """Price field containing the bid size.
    """
    BID_SPOT = "BidSpot"
    """Price field containing the bid spot rate associated with an FX forward.
    """
    BID_TICK = "BidTick"
    """Price field containing the tick direction for the bid price relative to the previous price.
    """
    BID_TIME = "BidTime"
    """Price field containing the time of the last change in the bid price.
    """
    BROKER = "Broker"
    """Price field containing the name of the broker quoting the price.
    """
    CLOSE = "Close"
    """Price field containing the previous market close price.
    """
    HIGH = "High"
    """Price field containing the market high price for the current day or session. 
    """
    LAST = "Last"
    """Price field containing the last traded price.
    """
    LAST_SIZE = "LastSize"
    """Price field containing the size of the last trade.
    """
    LAST_TICK = "LastTick"
    """Price field containing the tick direction of the last trade relative to the previous trade.
    """
    LOW = "Low"
    """Price field containing the market low price for the current day or session.
    """
    NET_CHANGE = "NetChange"
    """Price field containing the net change in price between the last price and the open price.
    """
    NUM_ASKS = "NumAsks"
    """Price field containing the number of participants offering at the ask price.
    """
    NUM_BIDS = "NumBids"
    """Price field containing the the number of participants bidding at the bid price.
    """
    OPEN = "Open"
    """Price field containing the market price at the open.
    """
    OPEN_INTEREST = "OpenInterest"
    """Price field containing the open interest in a future.
    """
    ORIGIN_TIME = "OriginTime"
    """Price field containing the time of a price tick as measured at the originating source.
    """
    PERCENT_CHANGE = "PercentChange"
    """Price field containing the percentage change between the last price and the market open.
    """
    PRICE_ID = "PriceID"
    """Price field containing the ID used by an LP to identify a tradable quote.
    """
    STRIKE = "Strike"
    """Price field containing the strike price of an option.
    """
    VOLUME = "Volume"
    """Price field containing the volume.
    """
    VWAP = "VWAP"
    """Price field containing the volume weighted average price.
    """
