from mt5_executor import MT5Executor
from trade_command import TradeCommand


executor = MT5Executor()


try:

    # ========================================================
    # CONNECT
    # ========================================================

    if not executor.connect():
        print("Could not connect to MT5.")
        raise SystemExit

    # ========================================================
    # SHOW CURRENT PRICE
    # ========================================================

    print("\n" + "=" * 70)
    print("CURRENT EURUSD PRICE")
    print("=" * 70)

    price = executor.get_current_price(
        "EURUSD",
        "buy"
    )

    print(f"EURUSD BUY price: {price}")

    # ========================================================
    # CREATE DEMO BUY COMMAND
    # ========================================================

    command = TradeCommand(
        action="OPEN",
        symbol="EURUSD",
        direction="buy",
        volume=0.01,
    )

    print("\n" + "=" * 70)
    print("SENDING DEMO ORDER")
    print("=" * 70)

    print(command)

    # ========================================================
    # EXECUTE
    # ========================================================

    result = executor.execute(
        command
    )

    # ========================================================
    # RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("ORDER RESULT")
    print("=" * 70)

    print(result)

    if result is not None:

        print(
            f"\nRetcode: {result.retcode}"
        )

        print(
            f"Comment: {result.comment}"
        )

        print(
            f"Order: {result.order}"
        )

        print(
            f"Deal: {result.deal}"
        )

    # ========================================================
    # CHECK OPEN POSITIONS
    # ========================================================

    print("\n" + "=" * 70)
    print("OPEN POSITIONS")
    print("=" * 70)

    positions = executor.get_positions(
        "EURUSD"
    )

    if positions:

        for position in positions:

            print(
                f"Ticket: {position.ticket}"
            )

            print(
                f"Symbol: {position.symbol}"
            )

            print(
                f"Volume: {position.volume}"
            )

            print(
                f"Type: {position.type}"
            )

            print(
                f"Open price: {position.price_open}"
            )

            print(
                f"SL: {position.sl}"
            )

            print(
                f"TP: {position.tp}"
            )

            print(
                f"Profit: {position.profit}"
            )

    else:

        print(
            "No EURUSD position found."
        )


finally:

    executor.disconnect()