
from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


# ============================================================
# SETUP
# ============================================================

manager = TradeManager()
executor = MT5Executor()


# ============================================================
# CONNECT TO MT5
# ============================================================

if not executor.connect():
    print("Failed to connect to MT5.")
    exit()


# ============================================================
# TELEGRAM MESSAGE
# ============================================================

message = "CLOSE 50%"

print("\n" + "=" * 70)
print("FULL PIPELINE — PARTIAL CLOSE TEST")
print("=" * 70)

print("\nTELEGRAM MESSAGE:")
print(message)


# ============================================================
# PARSE SIGNAL
# ============================================================

signal = parse_signal(message)

print("\nPARSED SIGNAL:")
print(signal)


if signal is None:
    print("ERROR: Signal could not be parsed.")
    executor.disconnect()
    exit()


# ============================================================
# RECREATE EXISTING TRADE IN TRADE MANAGER
# ============================================================
# Each test starts with a fresh TradeManager.
#
# We recreate the US30 trade so the symbol-less
# "CLOSE 50%" command can resolve to US30.
# ============================================================

entry_signal = parse_signal("BUY US30")

if entry_signal is None:
    print("ERROR: Could not recreate US30 trade.")
    executor.disconnect()
    exit()


manager.process_signal(entry_signal)


# ============================================================
# CREATE TRADE COMMAND
# ============================================================

command = manager.create_command(signal)

print("\nTRADE COMMAND:")
print(command)


if command is None:
    print("ERROR: Could not create partial-close command.")
    executor.disconnect()
    exit()


# ============================================================
# EXECUTE ON MT5
# ============================================================

print("\n" + "=" * 70)
print("EXECUTING PARTIAL CLOSE ON MT5")
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
    print(f"Volume remaining: {position.volume}")
    print(f"SL: {position.sl}")
    print(f"TP: {position.tp}")
    print(f"Profit: {position.profit}")

else:

    print("US30 position not found.")


# ============================================================
# DISCONNECT
# ============================================================

executor.disconnect()