from query import Query
from information_retrieval import IR

k = 10

_input = raw_input("Type your query... ")
query = Query(_input)
ir = IR()
documents = ir.search(query)
print "\nResults:\n"
for i in range(0,min(k,len(documents)))
	print i + ". " + documents[i].title