from dataclasses import dataclass

@dataclass
class ExportLimits:
    soft_limit:int
    hard_limit:int
    network_mode:str
