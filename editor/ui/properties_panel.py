import customtkinter as ctk

ROBLOX_MATERIALS = [
    "Air", "Asphalt", "Basalt", "Brick", "Cardboard", "Carpet", "CeramicTiles",
    "ClayRoofTiles", "Cobblestone", "Concrete", "CorrodedMetal", "CrackedLava",
    "DiamondPlate", "Fabric", "Foil", "ForceField", "Glacier", "Glass", "Granite",
    "Grass", "Ground", "Ice", "LeafyGrass", "Leather", "Limestone", "Marble", "Metal",
    "Mud", "Neon", "Pavement", "Pebble", "Plaster", "Plastic", "Rock", "RoofShingles",
    "Rubber", "Salt", "Sand", "Sandstone", "Slate", "SmoothPlastic", "Snow", "Water",
    "Wood", "WoodPlanks"
]


class PropertiesPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#4A4A4A", width=300, corner_radius=0, **kwargs)
        self.grid_propagate(False)

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(15, 10), padx=10)

        self.header_label = ctk.CTkLabel(self.header_frame, text="Proxy Properties",
                                         font=ctk.CTkFont(size=18, weight="bold"), text_color="#AE79F0")
        self.header_label.pack(side="left")

        self.close_btn = ctk.CTkButton(self.header_frame, text="X", width=24, height=24, fg_color="#222222",
                                       hover_color="#7C0000", text_color="#EEEEEE", command=self.hide_panel)
        self.close_btn.pack(side="right")

        self.target_name_entry = self.create_property_row("Name (Target):", "unnamed_entity")
        self.parent_entry = self.create_property_row("Parent:", "workspace")
        self.class_entry = self.create_property_row("Class:", "geom_static")

        self.divider = ctk.CTkFrame(self, height=2, fg_color="#222222")
        self.divider.pack(fill="x", padx=10, pady=10)

        self.attributes_label = ctk.CTkLabel(self, text="KeyValues / Attributes",
                                             font=ctk.CTkFont(size=14, weight="bold"), text_color="#EEEEEE")
        self.attributes_label.pack(pady=(0, 5), padx=10, anchor="w")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#222222", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.add_dropdown_row("material", ROBLOX_MATERIALS, "Concrete")
        self.add_attribute_row("speed", "1.0")
        self.add_attribute_row("damage", "25")

        self.apply_btn = ctk.CTkButton(self, text="Apply Changes", fg_color="#7514ED", text_color="#EEEEEE",
                                       hover_color="#500AA6", font=ctk.CTkFont(weight="bold"))
        self.apply_btn.pack(pady=10, padx=10, fill="x")

    def hide_panel(self):
        self.grid_remove()

    def create_property_row(self, label_text, default_val):
        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=2)

        lbl = ctk.CTkLabel(row_frame, text=label_text, width=100, anchor="w", text_color="#EEEEEE")
        lbl.pack(side="left")

        entry = ctk.CTkEntry(row_frame, fg_color="#222222", border_color="#7F7F7F", text_color="#EEEEEE")
        entry.insert(0, default_val)
        entry.pack(side="right", fill="x", expand=True)
        return entry

    def add_attribute_row(self, key, val):
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        key_entry = ctk.CTkEntry(row_frame, width=100, fg_color="#4A4A4A", border_color="#7F7F7F", text_color="#EEEEEE")
        key_entry.insert(0, key)
        key_entry.pack(side="left", padx=(0, 5))

        val_entry = ctk.CTkEntry(row_frame, fg_color="#222222", border_color="#7F7F7F", text_color="#EEEEEE")
        val_entry.insert(0, val)
        val_entry.pack(side="right", fill="x", expand=True)

    def add_dropdown_row(self, key, options, default_val):
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        key_entry = ctk.CTkEntry(row_frame, width=100, fg_color="#4A4A4A", border_color="#7F7F7F", text_color="#EEEEEE")
        key_entry.insert(0, key)
        key_entry.pack(side="left", padx=(0, 5))

        dropdown = ctk.CTkComboBox(row_frame, values=options, fg_color="#222222", border_color="#7F7F7F",
                                   text_color="#EEEEEE", dropdown_fg_color="#4A4A4A", dropdown_hover_color="#7514ED")
        dropdown.set(default_val)
        dropdown.pack(side="right", fill="x", expand=True)