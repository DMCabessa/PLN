from file_reader import document_bow, RELEVANT_TOPICS, TITLE_WEIGHT
from math import log

def estimate_word_prob(word, topic, freq_dist, vocabulary):
    numerator = (freq_dist[word]+1) if (word in freq_dist) else 1
    denominador = len(vocabulary)
    for value in freq_dist.values():
        denominador += value
    return numerator/float(denominador)

# Receives a document as the data of a <REUTER> tag
def classify_document(document, mega_documents, a_priori_probabilities, vocabulary):
    # Build BoWs for the title and the content of the document
    doc_title = document.find('title').text if document.find('title') != None else ""
    doc_text = document.find('content').text if document.find('content') != None else ""
    #doc_text_fst_sentences = " ".join(map(lambda paragraph: paragraph.split('. ')[0], doc_text.split("\n    ")))
    doc_title_bow = document_bow(doc_title, vocabulary)
    doc_text_bow = document_bow(doc_text, vocabulary)
    #doc_fst_sentences_bow = document_bow(doc_text_fst_sentences, vocabulary)
    # Create a single BoW for the document, giving weight 2 for the words in the title
    doc_bow = doc_title_bow*TITLE_WEIGHT + doc_text_bow #+ doc_fst_sentences_bow
    topic_probability_list = []
    for topic in mega_documents:
        # Compute the a posteriori probabilities
        a_posteriori_probabilities = [0, 0]
        for classifier in (0,1):
            summation = 0
            for word in doc_bow:
                summation += log(estimate_word_prob(word, topic, mega_documents[topic][classifier], vocabulary))
            a_priori_probability = a_priori_probabilities[topic] if classifier else (1 - a_priori_probabilities[topic])   
            a_posteriori_probabilities[classifier] = log(a_priori_probability) + summation
        topic_probability_list.append( (topic, a_posteriori_probabilities[1] > a_posteriori_probabilities[0]) )
    
    return map(lambda (topic,_): topic, filter(lambda (_,prob): prob, topic_probability_list))

def evaluate_algorithm2(raw_documents, mega_documents, a_priori_probabilities, vocabulary):
    # Build confusion matrix
    confusion_matrix = {}
    for topic in RELEVANT_TOPICS:
        confusion_matrix[topic] = {'tp':0.0, 'fp':0.0, 'tn':0.0, 'fn':0.0}

    print 'Computing metrics...\n'
    for raw_doc in raw_documents:
        classification = classify_document(raw_doc, mega_documents, a_priori_probabilities, vocabulary)
        for guessed_topic in classification:
            if guessed_topic in map(lambda d: d.text.encode('ascii'), raw_doc.find('topics').findAll('d')):
                confusion_matrix[guessed_topic]['tp'] += 1
            else:
                confusion_matrix[guessed_topic]['fp'] += 1
        for right_topic in map(lambda d: d.text.encode('ascii'), raw_doc.find('topics').findAll('d')):
            if right_topic not in classification and right_topic in RELEVANT_TOPICS:
                confusion_matrix[right_topic]['fn'] += 1
        for topic in RELEVANT_TOPICS:
            if topic not in set(classification + map(lambda d: d.text.encode('ascii'), raw_doc.find('topics').findAll('d'))):
                confusion_matrix[topic]['tn'] += 1

    print confusion_matrix
    
    # Compute evaluation metrics [precision, recall, accuracy, F1]
    f1_sum = 0.0
    for topic in confusion_matrix:
        counters = confusion_matrix[topic]
        precision = counters['tp'] / (counters['tp'] + counters['fp'])
        recall = counters['tp'] / (counters['tp'] + counters['fn'])
        accuracy = (counters['tp'] + counters['tn']) / sum(counters.values())
        f1 = 2 * precision * recall / (precision + recall)
        f1_sum += f1
        print topic + ":\n\tPrecision: " + str(precision) + "\n\tRecall: " + str(recall) + "\n\tAccuracy: " + str(accuracy) + "\n\tF1: " + str(f1) + "\n"
    print '\naverage F1: ' + str(f1_sum/len(RELEVANT_TOPICS))

def evaluate_algorithm(data):
    evaluate_algorithm2(data['raw_test_documents'], data['mega_documents'], data['a_priori_probabilities'], data['vocabulary'])
