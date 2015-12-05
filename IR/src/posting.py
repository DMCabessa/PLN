class Posting:
    def __init__(self, doc_id, positions = list()):
        self.doc_id = doc_id
        self.positions = positions

    def __str__(self):
        return str(self.doc_id) + ':' + str(self.positions)