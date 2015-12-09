class Posting:
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.positions = list()

    def __str__(self):
        return str(self.doc_id) + ':' + str(self.positions)

    def __cmp__(self, other):
        return self.doc_id - other.doc_id

    def __int__(self):
        return self.doc_id