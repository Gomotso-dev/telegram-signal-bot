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

message = "BUY US30"

print("\n" + "=" * 70)
print("FULL TRADING PIPELINE TEST")
print("=" * 70)

print(f"\nTELEGRAM MESSAGE:")
print(message)


# ============================================================
# STEP 1 — PARSE
# ============================================================

signal = parse_signal(message)

print("\nPARSED SIGNAL:")
print(signal)


if signal is None:
    print("ERROR: Signal could not be parsed.")
    executor.disconnect()
    exit()


# ============================================================
# STEP 2 — TRADE MANAGER
# ============================================================

trade_state = manager.process_signal(signal)

print("\nTRADE STATE:")
print(trade_state)


# ============================================================
# STEP 3 — CREATE COMMAND
# ============================================================

command = manager.create_command(signal)

print("\nTRADE COMMAND:")
print(command)


if command is None:
    print("ERROR: Trade command was not created.")
    executor.disconnect()
    exit()


# ============================================================
# STEP 4 — EXECUTE ON MT5
# ============================================================

print("\n" + "=" * 70)
print("EXECUTING ON MT5")
print("=" * 70)

result = executor.execute(command)

print("\nMT5 RESULT:")
print(result)


# ============================================================
# DISCONNECT
# ============================================================

executor.disconnect()