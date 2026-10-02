from dataclasses import dataclass
from typing import Optional


# ============================================================
# TRADE COMMAND
# ============================================================

@dataclass
class TradeCommand:
    """
    Standard instruction that will later be sent
    to the MT5 executor.
    """

    action: str

    symbol: Optional[str] = None
    direction: Optional[str] = None

    volume: Optional[float] = None
    percentage: Optional[float] = None

    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    ticket: Optional[int] = None
    