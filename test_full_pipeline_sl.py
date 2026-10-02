from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


# ============================================================
# TEST: FULL PIPELINE - MODIFY SL ON ALL US30 POSITIONS
# ============================================================

MESSAGE = "SL: @ 50500"


print("=" * 70)
print("FULL PIPELINE - MULTI-POSITION SL TEST")
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
# SL message has no symbol:
#
#     SL: @ 50500
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


if command.action != "MODIFY_SL":
    print(
        f"\nERROR: Expected MODIFY_SL, "
        f"got {command.action}"
    )
    raise SystemExit


if command.symbol != "US30":
    print(
        f"\nERROR: Expected US30, "
        f"got {command.symbol}"
    )
    raise SystemExit


if command.stop_loss != 50500.0:
    print(
        f"\nERROR: Expected SL 50500.0, "
        f"got {command.stop_loss}"
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
# 12. VERIFY SL
# ============================================================

print("\n" + "=" * 70)
print("SL VERIFICATION")
print("=" * 70)

all_correct = True

for position in positions_after:

    if position.sl == 50500.0:

        print(
            f"Ticket {position.ticket}: "
            f"SL correctly set to {position.sl}"
        )

    else:

        print(
            f"Ticket {position.ticket}: "
            f"ERROR - SL is {position.sl}"
        )

        all_correct = False


if all_correct:

    print("\nALL US30 POSITIONS HAVE THE CORRECT SL.")

else:

    print("\nSL VERIFICATION FAILED.")


# ============================================================
# 13. DISCONNECT
# ============================================================

executor.disconnect()


print("\n" + "=" * 70)
print("FULL PIPELINE SL TEST COMPLETE")
print("=" * 70)