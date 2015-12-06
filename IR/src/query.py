import nltk

class Query:
	def __init__(self,query):
		self.unquoted_words = []
		self.quoted_sentences = []
		self.negated_words = []

		subqueries = query.split('"')
		if len(subqueries) > 1 and not len(subqueries)%2 == 0:
			for i in range(0,len(subqueries)):
				if len(subqueries[i]) == 0:
					continue
				if i%2 == 0:
					self.unquoted_words += nltk.word_tokenize(subqueries[i])
				else:
					self.quoted_sentences.append(subqueries[i])
		else:
			self.unquoted_words += nltk.word_tokenize(" ".join(subqueries))

		for word in self.unquoted_words:
			if word[0] == '-':
				if len(word) > 1:
					self.negated_words.append(word[1:len(word)])
				self.unquoted_words.remove(word)