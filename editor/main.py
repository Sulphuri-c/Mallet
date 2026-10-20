import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.window import MalletWindow
import server


def run_server():
    server.start()


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    app = MalletWindow()
    app.mainloop()