from signal_parser import parse_signal
from trade_manager import TradeManager


manager = TradeManager()


messages = [
    "BUY US30",
    "SL: @ 51900",
    "TP: @ 52300",
    "LOCK US30",
    "CLOSE 50%",
]


for message in messages:

    print("\n" + "=" * 70)
    print("MESSAGE:")
    print(message)

    signal = parse_signal(message)

    print("\nSIGNAL:")
    print(signal)

    if signal:

        trade = manager.process_signal(signal)

        print("\nTRADE STATE:")
        print(trade)

manager.print_trades()