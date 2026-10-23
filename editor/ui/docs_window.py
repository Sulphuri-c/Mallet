import customtkinter as ctk
from typing import Any


class DocsWindow(ctk.CTkToplevel):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.title("Mallet Engine - Documentation")
        self.geometry("450x350")
        self.configure(fg_color="#222222")

        if args:
            self.transient(args[0])
        self.lift()
        self.focus_force()

        self.header = ctk.CTkLabel(self, text="Controls & Shortcuts", font=ctk.CTkFont(size=18, weight="bold"),
                                   text_color="#AE79F0")
        self.header.pack(pady=10)

        self.textbox = ctk.CTkTextbox(self, fg_color="#4A4A4A", text_color="#EEEEEE")
        self.textbox.pack(fill="both", expand=True, padx=10, pady=10)

        docs_text = """
Navigation & Viewports:
- Right Click + Drag: Pan Viewport

- C: Center view on origin (hover viewport)

- [ / ]: Decrease / Increase Grid Size

- Alt + Enter: Toggle Proxy Properties

- F11: Toggle Fullscreen


Tools:
- PTR: Select objects

- BLK: Make geometry

- PRX: Make a proxy

- MAT: Material Editor

- DCL: Create an overlay

- CLP: Clipping Tool

        """
        self.textbox.insert("0.0", docs_text)
        self.textbox.configure(state="disabled")