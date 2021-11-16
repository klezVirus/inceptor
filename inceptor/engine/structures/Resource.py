from pathlib import Path

from engine.structures.enums.ResourceType import ResourceType


class Resource:
    def __init__(self, resource_type: ResourceType, path: Path):
        self.resource_type = resource_type
        self.path = path
