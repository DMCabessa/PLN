from bs4 import BeautifulSoup,SoupStrainer
import nltk
categories = {
    'earn': "", 
    'acquisitions': "",
    'money-fx': "",
    'grain': "", 
    'crude': "",
    'trade': "", 
    'interest': "",
    'ship': "",
    'wheat': "",
    'corn': ""
    }
trainList = []
text = ""
testList = []
filterlist = ['is','said','are','be','reuter','was','were','say','has','had','have']
for i in range(0,22):
    filename = "../documents/reut2-0" + ("0" if i < 10 else "") + str(i) + ".sgm"
    f = open(filename)
    data = f.read()
    soup = BeautifulSoup(data, "html.parser")
    reuters = soup.findAll('reuters')
    for reuter in reuters:
	   if reuter['lewissplit'] == "train" or reuter['lewissplit'] == "TRAIN":
            topic = reuter.find('topics')
            ds = topic.findAll('d')
            useText = False
            for d in ds:
                if d.text in categories.keys():
                    useText = True
                    break
            if useText and reuter.find('content') != None:
                for d in ds:
                    if d.text in categories.keys():
                        categories[d.text] += reuter.find('content').text
                trainList.append(reuter.find('content').text)
                text = text + reuter.find('content').text
                #print "a" + reuter.find('content').text + "\n"
#print trainList

tokens = nltk.word_tokenize(text.lower())
filtered = filter(lambda x: not (x in filterlist),tokens)
taggedList = nltk.pos_tag(filtered)
fdist = nltk.FreqDist(word+"/"+tag for (word,tag) in taggedList if tag[:2] == 'VB' or tag[:2] == 'NN' or tag[:2] == 'JJ')
fdist.most_common(500)