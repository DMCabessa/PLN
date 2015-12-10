from bs4 import BeautifulSoup

class Document:
    def __init__(self,document):
        self.id = int(document['newid'])
        self.topics = map(lambda d: d.text, document.find('topics').findAll('d'))
        self.places = map(lambda d: d.text, document.find('places').findAll('d'))
        self.title = document.find('title').text if document.find('title') != None else unicode("")
        self.content = document.find('content').text if document.find('content') != None else unicode("")
        self.encode_to_ascii()

    def encode_to_ascii(self):
        self.topics = map(lambda s: s.encode('utf-8'), self.topics)
        self.places = map(lambda s: s.encode('utf-8'), self.places)
        self.title = self.title.encode('utf-8')
        self.content = self.content.encode('utf-8')

    def __str__(self):
        # The returned text is in the format: <Title>\n<Topics>\n<Places>\n<Content>.
        # Different topics/places are separated by a whitespace
        return self.title + "\n" + " ".join(self.topics) + "\n" + " ".join(self.places) + "\n" + self.content

    def fancy_str(self):
        return "TITLE:\n\t" + self.title + "\nTOPICS:\n\t" + ", ".join(self.topics) + "\nPLACES:\n\t" + ", ".join(self.places) + "\nCONTENT:\n\t" + self.content.replace("\n", "\n\t")