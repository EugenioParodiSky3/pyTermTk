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

# inspired by:
# https://grafana.com/docs/grafana/latest/panels/visualizations/graph-panel/
# And of course:
# https://github.com/aristocratos/bpytop

from TermTk.TTkCore.cfg import *
from TermTk.TTkCore.constant import TTkK
from TermTk.TTkCore.log import TTkLog
from TermTk.TTkWidgets.widget import TTkWidget
from TermTk.TTkTemplates.color import TColor

class TTkGraph(TTkWidget, TColor):
    __slots__ = ('_data', '_maxData', '_offset', '_direction')
    def __init__(self, *args, **kwargs):
        self._data = []
        self._offset = 0
        TTkWidget.__init__(self, *args, **kwargs)
        TColor.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'TTkGraph' )
        self._maxData = kwargs.get('maxData', 0x1000)
        self._direction = kwargs.get('direction', TTkK.RIGHT)

    def addValue(self, value):
        self._data.append(value)
        self.update()

    def paintEvent(self):
        if not self._data: return
        x=0
        y = self.height()//2
        w,h = self.size()
        v1,v2 = 0,0
        i=0
        data = self._data[-w*2:]
        zoom = 2*h/max(max(data),-min(data))
        for i in range(len(data)):
            v2 = v1
            v1 = data[i]
            if i%2==0:
                if self._direction == TTkK.RIGHT:
                    self._canvas.drawHChart(pos=(x+i//2,y),values=(v2,v1), zoom=zoom, color=self.color.modParam(val=-y))
                else:
                    self._canvas.drawHChart(pos=(w-(x+i//2),y),values=(v1,v2), zoom=zoom, color=self.color.modParam(val=-y))
        if i%2==1:
            if self._direction == TTkK.RIGHT:
                self._canvas.drawHChart(pos=(x+i//2+1,y),values=(v1,0), zoom=zoom, color=self.color.modParam(val=-y))
            else:
                self._canvas.drawHChart(pos=(w-(x+i//2+1),y),values=(0,v1), zoom=zoom, color=self.color.modParam(val=-y))
