from signal_parser import parse_signal
from trade_manager import TradeManager


print("=" * 70)
print("STAGE 1 - ADD MORE DIRECTION TEST")
print("=" * 70)


# ============================================================
# 1. CREATE MANAGER
# ============================================================

manager = TradeManager()


# ============================================================
# 2. FIRST SIGNAL
# ============================================================

first_signal = parse_signal("BUY US30")

print("\n" + "=" * 70)
print("FIRST SIGNAL")
print("=" * 70)

print(first_signal)


# ============================================================
# 3. PROCESS FIRST SIGNAL
# ============================================================

first_trade = manager.process_signal(first_signal)

print("\n" + "=" * 70)
print("FIRST TRADE STATE")
print("=" * 70)

print(first_trade)


# ============================================================
# 4. ADD MORE SIGNAL
# ============================================================

add_more_signal = parse_signal("ADD MORE US30")

print("\n" + "=" * 70)
print("ADD MORE SIGNAL")
print("=" * 70)

print(add_more_signal)


# ============================================================
# 5. PROCESS ADD MORE
# ============================================================

add_more_trade = manager.process_signal(add_more_signal)

print("\n" + "=" * 70)
print("TRADE STATE AFTER ADD MORE")
print("=" * 70)

print(add_more_trade)


# ============================================================
# 6. CREATE COMMAND
# ============================================================

command = manager.create_command(add_more_signal)

print("\n" + "=" * 70)
print("ADD MORE COMMAND")
print("=" * 70)

print(command)


# ============================================================
# 7. SAFETY CHECKS
# ============================================================

print("\n" + "=" * 70)
print("SAFETY CHECKS")
print("=" * 70)


if add_more_trade is None:
    raise SystemExit(
        "FAIL: ADD MORE did not produce a TradeState."
    )


if add_more_trade.direction != "buy":
    raise SystemExit(
        f"FAIL: Expected BUY, got "
        f"{add_more_trade.direction}"
    )


if command is None:
    raise SystemExit(
        "FAIL: ADD MORE did not produce a TradeCommand."
    )


if command.action != "ADD_MORE":
    raise SystemExit(
        f"FAIL: Expected ADD_MORE, got "
        f"{command.action}"
    )


if command.symbol != "US30":
    raise SystemExit(
        f"FAIL: Expected US30, got "
        f"{command.symbol}"
    )


if command.direction != "buy":
    raise SystemExit(
        f"FAIL: Expected BUY direction, got "
        f"{command.direction}"
    )


if command.volume != 0.05:
    raise SystemExit(
        f"FAIL: Expected volume 0.05, got "
        f"{command.volume}"
    )


print("PASS: Previous direction = BUY")
print("PASS: ADD MORE inherited BUY")
print("PASS: Symbol = US30")
print("PASS: Volume = 0.05")
print("PASS: Command = ADD_MORE")

print("\n" + "=" * 70)
print("STAGE 1 PASSED")
print("=" * 70)