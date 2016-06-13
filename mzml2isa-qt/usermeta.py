#!/usr/bin/env python3

import os
import json

from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette

from mzml2isa.isa import USERMETA
from mzml2isa.versionutils import dict_update

from qt.usermeta import Ui_Dialog as Ui_UserMeta
from scrapers import PSOThread, PROThread


class UserMetaDialog(QDialog):

    SigUpdateMetadata = pyqtSignal('QString')
    SigUpdatePSOBoxes = pyqtSignal('QString')
    SigUpdatePROBoxes = pyqtSignal('QString')

    def __init__(self, parent=None, metadata={}):
        
        super(UserMetaDialog, self).__init__(parent)
        

        self.metadata = dict_update(USERMETA, metadata)
        
        # Set up the user interface from Designer.
        self.ui = Ui_UserMeta()
        self.ui.setupUi(self)

        # Connect buttons
        self.ui.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.saveandquit)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.close)

        # Connect signals
        self.SigUpdatePSOBoxes.connect(self.fillPSOComboBoxes)
        self.PSOscraper = PSOThread(self.SigUpdatePSOBoxes)
        self.PSOscraper.start()
        self.SigUpdatePROBoxes.connect(self.fillPROComboBoxes)
        self.PROscraper = PROThread(self.SigUpdatePROBoxes)
        self.PROscraper.start()

        self.fillFields()

    def save(self):
        self.getFields()
        self.SigUpdateMetadata.emit(json.dumps(self.metadata))
        
    def saveandquit(self):
        self.save()
        self.close()

    def fillFields(self):
        
        ## STUDY
        self.ui.title.setText(self.metadata['study']['title'])

        ## INVESTIGATION
        self.ui.identifier_2.setText(self.metadata['investigation']['identifier'])
        self.ui.title_2.setText(self.metadata['investigation']['title'])


        ## COMBO BOXES


    def getFields(self):

        ## STUDY
        ### General
        self.metadata['study']['title'] = self.ui.title.text()
        ### Publication
        self.metadata['study_publication']['pubmed'] = self.ui.pubmed_id.text()
        self.metadata['study_publication']['doi'] = self.ui.doi.text()
        self.metadata['study_publication']['title'] = self.ui.pub_title.text()
        self.metadata['study_publication']['authors_list'] = self.ui.authors_list.toPlainText()
        self.metadata['study_publication']['status']['value'] = self.ui.combo_status.currentText() if self.ui.status.text() else ""
        self.metadata['study_publication']['status']['accession'] = self.ui.status.text()
        
        ## INVESTIGATION
        ### General
        self.metadata['investigation']['identifier'] = self.ui.identifier_2.text()
        ### Publication
        self.metadata['investigation_publication']['pubmed'] = self.ui.pubmed_id_2.text()
        self.metadata['investigation_publication']['doi'] = self.ui.doi_2.text()
        self.metadata['investigation_publication']['title'] = self.ui.pub_title_2.text()
        self.metadata['investigation_publication']['authors_list'] = self.ui.authors_list_2.toPlainText()
        self.metadata['investigation_publication']['status']['value'] = self.ui.combo_status_2.currentText()
        self.metadata['investigation_publication']['status']['accession'] = self.ui.status_2.text()
        self.metadata['investigation_publication']['status']['value'] = self.ui.combo_status_2.currentText() if self.ui.status.text() else ""
        self.metadata['investigation_publication']['status']['accession'] = self.ui.status_2.text()
    
    
    def fillPSOComboBoxes(self, jsontology):
        _translate = QCoreApplication.translate

        if not hasattr(self, 'ontoPSO'):
            # Get PSO ontology
            self.ontoPSO = json.loads(jsontology)
            self.ontoPSOk = sorted(self.ontoPSO)

            # Add status to combo box
            for i, status in enumerate(self.ontoPSOk):
                self.ui.combo_status.addItem("")
                self.ui.combo_status.setItemText(i, _translate("Dialog", status))
                self.ui.combo_status_2.addItem("")
                self.ui.combo_status_2.setItemText(i, _translate("Dialog", status))
            self.ui.combo_status.setCurrentText(self.metadata['study_publication']['status']['value'])
            self.ui.status.setText(self.metadata['study_publication']['status']['accession'])
            self.ui.combo_status_2.setCurrentText(self.metadata['investigation_publication']['status']['value'])
            self.ui.status_2.setText(self.metadata['investigation_publication']['status']['accession'])

            # Link comboboxes and display fields
            self.ui.combo_status.activated.connect(lambda x: self.ui.status.setText(\
              self.ontoPSO[self.ui.combo_status.currentText()]))
            self.ui.combo_status_2.activated.connect(lambda x: self.ui.status.setText(\
              self.ontoPSO[self.ui.combo_status_2.currentText()]))    

    def fillPROComboBoxes(self, jsontology):
        _translate = QCoreApplication.translate

        if not hasattr(self, 'ontoPRO'):
            # Get PSO ontology
            self.ontoPRO = json.loads(jsontology)
            self.ontoPROk = sorted(self.ontoPRO)

            # Add status to combo box
            for i, status in enumerate(self.ontoPROk):
                self.ui.combo_roles.addItem("")
                self.ui.combo_roles.setItemText(i, _translate("Dialog", status))
                self.ui.combo_roles_2.addItem("")
                self.ui.combo_roles_2.setItemText(i, _translate("Dialog", status))
            self.ui.combo_roles.setCurrentText(self.metadata['study_contacts']['roles']['value'])
            self.ui.roles.setText(self.metadata['study_contacts']['roles']['accession'])
            self.ui.combo_roles_2.setCurrentText(self.metadata['investigation_contacts']['roles']['value'])
            self.ui.roles_2.setText(self.metadata['investigation_contacts']['roles']['accession'])

            # Link comboboxes and display fields
            self.ui.combo_roles.activated.connect(lambda x: self.ui.roles.setText(\
              self.ontoPRO[self.ui.combo_roles.currentText()]))
            self.ui.combo_status_2.activated.connect(lambda x: self.ui.status.setText(\
              self.ontoPRO[self.ui.combo_roles_2.currentText()]))    




if __name__ == '__main__':
    print(json.dumps(get_publication_status()))
        