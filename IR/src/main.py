from query import Query
from information_retrieval import IR
import time
import datetime

def _print(k, documents):
    for i in range(k,min(k+10,len(documents))):
        print str(i+1) + ". [FILEID=" + str(documents[i].id) + "] " + documents[i].title

def main():
    print "============================================================\n"
    print "======================== IR Machine ========================\n"
    print "============================================================\n"
    quit = False
    while not quit:
        k = 0
        input_ = raw_input("Type your query ('q' to quit): ")
        if input_ == 'q':
            break
        query = Query(input_)
        ir = IR()
        documents = ir.search(query)
        if len(documents) > 0:
            print "\nResults:\n"
            _print(k, documents)

            while True:
                opt = raw_input("============================================================\n"
                    +"Type:\n"
                    +" '+' -> more results.\n"
                    +" <DOC#> -> print content.\n"
                    +" 'e' -> export all results to a file.\n"
                    +" 'r' -> query again.\n"
                    +" 'q' -> quit\n"
                    +"============================================================\n")
                if opt == '+':
                    k+=10
                    _print(k, documents)
                elif opt == 'e':
                    f = open("../dump/"+input_+" ("+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')+").txt", 'w')
                    result = '\n==============================================================================\n'.join([doc.fancy_str() for doc in documents])
                    result += '\n\n\n'
                    f.write(result)
                    f.close()
                elif opt == 'r':
                    break
                elif opt == 'q':
                    quit = True
                    break
                else:
                    print documents[int(opt)-1].fancy_str()
        else:
            print "No results found for '"+input_+"'"

main()