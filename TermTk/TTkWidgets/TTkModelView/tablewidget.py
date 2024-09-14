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


__all__ = ['TTkTableWidget']

from TermTk.TTkCore.log import TTkLog
from TermTk.TTkCore.cfg import TTkCfg
from TermTk.TTkCore.constant import TTkK
from TermTk.TTkCore.string import TTkString
from TermTk.TTkCore.color import TTkColor
from TermTk.TTkCore.signal import pyTTkSignal, pyTTkSlot

from TermTk.TTkGui.textdocument import TTkTextDocument

from TermTk.TTkWidgets.texedit  import TTkTextEdit, TTkTextEditView
from TermTk.TTkWidgets.lineedit import TTkLineEdit
from TermTk.TTkWidgets.spinbox  import TTkSpinBox
from TermTk.TTkWidgets.TTkPickers.textpicker import TTkTextPicker, TTkTextDialogPicker

from TermTk.TTkAbstract.abstractscrollview import TTkAbstractScrollView
from TermTk.TTkAbstract.abstracttablemodel import TTkAbstractTableModel

class _DefaultTableModel(TTkAbstractTableModel):
    def __init__(self, **args):
        super().__init__(**args)
    def rowCount(self):
        return 15
    def columnCount(self):
        return 10
    def data(self, row, col):
        return f"{row}x{col}"

class _HeaderView():
    '''_HeaderView
    This is a placeholder for a future "TTkHeaderView"
    '''
    __slots__ = ('_visible','visibilityUpdated')
    def __init__(self) -> None:
        self.visibilityUpdated = pyTTkSignal(bool)
        self._visible = True

    @pyTTkSlot(bool)
    def setVisible(self, visible: bool):
        '''setVisible'''
        if self._visible == visible: return
        self._visible = visible
        self.visibilityUpdated.emit(visible)

    @pyTTkSlot()
    def show(self):
        '''show'''
        self.setVisible(True)

    @pyTTkSlot()
    def hide(self):
        '''hide'''
        self.setVisible(False)

    def isVisible(self) -> bool:
        return self._visible

class _TTkTextEditViewCustom(TTkTextEditView):
    __slots__ = ('enterPressed')
    def __init__(self, **kwargs):
        self.enterPressed = pyTTkSignal(bool)
        super().__init__(**kwargs)

    def keyEvent(self, evt):
        if ( evt.type == TTkK.SpecialKey and
             evt.mod==TTkK.NoModifier and
             evt.key == TTkK.Key_Enter ):
            self.enterPressed.emit(True)
            return True
        elif ( evt.type == TTkK.SpecialKey and
             evt.mod==TTkK.ControlModifier|TTkK.AltModifier and
             evt.key == TTkK.Key_M ):
            evt.mod = TTkK.NoModifier
            evt.key = TTkK.Key_Enter
        return super().keyEvent(evt)

class TTkTableWidget(TTkAbstractScrollView):
    '''TTkTableWidget'''

    classStyle = {
                'default':     {
                    'color':          TTkColor.RST,
                    'lineColor':      TTkColor.fg("#444444"),
                    'headerColor':    TTkColor.fg("#FFFFFF")+TTkColor.bg("#444444")+TTkColor.BOLD,
                    'hoverColor':     TTkColor.fg("#FFFF00")+TTkColor.bg("#0088AA")+TTkColor.BOLD,
                    'currentColor':   TTkColor.fg("#FFFF00")+TTkColor.bg("#0088FF")+TTkColor.BOLD,
                    'selectedColor':  TTkColor.bg("#0066AA"),
                    'separatorColor': TTkColor.fg("#555555")+TTkColor.bg("#444444")},
                'disabled':    {
                    'color':          TTkColor.fg("#888888"),
                    'lineColor':      TTkColor.fg("#888888"),
                    'headerColor':    TTkColor.fg("#888888"),
                    'hoverColor':     TTkColor.bg("#888888"),
                    'currentColor':   TTkColor.bg("#888888"),
                    'selectedColor':  TTkColor.fg("#888888"),
                    'separatorColor': TTkColor.fg("#888888")},
            }

    __slots__ = ( '_tableModel',
                  '_vHeaderSize', '_hHeaderSize',
                  '_showVSeparators', '_showHSeparators',
                  '_verticalHeader', '_horizontallHeader',
                  '_colsPos', '_rowsPos',
                  '_internal',
                  '_selected', '_hSeparatorSelected', '_vSeparatorSelected',
                  '_hoverPos', '_dragPos', '_currentPos',
                  '_sortColumn', '_sortOrder',
                  '_fastCheck', '_guessDataEdit',
                  # Signals
                  # 'itemChanged', 'itemClicked', 'itemDoubleClicked', 'itemExpanded', 'itemCollapsed', 'itemActivated'
                  )

    def __init__(self, *,
                 tableModel:TTkAbstractTableModel=None,
                 vSeparator:bool=True, hSeparator:bool=True,
                 **kwargs) -> None:
        # Signals
        # self.itemActivated     = pyTTkSignal(TTkTableWidgetItem, int)
        # self.itemChanged       = pyTTkSignal(TTkTableWidgetItem, int)
        # self.itemClicked       = pyTTkSignal(TTkTableWidgetItem, int)
        # self.itemDoubleClicked = pyTTkSignal(TTkTableWidgetItem, int)
        # self.itemExpanded      = pyTTkSignal(TTkTableWidgetItem)
        # self.itemCollapsed     = pyTTkSignal(TTkTableWidgetItem)
        self._fastCheck = True
        self._guessDataEdit = True

        self._showHSeparators = vSeparator
        self._showVSeparators = hSeparator
        self._verticalHeader    = _HeaderView()
        self._horizontallHeader = _HeaderView()
        self._selected = None
        self._hoverPos = None
        self._dragPos = None
        self._currentPos = None
        self._internal = {}
        self._hSeparatorSelected = None
        self._vSeparatorSelected = None
        self._sortColumn = -1
        self._sortOrder = TTkK.AscendingOrder
        self._tableModel = tableModel if tableModel else _DefaultTableModel()
        super().__init__(**kwargs)
        self._refreshLayout()
        self.setMinimumHeight(1)
        self.setFocusPolicy(TTkK.ClickFocus + TTkK.TabFocus)
        # self._rootItem = TTkTableWidgetItem(expanded=True)
        # self.clear()
        self.viewChanged.connect(self._viewChangedHandler)
        self._verticalHeader.visibilityUpdated.connect(   self._headerVisibilityChanged)
        self._horizontallHeader.visibilityUpdated.connect(self._headerVisibilityChanged)

    @pyTTkSlot()
    def _headerVisibilityChanged(self):
        showVH = self._verticalHeader.isVisible()
        showHH = self._horizontallHeader.isVisible()
        vhs = self._vHeaderSize if showVH else 0
        hhs = self._hHeaderSize if showHH else 0
        self.setPadding(hhs,0,vhs,0)
        self.viewChanged.emit()

    def _refreshLayout(self):
        rows = self._tableModel.rowCount()
        cols = self._tableModel.columnCount()
        self._vHeaderSize = vhs = 1+max(len(self._tableModel.headerData(_p, TTkK.VERTICAL)) for _p in range(rows) )
        self._hHeaderSize = hhs = 1
        self.setPadding(hhs,0,vhs,0)
        if self._showVSeparators:
            self._colsPos  = [(1+x)*11 for x in range(cols)]
        else:
            self._colsPos  = [(1+x)*10 for x in range(cols)]
        if self._showHSeparators:
            self._rowsPos     = [1+x*2  for x in range(rows)]
        else:
            self._rowsPos     = [1+x    for x in range(rows)]
        self._selected = [[False]*cols for _ in range(rows)]

    # Overridden function
    def viewFullAreaSize(self) -> tuple[int, int]:
        showVH = self._verticalHeader.isVisible()
        showHH = self._horizontallHeader.isVisible()
        hhs = self._hHeaderSize if showHH else 0
        vhs = self._vHeaderSize if showVH else 0
        w = vhs+self._colsPos[-1]+1
        h = hhs+self._rowsPos[-1]+1
        return w,h

    # Overridden function
    def viewDisplayedSize(self) -> tuple[int, int]:
        return self.size()

    def setSelection(self, pos:tuple[int,int], size:tuple[int,int], flags:TTkK.TTkItemSelectionModel):
        x,y = pos
        w,h = size
        for line in self._selected[y:y+h]:
            line[x:x+w]=[True]*w
        self.update()

    @pyTTkSlot()
    def _viewChangedHandler(self) -> None:
        x,y = self.getViewOffsets()
        self.layout().setOffset(-x,-y)
        self.update()

    def verticalHeader(self):
        return self._verticalHeader

    def horizontalHeader(self):
        return self._horizontallHeader

    def hSeparatorVisibility(self) -> bool:
        return self._showHSeparators
    def vSeparatorVisibility(self) -> bool:
        return self._showVSeparators

    def setHSeparatorVisibility(self, visibility:bool):
        if self._showHSeparators == visibility: return
        self._showHSeparators = visibility
        if visibility:
            self._rowsPos = [v+i for i,v in enumerate(self._rowsPos,1)]
        else:
            self._rowsPos = [v-i for i,v in enumerate(self._rowsPos,1)]
        self.viewChanged.emit()

    def setVSeparatorVisibility(self, visibility:bool):
        if self._showVSeparators == visibility: return
        self._showVSeparators = visibility
        if visibility:
            self._colsPos = [v+i for i,v in enumerate(self._colsPos,1)]
        else:
            self._colsPos = [v-i for i,v in enumerate(self._colsPos,1)]
        self.viewChanged.emit()

    def model(self) -> TTkAbstractTableModel:
        return self._tableModel

    def setModel(self, model:TTkAbstractTableModel) -> None:
        self._tableModel = model
        self._refreshLayout()
        self.viewChanged.emit()

    def setSortingEnabled(self, enable) -> None:
        pass

    def focusOutEvent(self) -> None:
        self._hSeparatorSelected = None
        self._vSeparatorSelected = None

    def leaveEvent(self, evt):
        self._hoverPos = None
        self.update()
        return super().leaveEvent(evt)

    @pyTTkSlot(int)
    def setColumnWidth(self, column:int, width: int) -> None:
        i = column
        prevPos = self._colsPos[i-1] if i>0 else -1
        if self._showVSeparators:
            newPos = prevPos + width + 1
        else:
            newPos = prevPos + width
        oldPos = self._colsPos[i]
        diff    = newPos-oldPos
        for ii in range(i,len(self._colsPos)):
            self._colsPos[ii] += diff
        self.viewChanged.emit()
        self.update()

    def _columnContentsSize(self, column:int) -> int:
        def _wid(_c):
            txt = self._tableModel.ttkStringData(_c, column)
            return max(t.termWidth() for t in txt.split('\n'))
        rows = self._tableModel.rowCount()
        if self._fastCheck:
            w,h = self.size()
            row,_ = self._findCell(w//2, h//2, False)
            rowa,rowb = max(0,row-100), min(row+100,rows)
        else:
            rowa,rowb = 0,rows
        return max(_wid(i) for i in range(rowa,rowb))

    @pyTTkSlot(int)
    def resizeColumnToContents(self, column:int) -> None:
        self.setColumnWidth(column, self._columnContentsSize(column))

    @pyTTkSlot()
    def resizeColumnsToContents(self) -> None:
        _d = 1 if self._showVSeparators else 0
        cols = self._tableModel.columnCount()
        pos = -1
        for _c in range(cols):
            pos += _d+self._columnContentsSize(_c)
            self._colsPos[_c] = pos
        self.viewChanged.emit()
        self.update()

    @pyTTkSlot(int,int)
    def setRowHeight(self, row:int, height: int) -> None:
        i = row
        prevPos = self._rowsPos[i-1] if i>0 else -1
        if self._showHSeparators:
            newPos = prevPos + height + 1
        else:
            newPos = prevPos + height
        oldPos = self._rowsPos[i]
        diff    = newPos-oldPos
        for ii in range(i,len(self._rowsPos)):
            self._rowsPos[ii] += diff
        self.viewChanged.emit()
        self.update()

    def _rowContentsSize(self, row:int) -> int:
        def _hei(_c):
            txt = self._tableModel.ttkStringData(row, _c)
            return len(txt.split('\n'))
        cols = self._tableModel.columnCount()
        if self._fastCheck:
            w,h = self.size()
            _,col = self._findCell(w//2, h//2, False)
            cola,colb = max(0,col-30), min(col+30,cols)
        else:
            cola,colb = 0,cols
        return max(_hei(i) for i in range(cola,colb))

    @pyTTkSlot(int)
    def resizeRowToContents(self, row:int) -> None:
        self.setRowHeight(row, self._rowContentsSize(row))

    @pyTTkSlot()
    def resizeRowsToContents(self) -> None:
        rows = self._tableModel.rowCount()
        _d = 1 if self._showHSeparators else 0
        pos = -1
        for _r in range(rows):
            pos += _d + self._rowContentsSize(_r)
            self._rowsPos[_r] = pos
        self.viewChanged.emit()
        self.update()

    def _findCell(self, x, y, headers):
        showVH = self._verticalHeader.isVisible()
        showHH = self._horizontallHeader.isVisible()
        hhs = self._hHeaderSize if showHH else 0
        vhs = self._vHeaderSize if showVH else 0
        ox, oy = self.getViewOffsets()
        rp = self._rowsPos
        cp = self._colsPos

        row = 0
        col = 0

        if headers and y<hhs:
            row = -1
        else:
            y += oy-hhs
            for row,py in enumerate(rp):
                if py>=y:
                    break

        if headers and x<vhs:
            col = -1
        else:
            x += ox-vhs
            for col,px in enumerate(cp):
                if px>=x:
                    break

        return row,col

    def _editStr(self, x,y,w,h, row, col, data):
        _tev = _TTkTextEditViewCustom()
        _te = TTkTextEdit(
                    parent=self, pos=(x, y), size=(w,h),
                    readOnly=False, wrapMode=TTkK.NoWrap)
        _tev = _te.textEditView()
        _te.setText(data)
        _te.setFocus()

        @pyTTkSlot(bool)
        def _processClose(change):
            if change:
                self.focusChanged.disconnect(_processClose)
                txt = _te.toPlainText()
                self._tableModel.setData(row,col,txt)
                self.update()
                _te.close()
                self.setFocus()

        # Override the key event
        _ke = _tev.keyEvent
        _doc = _tev.document()
        _cur = _tev.textCursor()
        def _keyEvent(evt):
            if ( evt.type == TTkK.SpecialKey):
                _line = _cur.anchor().line
                _pos  = _cur.anchor().pos
                _lineCount = _doc.lineCount()
                _lineLen
                if evt.mod==TTkK.NoModifier:
                    if evt.key == TTkK.Key_Enter:
                        # self.enterPressed.emit(True)
                        self._moveCurrentCell( 0,+1)
                        _processClose(True)
                        return True
                    elif evt.key == TTkK.Key_Up:
                        if _cur.anchor().line == 0:
                            self._moveCurrentCell( 0,-1)
                            _processClose(True)
                            return True
                    elif evt.key == TTkK.Key_Left:
                        if _cur.anchor().pos == 0:
                            self._moveCurrentCell(-1, 0)
                            _processClose(True)
                            return True
                elif ( evt.type == TTkK.SpecialKey and
                       evt.mod==TTkK.ControlModifier|TTkK.AltModifier and
                       evt.key == TTkK.Key_M ):
                    evt.mod = TTkK.NoModifier
                    evt.key = TTkK.Key_Enter
            return _ke(evt)
        _tev.keyEvent = _keyEvent

        # _tev.enterPressed.connect(_processClose)
        self.focusChanged.connect(_processClose)

    def _editNum(self, x,y,w,h, row, col, data):
        _sb = TTkSpinBox(
                    parent=self, pos=(x, y), size=(w,1),
                    minimum=-1000000, maximum=1000000,
                    value=data)
        _sb.setFocus()

        @pyTTkSlot(bool)
        def _processClose(change):
            if change:
                self.focusChanged.disconnect(_processClose)
                val = _sb.value()
                self._tableModel.setData(row,col,val)
                self.update()
                _sb.close()
                self.setFocus()

        self.focusChanged.connect(_processClose)

    def _editTTkString(self, x,y,w,h, row, col, data):
        _tp = TTkTextPicker(
                    parent=self, pos=(x, y), size=(w,h),
                    text=data, autoSize=False, wrapMode=TTkK.NoWrap)

        _tp.setFocus()

        @pyTTkSlot(bool)
        def _processClose(change):
            if change:
                self.focusChanged.disconnect(_processClose)
                txt = _tp.getTTkString()
                self._tableModel.setData(row,col,txt)
                self.update()
                _tp.close()
                self.setFocus()

        self.focusChanged.connect(_processClose)

    def _editCell(self, row, col):
        showHS = self._showHSeparators
        showVS = self._showVSeparators
        rp = self._rowsPos
        cp = self._colsPos
        xa,xb = 1+cp[col-1] if col>0 else 0, cp[col] + (0 if showVS else 1)
        ya,yb = 1+rp[row-1] if row>0 else 0, rp[row] + (0 if showHS else 1)

        data = self._tableModel.data(row, col)
        if type(data) is str:
            self._editStr(xa,ya,xb-xa,yb-ya,row,col,data)
        elif type(data) in [int,float]:
            self._editNum(xa,ya,xb-xa,yb-ya,row,col,data)
        else:
            data = self._tableModel.ttkStringData(row, col)
            self._editTTkString(xa,ya,xb-xa,yb-ya,row,col,data)

    def _moveCurrentCell(self, dx, dy):
        rows = self._tableModel.rowCount()
        cols = self._tableModel.columnCount()
        if self._currentPos:
            row,col = self._currentPos
            row = max(0,min(row+dy, rows-1))
            col = max(0,min(col+dx, cols-1))
        else:
            row,col = 0,0
        self._currentPos = (row,col)
        self.update()

    def keyEvent(self, evt):
        if self._currentPos:
            row,col = self._currentPos
        else:
            row,col = 0,0
        if evt.type == TTkK.SpecialKey:
            if evt.mod==TTkK.NoModifier:
                if   evt.key == TTkK.Key_Up:    self._moveCurrentCell( 0,-1)
                elif evt.key == TTkK.Key_Down:  self._moveCurrentCell( 0, 1)
                elif evt.key == TTkK.Key_Left:  self._moveCurrentCell(-1, 0)
                elif evt.key == TTkK.Key_Right: self._moveCurrentCell( 1, 0)
                elif evt.key == TTkK.Key_Enter: self._editCell(row,col)
                self.update()
            return True
        else:
            self._tableModel.setData(row,col,evt.key)
            self._editCell(row,col)
        return True


    def mouseDoubleClickEvent(self, evt):
        x,y = evt.x, evt.y
        ox, oy = self.getViewOffsets()
        showHS = self._showHSeparators
        showVS = self._showVSeparators
        showVH = self._verticalHeader.isVisible()
        showHH = self._horizontallHeader.isVisible()
        hhs = self._hHeaderSize if showHH else 0
        vhs = self._vHeaderSize if showVH else 0

        self._hSeparatorSelected = None
        self._vSeparatorSelected = None

        rp = self._rowsPos
        cp = self._colsPos

        # Handle Header Events
        # And return if handled
        # This is important to handle the header selection in the next part
        if showVS and y < hhs:
            _x = x+ox-vhs
            for i, c in enumerate(self._colsPos):
                if _x == c:
                    # I-th separator selected
                    self.resizeColumnToContents(i)
                    return True
            # return True
        elif showHS and x < vhs:
            _y = y+oy-hhs
            for i, r in enumerate(self._rowsPos):
                if _y == r:
                    # I-th separator selected
                    # I-th separator selected
                    self.resizeRowToContents(i)
                    return True

        row,col = self._findCell(x,y, headers=False)
        self._editCell(row,col)
        return True
        xa,xb = 1+cp[col-1] if col>0 else 0, cp[col] + (0 if showVS else 1)
        ya,yb = 1+rp[row-1] if row>0 else 0, rp[row] + (0 if showHS else 1)

        data = self._tableModel.data(row, col)
        if type(data) is str:
            self._editStr(xa,ya,xb-xa,yb-ya,row,col,data)
        elif type(data) in [int,float]:
            self._editNum(xa,ya,xb-xa,yb-ya,row,col,data)
        else:
            data = self._tableModel.ttkStringData(row, col)
            self._editTTkString(xa,ya,xb-xa,yb-ya,row,col,data)

        return True

    def mouseMoveEvent(self, evt) -> bool:
        x,y = evt.x,evt.y
        ox, oy = self.getViewOffsets()
        showHS = self._showHSeparators
        showVS = self._showVSeparators
        showVH = self._verticalHeader.isVisible()
        showHH = self._horizontallHeader.isVisible()
        hhs = self._hHeaderSize if showHH else 0
        vhs = self._vHeaderSize if showVH else 0

        self._hoverPos = (row,col) = self._findCell(x,y, headers=True)
        if showVS and row==-1:
            _x = x+ox-vhs
            for i, c in enumerate(self._colsPos):
                if _x == c:
                    # Over the I-th separator
                    self._hoverPos = None
                    self.update()
                    return True
        if showHS and col==-1:
            _y = y+oy-hhs
            for i, r in enumerate(self._rowsPos):
                if _y == r:
                    # Over the I-th separator
                    self._hoverPos = None
                    self.update()
                    return True
        self.update()
        return True

    def mousePressEvent(self, evt) -> bool:
        x,y = evt.x, evt.y
        ox, oy = self.getViewOffsets()
        showHS = self._showHSeparators
        showVS = self._showVSeparators
        showVH = self._verticalHeader.isVisible()
        showHH = self._horizontallHeader.isVisible()
        hhs = self._hHeaderSize if showHH else 0
        vhs = self._vHeaderSize if showVH else 0

        self._hSeparatorSelected = None
        self._vSeparatorSelected = None

        # Handle Header Events
        # And return if handled
        # This is important to handle the header selection in the next part
        if showVS and y < hhs:
            _x = x+ox-vhs
            for i, c in enumerate(self._colsPos):
                if _x == c:
                    # I-th separator selected
                    self._hSeparatorSelected = i
                    self.update()
                    return True
                elif _x < c:
                    # # I-th header selected
                    # order = not self._sortOrder if self._sortColumn == i else TTkK.AscendingOrder
                    # self.sortItems(i, order)
                    break
            # return True
        elif showHS and x < vhs:
            _y = y+oy-hhs
            for i, r in enumerate(self._rowsPos):
                if _y == r:
                    # I-th separator selected
                    self._vSeparatorSelected = i
                    self.update()
                    return True
                elif _y < r:
                    # # I-th header selected
                    # order = not self._sortOrder if self._sortColumn == i else TTkK.AscendingOrder
                    # self.sortItems(i, order)
                    break
            #   return True

        row,col = self._findCell(x,y, headers=True)
        if not row==col==-1:
            self._dragPos = [(row,col),(row,col)]
        rows = self._tableModel.rowCount()
        cols = self._tableModel.columnCount()
        _ctrl = evt.mod==TTkK.ControlModifier
        if row==col==-1:
            # Corner Press
            # Select Everything
            self._selected = [[True]*cols for _ in range(rows)]
        elif col==-1:
            # Row select
            state = all(self._selected[row])
            if not _ctrl:
                self._selected = [[False]*cols for _ in range(rows)]
            self._selected[row] = [not state]*cols
        elif row==-1:
            # Col select
            state = all(line[col] for line in self._selected)
            if not _ctrl:
                self._selected = [[False]*cols for _ in range(rows)]
            for line in self._selected:
                line[col] = not state
        else:
            # Cell Select
            self._currentPos = (row,col)
            if _ctrl: self._selected[row][col] = not self._selected[row][col]
            else:     self._selected[row][col] = True
        self._hoverPos = None
        self.update()
        return True

    def mouseDragEvent(self, evt) -> bool:
        '''
        ::

            columnPos       (Selected = 2)
                0       1        2          3   4
            ----|-------|--------|----------|---|
            Mouse (Drag) Pos
                                    ^
            I consider at least 4 char (3+1) as spacing
            Min Selected Pos = (Selected+1) * 4

        '''
        x,y = evt.x, evt.y
        ox, oy = self.getViewOffsets()
        showVH = self._verticalHeader.isVisible()
        showHH = self._horizontallHeader.isVisible()
        hhs = self._hHeaderSize if showHH else 0
        vhs = self._vHeaderSize if showVH else 0
        if self._dragPos and not self._hSeparatorSelected and not self._vSeparatorSelected:
            self._dragPos[1] = self._findCell(x,y, headers=False)
            self.update()
            return True
        if self._hSeparatorSelected is not None:
            x += ox-vhs
            ss = self._hSeparatorSelected
            pos = max((ss+1)*4, x)
            diff = pos - self._colsPos[ss]
            # Align the previous Separators if pushed
            for i in range(ss):
                self._colsPos[i] = min(self._colsPos[i], pos-(ss-i)*4)
            # Align all the other Separators relative to the selection
            for i in range(ss, len(self._colsPos)):
                self._colsPos[i] += diff
            # self._alignWidgets()
            self.viewChanged.emit()
            self.update()
            return True
        if self._vSeparatorSelected is not None:
            y += oy-hhs
            ss = self._vSeparatorSelected
            pos = max((ss+1)*2-1, y)
            diff = pos - self._rowsPos[ss]
            # Align the previous Separators if pushed
            for i in range(ss):
                self._rowsPos[i] = min(self._rowsPos[i], pos-(ss-i)*2)
            # Align all the other Separators relative to the selection
            for i in range(ss, len(self._rowsPos)):
                self._rowsPos[i] += diff
            # self._alignWidgets()
            self.viewChanged.emit()
            self.update()
            return True
        return False

    def mouseReleaseEvent(self, evt) -> bool:
        if self._dragPos:
            rows = self._tableModel.rowCount()
            cols = self._tableModel.columnCount()
            state = True
            (rowa,cola),(rowb,colb) = self._dragPos

            if evt.mod==TTkK.ControlModifier:
                # Pick the status to be applied to the selection if CTRL is Pressed
                # In case of line/row selection I choose the element 0 of that line
                state = self._selected[max(0,rowa)][max(0,cola)]
            else:
                # Clear the selection if no ctrl has been pressed
                self._selected = [[False]*cols for _ in range(rows)]

            if rowa == -1:
                cola,colb=min(cola,colb),max(cola,colb)
                rowa,rowb=0,rows
            elif cola == -1:
                rowa,rowb=min(rowa,rowb),max(rowa,rowb)
                cola,colb=0,cols
            else:
                cola,colb=min(cola,colb),max(cola,colb)
                rowa,rowb=min(rowa,rowb),max(rowa,rowb)

            for line in self._selected[rowa:rowb+1]:
                line[cola:colb+1] = [state]*(colb-cola+1)

        self._hoverPos = None
        self._dragPos = None
        self.update()
        return True

    #
    #   -1  X
    #        <-(0,0)->│<-(1,0)->│<-(2,0)->│<-(3,0)->│
    #    1   ─────────┼─────────┼─────────┼─────────┼
    #        <-(0,1)->│<-(1,1)->│<-(2,1)->│<-(3,1)->│
    #    3   ─────────┼─────────┼─────────┼─────────┼
    #        <-(0,2)->│<-(1,2)->│<-(2,2)->│<-(3,2)->│
    #    4   ─────────┼─────────┼─────────┼─────────┼
    #        <-(0,3)->│<-(1,3)->│<-(2,3)->│<-(3,3)->│ h-cell = 5 = 10-(4+1)
    #                 │ abc     │         │         │
    #                 │ de      │         │         │
    #                 │         │         │         │
    #                 │         │         │         │
    #   10   ─────────┼─────────┼─────────┼─────────┼
    #        <-(0,4)->│<-(1,4)->│<-(2,4)->│<-(3,4)->│
    #   12   ─────────┼─────────┼─────────┼─────────┼
    #        <-(0,5)->│<-(1,5)->│<-(2,5)->│<-(3,5)->│
    #   14   ─────────┼─────────┼─────────┼─────────┼

    #   -1   X
    #    0   <-(0,0)->│<-(1,0)->│<-(2,0)->│<-(3,0)->│
    #    1   <-(0,1)->│<-(1,1)->│<-(2,1)->│<-(3,1)->│
    #    2   <-(0,2)->│<-(1,2)->│<-(2,2)->│<-(3,2)->│
    #    3   <-(0,3)->│<-(1,3)->│<-(2,3)->│<-(3,3)->│ h-cell = 5 = 10-(4+1)
    #                 │ abc     │         │         │
    #                 │ de      │         │         │
    #                 │         │         │         │
    #                 │         │         │         │
    #    8   <-(0,4)->│<-(1,4)->│<-(2,4)->│<-(3,4)->│
    #    9   <-(0,5)->│<-(1,5)->│<-(2,5)->│<-(3,5)->│
    #
    def paintEvent(self, canvas) -> None:
        style = self.currentStyle()

        color:TTkColor= style['color']
        lineColor:TTkColor= style['lineColor']
        headerColor:TTkColor= style['headerColor']
        hoverColor:TTkColor= style['hoverColor']
        currentColor:TTkColor= style['currentColor']
        selectedColor:TTkColor= style['selectedColor']
        separatorColor:TTkColor= style['separatorColor']

        selectedColorInv:TTkColor = selectedColor.background().invertFgBg()

        vHSeparator = TTkString('▐', separatorColor)

        ox,oy = self.getViewOffsets()
        w,h = self.size()

        rows = self._tableModel.rowCount()
        cols = self._tableModel.columnCount()
        rp = self._rowsPos
        cp = self._colsPos

        showVH = self._verticalHeader.isVisible()
        showHH = self._horizontallHeader.isVisible()
        hhs = self._hHeaderSize if showHH else 0
        vhs = self._vHeaderSize if showVH else 0

        showHS = self._showHSeparators
        showVS = self._showVSeparators

        sliceCol=list(zip([-1]+cp,cp))
        sliceRow=list(zip([-1]+rp,rp))

        # NOTE: Add Color Cache
        # NOTE: Add Select/Hover Cache
        # Draw cell and right/bottom corner

        # Find First/Last displayed Rows
        rowa, rowb = 0,rows-1
        for row in range(rows):
            ya,yb = sliceRow[row]
            ya,yb = ya+hhs-oy, yb+hhs-oy
            if ya>h  :
                rowb = row
                break
            if yb<hhs:
                rowa = row
                continue
        # Use this in range
        rrows = (rowa,rowb+1)

        # Find First/Last displayed Cols
        cola, colb = 0, cols-1
        for col in range(cols):
            xa,xb = sliceCol[col]
            xa,xb = xa+vhs-ox, xb+vhs-ox
            if xa>w  :
                colb = col
                break
            if xb<vhs:
                cola = col
                continue
        # Use this in range
        rcols = (cola,colb+1)

        # Cache Cells
        _cellsCache   = []
        _colorCache2d = [[None]*(colb+1-cola) for _ in range(rowb+1-rowa)]
        for row in range(*rrows):
            ya,yb = sliceRow[row]
            if showHS:
                ya,yb = ya+hhs-oy+1, yb+hhs-oy
            else:
                ya,yb = ya+hhs-oy+1, yb+hhs-oy+1
            if ya>h  : break
            if yb<hhs: continue
            rowColor = color.mod(0,row)
            for col in range(*rcols):
                xa,xb = sliceCol[col]
                if showVS:
                    xa,xb = xa+vhs-ox+1, xb+vhs-ox
                else:
                    xa,xb = xa+vhs-ox+1, xb+vhs-ox+1
                if xa>w  : break
                if xb<vhs: continue
                cellColor = (
                    # currentColor if self._currentPos == (row,col) else
                    hoverColor if self._hoverPos in [(row,col),(-1,col),(row,-1),(-1,-1)] else
                    selectedColor if self._selected[row][col] else
                    rowColor )
                _colorCache2d[row-rowa][col-cola] = cellColor
                _cellsCache.append([row,col,xa,xb,ya,yb,cellColor])

        def _drawCellContent(_col,_row,_xa,_xb,_ya,_yb,_color):
                txt = self._tableModel.ttkStringData(_row, _col)
                if _color != TTkColor.RST:
                    txt = txt.completeColor(_color)
                for i,line in enumerate(txt.split('\n')):
                    y = i+_ya
                    canvas.drawTTkString(pos=(_xa,y), text=line, width=_xb-_xa, color=_color)
                    if y >= _yb-1: break
                canvas.fill(pos=(_xa,y+1),size=(_xb-_xa,_yb-y-1),color=_color)

        def _drawCellBottom(_col,_row,_xa,_xb,_ya,_yb,cellColor):
            if _yb>=h: return
            if _row<rows-1:
                _belowColor:TTkColor = _colorCache2d[_row+1-rowa][_col-cola]

                # force black border if there are selections
                _sa = self._selected[_row  ][_col  ]
                _sb = self._selected[_row+1][_col  ]
                if (showHS and showVS) and _sa and not _sb:
                    _bgA:TTkColor = c if (c:=cellColor.background())   else TTkColor.RST
                    _bgB:TTkColor = TTkColor.RST
                elif (showHS and showVS) and not _sa and _sb:
                    _bgA:TTkColor = TTkColor.RST
                    _bgB:TTkColor = c if (c:=_belowColor.background()) else TTkColor.RST
                else:
                    _bgA:TTkColor = c if (c:=cellColor.background())   else TTkColor.RST
                    _bgB:TTkColor = c if (c:=_belowColor.background()) else TTkColor.RST

                if _bgA == _bgB:
                    _char='─'
                    _color = lineColor if _bgA == TTkColor.RST else _bgA + lineColor
                elif _bgB == TTkColor.RST:
                    _char='▀'
                    _color=_bgA.invertFgBg()
                elif _bgA == TTkColor.RST:
                    _char='▄'
                    _color=_bgB.invertFgBg()
                else:
                    _char='▀'
                    _color=_bgB + _bgA.invertFgBg()
            else:
                _bgA:TTkColor = c if (c:=cellColor.background())   else TTkColor.RST
                if self._selected[_row  ][_col  ]:
                    _char='▀'
                    _color=selectedColorInv
                elif _bgA:=cellColor.background():
                    _char='▀'
                    _color=_bgA.invertFgBg()
                else:
                    _char='─'
                    _color=lineColor
            canvas.fill(pos=(_xa,_yb), size=(_xb-_xa,1), char=_char, color=_color)

        def _drawCellRight(_col,_row,_xa,_xb,_ya,_yb,cellColor):
            if _xb>=w: return
            if _col<cols-1:
                _rightColor:TTkColor = _colorCache2d[_row-rowa][_col+1-cola]

                # force black border if there are selections
                _sa = self._selected[_row  ][_col  ]
                _sc = self._selected[_row  ][_col+1]
                if (showHS and showVS) and _sa and not _sc:
                    _bgA:TTkColor = c if (c:=cellColor.background())   else TTkColor.RST
                    _bgC:TTkColor = TTkColor.RST
                elif (showHS and showVS) and not _sa and _sc:
                    _bgA:TTkColor = TTkColor.RST
                    _bgC:TTkColor = c if (c:=_rightColor.background()) else TTkColor.RST
                else:
                    _bgA:TTkColor = c if (c:=cellColor.background())   else TTkColor.RST
                    _bgC:TTkColor = c if (c:=_rightColor.background()) else TTkColor.RST

                if _bgA == _bgC:
                    _char='│'
                    _color = lineColor if _bgA == TTkColor.RST else _bgA + lineColor
                elif _bgC == TTkColor.RST:
                    _char='▌'
                    _color=_bgA.invertFgBg()
                elif _bgA == TTkColor.RST:
                    _char='▐'
                    _color=_bgC.invertFgBg()
                else:
                    _char='▌'
                    _color=_bgC + _bgA.invertFgBg()
            else:
                _bgA:TTkColor = c if (c:=cellColor.background())   else TTkColor.RST
                if self._selected[_row  ][_col  ]:
                    _char='▌'
                    _color=selectedColorInv
                elif _bgA:=cellColor.background():
                    _char=' '
                    _color=_bgA
                else:
                    _char='│'
                    _color=lineColor
            canvas.fill(pos=(_xb,_ya), size=(1,_yb-_ya), char=_char, color=_color)

        _charList = [
            # 0x00 0x01 0x02 0x03
              ' ', '▘', '▝', '▀',
            # 0x04 0x05 0x06 0x07
              '▖', '▌', '▞', '▛',
            # 0x08 0x09 0x0A 0x0B
              '▗', '▚', '▐', '▜',
            # 0x0C 0x0D 0x0E 0x0F
              '▄', '▙', '▟', '█']

        def _drawCellCorner(_col:int,_row:int,_xa:int,_xb:int,_ya:int,_yb:int,cellColor:TTkColor):
            if _yb>=h or _xb>=w: return
            _char = 'X'
            _color = cellColor
            if _row<rows-1 and _col<cols-1:
                # Check if there are selected cells:
                chId = (
                    0x01 * self._selected[_row  ][_col  ] +
                    0x02 * self._selected[_row  ][_col+1] +
                    0x04 * self._selected[_row+1][_col  ] +
                    0x08 * self._selected[_row+1][_col+1] )
                if chId==0x00 or chId==0x0F:
                    _belowColor:TTkColor = _colorCache2d[_row+1-rowa][_col-cola]
                    _bgA:TTkColor = c if (c:=cellColor.background())   else TTkColor.RST
                    _bgB:TTkColor = c if (c:=_belowColor.background()) else TTkColor.RST

                    if _bgA == _bgB:
                        _color = lineColor if _bgA == TTkColor.RST else _bgA + lineColor
                        _char='┼'
                    elif _bgB == TTkColor.RST:
                        _char='▀'
                        _color=_bgA.invertFgBg()
                    elif _bgA == TTkColor.RST:
                        _char='▄'
                        _color=_bgB.invertFgBg()
                    else:
                        _char='▀'
                        _color=_bgB + _bgA.invertFgBg()
                else:
                    _char = _charList[chId]
                    _color=selectedColorInv

            elif _col<cols-1:
                chId = (
                    0x01 * self._selected[row  ][col  ] +
                    0x02 * self._selected[row  ][col+1] )
                if chId:
                    _char = _charList[chId]
                    _color=selectedColorInv
                elif _c:=cellColor.background():
                    _char='▀'
                    _color = _c.invertFgBg()
                else:
                    _char = '┴'
                    _color = lineColor
            elif _row<rows-1:
                chId = (
                    (0x01) * self._selected[row  ][col  ] +
                    (0x04) * self._selected[row+1][col  ] )
                _belowColor:TTkColor = _colorCache2d[_row+1-rowa][_col-cola]
                _bgA:TTkColor = c if (c:=cellColor.background())   else TTkColor.RST
                _bgB:TTkColor = c if (c:=_belowColor.background()) else TTkColor.RST

                if chId:
                    _char = _charList[chId]
                    _color=selectedColorInv
                elif _bgA == _bgB == TTkColor.RST:
                    _char = '┤'
                    _color = lineColor
                elif _bgB == TTkColor.RST:
                    _char='▀'
                    _color=_bgA.invertFgBg()
                elif _bgA == TTkColor.RST:
                    _char='▄'
                    _color=_bgB.invertFgBg()
                else:
                    _char='▀'
                    _color=_bgB + _bgA.invertFgBg()
            else:
                chId = (
                    (0x01) * self._selected[row  ][col  ] )
                if chId:
                    _char = _charList[chId]
                    _color=selectedColorInv
                elif _c:=cellColor.background():
                    _char='▀'
                    _color = _c.invertFgBg()
                else:
                    _char = '┘'
                    _color = lineColor
            canvas.fill(pos=(_xb,_yb), size=(1,1), char=_char, color=_color)

        # # Draw Cells
        for row,col,xa,xb,ya,yb,cellColor in _cellsCache:
            _drawCellContent(col,row,xa,xb,ya,yb,cellColor)

            if showHS:
                _drawCellBottom(col,row,xa,xb,ya,yb,cellColor)
            if showVS:
                _drawCellRight( col,row,xa,xb,ya,yb,cellColor)
            if showHS and showVS:
                _drawCellCorner(col,row,xa,xb,ya,yb,cellColor)

        # return f"cc={len(_cellsCache)}  size={(w,h)} tw={(sliceCol[0],sliceCol[-1])} th={(sliceRow[0],sliceRow[-1])}"

        if self._hoverPos:
            row,col = self._hoverPos
            if row == -1:
                ya,yb = -1,rp[-1]
            else:
                ya,yb = sliceRow[row]
            if col == -1:
                xa,xb = -1,cp[-1]
            else:
                xa,xb = sliceCol[col]

            if showVS:
                xa,xb = xa+vhs-ox, xb+vhs-ox
            else:
                xa,xb = xa+vhs-ox, xb+vhs-ox+1

            if showHS:
                ya,yb = ya+hhs-oy, yb+hhs-oy
            else:
                ya,yb = ya+hhs-oy, yb+hhs-oy+1

            # _drawCell(col,row,xa,xb,ya,yb,hoverColor)

            # Draw Borders
            # Top, Bottom
            hoverColorInv = hoverColor.background().invertFgBg()
            canvas.drawTTkString(pos=(xa,ya), text=TTkString('▗'+('▄'*(xb-xa-1))+'▖',hoverColorInv))
            canvas.drawTTkString(pos=(xa,yb), text=TTkString('▝'+('▀'*(xb-xa-1))+'▘',hoverColorInv))
            # Left, Right
            canvas.fill(char='▐',pos=(xa,ya+1), size=(1,yb-ya-1), color=hoverColorInv)
            canvas.fill(char='▌',pos=(xb,ya+1), size=(1,yb-ya-1), color=hoverColorInv)

        if self._dragPos:
            (rowa,cola),(rowb,colb) = self._dragPos
            if rowa == -1:
                cola,colb = min(cola,colb),max(cola,colb)
                xa = sliceCol[cola][0]-ox+vhs
                xb = sliceCol[colb][1]-ox+vhs + (0 if showHS else 1)
                ya,yb = -1-oy+hhs,rp[-1]-oy+hhs
            elif cola == -1:
                rowa,rowb = min(rowa,rowb),max(rowa,rowb)
                ya = sliceRow[rowa][0]-oy+hhs
                yb = sliceRow[rowb][1]-oy+hhs + (0 if showVS else 1)
                xa,xb = -1-ox+vhs,cp[-1]-ox+vhs
            else:
                cola,colb = min(cola,colb),max(cola,colb)
                rowa,rowb = min(rowa,rowb),max(rowa,rowb)
                xa = sliceCol[cola][0]-ox+vhs
                xb = sliceCol[colb][1]-ox+vhs + (0 if showHS else 1)
                ya = sliceRow[rowa][0]-oy+hhs
                yb = sliceRow[rowb][1]-oy+hhs + (0 if showVS else 1)

            hoverColorInv = hoverColor.background().invertFgBg()
            canvas.drawTTkString(pos=(xa,ya), text=TTkString('▗'+('▄'*(xb-xa-1))+'▖',hoverColorInv))
            canvas.drawTTkString(pos=(xa,yb), text=TTkString('▝'+('▀'*(xb-xa-1))+'▘',hoverColorInv))
            canvas.fill(char='▐',pos=(xa,ya+1), size=(1,yb-ya-1), color=hoverColorInv)
            canvas.fill(char='▌',pos=(xb,ya+1), size=(1,yb-ya-1), color=hoverColorInv)

        if self._currentPos:
            row,col = self._currentPos
            xa = sliceCol[col][0]-ox+vhs
            xb = sliceCol[col][1]-ox+vhs + (0 if showHS else 1)
            ya = sliceRow[row][0]-oy+hhs
            yb = sliceRow[row][1]-oy+hhs + (0 if showVS else 1)
            currentColorInv = currentColor.background().invertFgBg()
            canvas.drawTTkString(pos=(xa,ya), text=TTkString('▗'+('▄'*(xb-xa-1))+'▖',currentColorInv))
            canvas.drawTTkString(pos=(xa,yb), text=TTkString('▝'+('▀'*(xb-xa-1))+'▘',currentColorInv))
            canvas.fill(char='▐',pos=(xa,ya+1), size=(1,yb-ya-1), color=currentColorInv)
            canvas.fill(char='▌',pos=(xb,ya+1), size=(1,yb-ya-1), color=currentColorInv)

        # Draw H-Header first:
        if showHH:
            for col in range(*rcols):
                txt = self._tableModel.headerData(col,TTkK.HORIZONTAL)
                if isinstance(txt,TTkString): pass
                elif type(txt) == str: txt = TTkString(txt)
                else:                  txt = TTkString(f"{txt}")
                xa,xb = sliceCol[col]
                if showVS:
                    xa,xb = xa+vhs-ox+1, xb+vhs-ox
                else:
                    xa,xb = xa+vhs-ox+1, xb+vhs-ox+1
                canvas.drawText(pos=(xa,0), text=txt, width=xb-xa, color=headerColor)
                if col == self._sortColumn:
                    s = '▼' if self._sortOrder == TTkK.AscendingOrder else '▲'
                    canvas.drawText(pos=(xb,0), text=s, color=headerColor)
                if showVS:
                    canvas.drawChar(pos=(xb,0), char='╿', color=headerColor)

        # Draw V-Header :
        if showVH:
            hlineHead = TTkString('╾'+'╌'*(vhs-2), color=headerColor) + vHSeparator
            for row in range(*rrows):
                ya,yb = sliceRow[row]
                if showHS:
                    ya,yb = ya+hhs-oy+1, yb+hhs-oy
                else:
                    ya,yb = ya+hhs-oy+1, yb+hhs-oy+1
                if ya>h  : break
                if yb<hhs: continue
                txt = self._tableModel.headerData(row,TTkK.VERTICAL)
                if isinstance(txt,TTkString): pass
                elif type(txt) == str: txt = TTkString(txt)
                else:                  txt = TTkString(f"{txt}")
                canvas.drawTTkString(pos=(0    ,ya), text=txt, width=vhs, color=headerColor)
                canvas.drawTTkString(pos=(vhs-1,ya), text=vHSeparator)
                for y in range(ya+1,yb):
                    canvas.drawTTkString(pos=(0,y), text=vHSeparator, width=vhs, alignment=TTkK.RIGHT_ALIGN, color=headerColor)
                if showHS:
                    canvas.drawTTkString(pos=(0,yb), text=hlineHead)

        # Draw Top/Left Corner
        canvas.drawText(pos=(0,0), text=' ', width=vhs, color=separatorColor.invertFgBg() )





