import sys
import json

from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QStandardItemModel, QStandardItem

from qt.ols import Ui_Dialog as Ui_Ols

from scrapers import OlsSearcher






class OlsDialog(QDialog):

    SearchCompleted = pyqtSignal('QString')

    def __init__(self, parent=None):
        super(OlsDialog, self).__init__(parent)

        self.ui = Ui_Ols()
        self.ui.setupUi(self)

        self.ui.searchButton.clicked.connect(self.search)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.returnInformation)

        
        self.ui.queryLine.setFocus()
    

    def search(self):
        self.searcher = OlsSearcher(self.ui.queryLine.text())
        self.searcher.Finished.connect(self.updateSearchResults)
        self.searcher.start()

    def updateSearchResults(self, jresults):
        self.results = json.loads(jresults)
        nodes = {}


        if self.results:
            
            self.model = QStandardItemModel()
            self.orderedResults = {}

            for result in self.results:
                
                if result['ontology_prefix'] not in nodes:
                    node = QStandardItem(result['ontology_prefix'])
                    self.model.appendRow(node)
                    nodes[result['ontology_prefix']] = node

                nodes[result['ontology_prefix']].appendRow(
                    QStandardItem(result['short_form'].replace('_', ':'))
                )
            
            self.ui.ontoTree.setModel(self.model)
            self.ui.ontoTree.expandAll()
            self.model.setHorizontalHeaderLabels(["Object"])
            self.ui.ontoTree.selectionModel().selectionChanged.connect(self.updateInterface)

    def updateInterface(self, *args):
        if self.ui.ontoTree.selectedIndexes():
            index = self.ui.ontoTree.selectedIndexes()[0]
            crawler = index.model().itemFromIndex(index)
            print(crawler.text())
            
            # parse results to get the right entry
            entry = None
            for x in self.results:
                if x['short_form'].replace('_', ':') == crawler.text():
                    entry = x 
            
            if entry is None:
                print("SELECTION IS AN ONTOLOGY")
            else:
                print("SELECTION IS A CLASS")





    def returnInformation(self):
        if self.ui.ontoTree.selectedIndexes():
            index = self.ui.ontoTree.selectedIndexes()[0]
            crawler = index.model().itemFromIndex(index)
        
            entry = []

            for x in self.results:
                if x['short_form'].replace('_', ':') == crawler.text():
                    entry = x 
            
            print(entry)



if __name__=='__main__':
    app = QApplication(sys.argv)
    ols = OlsDialog()
    ols.show()
    sys.exit(app.exec_())
    
