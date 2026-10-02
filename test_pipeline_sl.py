from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


manager = TradeManager()
executor = MT5Executor()


# ============================================================
# CONNECT
# ============================================================

if not executor.connect():
    print("Failed to connect to MT5.")
    exit()


# ============================================================
# MESSAGE
# ============================================================

message = "SL: @ 50600"

print("\n" + "=" * 70)
print("FULL PIPELINE — STOP LOSS TEST")
print("=" * 70)

print("\nTELEGRAM MESSAGE:")
print(message)


# ============================================================
# PARSE
# ============================================================

signal = parse_signal(message)

print("\nPARSED SIGNAL:")
print(signal)


# ============================================================
# IMPORTANT
# ============================================================
# TradeManager needs to know about the existing US30 trade.
#
# We recreate the internal trade state here because each
# Python test starts with a fresh TradeManager.

manager.process_signal(
    parse_signal("BUY US30")
)


# ============================================================
# CREATE COMMAND
# ============================================================

command = manager.create_command(signal)

print("\nTRADE COMMAND:")
print(command)


if command is None:
    print("ERROR: Could not create SL command.")
    executor.disconnect()
    exit()


# ============================================================
# EXECUTE
# ============================================================

print("\n" + "=" * 70)
print("EXECUTING SL MODIFICATION ON MT5")
print("=" * 70)

result = executor.execute(command)

print("\nMT5 RESULT:")
print(result)


# ============================================================
# VERIFY POSITION
# ============================================================

print("\n" + "=" * 70)
print("VERIFYING MT5 POSITION")
print("=" * 70)

position = executor.get_position("US30")

if position:
    print(f"Ticket: {position.ticket}")
    print(f"Symbol: {position.symbol}")
    print(f"Volume: {position.volume}")
    print(f"SL: {position.sl}")
    print(f"TP: {position.tp}")
else:
    print("US30 position not found.")


# ============================================================
# DISCONNECT
# ============================================================

executor.disconnect()