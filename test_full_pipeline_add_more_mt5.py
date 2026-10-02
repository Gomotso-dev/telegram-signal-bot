from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


print("=" * 70)
print("FULL PIPELINE - ADD MORE MT5 TEST")
print("=" * 70)


# ============================================================
# 1. CREATE TRADE MANAGER
# ============================================================

manager = TradeManager()


# ============================================================
# 2. PREVIOUS SIGNAL
# ============================================================

previous_signal = parse_signal("BUY US30")

print("\n" + "=" * 70)
print("PREVIOUS SIGNAL")
print("=" * 70)

print(previous_signal)


# ============================================================
# 3. STORE PREVIOUS TRADE
# ============================================================

previous_trade = manager.process_signal(previous_signal)

print("\n" + "=" * 70)
print("PREVIOUS TRADE")
print("=" * 70)

print(previous_trade)


# ============================================================
# 4. ADD MORE SIGNAL
# ============================================================

message = "ADD MORE US30"

signal = parse_signal(message)

print("\n" + "=" * 70)
print("ADD MORE SIGNAL")
print("=" * 70)

print(signal)


# ============================================================
# 5. PROCESS ADD MORE
# ============================================================

trade_state = manager.process_signal(signal)

print("\n" + "=" * 70)
print("TRADE STATE")
print("=" * 70)

print(trade_state)


# ============================================================
# 6. CREATE COMMAND
# ============================================================

command = manager.create_command(signal)

print("\n" + "=" * 70)
print("TRADE COMMAND")
print("=" * 70)

print(command)


# ============================================================
# 7. SAFETY CHECK
# ============================================================

if command is None:
    raise SystemExit("ERROR: No command created.")

if command.action != "ADD_MORE":
    raise SystemExit(
        f"ERROR: Expected ADD_MORE, got {command.action}"
    )

if command.symbol != "US30":
    raise SystemExit(
        f"ERROR: Expected US30, got {command.symbol}"
    )

if command.direction != "buy":
    raise SystemExit(
        f"ERROR: Expected BUY, got {command.direction}"
    )

if command.volume != 0.05:
    raise SystemExit(
        f"ERROR: Expected 0.05 lot, got {command.volume}"
    )

print("\nSAFETY CHECK PASSED.")


# ============================================================
# 8. CONNECT MT5
# ============================================================

executor = MT5Executor()

if not executor.connect():
    raise SystemExit("ERROR: Could not connect to MT5.")


# ============================================================
# 9. POSITIONS BEFORE
# ============================================================

print("\n" + "=" * 70)
print("US30 POSITIONS BEFORE ADD MORE")
print("=" * 70)

positions_before = executor.get_positions("US30")

print(
    f"Found {len(positions_before)} "
    f"US30 position(s)."
)

for position in positions_before:
    print(
        f"Ticket: {position.ticket} | "
        f"Volume: {position.volume} | "
        f"Type: {position.type}"
    )


# ============================================================
# 10. EXECUTE ADD MORE
# ============================================================

print("\n" + "=" * 70)
print("EXECUTING ADD MORE")
print("=" * 70)

result = executor.execute(command)

print("\n" + "=" * 70)
print("MT5 RESULT")
print("=" * 70)

print(result)


# ============================================================
# 11. POSITIONS AFTER
# ============================================================

print("\n" + "=" * 70)
print("US30 POSITIONS AFTER ADD MORE")
print("=" * 70)

positions_after = executor.get_positions("US30")

print(
    f"Found {len(positions_after)} "
    f"US30 position(s)."
)

for position in positions_after:
    print(
        f"Ticket: {position.ticket} | "
        f"Volume: {position.volume} | "
        f"Type: {position.type}"
    )


# ============================================================
# 12. VERIFY NEW POSITION
# ============================================================

if len(positions_after) != len(positions_before) + 1:

    print("\nWARNING:")
    print(
        "Expected exactly one additional US30 position."
    )

else:

    new_positions = [
        position
        for position in positions_after
        if position.ticket not in {
            p.ticket for p in positions_before
        }
    ]

    if len(new_positions) != 1:

        print(
            "\nWARNING: Could not uniquely identify "
            "the new position."
        )

    else:

        new_position = new_positions[0]

        print("\n" + "=" * 70)
        print("NEW POSITION VERIFICATION")
        print("=" * 70)

        print(
            f"Ticket: {new_position.ticket}"
        )

        print(
            f"Volume: {new_position.volume}"
        )

        print(
            f"Type: {new_position.type}"
        )

        # MT5:
        # BUY = 0
        # SELL = 1

        if new_position.type != 0:
            raise SystemExit(
                "ERROR: New position is not BUY."
            )

        if abs(new_position.volume - 0.05) > 0.00001:
            raise SystemExit(
                "ERROR: New position volume is not 0.05."
            )

        print("\nNEW BUY POSITION VERIFIED.")


# ============================================================
# 13. DISCONNECT
# ============================================================

executor.disconnect()


print("\n" + "=" * 70)
print("FULL PIPELINE ADD MORE MT5 TEST COMPLETE")
print("=" * 70)