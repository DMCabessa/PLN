from file_handler import init_inverted_index
from query import Query

class IR:
	def __init__(self):
		self.inverted_index = init_inverted_index()

	def search(query):
		#1 TODO: busca binária para cada trecho quoted
		#2 TODO: busca ranqueada do passo anterior