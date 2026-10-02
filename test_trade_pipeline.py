from signal_parser import parse_signal
from trade_manager import TradeManager


# ============================================================
# CREATE MANAGER
# ============================================================

manager = TradeManager()


# ============================================================
# TELEGRAM MESSAGES
# ============================================================

messages = [
    "BUY US30",
    "SL: @ 51900",
    "TP: @ 52300",
    "LOCK US30",
    "CLOSE 50%",
]


# ============================================================
# PROCESS COMPLETE PIPELINE
# ============================================================

for message in messages:

    print("\n" + "=" * 70)

    print("TELEGRAM MESSAGE:")
    print(message)

    # --------------------------------------------------------
    # PARSER
    # --------------------------------------------------------

    signal = parse_signal(message)

    print("\nPARSED SIGNAL:")
    print(signal)

    if not signal:
        print("\nNo signal detected.")
        continue

    # --------------------------------------------------------
    # TRADE MANAGER
    # --------------------------------------------------------

    trade = manager.process_signal(signal)

    print("\nTRADE STATE:")
    print(trade)

    # --------------------------------------------------------
    # TRADE COMMAND
    # --------------------------------------------------------

    command = manager.create_command(signal)

    print("\nTRADE COMMAND:")
    print(command)


# ============================================================
# FINAL STATE
# ============================================================

print("\n" + "=" * 70)
print("FINAL TRADE STATE")
print("=" * 70)

manager.print_trades()