


#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 Eugenio Parodi <ceccopierangiolieugenio AT googlemail DOT com>
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

from TermTk.TTkCore.constant import TTkConstant, TTkK
from TermTk.TTkCore.log import TTkLog
from TermTk.TTkCore.cfg import *
from TermTk.TTkCore.signal import pyTTkSlot, pyTTkSignal
from TermTk.TTkWidgets.widget import TTkWidget
from TermTk.TTkWidgets.spacer import TTkSpacer
from TermTk.TTkWidgets.frame import TTkFrame
from TermTk.TTkWidgets.button import TTkButton
from TermTk.TTkWidgets.menubar import TTkMenuButton
from TermTk.TTkLayouts.boxlayout import TTkHBoxLayout
from TermTk.TTkLayouts.gridlayout import TTkGridLayout


class TTkTabButton(TTkButton):
    __slots__ = ('_sideEnd', '_tabStatus')
    def __init__(self, *args, **kwargs):
        self._sideEnd = TTkK.NONE
        self._tabStatus = TTkK.Unchecked
        TTkButton.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'TTkTabButton' )
        if self._border:
            self.resize(len(self._text)+2, 3)
            self.setMinimumSize(2+len(self._text), 3)
            self.setMaximumSize(2+len(self._text), 3)
        else:
            self.resize(len(self._text)+2, 2)
            self.setMinimumSize(len(self._text)+2, 2)
            self.setMaximumSize(len(self._text)+2, 2)
        self.setFocusPolicy(TTkK.ParentFocus)

    def sideEnd(self):
        return self._sideEnd

    def setSideEnd(self, sideEnd):
        self._sideEnd = sideEnd
        self.update()

    def tabStatus(self):
        return self._tabStatus

    def setTabStatus(self, status):
        self._tabStatus = status
        self.update()

    def paintEvent(self):
        self._canvas.drawTabButton(
            pos=(0,0), size=self.size(),
            small=(not self._border),
            sideEnd=self._sideEnd, status=self._tabStatus,
            label=self.text, color=self._borderColor )
        self._canvas.drawText(pos=(1,1 if self._border else 0), text=self.text, color=self.color())

class _TTkTabScrollerButton(TTkButton):
    __slots__ = ('_side')
    def __init__(self, *args, **kwargs):
        self._side = kwargs.get('side',TTkK.LEFT)
        TTkButton.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , '_TTkTabScrollerButton' )
        if self._border:
            self.resize(2, 3)
            self.setMinimumSize(2, 3)
            self.setMaximumSize(2, 3)
        else:
            self.resize(2, 2)
            self.setMinimumSize(2, 2)
            self.setMaximumSize(2, 2)
        self.setFocusPolicy(TTkK.ParentFocus)

    def paintEvent(self):
        tt = TTkCfg.theme.tab
        if self._border:
            if self._side == TTkK.LEFT:
                self._canvas.drawText(pos=(0,0), color=self._borderColor, text=tt[7] +tt[1])
                self._canvas.drawText(pos=(0,1), color=self._borderColor, text=tt[9] +tt[31])
                self._canvas.drawText(pos=(0,2), color=self._borderColor, text=tt[11]+tt[12])
            else:
                self._canvas.drawText(pos=(0,0), color=self._borderColor, text=tt[1] +tt[8])
                self._canvas.drawText(pos=(0,1), color=self._borderColor, text=tt[32]+tt[9])
                self._canvas.drawText(pos=(0,2), color=self._borderColor, text=tt[12]+tt[15])
        else:
            if self._side == TTkK.LEFT:
                self._canvas.drawText(pos=(0,0), color=self._borderColor, text=tt[9] +tt[31])
                self._canvas.drawText(pos=(0,1), color=self._borderColor, text=tt[23]+tt[1])
            else:
                self._canvas.drawText(pos=(0,0), color=self._borderColor, text=tt[32]+tt[9])
                self._canvas.drawText(pos=(0,1), color=self._borderColor, text=tt[1] +tt[24])

'''
_curentIndex =              2
_labelPos =      [0],[1],  [2],   [3],   [4],
                ╭─┌──┌──────╔══════╗──────┬──────┐─╮
_labels=        │◀│La│Label1║Label2║Label3│Label4│▶│
                ╞═══════════╩══════╩═══════════════╡
                 leftscroller                     rightScroller
'''

class TTkTabBar(TTkWidget):
    __slots__ = (
        '_tabButtons', '_small',
        '_highlighted', '_currentIndex','_lastIndex',
        '_leftScroller', '_rightScroller',
        '_borderColor',
        #Signals
        'currentChanged', 'tabBarClicked')

    def __init__(self, *args, **kwargs):
        self._tabButtons = []
        self._currentIndex = -1
        self._lastIndex = -1
        self._highlighted = -1
        self._tabMovable = False
        self._tabClosable = False
        self._borderColor = TTkCfg.theme.tabBorderColor
        self._small = kwargs.get('small',True)
        self._leftScroller =  _TTkTabScrollerButton(border=not self._small,side=TTkK.LEFT)
        self._rightScroller = _TTkTabScrollerButton(border=not self._small,side=TTkK.RIGHT)
        self._sideBorder = TTkK.LEFT | TTkK.RIGHT

        TTkWidget.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , '_TTkTabs')
        self.setFocusPolicy(TTkK.ClickFocus + TTkK.TabFocus)
        self.focusChanged.connect(self._focusChanged)


        # Add and connect the scrollers
        self.addWidget(self._leftScroller)
        self.addWidget(self._rightScroller)

        # Signals
        self.currentChanged = pyTTkSignal(int)
        self.tabBarClicked  = pyTTkSignal(int)

        self.setFocusPolicy(TTkK.ClickFocus + TTkK.TabFocus)

    def addTab(self, label):
        self.insertTab(len(self._tabButtons), label)

    def insertTab(self, index, label):
        button = TTkTabButton(parent=self, text=label, border=not self._small)
        self._tabButtons.insert(index,button)
        button.clicked.connect(lambda :self.setCurrentIndex(self._tabButtons.index(button)))
        self._updateTabs()

    def borderColor(self):
        return self._borderColor

    def setBorderColor(self, color):
        self._borderColor = color
        self.update()

    def setSideBorder(self, border):
        self._sideBorder |= border

    def unsetSideBorder(self, border):
        self._sideBorder &= ~border

    def currentIndex(self):
        return self._currentIndex

    @pyTTkSlot(int)
    def setCurrentIndex(self, index):
        TTkLog.debug(index)
        if 0 <= index < len(self._tabButtons):
            self._currentIndex = index
            self._offset = index
            self._updateTabs()

    def resizeEvent(self, w, h):
        self._updateTabs()

    def _updateTabs(self):
        w = self.width()
        # Find the tabs used size max size
        maxLen = 0
        sizes = [t.width()-1 for t in self._tabButtons]
        for s in sizes: maxLen += s
        if maxLen <= w:
            self._leftScroller.hide()
            self._rightScroller.hide()
            shrink = 1
            offx = 0
        else:
            self._leftScroller.show()
            self._rightScroller.show()
            self._rightScroller.move(w-2,0)
            w-=4
            shrink = w/maxLen
            offx = 2

        posx=0
        for t in self._tabButtons:
            tmpx = offx+min(int(posx*shrink),w-t.width())
            sideEnd = TTkK.NONE
            if tmpx==0:
                sideEnd |= TTkK.LEFT
            if tmpx+t.width()==self.width():
                sideEnd |= TTkK.RIGHT
            t.move(tmpx,0)
            t.setSideEnd(sideEnd)
            t.setTabStatus(TTkK.Unchecked)
            posx += t.width()-1

        # ZReorder the widgets:
        for i in range(0,max(0,self._currentIndex)):
            self._tabButtons[i].raiseWidget()
        for i in reversed(range(max(0,self._currentIndex),len(self._tabButtons))):
            self._tabButtons[i].raiseWidget()
        if 0 <= self._highlighted < len(self._tabButtons):
            self._tabButtons[self._highlighted].raiseWidget()

        if self._currentIndex == -1:
            self._currentIndex = len(self._tabButtons)-1

        if self._tabButtons:
            self._tabButtons[self._currentIndex].setTabStatus(TTkK.Checked)

        if self._lastIndex != self._currentIndex:
            self._lastIndex = self._currentIndex
            self.currentChanged.emit(self._currentIndex)

        # set the buttons text color based on the selection/offset
        for i,b in enumerate(self._tabButtons):
            if i == self._currentIndex:
                b.setColor(TTkCfg.theme.tabSelectColor)
            else:
                b.setColor(TTkCfg.theme.tabColor)

        self.update()

    @pyTTkSlot(bool)
    def _focusChanged(self, focus):
        if focus:
            borderColor = TTkCfg.theme.tabBorderColorFocus
        else:
            borderColor = TTkCfg.theme.tabBorderColor
        self.setBorderColor(borderColor)
        for b in self._tabButtons:
            b.setBorderColor(borderColor)
        self._leftScroller.setBorderColor(borderColor)
        self._rightScroller.setBorderColor(borderColor)

    def paintEvent(self):
        w = self.width()
        tt = TTkCfg.theme.tab
        if self._small:
            self._canvas.drawText(pos=(0,1),text=tt[23] + tt[19]*(w-2) + tt[24], color=self._borderColor)
        else:
            self._canvas.drawText(pos=(0,2),text=tt[11] + tt[12]*(w-2) + tt[15], color=self._borderColor)


'''
           ┌────────────────────────────┐
           │ Root Layout                │
           │┌────────┬────────┬────────┐│
           ││ Left M │ TABS   │ RightM ││
           │└────────┴────────┴────────┘│
           │┌──────────────────────────┐│
           ││ Layout                   ││
           ││                          ││
           │└──────────────────────────┘│
           └────────────────────────────┘
'''

class TTkTabWidget(TTkFrame):
    __slots__ = (
        '_tabBarTopLayout', '_tabBar', '_topLeftLayout', '_topRightLayout',
        '_tabWidgets',
        # Forward Signals
        'currentChanged', 'tabBarClicked',
        # forward methods
        'currentIndex', 'setCurrentIndex')

    def __init__(self, *args, **kwargs):
        self._tabWidgets = []
        self._tabBarTopLayout = TTkGridLayout()
        self._borderColor = TTkCfg.theme.tabBorderColor

        TTkFrame.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'TTkTabWidget')

        self._tabBar = TTkTabBar(small = not self.border())
        self._topLeftLayout   = None
        self._topRightLayout  = None
        self._tabBarTopLayout.addWidget(self._tabBar,0,1)

        self._tabBar.currentChanged.connect(self._tabChanged)
        self._tabBar.focusChanged.connect(self._focusChanged)

        self.setLayout(TTkGridLayout())
        if self.border():
            self.setPadding(3,1,1,1)
        else:
            self.setPadding(2,0,0,0)

        self.rootLayout().addItem(self._tabBarTopLayout)
        self._tabBarTopLayout.setGeometry(0,0,self._width,self._padt)
        # forwarded methods
        self.currentIndex    = self._tabBar.currentIndex
        self.setCurrentIndex = self._tabBar.setCurrentIndex
        # forwarded Signals
        self.currentChanged = self._tabBar.currentChanged
        self.tabBarClicked  = self._tabBar.tabBarClicked

    @pyTTkSlot(TTkWidget)
    def setCurrentWidget(self, widget):
        for i, w in enumerate(self._tabWidgets):
            if widget == w:
                self.setCurrentIndex(i)
                break

    @pyTTkSlot(int)
    def _tabChanged(self, index):
        for i, widget in enumerate(self._tabWidgets):
            if index == i:
                widget.show()
            else:
                widget.hide()

    @pyTTkSlot(bool)
    def _focusChanged(self, focus):
        if focus:
            self.setBorderColor(TTkCfg.theme.tabBorderColorFocus)
        else:
            self.setBorderColor(TTkCfg.theme.tabBorderColor)

    def addMenu(self, text, position=TTkK.LEFT):
        return TTkMenuButton()

    def addTab(self, widget, label):
        widget.hide()
        self._tabWidgets.append(widget)
        self.layout().addWidget(widget)
        self._tabBar.addTab(label)

    def insertTab(self, index, widget, label):
        widget.hide()
        self._tabWidgets.insert(index, widget)
        self.layout().addWidget(widget)
        self._tabBar.insertTab(index, label)

    def resizeEvent(self, w, h):
        self._tabBarTopLayout.setGeometry(0,0,w,self._padt)

    #def paintEvent(self): pass
