import math

import MetaTrader5 as mt5

from config import MT5_SYMBOL_MAP


class MT5Executor:

    def __init__(self):
        self.connected = False

    # ============================================================
    # CONNECTION
    # ============================================================

    def connect(self):
        if self.connected:
            return True

        if not mt5.initialize():
            print(
                f"MT5 initialization failed: "
                f"{mt5.last_error()}"
            )
            return False

        self.connected = True

        print("MT5 connected successfully.")

        return True

    def disconnect(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False

            print("MT5 disconnected.")

    # ============================================================
    # SYMBOLS
    # ============================================================

    def get_mt5_symbol(self, symbol):
        """
        Convert internal symbol to broker/MT5 symbol.

        Example:

            US30   -> US30m
            XAUUSD -> XAUUSDm
            NAS100 -> USTECm
            EURUSD -> EURUSDm
        """

        if symbol is None:
            return None

        return MT5_SYMBOL_MAP.get(
            symbol,
            symbol
        )

    def ensure_symbol(self, symbol):
        """
        Make sure the symbol exists and is visible in MT5.
        """

        if not symbol:
            print("No symbol supplied.")
            return None

        mt5_symbol = self.get_mt5_symbol(symbol)

        info = mt5.symbol_info(mt5_symbol)

        if info is None:
            print(
                f"Symbol not found: {mt5_symbol}"
            )
            return None

        if not info.visible:

            if not mt5.symbol_select(
                mt5_symbol,
                True
            ):
                print(
                    f"Could not select symbol: "
                    f"{mt5_symbol}"
                )
                return None

        return info

    def get_symbol_info(self, symbol):
        return self.ensure_symbol(symbol)

    def get_current_price(
        self,
        symbol,
        direction=None
    ):
        """
        Get the current market price.

        BUY  -> Ask
        SELL -> Bid
        None -> Mid price
        """

        mt5_symbol = self.get_mt5_symbol(symbol)

        tick = mt5.symbol_info_tick(
            mt5_symbol
        )

        if tick is None:
            print(
                f"Could not get price for "
                f"{mt5_symbol}"
            )
            return None

        if direction == "buy":
            return tick.ask

        if direction == "sell":
            return tick.bid

        return (tick.bid + tick.ask) / 2

    def normalize_price(
        self,
        symbol,
        price
    ):
        """
        Normalize a price according to the broker's
        number of digits for the symbol.
        """

        if price is None:
            return None

        info = self.ensure_symbol(symbol)

        if info is None:
            return float(price)

        return round(
            float(price),
            info.digits
        )

    # ============================================================
    # ACCOUNT
    # ============================================================

    def get_account_info(self):
        return mt5.account_info()

    # ============================================================
    # POSITIONS
    # ============================================================

    def get_positions(
        self,
        symbol=None
    ):
        """
        Return open MT5 positions.

        If symbol is supplied:

            Return ALL positions belonging
            to that internal symbol.

        If symbol is None:

            Return ALL open MT5 positions
            across ALL symbols.
        """

        positions = mt5.positions_get()

        if positions is None:
            return []

        # --------------------------------------------------------
        # No symbol = ALL positions
        # --------------------------------------------------------

        if symbol is None:
            return list(positions)

        # --------------------------------------------------------
        # Specific symbol
        # --------------------------------------------------------

        mt5_symbol = self.get_mt5_symbol(
            symbol
        )

        return [
            position
            for position in positions
            if position.symbol == mt5_symbol
        ]

    def get_position(
        self,
        symbol=None,
        ticket=None
    ):
        """
        Get one exact position.

        If ticket is supplied:

            Return that exact MT5 position.

        If no ticket is supplied:

            Return the first position matching
            the supplied symbol.

        For multiple-position management,
        use the all-position methods instead.
        """

        # --------------------------------------------------------
        # Exact ticket
        # --------------------------------------------------------

        if ticket is not None:

            positions = mt5.positions_get(
                ticket=int(ticket)
            )

            if positions:
                return positions[0]

            return None

        # --------------------------------------------------------
        # First matching position
        # --------------------------------------------------------

        positions = self.get_positions(
            symbol
        )

        if not positions:
            return None

        return positions[0]

    # ============================================================
    # OPEN POSITION
    # ============================================================

    def open_position(
        self,
        symbol,
        direction,
        volume,
        entry=None,
        stop_loss=None,
        take_profit=None,
    ):
        """
        Open a market position.

        Entry is currently informational for market orders.
        The actual market price comes from MT5.
        """

        info = self.ensure_symbol(
            symbol
        )

        if info is None:
            return None

        mt5_symbol = self.get_mt5_symbol(
            symbol
        )

        # --------------------------------------------------------
        # Direction
        # --------------------------------------------------------

        if direction == "buy":

            order_type = mt5.ORDER_TYPE_BUY
            price = info.ask

        elif direction == "sell":

            order_type = mt5.ORDER_TYPE_SELL
            price = info.bid

        else:

            print(
                f"Invalid direction: "
                f"{direction}"
            )

            return None

        # --------------------------------------------------------
        # Stop Loss
        # --------------------------------------------------------

        normalized_sl = (
            self.normalize_price(
                symbol,
                stop_loss
            )
            if stop_loss is not None
            else 0.0
        )

        # --------------------------------------------------------
        # Take Profit
        # --------------------------------------------------------

        normalized_tp = (
            self.normalize_price(
                symbol,
                take_profit
            )
            if take_profit is not None
            else 0.0
        )

        # --------------------------------------------------------
        # Order request
        # --------------------------------------------------------

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": mt5_symbol,
            "volume": float(volume),
            "type": order_type,
            "price": price,
            "sl": normalized_sl,
            "tp": normalized_tp,
            "deviation": 20,
            "magic": 100001,
            "comment": "Telegram Trading Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # --------------------------------------------------------
        # Send order
        # --------------------------------------------------------

        result = mt5.order_send(
            request
        )

        if result is None:

            print(
                f"OPEN ORDER FAILED: "
                f"{mt5.last_error()}"
            )

            return None

        print(
            f"OPEN ORDER RESULT: "
            f"retcode={result.retcode}, "
            f"order={result.order}, "
            f"deal={result.deal}, "
            f"volume={result.volume}, "
            f"price={result.price}"
        )

        if result.retcode != mt5.TRADE_RETCODE_DONE:

            print(
                f"Open failed. "
                f"Retcode: {result.retcode}"
            )

        return result

    # ============================================================
    # MODIFY STOP LOSS
    # ============================================================

    def modify_stop_loss(
        self,
        symbol,
        stop_loss,
        ticket=None,
    ):
        """
        If ticket is supplied:

            Modify that exact position.

        If ticket is None:

            Modify ALL positions for the symbol.

        Note:
            A symbol is required here because an SL price
            is instrument-specific.
        """

        if stop_loss is None:

            print(
                "MODIFY_SL requires a "
                "stop-loss price."
            )

            return None

        if symbol is None:

            print(
                "MODIFY_SL requires a symbol."
            )

            return None

        normalized_sl = self.normalize_price(
            symbol,
            stop_loss
        )

        positions = []

        # --------------------------------------------------------
        # Exact ticket
        # --------------------------------------------------------

        if ticket is not None:

            position = self.get_position(
                ticket=ticket
            )

            if position:
                positions.append(position)

        # --------------------------------------------------------
        # All positions for symbol
        # --------------------------------------------------------

        else:

            positions = self.get_positions(
                symbol
            )

        if not positions:

            print(
                f"No open positions found "
                f"for {symbol}."
            )

            return None

        results = []

        # --------------------------------------------------------
        # Modify every matching position
        # --------------------------------------------------------

        for position in positions:

            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": position.ticket,
                "sl": normalized_sl,
                "tp": float(position.tp),
            }

            result = mt5.order_send(
                request
            )

            if result is None:

                print(
                    f"MODIFY SL FAILED "
                    f"Ticket={position.ticket}: "
                    f"{mt5.last_error()}"
                )

            else:

                print(
                    f"MODIFY SL RESULT "
                    f"Ticket={position.ticket}: "
                    f"retcode={result.retcode}"
                )

            results.append(result)

        return results

    # ============================================================
    # MODIFY TAKE PROFIT
    # ============================================================

    def modify_take_profit(
        self,
        symbol,
        take_profit,
        ticket=None,
    ):
        """
        If ticket is supplied:

            Modify that exact position.

        If ticket is None:

            Modify ALL positions for the symbol.
        """

        if take_profit is None:

            print(
                "MODIFY_TP requires a "
                "take-profit price."
            )

            return None

        if symbol is None:

            print(
                "MODIFY_TP requires a symbol."
            )

            return None

        normalized_tp = self.normalize_price(
            symbol,
            take_profit
        )

        positions = []

        # --------------------------------------------------------
        # Exact ticket
        # --------------------------------------------------------

        if ticket is not None:

            position = self.get_position(
                ticket=ticket
            )

            if position:
                positions.append(position)

        # --------------------------------------------------------
        # All positions for symbol
        # --------------------------------------------------------

        else:

            positions = self.get_positions(
                symbol
            )

        if not positions:

            print(
                f"No open positions found "
                f"for {symbol}."
            )

            return None

        results = []

        # --------------------------------------------------------
        # Modify every matching position
        # --------------------------------------------------------

        for position in positions:

            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": position.ticket,
                "sl": float(position.sl),
                "tp": normalized_tp,
            }

            result = mt5.order_send(
                request
            )

            if result is None:

                print(
                    f"MODIFY TP FAILED "
                    f"Ticket={position.ticket}: "
                    f"{mt5.last_error()}"
                )

            else:

                print(
                    f"MODIFY TP RESULT "
                    f"Ticket={position.ticket}: "
                    f"retcode={result.retcode}"
                )

            results.append(result)

        return results

    # ============================================================
    # CLOSE ONE POSITION
    # ============================================================

    def close_position(
        self,
        position
    ):
        """
        Close ONE exact MT5 position.
        """

        tick = mt5.symbol_info_tick(
            position.symbol
        )

        if tick is None:

            print(
                f"Could not get price for "
                f"{position.symbol}"
            )

            return None

        # --------------------------------------------------------
        # BUY position is closed with SELL
        # SELL position is closed with BUY
        # --------------------------------------------------------

        if position.type == mt5.POSITION_TYPE_BUY:

            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid

        else:

            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": float(position.volume),
            "type": order_type,
            "position": position.ticket,
            "price": price,
            "deviation": 20,
            "magic": 100001,
            "comment": "Telegram Trading Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(
            request
        )

        if result is None:

            print(
                f"CLOSE FAILED "
                f"Ticket={position.ticket}: "
                f"{mt5.last_error()}"
            )

        else:

            print(
                f"CLOSE RESULT "
                f"Ticket={position.ticket}: "
                f"retcode={result.retcode}"
            )

        return result

    # ============================================================
    # PARTIAL CLOSE ONE POSITION
    # ============================================================

    def partial_close_position(
        self,
        position,
        percentage,
    ):
        """
        Partially close ONE exact position.

        Example:

            0.10 lots × 50% = 0.05 lots

        Broker minimum and volume step are respected.
        """

        # --------------------------------------------------------
        # Validate percentage
        # --------------------------------------------------------

        try:
            percentage = float(
                percentage
            )

        except (TypeError, ValueError):

            print(
                f"Invalid partial-close "
                f"percentage: {percentage}"
            )

            return None

        if percentage <= 0:

            print(
                "Partial-close percentage "
                "must be greater than 0."
            )

            return None

        if percentage > 100:

            print(
                "Partial-close percentage "
                "cannot exceed 100%."
            )

            return None

        # --------------------------------------------------------
        # Symbol information
        # --------------------------------------------------------

        info = mt5.symbol_info(
            position.symbol
        )

        if info is None:

            print(
                f"Could not get symbol info: "
                f"{position.symbol}"
            )

            return None

        # --------------------------------------------------------
        # Original volume
        # --------------------------------------------------------

        original_volume = float(
            position.volume
        )

        # --------------------------------------------------------
        # Calculate requested close volume
        # --------------------------------------------------------

        close_volume = (
            original_volume
            * (percentage / 100.0)
        )

        # --------------------------------------------------------
        # Floor to broker volume step
        # --------------------------------------------------------

        step = float(
            info.volume_step
        )

        if step > 0:

            close_volume = (
                math.floor(
                    close_volume / step
                )
                * step
            )

        close_volume = round(
            close_volume,
            8
        )

        minimum = float(
            info.volume_min
        )

        print(
            f"Ticket {position.ticket}: "
            f"{original_volume} × {percentage}% "
            f"= {close_volume}"
        )

        # --------------------------------------------------------
        # Broker minimum volume check
        # --------------------------------------------------------

        if close_volume < minimum:

            print(
                f"Ticket {position.ticket}: "
                f"calculated close volume "
                f"{close_volume} is below "
                f"minimum volume {minimum}. "
                f"Skipping."
            )

            return None

        # --------------------------------------------------------
        # Never close more than the position
        # --------------------------------------------------------

        if close_volume > original_volume:
            close_volume = original_volume

        # --------------------------------------------------------
        # Get current market price
        # --------------------------------------------------------

        tick = mt5.symbol_info_tick(
            position.symbol
        )

        if tick is None:

            print(
                f"Could not get price for "
                f"{position.symbol}"
            )

            return None

        # --------------------------------------------------------
        # Closing direction
        # --------------------------------------------------------

        if position.type == mt5.POSITION_TYPE_BUY:

            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid

        else:

            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask

        # --------------------------------------------------------
        # Order request
        # --------------------------------------------------------

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": close_volume,
            "type": order_type,
            "position": position.ticket,
            "price": price,
            "deviation": 20,
            "magic": 100001,
            "comment": "Telegram Trading Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # --------------------------------------------------------
        # Send partial close
        # --------------------------------------------------------

        result = mt5.order_send(
            request
        )

        if result is None:

            print(
                f"PARTIAL CLOSE FAILED "
                f"Ticket={position.ticket}: "
                f"{mt5.last_error()}"
            )

        else:

            print(
                f"PARTIAL CLOSE RESULT "
                f"Ticket={position.ticket}: "
                f"retcode={result.retcode}, "
                f"volume={result.volume}"
            )

        return result

    # ============================================================
    # PARTIAL CLOSE ALL MATCHING POSITIONS
    # ============================================================

    def partial_close(
        self,
        symbol=None,
        percentage=None,
        ticket=None,
    ):
        """
        If ticket is supplied:

            Partially close ONLY that position.

        If ticket is None and symbol is supplied:

            Partially close ALL positions
            for that symbol.

        If ticket is None and symbol is None:

            Partially close ALL open positions
            across ALL symbols.
        """

        # --------------------------------------------------------
        # Validate percentage
        # --------------------------------------------------------

        if percentage is None:

            print(
                "Partial close requires "
                "a percentage."
            )

            return None

        try:
            percentage = float(
                percentage
            )

        except (TypeError, ValueError):

            print(
                f"Invalid partial-close "
                f"percentage: {percentage}"
            )

            return None

        if percentage <= 0:

            print(
                "Partial-close percentage "
                "must be greater than 0."
            )

            return None

        if percentage > 100:

            print(
                "Partial-close percentage "
                "cannot exceed 100%."
            )

            return None

        # --------------------------------------------------------
        # Exact ticket
        # --------------------------------------------------------

        if ticket is not None:

            position = self.get_position(
                ticket=ticket
            )

            if position is None:

                print(
                    f"Position ticket "
                    f"{ticket} not found."
                )

                return None

            return self.partial_close_position(
                position,
                percentage
            )

        # --------------------------------------------------------
        # ALL POSITIONS
        #
        # If symbol=None, get_positions(None)
        # returns every open MT5 position.
        # --------------------------------------------------------

        positions = self.get_positions(
            symbol
        )

        if not positions:

            if symbol:

                print(
                    f"No open positions found "
                    f"for {symbol}."
                )

            else:

                print(
                    "No open positions found."
                )

            return None

        # --------------------------------------------------------
        # Display what we found
        # --------------------------------------------------------

        if symbol:

            print(
                f"PARTIAL CLOSE: "
                f"{percentage}% of "
                f"{len(positions)} "
                f"{symbol} position(s)."
            )

        else:

            print(
                f"PARTIAL CLOSE: "
                f"{percentage}% of "
                f"{len(positions)} "
                f"position(s) across ALL symbols."
            )

        results = []

        # --------------------------------------------------------
        # Process every position separately
        # --------------------------------------------------------

        for position in positions:

            result = self.partial_close_position(
                position,
                percentage
            )

            results.append(
                {
                    "ticket": position.ticket,
                    "symbol": position.symbol,
                    "result": result,
                }
            )

        return results

    # ============================================================
    # LOCK ONE POSITION
    # ============================================================

    def lock_position(
        self,
        position
    ):
        """
        Lock ONE exact position at breakeven.

        BUY:

            SL = position entry price

        SELL:

            SL = position entry price

        Existing TP is preserved.

        Volume is unchanged.
        """

        # --------------------------------------------------------
        # Entry price
        # --------------------------------------------------------

        entry_price = float(
            position.price_open
        )

        # --------------------------------------------------------
        # Broker symbol information
        # --------------------------------------------------------

        info = mt5.symbol_info(
            position.symbol
        )

        if info is None:

            print(
                f"Could not get symbol info "
                f"for {position.symbol}"
            )

            return None

        # --------------------------------------------------------
        # Normalize entry price
        # --------------------------------------------------------

        entry_price = round(
            entry_price,
            info.digits
        )

        # --------------------------------------------------------
        # SL = own entry price
        # TP stays unchanged
        # --------------------------------------------------------

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": position.symbol,
            "position": position.ticket,
            "sl": entry_price,
            "tp": float(position.tp),
        }

        result = mt5.order_send(
            request
        )

        if result is None:

            print(
                f"LOCK FAILED "
                f"Ticket={position.ticket}: "
                f"{mt5.last_error()}"
            )

            return None

        print(
            f"LOCK RESULT "
            f"Ticket={position.ticket}: "
            f"Entry={entry_price}, "
            f"SL={entry_price}, "
            f"TP={position.tp}, "
            f"retcode={result.retcode}"
        )

        return result

    # ============================================================
    # LOCK ALL MATCHING POSITIONS
    # ============================================================

    def lock_all_positions(
        self,
        symbol=None
    ):
        """
        Lock ALL open positions.

        If symbol is supplied:

            Lock all positions for that symbol.

        If symbol is None:

            Lock ALL positions across ALL symbols.

        Each position receives its OWN entry price
        as its stop-loss.
        """

        # --------------------------------------------------------
        # Get positions
        # --------------------------------------------------------

        positions = self.get_positions(
            symbol
        )

        if not positions:

            if symbol:

                print(
                    f"No open {symbol} "
                    f"positions found."
                )

            else:

                print(
                    "No open positions found."
                )

            return None

        # --------------------------------------------------------
        # Display
        # --------------------------------------------------------

        if symbol:

            print(
                f"\nLOCKING ALL {symbol} "
                f"POSITIONS AT BREAKEVEN"
            )

        else:

            print(
                "\nLOCKING ALL OPEN "
                "POSITIONS AT BREAKEVEN"
            )

        print(
            f"Found {len(positions)} "
            f"position(s)."
        )

        results = []

        # --------------------------------------------------------
        # Lock every position individually
        # --------------------------------------------------------

        for position in positions:

            entry_price = position.price_open

            print(
                f"Ticket {position.ticket}: "
                f"Symbol={position.symbol} | "
                f"Entry={entry_price} "
                f"-> SL={entry_price}"
            )

            result = self.lock_position(
                position
            )

            results.append(
                {
                    "ticket": position.ticket,
                    "symbol": position.symbol,
                    "result": result,
                }
            )

        return results

    # ============================================================
    # EXECUTE TRADE COMMAND
    # ============================================================

    def execute(
        self,
        command
    ):

        if command is None:

            print(
                "Cannot execute a "
                "None command."
            )

            return None

        # ========================================================
        # OPEN
        # ========================================================

        if command.action == "OPEN":

            return self.open_position(
                symbol=command.symbol,
                direction=command.direction,
                volume=command.volume,
                entry=command.entry,
                stop_loss=command.stop_loss,
                take_profit=command.take_profit,
            )

        # ========================================================
        # MODIFY STOP LOSS
        # ========================================================

        elif command.action == "MODIFY_SL":

            return self.modify_stop_loss(
                symbol=command.symbol,
                stop_loss=command.stop_loss,
                ticket=command.ticket,
            )

        # ========================================================
        # MODIFY TAKE PROFIT
        # ========================================================

        elif command.action == "MODIFY_TP":

            return self.modify_take_profit(
                symbol=command.symbol,
                take_profit=command.take_profit,
                ticket=command.ticket,
            )

        # ========================================================
        # CLOSE
        # ========================================================

        elif command.action == "CLOSE":

            # ----------------------------------------------------
            # Exact ticket
            # ----------------------------------------------------

            if command.ticket is not None:

                position = self.get_position(
                    ticket=command.ticket
                )

                if position is None:

                    print(
                        f"Position ticket "
                        f"{command.ticket} "
                        f"not found."
                    )

                    return None

                return self.close_position(
                    position
                )

            # ----------------------------------------------------
            # Get matching positions
            #
            # symbol=None means ALL symbols.
            # ----------------------------------------------------

            positions = self.get_positions(
                command.symbol
            )

            if not positions:

                if command.symbol:

                    print(
                        f"No open "
                        f"{command.symbol} "
                        f"positions found."
                    )

                else:

                    print(
                        "No open positions found."
                    )

                return None

            # ----------------------------------------------------
            # Display
            # ----------------------------------------------------

            if command.symbol:

                print(
                    f"\nCLOSE: Found "
                    f"{len(positions)} "
                    f"{command.symbol} "
                    f"position(s)."
                )

            else:

                print(
                    f"\nCLOSE: Found "
                    f"{len(positions)} "
                    f"open position(s) "
                    f"across ALL symbols."
                )

            results = []

            # ----------------------------------------------------
            # Close every position individually
            # ----------------------------------------------------

            for position in positions:

                result = self.close_position(
                    position
                )

                results.append(
                    {
                        "ticket": position.ticket,
                        "symbol": position.symbol,
                        "result": result,
                    }
                )

            return results

        # ========================================================
        # PARTIAL CLOSE
        # ========================================================

        elif command.action == "PARTIAL_CLOSE":

            return self.partial_close(
                symbol=command.symbol,
                percentage=command.percentage,
                ticket=command.ticket,
            )

        # ========================================================
        # LOCK
        # ========================================================

        elif command.action == "LOCK":

            return self.lock_all_positions(
                symbol=command.symbol
            )

        # ========================================================
        # ADD MORE
        # ========================================================

        elif command.action == "ADD_MORE":

            if not command.symbol:

                print(
                    "ADD_MORE requires "
                    "a symbol."
                )

                return None

            if not command.direction:

                print(
                    "ADD_MORE requires "
                    "a direction."
                )

                return None

            if not command.volume:

                print(
                    "ADD_MORE requires "
                    "a volume."
                )

                return None

            print(
                f"\nADD MORE: "
                f"{command.direction.upper()} "
                f"{command.symbol} "
                f"{command.volume} lots"
            )

            return self.open_position(
                symbol=command.symbol,
                direction=command.direction,
                volume=command.volume,
                entry=command.entry,
                stop_loss=command.stop_loss,
                take_profit=command.take_profit,
            )

        # ========================================================
        # UNKNOWN ACTION
        # ========================================================

        else:

            print(
                f"Unknown action: "
                f"{command.action}"
            )

            return None