## BACKEND
import os
import json
import urllib.request as rq
import urllib.error

## FRONTEND
from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette




class SparOntologyThread(QThread):

    Finished = pyqtSignal('QString')

    def __init__(self):
        super(SparOntologyThread, self).__init__()

    def run(self):
        try:
            onto = json.loads(rq.urlopen(self.jsonSourceUrl).read().decode('utf-8'))
            info = []
            for x in onto:
                if '@type' in x:
                    if self.ontoClass in x['@type']:
                        info.append(x)
            info = [ (x['http://www.w3.org/2000/01/rdf-schema#label'],x['@id']) for x in info ]
            info = json.dumps({x[0]['@value'].capitalize():y for (x,y) in info})
        except urllib.error:
            with open(os.path.join(os.path.dirname(__file__), os.path.join("ontologies", self.sparName + os.path.extsep + 'json')), 'r') as f:
                info = f.read()
        finally:
            self.Finished.emit(info)


class PSOThread(SparOntologyThread):
    """A thread to scrape the Publishing Status Ontology"""

    def __init__(self):
        super(PSOThread, self).__init__()
        self.jsonSourceUrl = "http://www.sparontologies.net/ontologies/pso/source.json"
        self.sparName = "pso"
        self.ontoClass = "http://purl.org/spar/pso/PublicationStatus"


class PROThread(SparOntologyThread):
    """A thread to scrape the Publishing Roles Ontology"""
    def __init__(self):
        super(PROThread, self).__init__()
        self.jsonSourceUrl = "http://www.sparontologies.net/ontologies/pro/source.json"
        self.sparName = "pro"
        self.ontoClass = "http://purl.org/spar/pro/PublishingRole"


class OlsSearcher(QThread):

    Finished = pyqtSignal('QString')

    def __init__(self, query):
        super(OlsSearcher, self).__init__()
        self.searchUrl = "http://www.ebi.ac.uk/ols/api/search/?q=" + query+"&groupField=1&rows=20"

    def run(self):
        try:
            request = rq.FancyURLopener({})
            with request.open(self.searchUrl) as url_opener:
                result = json.loads(url_opener.read().decode('utf-8'))
            
                if not 'response' in result or result['response']['numFound'] == 0:
                    answer = ('')
                else:
                    answer = json.dumps(result['response']['docs'])
                    
        except urllib.error:
            answer = ''
        finally:
            self.Finished.emit(answer)
