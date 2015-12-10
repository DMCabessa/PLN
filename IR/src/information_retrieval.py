from file_handler import deserialize, PATH
from posting import Posting
from query import Query
from math import log, sqrt
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
        doc_tfs = dict(zip(filtered_documents, [0]*len(filtered_documents)))
        if filtered_documents == []:
            return doc_tfs

        if term in expanded_inv_idx:
            inv_idx = expanded_inv_idx
        else:
            inv_idx = self.inverted_index

        # print 'filtered: ' + str(filtered_documents)
        idx_fd = 0
        for posting in inv_idx[term]:
            # Ignore doc_ids smaller than posting.doc_id
            while idx_fd < len(filtered_documents) and filtered_documents[idx_fd] < posting.doc_id:
                idx_fd += 1
            # Break if there are no more allowed doc_ids
            if idx_fd >= len(filtered_documents):
                break

            # print 'index: ' + str(idx_fd) + '   docs: ' + str(filtered_documents) + '   posting: ' + str(posting)
            allowed_id = filtered_documents[idx_fd]
            if posting.doc_id == allowed_id:
                # print '(' + term + ') id: ' + str(allowed_id) + '   count: ' + str(len(posting.positions)) + '   1+log: ' + str(1 + log(len(posting.positions)))
                doc_tfs[allowed_id] = 1 + log(len(posting.positions))
            if posting.doc_id >= allowed_id:
                idx_fd += 1

        return doc_tfs


    def _term_idf(self, term, expanded_inv_idx):
        if term in expanded_inv_idx:
            n_docs = len(expanded_inv_idx[term])
        else:
            n_docs = len(self.inverted_index[term])
        # Return the log on base 10
        if n_docs > 0:
            return log(self.inverted_index.n/float(n_docs), 10)
        else:
            return 0

    # TODO
    def _compute_scores(self, unquoted_words, expanded_inv_idx, filtered_documents):
        terms = unquoted_words + expanded_inv_idx.keys()
        tfs = {}
        idfs = {}
        # Compute all tfs and idfs
        for term in terms:
            tfs[term] = self._term_tfs(term, expanded_inv_idx, filtered_documents)
            tfs[term]['query'] = tfs[term]['query'] + 1 if tfs[term].has_key('query') else 1
            idfs[term] = self._term_idf(term, expanded_inv_idx)

        # print 'TFs:\n' + str(tfs)

        # Compute the tf-idfs
        tf_idfs = tfs
        for term in tfs:
            for doc_id in tfs[term]:
                tf_idfs[term][doc_id] *= idfs[term]
        # Create the documents and query vectors

        # print 'TF-IDFs:\n' + str(tf_idfs)

        vectors = {}
        for doc_id in filtered_documents + ['query']:
            vectors[doc_id] = []    
            for term in terms:
                vectors[doc_id].append(tf_idfs[term][doc_id])
        # Normalize the vectors
        for doc_id in filtered_documents + ['query']:
            length = sqrt(sum([x**2 for x in vectors[doc_id]]))
            if length == 0 and doc_id != 'query':
                filtered_documents.remove(doc_id)
                del vectors[doc_id]
            elif length > 0:
                vectors[doc_id] = [x/float(length) for x in vectors[doc_id]]
            # if max(vectors[doc_id]) > 0:
            #     print 'id: ' + str(doc_id) + '   normalized vector: ' + str(vectors[doc_id])
        # Compute the cosines
        cos = {}
        for doc_id in filtered_documents:
            cos[doc_id] = sum([vectors[doc_id][i]*vectors['query'][i] for i in 
                range(0, len(terms))])

        # print 'cos: ' + str(cos)

        # Order the doc_ids decreasingly with respect to cos[doc_id]
        ranked_documents = cos.keys()
        list.sort(ranked_documents, key=lambda doc_id: 1 - cos[doc_id])
        return ranked_documents


    def _binary_search(self, quoted_phrases, negated_words, expanded_inv_idx, filtered_documents):
        self._expand_inverted_index(quoted_phrases, expanded_inv_idx)
        self._binary_merge(negated_words, expanded_inv_idx, filtered_documents)


    def _binary_merge(self, negated_words, expanded_inv_idx, filtered_documents):
        if len(expanded_inv_idx) > 0:
            term_lines = [[posting.doc_id for posting in expanded_inv_idx[term]] 
                for term in expanded_inv_idx.keys()]
            # Find the documents that contain all the quoted phrases
            answer = self._intersection(term_lines)
        else:
            answer = range(1, self.inverted_index.n + 1)
        
        if len(negated_words) > 0:
            negated_term_lines = [[posting.doc_id for posting in self.inverted_index[term]] 
                for term in negated_words]
            # For each negated term, remove from answer the documents that contain it
            for negated_term_line in negated_term_lines:
                negated_intersection = self._intersection([answer] + [negated_term_line])
                answer = filter(lambda d: d not in negated_intersection, answer)

        filtered_documents.extend(answer)


    # def _intersection(self, term_lines, filtered_term_lines=list()):
    #     if len(term_lines) == 0:
    #         return []
    #     term_lines = deepcopy(term_lines)
    #     while len(filtered_term_lines) < len(term_lines):
    #         filtered_term_lines.append([])

    #     intersection = []
    #     while min(term_lines, key=len) != []:
    #         head_doc_ids = [term_line[0] for term_line in term_lines]
    #         min_head_doc = min(head_doc_ids)
    #         max_head_doc = max(head_doc_ids)

    #         if min_head_doc == max_head_doc:
    #             for i in range(0, len(term_lines)):
    #                 deepcopy_ = deepcopy(term_lines[i][0])
    #                 filtered_term_lines[i].append(deepcopy_)
    #             # Add the document to the intersection list and advances all
    #             # term_lines to the next documents
    #             intersection.append(int(min_head_doc))
    #             for term_line in term_lines:
    #                 del term_line[0]
    #         else:
    #             # Remove the smallest doc_id from all term_line heads
    #             for term_line in term_lines:
    #                 if term_line[0] == min_head_doc:
    #                     del term_line[0]

    #     return intersection


    def _intersection(self, term_lines, filtered_term_lines=list()):
        if len(term_lines) == 0:
            return []
        while len(filtered_term_lines) < len(term_lines):
            filtered_term_lines.append([])

        indices = [0] * len(term_lines)
        intersection = []
        length_minus_index = lambda (line, idx): len(line) - idx
        while min(map(length_minus_index, zip(term_lines, indices))) > 0:
            head_doc_ids = [term_line[idx] for (term_line, idx) in zip(term_lines, indices)]
            min_head_doc = min(head_doc_ids)
            max_head_doc = max(head_doc_ids)

            if min_head_doc == max_head_doc:
                for i in range(0, len(term_lines)):
                    idx = indices[i]
                    deepcopy_ = deepcopy(term_lines[i][idx])
                    filtered_term_lines[i].append(deepcopy_)
                # Add the document to the intersection list and advances all
                # term_lines to the next documents
                intersection.append(int(min_head_doc))
                for i in range(0, len(indices)):
                    indices[i] += 1
            else:
                # Remove the smallest doc_id from all term_line heads
                for i in range(0, len(term_lines)):
                    idx = indices[i]
                    if term_lines[i][idx] == min_head_doc:
                        indices[i] += 1

        return intersection


    # Expands the inverted index table to contain the quoted phrases, each
    # considered as a single term
    # def _expand_inverted_index(self, quoted_phrases, expansion):
    #     inv_idx = self.inverted_index
        
    #     for phrase in quoted_phrases:
    #         phrase = word_tokenize(phrase)
    #         # Create a new term representing the phrase and add it to the expansion
    #         new_term = "_".join(phrase)
    #         expansion[new_term] = list()
    #         # Get the doc_ids in the lines for each term in the phrase
    #         term_lines = [[posting for posting in inv_idx[word]] for word in phrase]
    #         # term_lines = [[posting.doc_id for posting in inv_idx[word]] for word in phrase]

    #         intersection = self._intersection(term_lines)
    #         for doc_id in intersection:
    #             # Create a new Posting for the document
    #             new_posting = Posting(doc_id)
    #             # Get the document in lowercase
    #             doc = word_tokenize(str(self.docs[doc_id]).lower())
    #             # Find the occurrences of the phrase's first word on the document
    #             fst_word_occurrences = list()
    #             for posting in inv_idx[phrase[0]]:
    #                 if posting.doc_id == doc_id:
    #                     fst_word_occurrences.extend(posting.positions)
    #                     break
    #             # Check if the occurrences of the first word are occurrences of
    #             # the whole phrase. If so, add it to the new posting
    #             for position in fst_word_occurrences:
    #                 match = True
    #                 for i in range(0, len(phrase)):
    #                     match = match and (phrase[i] == doc[position+i])
    #                 if match:
    #                     new_posting.positions.append(position)
    #             # If the new posting has occurrences of the phrase, add it
    #             # to the expansion
    #             if len(new_posting.positions) > 0:
    #                 expansion[new_term].append(new_posting)


    # Expands the inverted index table to contain the quoted phrases, each
    # considered as a single term
    def _expand_inverted_index(self, quoted_phrases, expansion):
        inv_idx = self.inverted_index
        
        for phrase in quoted_phrases:
            phrase = word_tokenize(phrase)
            # Create a new term representing the phrase and add it to the expansion
            new_term = "_".join(phrase)
            expansion[new_term] = list()
            # Get the doc_ids in the lines for each term in the phrase
            term_lines = [[posting for posting in inv_idx[word]] for word in phrase]

            # Select the documents which contain all the phrase's words
            filtered_postings = []
            intersection = self._intersection(term_lines, filtered_postings)
            while len(intersection) > 0:
                # Occurrences is a list of lists (matrix), where each line i contains
                # the occurrences of the ith word of the phrase in the document
                # intersection[0].
                occurrences = [postings_list[0].positions for postings_list in filtered_postings]
                # Subtract from all elements in each line of occurrences the line
                # index (line 0 is ignored).
                for i in range(1, len(occurrences)):
                    occurrences[i] = [(occurrence-i) for occurrence in occurrences[i]]
                # The positions in which there are intersections are occurrences
                # of the whole phrase in the document.
                phrase_occurrences = self._intersection(occurrences)
                # If there are occurrences, create a Posting for the document in 
                # expansion[new_term] 
                if len(phrase_occurrences) > 0:
                    new_posting = Posting(intersection[0])
                    new_posting.positions = deepcopy(phrase_occurrences)
                    expansion[new_term].append(new_posting)
                # Delete the heads of intersection and filtered_posting's lines
                for postings_list in filtered_postings:
                    del postings_list[0]
                del intersection[0]


    def search(self, query):
        expanded_inv_idx = {}
        filtered_documents = []

        # Binary AND search for quoted phrases and NOT search for negated words
        self._binary_search(query.quoted_phrases, query.negated_words, expanded_inv_idx, 
            filtered_documents)

        # TODO: busca ranqueada do passo anterior
        ranked_documents = self._compute_scores(query.unquoted_words, 
            expanded_inv_idx, filtered_documents)

        doc_number = 1
        return [deserialize(str(doc_id)+'.dbf') for doc_id in ranked_documents]
        # for doc_id in ranked_documents:
        #     doc = deserialize(str(doc_id)+'.dbf')
        #     print str(doc_number) + '. ' + doc.title
        #     doc_number += 1
            # if doc_number > 10:
            #    break

        # print '-------'
        # for term in (query.unquoted_words + expanded_inv_idx.keys()):
        #     print 'checking ' + term
        #     self.check(term, expanded_inv_idx)
        #     print '-------'


    # def check(self, term, expanded_inv_idx={}):
    #     dict_ = expanded_inv_idx if term in expanded_inv_idx else self.inverted_index
    #     for posting in dict_[term]:
    #         print 'doc #' + str(posting.doc_id) + ':'
    #         for pos in posting.positions:
    #             doc = deserialize(str(posting.doc_id) + '.dbf')
    #             print str(word_tokenize(str(doc).lower())[pos:pos+5])
