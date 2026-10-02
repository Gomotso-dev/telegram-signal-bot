import MetaTrader5 as mt5


# ============================================================
# CONNECT
# ============================================================

if not mt5.initialize():

    print("MT5 initialization failed:")
    print(mt5.last_error())

    raise SystemExit()


print("MT5 connected.")


# ============================================================
# GET ALL SYMBOLS
# ============================================================

symbols = mt5.symbols_get()

if symbols is None:

    print("Could not retrieve symbols.")
    print(mt5.last_error())

    mt5.shutdown()

    raise SystemExit()


print(f"\nTotal symbols available: {len(symbols)}")


# ============================================================
# SEARCH FOR RELEVANT SYMBOLS
# ============================================================

keywords = [
    "US30",
    "DJ",
    "WALL",
    "XAU",
    "GOLD",
    "NAS",
    "USTEC",
    "NDX",
    "EURUSD",
]


print("\n" + "=" * 80)
print("POSSIBLE TRADING SYMBOLS")
print("=" * 80)


found = []

for symbol in symbols:

    name = symbol.name.upper()

    for keyword in keywords:

        if keyword in name:

            found.append(symbol.name)

            break


for name in sorted(set(found)):

    print(name)


# ============================================================
# DISCONNECT
# ============================================================

mt5.shutdown()

print("\nMT5 disconnected.")