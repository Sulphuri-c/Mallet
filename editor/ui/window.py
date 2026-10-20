import customtkinter as ctk
from tkinter import filedialog
import sys
import os

from compiler import MalletCompiler
import server
from ui.properties_panel import PropertiesPanel

ctk.set_appearance_mode("dark")


class MalletWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mallet Engine")
        self.geometry("1440x900")
        self.configure(fg_color="#222222")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.top_menu = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color="#4A4A4A")
        self.top_menu.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.btn_file = ctk.CTkButton(self.top_menu, text="File (Save)", width=80, height=24, fg_color="transparent",
                                      hover_color="#7514ED", text_color="#EEEEEE", command=self.save_project)
        self.btn_file.pack(side="left", padx=2, pady=2)

        self.btn_edit = ctk.CTkButton(self.top_menu, text="Edit", width=50, height=24, fg_color="transparent",
                                      hover_color="#7514ED", text_color="#EEEEEE")
        self.btn_edit.pack(side="left", padx=2, pady=2)

        self.btn_map = ctk.CTkButton(self.top_menu, text="Map", width=50, height=24, fg_color="transparent",
                                     hover_color="#7514ED", text_color="#EEEEEE")
        self.btn_map.pack(side="left", padx=2, pady=2)

        self.btn_compile = ctk.CTkButton(self.top_menu, text="Compile .micheal", width=120, height=24,
                                         fg_color="#7514ED", hover_color="#500AA6", text_color="#EEEEEE",
                                         command=self.run_compile)
        self.btn_compile.pack(side="left", padx=15, pady=2)

        self.toolbar = ctk.CTkFrame(self, width=45, corner_radius=0, fg_color="#4A4A4A")
        self.toolbar.grid(row=1, column=0, sticky="ns")

        self.tools = ["PTR", "BLK", "ENT", "MAT", "DCL", "CLP"]
        for t in self.tools:
            btn = ctk.CTkButton(self.toolbar, text=t, width=35, height=35, corner_radius=4, fg_color="#222222",
                                hover_color="#7514ED", text_color="#AE79F0", font=ctk.CTkFont(weight="bold", size=11))
            btn.pack(pady=4, padx=5)

        self.viewport_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#222222")
        self.viewport_container.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)

        self.viewport_container.grid_rowconfigure((0, 1), weight=1)
        self.viewport_container.grid_columnconfigure((0, 1), weight=1)

        self.view_top = self.create_viewport(self.viewport_container, "2D Top", 0, 0)
        self.view_front = self.create_viewport(self.viewport_container, "2D Front", 0, 1)
        self.view_side = self.create_viewport(self.viewport_container, "2D Side", 1, 0)
        self.view_3d = self.create_viewport(self.viewport_container, "3D Textured", 1, 1, is_3d=True)

        self.properties_panel = PropertiesPanel(self)
        self.properties_panel.grid(row=1, column=2, sticky="ns")
        self.properties_panel.grid_remove()

        self.bind("<Alt-Return>", self.toggle_properties)

        self.status_bar = ctk.CTkFrame(self, height=24, corner_radius=0, fg_color="#4A4A4A")
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky="ew")

        self.status_text = ctk.CTkLabel(self.status_bar, text=" Grid: 16  |  Snap: On  |  Selected: None",
                                        text_color="#EEEEEE", font=ctk.CTkFont(size=12))
                                        #my ears when im in a quiet room for too long be like:
        self.status_text.pack(side="left", padx=10)

    def create_viewport(self, parent, title, row, col, is_3d=False):
        frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="#4A4A4A", border_width=2, border_color="#222222")
        frame.grid(row=row, column=col, sticky="nsew")

        lbl_color = "#AE79F0" if is_3d else "#7F7F7F"
        lbl = ctk.CTkLabel(frame, text=title, text_color=lbl_color, font=ctk.CTkFont(size=12, weight="bold"))
        lbl.pack(anchor="nw", padx=6, pady=2)

        canvas = ctk.CTkFrame(frame, corner_radius=0, fg_color="#222222")
        canvas.pack(fill="both", expand=True, padx=2, pady=(0, 2))

        return frame

    def toggle_properties(self, event=None):
        if self.properties_panel.winfo_viewable():
            self.properties_panel.grid_remove()
        else:
            self.properties_panel.grid()

    def save_project(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".micheal",
            filetypes=[("Micheal Map Files", "*.micheal"), ("All Files", "*.*")]
        )
        if file_path:
            compiler = MalletCompiler()
            compiler.add_proxy("geometry", "geom_static", [0, 5, 0], [4, 1, 4], "Concrete")
            compiler.export_micheal_file(file_path)
            self.status_text.configure(text=f" Saved project to {file_path}")

    def run_compile(self):
        compiler = MalletCompiler()
        compiler.add_proxy("geometry", "geom_static", [0, 5, 0], [4, 1, 4], "Concrete")
        compiler.add_proxy("geometry", "geom_static", [10, 5, 0], [4, 4, 4], "Wood")

        json_data = compiler.get_json_string()
        server.update_payload(json_data)

        self.status_text.configure(text=" Grid: 16  |  Snap: On  |  Status: Compiled to localhost:8000")


if __name__ == "__main__":
    app = MalletWindow()
    app.mainloop()


if __name__ == "__main__":
    app = MalletWindow()
    app.mainloop()