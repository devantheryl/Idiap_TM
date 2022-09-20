"""plannificateur permet l'ordonancement des lots sur la chaine de production"""


import src.Exploit as exploit

import sys

from functools import partial

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtCore import QDateTime, QDir
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDateEdit

from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QFileDialog

__version__ = "0.1"
__author__ = "Lucas Devanthéry"

ERROR_MSG = "ERROR"


# Create a subclass of QMainWindow to setup the calculator's GUI
class PyCalcUi(QMainWindow):
    """PyCalc's View (GUI)."""

    def __init__(self):
        """View initializer."""
        super().__init__()
        # Set some main window's properties
        self.setWindowTitle("Plannificateur")
        #self.setFixedSize(600, 600)
        # Set the central widget and the general layout
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        
        self.buttons = {}
        
        # Create the display and the buttons
        self._createDisplay()
        self._createButtons()

    def _createDisplay(self):
        """Create the display layout."""
        self.display_layout = QVBoxLayout()
        
        """get the excel filename"""
        self.filename_button = QPushButton("Excel File")
        self.buttons["Excel_file"] = self.filename_button
        self.filename_label = QLabel("")
        
        
        """Formulation comboxBox"""
        self.formulation_comboxBox = QComboBox()
        self.formulation_comboxBox.addItems(["3.75","11.25","22.5"])
        self.formulation_label = QLabel("Formulation :")
        self.formulation_label.setBuddy(self.formulation_comboxBox)
        
        """scale comboxBox"""
        self.scale_comboxBox = QComboBox()
        self.scale_comboxBox.addItems(["20000","6600"])
        self.scale_label = QLabel("Scale :")
        self.scale_label.setBuddy(self.scale_comboxBox)
        
        """target DateEdit"""
        self.target_dateEdit = QDateEdit()
        self.target_dateEdit.setDateTime(QDateTime.currentDateTime())
        self.target_dateEdit.setCalendarPopup(True)
        
        self.target_label = QLabel("Target Time :")
        self.target_label.setBuddy(self.target_dateEdit)
        
        """batch LineEdit"""
        self.batch_lineEdit = QLineEdit()
        self.batch_label = QLabel("Batch number :")
        self.batch_label.setBuddy(self.batch_lineEdit)
        
        
        """batch stock plainTextEdit"""
        self.batchList_plainText = QPlainTextEdit()
        self.batchList_label = QLabel("Batch list :")
        self.batchList_label.setBuddy(self.batchList_plainText)
        
        
   
        # Add the display to the general layout
        self.display_layout.addWidget(self.filename_button)
        self.display_layout.addWidget(self.filename_label)
        
        self.display_layout.addWidget(self.formulation_label)
        self.display_layout.addWidget(self.formulation_comboxBox)
        
        self.display_layout.addWidget(self.scale_label)
        self.display_layout.addWidget(self.scale_comboxBox)
        
        self.display_layout.addWidget(self.target_label)
        self.display_layout.addWidget(self.target_dateEdit)
        
        self.display_layout.addWidget(self.batch_label)
        self.display_layout.addWidget(self.batch_lineEdit)
        
        self.display_layout.addWidget(self.batchList_label)
        self.display_layout.addWidget(self.batchList_plainText)
        
        self.generalLayout.addLayout(self.display_layout)

    def _createButtons(self):
        """Create the buttons."""
        
        buttonsLayout = QGridLayout()
        # Button text | position on the QGridLayout
        buttons = {
            "Add": (0, 0),
            "Remove" : (0, 1),
            "Run": (0, 2),
            
        }
        # Create the buttons and add them to the grid layout
        for btnText, pos in buttons.items():
            self.buttons[btnText] = QPushButton(btnText)
            buttonsLayout.addWidget(self.buttons[btnText], pos[0], pos[1])
        # Add buttonsLayout to the general layout
        self.generalLayout.addLayout(buttonsLayout)



# Create a Model to handle the calculator's operation
def evaluateExpression(expression):
    """Evaluate an expression."""
    pass


# Create a Controller class to connect the GUI and the model
class PyCalcCtrl:
    """PyCalc's Controller."""

    def __init__(self, model, view):
        """Controller initializer."""
        self._evaluate = model
        self._view = view
        self.batch_dict = {}
        # Connect signals and slots
        self._connectSignals()

    def _runPlanning(self):
        """Evaluate expressions."""
        
        batch_names = []
        formulations = []
        scales = []
        targets = []
        filename= self._view.filename_label.text()
        
        formulation_driver = {
                "3.75" :1,
                "11.25" : 3,
                "22.5" : 6
            }
        for key,value in self.batch_dict.items():
            batch_names.append(key)
            formulations.append(formulation_driver[value["formulation"]])
            scales.append(int(value["scale"]))
            targets.append(value["target"])
        exploit.make_planning(batch_names, formulations, scales, targets, filename)
    
    def _addBatch(self):
        batch_number = self._view.batch_lineEdit.text()
        formulation = self._view.formulation_comboxBox.currentText()
        scale = self._view.scale_comboxBox.currentText()
        target = self._view.target_dateEdit.date().toString("yyyy-MM-dd") + " 00:00:00"
        target_year = str(self._view.target_dateEdit.date().year())[-2:]
        
        batch = "PROD-" + target_year + "-" + formulation + "-" + batch_number
        
        if batch not in self.batch_dict.keys():  
            self._view.batchList_plainText.insertPlainText(batch + " " + target + "\n")
            
            self.batch_dict[batch] = {
                    "formulation" : formulation,
                    "scale" : scale,
                    "target" : target
                }
            
        
    def _removeBatch(self):
        print(self._view.batchList_plainText.toPlainText().split("\n")[:-1])
        if self.batch_dict:
            self.batch_dict.popitem()
        
            new_text = ""
            for t in self._view.batchList_plainText.toPlainText().split("\n")[:-2]:
                new_text = new_text + t + "\n"
            self._view.batchList_plainText.setPlainText(new_text)
            
            
    def _browseFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self._view, 'Single File', QDir.rootPath() , '*.xlsm')
        self._view.filename_label.setText(str(fileName))

    def _connectSignals(self):
        """Connect signals and slots."""
        self._view.buttons["Add"].clicked.connect(partial(self._addBatch))
        self._view.buttons["Remove"].clicked.connect(partial(self._removeBatch))
        self._view.buttons["Run"].clicked.connect(partial(self._runPlanning))
        self._view.buttons["Excel_file"].clicked.connect(partial(self._browseFile))
        

        


# Client code
def main():
    """Main function."""
    # Create an instance of `QApplication`
    pycalc = QApplication(sys.argv)
    # Show the calculator's GUI
    view = PyCalcUi()
    view.show()
    # Create instances of the model and the controller
    model = evaluateExpression
    PyCalcCtrl(model=model, view=view)
    # Execute calculator's main loop
    sys.exit(pycalc.exec_())


if __name__ == "__main__":
    main()
