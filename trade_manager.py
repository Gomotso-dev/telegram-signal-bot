from dataclasses import dataclass
from typing import Optional, Dict

from signal_parser import TradingSignal
from trade_command import TradeCommand
from config import SYMBOL_LOT_SIZES


# ============================================================
# TRADE STATE
# ============================================================

@dataclass
class TradeState:
    symbol: str
    direction: str
    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    volume: Optional[float] = None
    is_open: bool = False
    is_locked: bool = False


# ============================================================
# TRADE MANAGER
# ============================================================

class TradeManager:

    def __init__(self):
        self.trades: Dict[str, TradeState] = {}

    # ========================================================
    # LOT SIZE
    # ========================================================

    def get_lot_size(self, symbol: str) -> float:
        """
        Get the configured lot size for a symbol.
        """

        if symbol not in SYMBOL_LOT_SIZES:
            raise ValueError(
                f"No lot size configured for symbol: {symbol}"
            )

        return SYMBOL_LOT_SIZES[symbol]

    # ========================================================
    # FIND TRADE
    # ========================================================

    def _find_trade(
        self,
        symbol: Optional[str] = None
    ) -> Optional[TradeState]:
        """
        Find an open trade.

        If symbol is supplied:
            return that trade.

        If symbol is not supplied:
            return the only open trade.

        If there are multiple open trades and no symbol
        is supplied:
            return None to avoid guessing.
        """

        # ----------------------------------------------------
        # Symbol explicitly supplied
        # ----------------------------------------------------

        if symbol:
            trade = self.trades.get(symbol)

            if trade and trade.is_open:
                return trade

            return None

        # ----------------------------------------------------
        # No symbol supplied
        # ----------------------------------------------------

        open_trades = [
            trade
            for trade in self.trades.values()
            if trade.is_open
        ]

        if len(open_trades) == 1:
            return open_trades[0]

        return None

    # ========================================================
    # HANDLE ENTRY
    # ========================================================

    def handle_entry(
        self,
        signal: TradingSignal
    ) -> Optional[TradeState]:

        if not signal.symbol:
            return None

        if not signal.direction:
            return None

        # ----------------------------------------------------
        # Get symbol-specific lot size
        # ----------------------------------------------------

        volume = self.get_lot_size(signal.symbol)

        # ----------------------------------------------------
        # Check if trade already exists
        # ----------------------------------------------------

        existing_trade = self.trades.get(signal.symbol)

        if existing_trade and existing_trade.is_open:
            # Do not automatically overwrite the existing trade.
            # ADD_MORE is handled separately.
            return existing_trade

        # ----------------------------------------------------
        # Create new trade
        # ----------------------------------------------------

        trade = TradeState(
            symbol=signal.symbol,
            direction=signal.direction,
            entry=signal.entry,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            volume=volume,
            is_open=True,
            is_locked=False,
        )

        self.trades[signal.symbol] = trade

        return trade

    # ========================================================
    # UPDATE STOP LOSS
    # ========================================================

    def update_stop_loss(
        self,
        signal: TradingSignal
    ) -> Optional[TradeState]:

        trade = self._find_trade(signal.symbol)

        if not trade:
            return None

        if signal.stop_loss is None:
            return trade

        trade.stop_loss = signal.stop_loss

        return trade

    # ========================================================
    # UPDATE TAKE PROFIT
    # ========================================================

    def update_take_profit(
        self,
        signal: TradingSignal
    ) -> Optional[TradeState]:

        trade = self._find_trade(signal.symbol)

        if not trade:
            return None

        if signal.take_profit is None:
            return trade

        trade.take_profit = signal.take_profit

        return trade

    # ========================================================
    # LOCK TRADE
    # ========================================================

    def lock_trade(
        self,
        signal: TradingSignal
    ) -> Optional[TradeState]:

        trade = self._find_trade(signal.symbol)

        if not trade:
            return None

        trade.is_locked = True

        return trade

    # ========================================================
    # LOCK ALL TRADES
    # ========================================================

    def lock_all_trades(self):
        """
        Lock every currently open logical trade.
        """

        open_trades = [
            trade
            for trade in self.trades.values()
            if trade.is_open
        ]

        for trade in open_trades:
            trade.is_locked = True

        return open_trades

    # ========================================================
    # CLOSE TRADE
    # ========================================================

    def close_trade(
        self,
        signal: TradingSignal
    ) -> Optional[TradeState]:

        trade = self._find_trade(signal.symbol)

        if not trade:
            return None

        trade.is_open = False

        return trade

    # ========================================================
    # CLOSE ALL TRADES
    # ========================================================

    def close_all_trades(self):
        """
        Close every currently open logical trade.
        """

        open_trades = [
            trade
            for trade in self.trades.values()
            if trade.is_open
        ]

        for trade in open_trades:
            trade.is_open = False

        return open_trades

    # ========================================================
    # PARTIAL CLOSE
    # ========================================================

    def partial_close(
        self,
        signal: TradingSignal
    ) -> Optional[TradeState]:

        trade = self._find_trade(signal.symbol)

        if not trade:
            return None

        if signal.percentage is None:
            return trade

        if trade.volume is None:
            return trade

        # ----------------------------------------------------
        # Calculate remaining volume
        # ----------------------------------------------------

        remaining_percentage = 100 - signal.percentage

        if remaining_percentage <= 0:

            trade.volume = 0
            trade.is_open = False

        else:

            trade.volume = round(
                trade.volume * remaining_percentage / 100,
                2
            )

        return trade

    # ========================================================
    # PARTIAL CLOSE ALL TRADES
    # ========================================================

    def partial_close_all_trades(
        self,
        percentage: float
    ):
        """
        Apply the requested partial-close percentage
        to every currently open logical trade.
        """

        open_trades = [
            trade
            for trade in self.trades.values()
            if trade.is_open
        ]

        for trade in open_trades:

            if trade.volume is None:
                continue

            remaining_percentage = 100 - percentage

            if remaining_percentage <= 0:

                trade.volume = 0
                trade.is_open = False

            else:

                trade.volume = round(
                    trade.volume * remaining_percentage / 100,
                    2
                )

        return open_trades

    # ========================================================
    # ADD MORE
    # ========================================================

    def add_more(
        self,
        signal: TradingSignal
    ) -> Optional[TradeState]:

        if not signal.symbol:
            return None

        symbol = signal.symbol

        # ----------------------------------------------------
        # Find the previous trade for this symbol
        # ----------------------------------------------------

        existing_trade = self.trades.get(symbol)

        if not existing_trade:

            print(
                f"No previous trade found for {symbol}. "
                f"Cannot determine ADD MORE direction."
            )

            return None

        # ----------------------------------------------------
        # Inherit the previous trade direction
        # ----------------------------------------------------

        direction = existing_trade.direction
        volume = self.get_lot_size(symbol)

        # ----------------------------------------------------
        # If the previous trade is open,
        # add another position
        # ----------------------------------------------------

        if existing_trade.is_open:

            existing_trade.volume += volume

            print(
                f"ADD MORE: inherited {direction.upper()} "
                f"direction for {symbol}"
            )

            return existing_trade

        # ----------------------------------------------------
        # If previous trade is closed, create a new logical
        # trade using the previous direction
        # ----------------------------------------------------

        trade = TradeState(
            symbol=symbol,
            direction=direction,
            volume=volume,
            is_open=True,
            is_locked=False,
        )

        self.trades[symbol] = trade

        print(
            f"ADD MORE: reopened {symbol} "
            f"using previous {direction.upper()} direction"
        )

        return trade

    # ========================================================
    # GET TRADE
    # ========================================================

    def get_trade(
        self,
        symbol: str
    ) -> Optional[TradeState]:

        return self._find_trade(symbol)

    # ========================================================
    # PROCESS SIGNAL
    # ========================================================

    def process_signal(
        self,
        signal: TradingSignal
    ):

        # ----------------------------------------------------
        # ENTRY
        # ----------------------------------------------------

        if signal.signal_type == "entry":
            return self.handle_entry(signal)

        # ----------------------------------------------------
        # UPDATE STOP LOSS
        # ----------------------------------------------------

        if signal.action == "update_sl":
            return self.update_stop_loss(signal)

        # ----------------------------------------------------
        # UPDATE TAKE PROFIT
        # ----------------------------------------------------

        if signal.action == "update_tp":
            return self.update_take_profit(signal)

        # ----------------------------------------------------
        # LOCK
        # ----------------------------------------------------

        if signal.action == "lock":

            # No symbol = LOCK EVERYTHING
            if signal.symbol is None:
                return self.lock_all_trades()

            # Specific symbol = LOCK THAT SYMBOL
            return self.lock_trade(signal)

        # ----------------------------------------------------
        # CLOSE
        # ----------------------------------------------------

        if signal.action == "close":

            # No symbol = CLOSE EVERYTHING
            if signal.symbol is None:
                return self.close_all_trades()

            # Specific symbol = CLOSE THAT SYMBOL
            return self.close_trade(signal)

        # ----------------------------------------------------
        # PARTIAL CLOSE
        # ----------------------------------------------------

        if signal.action == "partial_close":

            if signal.percentage is None:
                return None

            # No symbol = PARTIAL CLOSE EVERYTHING
            if signal.symbol is None:
                return self.partial_close_all_trades(
                    signal.percentage
                )

            # Specific symbol = PARTIAL CLOSE THAT SYMBOL
            return self.partial_close(signal)

        # ----------------------------------------------------
        # ADD MORE
        # ----------------------------------------------------

        if signal.action == "add_more":
            return self.add_more(signal)

        return None

    # ========================================================
    # CREATE TRADE COMMAND
    # ========================================================

    def create_command(
        self,
        signal: TradingSignal
    ) -> Optional[TradeCommand]:

        # ====================================================
        # ENTRY
        # ====================================================

        if signal.signal_type == "entry":

            if not signal.symbol:
                return None

            if not signal.direction:
                return None

            return TradeCommand(
                action="OPEN",
                symbol=signal.symbol,
                direction=signal.direction,
                volume=self.get_lot_size(signal.symbol),
                entry=signal.entry,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
            )

        # ====================================================
        # MANAGEMENT
        # ====================================================

        symbol = signal.symbol

        # ----------------------------------------------------
        # SYMBOL-LESS MANAGEMENT
        # ----------------------------------------------------
        #
        # CLOSE / PARTIAL_CLOSE / LOCK without a symbol
        # means ALL currently open MT5 positions.
        #
        # SL / TP and ADD MORE still need a specific symbol
        # when multiple symbols are involved.
        # ----------------------------------------------------

        if symbol is None:

            if signal.action in {
                "close",
                "partial_close",
                "lock",
            }:

                # Keep symbol=None.
                #
                # MT5Executor interprets this as
                # ALL currently open positions.

                symbol = None

            else:

                open_trades = [
                    trade
                    for trade in self.trades.values()
                    if trade.is_open
                ]

                if len(open_trades) == 1:

                    symbol = open_trades[0].symbol

                elif len(open_trades) > 1:

                    print(
                        "Multiple open symbols found. "
                        "Management command needs a symbol."
                    )

                    return None

                else:

                    stored_trades = list(
                        self.trades.values()
                    )

                    if len(stored_trades) == 1:

                        symbol = stored_trades[0].symbol

                    else:

                        print(
                            "No unique trade found for "
                            "management command."
                        )

                        return None

        # ====================================================
        # UPDATE SL
        # ====================================================

        if signal.action == "update_sl":

            if signal.stop_loss is None:
                return None

            return TradeCommand(
                action="MODIFY_SL",
                symbol=symbol,
                stop_loss=signal.stop_loss,
                ticket=None,
            )

        # ====================================================
        # UPDATE TP
        # ====================================================

        if signal.action == "update_tp":

            if signal.take_profit is None:
                return None

            return TradeCommand(
                action="MODIFY_TP",
                symbol=symbol,
                take_profit=signal.take_profit,
                ticket=None,
            )

        # ====================================================
        # LOCK
        # ====================================================

        if signal.action == "lock":

            return TradeCommand(
                action="LOCK",
                symbol=symbol,
                ticket=None,
            )

        # ====================================================
        # CLOSE
        # ====================================================

        if signal.action == "close":

            return TradeCommand(
                action="CLOSE",
                symbol=symbol,
                ticket=None,
            )

        # ====================================================
        # PARTIAL CLOSE
        # ====================================================

        if signal.action == "partial_close":

            if signal.percentage is None:
                return None

            return TradeCommand(
                action="PARTIAL_CLOSE",
                symbol=symbol,
                percentage=signal.percentage,
                ticket=None,
            )

        # ====================================================
        # ADD MORE
        # ====================================================

        if signal.action == "add_more":

            trade = self.trades.get(symbol)

            if not trade:
                return None

            return TradeCommand(
                action="ADD_MORE",
                symbol=symbol,
                direction=trade.direction,
                volume=self.get_lot_size(symbol),
                ticket=None,
            )

        return None

    # ========================================================
    # PRINT TRADES
    # ========================================================

    def print_trades(self):

        print("\n" + "=" * 70)
        print("CURRENT TRADES")
        print("=" * 70)

        if not self.trades:

            print("No trades.")
            return

        for symbol, trade in self.trades.items():

            print(
                f"{symbol}: "
                f"{trade.direction.upper()} | "
                f"Volume={trade.volume} | "
                f"Open={trade.is_open} | "
                f"Locked={trade.is_locked} | "
                f"Entry={trade.entry} | "
                f"SL={trade.stop_loss} | "
                f"TP={trade.take_profit}"
            )

        print("=" * 70)