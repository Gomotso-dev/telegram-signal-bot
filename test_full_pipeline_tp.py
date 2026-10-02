from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


# ============================================================
# TEST: FULL PIPELINE - MODIFY TP ON ALL US30 POSITIONS
# ============================================================

MESSAGE = "TP: @ 51000"


print("=" * 70)
print("FULL PIPELINE - MULTI-POSITION TP TEST")
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
#
# TP message has no symbol:
#
#     TP: @ 51000
#
# For this test, tell the manager the relevant symbol is US30.
#
# This does NOT open an MT5 position.
#
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


if command.action != "MODIFY_TP":
    print(
        f"\nERROR: Expected MODIFY_TP, "
        f"got {command.action}"
    )
    raise SystemExit


if command.symbol != "US30":
    print(
        f"\nERROR: Expected US30, "
        f"got {command.symbol}"
    )
    raise SystemExit


if command.take_profit != 51000.0:
    print(
        f"\nERROR: Expected TP 51000.0, "
        f"got {command.take_profit}"
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
print("US30 POSITIONS BEFORE")
print("=" * 70)

positions_before = executor.get_positions("US30")

if not positions_before:

    print("No US30 positions found.")

    executor.disconnect()

    raise SystemExit


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
print("EXECUTING COMMAND")
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
print("US30 POSITIONS AFTER")
print("=" * 70)

positions_after = executor.get_positions("US30")

for position in positions_after:

    print(
        f"Ticket: {position.ticket} | "
        f"Volume: {position.volume} | "
        f"Type: {position.type} | "
        f"SL: {position.sl} | "
        f"TP: {position.tp}"
    )


# ============================================================
# 12. VERIFY TP
# ============================================================

print("\n" + "=" * 70)
print("TP VERIFICATION")
print("=" * 70)

all_correct = True

for position in positions_after:

    if position.tp == 51000.0:

        print(
            f"Ticket {position.ticket}: "
            f"TP correctly set to {position.tp}"
        )

    else:

        print(
            f"Ticket {position.ticket}: "
            f"ERROR - TP is {position.tp}"
        )

        all_correct = False


if all_correct:

    print("\nALL US30 POSITIONS HAVE THE CORRECT TP.")

else:

    print("\nTP VERIFICATION FAILED.")


# ============================================================
# 13. DISCONNECT
# ============================================================

executor.disconnect()


print("\n" + "=" * 70)
print("FULL PIPELINE TP TEST COMPLETE")
print("=" * 70)