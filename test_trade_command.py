from trade_command import TradeCommand


commands = [

    TradeCommand(
        action="OPEN",
        symbol="US30",
        direction="buy",
        volume=0.10,
        stop_loss=51900,
        take_profit=52300,
    ),

    TradeCommand(
        action="MODIFY_SL",
        symbol="US30",
        stop_loss=51900,
    ),

    TradeCommand(
        action="MODIFY_TP",
        symbol="US30",
        take_profit=52300,
    ),

    TradeCommand(
        action="LOCK",
        symbol="US30",
    ),

    TradeCommand(
        action="PARTIAL_CLOSE",
        symbol="US30",
        percentage=50,
    ),

    TradeCommand(
        action="CLOSE",
        symbol="US30",
    ),

]


for command in commands:

    print("=" * 70)
    print("TRADE COMMAND")
    print(command)
    print()