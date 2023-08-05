# Standard Packages
import logging
import os

# External Packages
from fastapi import FastAPI
from rich.logging import RichHandler
import uvicorn

# Internal Packages
from velarium.configure import configure_routes, initialize_agent, initialize_conversation_sessions
from velarium import state

# Setup Logger
rich_handler = RichHandler(rich_tracebacks=True)
rich_handler.setFormatter(fmt=logging.Formatter(fmt="%(message)s", datefmt="[%X]"))
logging.basicConfig(handlers=[rich_handler])

logger = logging.getLogger("velarium")


# Initialize the Application Server
if os.getenv("DEBUG", False):
    app = FastAPI()
else:
    app = FastAPI(docs_url=None, redoc_url=None)


def start_server(app: FastAPI, host="0.0.0.0", port=8488, socket=None):
    logger.info("🌖 Velarium is ready to use")
    if socket:
        uvicorn.run(app, proxy_headers=True, uds=socket, log_level="debug", use_colors=True, log_config=None)
    else:
        uvicorn.run(app, host=host, port=port, log_level="debug", use_colors=True, log_config=None)
    logger.info("🌒 Stopping Velarium")


def run():
    state.converse = initialize_agent()
    try:
        state.conversation_sessions = initialize_conversation_sessions()
    except Exception as e:
        logger.error(f"Failed to initialize conversation sessions: {e}. You may need to run python src/velarium/manage.py migrate", exc_info=True)
    configure_routes(app)
    start_server(app)


if __name__ == "__main__":
    run()
