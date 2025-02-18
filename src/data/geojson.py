import json
import dataclasses

from src.data.data import BEATIFY_OUTPUT

@dataclasses.dataclass
class GeoJson:
    type: str
    geometry: dict

    def __str__(self):
        indent = 2 if BEATIFY_OUTPUT else None
        return json.dumps(dataclasses.asdict(self), indent=indent)
