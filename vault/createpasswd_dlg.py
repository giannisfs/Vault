# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class createpasswd(QDialog):
    
    def __init__(self, parent=None):
        super(createpasswd, self).__init__(parent)
        
        self.label1 = QLabel(self.tr("EncFS password:"))
        self.label2 = QLabel(self.tr("Confirm EncFS password:"))
        self.label3 = QLabel(self.tr("<b>Passwords do not match!</b>"))
        self.label4 = QLabel(self.tr("<b>Password cannot be empty!<b>"))
        self.createpasswdEdit = QLineEdit()
        self.ccreatepasswdEdit = QLineEdit()
        self.okButton2 = QPushButton(self.tr("Ok"))
        layout = QGridLayout()
        layout.addWidget(self.label3, 0, 0)
        layout.addWidget(self.label1, 1, 0)
        layout.addWidget(self.createpasswdEdit, 1, 1)
        layout.addWidget(self.label2, 2, 0)
        layout.addWidget(self.ccreatepasswdEdit, 2, 1)
        layout.addWidget(self.okButton2, 3, 1)
        
        self.label3.setVisible(0)
        self.label4.setVisible(0)
        self.createpasswdEdit.setEchoMode(2)
        self.ccreatepasswdEdit.setEchoMode(2)
        self.setLayout(layout)
        self.setWindowTitle(self.tr("Password"))
        
        self.connect(self.okButton2, SIGNAL("clicked()"), self.accept)
                 
