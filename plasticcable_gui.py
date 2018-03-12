#!/usr/bin/python
from PyQt4 import QtGui, QtCore
import sys, sqlite3, os, signal, time

#to import PyQt4:
#https://stackoverflow.com/a/22651895
#pip install PyQt4-4.11.4-cp36-cp36m-win_amd64.whl

signal.signal(signal.SIGINT, signal.SIG_DFL) #So we can Ctrl+C out

updateTimer = QtCore.QTimer()

DEBUG=False
def debugPrint(str):
  if(DEBUG):
    print(str)
    
#thanks qt creator!
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
      
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
      
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.centralWidget = QtGui.QGroupBox(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))

        form = QtGui.QGridLayout()

        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(770, 200)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)


        self.treeView = QtGui.QTreeView(self.centralWidget)
        self.treeView.setSortingEnabled(True)
        self.treeView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.treeView.setGeometry(QtCore.QRect(10, 40, 301, 141))
        self.treeView.setObjectName(_fromUtf8("treeView"))
        form.addWidget(self.treeView, 2, 0)


        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 320, 22))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MainWindow)
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
        MainWindow.setCentralWidget(self.centralWidget)

        self.centralWidget.setLayout(form)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "PlasticCable", None))



class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    global config

    def __init__(self, win_parent=None):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        
    def closeEvent(self, event):
        #if (readconfig(self,"MinimizeToTray")):
            self.hide()
            event.ignore()
        #else:
        #    event.accept()
        
class TrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, win_parent=None):
        QtGui.QMainWindow.__init__(self, win_parent)

        self.setToolTip("PlasticCable")

        #menu icons below, currently empty
        OpenIcon = QtGui.QIcon("") #needs icon?
        SettingsIcon = QtGui.QIcon("") #needs icon?
        AboutIcon = QtGui.QIcon("") #needs icon?
        QuitIcon = QtGui.QIcon("") #needs icon?

        #right click menu content
        global OpenAction
        global AboutAction
        global QuitAction
        ActionsMenu = QtGui.QMenu()
        OpenAction = ActionsMenu.addAction(OpenIcon, "Open PlasticCable...")
        ActionsMenu.addSeparator()
        SettingsAction = ActionsMenu.addAction(SettingsIcon, "Settings")
        AboutAction = ActionsMenu.addAction(AboutIcon, "About")
        ActionsMenu.addSeparator()
        QuitAction = ActionsMenu.addAction(QuitIcon, "Exit")

        # -- Now add the menu:
        # -- trigger the check action to set current state
        self.setContextMenu(ActionsMenu)
        
        # -- connect the actions:
        self.connect(OpenAction, QtCore.SIGNAL("triggered()"), showSearchScreen)
        self.connect(SettingsAction, QtCore.SIGNAL("triggered()"), showSettingScreen)
        self.connect(AboutAction, QtCore.SIGNAL("triggered()"), showAbout)
        self.connect(QuitAction, QtCore.SIGNAL("triggered()"), exitProperly)

def showSearchScreen():
    global main_window
    main_window.show()

def showSettingScreen():
    QtGui.QMessageBox.information(main_window, "Settings screen missing", "Not in yet.")
    #settings_window.show()
    
def showAbout():
    QtGui.QMessageBox.information(main_window, "About", "PlasticCable, crappy Glasswire clone, by zaggynl")
    
def exitProperly():
    sys.exit(0)   

def loadDatabase():
  #while(True):
    if not(os.path.isfile('plasticcable.db')):
      QtGui.QMessageBox.warning(main_window, "Error", "Error: database file \'plasticcable.db\' missing")
      os.exit(1)
    try:
      debugPrint ("DEBUG-loadDatabase()")
      conn = sqlite3.connect('plasticcable.db')
      debugPrint("DEBUG-Currently in database:")
      sqlreturned = conn.execute('''SELECT NAME, PATH, HASH, DESTIP, DESTPORT, DESTHOST, DATE FROM APPS''')
      queryresult =  sqlreturned.fetchall()
      rowcount = len(queryresult)
      conn.close()
    except Exception as e:
      try:
        conn.close()
      except Exception as e2:
        pass
        exit("Error:"+str(e))
    debugPrint  ("DEBUG-sqlreturned.rowcount="+str(rowcount))
    if rowcount > 0:
      viewmodel = QtGui.QStandardItemModel()
 
      for row in queryresult:
        row = list(row)
        row2 = []
        for item in row:
          item = QtGui.QStandardItem(item)
          row2.append(item)
        viewmodel.appendRow(row2)
      main_window.treeView.setModel(viewmodel)
      viewmodel.setHeaderData(0, QtCore.Qt.Horizontal, "NAME")
      viewmodel.setHeaderData(1, QtCore.Qt.Horizontal, "PATH")
      viewmodel.setHeaderData(2, QtCore.Qt.Horizontal, "HASH")      
      viewmodel.setHeaderData(3, QtCore.Qt.Horizontal, "DESTIP")
      viewmodel.setHeaderData(4, QtCore.Qt.Horizontal, "DESTPORT")      
      viewmodel.setHeaderData(5, QtCore.Qt.Horizontal, "DESTHOST")      
      viewmodel.setHeaderData(6, QtCore.Qt.Horizontal, "DATE") 
      main_window.treeView.sortByColumn(6) #sort by date
    else:
            QtGui.QMessageBox.information(main_window, "Database message", "Database is empty, did you run plasticcable_cli.py yet?")
    
            
if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  app.connect(updateTimer, QtCore.SIGNAL("timeout()"), loadDatabase)
  #The Main window
  main_window = MainWindow()
  main_window.show()
  #The tray icon
  tray_icon = TrayIcon()
  tray_icon.show()
  # Enter the main loop
  updateTimer.start(1000)
  app.exec_()
    
  