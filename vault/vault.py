#!/usr/bin/python
# -*- coding: utf-8 -*-

#!/usr/bin/python

# Copyright (C) 2012 Chris Triantafillis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import platform
import os
import signal
import subprocess
import shlex
import shutil
import pickle
import re
import time
import tempfile
import webbrowser

import passwd_dlg
import createpasswd_dlg
import qrc_resources

__version__ = "1.0.0" 
py_version = platform.python_version()

if not (py_version >= '2.6' and py_version < '3'):
    exit('Error: You need python 2.6 or python2.7 to run this program.')
    
try:
    import PyQt4
except ImportError:
    exit('Error: You need PyQt4 to run this program.') 

ECHO = "/bin/echo"
ENCFS = "/usr/bin/encfs"
FUSERMOUNT = "/bin/fusermount"
MOUNT = "/bin/mount"
home = os.getenv('HOME')
efolders = home + '/.vault/cache/existing_folders.data'
ofolders = home + '/.vault/cache/open_folders.data'

class Vault(QMainWindow):
    def __init__(self, parent=None):
        super(Vault, self).__init__(parent)
        
        tabWidget = QTabWidget()
        
        createWidget = QWidget()
        self.createLabel = QLabel(self.tr("Folder name:"))
        self.createLineEdit = QLineEdit()
        self.continueButton = QPushButton(self.tr("Continue"))
        self.continueButton.setDefault(0)
        createLayout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout1.addWidget(self.createLabel)
        layout1.addWidget(self.createLineEdit)
        layout1.addStretch()
        layout2 = QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addStretch()
        layout3 = QHBoxLayout()
        layout3.addStretch()
        layout3.addWidget(self.continueButton)
        createLayout.addLayout(layout1)
        createLayout.addLayout(layout2)
        createLayout.addLayout(layout3)
        createWidget.setLayout(createLayout)
        tabWidget.addTab(createWidget, self.tr("&Create"))

        openWidget = QWidget()
        openLayout = QVBoxLayout()
        self.existingfoldersListWidget = QListWidget()
        self.openLabel = QLabel(self.tr("Choose a folder from the list:"))
        openLayout.addWidget(self.openLabel)
        openLayout.addWidget(self.existingfoldersListWidget)
        openWidget.setLayout(openLayout)
        tabWidget.addTab(openWidget, self.tr("&Open"))

        closeWidget = QWidget()
        closeLayout = QVBoxLayout()
        self.openfoldersListWidget = QListWidget()
        self.closeLabel = QLabel(self.tr("Choose a folder from the list:"))
        self.dmpointCheckBox = QCheckBox(self.tr("Delete mount point"))
        self.dmpointCheckBox.setChecked(True)
        closeLayout.addWidget(self.closeLabel)
        closeLayout.addWidget(self.openfoldersListWidget)
        closeLayout.addWidget(self.dmpointCheckBox)
        closeWidget.setLayout(closeLayout)
        tabWidget.addTab(closeWidget, self.tr("Clo&se"))
        
        deleteWidget = QWidget()
        deleteLayout = QVBoxLayout()
        self.deleteLabel = QLabel(self.tr("Choose a folder from the list:"))
        self.dexistingfoldersListWidget = QListWidget()
        self.dmpointdCheckBox = QCheckBox(self.tr("Delete mount point"))
        self.dencryptedfolder = QCheckBox(self.tr("Delete encrypted folder"))
        self.dmpointdCheckBox.setChecked(True)
        deleteLayout.addWidget(self.deleteLabel)
        deleteLayout.addWidget(self.dexistingfoldersListWidget)
        deleteLayout.addWidget(self.dmpointdCheckBox)
        deleteLayout.addWidget(self.dencryptedfolder)
        deleteWidget.setLayout(deleteLayout)
        tabWidget.addTab(deleteWidget, self.tr("&Delete"))
        
        settings = QSettings()
        
        tabWidget.setCurrentIndex(1)
        layout = QVBoxLayout()
        layout.addWidget(tabWidget)
        self.setCentralWidget(tabWidget)
        self.resize(400, 150)
        self.setWindowTitle('Vault')
        
        exitAction = QAction(QIcon(''), self.tr("&Exit"), self) 
        exitAction.setShortcut("Ctrl+Q")
    
        reportAction = QAction(QIcon(''), self.tr("&Report a bug!"), self) 
        reportAction.setShortcut("Ctrl+R")
        
        aboutAction = QAction(QIcon(''), self.tr("&About"), self)
        aboutAction.setShortcut("Ctrl+A")
        
        involvedAction = QAction(QIcon(''), self.tr("Get &Involved!"), self)
        involvedAction.setShortcut("Ctrl+I")
        
        vaultMenu = self.menuBar().addMenu(self.tr("Vault"))
        helpMenu = self.menuBar().addMenu(self.tr("Help"))
        vaultMenu.addAction(exitAction)
        helpMenu.addAction(reportAction)
        helpMenu.addAction(involvedAction)
        helpMenu.addAction(aboutAction)
        
        self.connect(exitAction, SIGNAL("triggered()"), self.close)
        self.connect(reportAction, SIGNAL("triggered()"), self.report)
        self.connect(involvedAction, SIGNAL("triggered()"), self.getinvolved)
        self.connect(aboutAction, SIGNAL("triggered()"), self.about)
        self.connect(self.continueButton, SIGNAL("clicked()"), self.create_folder)
        self.existingfoldersListWidget.doubleClicked.connect(self.open_folder)
        self.openfoldersListWidget.doubleClicked.connect(self.close_folder)
        self.dexistingfoldersListWidget.doubleClicked.connect(self.delete)
        
    def create_folder(self):
        foldername = str(self.createLineEdit.text().toUtf8())
        self.createLineEdit.clear()
        folderdir = home + '/' + foldername
        enfolderdir = home + '/' + '.' + foldername
        if not os.path.exists(folderdir):
            os.mkdir(folderdir, 0700)
        if not os.path.exists(enfolderdir):
            os.mkdir(enfolderdir, 0700)
        dialog = createpasswd_dlg.createpasswd()
        if dialog.exec_():
            pass1 = dialog.createpasswdEdit.text()
            pass2 = dialog.ccreatepasswdEdit.text()
        tmp = tempfile.mkstemp()[1]
        with open(tmp, 'w') as f:
            f.write(pass1)
        extpass = "/bin/cat %s" % (tmp)
        p2 = subprocess.Popen([ENCFS, "--standard","--extpass", extpass, enfolderdir, folderdir],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        output = p2.communicate()[0]
        os.remove(tmp)
        if p2.poll == 0:
            nautilusfolder = 'nautilus {0}'.format(folderdir)
            subprocess.call(shlex.split(nautilusfolder))
            self.load_folders()
            self.efoldersdata.append(foldername)
            f = open(efolders, 'wb')
            pickle.dump(self.efoldersdata, f)
            f.close()
            self.ofoldersdata.append(foldername)
            f = open(ofolders, 'wb')
            pickle.dump(self.ofoldersdata, f)
            f.close()
            self.load_lists()
        else:
            QMessageBox.warning(self, self.tr("Error"),
            self.tr("The application encounter an error and the folders weren't created!"))
       
    def open_folder(self):
        item = self.existingfoldersListWidget.currentItem()
        foldername = item.text()
        path = home + '/' + foldername
        enfolder = home + '/' + '.' + foldername
        if not os.path.exists(path):
            os.mkdir(path)
        dialog = passwd_dlg.passwd()
        if dialog.exec_():
            passwd = dialog.passwdEdit.text()
        passwd = dialog.passwdEdit.text() 
        p1 = subprocess.Popen([ECHO, passwd], stdout=subprocess.PIPE)
        p2 = subprocess.Popen([ENCFS, "-S", enfolder, path], stdin=p1.stdout, stdout=subprocess.PIPE)
        p3 = p2.communicate()[0]
        if p2.poll() is not 0:
            QMessageBox.warning(self, self.tr("Something is wrong"),
            self.tr("Something is wrong, check the password again. Also check if the folder is still open.")) 
        else:
            nautilusfolder = 'nautilus {0}'.format(path)
            subprocess.call(shlex.split(nautilusfolder))
            self.load_folders()
            self.ofoldersdata.append(foldername)
            f = open(ofolders, 'wb')
            pickle.dump(self.ofoldersdata, f)
            f.close()
            self.load_lists()
            
    def close_folder(self):
        item = self.openfoldersListWidget.currentItem()
        self.foldername = item.text()
        self.close_foldername = home + '/' + self.foldername
        p1 = subprocess.Popen([FUSERMOUNT, "-u", self.close_foldername], stdin=None, stdout=subprocess.PIPE)
        while p1.poll() is None:
            time.sleep(1)
        if p1.returncode is not 0:
            reply = QMessageBox.question(self, self.tr('Folder is busy'),
                    self.tr("The folder is probably busy, do you want to close it anyway?"), QMessageBox.Yes | 
                    QMessageBox.No)
            if reply == QMessageBox.Yes:
                p1 = subprocess.Popen([FUSERMOUNT, "-z", "-u", self.close_foldername], stdin=None, stdout=subprocess.PIPE)
                p2 = p1.communicate()[0]
            elif reply == QMessageBox.No:
                QMessageBox.information(self, self.tr('Close folder'), self.tr('Close all programs that keep the folder busy and press ok.'))
                p1 = subprocess.Popen([FUSERMOUNT, "-u", self.close_foldername], stdin=None, stdout=subprocess.PIPE)
                p2 = p1.communicate()[0]
            if p1.poll() is not 0:
                QMessageBox.warning(self, self.tr("Error"),
                self.tr("An error occur while unmounting the folder!"))
            else:
                self.close_commands()
        else:
            self.close_commands()
                
    def close_commands(self):
        if self.dmpointCheckBox.isChecked():
            try:
                shutil.rmtree(self.close_foldername, True)
            except IOError:
                pass
        self.load_folders()
        for name in self.ofoldersdata:
            if name == self.foldername:
                self.ofoldersdata.remove(self.foldername)
        f = open(ofolders, 'wb')
        pickle.dump(self.ofoldersdata, f)
        f.close()
        self.load_lists()
        
    def delete(self):
        item = self.dexistingfoldersListWidget.currentItem()
        foldername = str(item.text())
        self.delete_folder = home + '/' + foldername
        self.delete_enfolder = home + '/' + '.' + foldername 
        if self.is_mounted() is False:
            if self.dmpointdCheckBox.isChecked():
                try:
                    shutil.rmtree(self.delete_folder, True)
                except IOError:
                    pass
            if self.dencryptedfolder.isChecked():
                try:
                    shutil.rmtree(self.delete_enfolder, True)
                except IOError:
                    pass
            self.load_folders()
            self.efoldersdata.remove(foldername)
            f = open(efolders, 'wb')
            pickle.dump(self.efoldersdata, f)
            f.close()
            self.load_lists()
        else:
            QMessageBox.warning(self, self.tr("The folder is mounted!"),
            self.tr("If you want to delete this folder, you must close it first!"))
            
    def is_mounted(self):
        p = subprocess.Popen([MOUNT], stdout=subprocess.PIPE)
        p = p.communicate()[0]
        p = p.split("\n")
        r = re.compile("^encfs on %s type fuse" % self.delete_folder)
        for l in p:
            if r.match(l):
                return True
            else:
                return False
        
    def load_folders(self):
        self.efoldersdata = []
        self.ofoldersdata = []
        f = open(efolders, 'rb')
        try:
            self.efoldersdata = pickle.load(f)
        except (EOFError, IOError):
            pass
        f.close()
        f = open(ofolders, 'rb')
        try:
            self.ofoldersdata = pickle.load(f)
        except (EOFError, IOError):
            pass
        f.close()
        
    def load_lists(self):
        self.existingfoldersListWidget.clear()
        self.existingfoldersListWidget.addItems(self.efoldersdata)
        self.existingfoldersListWidget.setCurrentRow(0)
        self.dexistingfoldersListWidget.clear()
        self.dexistingfoldersListWidget.addItems(self.efoldersdata)
        self.dexistingfoldersListWidget.setCurrentRow(0)
        self.openfoldersListWidget.clear()
        self.openfoldersListWidget.addItems(self.ofoldersdata)
        self.openfoldersListWidget.setCurrentRow(0)
        
    def about(self):
        link  = ''
        link += 'Vault'
        QMessageBox.about(self, self.tr("About Vault"), self.tr(
            '''<b> Vault %1 </b>
            <p>Create and manage encrypted folders using encfs.
            <p><a href="%2">Vault</a>
            <p>Copyright &copy; Chris Triantafillis  
            <br>License: GNU GPL3
            <p>Python %3 - Qt %4 - PyQt %5 on %6''').arg(__version__).arg(link)
            .arg(platform.python_version()[:5]).arg(QT_VERSION_STR)
            .arg(PYQT_VERSION_STR).arg(platform.system()))
    
    def report(self):
        url = ''
        webbrowser.open_new_tab(url)

    def getinvolved(self):
        url = ''
        webbrowser.open_new_tab(url)
        
def main():
    app = QApplication(sys.argv)
    
    locale = QLocale.system().name()
    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + locale, ":/"):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    if appTranslator.load("vault_" + locale, ":/"):
        app.installTranslator(appTranslator)
    
    program = Vault()
    program.load_folders()
    program.load_lists()
    program.show()
    app.exec_() 

if __name__ == '__main__':
    main()
