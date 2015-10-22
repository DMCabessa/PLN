from bs4 import BeautifulSoup,SoupStrainer
import nltk

# Constants
TITLE_WEIGHT = 2
MAX_INTERSECTION = 5
RELEVANT_TOPICS = ['earn', 'acq', 'money-fx', 'grain', 'crude', 'trade', 'interest', 'ship', 'wheat', 'corn']
IRRELEVANT_WORDS = ['is','said','are','be','reuter','was','were','say','has','had','have','did','do','does',
                     'go','goes','gone','i','been','\x03shr','>','<', '\x03the']


def document_bow(document_text, vocabulary):
    # Select only the words that belong to the vocabulary
    tokens = nltk.word_tokenize(document_text.lower())
    tokens = filter(lambda t: t in vocabulary, tokens)
    # Convert the words from unicode to ascii
    return map(lambda t: t.encode('ascii'), tokens)

def build_bow_freq_dist(document_text, vocabulary):
    bow = document_bow(document_text, vocabulary)
    # Compute the frequency distribution
    freq_dist = nltk.FreqDist(bow)
    # Create a dictionary for the frequency distribution
    BoW_freq_dist = {}
    for word in freq_dist:
        BoW_freq_dist[word] = freq_dist[word]
    return BoW_freq_dist

def readFiles():
    num_documents = { 'total': 0.0 }
    mega_documents = {}
    for topic in RELEVANT_TOPICS:
        num_documents[topic] = 0
        mega_documents[topic] = ('','')
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
                        for rt in RELEVANT_TOPICS:
                            if rt in map(lambda d: d.text, ds):
                                mega_documents[rt] = (mega_documents[rt][0], mega_documents[rt][1] + reuter.find('content').text)
                            else:
                                mega_documents[rt] = (mega_documents[rt][0] + reuter.find('content').text, mega_documents[rt][1])
                        all_contents = all_contents + reuter.find('content').text
            if reuter['lewissplit'] == 'TEST':
                    raw_test_documents.append(reuter)

    # Create a dictionary for the return values
    return_values = {'num_documents': num_documents, 'mega_documents': mega_documents,
                        'all_contents': all_contents, 'raw_training_documents': raw_training_documents,
                        'raw_test_documents': raw_test_documents}
    return return_values


def create_vocabulary():
    data = readFiles()

    raw_training_documents = data['raw_training_documents']
    raw_test_documents = data['raw_test_documents']
    num_documents = data['num_documents']
    mega_documents = data['mega_documents']
    all_contents = data['all_contents']

    a_priori_probabilities = {}
    vocabulary = set()
    general_vocabulary = []

    # Compute the class a priori probabilities for all classes
    for topic in RELEVANT_TOPICS:
        a_priori_probabilities[topic] = num_documents[topic]/num_documents['total']
    print 'A Priori Probabilities:\n' + str(a_priori_probabilities) + '\n'
    
    freq_dists = {}
    for topic in RELEVANT_TOPICS:   
        # Separate all_contents into tokens
        tokens = nltk.word_tokenize(mega_documents[topic][1].lower())
        # Change the encoding from unicode to ascii
        tokens = [t.encode('ascii') for t in tokens]
        # Remove irrelevant words
        filtered = filter(lambda x: not (x in IRRELEVANT_WORDS),tokens)
        # Classify the tokens grammatically
        taggedList = nltk.pos_tag(filtered)
        # Replace all numbers with a single __NUMBER__ tag
        taggedList = map(lambda (token,tag): ('__NUMBER__',tag) if tag == 'CD' else (token,tag), taggedList)
        # Select only the verbs, nouns and adjectives
        freq_dists[topic] = nltk.FreqDist((word+'/'+tag) for (word,tag) in taggedList if (tag in ['VB','NN','JJ']))
    # Print the 500 most frequent words in fdist
    #print '500 most common words:\n' + str(fdist.most_common(500)) + '\n'

    # Build the vocabulary
    #x = fdist.most_common(1500)
    #y = fdist.most_common(1000)
    #aux_vocabulary = []
    #for word in x:
    #    if word not in y:
    #        aux_vocabulary.append(word)
    for fd in freq_dists:
        #vocabulary = vocabulary.union(set([word[0:len(word)-3] for (word,_) in freq_dists[fd].most_common(500)]))
        general_vocabulary.append( (fd, set([word[0:len(word)-3] for (word,_) in freq_dists[fd].most_common(150)]), freq_dists[fd].most_common(150)) )


    for (topic, topic_set, frequency) in general_vocabulary:
        for word in topic_set:
            contain = filter(lambda (_,s,_): word in s, general_vocabulary)
            if len(contain) > MAX_INTERSECTION:
                print "<" + word + ">, " + str(map(lambda (t,_): t+": "+frequency[word], contain)) + "  size: " + str(len(contain)) + "\n" 
            else:
                vocabulary = vocabulary.union(set([word]))

    print 'The vocabulary:\n' + str(vocabulary) + '\n'

    # Built the bag of words for each class mega document
    for topic in mega_documents:
        mega_documents[topic] = (build_bow_freq_dist(mega_documents[topic][0], vocabulary) , build_bow_freq_dist(mega_documents[topic][1], vocabulary))

    return {'mega_documents': mega_documents, 'vocabulary': vocabulary, 'a_priori_probabilities': a_priori_probabilities, 
            'raw_training_documents': raw_training_documents, 'raw_test_documents': raw_test_documents}