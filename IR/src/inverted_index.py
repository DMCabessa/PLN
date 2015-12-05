class InvertedIndex:
    def __init__(self):
        self.table = {}
        self.n = 0

    def __getitem__(self, index):
        return self.table[index]

    def __setitem__(self, key, value):
        self.table[key] = value

    def __iter__(self):
        return iter(self.table)

    def keys(self):
        return self.table.keys()