#!/usr/bin/env python3

import os
import sys
import json
import urllib.request as rq
import urllib.error


from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette

from mzml2isa.isa import USERMETA
from mzml2isa.versionutils import dict_update

from mzml2isaqt.ols import OlsDialog

from mzml2isaqt.qt.usermeta import Ui_Dialog as Ui_UserMeta


class UserMetaDialog(QDialog):

    SigUpdateMetadata = pyqtSignal('QString')

    def __init__(self, parent=None, metadata={}):

        super(UserMetaDialog, self).__init__(parent)

        self.ui = Ui_UserMeta()
        self.ui.setupUi(self)

        self.metadata = dict_update(USERMETA, metadata)

        self.ui.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.save)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.saveandquit)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.ui.search_organism.clicked.connect(self.searchOrganism)
        self.ui.search_organism_part.clicked.connect(self.searchOrganismPart)
        self.ui.search_organism_variant.clicked.connect(self.searchOrganismVariant)
        self.ui.rm_organism.clicked.connect(lambda: self.updateOrganism('null'))                # As this get deserialized
        self.ui.rm_organism_variant.clicked.connect(lambda: self.updateOrganismVariant('null')) # from JSON, nill is the way
        self.ui.rm_organism_part.clicked.connect(lambda: self.updateOrganismPart('null'))       # to set ontology to None

        self.launchScrapers()
        self.setUpDates()
        self.fillFields()

        self.ui.buttonBox.button(QDialogButtonBox.Apply).setFocus()

    def launchScrapers(self):
        self.PSOscraper = PSOThread()
        self.PSOscraper.Finished.connect(self.fillPSOComboBoxes)
        self.PSOscraper.start()
        
        self.PROscraper = PROThread()
        self.PROscraper.Finished.connect(self.fillPROComboBoxes)
        self.PROscraper.start()

    def setUpDates(self):
        self.dates_changed = {x:False for x in ('s_rel', 's_sub', 'i_rel', 'i_sub')}
        self.ui.submission_date.editingFinished.connect(lambda: self.setDateChanged('s_sub'))
        self.ui.release_date.editingFinished.connect(lambda: self.setDateChanged('s_rel'))
        self.ui.submission_date_2.editingFinished.connect(lambda: self.setDateChanged('i_sub'))
        self.ui.release_date_2.editingFinished.connect(lambda: self.setDateChanged('i_rel'))

    def setDateChanged(self, date):
        self.dates_changed[date] = True

    def save(self):
        self.getFields()
        self.SigUpdateMetadata.emit(json.dumps(self.metadata))
        
    def saveandquit(self):
        self.save()
        self.close()



    def fillFields(self):

        ## STUDY
        ### General
        self.ui.title.setText(self.metadata['study']['title'])
        #self.ui.identifier.setText(self.metadata['study']['identifier'])
        self.ui.description.setPlainText(self.metadata['study']['description'])
        if self.metadata['study']['submission_date']:
            self.ui.submission_date.setDate(QDate.fromString(self.metadata['study']['submission_date'], "yyyy-MM-dd"))
            self.setDateChanged('s_sub')
        if self.metadata['study']['release_date']:
            self.ui.release_date.setDate(QDate.fromString(self.metadata['study']['release_date'], "yyyy-MM-dd"))
            self.setDateChanged('s_rel')
        ### Publication
        self.ui.pubmed_id.setText(self.metadata['study_publication']['pubmed'])
        self.ui.doi.setText(self.metadata['study_publication']['doi'])
        self.ui.pub_title.setText(self.metadata['study_publication']['title'])
        self.ui.authors_list.setPlainText(self.metadata['study_publication']['author_list'])        
        ### Contact
        self.ui.first_name.setText(self.metadata['study_contacts'][0]['first_name'])
        self.ui.mid.setText(self.metadata['study_contacts'][0]['mid_initials'])
        self.ui.last_name.setText(self.metadata['study_contacts'][0]['last_name'])
        self.ui.mail.setText(self.metadata['study_contacts'][0]['email'])
        self.ui.phone.setText(self.metadata['study_contacts'][0]['phone'])
        self.ui.fax.setText(self.metadata['study_contacts'][0]['fax'])
        self.ui.adress.setPlainText(self.metadata['study_contacts'][0]['adress'])
        self.ui.affiliation.setText(self.metadata['study_contacts'][0]['affiliation'])

        ## INVESTIGATION
        ### General
        self.ui.identifier_2.setText(self.metadata['investigation']['identifier'])
        self.ui.description_2.setPlainText(self.metadata['investigation']['description'])
        if self.metadata['investigation']['submission_date']:
            self.ui.submission_date_2.setDate(QDate.fromString(self.metadata['investigation']['submission_date'], "yyyy-MM-dd"))
            self.setDateChanged('i_sub')
        if self.metadata['investigation']['release_date']:
            self.ui.release_date_2.setDate(QDate.fromString(self.metadata['investigation']['release_date'], "yyyy-MM-dd"))
            self.setDateChanged('i_rel')
        ### Publication
        self.ui.pubmed_id.setText(self.metadata['investigation_publication']['pubmed'])
        self.ui.doi_2.setText(self.metadata['investigation_publication']['doi'])
        self.ui.pub_title_2.setText(self.metadata['investigation_publication']['title'])
        self.ui.authors_list_2.setPlainText(self.metadata['investigation_publication']['author_list'])
        ### Contact
        self.ui.first_name_2.setText(self.metadata['investigation_contacts'][0]['first_name'])
        self.ui.mid_2.setText(self.metadata['investigation_contacts'][0]['mid_initials'])
        self.ui.last_name_2.setText(self.metadata['investigation_contacts'][0]['last_name'])
        self.ui.mail_2.setText(self.metadata['investigation_contacts'][0]['email'])
        self.ui.phone_2.setText(self.metadata['investigation_contacts'][0]['phone'])
        self.ui.fax_2.setText(self.metadata['investigation_contacts'][0]['fax'])
        self.ui.adress_2.setPlainText(self.metadata['investigation_contacts'][0]['adress'])
        self.ui.affiliation_2.setText(self.metadata['investigation_contacts'][0]['affiliation'])

        ## EXPERIMENTS
        ## Characteristics
        self.ui.name_organism.setText(self.metadata['characteristics']['organism']['value'])
        self.ui.iri_organism.setText(self.metadata['characteristics']['organism']['accession'])
        self.ui.ref_organism.setText(self.metadata['characteristics']['organism']['ref'])
        
        self.ui.name_organism_part.setText(self.metadata['characteristics']['part']['value'])
        self.ui.iri_organism_part.setText(self.metadata['characteristics']['part']['accession'])
        self.ui.ref_organism_part.setText(self.metadata['characteristics']['part']['ref'])
        
        self.ui.name_organism_variant.setText(self.metadata['characteristics']['variant']['value'])
        self.ui.iri_organism_variant.setText(self.metadata['characteristics']['variant']['accession'])
        self.ui.ref_organism_variant.setText(self.metadata['characteristics']['variant']['ref'])
        ### Descriptions
        self.ui.sample_collect_desc.setPlainText(self.metadata['description']['sample_collect'])
        self.ui.extraction_desc.setPlainText(self.metadata['description']['extraction'])
        self.ui.chroma_desc.setPlainText(self.metadata['description']['chroma'])
        self.ui.mass_spec_desc.setPlainText(self.metadata['description']['mass_spec'])
        self.ui.data_trans_desc.setPlainText(self.metadata['description']['data_trans'])
        self.ui.metabo_id_desc.setPlainText(self.metadata['description']['metabo_id'])


    def getFields(self):

        ## STUDY
        ### General
        self.metadata['study']['title'] = self.ui.title.text()
        self.metadata['study']['identifier'] = self.ui.identifier.text()
        self.metadata['study']['description'] = self.ui.description.toPlainText()
        self.metadata['study']['submission_date'] = self.ui.submission_date.date().toString("yyyy-MM-dd") if self.dates_changed['s_sub'] else ''
        self.metadata['study']['release_date'] = self.ui.release_date.date().toString("yyyy-MM-dd") if self.dates_changed['s_rel'] else ''
        ### Publication
        self.metadata['study_publication']['pubmed'] = self.ui.pubmed_id.text()
        self.metadata['study_publication']['doi'] = self.ui.doi.text()
        self.metadata['study_publication']['title'] = self.ui.pub_title.text()
        self.metadata['study_publication']['author_list'] = self.ui.authors_list.toPlainText()
        self.metadata['study_publication']['status']['value'] = self.ui.combo_status.currentText() if self.ui.status.text() else ''
        self.metadata['study_publication']['status']['accession'] = self.ui.status.text()
        self.metadata['study_publication']['status']['ref'] = 'PSO' if self.ui.status.text() else ''
        ### Contact
        self.metadata['study_contacts'][0]['first_name'] = self.ui.first_name.text()
        self.metadata['study_contacts'][0]['mid_initials'] = self.ui.mid.text()
        self.metadata['study_contacts'][0]['last_name'] = self.ui.last_name.text()
        self.metadata['study_contacts'][0]['email'] = self.ui.mail.text()
        self.metadata['study_contacts'][0]['phone'] = self.ui.phone.text()
        self.metadata['study_contacts'][0]['fax'] = self.ui.fax.text()
        self.metadata['study_contacts'][0]['adress'] = self.ui.adress.toPlainText()
        self.metadata['study_contacts'][0]['affiliation'] = self.ui.affiliation.text()
        self.metadata['study_contacts'][0]['roles']['value'] = self.ui.combo_roles.currentText() if self.ui.roles.text() else ''
        self.metadata['study_contacts'][0]['roles']['accession'] = self.ui.roles.text()
        self.metadata['study_contacts'][0]['roles']['ref'] = 'PRO' if self.ui.roles.text() else ''

        ## INVESTIGATION
        ### General
        self.metadata['investigation']['identifier'] = self.ui.identifier_2.text()
        self.metadata['investigation']['description'] = self.ui.description_2.toPlainText()
        self.metadata['investigation']['submission_date'] = self.ui.submission_date_2.date().toString("yyyy-MM-dd") if self.dates_changed['i_sub'] else ''
        self.metadata['investigation']['release_date'] = self.ui.release_date_2.date().toString("yyyy-MM-dd") if self.dates_changed['i_rel'] else ''
        ### Publication
        self.metadata['investigation_publication']['pubmed'] = self.ui.pubmed_id_2.text()
        self.metadata['investigation_publication']['doi'] = self.ui.doi_2.text()
        self.metadata['investigation_publication']['title'] = self.ui.pub_title_2.text()
        self.metadata['investigation_publication']['author_list'] = self.ui.authors_list_2.toPlainText()
        self.metadata['investigation_publication']['status']['value'] = self.ui.combo_status_2.currentText() if self.ui.status_2.text() else ""
        self.metadata['investigation_publication']['status']['accession'] = self.ui.status_2.text()
        self.metadata['investigation_publication']['status']['ref'] = 'PSO' if self.ui.status_2.text() else ''
        ### Contact
        self.metadata['investigation_contacts'][0]['first_name'] = self.ui.first_name_2.text()
        self.metadata['investigation_contacts'][0]['mid_initials'] = self.ui.mid_2.text()
        self.metadata['investigation_contacts'][0]['last_name'] = self.ui.last_name_2.text()
        self.metadata['investigation_contacts'][0]['email'] = self.ui.mail_2.text()
        self.metadata['investigation_contacts'][0]['phone'] = self.ui.phone_2.text()
        self.metadata['investigation_contacts'][0]['fax'] = self.ui.fax_2.text()
        self.metadata['investigation_contacts'][0]['adress'] = self.ui.adress_2.toPlainText()
        self.metadata['investigation_contacts'][0]['affiliation'] = self.ui.affiliation_2.text()
        self.metadata['investigation_contacts'][0]['roles']['value'] = self.ui.combo_roles_2.currentText() if self.ui.roles_2.text() else ''
        self.metadata['investigation_contacts'][0]['roles']['accession'] = self.ui.roles_2.text()
        self.metadata['investigation_contacts'][0]['roles']['ref'] = 'PRO' if self.ui.roles_2.text() else ''

        ## EXPERIMENTS
        ## Characteristics
        self.metadata['characteristics']['organism']['value'] = self.ui.name_organism.text()
        self.metadata['characteristics']['organism']['accession'] = self.ui.iri_organism.text()
        self.metadata['characteristics']['organism']['ref'] = self.ui.ref_organism.text()
        self.metadata['characteristics']['part']['value'] = self.ui.name_organism_part.text()
        self.metadata['characteristics']['part']['accession'] = self.ui.iri_organism_part.text()
        self.metadata['characteristics']['part']['ref'] = self.ui.ref_organism_part.text()
        self.metadata['characteristics']['variant']['value'] = self.ui.name_organism_variant.text()
        self.metadata['characteristics']['variant']['accession'] = self.ui.iri_organism_variant.text()
        self.metadata['characteristics']['variant']['ref'] = self.ui.ref_organism_variant.text()
        ### Descriptions
        self.metadata['description']['sample_collect'] = self.ui.sample_collect_desc.toPlainText()
        self.metadata['description']['extraction'] = self.ui.extraction_desc.toPlainText()
        self.metadata['description']['chroma'] = self.ui.chroma_desc.toPlainText()
        self.metadata['description']['mass_spec'] = self.ui.mass_spec_desc.toPlainText()
        self.metadata['description']['data_trans'] = self.ui.data_trans_desc.toPlainText()
        self.metadata['description']['metabo_id'] = self.ui.metabo_id_desc.toPlainText()


    def fillPSOComboBoxes(self, jsontology):
        _translate = QCoreApplication.translate
        # Get PSO ontology
        self.ontoPSO = json.loads(jsontology)
        self.ontoPSOk = sorted(self.ontoPSO)
        # Hide status fields (they ARE useful, though !)
        self.ui.status.hide()
        self.ui.status_2.hide()
        # Hide "connecting to PSO" labels
        self.ui.label_pso.hide()
        self.ui.label_pso_2.hide()
        # Add status to combo box
        for i, status in enumerate(self.ontoPSOk):
            self.ui.combo_status.addItem("")
            self.ui.combo_status.setItemText(i, _translate("Dialog", status))
            self.ui.combo_status_2.addItem("")
            self.ui.combo_status_2.setItemText(i, _translate("Dialog", status))
        # Chek if value to display
        if self.metadata['study_publication']['status']['value']:
            self.ui.combo_status.setCurrentText(self.metadata['study_publication']['status']['value'])
            self.ui.status.setText(self.metadata['study_publication']['status']['accession'])    
        else:
            self.ui.combo_status.setCurrentIndex(-1)   
        if self.metadata['investigation_publication']['status']['value']:
            self.ui.combo_status_2.setCurrentText(self.metadata['investigation_publication']['status']['value'])
            self.ui.status_2.setText(self.metadata['investigation_publication']['status']['accession'])
        else:
            self.ui.combo_status_2.setCurrentIndex(-1)    
        # Link comboboxes and display fields
        self.ui.combo_status.activated.connect(lambda x: self.ui.status.setText(\
          self.ontoPSO[self.ui.combo_status.currentText()]))
        self.ui.combo_status_2.activated.connect(lambda x: self.ui.status_2.setText(\
          self.ontoPSO[self.ui.combo_status_2.currentText()])) 
        # Enable comboboxes
        self.ui.combo_status.setEnabled(True)
        self.ui.combo_status_2.setEnabled(True)

    def fillPROComboBoxes(self, jsontology):
        _translate = QCoreApplication.translate
        # Get PRO ontology
        self.ontoPRO = json.loads(jsontology)
        self.ontoPROk = sorted(self.ontoPRO)
        # Hide roles fields (they ARE useful, though !)
        self.ui.roles.hide()
        self.ui.roles_2.hide()
        # Hide "connecting to PRO" labels
        self.ui.label_pro.hide()
        self.ui.label_pro_2.hide()
        # Add status to combo box
        for i, status in enumerate(self.ontoPROk):
            self.ui.combo_roles.addItem("")
            self.ui.combo_roles.setItemText(i, _translate("Dialog", status))
            self.ui.combo_roles_2.addItem("")
            self.ui.combo_roles_2.setItemText(i, _translate("Dialog", status))
        # Check if value to display
        if self.metadata['study_contacts'][0]['roles']['value']:
            self.ui.combo_roles.setCurrentText(self.metadata['study_contacts'][0]['roles']['value'])
            self.ui.roles.setText(self.metadata['study_contacts'][0]['roles']['accession'])
        else:
            self.ui.combo_roles.setCurrentIndex(-1)
            
        if self.metadata['investigation_contacts'][0]['roles']['value']:
            self.ui.combo_roles_2.setCurrentText(self.metadata['investigation_contacts'][0]['roles']['value'])
            self.ui.roles_2.setText(self.metadata['investigation_contacts'][0]['roles']['accession'])
        else:
            self.ui.combo_roles_2.setCurrentIndex(-1)
        # Link comboboxes and display fields
        self.ui.combo_roles.activated.connect(lambda x: self.ui.roles.setText(\
          self.ontoPRO[self.ui.combo_roles.currentText()]))
        self.ui.combo_roles_2.activated.connect(lambda x: self.ui.roles_2.setText(\
          self.ontoPRO[self.ui.combo_roles_2.currentText()]))    
        # Enable comboboxes
        self.ui.combo_roles.setEnabled(True)
        self.ui.combo_roles_2.setEnabled(True)



        

    def searchOrganism(self, *args):
        self.ols = OlsDialog(self)
        self.ols.SigSelected.connect(self.updateOrganism)
        x = self.ols.show()

    def searchOrganismPart(self):
        self.ols = OlsDialog(self)
        self.ols.SigSelected.connect(self.updateOrganismPart)
        self.ols.show()

    def searchOrganismVariant(self):
        self.ols = OlsDialog(self)
        self.ols.SigSelected.connect(self.updateOrganismVariant)
        self.ols.show()

    def updateOrganism(self, jsontology):
        ontology = json.loads(jsontology)
        if ontology is not None:
            self.ui.name_organism.setText(ontology['label'])
            self.ui.ref_organism.setText(ontology['ontology_prefix'].upper())
            self.ui.iri_organism.setText(ontology['iri'])
        else:
            self.ui.name_organism.setText('')
            self.ui.ref_organism.setText('')
            self.ui.iri_organism.setText('')
        
    def updateOrganismPart(self, jsontology):
        ontology = json.loads(jsontology)
        if ontology is not None:
            self.ui.name_organism_part.setText(ontology['label'])
            self.ui.ref_organism_part.setText(ontology['ontology_prefix'])
            self.ui.iri_organism_part.setText(ontology['iri'])
        else:
            self.ui.name_organism_part.setText('')
            self.ui.ref_organism_part.setText('')
            self.ui.iri_organism_part.setText('')

    def updateOrganismVariant(self, jsontology):
        ontology = json.loads(jsontology)
        if ontology is not None:
            self.ui.name_organism_variant.setText(ontology['label'])
            self.ui.ref_organism_variant.setText(ontology['ontology_prefix'])
            self.ui.iri_organism_variant.setText(ontology['iri'])
        else:
            self.ui.name_organism_variant.setText('')
            self.ui.ref_organism_variant.setText('')
            self.ui.iri_organism_variant.setText('')



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



if __name__=='__main__':

    app = QApplication(sys.argv)
    um = UserMetaDialog()
    um.SigUpdateMetadata.connect(lambda x: print(x))
    um.show()
    sys.exit(app.exec_())
