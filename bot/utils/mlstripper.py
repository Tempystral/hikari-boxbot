from html.parser import HTMLParser
from io import StringIO

'''
Sourced from https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
'''

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html:str):
    s = MLStripper()
    s.feed(html.replace("<br />", "\n"))
    return s.get_data()