
from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


# ============================================================
# SETUP
# ============================================================

manager = TradeManager()
executor = MT5Executor()


# ============================================================
# CONNECT
# ============================================================

if not executor.connect():
    print("Failed to connect to MT5.")
    exit()


# ============================================================
# OPEN 0.10 LOT US30
# ============================================================

print("\n" + "=" * 70)
print("STEP 1 — OPEN 0.10 LOT US30")
print("=" * 70)

entry_signal = parse_signal("BUY US30")

if entry_signal is None:
    print("ERROR: Could not parse BUY US30.")
    executor.disconnect()
    exit()


# Create the normal TradeManager command
command = manager.create_command(entry_signal)

print("\nNORMAL COMMAND:")
print(command)


# ------------------------------------------------------------
# Override volume ONLY FOR THIS TEST
# ------------------------------------------------------------
# Your normal US30 bot setting remains 0.05.
# We use 0.10 here only so that 50% = 0.05,
# which satisfies the broker minimum.
# ------------------------------------------------------------

command.volume = 0.10

print("\nTEST COMMAND:")
print(command)


# ============================================================
# EXECUTE OPEN
# ============================================================

print("\n" + "=" * 70)
print("OPENING 0.10 LOT US30")
print("=" * 70)

open_result = executor.execute(command)

print("\nOPEN RESULT:")
print(open_result)


if open_result is None:
    print("ERROR: US30 position was not opened.")
    executor.disconnect()
    exit()


# ============================================================
# VERIFY OPEN POSITION
# ============================================================

position = executor.get_position("US30")

if position:

    print("\nOPEN POSITION:")
    print(f"Ticket: {position.ticket}")
    print(f"Symbol: {position.symbol}")
    print(f"Volume: {position.volume}")
    print(f"SL: {position.sl}")
    print(f"TP: {position.tp}")

else:

    print("ERROR: Could not find US30 position.")
    executor.disconnect()
    exit()


# ============================================================
# STEP 2 — PARSE CLOSE 50%
# ============================================================

print("\n" + "=" * 70)
print("STEP 2 — CLOSE 50%")
print("=" * 70)

message = "CLOSE 50%"

print("\nTELEGRAM MESSAGE:")
print(message)

signal = parse_signal(message)

print("\nPARSED SIGNAL:")
print(signal)


# ============================================================
# RECREATE TRADE STATE
# ============================================================

manager.process_signal(entry_signal)

partial_command = manager.create_command(signal)

print("\nPARTIAL CLOSE COMMAND:")
print(partial_command)


if partial_command is None:
    print("ERROR: Could not create partial-close command.")
    executor.disconnect()
    exit()


# ============================================================
# EXECUTE PARTIAL CLOSE
# ============================================================

print("\n" + "=" * 70)
print("EXECUTING 50% PARTIAL CLOSE")
print("=" * 70)

partial_result = executor.execute(partial_command)

print("\nPARTIAL CLOSE RESULT:")
print(partial_result)


# ============================================================
# VERIFY REMAINING POSITION
# ============================================================

print("\n" + "=" * 70)
print("VERIFYING REMAINING POSITION")
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

    print("No US30 position found.")


# ============================================================
# DISCONNECT
# ============================================================

executor.disconnect()