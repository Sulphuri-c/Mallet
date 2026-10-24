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

class MaterialPanel(ctk.CTkFrame):
    def __init__(self, master, on_material_picked=None, **kwargs):
        super().__init__(master, fg_color="#4A4A4A", width=300, corner_radius=0, **kwargs)
        self.grid_propagate(False)
        self.on_material_picked = on_material_picked
        self.selected_material = "SmoothPlastic"

        header_label = ctk.CTkLabel(
            self,
            text="Material Editor (MAT)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#AE79F0"
        )
        header_label.pack(pady=(15, 10), padx=10, anchor="w")

        info_lbl = ctk.CTkLabel(self, text="Active Paint Material:", text_color="#EEEEEE", font=ctk.CTkFont(size=12))
        info_lbl.pack(padx=10, anchor="w", pady=(0, 2))

        self.material_var = ctk.StringVar(value=self.selected_material)
        self.material_dropdown = ctk.CTkOptionMenu(
            self,
            values=ROBLOX_MATERIALS,
            variable=self.material_var,
            command=self.select_material,
            fg_color="#222222",
            button_color="#222222",
            button_hover_color="#7514ED",
            text_color="#EEEEEE"
        )
        self.material_dropdown.pack(fill="x", padx=10, pady=(0, 10))

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#222222", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for mat in ROBLOX_MATERIALS:
            btn = ctk.CTkButton(
                self.scroll_frame,
                text=mat,
                fg_color="#4A4A4A",
                hover_color="#7514ED",
                text_color="#EEEEEE",
                anchor="w",
                command=lambda m=mat: self.select_material(m)
            )
            btn.pack(fill="x", pady=2, padx=2)

    def select_material(self, mat_name):
        self.selected_material = mat_name
        self.material_var.set(mat_name)
        if self.on_material_picked:
            self.on_material_picked(mat_name)