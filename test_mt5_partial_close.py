from mt5_executor import MT5Executor
from trade_command import TradeCommand


executor = MT5Executor()


try:

    if not executor.connect():
        print("Could not connect to MT5.")
        raise SystemExit

    # ========================================================
    # STEP 1: OPEN 0.10 LOT EURUSD BUY
    # ========================================================

    print("\n" + "=" * 70)
    print("OPENING 0.10 LOT EURUSD BUY")
    print("=" * 70)

    open_command = TradeCommand(
        action="OPEN",
        symbol="EURUSD",
        direction="buy",
        volume=0.10,
    )

    print(open_command)

    open_result = executor.execute(
        open_command
    )

    print("\nOPEN RESULT:")
    print(open_result)

    if open_result is None:
        print("Open order returned no result.")
        raise SystemExit

    print(f"Retcode: {open_result.retcode}")
    print(f"Comment: {open_result.comment}")

    if open_result.retcode != 10009:
        print("OPEN ORDER FAILED.")
        raise SystemExit

    # ========================================================
    # STEP 2: CHECK POSITION
    # ========================================================

    print("\n" + "=" * 70)
    print("POSITION BEFORE PARTIAL CLOSE")
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

    # ========================================================
    # STEP 3: PARTIAL CLOSE 50%
    # ========================================================

    partial_command = TradeCommand(
        action="PARTIAL_CLOSE",
        symbol="EURUSD",
        percentage=50,
    )

    print("\n" + "=" * 70)
    print("PARTIAL CLOSE 50%")
    print("=" * 70)

    print(partial_command)

    partial_result = executor.execute(
        partial_command
    )

    print("\nPARTIAL CLOSE RESULT:")
    print(partial_result)

    if partial_result is not None:
        print(f"Retcode: {partial_result.retcode}")
        print(f"Comment: {partial_result.comment}")
        print(f"Order: {partial_result.order}")
        print(f"Deal: {partial_result.deal}")
        print(f"Volume: {partial_result.volume}")

    # ========================================================
    # STEP 4: CHECK REMAINING POSITION
    # ========================================================

    print("\n" + "=" * 70)
    print("POSITION AFTER PARTIAL CLOSE")
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

    else:

        print("No EURUSD position found.")

finally:

    executor.disconnect()