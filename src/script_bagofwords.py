from bs4 import BeautifulSoup,SoupStrainer
import nltk
relevantTopics = ['earn', 'acq', 'money-fx', 'grain', 'crude', 'trade', 'interest', 'ship', 'wheat', 'corn']
nDocuments = { 'total': 0.0 }
megaDocuments = {}
aPrioriProbabilities = {}
for topic in relevantTopics:
    nDocuments[topic] = 0
    megaDocuments[topic] = ''

#allTopics = []
#allContents_List = []
allContents = ""

irrelevantWords = ['is','said','are','be','reuter','was','were','say','has','had','have']
for i in range(0,22):
    filename = "../documents/reut2-0" + ("0" if i < 10 else "") + str(i) + ".sgm"
    f = open(filename)
    data = f.read()
    soup = BeautifulSoup(data, "html.parser")
    reuters = soup.findAll('reuters')
    for reuter in reuters:
	   if reuter['lewissplit'] == "train" or reuter['lewissplit'] == "TRAIN":
            topics = reuter.find('topics')
            ds = topics.findAll('d')
#            for d in ds:
#               if not(d.text in allTopics):
#                    allTopics.append(d.text)
            # Keep only the relevant topics
            ds = filter(lambda d: d.text in relevantTopics, ds)
            # Check if the document belongs to any of the relevant topics
            if len(ds) > 0:
                nDocuments['total'] += 1
                # Increase the document count for every relevant topic counter
                for d in ds:
                    nDocuments[d.text] += 1
                if reuter.find('content') != None:
                    for d in ds:
                        megaDocuments[d.text] += reuter.find('content').text
                    #allContents_List.append(reuter.find('content').text)
                    allContents = allContents + reuter.find('content').text
#print sorted(allTopics)

# Compute the class a priori probabilities for all classes
for topic in relevantTopics:
    aPrioriProbabilities[topic] = nDocuments[topic]/nDocuments['total']
print 'A Priori Probabilities:\n' + str(aPrioriProbabilities) + '\n'

# Separate allContents into tokens
tokens = nltk.word_tokenize(allContents.lower())
# Change the encoding from unicode to ascii
tokens = [t.encode('ascii') for t in tokens]
# Remove irrelevant words
filtered = filter(lambda x: not (x in irrelevantWords),tokens)
# Classify the tokens grammatically
taggedList = nltk.pos_tag(filtered)
# Select only the verbs, nouns and adjectives
fdist = nltk.FreqDist((word+"/"+tag) for (word,tag) in taggedList if (tag[:2] == 'VB' or tag[:2] == 'NN' or tag[:2] == 'JJ'))
# Print the 500 most frequent words in fdist
print '500 most common words:\n' + str(fdist.most_common(500)) + '\n'



