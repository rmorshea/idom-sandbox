import os
from sandbox import SandboxView, SandboxServer


if __name__ == "__main__":
    server = SandboxServer(SandboxView)
    server.run(
        "0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        workers=int(os.environ.get("WEB_CONCURRENCY", 1)),
        debug=(os.environ.get("DEBUG") in ("True", "true")),
    )
