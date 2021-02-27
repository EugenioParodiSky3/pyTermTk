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

from TermTk.TTkCore.cfg import *
from TermTk.TTkCore.log import TTkLog
from TermTk.TTkWidgets.widget import TTkWidget

class TTkFrame(TTkWidget):
    __slots__ = ('_border','_title', '_titleColor', '_borderColor')
    def __init__(self, *args, **kwargs):
        TTkWidget.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'TTkFrame' )
        self._borderColor = kwargs.get('borderColor', TTkCfg.theme.frameBorderColor )
        self._titleColor = kwargs.get('titleColor', TTkCfg.theme.frameTitleColor )
        self._title = kwargs.get('title' , '' )
        self._border = kwargs.get('border', True )
        self.setBorder(self._border)

    def setBorder(self, border):
        self._border = border
        if border: self.setPadding(1,1,1,1)
        else:      self.setPadding(0,0,0,0)

    def paintEvent(self):
        if self._border:
            self._canvas.drawBox(pos=(0,0),size=(self._width,self._height), color=self._borderColor)
            if self._title != '':
                self._canvas.drawBoxTitle(
                                pos=(0,0),
                                size=(self._width,self._height),
                                text=self._title,
                                color=self._borderColor,
                                colorText=self._titleColor)

