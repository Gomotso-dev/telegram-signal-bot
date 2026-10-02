from mt5_executor import MT5Executor
from trade_command import TradeCommand


executor = MT5Executor()


try:

    if not executor.connect():
        print("Could not connect to MT5.")
        raise SystemExit

    print("\n" + "=" * 70)
    print("CURRENT POSITION")
    print("=" * 70)

    position = executor.get_position("EURUSD")

    if position is None:
        print("No EURUSD position found.")
        raise SystemExit

    print(f"Ticket: {position.ticket}")
    print(f"Symbol: {position.symbol}")
    print(f"Volume: {position.volume}")
    print(f"Open price: {position.price_open}")
    print(f"Current SL: {position.sl}")
    print(f"Current TP: {position.tp}")

    command = TradeCommand(
        action="MODIFY_TP",
        symbol="EURUSD",
        take_profit=1.13200,
    )

    print("\n" + "=" * 70)
    print("MODIFYING TAKE PROFIT")
    print("=" * 70)

    print(command)

    result = executor.execute(command)

    print("\n" + "=" * 70)
    print("MODIFY RESULT")
    print("=" * 70)

    print(result)

    if result is not None:
        print(f"\nRetcode: {result.retcode}")
        print(f"Comment: {result.comment}")

    print("\n" + "=" * 70)
    print("POSITION AFTER MODIFY")
    print("=" * 70)

    position = executor.get_position("EURUSD")

    if position:

        print(f"Ticket: {position.ticket}")
        print(f"Symbol: {position.symbol}")
        print(f"Volume: {position.volume}")
        print(f"Open price: {position.price_open}")
        print(f"SL: {position.sl}")
        print(f"TP: {position.tp}")
        print(f"Profit: {position.profit}")

finally:

    executor.disconnect()