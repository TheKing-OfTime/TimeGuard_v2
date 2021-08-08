from dataclasses import dataclass

@dataclass
class Guild:
    id:             int = None
    name:           str = None
    mode:           int = None
    mute_role_id:   int = None
    lang:           str = None
    flags:          int = None