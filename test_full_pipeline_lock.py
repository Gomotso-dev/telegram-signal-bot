from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


print("=" * 70)
print("FULL PIPELINE - LOCK TEST")
print("=" * 70)


# ============================================================
# 1. CREATE MANAGER
# ============================================================

manager = TradeManager()


# ============================================================
# 2. CREATE LOGICAL TRADE
# ============================================================

entry_signal = parse_signal("BUY US30")

trade = manager.process_signal(entry_signal)

print("\n" + "=" * 70)
print("INITIAL TRADE STATE")
print("=" * 70)

print(trade)


# ============================================================
# 3. PARSE LOCK
# ============================================================

lock_signal = parse_signal("LOCK US30")

print("\n" + "=" * 70)
print("PARSED LOCK SIGNAL")
print("=" * 70)

print(lock_signal)


# ============================================================
# 4. PROCESS LOCK
# ============================================================

trade_state = manager.process_signal(lock_signal)

print("\n" + "=" * 70)
print("TRADE STATE AFTER LOCK")
print("=" * 70)

print(trade_state)


# ============================================================
# 5. CREATE COMMAND
# ============================================================

command = manager.create_command(lock_signal)

print("\n" + "=" * 70)
print("LOCK COMMAND")
print("=" * 70)

print(command)


# ============================================================
# 6. SAFETY CHECK
# ============================================================

if command is None:
    raise SystemExit("ERROR: No LOCK command created.")

if command.action != "LOCK":
    raise SystemExit(
        f"ERROR: Expected LOCK, got {command.action}"
    )

if command.symbol != "US30":
    raise SystemExit(
        f"ERROR: Expected US30, got {command.symbol}"
    )

print("\nSAFETY CHECK PASSED.")


# ============================================================
# 7. CONNECT MT5
# ============================================================

executor = MT5Executor()

if not executor.connect():
    raise SystemExit("ERROR: Could not connect to MT5.")


# ============================================================
# 8. POSITIONS BEFORE LOCK
# ============================================================

print("\n" + "=" * 70)
print("US30 POSITIONS BEFORE LOCK")
print("=" * 70)

positions_before = executor.get_positions("US30")

print(
    f"Found {len(positions_before)} "
    f"US30 position(s)."
)

if not positions_before:
    executor.disconnect()
    raise SystemExit(
        "ERROR: No US30 positions found."
    )

for position in positions_before:

    direction = (
        "BUY"
        if position.type == 0
        else "SELL"
    )

    print(
        f"Ticket: {position.ticket} | "
        f"Type: {direction} | "
        f"Volume: {position.volume} | "
        f"Entry: {position.price_open} | "
        f"SL: {position.sl} | "
        f"TP: {position.tp}"
    )


# ============================================================
# 9. EXECUTE LOCK
# ============================================================

print("\n" + "=" * 70)
print("EXECUTING LOCK")
print("=" * 70)

results = executor.execute(command)

print("\n" + "=" * 70)
print("LOCK RESULTS")
print("=" * 70)

print(results)


# ============================================================
# 10. GET POSITIONS AFTER LOCK
# ============================================================

print("\n" + "=" * 70)
print("US30 POSITIONS AFTER LOCK")
print("=" * 70)

positions_after = executor.get_positions("US30")

print(
    f"Found {len(positions_after)} "
    f"US30 position(s)."
)

for position in positions_after:

    direction = (
        "BUY"
        if position.type == 0
        else "SELL"
    )

    print(
        f"Ticket: {position.ticket} | "
        f"Type: {direction} | "
        f"Volume: {position.volume} | "
        f"Entry: {position.price_open} | "
        f"SL: {position.sl} | "
        f"TP: {position.tp}"
    )


# ============================================================
# 11. VERIFY EVERY POSITION
# ============================================================

print("\n" + "=" * 70)
print("LOCK VERIFICATION")
print("=" * 70)


if len(positions_after) != len(positions_before):
    raise SystemExit(
        "ERROR: Number of positions changed during LOCK."
    )


for position in positions_after:

    expected_sl = position.price_open

    if abs(position.sl - expected_sl) > 0.00001:

        raise SystemExit(
            f"ERROR: Ticket {position.ticket} "
            f"has incorrect SL. "
            f"Expected {expected_sl}, "
            f"got {position.sl}"
        )

    print(
        f"Ticket {position.ticket}: "
        f"SL correctly locked at "
        f"{position.price_open}"
    )


print("\nALL US30 POSITIONS LOCKED AT BREAKEVEN.")


# ============================================================
# 12. DISCONNECT
# ============================================================

executor.disconnect()


print("\n" + "=" * 70)
print("FULL PIPELINE LOCK TEST PASSED")
print("=" * 70)