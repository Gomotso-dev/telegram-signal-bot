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
    print(f"SL: {position.sl}")
    print(f"TP: {position.tp}")
    print(f"Profit: {position.profit}")

    command = TradeCommand(
        action="CLOSE",
        symbol="EURUSD",
    )

    print("\n" + "=" * 70)
    print("CLOSING POSITION")
    print("=" * 70)

    print(command)

    result = executor.execute(command)

    print("\n" + "=" * 70)
    print("CLOSE RESULT")
    print("=" * 70)

    print(result)

    if result is not None:
        print(f"\nRetcode: {result.retcode}")
        print(f"Comment: {result.comment}")
        print(f"Order: {result.order}")
        print(f"Deal: {result.deal}")

    print("\n" + "=" * 70)
    print("POSITIONS AFTER CLOSE")
    print("=" * 70)

    positions = executor.get_positions("EURUSD")

    if positions:

        for position in positions:
            print(f"Ticket: {position.ticket}")
            print(f"Volume: {position.volume}")
            print(f"Profit: {position.profit}")

    else:

        print("No EURUSD position found.")

finally:

    executor.disconnect()