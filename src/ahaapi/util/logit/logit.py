import atexit
import html
import logging
import logging.handlers
import os
import queue
import smtplib
import sys
import threading
from datetime import datetime, time
from pathlib import Path

import colorlog

from ahaapi.util.env.environment import env_bool, env_int, env_level

logger = logging.getLogger(__name__)


class PreciseConsoleFormatter(colorlog.ColoredFormatter):
    """Console formatter with microsecond precision."""

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)

        if datefmt:
            return f"{dt.strftime(datefmt)}.{dt.microsecond:06d}"

        return dt.isoformat(sep=" ", timespec="microseconds")


class PreciseFileFormatter(logging.Formatter):
    """File formatter with microsecond precision."""

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)

        if datefmt:
            return f"{dt.strftime(datefmt)}.{dt.microsecond:06d}"

        return dt.isoformat(sep=" ", timespec="microseconds")


class HTMLSMTPHandler(logging.handlers.SMTPHandler):
    """SMTP handler that sends HTML-formatted log messages."""

    def emit(self, record):
        smtp = None

        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            port = self.mailport or smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)

            if self.secure is not None:
                smtp.starttls()

            if self.username:
                smtp.login(self.username, self.password)

            timestamp = datetime.fromtimestamp(
                record.created
            ).isoformat(sep=" ", timespec="microseconds")

            message = MIMEMultipart("alternative")
            message["From"] = self.fromaddr
            message["To"] = ", ".join(self.toaddrs)
            message["Subject"] = self.getSubject(record)

            html_body = f"""
            <html>
              <body>
                <h2 style="color:red;">Critical System Alert</h2>
                <table border="1"
                       style="border-collapse:collapse;width:100%;">
                  <tr>
                    <th>Timestamp</th>
                    <td>{html.escape(timestamp)}</td>
                  </tr>
                  <tr>
                    <th>Level</th>
                    <td>{html.escape(record.levelname)}</td>
                  </tr>
                  <tr>
                    <th>Message</th>
                    <td>{html.escape(record.getMessage())}</td>
                  </tr>
                  <tr>
                    <th>Location</th>
                    <td>{html.escape(record.pathname)}
                        (Line: {record.lineno})</td>
                  </tr>
                </table>
              </body>
            </html>
            """

            message.attach(MIMEText(html_body, "html", "utf-8"))
            smtp.sendmail(
                self.fromaddr,
                self.toaddrs,
                message.as_string(),
            )

        except (OSError, smtplib.SMTPException):
            self.handleError(record)

        finally:
            if smtp is not None:
                try:
                    smtp.quit()
                except (OSError, smtplib.SMTPException):
                    pass


def handle_exception(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions from the main thread."""

    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(
            exc_type, exc_value, exc_traceback
        )
        return

    logger.critical(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def handle_thread_exception(args):
    """Log uncaught exceptions from worker threads."""

    logger.critical(
        "Unhandled exception in thread: %s",
        args.exc_type,
        exc_info=(
            args.exc_type,
            args.exc_value,
            args.exc_traceback,
        ),
    )


def set_unhandled_exception_logging():
    sys.excepthook = handle_exception
    threading.excepthook = handle_thread_exception


def get_formats():
    console_format = (
        "[%(asctime)s] [%(levelname)s] "
        "[%(name)s:%(lineno)d] - %(message)s"
    )

    file_format = (
        "[%(asctime)s] [%(levelname)s] [%(threadName)s] "
        "[%(name)s.%(funcName)s:%(lineno)d] - %(message)s"
    )

    date_format = "%Y-%m-%d %H:%M:%S"

    return file_format, console_format, date_format


def get_console_handler():
    _, console_format, date_format = get_formats()

    handler = logging.StreamHandler()
    handler.setLevel(env_level("LOG_CONSOLE_LEVEL", "DEBUG"))

    handler.setFormatter(
        PreciseConsoleFormatter(
            "%(log_color)s" + console_format,
            datefmt=date_format,
            log_colors={
                "DEBUG": "cyan",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red,bg_white",
            },
        )
    )

    return handler


def get_file_handler():
    file_format, _, date_format = get_formats()

    log_path = Path(
        os.getenv("LOG_FILE_PATH", "log/aha.log")
    )

    if not log_path.is_absolute():
        log_path = Path.cwd() / log_path

    log_path.parent.mkdir(parents=True, exist_ok=True)

    backup_count = env_int("LOG_FILE_BACKUP_COUNT", 180)
    rotation_hour = env_int("LOG_FILE_ROTATION_HOUR", 2)

    if not 0 <= rotation_hour <= 23:
        raise ValueError("LOG_FILE_ROTATION_HOUR must be 0-23.")

    handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_path),
        when="midnight",
        interval=1,
        atTime=time(rotation_hour, 0),
        backupCount=backup_count,
        encoding="utf-8",
        delay=True,
    )

    handler.setLevel(env_level("LOG_FILE_LEVEL", "DEBUG"))
    handler.setFormatter(
        PreciseFileFormatter(file_format, datefmt=date_format)
    )

    return handler


def get_email_handler():
    if not env_bool("LOG_EMAIL_ENABLED", False):
        return None

    host = os.getenv("LOG_EMAIL_HOST", "").strip()
    sender = os.getenv("LOG_EMAIL_FROM", "").strip()
    recipients = [
        address.strip()
        for address in os.getenv("LOG_EMAIL_TO", "").split(",")
        if address.strip()
    ]

    if not host or not sender or not recipients:
        raise ValueError(
            "Email logging requires LOG_EMAIL_HOST, "
            "LOG_EMAIL_FROM, and LOG_EMAIL_TO."
        )

    port = env_int("LOG_EMAIL_PORT", 587)
    username = os.getenv("LOG_EMAIL_USERNAME", "").strip()
    password = os.getenv("LOG_EMAIL_PASSWORD", "")

    use_tls = env_bool("LOG_EMAIL_USE_TLS", True)

    credentials = (
        (username, password)
        if username
        else None
    )

    handler = HTMLSMTPHandler(
        mailhost=(host, port),
        fromaddr=sender,
        toaddrs=recipients,
        subject="[Critical System Alert]",
        credentials=credentials,
        secure=() if use_tls else None,
    )

    handler.setLevel(env_level("LOG_EMAIL_LEVEL", "CRITICAL"))

    file_format, _, date_format = get_formats()
    handler.setFormatter(
        PreciseFileFormatter(file_format, datefmt=date_format)
    )

    return handler


def setup_logging(asynchronous: bool = False):
    """Configure root logging using environment variables."""

    set_unhandled_exception_logging()

    handlers = []

    if env_bool("LOG_CONSOLE_ENABLED", True):
        handlers.append(get_console_handler())

    if env_bool("LOG_FILE_ENABLED", True):
        handlers.append(get_file_handler())

    email_handler = get_email_handler()

    if email_handler is not None:
        handlers.append(email_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for old_handler in root_logger.handlers[:]:
        root_logger.removeHandler(old_handler)
        old_handler.close()

    if not asynchronous:
        for handler in handlers:
            root_logger.addHandler(handler)

        return root_logger

    log_queue = queue.Queue(-1)

    listener = logging.handlers.QueueListener(
        log_queue,
        *handlers,
        respect_handler_level=True,
    )
    listener.start()

    root_logger.addHandler(
        logging.handlers.QueueHandler(log_queue)
    )

    atexit.register(listener.stop)

    return root_logger


def setup_sync_logging():
    return setup_logging(asynchronous=False)


def setup_async_logging():
    return setup_logging(asynchronous=True)
