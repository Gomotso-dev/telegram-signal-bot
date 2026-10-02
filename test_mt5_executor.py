import MetaTrader5 as mt5

from mt5_executor import MT5Executor


executor = MT5Executor()


if executor.connect():

    print("\n" + "=" * 70)
    print("SYMBOL DIAGNOSTIC TEST")
    print("=" * 70)

    symbols = [
        "US30",
        "XAUUSD",
        "NAS100",
        "EURUSD",
    ]

    for symbol in symbols:

        print("\n" + "-" * 70)
        print(f"BOT SYMBOL: {symbol}")
        print("-" * 70)

        mt5_symbol = executor.get_mt5_symbol(symbol)

        print(f"MT5 SYMBOL: {mt5_symbol}")

        if mt5_symbol is None:
            print("No mapping found.")
            continue

        # ----------------------------------------------------
        # Symbol information
        # ----------------------------------------------------

        info = mt5.symbol_info(mt5_symbol)

        print(f"Symbol info: {info}")

        if info is None:
            print(
                "ERROR: symbol_info() returned None"
            )
            print(
                "Last error:",
                mt5.last_error()
            )
            continue

        print(f"Visible before select: {info.visible}")

        # ----------------------------------------------------
        # Select symbol
        # ----------------------------------------------------

        selected = mt5.symbol_select(
            mt5_symbol,
            True
        )

        print(f"symbol_select result: {selected}")

        if not selected:
            print(
                "symbol_select failed:",
                mt5.last_error()
            )
            continue

        # ----------------------------------------------------
        # Get updated symbol information
        # ----------------------------------------------------

        info = mt5.symbol_info(
            mt5_symbol
        )

        print(
            f"Visible after select: {info.visible}"
        )

        # ----------------------------------------------------
        # Get tick
        # ----------------------------------------------------

        tick = mt5.symbol_info_tick(
            mt5_symbol
        )

        print(f"Tick: {tick}")

        if tick is None:

            print(
                "Could not retrieve tick."
            )

            print(
                "Last error:",
                mt5.last_error()
            )

            continue

        # ----------------------------------------------------
        # Print prices
        # ----------------------------------------------------

        print(f"Bid:  {tick.bid}")
        print(f"Ask:  {tick.ask}")
        print(f"Last: {tick.last}")

        print(
            f"Time: {tick.time}"
        )

    print("\n" + "=" * 70)
    print("FINAL MT5 SYMBOL LIST CHECK")
    print("=" * 70)

    for symbol in symbols:

        mt5_symbol = executor.get_mt5_symbol(symbol)

        if mt5_symbol:

            info = mt5.symbol_info(
                mt5_symbol
            )

            if info:

                print(
                    f"{symbol} -> "
                    f"{mt5_symbol} | "
                    f"Visible={info.visible}"
                )

    executor.disconnect()