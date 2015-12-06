class Posting:
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.positions = list()

    def __str__(self):
        return str(self.doc_id) + ':' + str(self.positions)