import logging
import sys


def setup_logging(environment: str) -> None:
    level = logging.INFO if environment.lower() == "production" else logging.DEBUG

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
        )
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Quiet down noisy third-party loggers; never log request/response bodies or secrets.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
