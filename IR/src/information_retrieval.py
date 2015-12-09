from file_handler import deserialize, PATH
from posting import Posting
from query import Query
from math import log
from copy import deepcopy
from nltk import word_tokenize
from inverted_index import InvertedIndex

class IR:
    def __init__(self):
        self.inverted_index = deserialize(PATH+'inverted_index.idx')
        # self.docs = {}
        # idx = 1
        # while True:
        #     try:
        #         document = deserialize(str(idx)+".dbf")
        #         self.docs[document.id] = document
        #         idx  += 1;
        #     except IOError:
        #         break

    def _term_tfs(self, term, expanded_inv_idx, filtered_documents):
        doc_tfs = {}
        iterator = iter(filtered_documents)
        if filtered_documents == []:
            return doc_tfs

        if term in expanded_inv_idx:
            inverted_index = expanded_inv_idx
        else:
            inverted_index = self.inverted_index

        allowed_id = iterator.next()
        doc_tfs[allowed_id] = 0
        for posting in inverted_index[term]:
            if posting.doc_id == allowed_id:
                doc_tfs[allowed_id] = 1 + log(len(posting.positions))
            elif posting.doc_id > allowed_id:
                doc_tfs[allowed_id] = 0
                try:
                    allowed_id = iterator.next()
                    doc_tfs[allowed_id] = 0
                except StopIteration:
                    break

        for allowed_id in iterator:
            doc_tfs[allowed_id] = 0

        return doc_tfs


    def _term_idf(self, term, expanded_inv_idx):
        if term in expanded_inv_idx:
            n_docs = len(expanded_inv_idx[term])
        else:
            n_docs = len(self.inverted_index[term])
        return log(self.inverted_index.n/float(n_docs))

    # TODO
    def _compute_scores(self, unquoted_words, expanded_inv_idx, filtered_documents):
        terms = unquoted_words + expanded_inv_idx.keys()
        tfs = {}
        idfs = {}
        # Compute all tfs and idfs
        for term in terms:
            tfs[term] = self._term_tfs(term, expanded_inv_idx, filtered_documents)
            idfs[term] = _term_idf(term, expanded_inv_idx)
        # Compute the tf-idfs
        tf_idf = deepcopy(tfs)
        for term in terms:
            for doc_id in filtered_documents:
                tf_idf[term][doc_id] *= idfs[term]

        # TODO


    def _binary_search(self, quoted_sentences, negated_words, expanded_inv_idx, filtered_documents):
        self._expand_inverted_index(quoted_sentences, expanded_inv_idx)
        self._binary_merge(negated_words, expanded_inv_idx, filtered_documents)


    def _binary_merge(self, negated_words, expanded_inv_idx, filtered_documents):
        term_lines = [[posting.doc_id for posting in expanded_inv_idx[term]] 
            for term in expanded_inv_idx.keys()]
        negated_term_lines = [[posting.doc_id for posting in self.inverted_index[term]] 
            for term in negated_words]
        # Find the documents that contain all the quoted sentences
        answer = self._intersection(term_lines)
        # For each negated term, remove from answer the documents that contain it
        for negated_term_line in negated_term_lines:
            negated_intersection = self._intersection([answer] + [negated_term_line])
            answer = filter(lambda d: d not in negated_intersection, answer)

        filtered_documents.extend(answer)


    def _intersection(self, term_lines, filtered_term_lines=list()):
        if len(term_lines) == 0:
            return []
        term_lines = deepcopy(term_lines)
        while len(filtered_term_lines) < len(term_lines):
            filtered_term_lines.append([])

        intersection = []
        while min(term_lines, key=len) != []:
            head_doc_ids = [term_line[0] for term_line in term_lines]
            min_head_doc = min(head_doc_ids)
            max_head_doc = max(head_doc_ids)

            if min_head_doc == max_head_doc:
                for i in range(0, len(term_lines)):
                    deepcopy_ = deepcopy(term_lines[i][0])
                    filtered_term_lines[i].append(deepcopy_)
                # Add the document to the intersection list and advances all
                # term_lines to the next documents
                intersection.append(int(min_head_doc))
                for term_line in term_lines:
                    del term_line[0]
            else:
                # Remove the smallest doc_id from all term_line heads
                for term_line in term_lines:
                    if term_line[0] == min_head_doc:
                        del term_line[0]

        return intersection


    # Expands the inverted index table to contain the quoted sentences, each
    # considered as a single term
    # def _expand_inverted_index(self, quoted_sentences, expansion):
    #     inv_idx = self.inverted_index
        
    #     for sentence in quoted_sentences:
    #         sentence = word_tokenize(sentence)
    #         # Create a new term representing the sentence and add it to the expansion
    #         new_term = "_".join(sentence)
    #         expansion[new_term] = list()
    #         # Get the doc_ids in the lines for each term in the sentence
    #         term_lines = [[posting for posting in inv_idx[word]] for word in sentence]
    #         # term_lines = [[posting.doc_id for posting in inv_idx[word]] for word in sentence]

    #         intersection = self._intersection(term_lines)
    #         for doc_id in intersection:
    #             # Create a new Posting for the document
    #             new_posting = Posting(doc_id)
    #             # Get the document in lowercase
    #             doc = word_tokenize(str(self.docs[doc_id]).lower())
    #             # Find the occurances of the sentence's first word on the document
    #             fst_word_occurances = list()
    #             for posting in inv_idx[sentence[0]]:
    #                 if posting.doc_id == doc_id:
    #                     fst_word_occurances.extend(posting.positions)
    #                     break
    #             # Check if the occurances of the first word are occurances of
    #             # the whole sentence. If so, add it to the new posting
    #             for position in fst_word_occurances:
    #                 match = True
    #                 for i in range(0, len(sentence)):
    #                     match = match and (sentence[i] == doc[position+i])
    #                 if match:
    #                     new_posting.positions.append(position)
    #             # If the new posting has occurances of the sentence, add it
    #             # to the expansion
    #             if len(new_posting.positions) > 0:
    #                 expansion[new_term].append(new_posting)


    # Expands the inverted index table to contain the quoted sentences, each
    # considered as a single term
    def _expand_inverted_index(self, quoted_sentences, expansion):
        inv_idx = self.inverted_index
        
        for sentence in quoted_sentences:
            sentence = word_tokenize(sentence)
            # Create a new term representing the sentence and add it to the expansion
            new_term = "_".join(sentence)
            expansion[new_term] = list()
            # Get the doc_ids in the lines for each term in the sentence
            term_lines = [[posting for posting in inv_idx[word]] for word in sentence]
            # term_lines = [[posting.doc_id for posting in inv_idx[word]] for word in sentence]

            filtered_postings = []
            intersection = self._intersection(term_lines, filtered_postings)
            while len(intersection) > 0:
                occurances = [postings_list[0].positions for postings_list in filtered_postings]
                for i in range(1, len(occurances)):
                    occurances[i] = [(occurance-i) for occurance in occurances[i]]
                sentence_occurances = self._intersection(occurances)
                if len(sentence_occurances) > 0:
                    new_posting = Posting(intersection[0])
                    new_posting.positions = deepcopy(sentence_occurances)
                    expansion[new_term].append(new_posting)
                for postings_list in filtered_postings:
                    del postings_list[0]
                del intersection[0]


    def search(self, query):
        expanded_inv_idx = {}
        filtered_documents = []

        # Binary AND search for quoted sentences and NOT search for negated words
        self._binary_search(query.quoted_sentences, query.negated_words, expanded_inv_idx, 
            filtered_documents)

        # TODO: busca ranqueada do passo anterior

        doc_number = 1
        for doc_id in filtered_documents:
            doc = deserialize(str(doc_id)+'.dbf')
            print str(doc_number) + '. ' + doc.title
            doc_number += 1
