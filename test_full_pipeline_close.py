from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


# ============================================================
# TEST: FULL PIPELINE - CLOSE ALL US30 POSITIONS
# ============================================================

MESSAGE = "CLOSE"


print("=" * 70)
print("FULL PIPELINE - MULTI-POSITION CLOSE TEST")
print("=" * 70)

print("\nTELEGRAM MESSAGE:")
print(MESSAGE)


# ============================================================
# 1. PARSE MESSAGE
# ============================================================

signal = parse_signal(MESSAGE)

print("\n" + "=" * 70)
print("PARSED SIGNAL")
print("=" * 70)

print(signal)


# ============================================================
# 2. CREATE TRADE MANAGER
# ============================================================

manager = TradeManager()


# ============================================================
# 3. GIVE MANAGER THE RELEVANT SYMBOL
# ============================================================

manager.handle_entry(
    parse_signal("BUY US30")
)


# ============================================================
# 4. PROCESS SIGNAL
# ============================================================

trade_state = manager.process_signal(signal)

print("\n" + "=" * 70)
print("TRADE STATE")
print("=" * 70)

print(trade_state)


# ============================================================
# 5. CREATE TRADE COMMAND
# ============================================================

command = manager.create_command(signal)

print("\n" + "=" * 70)
print("TRADE COMMAND")
print("=" * 70)

print(command)


# ============================================================
# 6. SAFETY CHECK
# ============================================================

if command is None:
    print("\nERROR: No trade command was created.")
    raise SystemExit


if command.action != "CLOSE":
    print(
        f"\nERROR: Expected CLOSE, "
        f"got {command.action}"
    )
    raise SystemExit


if command.symbol != "US30":
    print(
        f"\nERROR: Expected US30, "
        f"got {command.symbol}"
    )
    raise SystemExit


if command.ticket is not None:
    print(
        f"\nERROR: Expected ticket=None, "
        f"got {command.ticket}"
    )
    raise SystemExit


print("\nSAFETY CHECK PASSED.")


# ============================================================
# 7. CONNECT TO MT5
# ============================================================

executor = MT5Executor()

if not executor.connect():
    print("\nERROR: Could not connect to MT5.")
    raise SystemExit


# ============================================================
# 8. SHOW POSITIONS BEFORE
# ============================================================

print("\n" + "=" * 70)
print("US30 POSITIONS BEFORE CLOSE")
print("=" * 70)

positions_before = executor.get_positions("US30")

if not positions_before:
    print("No US30 positions found.")
    executor.disconnect()
    raise SystemExit


print(f"Found {len(positions_before)} US30 position(s).")

for position in positions_before:
    print(
        f"Ticket: {position.ticket} | "
        f"Volume: {position.volume} | "
        f"Type: {position.type} | "
        f"SL: {position.sl} | "
        f"TP: {position.tp}"
    )


# ============================================================
# 9. EXECUTE CLOSE
# ============================================================

print("\n" + "=" * 70)
print("EXECUTING CLOSE COMMAND")
print("=" * 70)

print(command)

result = executor.execute(command)


# ============================================================
# 10. EXECUTION RESULT
# ============================================================

print("\n" + "=" * 70)
print("EXECUTION RESULT")
print("=" * 70)

print(result)


# ============================================================
# 11. CHECK POSITIONS AFTER
# ============================================================

print("\n" + "=" * 70)
print("US30 POSITIONS AFTER CLOSE")
print("=" * 70)

positions_after = executor.get_positions("US30")


if not positions_after:

    print("No US30 positions remain.")

else:

    print(
        f"WARNING: {len(positions_after)} "
        f"US30 position(s) still remain."
    )

    for position in positions_after:
        print(
            f"Ticket: {position.ticket} | "
            f"Volume: {position.volume} | "
            f"Type: {position.type} | "
            f"SL: {position.sl} | "
            f"TP: {position.tp}"
        )


# ============================================================
# 12. FINAL VERIFICATION
# ============================================================

print("\n" + "=" * 70)
print("CLOSE VERIFICATION")
print("=" * 70)

if not positions_after:

    print("ALL US30 POSITIONS WERE CLOSED SUCCESSFULLY.")

else:

    print("CLOSE VERIFICATION FAILED.")


# ============================================================
# 13. DISCONNECT
# ============================================================

executor.disconnect()


print("\n" + "=" * 70)
print("FULL PIPELINE CLOSE TEST COMPLETE")
print("=" * 70)