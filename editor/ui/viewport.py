import customtkinter as ctk


class Viewport3D(ctk.CTkScrollableFrame):
    def __init__(self, master, theme_colors=None, **kwargs):
        super().__init__(master, fg_color=theme_colors.get("bg", "#222222") if theme_colors else "#222222",
                         corner_radius=0, **kwargs)

        self.colors = theme_colors or {
            "bg": "#222222",
            "sidebar": "#4A4A4A",
            "accent": "#7514ED",
            "text": "#EEEEEE"
        }

        self.title_lbl = ctk.CTkLabel(self, text="Map Setup & Overview", font=ctk.CTkFont(size=14, weight="bold"),
                                      text_color=self.colors.get("accent", "#7514ED"))
        self.title_lbl.pack(anchor="w", padx=10, pady=(10, 5))

        self.stats_frame = ctk.CTkFrame(self, fg_color=self.colors.get("sidebar", "#4A4A4A"), corner_radius=6)
        self.stats_frame.pack(fill="x", padx=10, pady=5)

        self.geom_count_lbl = ctk.CTkLabel(self.stats_frame, text="Active Brushes: 0",
                                           text_color=self.colors.get("text", "#EEEEEE"))
        self.geom_count_lbl.pack(anchor="w", padx=10, pady=4)

        self.proxy_count_lbl = ctk.CTkLabel(self.stats_frame, text="Spawned Entities: 0",
                                            text_color=self.colors.get("text", "#EEEEEE"))
        self.proxy_count_lbl.pack(anchor="w", padx=10, pady=4)

        self.env_lbl = ctk.CTkLabel(self, text="Roblox World & Lighting", font=ctk.CTkFont(size=14, weight="bold"),
                                    text_color=self.colors.get("accent", "#7514ED"))
        self.env_lbl.pack(anchor="w", padx=10, pady=(15, 5))

        self.time_row = ctk.CTkFrame(self, fg_color="transparent")
        self.time_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(self.time_row, text="ClockTime (Hours)", width=130, anchor="w",
                     text_color=self.colors.get("text", "#EEEEEE")).pack(side="left")
        self.time_entry = ctk.CTkEntry(self.time_row, fg_color="#222222", border_color="#7F7F7F", text_color="#EEEEEE")
        self.time_entry.insert(0, "14.5")
        self.time_entry.pack(side="right", fill="x", expand=True)

        self.multi_row = ctk.CTkFrame(self, fg_color="transparent")
        self.multi_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(self.multi_row, text="Max Players", width=130, anchor="w",
                     text_color=self.colors.get("text", "#EEEEEE")).pack(side="left")
        self.multi_entry = ctk.CTkEntry(self.multi_row, fg_color="#222222", border_color="#7F7F7F",
                                        text_color="#EEEEEE")
        self.multi_entry.insert(0, "16")
        self.multi_entry.pack(side="right", fill="x", expand=True)

        self.fog_row = ctk.CTkFrame(self, fg_color="transparent")
        self.fog_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(self.fog_row, text="Enable Atmosphere", width=130, anchor="w",
                     text_color=self.colors.get("text", "#EEEEEE")).pack(side="left")
        self.fog_var = ctk.BooleanVar(value=True)
        self.fog_check = ctk.CTkCheckBox(self.fog_row, text="", variable=self.fog_var, fg_color="#7514ED",
                                         hover_color="#500AA6")
        self.fog_check.pack(side="right", anchor="w")

        self.io_lbl = ctk.CTkLabel(self, text="Signal & Event Routing", font=ctk.CTkFont(size=14, weight="bold"),
                                   text_color=self.colors.get("accent", "#7514ED"))
        self.io_lbl.pack(anchor="w", padx=10, pady=(15, 5))

        self.io_info = ctk.CTkLabel(self,
                                    text="Configure global channels and entity connections across your level layout.",
                                    text_color=self.colors.get("text", "#EEEEEE"), wraplength=320, justify="left")
        self.io_info.pack(anchor="w", padx=10, pady=5)

    def draw_grid(self, event=None):
        self.refresh_stats()

    def refresh_stats(self):
        master_app = self.winfo_toplevel()
        if hasattr(master_app, "workspace_brushes") and hasattr(master_app, "workspace_proxies"):
            g_count = len(master_app.workspace_brushes)
            p_count = len(master_app.workspace_proxies)
            self.geom_count_lbl.configure(text=f"Active Brushes: {g_count}")
            self.proxy_count_lbl.configure(text=f"Spawned Entities: {p_count}")

    def update_theme(self, new_colors):
        self.colors = new_colors
        self.configure(fg_color=new_colors["bg"])
        self.title_lbl.configure(text_color=new_colors["accent"])
        self.env_lbl.configure(text_color=new_colors["accent"])
        self.io_lbl.configure(text_color=new_colors["accent"])