from bs4 import BeautifulSoup
from document import Document
from term_data import *
import cPickle
import nltk

PATH = "database/"

def serialize(document, filename):
    f = open(PATH+filename, 'wb')
    cPickle.dump(document, f, cPickle.HIGHEST_PROTOCOL)

def deserialize(filename):
    f = open(PATH+filename, 'rb')
    return cPickle.load(f)

def pre_process():
    for i in range(0,22):
        filename = "source-documents/reut2-0" + ("0" if i < 10 else "") + str(i) + ".sgm"
        f = open(filename)
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
        reuters = soup.findAll('reuters')
        for reuter in reuters:
            document = Document(reuter)
            serialize(document, document.id+".dbf")

def init_inverted_index():
    idx = 1
    doc_list = []
    inverted_index = {}

    while True:
        try:
            document = deserialize(str(idx)+".dbf")
            doc_list.append(document)
            idx  += 1;
        except IOError:
            break

    total = len(doc_list)
    for document in doc_list:
        tokens = nltk.word_tokenize(str(document))
        for pos in range(0,len(tokens)):
            tk = tokens[pos]
            if not tk in inverted_index.keys():
                inverted_index[tk] = TermData()
            
            term_data = inverted_index[tk]
            if not document.id in map(lambda p: p.doc_id, term_data.posting_list):
                term_data.frequency += 1
                term_data.posting_list.append(Posting(document.id))

            for posting in term_data.posting_list:
                if posting.doc_id == document.id:
                    posting.positions.append(pos)
                    break
        print "{0:.2f}% completed...".format(float(document.id)/total * 100)

    serialize(inverted_index,"inverted_index.idx")