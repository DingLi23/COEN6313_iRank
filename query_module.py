import json
import urllib.request
import datetime
import pymongo
import pandas as pd
from json import dumps
from io import StringIO

client = pymongo.MongoClient("mongodb+srv://coen6313:irank@coen6313irank.xbzvo.mongodb.net/"
                             "myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database('paper_search')
paper_db = db.paper_db
# app.secret_key = "testing_coen6313"

paper_id_list = [0]
papers_example = [
    {
        'title': 'Jumping NLP Curves: A Review of Natural Language Processing Research',
        'abstract': 'Natural language processing (NLP) is a theory-motivated range of computational techniques for '
                    'the automatic analysis and representation of human language. NLP research has evolved from the '
                    'era of punch cards and batch processing (in which the analysis of a sentence could take up to 7 '
                    'minutes) to the era of Google and the likes of it (in which millions of webpages can be '
                    'processed in less than a second). This review paper draws on recent developments in NLP research '
                    'to look at the past, present, and future of NLP technology in a new light. Borrowing the '
                    'paradigm of jumping curves from the field of business management and marketing prediction, '
                    'this survey article reinterprets the evolution of NLP research as the intersection of three '
                    'overlapping curves-namely Syntactics, Semantics, and Pragmatics Curveswhich will eventually lead '
                    'NLP research to evolve into natural language understanding.',
        'venue': 'IEEE Computational intelligence ',
        'authors': ['E Cambria', 'B White'],
        'year': 2014,
        'n_citations': 900,
    },
    {
        'title': 'BERT rediscovers the classical NLP pipeline',
        'abstract': 'Pre-trained text encoders have rapidly advanced the state of the art on many NLP tasks. We focus on one such model, BERT, and aim to quantify where linguistic information is captured within the network. We find that the model represents the steps of the traditional NLP pipeline in an interpretable and localizable way, and that the regions responsible for each step appear in the expected sequence: POS tagging, parsing, NER, semantic roles, then coreference. Qualitative analysis reveals that the model can and often does adjust this pipeline dynamically, revising lower-level decisions on the basis of disambiguating information from higher-level representations.',
        'venue': 'Computation and Language',
        'authors': ['Ian Tenney', 'Dipanjan Das', 'Ellie Pavlick'],
        'year': 2015,
        'n_citations': 519  # we don't have n_key_citations here and that's OK
    },
    {
        'title': 'Neural networks in civil engineering. I: Principles and understanding',
        'abstract': 'This is the first of two papers providing a discourse on the understanding, usage, and potential for application of artificial neural networks within civil engineering.',
        'venue': 'Journal of computing in civil engineering',
        'authors': ['Ian Flood', 'Nabil Kartam'],
        'year': 1994,
        'n_citations': 810  # we don't have n_key_citations here and that's OK
    },
    {
        'title': 'Xlnet: Generalized autoregressive pretraining for language understanding',
        'abstract': 'With the capability of modeling bidirectional contexts, denoting getencoding based pretraining '
                    'like BERT achieves better performance than pretraining approaches based on autoregressive '
                    'language modeling.',
        'venue': 'Advances in neural networks',
        'authors': ['Z Yang', 'Z Dai'],
        'year': 2019,
        'n_citations': 3581
    }
]


def query_from_API(keywords, numbers):
    query_url = 'https://api.semanticscholar.org/graph/v1/paper/search?query=' + keywords + '&fields=title,abstract,venue,authors,year,url,citationCount&limit=' + numbers

    with urllib.request.urlopen(query_url) as url:
        s = url.read()

    s = json.loads(s)

    now_time = datetime.datetime.now()
    paper_dict_list = []
    # last_paper_id = paper_id_list[-1]
    # count = 0

    for i in range(len(s['data'])):
        # paper_dict_format[i]['title'] = s['data'][i]['title']
        author_list = []
        for author in range(len(s['data'][i]['authors'])):
            author_list.append(s['data'][i]['authors'][author]['name'])

        new_paper = {'title': s['data'][i]['title'], 'abstract': s['data'][i]['abstract'],
                     'venue': s['data'][i]['venue'], 'authors': author_list, 'year': s['data'][i]['year'],
                     'n_citations': s['data'][i]['citationCount'],
                     'paper_id': s['data'][i]['paperId']}
        # 'url': s['data'][i]['url'],
        paper_found = paper_db.find_one({'title': s['data'][i]['title']})
        if not paper_found:
            # count = count + 1
            paper_details = {'paper_id': s['data'][i]['paperId'], 'create_time': now_time,
                             'title': s['data'][i]['title'], 'author': author_list,
                             'abstract': s['data'][i]['abstract'], 'venue': s['data'][i]['venue'],
                             'year': s['data'][i]['year'], 'citations': s['data'][i]['citationCount'],
                             'url': s['data'][i]['url']}
            # paper_id_list.append(count)
            paper_db.insert_one(paper_details)
        paper_dict_list.append(new_paper)
        # json_rlt = json.dumps(paper_dict_list)
    return paper_dict_list


def reorder_bycitations(paper_list):
    cite_order = []
    for paper in paper_list:
        cite_order.append(int(paper['n_citations']))
    cite_order = sorted(range(len(cite_order)), key=lambda k: cite_order[k], reverse=True)
    paper_list = [paper_list[i] for i in cite_order]

    return paper_list


def reorder_bydate(paper_list):
    date_order = []
    for paper in paper_list:
        date_order.append(int(paper['year']))
    date_order = sorted(range(len(date_order)), key=lambda k: date_order[k], reverse=True)
    paper_list = [paper_list[i] for i in date_order]
    return paper_list


def reorder_byML(paper_list):
    return paper_list


def reorder_bytrend(paper_list):
    trendy_order = []
    year = []
    citations = []
    for paper in paper_list:
        year.append(int(paper['year']))
        citations.append(int(paper['n_citations']))
    year = [(2022-i) for i in year]
    trendy_order = [i / j for i, j in zip(citations, year)]
    trendy_order = sorted(range(len(trendy_order)), key=lambda k: trendy_order[k], reverse=True)
    paper_list = [paper_list[i] for i in trendy_order]
    return paper_list


def clean_paperjson_toshow(paper_list):
    paper_list_clean = []
    for paper in paper_list:
        paper = {key: val for key, val in paper.items() if key != '_id'}
        paper = {key: val for key, val in paper.items() if key != 'create_time'}
        paper_list_clean.append(paper)
    json_data = dumps(paper_list)
    df = pd.read_json(StringIO(json_data))
    return df

def query_from_API_s2search(keyword, number):
    query_url = 'http://127.0.0.1:5001/s2rank/' + keyword + '&' + number
    # query_url = 'http://localhost:5000/s2rank/' + keyword + '&' + number
    with urllib.request.urlopen(query_url) as url:
        s = url.read()
    s = json.loads(s)
    paper_list = []
    score = []
    for paper in s:
        paper_db.insert_one(paper)
        paper_list.append(paper)
        score.append(float(paper['Relevance Score by S2Search']))
    score_order = sorted(range(len(score)), key=lambda k: score[k], reverse=True)
    paper_list = [paper_list[i] for i in score_order]

    paper_list_clean = []
    for paper in paper_list:
        paper = {key: val for key, val in paper.items() if key != '_id'}
        paper = {key: val for key, val in paper.items() if key != 'abstract'}
        paper = {key: val for key, val in paper.items() if key != 'url'}
        paper_list_clean.append(paper)

    return paper_list_clean


# list,s = query_from_API("nlp", '2')
# print(s)
#

