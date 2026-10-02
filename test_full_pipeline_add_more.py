from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


# ============================================================
# TEST: FULL PIPELINE - ADD MORE US30
# ============================================================

MESSAGE = "ADD MORE US30"


print("=" * 70)
print("FULL PIPELINE - ADD MORE TEST")
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
# 3. CREATE AN EXISTING US30 TRADE IN MANAGER
# ============================================================

manager.handle_entry(
    parse_signal("BUY US30")
)


# ============================================================
# 4. PROCESS ADD MORE SIGNAL
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
# 6. SAFETY CHECKS
# ============================================================

if command is None:
    print("\nERROR: No trade command was created.")
    raise SystemExit


if command.action != "ADD_MORE":
    print(
        f"\nERROR: Expected ADD_MORE, "
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
# 8. SHOW US30 POSITIONS BEFORE
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
        f"Type: {position.type} | "
        f"SL: {position.sl} | "
        f"TP: {position.tp}"
    )


# ============================================================
# 9. EXECUTE COMMAND
# ============================================================

print("\n" + "=" * 70)
print("EXECUTING ADD MORE COMMAND")
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
# 11. SHOW POSITIONS AFTER
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
        f"Type: {position.type} | "
        f"SL: {position.sl} | "
        f"TP: {position.tp}"
    )


# ============================================================
# 12. DISCONNECT
# ============================================================

executor.disconnect()


print("\n" + "=" * 70)
print("FULL PIPELINE ADD MORE TEST COMPLETE")
print("=" * 70)