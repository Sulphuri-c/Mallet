import customtkinter as ctk


class DocsWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Mallet Engine - Documentation")
        self.geometry("480x420")
        self.configure(fg_color="#222222")

        self.transient(args[0])
        self.lift()
        self.focus_force()

        self.header = ctk.CTkLabel(self, text="Controls & Shortcuts", font=ctk.CTkFont(size=18, weight="bold"),
                                   text_color="#AE79F0")
        self.header.pack(pady=10)

        self.textbox = ctk.CTkTextbox(self, fg_color="#4A4A4A", text_color="#EEEEEE")
        self.textbox.pack(fill="both", expand=True, padx=10, pady=10)

        docs_text = """Navigation & Viewports:
- Right Click + Drag: Pan Viewport
- Scroll Wheel: Zoom In / Out
- C: Center view on origin (hover viewport)
- [ / ]: Decrease / Increase Grid Size
- F11: Toggle Fullscreen

Selection & Editing:
- Left Click (on already-selected Geometry/Mesh): Toggle Scale / Rotate handles
- Right Click (in PTR mode): Cut / Copy / Duplicate / Paste / Delete menu
- Delete / BackSpace: Delete selected Geometry or Proxy
- Ctrl + Z / Ctrl + Y: Undo / Redo
- Alt + Enter: Toggle Proxy Properties Panel
- Tab (in Properties / I/O Dropdowns): Autocomplete closest match

Visual I/O & Payloads:
- Show Visual I/O Connections: Draws visual I/O connections, showing broken connections in red.

Tools:
- PTR: Select, Move, Scale, and Rotate objects

- BLK: Drag to create Geometry

- PRX: Click to spawn a Proxy

- MAT: Material Editor

- DCL: Create an overlay

- CLP: Clipping Tool
"""
        self.textbox.insert("0.0", docs_text)
        self.textbox.configure(state="disabled")