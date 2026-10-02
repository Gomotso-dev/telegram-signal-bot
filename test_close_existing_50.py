import MetaTrader5 as mt5
from mt5_executor import MT5Executor


def main():
    executor = MT5Executor()

    if not executor.connect():
        print("Failed to connect to MT5.")
        return

    try:
        print("=" * 70)
        print("FIND EXISTING 0.10 LOT US30 POSITION")
        print("=" * 70)

        positions = executor.get_positions("US30")

        if not positions:
            print("No US30 positions found.")
            return

        print(f"\nFound {len(positions)} US30 position(s):\n")

        selected_position = None

        for position in positions:
            print(
                f"Ticket: {position.ticket} | "
                f"Volume: {position.volume} | "
                f"Type: {position.type} | "
                f"SL: {position.sl} | "
                f"TP: {position.tp}"
            )

            if abs(position.volume - 0.10) < 0.00001:
                if selected_position is None:
                    selected_position = position

        if selected_position is None:
            print("\nNo 0.10 lot US30 position found.")
            return

        print("\n" + "=" * 70)
        print("SELECTED POSITION")
        print("=" * 70)

        print(f"Ticket: {selected_position.ticket}")
        print(f"Symbol: {selected_position.symbol}")
        print(f"Volume: {selected_position.volume}")

        print("\n" + "=" * 70)
        print("CLOSING 50%")
        print("=" * 70)

        close_volume = selected_position.volume * 0.50

        print(f"Original volume: {selected_position.volume}")
        print(f"50% close volume: {close_volume}")

        result = executor.partial_close(
            symbol="US30",
            percentage=50.0,
            ticket=selected_position.ticket,
        )

        print("\nPARTIAL CLOSE RESULT:")
        print(result)

        print("\n" + "=" * 70)
        print("VERIFYING POSITIONS")
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