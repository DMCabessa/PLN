from bs4 import BeautifulSoup,SoupStrainer
from prettytable import PrettyTable
from random import shuffle
import nltk

def readFiles():
    document_ids = {}

    for i in range(0,22):
        filename = "Naive Bayes/documents/reut2-0" + ("0" if i < 10 else "") + str(i) + ".sgm"
        f = open(filename)
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
        reuters = soup.findAll('reuters')
        for reuter in reuters:
            topics = reuter.find('topics')
            ds = topics.findAll('d')
            if len(ds) > 0:
                # Increase the document count for every relevant topic counter
                for d in ds:
                    if not document_ids.has_key(d.text):
                        document_ids[d.text] = []
                    document_ids[d.text].append(int(reuter['newid']))

    return document_ids

def makeShuffle(documents):
    sorted_ = [key.encode('utf-8') for key in sorted(documents.keys(), key=lambda d: -len(documents[d]))]
    sorted_10 = sorted_[0:10]
    
    for topic in filter(lambda t: not t in sorted_10, documents.keys()):
        del documents[topic]

    for topic in documents:
        shuffle(documents[topic])

    return_ = {}
    for topic in documents:
        return_[topic] = documents[topic][0:10]

    # return return_
    
    t = PrettyTable(['TOPIC'] + range(1, 11))
    for topic in documents:
        t.add_row([topic.upper()] + documents[topic][0:10])
    print t