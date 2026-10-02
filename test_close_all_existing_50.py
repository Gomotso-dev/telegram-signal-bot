from mt5_executor import MT5Executor


def main():

    executor = MT5Executor()

    if not executor.connect():
        return

    try:

        print("=" * 70)
        print("EXISTING US30 POSITIONS")
        print("=" * 70)

        positions = executor.get_positions("US30")

        if not positions:
            print("No US30 positions found.")
            return

        print(f"\nFound {len(positions)} US30 position(s).\n")

        for position in positions:
            print(
                f"Ticket: {position.ticket} | "
                f"Volume: {position.volume} | "
                f"SL: {position.sl} | "
                f"TP: {position.tp}"
            )

        print("\n" + "=" * 70)
        print("CLOSE 50% OF ALL US30 POSITIONS")
        print("=" * 70)

        results = executor.partial_close(
            symbol="US30",
            percentage=50.0,
        )

        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)

        print(results)

        print("\n" + "=" * 70)
        print("POSITIONS AFTER PARTIAL CLOSE")
        print("=" * 70)

        positions_after = executor.get_positions("US30")

        if not positions_after:
            print("No US30 positions remaining.")
            return

        for position in positions_after:
            print(
                f"Ticket: {position.ticket} | "
                f"Volume: {position.volume} | "
                f"SL: {position.sl} | "
                f"TP: {position.tp}"
            )

    finally:
        executor.disconnect()


if __name__ == "__main__":
    main()