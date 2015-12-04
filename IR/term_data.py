class TermData:
	def __init__(self, frequency = 0, posting_list = []):
		self.frequency = frequency
		self.posting_list = posting_list

class Posting:
	def __init__(self, doc_id, positions = []):
		self.doc_id = doc_id
		self.positions = positions