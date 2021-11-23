import pymongo

client = pymongo.MongoClient("mongodb+srv://coen6313:irank@coen6313irank.xbzvo.mongodb.net/"
                             "myFirstDatabase?retryWrites=true&w=majority")
# db = client.test
from wtforms import Form, StringField, SelectField


class User_Info:
    def __init__(self):
        self.username = 'a'
        self.email = 'a@gmail.com'
        self.password = '123'
        self.user_id = '0'
        self.search_history = ''
        self.like_history = ''
        self.unlike_history = ''
        self.comment_history = ''


class Paper_info:
    def __init__(self):
        self.title = 'NLP'
        self.abstract = 'NLP is'
        self.venue = 'IEEE'
        self.authors = ['a', 'b']
        self.year = 2020
        self.citations = 1000


class PaperSearchForm(Form):
    choices = [('NormalSearch', 'NormalSearch'),
               ('by_Date', 'by_Date'),
               ('by_Citations', 'by_Citations'),
               ('by_Trend', 'by_Trend'),
               ('by_s2Model', 'by_s2Model')]
    select = SelectField('Sort_Method:', choices=choices)
    search = StringField('Keywords')
    number = StringField('Query_Paper_numbers')

class Reaction(Form):
    likes = StringField('You like this Paper?')
    comments = StringField('Please have your comments to this paper')
    paper_title = StringField('Paper title')
