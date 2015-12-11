from query import Query
from information_retrieval import IR
from prettytable import PrettyTable
import time
import datetime

def _print(k, documents):
    t = PrettyTable(['DOC #','DOC ID','DOC TITLE'])
    t.align["DOC TITLE"] = "l"
    for i in range(k,min(k+10,len(documents))):
        t.add_row([str(i+1),str(documents[i].id),documents[i].title])
    print t
        # print str(i+1) + ". [FILEID=" + str(documents[i].id) + "] " + documents[i].title

def _help():
    print '======================= User  Manual ======================='
    print '= Types of queries supported:                              ='
    print '=     -> unquoted words, e.g. professional builders        ='
    print '=     -> quoted phrase, e.g. "cocoa zone"                  ='
    print '=     -> negated words, e.g. professional -builders        ='
    print '=     -> combinations of the options above                 ='
    print '============================================================'

def main():
    print "Loading index..."
    start = time.time()
    ir = IR()
    done = time.time()
    elapsed = done - start
    print "Index loaded in "+str(elapsed)+" seconds"
    print "\n============================================================"
    print "======================== IR Machine ========================"
    print "============================================================"
    print "= A IR tool to query over the Reuters database.            ="
    print "= More details about the database at http://bit.ly/1F8AFcO ="
    print "= Source code avaliable at http://bit.ly/1mezIcN           ="
    print "= Authors:                                                 ="
    print "=     @Joao Gabriel Santiago Mauricio de Abreu             ="
    print "=     @Natalia Paola de Vasconcelos Cometti                ="
    print "=     @Victor Felix Pimenta                                ="
    print "= Since: 12/11/2015                                        ="
    print "============================================================\n"
    quit = False
    while not quit:
        k = 0
        input_ = raw_input("Type your query ('q' to quit, 'h' to help): ")
        if input_ == 'q':
            break
        elif input_ == 'h':
            _help()
            continue
        query = Query(input_)
        start = time.time()
        documents = ir.search(query)
        done = time.time()
        elapsed = done - start
        if len(documents) > 0:
            print "\n"+str(len(documents))+" results found in "+str(elapsed)+" seconds:\n"
            _print(k, documents)

            while True:
                opt = raw_input("============================================================\n"
                    +"Type:\n"
                    +" '+' -> more results\n"
                    +" <DOC#> -> print content\n"
                    +" 'e' -> export all results to a file\n"
                    +" 'r' -> query again\n"
                    +" 'q' -> quit\n"
                    +" 'h' -> help\n"
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
                elif opt == 'h':
                    _help()
                else:
                    try:
                        idx = int(opt)
                        if idx > 0 and idx <= (k+10):
                            print documents[int(opt)-1].fancy_str()
                        else:
                            print "Error: Document number out of bounds!"
                    except ValueError:
                        print "Error: Invalid input!"

        else:
            print "No results found for '"+input_+"'"

main()