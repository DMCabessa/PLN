from file_handler import deserialize, PATH
from posting import Posting
from query import Query
from math import log
from copy import deepcopy
from nltk import word_tokenize

class IR:
    def __init__(self):
        self.inverted_index = deserialize(PATH+'inverted_index.idx')
        self.docs = {}
        idx = 1
        while True:
            try:
                document = deserialize(str(idx)+".dbf")
                self.docs[document.id] = document
                idx  += 1;
            except IOError:
                break

    def term_tfs(self, term):
        doc_tfs = list()
        for posting in self.inverted_index[term]:
            # Adds 0s for the tfs of documents which do not contain term
            missing_docs = int(posting.doc_id) - len(doc_tfs)
            doc_tfs.extend([0] * missing_docs)
            # Compute the tf and add it
            current_tf = 1 + log(len(posting.positions))
            doc_tfs.append(current_tf)
        # Adds 0s for the remaining documents which do not contain term
        missing_docs = self.inverted_index.n - (len(doc_tfs) - 1)
        doc_tfs.extend([0] * missing_docs)
        return doc_tfs

    def term_idf(self, term):
        n_docs = len(self.inverted_index[term])
        return log(self.inverted_index.n/float(n_docs))

    def compute_scores(self, query):
        dic_tfs = {}
        dic_idfs = {}
        expanded_inv_idx = expand_inverted_index(query)
        for word in query.unquoted_words:
            if word not in dic_tfs.keys():
                dic_tfs[word] = term_tfs(word)
                dic_idfs[word] = term_idf(word)
        # TODO

    # Expands the inverted index table to contain the quoted sentences, each
    # considered as a single term
    def expand_inverted_index(self, query):
        expansion = {}
        inv_idx = self.inverted_index
        for sentence in query.quoted_sentences:
            sentence = word_tokenize(sentence)
            # Create a new term representing the sentence and add it to the expansion
            new_term = "_".join(sentence)
            expansion[new_term] = list()
            # Get the doc_ids in the lines for each term in the sentence
            term_lines = [[posting.doc_id for posting in inv_idx[word]] for word in sentence]

            doc_id = 1
            while min(term_lines, key=len) != []:
                head_doc_ids = [term_line[0] for term_line in term_lines]
                min_fst_doc = min(head_doc_ids)
                max_fst_doc = max(head_doc_ids)

                if min_fst_doc == max_fst_doc:
                    # Create a new Posting for the document
                    new_posting = Posting(min_fst_doc)
                    # Get the document in lowercase
                    doc = word_tokenize(str(self.docs[min_fst_doc]).lower())

                    # Find all the occurances of the sentence's first word on the document
                    fst_word_occurances = list()
                    for posting in inv_idx[sentence[0]]:
                        if posting.doc_id == min_fst_doc:
                            fst_word_occurances.extend(posting.positions)
                            break
                    # Check if the occurances of the first word are occurances of
                    # the whose sentence. If so, add it to the new posting
                    for position in fst_word_occurances:
                        match = True
                        for i in range(0, len(sentence)):
                            match = match and (sentence[i] == doc[position+i])
                        if match:
                            new_posting.positions.append(position)
                    # If the new posting has occurances of the sentence, add it
                    # to the expansion
                    if len(new_posting.positions) > 0:
                        expansion[new_term].append(new_posting)
                    # Advances to the next document
                    for term_line in term_lines:
                        del term_line[0]
                else:
                    # Remove the smallest doc_id from all term_line heads
                    for term_line in term_lines:
                        if term_line[0] == min_fst_doc:
                            del term_line[0]
        return expansion

    def search(self, query):
        # TODO: busca binaria para cada trecho quoted
        # TODO: busca ranqueada do passo anterior
        return 0