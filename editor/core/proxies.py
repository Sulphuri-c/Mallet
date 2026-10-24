import os
import uuid

try:
    from PIL import Image
    import customtkinter as ctk

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "icons")

PROXY_REGISTRY = {
    "geom_static": {
        "category": "geometry",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": None,
        "attributes": {
            "material": {"type": "material", "default": "Concrete"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "transparency": {"type": "float", "default": "0.0"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"}
        },
        "inputs": [],
        "outputs": {}
    },
    "geom_dynamic": {
        "category": "geometry",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": None,
        "attributes": {
            "material": {"type": "material", "default": "Limestone"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "transparency": {"type": "float", "default": "0.0"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["Enable", "Disable", "Toggle", "SetMaterial", "SetColor", "Destroy"],
        "outputs": {
            "OnCollidedWith": "!collider",
            "OnDestroyed": "!destroyer"
        }
    },
    "geom_dambrick": {
        "category": "geometry",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": None,
        "attributes": {
            "material": {"type": "material", "default": "Concrete"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "transparency": {"type": "float", "default": "0.0"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"},
            "damage": {"type": "float", "default": "10"},
            "refire_interval": {"type": "float", "default": "1"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["Enable", "Disable", "SetDamage"],
        "outputs": {
            "OnCollidedWith": "!collider",
            "OnHurtPlayer": "!victim"
        }
    },
    "geom_log_trigger": {
        "category": "geometry",
        "default_size": [6.0, 6.0, 6.0],
        "has_texture": True,
        "editor_texture": "trigger",
        "icon": None,
        "attributes": {
            "only_once": {"type": "bool", "default": "false"},
            "players_allowed": {"type": "bool", "default": "true"},
            "objects_allowed": {"type": "bool", "default": "true"},
            "npcs_allowed": {"type": "bool", "default": "true"},
            "transparency": {"type": "float", "default": "0.0"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["Enable", "Disable", "Toggle"],
        "outputs": {
            "OnStartTouch": "!toucher",
            "OnEndTouch": "!toucher",
            "OnTrigger": "!activator"
        }
    },

    "msh_static": {
        "category": "proxy",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": "msh_static.png",
        "attributes": {
            "mesh_filepath": {"type": "filepath", "default": ""},
            "material": {"type": "material", "default": "SmoothPlastic"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"}
        },
        "inputs": [],
        "outputs": {}
    },
    "msh_dynamic": {
        "category": "proxy",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": "msh_dynamic.png",
        "attributes": {
            "mesh_filepath": {"type": "filepath", "default": ""},
            "default_anim": {"type": "string", "default": ""},
            "material": {"type": "material", "default": "SmoothPlastic"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"},
            "start_enabled": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": [
            "Enable", "Disable", "Toggle", "SetMaterial", "SetColor",
            "PlayAnimation", "StopAnimation", "Destroy"
        ],
        "outputs": {
            "OnCollidedWith": "!collider",
            "OnAnimFinished": "!anim_name",
            "OnDestroyed": "!destroyer"
        }
    },
    "msh_physics": {
        "category": "proxy",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": "msh_physics.png",
        "attributes": {
            "mesh_filepath": {"type": "filepath", "default": ""},
            "collision_filepath": {"type": "filepath", "default": ""},
            "material": {"type": "material", "default": "SmoothPlastic"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"},
            "mass": {"type": "float", "default": "10.0"},
            "anchored": {"type": "bool", "default": "false"},
            "start_enabled": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": [
            "Enable", "Disable", "Toggle", "SetMaterial", "SetColor",
            "Wake", "Sleep", "ApplyImpulse", "Destroy"
        ],
        "outputs": {
            "OnCollidedWith": "!collider",
            "OnDamaged": "!attacker",
            "OnDestroyed": "!destroyer"
        }
    },
    "msh_deform": {
        "category": "proxy",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": "msh_deform.png",
        "attributes": {
            "mesh_filepath": {"type": "filepath", "default": ""},
            "material": {"type": "material", "default": "SmoothPlastic"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"},
            "deform_type": {"type": "string", "default": "softbody"},
            "stiffness": {"type": "float", "default": "0.5"},
            "damping": {"type": "float", "default": "0.1"},
            "plasticity": {"type": "float", "default": "0.2"},
            "start_enabled": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": [
            "Enable", "Disable", "Toggle", "SetMaterial", "SetColor",
            "DeformAtPoint", "PlayAnimation", "ResetMesh", "Destroy"
        ],
        "outputs": {
            "OnCollidedWith": "!collider",
            "OnDeformed": "!impact_force",
            "OnDestroyed": "!destroyer"
        }
    },
    "msh_physics_deform": {
        "category": "proxy",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": "msh_physics_deform.png",
        "attributes": {
            "mesh_filepath": {"type": "filepath", "default": ""},
            "collision_filepath": {"type": "filepath", "default": ""},
            "material": {"type": "material", "default": "SmoothPlastic"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"},
            "mass": {"type": "float", "default": "10.0"},
            "anchored": {"type": "bool", "default": "false"},
            "deform_type": {"type": "string", "default": "dent"},
            "stiffness": {"type": "float", "default": "0.5"},
            "damping": {"type": "float", "default": "0.1"},
            "plasticity": {"type": "float", "default": "0.2"},
            "start_enabled": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": [
            "Enable", "Disable", "Toggle", "SetMaterial", "SetColor",
            "Wake", "Sleep", "ApplyImpulse", "DeformAtPoint", "ResetMesh", "Destroy"
        ],
        "outputs": {
            "OnCollidedWith": "!collider",
            "OnDeformed": "!impact_force",
            "OnDamaged": "!attacker",
            "OnDestroyed": "!destroyer"
        }
    },

    "msh_id_static": {
        "category": "proxy",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": "msh_id_static.png",
        "attributes": {
            "mesh_id": {"type": "string", "default": "rbxassetid://"},
            "texture_id": {"type": "string", "default": "rbxassetid://"},
            "material": {"type": "material", "default": "SmoothPlastic"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"}
        },
        "inputs": [],
        "outputs": {}
    },
    "msh_id_dynamic": {
        "category": "proxy",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": "msh_id_dynamic.png",
        "attributes": {
            "mesh_id": {"type": "string", "default": "rbxassetid://"},
            "texture_id": {"type": "string", "default": "rbxassetid://"},
            "material": {"type": "material", "default": "SmoothPlastic"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"},
            "start_enabled": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": [
            "Enable", "Disable", "Toggle", "SetMaterial", "SetColor",
            "SetMeshId", "SetTextureId", "Destroy"
        ],
        "outputs": {
            "OnCollidedWith": "!collider",
            "OnDestroyed": "!destroyer"
        }
    },
    "msh_id_physics": {
        "category": "proxy",
        "default_size": [4.0, 4.0, 4.0],
        "has_texture": True,
        "icon": "msh_id_physics.png",
        "attributes": {
            "mesh_id": {"type": "string", "default": "rbxassetid://"},
            "texture_id": {"type": "string", "default": "rbxassetid://"},
            "collision_fidelity": {"type": "string", "default": "Default"},
            "material": {"type": "material", "default": "SmoothPlastic"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "can_collide": {"type": "bool", "default": "true"},
            "cast_shadow": {"type": "bool", "default": "true"},
            "mass": {"type": "float", "default": "10.0"},
            "anchored": {"type": "bool", "default": "false"},
            "start_enabled": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": [
            "Enable", "Disable", "Toggle", "SetMaterial", "SetColor",
            "Wake", "Sleep", "ApplyImpulse", "Destroy"
        ],
        "outputs": {
            "OnCollidedWith": "!collider",
            "OnDamaged": "!attacker",
            "OnDestroyed": "!destroyer"
        }
    },

    "wrd_player_start": {
        "category": "proxy",
        "default_size": [2.0, 4.0, 2.0],
        "has_texture": False,
        "icon": "wrd_player_start.png",
        "attributes": {
            "team": {"type": "string", "default": "Neutral"},
            "start_enabled": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["Enable", "Disable", "SetTeam", "TeleportPlayer"],
        "outputs": {
            "OnPlayerSpawn": "!player"
        }
    },
    "wrd_light": {
        "category": "proxy",
        "default_size": [1.0, 1.0, 1.0],
        "has_texture": False,
        "icon": "wrd_light.png",
        "attributes": {
            "brightness": {"type": "float", "default": "1.0"},
            "color": {"type": "color", "default": "#FFFFFF"},
            "range": {"type": "float", "default": "16.0"},
            "shadows": {"type": "bool", "default": "true"},
            "start_enabled": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["TurnOn", "TurnOff", "Toggle", "SetBrightness", "SetColor"],
        "outputs": {}
    },

    "log_timer": {
        "category": "proxy",
        "default_size": [1.0, 1.0, 1.0],
        "has_texture": False,
        "icon": "log_timer.png",
        "attributes": {
            "refire_interval_max": {"type": "float", "default": "2"},
            "refire_interval_min": {"type": "float", "default": "1"},
            "start_enabled": {"type": "bool", "default": "true"},
            "use_random_time": {"type": "bool", "default": "false"},
            "oscilate": {"type": "bool", "default": "false"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["Enable", "Disable", "Toggle", "ResetTimer", "FireTimer"],
        "outputs": {
            "OnTimer": "!interval",
            "OnTimerHigh": "!interval",
            "OnTimerLow": "!interval"
        }
    },
    "log_relay": {
        "category": "proxy",
        "default_size": [1.0, 1.0, 1.0],
        "has_texture": False,
        "icon": "log_relay.png",
        "attributes": {
            "start_enabled": {"type": "bool", "default": "true"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["Trigger", "Enable", "Disable", "Toggle"],
        "outputs": {
            "OnTrigger": "!payload"
        }
    },

    "fx_particle": {
        "category": "proxy",
        "default_size": [1.0, 1.0, 1.0],
        "has_texture": False,
        "icon": "fx_particle.png",
        "attributes": {
            "start_enabled": {"type": "bool", "default": "true"},
            "particle_type": {"type": "string", "default": ""},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["Start", "Stop", "Emit"],
        "outputs": {}
    },

    "sfx_regular": {
        "category": "proxy",
        "default_size": [1.0, 1.0, 1.0],
        "has_texture": False,
        "icon": "sfx_regular.png",
        "attributes": {
            "start_enabled": {"type": "bool", "default": "true"},
            "sound_filepath": {"type": "filepath", "default": ""},
            "looped": {"type": "bool", "default": "false"},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["PlaySound", "StopSound", "ToggleSound"],
        "outputs": {
            "OnSoundFinished": "!self"
        }
    },
    "sfx_oneshot": {
        "category": "proxy",
        "default_size": [1.0, 1.0, 1.0],
        "has_texture": False,
        "icon": "sfx_oneshot.png",
        "attributes": {
            "start_enabled": {"type": "bool", "default": "true"},
            "sound_filepath": {"type": "filepath", "default": ""},
            "mallet_id": {"type": "string", "default": ""}
        },
        "inputs": ["PlaySound"],
        "outputs": {
            "OnSoundFinished": "!self"
        }
    }
}


def generate_element_uuid(proxy_type):
    short_hex = uuid.uuid4().hex[:8]
    return f"{proxy_type}-{short_hex}"


def ensure_class_uuid(current_uuid, proxy_type):
    if not current_uuid or "-" not in current_uuid:
        return generate_element_uuid(proxy_type)
    suffix = current_uuid.split("-")[-1]
    return f"{proxy_type}-{suffix}"


def get_proxy_definition(proxy_type):
    return PROXY_REGISTRY.get(proxy_type, {})


def get_all_proxy_types():
    return list(PROXY_REGISTRY.keys())


def get_proxy_types_by_category(category):
    return [k for k, v in PROXY_REGISTRY.items() if v.get("category") == category]


def get_proxy_inputs(proxy_type):
    return get_proxy_definition(proxy_type).get("inputs", [])


def get_proxy_outputs(proxy_type):
    outputs = get_proxy_definition(proxy_type).get("outputs", {})
    if isinstance(outputs, dict):
        return list(outputs.keys())
    return list(outputs)


def get_output_payload(proxy_type, output_name):
    outputs = get_proxy_definition(proxy_type).get("outputs", {})
    if isinstance(outputs, dict):
        return outputs.get(output_name, "!payload")
    return "!payload"


def load_proxy_icon(key_or_filename):
    if not PIL_AVAILABLE or not key_or_filename:
        return None

    definition = get_proxy_definition(key_or_filename)
    icon_filename = definition.get("icon") if definition else key_or_filename
    if not icon_filename:
        return None

    path = os.path.join(ASSET_DIR, icon_filename)
    if os.path.exists(path):
        pil_image = Image.open(path)
        return ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(32, 32))
    return None