import customtkinter as ctk
import math
import tkinter as tk
import copy
from core.proxies import generate_element_uuid


class Viewport2D(ctk.CTkCanvas):
    def __init__(self, master, view_type="top", grid_size=1, theme_colors=None, on_hover_callback=None, **kwargs):
        super().__init__(master, bg="#222222", highlightthickness=0, **kwargs)

        self.view_type = view_type
        self.grid_size = grid_size
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1.0
        self.pixels_per_stud = 16
        self.on_hover_callback = on_hover_callback

        self.colors = theme_colors or {
            "bg": "#222222",
            "line": "#4A4A4A",
            "subline": "#333333",
            "origin_x": "#EE6767",
            "origin_y": "#68FF88"
        }

        self.bind("<Configure>", self.on_configure)
        self.bind("<ButtonPress-3>", self.start_pan)
        self.bind("<B3-Motion>", self.do_pan)
        self.bind("<ButtonRelease-3>", self.on_right_release)

        self.bind("<ButtonPress-1>", self.on_left_press)
        self.bind("<B1-Motion>", self.on_left_drag)
        self.bind("<ButtonRelease-1>", self.on_left_release)

        self.bind("<MouseWheel>", self.zoom_view)
        self.bind("<Button-4>", self.zoom_view)
        self.bind("<Button-5>", self.zoom_view)

        self.bind("<bracketleft>", self.decrease_grid)
        self.bind("<bracketright>", self.increase_grid)
        self.bind("c", self.center_view)
        self.bind("<Delete>", self.delete_selected)
        self.bind("<BackSpace>", self.delete_selected)
        self.bind("<Enter>", self.on_mouse_enter)

        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.press_screen_x = 0
        self.press_screen_y = 0
        self.did_drag = False
        self.did_right_drag = False
        self.clicked_already_selected = False
        self.drawing_start_x = 0
        self.drawing_start_y = 0
        self.current_rect = None
        self.dragging_brush = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.active_handle = None
        self.rotate_start_angle = 0.0
        self.initial_brush_rot = 0.0
        self.initialized_center = False

    def is_volumetric_item(self, item):
        if not item or "size" not in item:
            return False
        t = item.get("type", "")
        return t.startswith("geom_") or t.startswith("msh_")

    def on_configure(self, event):
        if not self.initialized_center and event.width > 1 and event.height > 1:
            self.pan_x = event.width / 2
            self.pan_y = event.height / 2
            self.initialized_center = True
        self.draw_grid()

    def on_mouse_enter(self, event):
        self.focus_set()
        if self.on_hover_callback:
            self.on_hover_callback(self.grid_size, self.view_type)

    def delete_selected(self, event=None):
        master_app = self.winfo_toplevel()
        selected = getattr(master_app, "selected_brush", None)
        if selected:
            self.context_delete(selected)

    def screen_to_world(self, screen_x, screen_y):
        world_x = (screen_x - self.pan_x) / (self.pixels_per_stud * self.zoom)
        world_y = (screen_y - self.pan_y) / (self.pixels_per_stud * self.zoom)
        return world_x, world_y

    def world_to_screen(self, world_x, world_y):
        screen_x = world_x * self.pixels_per_stud * self.zoom + self.pan_x
        screen_y = world_y * self.pixels_per_stud * self.zoom + self.pan_y
        return screen_x, screen_y

    def get_item_screen_center(self, item):
        px, py, pz = item["pos"][0], item["pos"][1], item["pos"][2]
        if self.view_type == "2d top":
            return self.world_to_screen(px, pz)
        elif self.view_type == "2d front":
            return self.world_to_screen(px, py)
        else:
            return self.world_to_screen(pz, py)

    def get_axes_coords(self, pos, size):
        x, y, z = pos[0], pos[1], pos[2]
        sx, sy, sz = size[0], size[1], size[2]

        if self.view_type == "2d top":
            return x - sx / 2, z - sz / 2, x + sx / 2, z + sz / 2
        elif self.view_type == "2d front":
            return x - sx / 2, y - sy / 2, x + sx / 2, y + sy / 2
        else:
            return z - sz / 2, y - sy / 2, z + sz / 2, y + sy / 2

    def set_axes_coords(self, brush, x1, y1, x2, y2):
        nx1, nx2 = min(x1, x2), max(x1, x2)
        ny1, ny2 = min(y1, y2), max(y1, y2)

        if nx2 - nx1 < self.grid_size:
            nx2 = nx1 + self.grid_size
        if ny2 - ny1 < self.grid_size:
            ny2 = ny1 + self.grid_size

        sa = nx2 - nx1
        sb = ny2 - ny1
        ca = nx1 + sa / 2
        cb = ny1 + sb / 2

        if self.view_type == "2d top":
            brush["pos"][0] = ca
            brush["pos"][2] = cb
            brush["size"][0] = sa
            brush["size"][2] = sb
        elif self.view_type == "2d front":
            brush["pos"][0] = ca
            brush["pos"][1] = cb
            brush["size"][0] = sa
            brush["size"][1] = sb
        else:
            brush["pos"][2] = ca
            brush["pos"][1] = cb
            brush["size"][2] = sa
            brush["size"][1] = sb

    def get_3d_transformed_screen_vertices(self, item):
        cx, cy, cz = item["pos"][0], item["pos"][1], item["pos"][2]
        sx, sy, sz = item["size"][0] / 2.0, item["size"][1] / 2.0, item["size"][2] / 2.0
        rot = item.get("rot", [0.0, 0.0, 0.0])

        rx = math.radians(rot[0])
        ry = math.radians(rot[1])
        rz = math.radians(rot[2])

        cx_r, sx_r = math.cos(rx), math.sin(rx)
        cy_r, sy_r = math.cos(ry), math.sin(ry)
        cz_r, sz_r = math.cos(rz), math.sin(rz)

        local_verts = [
            (-sx, -sy, -sz),
            (sx, -sy, -sz),
            (sx, sy, -sz),
            (-sx, sy, -sz),
            (-sx, -sy, sz),
            (sx, -sy, sz),
            (sx, sy, sz),
            (-sx, sy, sz)
        ]

        screen_verts = []
        for lx, ly, lz in local_verts:
            y1 = ly * cx_r - lz * sx_r
            z1 = ly * sx_r + lz * cx_r
            x1 = lx

            x2 = x1 * cy_r + z1 * sy_r
            z2 = -x1 * sy_r + z1 * cy_r
            y2 = y1

            x3 = x2 * cz_r - y2 * sz_r
            y3 = x2 * sz_r + y2 * cz_r
            z3 = z2

            wx = cx + x3
            wy = cy + y3
            wz = cz + z3

            if self.view_type == "2d top":
                px, py = wx, wz
            elif self.view_type == "2d front":
                px, py = wx, wy
            else:
                px, py = wz, wy

            screen_verts.append(self.world_to_screen(px, py))

        return screen_verts

    def get_projected_2d_corners(self, item):
        verts = self.get_3d_transformed_screen_vertices(item)
        if self.view_type == "2d top":
            c0 = ((verts[0][0] + verts[3][0]) / 2, (verts[0][1] + verts[3][1]) / 2)
            c1 = ((verts[1][0] + verts[2][0]) / 2, (verts[1][1] + verts[2][1]) / 2)
            c2 = ((verts[5][0] + verts[6][0]) / 2, (verts[5][1] + verts[6][1]) / 2)
            c3 = ((verts[4][0] + verts[7][0]) / 2, (verts[4][1] + verts[7][1]) / 2)
        elif self.view_type == "2d front":
            c0 = ((verts[0][0] + verts[4][0]) / 2, (verts[0][1] + verts[4][1]) / 2)
            c1 = ((verts[1][0] + verts[5][0]) / 2, (verts[1][1] + verts[5][1]) / 2)
            c2 = ((verts[2][0] + verts[6][0]) / 2, (verts[2][1] + verts[6][1]) / 2)
            c3 = ((verts[3][0] + verts[7][0]) / 2, (verts[3][1] + verts[7][1]) / 2)
        else:
            c0 = ((verts[0][0] + verts[1][0]) / 2, (verts[0][1] + verts[1][1]) / 2)
            c1 = ((verts[4][0] + verts[5][0]) / 2, (verts[4][1] + verts[5][1]) / 2)
            c2 = ((verts[6][0] + verts[7][0]) / 2, (verts[6][1] + verts[7][1]) / 2)
            c3 = ((verts[2][0] + verts[3][0]) / 2, (verts[2][1] + verts[3][1]) / 2)
        return [c0, c1, c2, c3]

    def get_rotated_transform_handles(self, pts):
        p0, p1, p2, p3 = pts
        nmx, nmy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        emx, emy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        smx, smy = (p3[0] + p2[0]) / 2, (p3[1] + p2[1]) / 2
        wmx, wmy = (p0[0] + p3[0]) / 2, (p0[1] + p3[1]) / 2
        return {
            "nw": p0,
            "n": (nmx, nmy),
            "ne": p1,
            "e": (emx, emy),
            "se": p2,
            "s": (smx, smy),
            "sw": p3,
            "w": (wmx, wmy)
        }

    def get_brush_angle(self, brush):
        rot = brush.get("rot", [0.0, 0.0, 0.0])
        if self.view_type == "2d top":
            return -rot[1]
        elif self.view_type == "2d front":
            return rot[2]
        else:
            return -rot[0]

    def set_brush_angle(self, brush, angle):
        if "rot" not in brush:
            brush["rot"] = [0.0, 0.0, 0.0]
        if self.view_type == "2d top":
            brush["rot"][1] = (-angle) % 360.0
        elif self.view_type == "2d front":
            brush["rot"][2] = angle % 360.0
        else:
            brush["rot"][0] = (-angle) % 360.0

    def get_brush_depth_sort_key(self, brush):
        x, y, z = brush["pos"][0], brush["pos"][1], brush["pos"][2]
        sx, sy, sz = brush["size"][0], brush["size"][1], brush["size"][2]

        if self.view_type == "2d top":
            depth = -y + sy / 2
            area = sx * sz
        elif self.view_type == "2d front":
            depth = -z + sz / 2
            area = sx * sy
        else:
            depth = x + sx / 2
            area = sz * sy

        return (-area, depth)

    def draw_grid(self, event=None):
        self.delete("grid_element")
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        scaled_grid = self.grid_size * self.pixels_per_stud * self.zoom

        start_x = (self.pan_x % scaled_grid) - scaled_grid
        start_y = (self.pan_y % scaled_grid) - scaled_grid

        x = start_x
        while x < width:
            is_major = abs((x - self.pan_x) / scaled_grid) % 4 == 0
            color = self.colors["line"] if is_major else self.colors["subline"]
            self.create_line(x, 0, x, height, fill=color, tags="grid_element")
            x += scaled_grid

        y = start_y
        while y < height:
            is_major = abs((y - self.pan_y) / scaled_grid) % 4 == 0
            color = self.colors["line"] if is_major else self.colors["subline"]
            self.create_line(0, y, width, y, fill=color, tags="grid_element")
            y += scaled_grid

        self.create_line(self.pan_x, 0, self.pan_x, height, fill=self.colors["origin_y"], width=2, tags="grid_element")
        self.create_line(0, self.pan_y, width, self.pan_y, fill=self.colors["origin_x"], width=2, tags="grid_element")

        self.tag_lower("grid_element")
        self.redraw_workspace_brushes()

    def draw_wireframe_box(self, item, edge_color, diag_color):
        cube_edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        face_diagonals = [
            (0, 2), (4, 6), (0, 5), (2, 7), (0, 7), (1, 6)
        ]
        verts = self.get_3d_transformed_screen_vertices(item)
        for i1, i2 in face_diagonals:
            self.create_line(
                verts[i1][0], verts[i1][1], verts[i2][0], verts[i2][1],
                fill=diag_color,
                width=1,
                tags="grid_element"
            )
        for i1, i2 in cube_edges:
            self.create_line(
                verts[i1][0], verts[i1][1], verts[i2][0], verts[i2][1],
                fill=edge_color,
                width=2,
                tags="grid_element"
            )

    def draw_io_connections(self, master_app, selected_item):
        if not getattr(master_app, "app_settings", {}).get("show_io_lines", False):
            return

        all_items = getattr(master_app, "workspace_brushes", []) + getattr(master_app, "workspace_proxies", [])
        target_map = {}
        for it in all_items:
            mid = it.get("mallet_id", "").strip()
            if not mid and "attributes" in it:
                mid = it["attributes"].get("mallet_id", "").strip()
            if mid:
                target_map.setdefault(mid, []).append(it)

        for src in all_items:
            io_list = src.get("io", [])
            if not io_list:
                continue

            sx1, sy1 = self.get_item_screen_center(src)
            for conn in io_list:
                target_id = conn.get("target", "").strip()
                if not target_id:
                    continue

                targets = target_map.get(target_id, [])
                if not targets:
                    if src == selected_item:
                        self.create_oval(
                            sx1 - 10, sy1 - 10, sx1 + 10, sy1 + 10,
                            outline="#FF4444", width=2, tags="grid_element"
                        )
                    continue

                for dst in targets:
                    sx2, sy2 = self.get_item_screen_center(dst)
                    is_active = (src == selected_item or dst == selected_item)
                    line_color = "#00E5FF" if is_active else "#2A6B7C"
                    line_width = 2 if is_active else 1

                    self.create_line(
                        sx1, sy1, sx2, sy2,
                        fill=line_color,
                        width=line_width,
                        dash=(6, 4),
                        arrow=tk.LAST,
                        arrowshape=(10, 12, 5),
                        tags="grid_element"
                    )

                    if is_active:
                        mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
                        out_name = conn.get("output", "")
                        inp_name = conn.get("input", "")
                        self.create_text(
                            mx, my - 8,
                            text=f"{out_name} -> {inp_name}",
                            fill="#00E5FF",
                            font=("Arial", 8, "bold"),
                            tags="grid_element"
                        )

    def redraw_workspace_brushes(self):
        master_app = self.winfo_toplevel()
        selected_item = getattr(master_app, "selected_brush", None)

        if hasattr(master_app, "workspace_brushes"):
            for brush in master_app.workspace_brushes:
                if brush == selected_item:
                    continue
                self.draw_wireframe_box(
                    brush,
                    self.colors.get("accent", "#7514ED"),
                    self.colors.get("line", "#3b3b3b")
                )

        if hasattr(master_app, "workspace_proxies"):
            for proxy in master_app.workspace_proxies:
                is_selected = (proxy == selected_item)
                if self.is_volumetric_item(proxy):
                    if not is_selected:
                        self.draw_wireframe_box(proxy, "#AE79F0", self.colors.get("line", "#3b3b3b"))
                    sx, sy = self.get_item_screen_center(proxy)
                    proxy_type = proxy.get("type", "msh")
                    short_label = proxy_type.upper()
                    self.create_text(
                        sx, sy,
                        text=short_label,
                        fill="#EEEEEE" if is_selected else "#AE79F0",
                        font=("Arial", 8, "bold"),
                        tags="grid_element"
                    )
                else:
                    sx, sy = self.get_item_screen_center(proxy)
                    color = "#EEEEEE" if is_selected else self.colors.get("accent", "#7514ED")
                    size = 6

                    self.create_rectangle(
                        sx - size, sy - size,
                        sx + size, sy + size,
                        fill=color,
                        outline="#222222",
                        width=2,
                        tags="grid_element"
                    )

                    proxy_type = proxy.get("type", "proxy")
                    short_label = proxy_type.split("_")[-1][:3].upper()
                    self.create_text(
                        sx, sy - 12,
                        text=short_label,
                        fill=color,
                        font=("Arial", 9, "bold"),
                        tags="grid_element"
                    )

        self.draw_io_connections(master_app, selected_item)

        if selected_item and self.is_volumetric_item(selected_item):
            all_volumetric = getattr(master_app, "workspace_brushes", []) + getattr(master_app, "workspace_proxies", [])
            if selected_item in all_volumetric:
                self.draw_wireframe_box(selected_item, "#EEEEEE", "#7F7F7F")

                pts = self.get_projected_2d_corners(selected_item)
                handles = self.get_rotated_transform_handles(pts)
                hs = 6
                mode = getattr(master_app, "transform_mode", "scale")

                if mode == "scale":
                    for h_name, (hx, hy) in handles.items():
                        self.create_rectangle(
                            hx - hs, hy - hs,
                            hx + hs, hy + hs,
                            fill="#EEEEEE",
                            outline="#222222",
                            width=1,
                            tags="grid_element"
                        )
                elif mode == "rotate":
                    for h_name in ["nw", "ne", "se", "sw"]:
                        hx, hy = handles[h_name]
                        self.create_oval(
                            hx - hs - 1, hy - hs - 1,
                            hx + hs + 1, hy + hs + 1,
                            fill=self.colors.get("origin_y", "#68FF88"),
                            outline="#222222",
                            width=1,
                            tags="grid_element"
                        )

    def start_pan(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.press_screen_x = event.x
        self.press_screen_y = event.y
        self.did_right_drag = False

    def do_pan(self, event):
        if abs(event.x - self.press_screen_x) > 2 or abs(event.y - self.press_screen_y) > 2:
            self.did_right_drag = True
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        self.pan_x += dx
        self.pan_y += dy
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.draw_grid()

    def on_right_release(self, event):
        if not self.did_right_drag:
            self.show_context_menu_at(event)

    def zoom_view(self, event):
        if event.delta > 0 or event.keysym == "Button-4":
            self.zoom *= 1.15
        elif event.delta < 0 or event.keysym == "Button-5":
            self.zoom /= 1.15
        self.draw_grid()

    def on_left_press(self, event):
        master_app = self.winfo_toplevel()
        active_tool = getattr(master_app, "active_tool", "PTR")
        wx, wy = self.screen_to_world(event.x, event.y)
        self.active_handle = None
        self.did_drag = False
        self.clicked_already_selected = False
        self.press_screen_x = event.x
        self.press_screen_y = event.y

        if active_tool == "PTR":
            selected = getattr(master_app, "selected_brush", None)
            mode = getattr(master_app, "transform_mode", "scale")

            if selected and self.is_volumetric_item(selected):
                pts = self.get_projected_2d_corners(selected)
                handles = self.get_rotated_transform_handles(pts)

                for h_name, (hx, hy) in handles.items():
                    if mode == "rotate" and h_name not in ["nw", "ne", "se", "sw"]:
                        continue
                    if abs(event.x - hx) <= 12 and abs(event.y - hy) <= 12:
                        self.active_handle = h_name
                        self.dragging_brush = selected
                        if hasattr(master_app, "save_history_state"):
                            master_app.save_history_state()
                        if mode == "rotate":
                            cx, cy = (pts[0][0] + pts[2][0]) / 2, (pts[0][1] + pts[2][1]) / 2
                            self.rotate_start_angle = math.degrees(math.atan2(event.y - cy, event.x - cx))
                            self.initial_brush_rot = self.get_brush_angle(selected)
                        return

            clicked_item = None
            if hasattr(master_app, "workspace_proxies"):
                for proxy in master_app.workspace_proxies:
                    if self.is_volumetric_item(proxy):
                        continue
                    px, py, pz = proxy["pos"][0], proxy["pos"][1], proxy["pos"][2]
                    psx, psy = proxy["size"][0], proxy["size"][2]
                    if self.view_type == "2d top":
                        x1, y1, x2, y2 = px - psx / 2, pz - psy / 2, px + psx / 2, pz + psy / 2
                    elif self.view_type == "2d front":
                        x1, y1, x2, y2 = px - psx / 2, py - psy / 2, px + psx / 2, py + psy / 2
                    else:
                        x1, y1, x2, y2 = pz - psx / 2, py - psy / 2, pz + psx / 2, py + psy / 2

                    if x1 <= wx <= x2 and y1 <= wy <= y2:
                        clicked_item = proxy
                        break

            if not clicked_item:
                candidates = []
                volumetric_pool = [
                                      p for p in getattr(master_app, "workspace_proxies", []) if
                                      self.is_volumetric_item(p)
                                  ] + getattr(master_app, "workspace_brushes", [])

                for idx, brush in enumerate(volumetric_pool):
                    verts = self.get_3d_transformed_screen_vertices(brush)
                    xs = [v[0] for v in verts]
                    ys = [v[1] for v in verts]
                    if min(xs) <= event.x <= max(xs) and min(ys) <= event.y <= max(ys):
                        depth, neg_area = self.get_brush_depth_sort_key(brush)
                        candidates.append((depth, neg_area, idx, brush))
                if candidates:
                    candidates.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
                    clicked_item = candidates[0][3]

            if clicked_item:
                if clicked_item == selected:
                    self.clicked_already_selected = True
                else:
                    master_app.transform_mode = "scale"
                    if hasattr(master_app, "select_brush"):
                        master_app.select_brush(clicked_item)

                self.dragging_brush = clicked_item
                if hasattr(master_app, "save_history_state"):
                    master_app.save_history_state()
                if self.is_volumetric_item(clicked_item):
                    x1, y1, x2, y2 = self.get_axes_coords(clicked_item["pos"], clicked_item["size"])
                    self.drag_offset_x = x1 - wx
                    self.drag_offset_y = y1 - wy
                else:
                    if self.view_type == "2d top":
                        self.drag_offset_x = clicked_item["pos"][0] - wx
                        self.drag_offset_y = clicked_item["pos"][2] - wy
                    elif self.view_type == "2d front":
                        self.drag_offset_x = clicked_item["pos"][0] - wx
                        self.drag_offset_y = clicked_item["pos"][1] - wy
                    else:
                        self.drag_offset_x = clicked_item["pos"][2] - wx
                        self.drag_offset_y = clicked_item["pos"][1] - wy
            else:
                if hasattr(master_app, "select_brush"):
                    master_app.select_brush(None)
                master_app.transform_mode = "scale"

        elif active_tool == "PRX":
            wx, wy = self.screen_to_world(event.x, event.y)
            grid_x = round(wx / self.grid_size) * self.grid_size
            grid_y = round(wy / self.grid_size) * self.grid_size

            if self.view_type == "2d top":
                pos = [grid_x, 0.0, grid_y]
            elif self.view_type == "2d front":
                pos = [grid_x, grid_y, 0.0]
            else:
                pos = [0.0, grid_y, grid_x]

            if hasattr(master_app, "save_history_state"):
                master_app.save_history_state()
            if hasattr(master_app, "add_workspace_proxy"):
                default_type = master_app.app_settings.get("default_proxy", "wrd_player_start")
                master_app.add_workspace_proxy(default_type, pos)

        elif active_tool == "BLK":
            self.drawing_start_x = round(wx / self.grid_size) * self.grid_size
            self.drawing_start_y = round(wy / self.grid_size) * self.grid_size

        elif active_tool == "MAT":
            clicked_brush = None
            if hasattr(master_app, "workspace_brushes"):
                candidates = []
                for idx, brush in enumerate(master_app.workspace_brushes):
                    verts = self.get_3d_transformed_screen_vertices(brush)
                    xs = [v[0] for v in verts]
                    ys = [v[1] for v in verts]
                    if min(xs) <= event.x <= max(xs) and min(ys) <= event.y <= max(ys):
                        candidates.append((idx, brush))
                if candidates:
                    clicked_brush = candidates[0][1]

            if clicked_brush and "materials" in clicked_brush:
                if hasattr(master_app, "save_history_state"):
                    master_app.save_history_state()

                face_to_paint = "Top"
                if self.view_type == "2d front":
                    face_to_paint = "Front"
                elif self.view_type == "2d side":
                    face_to_paint = "Left"

                active_mat = getattr(master_app, "current_paint_material", "SmoothPlastic")
                clicked_brush["materials"][face_to_paint] = active_mat
                clicked_brush["material"] = active_mat
                self.draw_grid()

    def show_context_menu_at(self, event):
        master_app = self.winfo_toplevel()
        active_tool = getattr(master_app, "active_tool", "PTR")
        wx, wy = self.screen_to_world(event.x, event.y)
        clicked_item = None

        if active_tool == "PTR":
            if hasattr(master_app, "workspace_proxies"):
                for proxy in master_app.workspace_proxies:
                    if self.is_volumetric_item(proxy):
                        verts = self.get_3d_transformed_screen_vertices(proxy)
                        xs = [v[0] for v in verts]
                        ys = [v[1] for v in verts]
                        if min(xs) <= event.x <= max(xs) and min(ys) <= event.y <= max(ys):
                            clicked_item = proxy
                            break
                    else:
                        px, py, pz = proxy["pos"][0], proxy["pos"][1], proxy["pos"][2]
                        psx, psy = proxy["size"][0], proxy["size"][2]
                        if self.view_type == "2d top":
                            x1, y1, x2, y2 = px - psx / 2, pz - psy / 2, px + psx / 2, pz + psy / 2
                        elif self.view_type == "2d front":
                            x1, y1, x2, y2 = px - psx / 2, py - psy / 2, px + psx / 2, py + psy / 2
                        else:
                            x1, y1, x2, y2 = pz - psx / 2, py - psy / 2, pz + psx / 2, py + psy / 2
                        if x1 <= wx <= x2 and y1 <= wy <= y2:
                            clicked_item = proxy
                            break

            if not clicked_item and hasattr(master_app, "workspace_brushes"):
                for brush in master_app.workspace_brushes:
                    verts = self.get_3d_transformed_screen_vertices(brush)
                    xs = [v[0] for v in verts]
                    ys = [v[1] for v in verts]
                    if min(xs) <= event.x <= max(xs) and min(ys) <= event.y <= max(ys):
                        clicked_item = brush
                        break

        menu = tk.Menu(self, tearoff=0, bg="#333333", fg="#EEEEEE", activebackground="#7514ED",
                       activeforeground="#EEEEEE")
        if clicked_item:
            menu.add_command(label="Cut", command=lambda: self.context_cut(clicked_item))
            menu.add_command(label="Copy", command=lambda: self.context_copy(clicked_item))
            menu.add_command(label="Duplicate", command=lambda: self.context_duplicate(clicked_item))
            menu.add_separator()
            menu.add_command(label="Delete", command=lambda: self.context_delete(clicked_item))
        else:
            menu.add_command(label="Paste", command=self.context_paste)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def context_copy(self, item):
        master_app = self.winfo_toplevel()
        master_app.clipboard_item = copy.deepcopy(item)

    def context_cut(self, item):
        master_app = self.winfo_toplevel()
        if hasattr(master_app, "save_history_state"):
            master_app.save_history_state()
        master_app.clipboard_item = copy.deepcopy(item)
        self.context_delete(item)

    def context_paste(self):
        master_app = self.winfo_toplevel()
        if hasattr(master_app, "clipboard_item") and master_app.clipboard_item:
            if hasattr(master_app, "save_history_state"):
                master_app.save_history_state()
            new_item = copy.deepcopy(master_app.clipboard_item)
            new_item["uuid"] = generate_element_uuid(new_item.get("type", "geom_static"))
            new_item["pos"][0] += 4
            new_item["pos"][2] += 4
            if new_item in master_app.workspace_brushes or new_item["type"].startswith("geom_"):
                master_app.workspace_brushes.append(new_item)
            else:
                master_app.workspace_proxies.append(new_item)
            for vp in master_app.viewports:
                vp.draw_grid()

    def context_duplicate(self, item):
        self.context_copy(item)
        self.context_paste()

    def context_delete(self, item):
        master_app = self.winfo_toplevel()
        if hasattr(master_app, "save_history_state"):
            master_app.save_history_state()
        if item in master_app.workspace_brushes:
            master_app.workspace_brushes.remove(item)
        elif item in master_app.workspace_proxies:
            master_app.workspace_proxies.remove(item)
        if master_app.selected_brush == item:
            master_app.select_brush(None)
        for vp in master_app.viewports:
            vp.draw_grid()

    def on_left_drag(self, event):
        if abs(event.x - self.press_screen_x) > 2 or abs(event.y - self.press_screen_y) > 2:
            self.did_drag = True

        master_app = self.winfo_toplevel()
        active_tool = getattr(master_app, "active_tool", "PTR")
        wx, wy = self.screen_to_world(event.x, event.y)
        mode = getattr(master_app, "transform_mode", "scale")

        if active_tool == "PTR" and self.dragging_brush:
            if not self.is_volumetric_item(self.dragging_brush):
                if self.view_type == "2d top":
                    self.dragging_brush["pos"][0] = round(wx / self.grid_size) * self.grid_size
                    self.dragging_brush["pos"][2] = round(wy / self.grid_size) * self.grid_size
                elif self.view_type == "2d front":
                    self.dragging_brush["pos"][0] = round(wx / self.grid_size) * self.grid_size
                    self.dragging_brush["pos"][1] = round(wy / self.grid_size) * self.grid_size
                else:
                    self.dragging_brush["pos"][2] = round(wx / self.grid_size) * self.grid_size
                    self.dragging_brush["pos"][1] = round(wy / self.grid_size) * self.grid_size
                for vp in master_app.viewports:
                    vp.draw_grid()
                return

            x1, y1, x2, y2 = self.get_axes_coords(self.dragging_brush["pos"], self.dragging_brush["size"])

            if self.active_handle and mode == "rotate":
                wx1, wy1, wx2, wy2 = self.get_axes_coords(self.dragging_brush["pos"], self.dragging_brush["size"])
                sx1, sy1 = self.world_to_screen(wx1, wy1)
                sx2, sy2 = self.world_to_screen(wx2, wy2)
                cx, cy = (sx1 + sx2) / 2, (sy1 + sy2) / 2

                current_angle = math.degrees(math.atan2(event.y - cy, event.x - cx))
                delta_angle = current_angle - self.rotate_start_angle
                raw_angle = self.initial_brush_rot + delta_angle

                snap_setting = master_app.app_settings.get("rotation_snap", "15")
                if snap_setting == "Off":
                    new_angle = raw_angle
                else:
                    snap_val = float(str(snap_setting).replace("°", ""))
                    new_angle = round(raw_angle / snap_val) * snap_val

                self.set_brush_angle(self.dragging_brush, new_angle)
                for vp in master_app.viewports:
                    vp.draw_grid()
                return

            if self.active_handle and mode == "scale":
                snapped_wx = round(wx / self.grid_size) * self.grid_size
                snapped_wy = round(wy / self.grid_size) * self.grid_size

                if "w" in self.active_handle:
                    x1 = min(snapped_wx, x2 - self.grid_size)
                if "e" in self.active_handle:
                    x2 = max(snapped_wx, x1 + self.grid_size)
                if "n" in self.active_handle:
                    y1 = min(snapped_wy, y2 - self.grid_size)
                if "s" in self.active_handle:
                    y2 = max(snapped_wy, y1 + self.grid_size)

                self.set_axes_coords(self.dragging_brush, x1, y1, x2, y2)
            else:
                w = x2 - x1
                h = y2 - y1
                nx1 = round((wx + self.drag_offset_x) / self.grid_size) * self.grid_size
                ny1 = round((wy + self.drag_offset_y) / self.grid_size) * self.grid_size
                self.set_axes_coords(self.dragging_brush, nx1, ny1, nx1 + w, ny1 + h)

            for vp in master_app.viewports:
                vp.draw_grid()

        elif active_tool == "BLK":
            current_x = round(wx / self.grid_size) * self.grid_size
            current_y = round(wy / self.grid_size) * self.grid_size

            if self.current_rect:
                self.delete(self.current_rect)

            s_x1, s_y1 = self.world_to_screen(self.drawing_start_x, self.drawing_start_y)
            s_x2, s_y2 = self.world_to_screen(current_x, current_y)

            self.current_rect = self.create_rectangle(
                s_x1, s_y1, s_x2, s_y2,
                outline=self.colors.get("accent", "#7514ED"),
                width=2,
                tags="grid_element"
            )

    def on_left_release(self, event):
        master_app = self.winfo_toplevel()
        active_tool = getattr(master_app, "active_tool", "PTR")

        if active_tool == "PTR":
            if self.clicked_already_selected and not self.did_drag and not self.active_handle:
                selected = getattr(master_app, "selected_brush", None)
                if selected and self.is_volumetric_item(selected):
                    mode = getattr(master_app, "transform_mode", "scale")
                    master_app.transform_mode = "rotate" if mode == "scale" else "scale"
                    for vp in master_app.viewports:
                        vp.draw_grid()
            self.dragging_brush = None
            self.active_handle = None
            self.clicked_already_selected = False
            self.did_drag = False
        elif active_tool == "BLK":
            if self.current_rect:
                self.delete(self.current_rect)
                self.current_rect = None

            wx, wy = self.screen_to_world(event.x, event.y)
            end_x = round(wx / self.grid_size) * self.grid_size
            end_y = round(wy / self.grid_size) * self.grid_size

            x1 = min(self.drawing_start_x, end_x)
            y1 = min(self.drawing_start_y, end_y)
            x2 = max(self.drawing_start_x, end_x)
            y2 = max(self.drawing_start_y, end_y)

            size_a = max(x2 - x1, self.grid_size)
            size_b = max(y2 - y1, self.grid_size)

            center_a = x1 + size_a / 2
            center_b = y1 + size_b / 2

            default_geom = master_app.app_settings.get("default_geometry", "geom_static")

            if self.view_type == "2d top":
                pos = [center_a, 0.0, center_b]
                size = [size_a, 1.0, size_b]
            elif self.view_type == "2d front":
                pos = [center_a, center_b, 0.0]
                size = [size_a, size_b, 1.0]
            else:
                pos = [0.0, center_b, center_a]
                size = [1.0, size_b, size_a]

            if hasattr(master_app, "save_history_state"):
                master_app.save_history_state()
            if hasattr(master_app, "add_workspace_brush"):
                master_app.add_workspace_brush(default_geom, pos, size)

    def increase_grid(self, event=None):
        if self.grid_size < 256:
            self.grid_size *= 2
            self.draw_grid()
            if self.on_hover_callback:
                self.on_hover_callback(self.grid_size, self.view_type)

    def decrease_grid(self, event=None):
        if self.grid_size > 1:
            self.grid_size //= 2
            self.draw_grid()
            if self.on_hover_callback:
                self.on_hover_callback(self.grid_size, self.view_type)

    def center_view(self, event=None):
        self.pan_x = self.winfo_width() / 2
        self.pan_y = self.winfo_height() / 2
        self.draw_grid()

    def update_theme(self, new_colors):
        self.colors = new_colors
        self.configure(bg=new_colors["bg"])
        self.draw_grid()