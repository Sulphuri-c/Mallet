import json
from core.proxies import ensure_class_uuid


class MalletCompiler:
    def __init__(self):
        self.payload = {
            "version": "1.2",
            "world": {
                "clock_time": "14.5",
                "gravity": "196.2",
                "max_players": "16",
                "enable_atmosphere": True,
                "atmosphere_density": "0.3"
            },
            "geometry": [],
            "proxies": []
        }

    def set_world_settings(self, world_dict):
        if world_dict:
            self.payload["world"].update(world_dict)

    def add_element(self, uuid_str, mallet_id, elem_type, category, pos, size, rot, material, attributes, io_list,
                    parent):
        transparency = float(attributes.get("transparency", 0.0))

        element_data = {
            "uuid": uuid_str,
            "mallet_id": mallet_id,
            "type": elem_type,
            "category": category,
            "pos": pos,
            "size": size,
            "rot": rot,
            "material": material,
            "transparency": transparency,
            "attributes": attributes,
            "io": io_list,
            "parent": parent
        }
        self.elements.append(element_data)

    def get_json_string(self):
        return json.dumps(self.payload, indent=4)

    def export_micheal_file(self, filepath):
        with open(filepath, "w") as f:
            f.write(self.get_json_string())

    def import_micheal_file(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
            world = data.get("world", {})
            geom = data.get("geometry", [])
            proxies = data.get("proxies", [])
            for item in geom + proxies:
                item["uuid"] = ensure_class_uuid(item.get("uuid"), item.get("type", "geom_static"))
                if "mallet_id" not in item:
                    item["mallet_id"] = ""
                if "parent" not in item:
                    item["parent"] = "workspace"
                if "io" not in item:
                    item["io"] = []
            return geom, proxies, world