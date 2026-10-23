import json
from core.proxies import ensure_class_uuid

class MalletCompiler:
    def __init__(self):
        self.payload = {
            "version": "1.1",
            "geometry": [],
            "proxies": []
        }

    def add_element(self, element_uuid, mallet_id, element_type, category, pos, size, rot=None, material="SmoothPlastic", attributes=None, io_connections=None):
        item = {
            "uuid": ensure_class_uuid(element_uuid, element_type),
            "mallet_id": mallet_id if mallet_id is not None else "",
            "type": element_type,
            "pos": pos,
            "size": size,
            "rot": rot or [0.0, 0.0, 0.0],
            "material": material,
            "attributes": attributes or {},
            "io": io_connections or []
        }
        if category == "geometry":
            self.payload["geometry"].append(item)
        else:
            self.payload["proxies"].append(item)

    def get_json_string(self):
        return json.dumps(self.payload, indent=4)

    def export_micheal_file(self, filepath):
        with open(filepath, "w") as f:
            f.write(self.get_json_string())

    def import_micheal_file(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
            geom = data.get("geometry", [])
            proxies = data.get("proxies", [])
            for item in geom + proxies:
                item["uuid"] = ensure_class_uuid(item.get("uuid"), item.get("type", "geom_static"))
                if "mallet_id" not in item:
                    item["mallet_id"] = ""
                if "io" not in item:
                    item["io"] = []
            return geom, proxies