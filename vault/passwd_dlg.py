#!/usr/bin/python
# -*- coding: utf-8 -*-


from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys

class passwd(QDialog):
    
    def __init__(self, parent=None):
        super(passwd, self).__init__(parent)
        
        self.label = QLabel(self.tr("Password"))
        self.passwdEdit = QLineEdit()
        okButton = QPushButton(self.tr("Ok"))
        layout1 = QGridLayout()
        layout1.addWidget(self.label, 0, 0)
        layout1.addWidget(self.passwdEdit, 0, 1)
        layout1.addWidget(okButton, 1, 1)
        
        self.passwdEdit.setEchoMode(2)
        self.setLayout(layout1)
        self.setWindowTitle(self.tr("Password"))
        
        self.connect(okButton, SIGNAL("clicked()"), self.accept)

