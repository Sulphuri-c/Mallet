import customtkinter as ctk
import json
import os

CONFIG_FILE = "mallet_config.json"

THEMES_MAP = {
    "Regular": {"Background": "#222222", "Sidebar": "#4A4A4A", "Accent": "#7514ED", "Grid Lines": "#3b3b3b"},
    "Night": {"Background": "#000000", "Sidebar": "#121212", "Accent": "#EEAF5C", "Grid Lines": "#1f1f1f"},
    "Calm": {"Background": "#383338", "Sidebar": "#5c525c", "Accent": "#EE7BF0", "Grid Lines": "#4a424a"}
}


class PreferencesWindow(ctk.CTkToplevel):
    def __init__(self, master, current_settings, on_save_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Preferences")
        self.geometry("450x650")
        self.configure(fg_color="#222222")

        self.transient(master)
        self.lift()
        self.focus_force()

        self.on_save_callback = on_save_callback
        self.settings = current_settings

        self.header = ctk.CTkLabel(self, text="Preferences & Customization", font=ctk.CTkFont(size=18, weight="bold"),
                                   text_color="#AE79F0")
        self.header.pack(pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#4A4A4A", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.add_section_label("Theme Presets")
        self.preset_var = ctk.StringVar(value=self.settings.get("theme", "Regular"))
        self.preset_menu = ctk.CTkOptionMenu(self.scroll_frame, values=["Regular", "Night", "Calm", "Custom"],
                                             variable=self.preset_var, command=self.on_preset_changed,
                                             fg_color="#222222", button_color="#222222", button_hover_color="#7514ED",
                                             text_color="#EEEEEE")
        self.preset_menu.pack(fill="x", padx=10, pady=5)

        self.add_section_label("Default Tool Classes")
        self.default_geom_var = ctk.StringVar(value=self.settings.get("default_geometry", "geom_static"))
        self.geom_menu = ctk.CTkOptionMenu(self.scroll_frame,
                                           values=["geom_static", "geom_dynamic", "geom_dambrick", "geom_log_trigger"],
                                           variable=self.default_geom_var, fg_color="#222222", button_color="#222222",
                                           button_hover_color="#7514ED", text_color="#EEEEEE")
        self.geom_menu.pack(fill="x", padx=10, pady=2)

        self.default_prx_var = ctk.StringVar(value=self.settings.get("default_proxy", "wrd_player_start"))
        self.prx_menu = ctk.CTkOptionMenu(self.scroll_frame,
                                          values=["wrd_player_start", "wrd_light", "log_timer", "log_relay",
                                                  "fx_particle", "sfx_regular", "sfx_oneshot"],
                                          variable=self.default_prx_var, fg_color="#222222", button_color="#222222",
                                          button_hover_color="#7514ED", text_color="#EEEEEE")
        self.prx_menu.pack(fill="x", padx=10, pady=5)

        self.add_section_label("Editor & Transformation")
        self.rot_snap_var = ctk.StringVar(value=str(self.settings.get("rotation_snap", "15")))
        self.rot_menu = ctk.CTkOptionMenu(self.scroll_frame, values=["Off", "5", "15", "30", "45", "90"],
                                          variable=self.rot_snap_var, fg_color="#222222", button_color="#222222",
                                          button_hover_color="#7514ED", text_color="#EEEEEE")
        self.rot_menu.pack(fill="x", padx=10, pady=5)

        self.add_section_label("Audio & Immersion Settings")

        self.kbd_sound_var = ctk.BooleanVar(value=self.settings.get("keyboard_sounds", False))
        self.kbd_checkbox = ctk.CTkCheckBox(self.scroll_frame, text="Enable Keyboard Sounds",
                                            variable=self.kbd_sound_var, text_color="#EEEEEE", fg_color="#7514ED",
                                            hover_color="#500AA6")
        self.kbd_checkbox.pack(anchor="w", padx=15, pady=5)

        self.music_var = ctk.BooleanVar(value=self.settings.get("custom_music", True))
        self.music_checkbox = ctk.CTkCheckBox(self.scroll_frame, text="Background Music (Custom Queue)",
                                              variable=self.music_var, text_color="#EEEEEE", fg_color="#7514ED",
                                              hover_color="#500AA6")
        self.music_checkbox.pack(anchor="w", padx=15, pady=5)

        self.add_section_label("Custom HEX Colors")
        self.color_entries = {}

        current_colors = self.settings.get("custom_colors", THEMES_MAP["Regular"])

        for label, hex_val in current_colors.items():
            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            lbl = ctk.CTkLabel(row, text=label, width=120, anchor="w", text_color="#EEEEEE")
            lbl.pack(side="left")
            entry = ctk.CTkEntry(row, fg_color="#222222", border_color="#7F7F7F", text_color="#EEEEEE")
            entry.insert(0, hex_val)
            entry.bind("<KeyRelease>", self.on_hex_edited)
            entry.pack(side="right", fill="x", expand=True)
            self.color_entries[label] = entry

        self.save_btn = ctk.CTkButton(self, text="Apply & Save Preferences", fg_color="#7514ED", text_color="#EEEEEE",
                                      hover_color="#500AA6", font=ctk.CTkFont(weight="bold"),
                                      command=self.save_preferences)
        self.save_btn.pack(pady=10, padx=10, fill="x")

    def add_section_label(self, text):
        lbl = ctk.CTkLabel(self.scroll_frame, text=text, font=ctk.CTkFont(size=14, weight="bold"), text_color="#AE79F0")
        lbl.pack(anchor="w", padx=10, pady=(15, 5))

    def on_preset_changed(self, choice):
        if choice in THEMES_MAP:
            theme_vals = THEMES_MAP[choice]
            for label, entry in self.color_entries.items():
                if label in theme_vals:
                    entry.delete(0, "end")
                    entry.insert(0, theme_vals[label])

    def on_hex_edited(self, event):
        if self.preset_var.get() != "Custom":
            self.preset_var.set("Custom")

    def save_preferences(self):
        updated_settings = {
            "theme": self.preset_var.get(),
            "default_geometry": self.default_geom_var.get(),
            "default_proxy": self.default_prx_var.get(),
            "rotation_snap": self.rot_snap_var.get(),
            "keyboard_sounds": self.kbd_sound_var.get(),
            "custom_music": self.music_var.get(),
            "custom_colors": {k: v.get() for k, v in self.color_entries.items()}
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(updated_settings, f, indent=4)

        self.on_save_callback(updated_settings)
        self.destroy()


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "theme": "Regular",
        "default_geometry": "geom_static",
        "default_proxy": "wrd_player_start",
        "rotation_snap": "15",
        "keyboard_sounds": False,
        "custom_music": True,
        "custom_colors": {
            "Background": "#222222",
            "Sidebar": "#4A4A4A",
            "Accent": "#7514ED",
            "Grid Lines": "#3b3b3b"
        }
    }