from bs4 import BeautifulSoup

class Document:
    def __init__(self,document):
        self.id = int(document['newid'])
        self.topics = map(lambda d: d.text, document.find('topics').findAll('d'))
        self.places = map(lambda d: d.text, document.find('places').findAll('d'))
        self.title = document.find('title').text if document.find('title') != None else unicode("")
        self.content = document.find('content').text if document.find('content') != None else unicode("")
        # self.encode_to_ascii()

    def encode_to_ascii(self):
        self.id = self.id.encode('ascii')
        self.topics = map(lambda s: s.encode('ascii'), self.topics)
        self.places = map(lambda s: s.encode('ascii'), self.places)
        self.title = self.title.encode('ascii')
        self.content = self.content.encode('ascii')

    def __str__(self):
        # The returned text is in the format: <Title>\n<Topics>\n<Places>\n<Content>.
        # Different topics/places are separated by a whitespace
        return self.title + "\n" + " ".join(self.topics) + "\n" + " ".join(self.places) + "\n" + self.content