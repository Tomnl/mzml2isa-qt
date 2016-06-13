#!/usr/bin/env python3

import urllib.request as rq
import urllib.error
import os
import json

from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette

from mzml2isa.isa import USERMETA
from mzml2isa.versionutils import dict_update

from qt.usermeta import Ui_Dialog as Ui_UserMeta


def get_publication_status():
    
    try:
        onto = json.loads(rq.urlopen("http://www.sparontologies.net/ontologies/pso/source.json").read().decode('utf-8'))
        pub_status = []
        for x in onto:
            if '@type' in x:
                if "http://purl.org/spar/pso/PublicationStatus" in x['@type']:
                    pub_status.append(x)
        pub_status = [ (x['http://www.w3.org/2000/01/rdf-schema#label'],x['@id']) for x in pub_status[:] ]
        pub_status = {x[0]['@value'].capitalize():y for (x,y) in pub_status}
        return pub_status
    except urllib.error:
        with open(os.path.join(os.path.dirname(__file__), "publication_status.json"), 'r') as f:
            pub_status = json.loads(f.read())
    finally:
        return pub_status


class UserMetaDialog(QDialog):

    SigUpdateMetadata = pyqtSignal('QString')
    
    def __init__(self, parent=None, metadata={}):
        super(UserMetaDialog, self).__init__(parent)
        

        ### TODO: THREAD THAT###########################
        self.metadata = dict_update(USERMETA, metadata)#
        ### AND UPDATE COMBOBOXES ON NETWORK ANSWER#####


        self.ontoPub = get_publication_status()
        self.ontoPubStatus = sorted(self.ontoPub)

        # Set up the user interface from Designer.
        self.ui = Ui_UserMeta()
        self.ui.setupUi(self)

        self.ui.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.saveandquit)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.close)


        self.ui.combo_status.activated.connect(lambda x: self.ui.status.setText(self.ontoPub[self.ui.combo_status.currentText()]))


        self.fillFields()

            

    def save(self):
        print("save")
        self.getFields()
        self.SigUpdateMetadata.emit(json.dumps(self.metadata))
        
    def saveandquit(self):
        self.save()
        print("quit")
        super(UserMetaDialog, self).close()


    def fillFields(self):
        _translate = QCoreApplication.translate
        
        ## STUDY
        self.ui.title.setText(self.metadata['study']['title'])

        ## INVESTIGATION
        self.ui.identifier_2.setText(self.metadata['investigation']['identifier'])
        self.ui.title_2.setText(self.metadata['investigation']['title'])


        ## COMBO BOXES
        for i, status in enumerate(self.ontoPubStatus):
            print(status)
            self.ui.combo_status.addItem("")
            self.ui.combo_status.setItemText(i, _translate("Dialog", status))
            self.ui.combo_status_2.addItem("")
            self.ui.combo_status_2.setItemText(i, _translate("Dialog", status))




    def getFields(self):

        ## STUDY
        ### General
        self.metadata['study']['title'] = self.ui.title.text()

        ### Publication
        self.metadata['study_publication']['status']['value'] = self.ui.combo_status.currentText()
        self.metadata['study_publication']['status']['ref'] = self.ontoPub[self.ui.combo_status.currentText()]

        ## INVESTIGATION
        self.metadata['investigation']['identifier'] = self.ui.identifier_2.text()
    
    






if __name__ == '__main__':
    print(json.dumps(get_publication_status()))
        