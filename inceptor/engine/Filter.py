class Filter:
    def __init__(self, include: list = None, exclude: list = None, imode="or", emode="and"):
        self.include = include if include else []
        self.exclude = exclude if exclude else []
        self.imode = imode.lower()
        self.emode = emode.lower()

    def match(self, target):
        match_include = match_exclude = True
        if self.include and len(self.include) > 0:
            if self.imode == "or":
                match_include = any([target.find(s) >= 0 for s in self.include])
            elif self.imode == "and":
                match_include = all([target.find(s) >= 0 for s in self.include])
        if self.exclude and len(self.exclude) > 0:
            if self.emode == "or":
                match_exclude = any([target.find(s) == -1 for s in self.exclude])
            elif self.emode == "and":
                match_exclude = all([target.find(s) == -1 for s in self.exclude])
        return match_include and match_exclude

    def to_string(self):
        print(f"Include: {','.join(self.include)}, Mode: {self.imode}")
        print(f"Exclude: {','.join(self.exclude)}, Mode: {self.emode}")
