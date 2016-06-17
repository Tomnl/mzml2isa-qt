import sys
import os
import json
import urllib.error
import urllib.request as rq
from urllib.parse import quote

from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QStandardItemModel, QStandardItem

from mzml2isaqt.qt.ols import Ui_Dialog as Ui_Ols




class OlsDialog(QDialog):
    """Dialog to search the OLS for an ontology

    The OlsDialog uses threads to connect to the Ontology Lookup Service,
    and search for a query, get results, and get informations about 
    ontologies. 

    Selected ontology is returned as a json serialized dict.
    """

    SigSearchCompleted = pyqtSignal('QString')
    SigSelected = pyqtSignal('QString')

    def __init__(self, parent=None, allow_onto=False):
        super(OlsDialog, self).__init__(parent)

        self.ui = Ui_Ols()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.onto = {}
        self.ontothreads = {}
        self.allow_onto = allow_onto
        self.entry = None

        self.ui.searchButton.clicked.connect(self.search)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(
            self.onOkClicked
            )
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(
            lambda: self.close()
            )

        self.ui.queryLine.setFocus()

    def search(self):
        """Launch the OlsSearchThread"""
        self.searcher = OlsSearcher(self.ui.queryLine.text())
        self.searcher.Finished.connect(self.updateSearchResults)
        self.searcher.start()

    def updateSearchResults(self, jresults):
        """Update TreeView with search results."""

        self.model = QStandardItemModel()
        self.orderedResults = {}

        if jresults:
            
            self.results = json.loads(jresults)

            for result in self.results:
                prefix = result['ontology_prefix']
                
                # Create a new node & append it to StandardItemModel
                # if the ontology of the result is not already in StandardItemModel
                if not self.model.findItems(prefix):
                    node = QStandardItem(prefix)
                    self.model.appendRow(node)
                    
                # Look for details of that new ontology if that ontology is not
                # already memo table and not other OlsOntologist is querying
                # informations about that ontology
                if prefix not in self.ontothreads and prefix not in self.onto:
                    thread = OlsOntologist(prefix)
                    thread.Finished.connect(self._memo_onto)
                    thread.start()
                    self.ontothreads[prefix] = thread

                # Add the entry to its ontology node
                result['tag'] = result['short_form'].replace('_', ':') + ' - ' + result['label']    
                self.model.findItems(prefix)[0].appendRow(
                        QStandardItem(result['tag'])
                    )

        self.model.sort(0)
        self.ui.ontoTree.setModel(self.model)
        #self.ui.ontoTree.expandAll()
        self.model.setHorizontalHeaderLabels(["Object"])
        self.ui.ontoTree.selectionModel().selectionChanged.connect(
            lambda selection: self.updateInterface(selection.indexes()[0])
            )
        self.ui.ontoTree.clicked.connect(self.updateInterface)
        self.ui.ontoTree.doubleClicked.connect(self.onDoubleClick)
        
    def _getResultFromIndex(self, index):
        """Iterate on self.results to get the right entry"""
        crawler = self.model.itemFromIndex(index)
        self.entry = None
        for x in self.results:
            if x['tag'] == crawler.text():
                self.entry = x 
        return crawler.text()

    def updateInterface(self, index):
        """Update the interface fields with the value from the TreeView"""
        
        if index:       
            tag = self._getResultFromIndex(index)
            
            # selection is an ontology
            if self.entry is None:

                if not self.allow_onto:
                    self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

                # information about ontology is present in memoization table
                if tag in self.onto.keys():
                    
                    self.entry = self.onto[tag]
                    self.ui.value.setPlainText(self.entry['title'])
                    self.ui.prefix.setText(self.entry['preferredPrefix'])
                    self.ui.iri.setPlainText(self.entry['id'])
                    self.ui.description.setPlainText(self.entry['description'])

                # No information is to be found
                else:
                    self.ui.value.setPlainText("")
                    self.ui.prefix.setText("")
                    self.ui.iri.setPlainText("")
                    self.ui.description.setPlainText("")

                self.ui.prefix.setText(tag)
                self.ui.type.setText('Ontology')

            # selection is a class
            else:
                
                self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

                self.ui.value.setPlainText(self.entry['label'])
                self.ui.prefix.setText(self.entry['ontology_prefix'])
                self.ui.iri.setPlainText(self.entry['iri'])
                self.ui.type.setText('Class')
                
                self.ui.description.setPlainText(
                    self.entry['description'][0] if 'description' in self.entry else ''
                    )
          
    def onOkClicked(self):
        self.SigSelected.emit(json.dumps(self.entry))
        self.close()

    def onDoubleClick(self, index):
        """Return class when double clicked"""
        self._getResultFromIndex(index)
        if self.entry is not None:
            self.SigSelected.emit(json.dumps(self.entry))
            self.close()

    def _memo_onto(self, prefix, jsonconfig):
        self.onto[prefix] = json.loads(jsonconfig)
        # FIND A WAY TO UPDATE INTERFACE
        # IF MEMOIZED ONTOLOGY IS THE ONE BEING DISPLAYED
        
    
        




class OlsSearcher(QThread):
    """A thread that searches the Ontology Lookup Service."""

    Finished = pyqtSignal('QString')

    def __init__(self, query, rows=200):
        super(OlsSearcher, self).__init__()
        self.searchUrl = "http://www.ebi.ac.uk/ols/api/search/?q={}"\
            "&groupField=1&rows={}".format(query, rows)

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



class OlsExplorer(QThread):
    """A thread that get the informations of a class based on its iri."""
  
    Finished = pyqtSignal('QString', 'QString')

    def __init__(self, short_ref, prefix, iri, ):
        super(OlsExplorer, self).__init__()
        self.ref = short_ref
        self.url = 'http://www.ebi.ac.uk/ols/api/ontologies/{prefix}' \
                    '/terms/{iri}'.format(prefix=prefix, 
                                          iri=quote(quote(iri, safe=''), safe='')
                                          )


    def run(self):
        try:
            request = rq.FancyURLopener({})
            with request.open(self.url) as url_opener:
                self.result = url_opener.read().decode('utf-8')
        except urllib.error:
            self.result = ''
        finally:
            self.Finished.emit(self.ref, self.result)



class OlsOntologist(QThread):
    """A thread that get the informations of an ontology based on its prefix."""
   
    Finished = pyqtSignal('QString', 'QString')

    def __init__(self, prefix, parent=None, *args, **kwargs):
        super(OlsOntologist, self).__init__(parent, *args, **kwargs)
        self.prefix = prefix
        self.url = 'http://www.ebi.ac.uk/ols/api/ontologies/{prefix}'.format(prefix=prefix) 


    def run(self):
        try:
            request = rq.FancyURLopener({})
            with request.open(self.url) as url_opener:
                result = json.loads(url_opener.read().decode('utf-8'))
                self.config = result['config']
        except urllib.error:
            self.result = ''
        finally:
            self.Finished.emit(self.prefix, json.dumps(self.config))




if __name__=='__main__':
    app = QApplication(sys.argv)
    ols = OlsDialog()
    ols.SigSelected.connect(lambda x: print(x))
    ols.show()
    sys.exit(app.exec_())
    
