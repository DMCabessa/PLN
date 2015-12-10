from query import Query
from information_retrieval import IR

k = 10

def main():
	input_ = raw_input("Type your query... ")
	query = Query(input_)
	ir = IR()
	documents = ir.search(query)
	if len(documents) > 0:
		print "\nResults:\n"
		for i in range(0,min(k,len(documents))):
			print str(i+1) + ". [" + str(documents[i].id) + "]" + documents[i].title
	else:
		print "No results found for '"+input_+"'"