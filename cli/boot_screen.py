import time


class BootScreen:
    def __init__(self):
        self.title = "AXON OS"
        self.subtitle = "AI-Native Operating Layer"
        self.version = "Developer Preview 0.1"
        self.credit = "Developed by Abdullah Ali"

    def render(self, fast=False):
        lines = [
            "",
            "╔══════════════════════════════════════════════════════════════╗",
            "║                                                              ║",
            "║                         AXON OS                              ║",
            "║                                                              ║",
            "║              AI-Native Operating Layer                       ║",
            "║                                                              ║",
            "║                 Developer Preview 0.1                        ║",
            "║                                                              ║",
            "║        Initializing secure AI runtime environment...          ║",
            "║                                                              ║",
            "║                 Developed by Abdullah Ali                    ║",
            "║                                                              ║",
            "╚══════════════════════════════════════════════════════════════╝",
            ""
        ]

        for line in lines:
            print(line)
            if not fast:
                time.sleep(0.03)

        self._progress_bar(fast=fast)

    def _progress_bar(self, fast=False):
        steps = [
            ("Runtime Environment", "ready"),
            ("Safety Layer", "enabled"),
            ("Reports", "enabled"),
            ("VM/GPU Policy", "checked"),
            ("AXON Core", "ready")
        ]

        for label, status in steps:
            print(f"[AXON] {label}: {status}")
            if not fast:
                time.sleep(0.08)

        print("")
        print("AXON Runtime Ready.")
        print("")
