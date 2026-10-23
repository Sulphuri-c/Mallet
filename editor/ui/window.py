import customtkinter as ctk
from tkinter import filedialog
import sys
import os
import copy
import time
import uuid

from compiler import MalletCompiler
import server
from core.proxies import load_proxy_icon, get_proxy_definition
from ui.properties_panel import PropertiesPanel
from ui.tooltips import ToolTip
from ui.docs_window import DocsWindow
from ui.preferences import PreferencesWindow, load_config
from ui.viewport2d import Viewport2D
from ui.viewport import Viewport3D

ctk.set_appearance_mode("dark")

THEMES = {
    "Regular": {
        "bg": "#222222", "sidebar": "#4A4A4A", "accent": "#7514ED",
        "text": "#EEEEEE", "line": "#3b3b3b", "subline": "#2a2a2a",
        "origin_x": "#F06767", "origin_y": "#68FF88"
    },
    "Night": {
        "bg": "#000000", "sidebar": "#121212", "accent": "#EEAF5C",
        "text": "#EEEEEE", "line": "#1f1f1f", "subline": "#0a0a0a",
        "origin_x": "#F06767", "origin_y": "#EEAF5C"
    },
    "Calm": {
        "bg": "#383338", "sidebar": "#5c525c", "accent": "#EE7BF0",
        "text": "#FFFFFF", "line": "#4a424a", "subline": "#3f383f",
        "origin_x": "#EE7BF0", "origin_y": "#7EEDED"
    }
}


class MalletWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mallet Engine")
        self.geometry("1440x900")

        self.app_settings = load_config()
        self.current_theme_name = self.app_settings.get("theme", "Regular")

        if self.current_theme_name == "Custom" or self.current_theme_name not in THEMES:
            self.current_theme = THEMES["Regular"].copy()
            custom = self.app_settings.get("custom_colors", {})
            if custom.get("Background"): self.current_theme["bg"] = custom["Background"]
            if custom.get("Sidebar"): self.current_theme["sidebar"] = custom["Sidebar"]
            if custom.get("Accent"): self.current_theme["accent"] = custom["Accent"]
            if custom.get("Grid Lines"): self.current_theme["line"] = custom["Grid Lines"]
        else:
            self.current_theme = THEMES[self.current_theme_name].copy()

        self.configure(fg_color=self.current_theme["bg"])

        self.workspace_brushes = []
        self.workspace_proxies = []
        self.selected_brush = None
        self.transform_mode = "scale"
        self.clipboard_item = None

        self.history_stack = []
        self.redo_stack = []

        self.is_fullscreen = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Control-z>", self.perform_undo)
        self.bind("<Control-y>", self.perform_redo)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        self.top_menu = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color=self.current_theme["sidebar"])
        self.top_menu.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.menu_file = ctk.CTkOptionMenu(self.top_menu, values=["Open...", "Save...", "Exit"], width=60, height=24,
                                           fg_color=self.current_theme["sidebar"],
                                           button_color=self.current_theme["sidebar"],
                                           button_hover_color=self.current_theme["accent"],
                                           text_color=self.current_theme["text"],
                                           dropdown_fg_color=self.current_theme["sidebar"],
                                           dropdown_hover_color=self.current_theme["accent"],
                                           command=self.handle_file_menu)
        self.menu_file.set("File")
        self.menu_file.pack(side="left", padx=2, pady=2)

        self.menu_edit = ctk.CTkOptionMenu(self.top_menu, values=["Preferences..."], width=90, height=24,
                                           fg_color=self.current_theme["sidebar"],
                                           button_color=self.current_theme["sidebar"],
                                           button_hover_color=self.current_theme["accent"],
                                           text_color=self.current_theme["text"],
                                           dropdown_fg_color=self.current_theme["sidebar"],
                                           dropdown_hover_color=self.current_theme["accent"],
                                           command=self.handle_edit_menu)
        self.menu_edit.set("Edit")
        self.menu_edit.pack(side="left", padx=2, pady=2)

        self.menu_map = ctk.CTkOptionMenu(self.top_menu, values=["Docs / Help"], width=60, height=24,
                                          fg_color=self.current_theme["sidebar"],
                                          button_color=self.current_theme["sidebar"],
                                          button_hover_color=self.current_theme["accent"],
                                          text_color=self.current_theme["text"],
                                          dropdown_fg_color=self.current_theme["sidebar"],
                                          dropdown_hover_color=self.current_theme["accent"],
                                          command=self.handle_map_menu)
        self.menu_map.set("Map")
        self.menu_map.pack(side="left", padx=2, pady=2)

        self.btn_compile = ctk.CTkButton(self.top_menu, text="Sync", width=80, height=24,
                                         fg_color=self.current_theme["accent"], hover_color="#500AA6",
                                         text_color=self.current_theme["text"],
                                         command=self.run_compile)
        self.btn_compile.pack(side="left", padx=15, pady=2)

        ToolTip(self.btn_compile, "Push data to Roblox Plugin")

        self.toolbar = ctk.CTkFrame(self, width=45, corner_radius=0, fg_color=self.current_theme["sidebar"])
        self.toolbar.grid(row=1, column=0, sticky="ns")

        self.active_tool = "PTR"
        self.tool_buttons = {}

        self.tools = [
            ("PTR", "tool_pointer.png", "Pointer Tool"),
            ("BLK", "tool_geometry.png", "Geometry Brush"),
            ("PRX", "tool_entity.png", "Proxy Tool"),
            ("MAT", "tool_material.png", "Material Editor"),
            ("DCL", "tool_decal.png", "Overlay/Decal Tool"),
            ("CLP", "tool_clip.png", "Clipping Tool")
        ]

        for code, icon_filename, desc in self.tools:
            icon_img = load_proxy_icon(code.lower() if not icon_filename else icon_filename) if icon_filename else None

            btn_params = {
                "master": self.toolbar,
                "width": 38,
                "height": 38,
                "corner_radius": 4,
                "fg_color": self.current_theme["bg"],
                "hover_color": self.current_theme["accent"],
                "command": lambda c=code: self.select_tool(c)
            }

            if icon_img:
                btn_params["image"] = icon_img
                btn_params["text"] = ""
            else:
                btn_params["text"] = code
                btn_params["text_color"] = self.current_theme["text"]
                btn_params["font"] = ctk.CTkFont(weight="bold", size=11)

            btn = ctk.CTkButton(**btn_params)
            btn.pack(pady=4, padx=4)
            ToolTip(btn, desc)
            self.tool_buttons[code] = btn

        self.highlight_active_tool()

        self.viewport_container = ctk.CTkFrame(self, corner_radius=0, fg_color=self.current_theme["bg"])
        self.viewport_container.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)

        self.viewport_container.grid_rowconfigure((0, 1), weight=1)
        self.viewport_container.grid_columnconfigure((0, 1), weight=1)

        self.viewports = []
        self.viewport_labels = []
        self.view_top = self.create_viewport(self.viewport_container, "2D Top", 0, 0)
        self.view_front = self.create_viewport(self.viewport_container, "2D Front", 0, 1)
        self.view_side = self.create_viewport(self.viewport_container, "2D Side", 1, 0)
        self.view_map = self.create_viewport(self.viewport_container, "Map Setup & Overview", 1, 1, is_3d=True)

        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="transparent")
        self.sidebar_frame.grid(row=1, column=2, sticky="ns")
        self.sidebar_frame.grid_propagate(False)

        self.properties_panel = PropertiesPanel(self.sidebar_frame, on_apply_callback=self.apply_brush_properties)
        self.properties_panel.pack(fill="both", expand=True)
        self.properties_panel.pack_forget()

        self.bind("<Alt-Return>", self.toggle_properties)

        self.status_bar = ctk.CTkFrame(self, height=24, corner_radius=0, fg_color=self.current_theme["sidebar"])
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky="ew")

        self.status_text = ctk.CTkLabel(self.status_bar, text=" Active Tool: PTR  |  Grid: 1  |  Snap: On",
                                        text_color=self.current_theme["text"], font=ctk.CTkFont(size=12))
        self.status_text.pack(side="left", padx=10)

    def save_history_state(self):
        state = {
            "brushes": copy.deepcopy(self.workspace_brushes),
            "proxies": copy.deepcopy(self.workspace_proxies)
        }
        self.history_stack.append(state)
        self.redo_stack.clear()
        if len(self.history_stack) > 30:
            self.history_stack.pop(0)

    def perform_undo(self, event=None):
        if not self.history_stack:
            return
        current_state = {
            "brushes": copy.deepcopy(self.workspace_brushes),
            "proxies": copy.deepcopy(self.workspace_proxies)
        }
        self.redo_stack.append(current_state)
        prev_state = self.history_stack.pop()
        self.workspace_brushes = prev_state["brushes"]
        self.workspace_proxies = prev_state["proxies"]
        self.selected_brush = None
        self.properties_panel.pack_forget()
        for vp in self.viewports:
            vp.draw_grid()

    def perform_redo(self, event=None):
        if not self.redo_stack:
            return
        current_state = {
            "brushes": copy.deepcopy(self.workspace_brushes),
            "proxies": copy.deepcopy(self.workspace_proxies)
        }
        self.history_stack.append(current_state)
        next_state = self.redo_stack.pop()
        self.workspace_brushes = next_state["brushes"]
        self.workspace_proxies = next_state["proxies"]
        self.selected_brush = None
        self.properties_panel.pack_forget()
        for vp in self.viewports:
            vp.draw_grid()

    def select_tool(self, tool_code):
        self.active_tool = tool_code
        self.highlight_active_tool()
        self.status_text.configure(text=f" Active Tool: {tool_code}  |  Grid: 1  |  Snap: On")

    def highlight_active_tool(self):
        for code, btn in self.tool_buttons.items():
            if code == self.active_tool:
                btn.configure(fg_color=self.current_theme["accent"])
            else:
                btn.configure(fg_color=self.current_theme["bg"])

    def create_viewport(self, parent, title, row, col, is_3d=False):
        frame = ctk.CTkFrame(parent, corner_radius=0, fg_color=self.current_theme["sidebar"], border_width=2,
                             border_color=self.current_theme["bg"])
        frame.grid(row=row, column=col, sticky="nsew")

        lbl_color = self.current_theme["accent"] if is_3d else self.current_theme["text"]
        lbl = ctk.CTkLabel(frame, text=title, text_color=lbl_color, font=ctk.CTkFont(size=12, weight="bold"))
        lbl.pack(anchor="nw", padx=6, pady=2)
        self.viewport_labels.append((lbl, is_3d))

        if not is_3d:
            canvas = Viewport2D(frame, view_type=title.lower(), theme_colors=self.current_theme,
                                on_hover_callback=self.update_status_grid)
            canvas.pack(fill="both", expand=True, padx=2, pady=(0, 2))
            self.viewports.append(canvas)
        else:
            canvas = Viewport3D(frame, theme_colors=self.current_theme)
            canvas.pack(fill="both", expand=True, padx=2, pady=(0, 2))
            self.viewports.append(canvas)

        return frame

    def update_status_grid(self, grid_size, view_name):
        self.status_text.configure(
            text=f" Active Tool: {self.active_tool}  |  View: {view_name.capitalize()}  |  Grid: {grid_size}  |  Snap: On")

    def handle_file_menu(self, choice):
        self.menu_file.set("File")
        if choice == "Open...":
            self.open_file()
        elif choice == "Save...":
            self.save_file()
        elif choice == "Exit":
            self.quit()

    def handle_edit_menu(self, choice):
        self.menu_edit.set("Edit")
        if choice == "Preferences...":
            PreferencesWindow(self, self.app_settings, self.apply_preferences)

    def apply_preferences(self, new_settings):
        self.app_settings = new_settings
        self.current_theme_name = new_settings["theme"]

        if self.current_theme_name in THEMES:
            self.current_theme = THEMES[self.current_theme_name].copy()
        else:
            self.current_theme = THEMES["Regular"].copy()

        custom = new_settings.get("custom_colors", {})
        if custom.get("Background"):
            self.current_theme["bg"] = custom["Background"]
        if custom.get("Sidebar"):
            self.current_theme["sidebar"] = custom["Sidebar"]
        if custom.get("Accent"):
            self.current_theme["accent"] = custom["Accent"]
        if custom.get("Grid Lines"):
            self.current_theme["line"] = custom["Grid Lines"]

        self.apply_theme()

    def apply_theme(self):
        self.configure(fg_color=self.current_theme["bg"])
        self.top_menu.configure(fg_color=self.current_theme["sidebar"])
        self.toolbar.configure(fg_color=self.current_theme["sidebar"])
        self.status_bar.configure(fg_color=self.current_theme["sidebar"])
        self.viewport_container.configure(fg_color=self.current_theme["bg"])

        self.btn_compile.configure(fg_color=self.current_theme["accent"], text_color=self.current_theme["text"])
        self.status_text.configure(text_color=self.current_theme["text"])

        for lbl, is_3d in self.viewport_labels:
            lbl_color = self.current_theme["accent"] if is_3d else self.current_theme["text"]
            lbl.configure(text_color=lbl_color)

        self.highlight_active_tool()

        for vp in self.viewports:
            vp.update_theme(self.current_theme)

    def handle_map_menu(self, choice):
        self.menu_map.set("Map")
        if choice == "Docs / Help":
            DocsWindow(self)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def toggle_properties(self, event=None):
        if self.selected_brush:
            if self.properties_panel.winfo_ismapped():
                self.properties_panel.pack_forget()
            else:
                self.properties_panel.pack(fill="both", expand=True)

    def select_brush(self, brush):
        self.selected_brush = brush
        if brush:
            self.properties_panel.pack(fill="both", expand=True)
            self.properties_panel.load_target(brush)
        else:
            self.properties_panel.pack_forget()

        for vp in self.viewports:
            vp.draw_grid()

    def apply_brush_properties(self, updated_data):
        if self.selected_brush:

            self.selected_brush["parent"] = updated_data["parent"]
            self.selected_brush["attributes"] = updated_data["attributes"]
            self.selected_brush["type"] = updated_data["type"]
            self.selected_brush["uuid"] = ensure_class_uuid(self.selected_brush.get("uuid"), updated_data["type"])
            self.selected_brush["io"] = updated_data.get("io", [])

            self.save_history_state()
            self.selected_brush["type"] = updated_data["type"]
            self.selected_brush["mallet_id"] = updated_data.get("mallet_id", updated_data.get("name", ""))
            self.selected_brush["name"] = self.selected_brush["mallet_id"]
            self.selected_brush["parent"] = updated_data["parent"]
            self.selected_brush["attributes"] = updated_data["attributes"]

            if self.selected_brush["type"] == "geom_static":
                self.selected_brush["mallet_id"] = ""
                self.selected_brush["name"] = ""
            elif "mallet_id" in self.selected_brush["attributes"]:
                self.selected_brush["mallet_id"] = self.selected_brush["attributes"]["mallet_id"]
                self.selected_brush["name"] = self.selected_brush["mallet_id"]

            if "material" in updated_data["attributes"]:
                self.selected_brush["material"] = updated_data["attributes"]["material"]

            self.status_text.configure(
                text=f" Active Tool: {self.active_tool}  |  UUID: {self.selected_brush.get('uuid')[:8]}...  |  mallet_id: '{self.selected_brush.get('mallet_id')}'")
            for vp in self.viewports:
                vp.draw_grid()

    def add_workspace_brush(self, geom_type, pos, size):
        "uuid": generate_element_uuid(geom_type),
        self.save_history_state()
        default_def = get_proxy_definition(geom_type)
        default_attrs = copy.deepcopy(default_def.get("attributes", {}))
        for k, v in default_attrs.items():
            default_attrs[k] = v.get("default", "")

        brush_data = {
            "uuid": str(uuid.uuid4()),
            "mallet_id": "",
            "type": geom_type,
            "name": "",
            "parent": "workspace",
            "pos": pos,
            "size": size,
            "rot": [0.0, 0.0, 0.0],
            "material": default_attrs.get("material", "SmoothPlastic"),
            "attributes": default_attrs,
            "io": []
        }
        self.workspace_brushes.append(brush_data)
        for vp in self.viewports:
            vp.draw_grid()

    def add_workspace_proxy(self, proxy_type, pos):
        "uuid": generate_element_uuid(geom_type),
        current_time = time.time()
        if hasattr(self, "_last_proxy_spawn") and current_time - self._last_proxy_spawn < 0.15:
            return
        self._last_proxy_spawn = current_time

        self.save_history_state()
        default_def = get_proxy_definition(proxy_type)
        default_attrs = copy.deepcopy(default_def.get("attributes", {}))
        for k, v in default_attrs.items():
            default_attrs[k] = v.get("default", "")

        proxy_data = {
            "uuid": str(uuid.uuid4()),
            "mallet_id": "",
            "type": proxy_type,
            "name": "",
            "parent": "workspace",
            "pos": pos,
            "size": default_def.get("default_size", [2.0, 2.0, 2.0]),
            "rot": [0.0, 0.0, 0.0],
            "attributes": default_attrs,
            "io": []
        }
        self.workspace_proxies.append(proxy_data)
        for vp in self.viewports:
            vp.draw_grid()

    def open_file(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".micheal",
            filetypes=[
                ("Mallet Map File (.micheal)", "*.micheal"),
                ("All Files", "*.*")
            ]
        )
        if filepath:
            compiler = MalletCompiler()
            geom, proxies = compiler.import_micheal_file(filepath)
            self.save_history_state()
            self.workspace_brushes = copy.deepcopy(geom)
            self.workspace_proxies = copy.deepcopy(proxies)
            self.selected_brush = None
            self.properties_panel.pack_forget()
            for vp in self.viewports:
                vp.draw_grid()
            self.status_text.configure(
                text=f" Opened: {os.path.basename(filepath)} ({len(geom)} geometry, {len(proxies)} proxies)")

    def save_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".micheal",
            filetypes=[
                ("Mallet Map File (.micheal)", "*.micheal"),
                ("All Files", "*.*")
            ]
        )
        if filepath:
            compiler = MalletCompiler()
            for geom in self.workspace_brushes:
                compiler.add_element(
                    geom.get("uuid"), geom.get("mallet_id", ""),
                    geom["type"], "geometry",
                    geom["pos"], geom["size"],
                    geom.get("rot", [0.0, 0.0, 0.0]),
                    geom.get("material", "SmoothPlastic"),
                    copy.deepcopy(geom.get("attributes", {})),
                    copy.deepcopy(geom.get("io", []))
                )
            for proxy in getattr(self, "workspace_proxies", []):
                compiler.add_element(
                    proxy.get("uuid"), proxy.get("mallet_id", ""),
                    proxy["type"], "proxy",
                    proxy["pos"], proxy["size"],
                    proxy.get("rot", [0.0, 0.0, 0.0]),
                    "Plastic",
                    copy.deepcopy(proxy.get("attributes", {})),
                    copy.deepcopy(proxy.get("io", []))
                )
            compiler.export_micheal_file(filepath)
            self.status_text.configure(text=f" Saved project to {os.path.basename(filepath)}")

    def run_compile(self):
        compiler = MalletCompiler()
        for geom in self.workspace_brushes:
            compiler.add_element(
                geom.get("uuid"), geom.get("mallet_id", ""),
                geom["type"], "geometry",
                geom["pos"], geom["size"],
                geom.get("rot", [0.0, 0.0, 0.0]),
                geom.get("material", "SmoothPlastic"),
                copy.deepcopy(geom.get("attributes", {})),
                copy.deepcopy(geom.get("io", []))
            )
        for proxy in getattr(self, "workspace_proxies", []):
            compiler.add_element(
                proxy.get("uuid"), proxy.get("mallet_id", ""),
                proxy["type"], "proxy",
                proxy["pos"], proxy["size"],
                proxy.get("rot", [0.0, 0.0, 0.0]),
                "Plastic",
                copy.deepcopy(proxy.get("attributes", {})),
                copy.deepcopy(proxy.get("io", []))
            )

        json_data = compiler.get_json_string()
        server.update_payload(json_data)
        self.status_text.configure(
            text=f" Active Tool: {self.active_tool}  |  Synced {len(self.workspace_brushes)} geometry, {len(getattr(self, 'workspace_proxies', []))} proxies")


if __name__ == "__main__":
    app = MalletWindow()
    app.mainloop()