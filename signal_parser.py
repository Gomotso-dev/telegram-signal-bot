import re
from dataclasses import dataclass
from typing import Optional


# ============================================================
# SUPPORTED SYMBOLS
# ============================================================

SYMBOL_WHITELIST = {
    "XAUUSD",
    "GOLD",
    "US30",
    "NAS100",
    "NASDAQ",
    "GER30",
    "AUDUSD",
    "EURUSD",
}


# ============================================================
# SIGNAL DATA
# ============================================================

@dataclass
class TradingSignal:
    signal_type: str

    symbol: Optional[str] = None
    direction: Optional[str] = None

    order_type: str = "market"

    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    percentage: Optional[float] = None

    action: Optional[str] = None


# ============================================================
# SYMBOL NORMALIZATION
# ============================================================

SYMBOL_ALIASES = {
    "GOLD": "XAUUSD",
    "XAUUSD": "XAUUSD",

    "US30": "US30",

    "NASDAQ": "NAS100",
    "NAS100": "NAS100",

    "GER30": "GER30",

    "AUDUSD": "AUDUSD",
    "EURUSD": "EURUSD",
}


def extract_symbol(text: str) -> Optional[str]:

    pattern = re.compile(
        r"\b(XAUUSD|GOLD|US30|NAS100|NASDAQ|GER30|AUDUSD|EURUSD)\b",
        re.IGNORECASE,
    )

    match = pattern.search(text)

    if not match:
        return None

    raw_symbol = match.group(1).upper()

    return SYMBOL_ALIASES.get(raw_symbol)


# ============================================================
# DIRECTION
# ============================================================

def extract_direction(text: str) -> Optional[str]:

    match = re.search(
        r"\b(BUY|SELL)\b",
        text,
        re.IGNORECASE,
    )

    if not match:
        return None

    return match.group(1).lower()


# ============================================================
# PRICE EXTRACTION
# ============================================================

PRICE_PATTERN = r"\d+(?:,\d{3})*(?:\.\d+)?"


def clean_price(value: str) -> float:

    return float(value.replace(",", ""))


# ============================================================
# STOP LOSS
# ============================================================

def extract_stop_loss(text: str) -> Optional[float]:

    pattern = re.compile(
        rf"""
        \b
        (?:
            sl
            |
            s/l
            |
            stop\s*loss
            |
            stoploss
        )
        \s*
        (?:at|@|=|:)?
        \s*
        (?:@|:)?
        \s*
        (?P<price>{PRICE_PATTERN})
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    match = pattern.search(text)

    if not match:
        return None

    return clean_price(match.group("price"))

def extract_standalone_stop_loss(text: str) -> Optional[float]:

    pattern = re.compile(
        rf"""
        ^\s*
        (?:
            sl
            |
            s/l
            |
            stop\s*loss
            |
            stoploss
        )
        \s*
        (?:at|@|=|:)?
        \s*
        (?:@|:)?
        \s*
        (?P<price>{PRICE_PATTERN})
        \s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    match = pattern.search(text)

    if not match:
        return None

    return clean_price(match.group("price"))


# ============================================================
# TAKE PROFIT
# ============================================================

def extract_take_profit(text: str) -> Optional[float]:

    pattern = re.compile(
        rf"""
        \b
        (?:
            tp
            |
            t/p
            |
            take\s*profit
        )
        \s*
        (?:at|@|=|:)?
        \s*
        (?:@|:)?
        \s*
        (?P<price>{PRICE_PATTERN})
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    match = pattern.search(text)

    if not match:
        return None

    return clean_price(match.group("price"))

def extract_standalone_take_profit(text: str) -> Optional[float]:

    pattern = re.compile(
        rf"""
        ^\s*
        (?:
            tp
            |
            t/p
            |
            take\s*profit
        )
        \s*
        (?:at|@|=|:)?
        \s*
        (?:@|:)?
        \s*
        (?P<price>{PRICE_PATTERN})
        \s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    match = pattern.search(text)

    if not match:
        return None

    return clean_price(match.group("price"))
# ============================================================
# ENTRY PRICE
# ============================================================

def extract_entry(text: str) -> Optional[float]:

    # Entry / price explicitly stated
    pattern = re.compile(
        rf"""
        \b
        (?:
            entry
            |
            price
        )
        \s*
        (?:at|@|=|:)?
        \s*
        (?P<price>{PRICE_PATTERN})
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    match = pattern.search(text)

    if match:
        return clean_price(match.group("price"))

    # BUY/SELL @ PRICE
    pattern = re.compile(
        rf"""
        \b
        (?:buy|sell)
        \s+
        (?:[A-Z0-9]+)
        \s*
        @
        \s*
        (?P<price>{PRICE_PATTERN})
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    match = pattern.search(text)

    if match:
        return clean_price(match.group("price"))

    return None


# ============================================================
# ORDER TYPE
# ============================================================

def detect_order_type(text: str) -> str:

    text_lower = text.lower()

    if "buy limit" in text_lower:
        return "buy_limit"

    if "sell limit" in text_lower:
        return "sell_limit"

    if "buy stop" in text_lower:
        return "buy_stop"

    if "sell stop" in text_lower:
        return "sell_stop"

    return "market"


# ============================================================
# PERCENTAGE
# ============================================================

def extract_percentage(text: str) -> Optional[float]:

    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*%",
        text,
        re.IGNORECASE,
    )

    if not match:
        return None

    return float(match.group(1))


# ============================================================
# MANAGEMENT COMMAND
# ============================================================

def detect_management_action(text: str) -> Optional[str]:

    text_lower = text.lower().strip()

    # EXIT means exactly the same thing as CLOSE.
    if re.search(r"\bexit\b", text_lower):
        percentage = extract_percentage(text)

        if percentage is not None:
            return "partial_close"

        return "close"

    # CLOSE
    if re.search(r"\bclose\b", text_lower):
        percentage = extract_percentage(text)

        if percentage is not None:
            return "partial_close"

        return "close"

    # LOCK
    if re.search(r"\block\b", text_lower):
        return "lock"

    # ADD MORE
    if re.search(
        r"\badd\s+more\b",
        text_lower,
    ):
        return "add_more"

    return None


# ============================================================
# ENTRY DETECTION
# ============================================================

def is_entry_signal(text: str) -> bool:

    direction = extract_direction(text)
    symbol = extract_symbol(text)

    if direction is None:
        return False

    if symbol is None:
        return False

    return True


# ============================================================
# MAIN PARSER
# ============================================================
    
    
def parse_signal(text: str) -> Optional[TradingSignal]:

    if not text:
        return None

    text = text.strip()

    # --------------------------------------------------------
    # First check management commands
    # --------------------------------------------------------

    management_action = detect_management_action(text)

    if management_action is not None:
        return TradingSignal(
            signal_type="management",
            symbol=extract_symbol(text),
            direction=None,
            action=management_action,
            percentage=extract_percentage(text),
        )

    # --------------------------------------------------------
    # Standalone STOP LOSS update
    # --------------------------------------------------------

    stop_loss = extract_standalone_stop_loss(text)

    if stop_loss is not None:
        return TradingSignal(
            signal_type="management",
            symbol=extract_symbol(text),
            direction=None,
            order_type="market",
            entry=None,
            stop_loss=stop_loss,
            take_profit=None,
            percentage=None,
            action="update_sl",
        )

    # --------------------------------------------------------
    # Standalone TAKE PROFIT update
    # --------------------------------------------------------

    take_profit = extract_standalone_take_profit(text)

    if take_profit is not None:
        return TradingSignal(
            signal_type="management",
            symbol=extract_symbol(text),
            direction=None,
            order_type="market",
            entry=None,
            stop_loss=None,
            take_profit=take_profit,
            percentage=None,
            action="update_tp",
        )

    # --------------------------------------------------------
    # Then check entry
    # --------------------------------------------------------

    if is_entry_signal(text):

        direction = extract_direction(text)
        symbol = extract_symbol(text)

        return TradingSignal(
            signal_type="entry",
            symbol=symbol,
            direction=direction,
            order_type=detect_order_type(text),
            entry=extract_entry(text),
            stop_loss=extract_stop_loss(text),
            take_profit=extract_take_profit(text),
        )

    # --------------------------------------------------------
    # Not a recognised signal
    # --------------------------------------------------------

    return None

    # --------------------------------------------------------
    # First check management commands
    # --------------------------------------------------------

    management_action = detect_management_action(text)

    if management_action is not None:

        return TradingSignal(
            signal_type="management",
            symbol=extract_symbol(text),
            direction=None,
            action=management_action,
            percentage=extract_percentage(text),
        )

    # --------------------------------------------------------
    # Then check entry
    # --------------------------------------------------------

    if is_entry_signal(text):

        direction = extract_direction(text)
        symbol = extract_symbol(text)

        return TradingSignal(
            signal_type="entry",
            symbol=symbol,
            direction=direction,
            order_type=detect_order_type(text),
            entry=extract_entry(text),
            stop_loss=extract_stop_loss(text),
            take_profit=extract_take_profit(text),
        )

    # --------------------------------------------------------
    # Not a recognised signal
    # --------------------------------------------------------

    return None


# ============================================================
# LOCAL TESTS
# ============================================================

if __name__ == "__main__":

    test_messages = [

        # ENTRY
        "Sell US30",

        "Buy EURUSD",

        "BUY US30 NOW",

        "BUY GOLD",

        "BUY GOLD NOW",

        "BUY NASDAQ NOW",

        "Sell AUDUSD",

        # ENTRY WITH PRICE
        "BUY US30 @ 53366.72",

        "Sell US30 @ 53766.80",

        # ENTRY WITH SL
        """
        BUY US30
        SL: @ 51900.00
        """,

        # ENTRY WITH SL + TP
        """
        Buy EURUSD
        SL @ 1.1700
        TP @ 1.1800
        """,

        # MANAGEMENT
        "Lock",

        "Lock and hold",

        "Exit",

        "Close",

        "Close 50% profit",

        "LOCK US30",

        "EXIT US30",

        "CLOSE US30",

        # ADD MORE
        "Add more sells",

        "Add more buys",

        # INVALID
        "Good morning everyone",

        "Stay disciplined",

        "Wait for confirmation",
    ]


    for message in test_messages:

        print()
        print("=" * 70)
        print("MESSAGE:")
        print(message.strip())

        signal = parse_signal(message)

        print()
        print("PARSED:")

        if signal is None:
            print("NO SIGNAL")

        else:
            print(signal)