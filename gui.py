import pymel.core as pCore
from Qt import QtGui, QtWidgets, QtCore
from maya.app.general.mayaMixin import *


class SetDrivenKeyToolBoxGui(MayaQWidgetDockableMixin, QWidget):
    def __init__(self, parent=None):
        super(SetDrivenKeyToolBoxGui, self).__init__(parent)
        self.setWindowTitle("Set Driven Key ToolBox")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # Driver Section

        self.driverLE = QtWidgets.QLineEdit(self)
        self.setDriverPB = QtWidgets.QPushButton("Set Driver")
        labelDriver = QtWidgets.QLabel("Set Driver")

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(labelDriver)
        layout.addWidget(self.driverLE)
        layout.addWidget(self.setDriverPB)
        self.mainLayout.addLayout(layout)

        self.driverChannelLW = QtWidgets.QListWidget()
        self.mainLayout.addWidget(self.driverChannelLW)

        # Driven Section

        self.drivenLE = QtWidgets.QLineEdit(self)
        self.setDrivenPB = QtWidgets.QPushButton("Set Driven")
        labelDriven = QtWidgets.QLabel("Set Driven")
        self.attributeFilter = QLineEdit(self)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(labelDriven)
        layout.addWidget(self.drivenLE)
        layout.addWidget(self.setDrivenPB)
        self.mainLayout.addLayout(layout)

        self.drivenChannelLV = QtWidgets.QListView(self)
        self.drivenAttrModel = QStringListModel()
        self.filterModel = QtCore.QSortFilterProxyModel()
        self.filterModel.setSourceModel(self.drivenAttrModel)
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.drivenChannelLV.setModel(self.filterModel)
        self.drivenChannelLV.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.mainLayout.addWidget(self.attributeFilter)
        self.mainLayout.addWidget(self.drivenChannelLV)

        self.keyPB = QtWidgets.QPushButton("KEY")
        self.mainLayout.addWidget(self.keyPB)

        self.attributeFilter.textChanged.connect(self.filterModel.setFilterWildcard)

        self.driverNode = None
        self.drivenNode = None
        self.setDriverPB.clicked.connect(self.fill)
        self.setDrivenPB.clicked.connect(self.fill)
        self.keyPB.clicked.connect(self.key)
        self.driverChannelLW.itemDoubleClicked.connect(self.selectDriver)
        self.drivenChannelLV.doubleClicked.connect(self.selectDriven)


    def selectDriver(self, item):
        pCore.select(self.driverNode)

    def selectDriven(self, selectedIndex):
        app = QtWidgets.QApplication.instance()

        modifiers = app.keyboardModifiers()

        if modifiers == Qt.ControlModifier:
            sourceIndex = self.filterModel.mapToSource(selectedIndex)
            drivenAttrNode = self.drivenNode + "." + self.drivenAttrModel.data(sourceIndex, Qt.DisplayRole)
            pAttr = pCore.PyNode(drivenAttrNode)
            attrType = pAttr.type()
            try:
                attrMin = pAttr.getMin() if pAttr.getMin() else -9999
                attrMax = pAttr.getMax() if pAttr.getMax() else 9999
            except:
                attrMin = -9999
                attrMax = 9999

            result = None

            if attrType in ["float", "int", "doubleLinear", "doubleAngle"]:
                if attrType == "float":
                    attrMax = float(attrMax)
                    attrMin = float(attrMin)
                    result = QtWidgets.QInputDialog.getDouble(self, "Set Value", "Node %s" % drivenAttrNode, pAttr.get(), attrMin, attrMax)
                else:
                    attrMax = int(attrMax)
                    attrMin = int(attrMin)
                    result = QtWidgets.QInputDialog.getDouble(self, "Set Value", "Node %s" % drivenAttrNode, pAttr.get(), attrMin, attrMax)

            if result[1]:
                pAttr.set(result[0])

                self.drivenChannelLV.setCurrentIndex(selectedIndex)

        else:
            pCore.select(self.drivenNode)


    def fill(self):

        if self.sender() == self.setDriverPB:
            node = pCore.selected()[0]
            self.driverLE.setText(node.name())
            self.driverNode = node.name()
            attrs = node.listAttr(k=True)
            attrs = [a.attrName(longName=True) for a in attrs]
            self.driverChannelLW.clear()
            for a in attrs:
                self.driverChannelLW.addItem(a)
        else:
            node = pCore.selected()[0]
            self.drivenNode = node
            self.drivenLE.setText(node.name())
            self.drivenNode = node.name()
            if node.type() != "blendShape":
                attrs = node.listAttr(k=True)
                attrs = [a.attrName(longName=True) for a in attrs]
            else:
                attrs = pCore.listAttr(node.w, m=True)
            self.drivenAttrModel.setStringList(attrs)


    def key(self):
        selectedIndex = self.drivenChannelLV.selectedIndexes()[0]
        sourceIndex = self.filterModel.mapToSource(selectedIndex)
        drivenAttrNode = self.drivenNode + "." + self.drivenAttrModel.data(sourceIndex, Qt.DisplayRole)
        driverAttrNode = self.driverNode + "." + self.driverChannelLW.selectedItems()[0].text()
        # setDrivenKeyframe -currentDriver mouthCnr_ctrl.translateX blendshape_blends_node.l_lipNarrow;
        pCore.setDrivenKeyframe( drivenAttrNode, cd=driverAttrNode )