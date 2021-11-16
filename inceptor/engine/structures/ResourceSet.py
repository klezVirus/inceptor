from engine.structures.Resource import Resource


class ResourceSet:
    def __init__(self):
        self.memory = []

    def is_empty(self):
        return len(self.memory) == 0

    def append(self, value):
        if isinstance(value, Resource):
            self.memory.append(value)
        elif isinstance(value, ResourceSet):
            for res in value.memory:
                self.memory.append(res)
