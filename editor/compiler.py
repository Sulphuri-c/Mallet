import json


class MalletCompiler:
    def __init__(self):
        self.level_data = {
            "version": "1.0",
            "metadata": {
                "author": "mallet_user",
                "engine": "mallet_v1"
            },
            "geometry": [],
            "logic": [],
            "world": []
        }

    def add_proxy(self, category, proxy_type, pos, size, material="Concrete"):
        proxy_entry = {
            "type": proxy_type,
            "pos": [float(pos[0]), float(pos[1]), float(pos[2])],
            "size": [float(size[0]), float(size[1]), float(size[2])],
            "material": material
        }

        if category in self.level_data:
            self.level_data[category].append(proxy_entry)
        else:
            raise ValueError(f"Invalid category: {category}")

    def export_micheal_file(self, filepath):
        try:
            with open(filepath, "w") as f:
                json.dump(self.level_data, f, indent=4)
            print(f"Compiled map to {filepath}")
        except Exception as e:
            print(f"Compile failed: {e}")

    def get_json_string(self):
        return json.dumps(self.level_data)