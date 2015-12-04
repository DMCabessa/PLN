from file_handler import init_inverted_index
from term_data import Posting
from query import Query
from math import log

class IR:
	def __init__(self):
		self.inverted_index = init_inverted_index()

	def term_tfs(term):
		doc_tfs = []
		doc_id = 1
		for posting in self.inverted_index[term]:
			while posting.doc_id > doc_id:
				doc_tfs.append(0)
				doc_id += 1
			current_tf = 1 + log(len(posting.positions))
			doc_tfs.append(current_tf)
		return doc_tfs

	def term_idf(term):
		# TODO: this method

	def search(query):
		# TODO: busca binária para cada trecho quoted
		# TODO: busca ranqueada do passo anterior