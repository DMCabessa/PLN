from bs4 import BeautifulSoup,SoupStrainer
from math import log
import nltk

# Constants
TITLE_WEIGHT = 2
RELEVANT_TOPICS = ['earn', 'acq', 'money-fx', 'grain', 'crude', 'trade', 'interest', 'ship', 'wheat', 'corn']
IRRELEVANT_WORDS = ['is','said','are','be','reuter','was','were','say','has','had','have','did','do','does',
                     'go','goes','gone','i','been']

def document_bow(document_text):
    # Select only the words that belong to the vocabulary
    tokens = nltk.word_tokenize(document_text.lower())
    tokens = filter(lambda t: t in vocabulary, tokens)
    # Convert the words from unicode to ascii
    return map(lambda t: t.encode('ascii'), tokens)

def build_bow_freq_dist(document_text):
    bow = document_bow(document_text)
    # Compute the frequency distribution
    freq_dist = nltk.FreqDist(bow)
    # Create a dictionary for the frequency distribution
    BoW_freq_dist = {}
    for word in freq_dist:
        BoW_freq_dist[word] = freq_dist[word]
    return BoW_freq_dist

def estimate_word_prob(word, topic):
    numerator = (mega_documents[topic][word]+1) if (word in mega_documents[topic]) else 1
    denominador = len(vocabulary)
    for value in mega_documents[topic].values():
        denominador += value
    return numerator/float(denominador)

# Receives a document as the data of a <REUTER> tag
def classify_document(document):
    # Build BoWs for the title and the content of the document
    doc_title = document.find('title').text if document.find('title') != None else ""
    doc_text = document.find('content').text if document.find('content') != None else ""
    doc_title_bow = document_bow(doc_title)
    doc_text_bow = document_bow(doc_text)
    # Create a single BoW for the document, giving weight 2 for the words in the title
    doc_bow = doc_title_bow*TITLE_WEIGHT + doc_text_bow
    # Compute the a posteriori probabilities
    a_posteriori_probabilities = []
    for topic in mega_documents:
        summation = 0
        for word in doc_bow:
            summation += log(estimate_word_prob(word, topic))
        a_posteriori_probabilities.append((topic, a_priori_probabilities[topic] + summation))
    # Find the topic with the maximum a posteriori probability
    (topic, _) = max(a_posteriori_probabilities, key=(lambda (_,prob): prob))
    #if not(topic in map(lambda d: d.text.encode('ascii'), document.find('topics').findAll('d'))):
    #    print ('\n'+topic.upper()+'  '+str(map(lambda d: d.text.encode('ascii'),document.find('topics').findAll('d'))) 
    #        + '\n' + str(a_posteriori_probabilities))
    return topic

def readFiles():
    num_documents = { 'total': 0.0 }
    mega_documents = {}
    for topic in RELEVANT_TOPICS:
        num_documents[topic] = 0
        mega_documents[topic] = ''
    all_contents = ""
    raw_training_documents = []
    raw_test_documents = []

    for i in range(0,22):
        filename = "../documents/reut2-0" + ("0" if i < 10 else "") + str(i) + ".sgm"
        f = open(filename)
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
        reuters = soup.findAll('reuters')
        for reuter in reuters:
            if reuter['lewissplit'] == 'TRAIN':
                topics = reuter.find('topics')
                ds = topics.findAll('d')
                # Keep only the relevant topics
                ds = filter(lambda d: d.text in RELEVANT_TOPICS, ds)
                # Check if the document belongs to any of the relevant topics
                if len(ds) > 0:

                    raw_training_documents.append(reuter)

                    num_documents['total'] += 1
                    # Increase the document count for every relevant topic counter
                    for d in ds:
                        num_documents[d.text] += 1
                    if reuter.find('content') != None:
                        for d in ds:
                            mega_documents[d.text] += reuter.find('content').text
                        all_contents = all_contents + reuter.find('content').text
            if reuter['lewissplit'] == 'TEST':
                    raw_test_documents.append(reuter)

    # Create a dictionary for the return values
    return_values = {'num_documents': num_documents, 'mega_documents': mega_documents,
                        'all_contents': all_contents, 'raw_training_documents': raw_training_documents,
                        'raw_test_documents': raw_test_documents}
    return return_values


data = readFiles()

raw_training_documents = data['raw_training_documents']
raw_test_documents = data['raw_test_documents']
num_documents = data['num_documents']
mega_documents = data['mega_documents']
all_contents = data['all_contents']

vocabulary = set()
a_priori_probabilities = {}

# Compute the class a priori probabilities for all classes
for topic in RELEVANT_TOPICS:
    a_priori_probabilities[topic] = num_documents[topic]/num_documents['total']
print 'A Priori Probabilities:\n' + str(a_priori_probabilities) + '\n'
    
# Separate all_contents into tokens
tokens = nltk.word_tokenize(all_contents.lower())
# Change the encoding from unicode to ascii
tokens = [t.encode('ascii') for t in tokens]
# Remove irrelevant words
filtered = filter(lambda x: not (x in IRRELEVANT_WORDS),tokens)
# Classify the tokens grammatically
taggedList = nltk.pos_tag(filtered)
# Select only the verbs, nouns and adjectives
fdist = nltk.FreqDist((word+'/'+tag) for (word,tag) in taggedList if (tag == 'VB' or tag == 'NN' or tag == 'JJ'))
# Print the 500 most frequent words in fdist
print '500 most common words:\n' + str(fdist.most_common(500)) + '\n'

# Build the vocabulary
vocabulary = set([word[0:len(word)-3] for (word,_) in fdist.most_common(500)])
print 'The vocabulary:\n' + str(vocabulary) + '\n'

# Built the bag of words for each class mega document
for topic in mega_documents:
    mega_documents[topic] = build_bow_freq_dist(mega_documents[topic])
print "The BoW mega documents:"
for topic in mega_documents:
    print topic.upper() + ':\n' + str(mega_documents[topic]) + '\n'

counter = 0.0

print len(raw_test_documents)

for raw_doc in raw_test_documents:
    classification = classify_document(raw_doc)
    if not(classification in map(lambda d: d.text.encode('ascii'), raw_doc.find('topics').findAll('d'))):
        counter += 1
    #print ("Classified as " + classification + ", topics are: " + 
    #    str(map(lambda d: d.text.encode('ascii'), raw_doc.find('topics').findAll('d'))))
print '\n' + str(100*counter/num_documents['total']) + "%\n"
