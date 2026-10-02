import asyncio
import logging
import os

from telethon import TelegramClient, events
from dotenv import load_dotenv

from signal_parser import parse_signal
from trade_manager import TradeManager
from mt5_executor import MT5Executor


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            "listener.log",
            encoding="utf-8"
        ),
        logging.StreamHandler(),
    ],
)

log = logging.getLogger("listener")


# ============================================================
# TELEGRAM CONFIGURATION
# ============================================================

try:
    API_ID = int(os.environ["TG_API_ID"])
    API_HASH = os.environ["TG_API_HASH"]
except KeyError as error:
    raise RuntimeError(
        f"Missing Telegram environment variable: {error}"
    )


SESSION_NAME = "telegram_listener"


CHANNELS = [
    -1001927584198,  # Trading Room VVVIP
    -1004475058081,  # SmileDaTrader - testing channel
]


# ============================================================
# OBJECTS
# ============================================================

client = TelegramClient(
    SESSION_NAME,
    API_ID,
    API_HASH,
)

queue = asyncio.Queue()

trade_manager = TradeManager()
mt5_executor = MT5Executor()


# ============================================================
# MESSAGE QUEUE
# ============================================================

@client.on(events.NewMessage(chats=CHANNELS))
async def on_new(event):

    await queue.put(
        (
            "new",
            event.chat_id,
            event.message.id,
            event.date,
            event.raw_text,
        )
    )


@client.on(events.MessageEdited(chats=CHANNELS))
async def on_edit(event):

    await queue.put(
        (
            "edit",
            event.chat_id,
            event.message.id,
            event.date,
            event.raw_text,
        )
    )


# ============================================================
# PROCESS ONE TELEGRAM MESSAGE
# ============================================================

async def process_message(
    kind,
    chat_id,
    msg_id,
    date,
    text,
):
    """
    Process one Telegram message.

    NEW messages:
        Parse → TradeManager → TradeCommand → MT5

    EDITED messages:
        Parse and log only.
        Do NOT automatically execute.

    This prevents an edited entry signal from
    accidentally opening another trade.
    """

    log.info(
        "============================================================"
    )

    log.info(
        "%s MESSAGE | chat=%s | msg=%s",
        kind.upper(),
        chat_id,
        msg_id,
    )

    log.info(
        "MESSAGE TEXT:\n%s",
        text,
    )

    # ========================================================
    # PARSE
    # ========================================================

    signal = parse_signal(text)

    if signal is None:

        log.info(
            "NOT A VALID SIGNAL | msg=%s",
            msg_id,
        )

        return

    log.info(
        "SIGNAL DETECTED | "
        "type=%s | "
        "symbol=%s | "
        "direction=%s | "
        "action=%s | "
        "order_type=%s | "
        "entry=%s | "
        "SL=%s | "
        "TP=%s | "
        "percentage=%s",
        signal.signal_type,
        signal.symbol,
        signal.direction,
        signal.action,
        signal.order_type,
        signal.entry,
        signal.stop_loss,
        signal.take_profit,
        signal.percentage,
    )

    # ========================================================
    # EDIT SAFETY
    # ========================================================

    if kind == "edit":

        log.warning(
            "EDITED MESSAGE DETECTED. "
            "Signal will NOT be executed automatically. "
            "msg=%s",
            msg_id,
        )

        return

    # ========================================================
    # PROCESS THROUGH TRADE MANAGER
    # ========================================================

    try:

        trade_state = trade_manager.process_signal(
            signal
        )

    except Exception:

        log.exception(
            "TradeManager failed | msg=%s",
            msg_id,
        )

        return

    log.info(
        "TRADE MANAGER STATE: %s",
        trade_state,
    )

    # ========================================================
    # CREATE TRADE COMMAND
    # ========================================================

    try:

        command = trade_manager.create_command(
            signal
        )

    except Exception:

        log.exception(
            "Failed creating TradeCommand | msg=%s",
            msg_id,
        )

        return

    if command is None:

        log.warning(
            "NO TRADE COMMAND CREATED | "
            "msg=%s | signal=%s",
            msg_id,
            signal,
        )

        return

    log.info(
        "TRADE COMMAND CREATED: %s",
        command,
    )

    # ========================================================
    # EXECUTE THROUGH MT5
    # ========================================================

    try:

        result = mt5_executor.execute(
            command
        )

    except Exception:

        log.exception(
            "MT5 EXECUTION FAILED | msg=%s",
            msg_id,
        )

        return

    # ========================================================
    # RESULT
    # ========================================================

    log.info(
        "MT5 EXECUTION FINISHED | "
        "msg=%s | result=%s",
        msg_id,
        result,
    )


# ============================================================
# QUEUE PROCESSOR
# ============================================================

async def processor():

    while True:

        (
            kind,
            chat_id,
            msg_id,
            date,
            text,
        ) = await queue.get()

        try:

            await process_message(
                kind=kind,
                chat_id=chat_id,
                msg_id=msg_id,
                date=date,
                text=text,
            )

        except Exception:

            log.exception(
                "Unexpected processing error "
                "for message %s",
                msg_id,
            )

        finally:

            queue.task_done()


# ============================================================
# MAIN
# ============================================================

async def main():

    log.info(
        "Starting Telegram Trading Bot..."
    )

    # ========================================================
    # CONNECT MT5
    # ========================================================

    if not mt5_executor.connect():

        log.error(
            "Could not connect to MT5. "
            "Bot will not start."
        )

        return

    # ========================================================
    # START TELEGRAM
    # ========================================================

    try:

        await client.start()

        log.info(
            "Telegram connected successfully."
        )

        log.info(
            "Listening to channels: %s",
            CHANNELS,
        )

        # ====================================================
        # START MESSAGE PROCESSOR
        # ====================================================

        asyncio.create_task(
            processor()
        )

        log.info(
            "Trading pipeline is running."
        )

        log.info(
         "Pipeline: Telegram -> Parser -> TradeManager -> "
         "TradeCommand -> MT5"
         )

        # ====================================================
        # WAIT FOR TELEGRAM
        # ====================================================

        await client.run_until_disconnected()

    finally:

        log.info(
            "Shutting down Telegram Trading Bot..."
        )

        mt5_executor.disconnect()

        log.info(
            "Bot stopped."
        )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "\nBot stopped by user."
        )