from signal_parser import parse_signal
from trade_manager import TradeManager


print("=" * 70)
print("FULL PIPELINE MANAGEMENT TEST")
print("=" * 70)


# ============================================================
# TEST MESSAGE
# ============================================================

message = "CLOSE 50%"

print("\nTELEGRAM MESSAGE:")
print(message)


# ============================================================
# PARSE
# ============================================================

signal = parse_signal(message)

print("\n" + "=" * 70)
print("PARSED SIGNAL")
print("=" * 70)

print(signal)


# ============================================================
# CHECK PARSER
# ============================================================

if signal is None:
    print("ERROR: Parser returned None.")
    raise SystemExit(1)

if signal.signal_type != "management":
    print(
        f"ERROR: Expected management, "
        f"got {signal.signal_type}"
    )
    raise SystemExit(1)

if signal.action != "partial_close":
    print(
        f"ERROR: Expected partial_close, "
        f"got {signal.action}"
    )
    raise SystemExit(1)

if signal.symbol is not None:
    print(
        f"ERROR: Expected symbol=None, "
        f"got {signal.symbol}"
    )
    raise SystemExit(1)

if signal.percentage != 50.0:
    print(
        f"ERROR: Expected percentage=50.0, "
        f"got {signal.percentage}"
    )
    raise SystemExit(1)


print("\nPARSER CHECK: PASSED")


# ============================================================
# TRADE MANAGER
# ============================================================

manager = TradeManager()


# ------------------------------------------------------------
# Create an existing logical US30 trade
# ------------------------------------------------------------

previous_signal = parse_signal(
    "BUY US30"
)

manager.process_signal(
    previous_signal
)


# ------------------------------------------------------------
# Process CLOSE 50%
# ------------------------------------------------------------

trade_state = manager.process_signal(
    signal
)

print("\n" + "=" * 70)
print("TRADE STATE")
print("=" * 70)

print(trade_state)


# ============================================================
# CHECK TRADE STATE
# ============================================================

if not trade_state:
    print(
        "ERROR: TradeManager returned no trade state."
    )
    raise SystemExit(1)

if len(trade_state) != 1:
    print(
        f"ERROR: Expected 1 trade state, "
        f"got {len(trade_state)}"
    )
    raise SystemExit(1)

trade = trade_state[0]

if trade.symbol != "US30":
    print(
        f"ERROR: Expected US30 trade state, "
        f"got {trade.symbol}"
    )
    raise SystemExit(1)

if trade.volume != 0.03:
    print(
        f"ERROR: Expected logical volume 0.03, "
        f"got {trade.volume}"
    )
    raise SystemExit(1)

if not trade.is_open:
    print(
        "ERROR: Trade should still be open."
    )
    raise SystemExit(1)


print("TRADE MANAGER CHECK: PASSED")


# ============================================================
# CREATE TRADE COMMAND
# ============================================================

command = manager.create_command(
    signal
)

print("\n" + "=" * 70)
print("TRADE COMMAND")
print("=" * 70)

print(command)


# ============================================================
# CHECK COMMAND
# ============================================================

if command is None:
    print(
        "ERROR: TradeManager created no command."
    )
    raise SystemExit(1)

if command.action != "PARTIAL_CLOSE":
    print(
        f"ERROR: Expected PARTIAL_CLOSE, "
        f"got {command.action}"
    )
    raise SystemExit(1)

# IMPORTANT:
# symbol=None is now CORRECT.
#
# It means:
# PARTIAL CLOSE ALL OPEN MT5 POSITIONS.

if command.symbol is not None:
    print(
        f"ERROR: Expected symbol=None "
        f"for global partial close, "
        f"got {command.symbol}"
    )
    raise SystemExit(1)

if command.percentage != 50.0:
    print(
        f"ERROR: Expected percentage=50.0, "
        f"got {command.percentage}"
    )
    raise SystemExit(1)


print("\n" + "=" * 70)
print("ALL MANAGEMENT CHECKS PASSED")
print("=" * 70)

print(
    "\nCLOSE 50% correctly produces:"
)

print(
    f"Action     : {command.action}"
)

print(
    f"Symbol     : {command.symbol}"
)

print(
    f"Percentage : {command.percentage}%"
)

print(
    "\nMeaning:"
)

print(
    "PARTIAL_CLOSE + symbol=None "
    "means close the requested percentage "
    "of ALL currently open MT5 positions."
)

print(
    "\nTEST PASSED"
)