from mt5_executor import MT5Executor


print("=" * 70)
print("STAGE 1 - LOCK BREAK-EVEN CALCULATION TEST")
print("=" * 70)


executor = MT5Executor()

if not executor.connect():
    raise SystemExit("ERROR: Could not connect to MT5.")


# ============================================================
# GET ALL US30 POSITIONS
# ============================================================

positions = executor.get_positions("US30")

print("\n" + "=" * 70)
print("US30 POSITIONS")
print("=" * 70)

print(f"Found {len(positions)} US30 position(s).")


if not positions:
    executor.disconnect()
    raise SystemExit(
        "No US30 positions found. "
        "Open at least one US30 demo position first."
    )


# ============================================================
# CALCULATE BREAK-EVEN SL
# ============================================================

print("\n" + "=" * 70)
print("LOCK CALCULATION")
print("=" * 70)


for position in positions:

    entry_price = position.price_open

    direction = (
        "BUY"
        if position.type == 0
        else "SELL"
    )

    print(
        f"Ticket: {position.ticket} | "
        f"Type: {direction} | "
        f"Volume: {position.volume} | "
        f"Entry: {entry_price} | "
        f"Current SL: {position.sl} | "
        f"New SL: {entry_price}"
    )


# ============================================================
# VERIFY
# ============================================================

print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)


for position in positions:

    entry_price = position.price_open

    if entry_price <= 0:
        raise SystemExit(
            f"ERROR: Invalid entry price for "
            f"ticket {position.ticket}"
        )


print("PASS: Every position has a valid entry price.")
print(
    "PASS: Each position can use its own "
    "entry price as SL."
)
print("PASS: No MT5 SL modification was performed.")


executor.disconnect()


print("\n" + "=" * 70)
print("STAGE 1 LOCK TEST PASSED")
print("=" * 70)