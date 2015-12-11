from information_retrieval import IR
from query import Query

def read_queries(filename):
	in_ = open(filename, 'r')
	queries = in_.read()
	queries = queries.split("\n")

	ir = IR()

	for query in queries:
		target_doc_id = int(query[0 : query.index(' ')])
		q = Query(query[query.index(' ')+1 : len(query)])
		
		rank = -1
		documents = ir.search(q)
		for i in range(0, len(documents)):
			if documents[i].id == target_doc_id:
				rank = i
				break
		documents = documents[0:15]
		
		divider = '\n==============================================================================\n'
		out_ = open('../tests/'+ query +'.txt', 'w')

		result = ('target document is rank ' + str(rank + 1) + divider + 
			divider.join(['DOC ID:\n\t' + str(doc.id) + '\n' + doc.fancy_str() for (doc, r) in zip(documents, range(1, len(documents)+1))]))
		result += '\n\n\n'
		out_.write(result)
		out_.close()

	in_.close()

