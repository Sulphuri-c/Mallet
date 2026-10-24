import customtkinter as ctk
import math
import tkinter as tk


class Viewport3D(ctk.CTkCanvas):
    def __init__(self, master, theme_colors=None, **kwargs):
        super().__init__(master, bg="#222222", highlightthickness=0, **kwargs)

        self.colors = theme_colors or {
            "bg": "#222222",
            "line": "#4A4A4A",
            "accent": "#7514ED",
            "text": "#EEEEEE"
        }

        self.sun_elevation = 45.0
        self.sun_azimuth = 0.0
        self.max_players = 16
        self.gravity = 196.2
        self.atmosphere_density = 0.3

        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1.0
        self.rot_x = 30.0
        self.rot_y = 45.0

        self.bind("<Configure>", self.on_configure)
        self.bind("<ButtonPress-3>", self.start_pan)
        self.bind("<B3-Motion>", self.do_pan)
        self.bind("<ButtonPress-1>", self.on_left_press)
        self.bind("<B1-Motion>", self.do_rotate)
        self.bind("<MouseWheel>", self.zoom_view)
        self.bind("<Button-4>", self.zoom_view)
        self.bind("<Button-5>", self.zoom_view)

        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.initialized_center = False
        self.face_polys = {}

    def on_configure(self, event):
        if not self.initialized_center and event.width > 1 and event.height > 1:
            self.pan_x = event.width / 2
            self.pan_y = event.height / 2
            self.initialized_center = True
        self.draw_grid()

    def start_pan(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def do_pan(self, event):
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        self.pan_x += dx
        self.pan_y += dy
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.draw_grid()

    def on_left_press(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

        master_app = self.winfo_toplevel()
        selected = getattr(master_app, "selected_brush", None)
        active_tool = getattr(master_app, "active_tool", "PTR")

        if selected and active_tool == "MAT" and selected.get("type", "").startswith("geom_"):
            clicked_face = None
            overlapping_items = self.find_overlapping(event.x - 2, event.y - 2, event.x + 2, event.y + 2)

            for item_id in reversed(overlapping_items):
                for face_name, poly_id in self.face_polys.items():
                    if item_id == poly_id:
                        clicked_face = face_name
                        break
                if clicked_face:
                    break

            if clicked_face:
                if hasattr(master_app, "save_history_state"):
                    master_app.save_history_state()

                active_mat = getattr(master_app, "current_paint_material", "SmoothPlastic")
                if "materials" not in selected or not isinstance(selected["materials"], dict):
                    current_default = selected.get("material", "SmoothPlastic")
                    selected["materials"] = {
                        "Top": current_default,
                        "Bottom": current_default,
                        "Left": current_default,
                        "Right": current_default,
                        "Front": current_default,
                        "Back": current_default
                    }

                selected["materials"][clicked_face] = active_mat
                self.draw_grid()

    def do_rotate(self, event):
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        self.rot_y += dx * 0.5
        self.rot_x += dy * 0.5
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.draw_grid()

    def zoom_view(self, event):
        if event.delta > 0 or event.keysym == "Button-4":
            self.zoom *= 1.15
        elif event.delta < 0 or event.keysym == "Button-5":
            self.zoom /= 1.15
        self.draw_grid()

    def project_3d_to_2d_with_depth(self, x, y, z):
        rad_x = math.radians(self.rot_x)
        rad_y = math.radians(self.rot_y)

        y1 = y * math.cos(rad_x) - z * math.sin(rad_x)
        z1 = y * math.sin(rad_x) + z * math.cos(rad_x)
        x1 = x

        x2 = x1 * math.cos(rad_y) + z1 * math.sin(rad_y)
        z2 = -x1 * math.sin(rad_y) + z1 * math.cos(rad_y)
        y2 = y1

        scale = 16.0 * self.zoom * 2.0
        screen_x = x2 * scale + self.pan_x
        screen_y = y2 * scale + self.pan_y
        return screen_x, screen_y, z2

    def draw_grid(self, event=None):
        self.delete("grid_3d")
        self.face_polys.clear()
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        master_app = self.winfo_toplevel()
        selected = getattr(master_app, "selected_brush", None)

        if selected and selected.get("size") and selected.get("type", "").startswith("geom_"):
            sx, sy, sz = selected["size"][0] / 2, selected["size"][1] / 2, selected["size"][2] / 2
            local_verts = [
                (-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
                (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)
            ]

            projected = [self.project_3d_to_2d_with_depth(vx, vy, vz) for vx, vy, vz in local_verts]

            faces = {
                "Top": [4, 5, 6, 7],
                "Bottom": [0, 1, 2, 3],
                "Front": [0, 4, 7, 3],
                "Back": [1, 5, 6, 2],
                "Left": [0, 1, 5, 4],
                "Right": [3, 2, 6, 7]
            }

            face_depths = []
            for face_name, indices in faces.items():
                avg_z = sum(projected[i][2] for i in indices) / len(indices)
                face_depths.append((avg_z, face_name, indices))

            face_depths.sort(key=lambda x: x[0])

            base_color = selected.get("attributes", {}).get("color", "#7514ED")

            for avg_z, face_name, indices in face_depths:
                poly_pts = []
                for idx in indices:
                    poly_pts.extend([projected[idx][0], projected[idx][1]])

                poly_id = self.create_polygon(
                    poly_pts,
                    fill="#332244",
                    outline=base_color,
                    width=2,
                    tags="grid_3d"
                )
                self.face_polys[face_name] = poly_id

                cx = sum(projected[i][0] for i in indices) / len(indices)
                cy = sum(projected[i][1] for i in indices) / len(indices)

                mat_name = selected.get("materials", {}).get(face_name, selected.get("material", "Plastic"))
                self.create_text(
                    cx, cy,
                    text=f"{face_name}\n({mat_name})",
                    fill="#EEEEEE",
                    font=("Arial", 8, "bold"),
                    justify="center",
                    tags="grid_3d"
                )

            info_text = f"Inspecting: {selected.get('type')}"
            self.create_text(
                20, 20,
                text=info_text,
                fill=self.colors.get("text", "#EEEEEE"),
                font=("Arial", 10, "bold"),
                anchor="nw",
                tags="grid_3d"
            )
        else:
            self.create_text(
                20, 20,
                text="Map Overview Mode (Select a geometry brush to inspect 3D)",
                fill=self.colors.get("text", "#EEEEEE"),
                font=("Arial", 10, "bold"),
                anchor="nw",
                tags="grid_3d"
            )

    def get_world_settings(self):
        return {
            "sun_elevation": self.sun_elevation,
            "sun_azimuth": self.sun_azimuth,
            "max_players": self.max_players,
            "gravity": self.gravity,
            "atmosphere_density": self.atmosphere_density
        }

    def set_world_settings(self, settings):
        self.sun_elevation = settings.get("sun_elevation", 45.0)
        self.sun_azimuth = settings.get("sun_azimuth", 0.0)
        self.max_players = settings.get("max_players", 16)
        self.gravity = settings.get("gravity", 196.2)
        self.atmosphere_density = settings.get("atmosphere_density", 0.3)
        self.draw_grid()

    def update_theme(self, new_colors):
        self.colors = new_colors
        self.configure(bg=new_colors["bg"])
        self.draw_grid()