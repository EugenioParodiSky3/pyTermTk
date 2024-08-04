# MIT License
#
# Copyright (c) 2024 Eugenio Parodi <ceccopierangiolieugenio AT googlemail DOT com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__all__ = ['TTkTable']

from TermTk.TTkCore.constant import TTkK
from TermTk.TTkWidgets.TTkModelView.tablewidget import TTkTableWidget
from TermTk.TTkAbstract.abstractscrollarea import TTkAbstractScrollArea

class TTkTable(TTkAbstractScrollArea):
    __slots__ = (
        '_tableView',
        # Forwarded Signals
        'itemActivated', 'itemChanged', 'itemClicked', 'itemExpanded', 'itemCollapsed', 'itemDoubleClicked',
        # Forwarded Methods
        'setModel', 'setSortingEnabled',
        'resizeColumnsToContents',

        # Forwarded Methods From TTkTree
        'setHeaderLabels',
        'setColumnWidth', 'resizeColumnToContents',
        # 'appendItem', 'setAlignment', 'setColumnColors', 'setColumnSize', 'setHeader',
        'addTopLevelItem', 'addTopLevelItems', 'takeTopLevelItem', 'topLevelItem', 'indexOfTopLevelItem', 'selectedItems', 'clear' )

    def __init__(self, *, parent=None, visible=True, **kwargs):
        super().__init__(parent=parent, visible=visible, **kwargs)
        self._tableView = kwargs.get('TableWidget',TTkTableWidget(**kwargs))
        self.setViewport(self._tableView)
        self.setFocusPolicy(TTkK.ClickFocus)

        self.setModel = self._tableView.setModel
        self.setSortingEnabled = self._tableView.setSortingEnabled
        self.resizeColumnsToContents = self._tableView.resizeColumnsToContents

        # # Forward the signal
        # self.itemActivated     = self._tableView.itemActivated
        # self.itemChanged       = self._tableView.itemChanged
        # self.itemClicked       = self._tableView.itemClicked
        # self.itemDoubleClicked = self._tableView.itemDoubleClicked

        # # Forwarded Methods
        # #self.setAlignment    = self._tableView.setAlignment
        # #self.setHeader       = self._tableView.setHeader
        # self.setHeaderLabels = self._tableView.setHeaderLabels
        # #self.setColumnSize   = self._tableView.setColumnSize
        # #self.setColumnColors = self._tableView.setColumnColors
        # #self.appendItem      = self._tableView.appendItem
        # self.selectedItems       = self._tableView.selectedItems
        # self.setColumnWidth         = self._tableView.setColumnWidth
        # self.resizeColumnToContents = self._tableView.resizeColumnToContents

        # self.clear           = self._tableView.clear
