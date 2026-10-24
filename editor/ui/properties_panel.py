import customtkinter as ctk
from tkinter import filedialog
from core.proxies import get_all_proxy_types, get_proxy_definition, get_proxy_types_by_category

ROBLOX_MATERIALS = [
    "Air", "Asphalt", "Basalt", "Brick", "Cardboard", "Carpet", "CeramicTiles",
    "ClayRoofTiles", "Cobblestone", "Concrete", "CorrodedMetal", "CrackedLava",
    "DiamondPlate", "Fabric", "Foil", "ForceField", "Glacier", "Glass", "Granite",
    "Grass", "Ground", "Ice", "LeafyGrass", "Leather", "Limestone", "Marble", "Metal",
    "Mud", "Neon", "Pavement", "Pebble", "Plaster", "Plastic", "Rock", "RoofShingles",
    "Rubber", "Salt", "Sand", "Sandstone", "Slate", "SmoothPlastic", "Snow", "Water",
    "Wood", "WoodPlanks"
]


class FilepathEntry(ctk.CTkFrame):
    def __init__(self, master, default_val="", attr_key="", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.attr_key = attr_key

        self.entry = ctk.CTkEntry(
            self,
            fg_color="#222222",
            border_color="#7F7F7F",
            text_color="#EEEEEE"
        )
        self.entry.insert(0, default_val)
        self.entry.pack(side="left", fill="x", expand=True)

        self.browse_btn = ctk.CTkButton(
            self,
            text="...",
            width=28,
            fg_color="#4A4A4A",
            hover_color="#7514ED",
            text_color="#EEEEEE",
            command=self.browse_file
        )
        self.browse_btn.pack(side="right", padx=(4, 0))

    def browse_file(self):
        if "sound" in self.attr_key:
            filetypes = [("Audio Files", "*.ogg *.mp3 *.wav"), ("All Files", "*.*")]
        else:
            filetypes = [
                ("3D Mesh Files (.fbx, .obj)", "*.fbx *.obj"),
                ("FBX Files", "*.fbx"),
                ("OBJ Files", "*.obj"),
                ("All Files", "*.*")
            ]

        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.entry.delete(0, "end")
            self.entry.insert(0, path)

    def get(self):
        return self.entry.get().strip()

    def set(self, val):
        self.entry.delete(0, "end")
        self.entry.insert(0, val)


class AutocompleteComboBox(ctk.CTkFrame):
    def __init__(self, master, options, default_val="", on_select_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.options = options
        self.on_select_callback = on_select_callback
        self.closest_match = None

        self.combobox = ctk.CTkComboBox(
            self,
            values=self.options,
            fg_color="#222222",
            border_color="#7F7F7F",
            text_color="#EEEEEE",
            dropdown_fg_color="#4A4A4A",
            dropdown_hover_color="#7514ED",
            command=self.on_dropdown_picked
        )
        self.combobox.set(default_val)
        self.combobox.pack(fill="x", expand=True)

        self.hint_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#AE79F0",
            anchor="w",
            height=14
        )

        self.combobox._entry.bind("<KeyRelease>", self.on_key_release)
        self.combobox._entry.bind("<Tab>", self.on_tab_complete)
        self.combobox._entry.bind("<Return>", self.on_enter_pressed)

    def on_key_release(self, event):
        if event.keysym in ("Tab", "Return", "Up", "Down", "Left", "Right", "Shift_L", "Shift_R", "space"):
            return

        typed = self.combobox.get().strip().lower()
        if not typed:
            self.closest_match = None
            self.hint_label.pack_forget()
            self.combobox.configure(values=self.options)
            return

        starts = [opt for opt in self.options if opt.lower().startswith(typed)]
        contains = [opt for opt in self.options if typed in opt.lower() and opt not in starts]
        matches = starts + contains

        if matches:
            self.closest_match = matches[0]
            self.combobox.configure(values=matches)
            if self.closest_match.lower() != typed:
                self.hint_label.configure(text=f"Tab -> {self.closest_match}")
                self.hint_label.pack(fill="x", pady=(2, 0))
            else:
                self.hint_label.pack_forget()
                if self.on_select_callback:
                    self.on_select_callback(self.closest_match)
        else:
            self.closest_match = None
            self.hint_label.configure(text="No matching enumerator")
            self.hint_label.pack(fill="x", pady=(2, 0))

    def on_tab_complete(self, event):
        if self.closest_match:
            self.combobox.set(self.closest_match)
            self.combobox._entry.icursor("end")
            self.hint_label.pack_forget()
            if self.on_select_callback:
                self.on_select_callback(self.closest_match)
            return "break"

    def on_enter_pressed(self, event):
        current = self.combobox.get().strip()
        if current in self.options and self.on_select_callback:
            self.hint_label.pack_forget()
            self.on_select_callback(current)

    def on_dropdown_picked(self, choice):
        self.closest_match = choice
        self.hint_label.pack_forget()
        if self.on_select_callback:
            self.on_select_callback(choice)

    def get(self):
        return self.combobox.get().strip()

    def set(self, val):
        self.combobox.set(val)
        self.hint_label.pack_forget()

    def set_options(self, new_options):
        self.options = new_options
        self.combobox.configure(values=new_options)


class PropertiesPanel(ctk.CTkFrame):
    def __init__(self, master, on_apply_callback=None, **kwargs):
        super().__init__(master, fg_color="#4A4A4A", width=300, corner_radius=0, **kwargs)
        self.grid_propagate(False)
        self.on_apply_callback = on_apply_callback
        self.attribute_widgets = {}
        self.current_target = None
        self.pending_io = []

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(15, 10), padx=10)

        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="Proxy Properties",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#AE79F0"
        )
        self.header_label.pack(side="left")

        self.close_btn = ctk.CTkButton(
            self.header_frame,
            text="X",
            width=24,
            height=24,
            fg_color="#222222",
            hover_color="#7C0000",
            text_color="#EEEEEE",
            command=self.hide_panel
        )
        self.close_btn.pack(side="right")

        self.parent_entry = self.create_property_row("Parent:", "workspace")

        class_row = ctk.CTkFrame(self, fg_color="transparent")
        class_row.pack(fill="x", padx=10, pady=2)
        class_lbl = ctk.CTkLabel(class_row, text="Class:", width=100, anchor="nw", text_color="#EEEEEE")
        class_lbl.pack(side="left", pady=4)

        self.class_selector = AutocompleteComboBox(
            class_row,
            options=get_all_proxy_types(),
            default_val="geom_dynamic",
            on_select_callback=self.on_class_changed
        )
        self.class_selector.pack(side="right", fill="x", expand=True)

        self.divider = ctk.CTkFrame(self, height=2, fg_color="#222222")
        self.divider.pack(fill="x", padx=10, pady=10)

        self.attributes_label = ctk.CTkLabel(
            self,
            text="KeyValues / Attributes",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#EEEEEE"
        )
        self.attributes_label.pack(pady=(0, 5), padx=10, anchor="w")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#222222", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.io_btn = ctk.CTkButton(
            self,
            text="Edit I/O Connections (0)",
            fg_color="#222222",
            text_color="#EEEEEE",
            hover_color="#7514ED",
            command=self.open_io_window
        )
        self.io_btn.pack(pady=(0, 5), padx=10, fill="x")

        self.apply_btn = ctk.CTkButton(
            self,
            text="Apply Changes",
            fg_color="#7514ED",
            text_color="#EEEEEE",
            hover_color="#500AA6",
            font=ctk.CTkFont(weight="bold"),
            command=self.apply_changes
        )
        self.apply_btn.pack(pady=(0, 10), padx=10, fill="x")

        self.rebuild_attributes_for_class("geom_dynamic", {})

    def hide_panel(self):
        self.pack_forget()

    def create_property_row(self, label_text, default_val):
        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=2)

        lbl = ctk.CTkLabel(row_frame, text=label_text, width=100, anchor="w", text_color="#EEEEEE")
        lbl.pack(side="left")

        entry = ctk.CTkEntry(row_frame, fg_color="#222222", border_color="#7F7F7F", text_color="#EEEEEE")
        entry.insert(0, default_val)
        entry.pack(side="right", fill="x", expand=True)
        return entry

    def clear_attribute_rows(self):
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self.attribute_widgets.clear()

    def rebuild_attributes_for_class(self, class_name, existing_values=None):
        self.clear_attribute_rows()
        existing_values = existing_values or {}
        definition = get_proxy_definition(class_name)
        schema = definition.get("attributes", {})

        for attr_key, attr_meta in schema.items():
            attr_type = attr_meta.get("type", "string")
            default_val = str(existing_values.get(attr_key, attr_meta.get("default", "")))

            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=3)

            key_lbl = ctk.CTkLabel(
                row_frame,
                text=attr_key,
                width=95,
                anchor="w",
                fg_color="#4A4A4A",
                text_color="#EEEEEE",
                corner_radius=3,
                padx=6
            )
            key_lbl.pack(side="left", padx=(0, 5))

            if attr_type == "material":
                widget = AutocompleteComboBox(
                    row_frame,
                    options=ROBLOX_MATERIALS,
                    default_val=default_val
                )
                widget.pack(side="right", fill="x", expand=True)
            elif attr_type == "bool":
                widget = AutocompleteComboBox(
                    row_frame,
                    options=["true", "false"],
                    default_val=default_val
                )
                widget.pack(side="right", fill="x", expand=True)
            elif attr_type == "filepath" or attr_key.endswith("_filepath"):
                widget = FilepathEntry(
                    row_frame,
                    default_val=default_val,
                    attr_key=attr_key
                )
                widget.pack(side="right", fill="x", expand=True)
            else:
                widget = ctk.CTkEntry(
                    row_frame,
                    fg_color="#222222",
                    border_color="#7F7F7F",
                    text_color="#EEEEEE"
                )
                widget.insert(0, default_val)
                widget.pack(side="right", fill="x", expand=True)

            self.attribute_widgets[attr_key] = widget

        if class_name in ("geom_static", "msh_static", "msh_id_static") or "mallet_id" not in schema:
            self.io_btn.configure(state="disabled", text="I/O Disabled (Static)")
        else:
            self.io_btn.configure(state="normal", text=f"Edit I/O Connections ({len(self.pending_io)})")

    def on_class_changed(self, new_class_name):
        existing_attrs = {}
        if self.current_target:
            existing_attrs = self.current_target.get("attributes", {}).copy()
            if "material" in self.current_target:
                existing_attrs["material"] = self.current_target["material"]
        self.rebuild_attributes_for_class(new_class_name, existing_attrs)

    def open_io_window(self):
        if not self.current_target:
            return
        from ui.io_window import IOWindow
        temp_target = self.current_target.copy()
        temp_target["io"] = self.pending_io
        if "mallet_id" in self.attribute_widgets:
            temp_target["mallet_id"] = self.attribute_widgets["mallet_id"].get()
        IOWindow(self.winfo_toplevel(), temp_target, self.on_io_saved)

    def on_io_saved(self, updated_io):
        self.pending_io = updated_io
        self.io_btn.configure(text=f"Edit I/O Connections ({len(self.pending_io)})")
        self.apply_changes()

    def load_target(self, target_dict):
        self.current_target = target_dict
        if not target_dict:
            return

        self.pending_io = list(target_dict.get("io", []))
        class_name = target_dict.get("type", "geom_dynamic")

        if class_name.startswith("geom_"):
            allowed_classes = get_proxy_types_by_category("geometry")
        else:
            allowed_classes = get_proxy_types_by_category("proxy")

        self.class_selector.set_options(allowed_classes)
        self.class_selector.set(class_name)

        self.parent_entry.delete(0, "end")
        self.parent_entry.insert(0, target_dict.get("parent", "workspace"))

        existing_attrs = target_dict.get("attributes", {}).copy()
        if "material" in target_dict and "material" not in existing_attrs:
            existing_attrs["material"] = target_dict["material"]
        if target_dict.get("mallet_id") and not existing_attrs.get("mallet_id"):
            existing_attrs["mallet_id"] = target_dict["mallet_id"]

        self.rebuild_attributes_for_class(class_name, existing_attrs)

    def get_updated_data(self):
        attrs = {}
        for k, widget in self.attribute_widgets.items():
            attrs[k] = widget.get()

        mallet_id = attrs.get("mallet_id", "").strip()

        return {
            "type": self.class_selector.get(),
            "mallet_id": mallet_id,
            "name": mallet_id,
            "parent": self.parent_entry.get().strip(),
            "attributes": attrs,
            "io": self.pending_io
        }

    def apply_changes(self):
        if self.on_apply_callback:
            self.on_apply_callback(self.get_updated_data())