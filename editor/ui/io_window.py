import customtkinter as ctk
from core.proxies import get_proxy_inputs, get_proxy_outputs, get_output_payload, PROXY_REGISTRY
from core.proxies import load_proxy_icon, get_proxy_definition, generate_element_uuid, ensure_class_uuid
from ui.properties_panel import AutocompleteComboBox

BASE_PARAMS = ["!payload", "!self", "!player", "!activator", "!caller"]


class IOWindow(ctk.CTkToplevel):
    def __init__(self, master, target_item, on_save_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.master_app = master
        self.target_item = target_item
        self.on_save_callback = on_save_callback
        self.connections = [dict(c) for c in target_item.get("io", [])]

        self.title(f"Entity I/O Connections - {target_item.get('mallet_id') or target_item.get('uuid')}")
        self.geometry("820x450")
        self.configure(fg_color="#222222")

        self.transient(master)
        self.lift()
        self.focus_force()

        self.header = ctk.CTkLabel(
            self,
            text="Input/Output & Payload Wiring",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#AE79F0"
        )
        self.header.pack(pady=(10, 5))

        col_header = ctk.CTkFrame(self, fg_color="transparent")
        col_header.pack(fill="x", padx=15, pady=(5, 0))
        headers = [
            ("Output", 150),
            ("Target (mallet_id)", 150),
            ("Input", 150),
            ("Payload / Param", 160),
            ("Delay", 60)
        ]
        for text, w in headers:
            ctk.CTkLabel(col_header, text=text, width=w, anchor="w", text_color="#AE79F0",
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#4A4A4A", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.rebuild_rows()

        self.add_btn = ctk.CTkButton(
            self,
            text="Add Connection",
            fg_color="#7514ED",
            text_color="#EEEEEE",
            hover_color="#500AA6",
            command=self.add_connection_row
        )
        self.add_btn.pack(pady=5, padx=10, fill="x")

        self.save_btn = ctk.CTkButton(
            self,
            text="Save & Close",
            fg_color="#7514ED",
            text_color="#EEEEEE",
            hover_color="#500AA6",
            font=ctk.CTkFont(weight="bold"),
            command=self.save_and_close
        )
        self.save_btn.pack(pady=(0, 10), padx=10, fill="x")

    def get_workspace_targets(self):
        targets = {}
        brushes = getattr(self.master_app, "workspace_brushes", [])
        proxies = getattr(self.master_app, "workspace_proxies", [])
        for item in brushes + proxies:
            mid = item.get("mallet_id", "").strip()
            if not mid and "attributes" in item:
                mid = item["attributes"].get("mallet_id", "").strip()
            if mid:
                targets[mid] = item.get("type", "")
        return targets

    def get_all_possible_inputs(self):
        all_inputs = set()
        for data in PROXY_REGISTRY.values():
            for inp in data.get("inputs", []):
                all_inputs.add(inp)
        return sorted(list(all_inputs))

    def get_param_options_for_output(self, my_type, output_name, target_names):
        specific_payload = get_output_payload(my_type, output_name)
        options = []
        if specific_payload:
            options.append(specific_payload)
        for p in BASE_PARAMS:
            if p not in options:
                options.append(p)
        return options + target_names

    def rebuild_rows(self):
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        my_type = self.target_item.get("type", "")
        available_outputs = get_proxy_outputs(my_type) or ["OnTrigger"]
        workspace_targets = self.get_workspace_targets()
        target_names = sorted(list(workspace_targets.keys()))
        all_inputs = self.get_all_possible_inputs()

        for idx, conn in enumerate(self.connections):
            row = ctk.CTkFrame(self.scroll_frame, fg_color="#222222")
            row.pack(fill="x", pady=4, padx=5)

            current_out = conn.get("output", available_outputs[0])
            param_options = self.get_param_options_for_output(my_type, current_out, target_names)

            param_box = AutocompleteComboBox(
                row,
                options=param_options,
                default_val=conn.get("param", param_options[0] if param_options else ""),
                width=160
            )

            def on_output_selected(selected_out, p_widget=param_box):
                new_opts = self.get_param_options_for_output(my_type, selected_out, target_names)
                p_widget.set_options(new_opts)
                expected_payload = get_output_payload(my_type, selected_out)
                if not p_widget.get() or p_widget.get().startswith("!"):
                    p_widget.set(expected_payload)

            out_box = AutocompleteComboBox(
                row,
                options=available_outputs,
                default_val=current_out,
                on_select_callback=on_output_selected,
                width=150
            )
            out_box.pack(side="left", padx=4, pady=5)

            current_target = conn.get("target", "")
            target_type = workspace_targets.get(current_target, "")
            initial_inputs = get_proxy_inputs(target_type) if target_type else all_inputs
            if not initial_inputs:
                initial_inputs = all_inputs

            inp_box = AutocompleteComboBox(
                row,
                options=initial_inputs,
                default_val=conn.get("input", initial_inputs[0] if initial_inputs else "Enable"),
                width=150
            )

            def on_target_selected(selected_target, input_widget=inp_box):
                t_type = self.get_workspace_targets().get(selected_target, "")
                valid_inps = get_proxy_inputs(t_type) if t_type else self.get_all_possible_inputs()
                if valid_inps:
                    input_widget.set_options(valid_inps)
                    if input_widget.get() not in valid_inps:
                        input_widget.set(valid_inps[0])

            target_box = AutocompleteComboBox(
                row,
                options=target_names,
                default_val=current_target,
                on_select_callback=on_target_selected,
                width=150
            )
            target_box.pack(side="left", padx=4, pady=5)
            inp_box.pack(side="left", padx=4, pady=5)
            param_box.pack(side="left", padx=4, pady=5)

            delay_entry = ctk.CTkEntry(row, width=60, fg_color="#4A4A4A", text_color="#EEEEEE")
            delay_entry.insert(0, str(conn.get("delay", "0.0")))
            delay_entry.pack(side="left", padx=4, pady=5)

            del_btn = ctk.CTkButton(
                row,
                text="X",
                width=30,
                fg_color="#7C0000",
                hover_color="#A00000",
                command=lambda i=idx: self.delete_connection(i)
            )
            del_btn.pack(side="right", padx=4, pady=5)

            conn["_widgets"] = (out_box, target_box, inp_box, param_box, delay_entry)

    def add_connection_row(self):
        self.sync_widgets_to_connections()
        my_type = self.target_item.get("type", "")
        my_outputs = get_proxy_outputs(my_type)
        default_out = my_outputs[0] if my_outputs else "OnTrigger"
        default_payload = get_output_payload(my_type, default_out)
        self.connections.append({
            "output": default_out,
            "target": "",
            "input": "Enable",
            "param": default_payload,
            "delay": "0.0"
        })
        self.rebuild_rows()

    def delete_connection(self, index):
        self.sync_widgets_to_connections()
        self.connections.pop(index)
        self.rebuild_rows()

    def sync_widgets_to_connections(self):
        for conn in self.connections:
            if "_widgets" in conn:
                out_b, tar_b, inp_b, par_b, del_e = conn["_widgets"]
                conn["output"] = out_b.get()
                conn["target"] = tar_b.get()
                conn["input"] = inp_b.get()
                conn["param"] = par_b.get()
                conn["delay"] = del_e.get().strip()

    def save_and_close(self):
        self.sync_widgets_to_connections()
        updated_io = []
        for conn in self.connections:
            updated_io.append({
                "output": conn.get("output", ""),
                "target": conn.get("target", ""),
                "input": conn.get("input", ""),
                "param": conn.get("param", ""),
                "delay": conn.get("delay", "0.0")
            })
        self.on_save_callback(updated_io)
        self.destroy()