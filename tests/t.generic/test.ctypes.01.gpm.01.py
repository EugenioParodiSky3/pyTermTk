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

# Example from:
#   https://www.linuxjournal.com/article/4600
#   https://stackoverflow.com/questions/3794309/python-ctypes-python-file-object-c-file

import sys

from ctypes import CDLL, c_void_p, cdll, CFUNCTYPE
from ctypes import Structure, Union, pointer, POINTER, cast
from ctypes import c_short, c_int, c_char, c_ushort, c_ubyte, c_void_p

libgpm = CDLL('libgpm.so.2')

libc = cdll.LoadLibrary('libc.so.6')
cstdout = c_void_p.in_dll(libc, 'stdout')
cstdin = c_void_p.in_dll(libc, 'stdin')

gpm_handler = c_void_p.in_dll(libgpm, 'gpm_handler')

'''
    #define GPM_MAGIC 0x47706D4C /* "GpmL" */
    typedef struct Gpm_Connect {
      unsigned short eventMask, defaultMask;
      unsigned short minMod, maxMod;
      int pid;
      int vc;
    }              Gpm_Connect;
'''
class Gpm_Connect(Structure):
    _fields_ = [
        ("eventMask", c_ushort),
        ("defaultMask", c_ushort),
        ("minMod", c_ushort),
        ("maxMod", c_ushort),
        ("pid", c_int),
        ("vc", c_int)]

'''
    enum Gpm_Etype {
        GPM_MOVE=1,
        GPM_DRAG=2,   /* exactly one of the bare ones is active at a time */
        GPM_DOWN=4,
        GPM_UP=  8,

    #define GPM_BARE_EVENTS(type) ((type)&(0x0f|GPM_ENTER|GPM_LEAVE))

        GPM_SINGLE=16,            /* at most one in three is set */
        GPM_DOUBLE=32,
        GPM_TRIPLE=64,            /* WARNING: I depend on the values */

        GPM_MFLAG=128,            /* motion during click? */
        GPM_HARD=256,             /* if set in the defaultMask, force an already
                                     used event to pass over to another handler */

        GPM_ENTER=512,            /* enter event, user in Roi's */
        GPM_LEAVE=1024            /* leave event, used in Roi's */
    };

    enum Gpm_Margin {GPM_TOP=1, GPM_BOT=2, GPM_LFT=4, GPM_RGT=8};

    typedef struct Gpm_Event {
        unsigned char buttons, modifiers;  /* try to be a multiple of 4 */
        unsigned short vc;
        short dx, dy, x, y; /* displacement x,y for this event, and absolute x,y */
        enum Gpm_Etype type;
        /* clicks e.g. double click are determined by time-based processing */
        int clicks;
        enum Gpm_Margin margin;
        /* wdx/y: displacement of wheels in this event. Absolute values are not
        * required, because wheel movement is typically used for scrolling
        * or selecting fields, not for cursor positioning. The application
        * can determine when the end of file or form is reached, and not
        * go any further.
        * A single mouse will use wdy, "vertical scroll" wheel. */
        short wdx, wdy;
    }              Gpm_Event;
'''

class Gpm_Event(Structure):
    _fields_ = [
        ("buttons", c_ubyte),
        ("modifiers", c_ubyte),
        ("vc", c_short),
        ("dx", c_short),
        ("dy", c_short),
        ("x",  c_short),
        ("y",  c_short),
        ("type", c_int),
        ("clicks", c_int),
        ("margin", c_int),
        ("wdx", c_short),
        ("wdy", c_short)]

'''
    int my_handler(Gpm_Event *event, void *data)
    {
        printf("Event Type : %d at x=%d y=%d\n", event->type, event->x, event->y);
        return 0;
    }
'''

# CFUNCTYPE(c_int, POINTER(Gpm_Event), c_void_p)
HANDLER_FUNC = CFUNCTYPE(c_int, POINTER(Gpm_Event), POINTER(c_void_p))
# gpm_handler = POINTER(HANDLER_FUNC).in_dll(libgpm, 'gpm_handler')

def my_handler(event:Gpm_Event, data):
    # print(f"{event=} {data=} {dir(event)=} {event.contents=}")
    ec = event.contents
    buttons   = ec.buttons
    modifiers = ec.modifiers
    vc     = ec.vc
    dx     = ec.dx
    dy     = ec.dy
    x      = ec.x
    y      = ec.y
    type   = ec.type
    clicks = ec.clicks
    margin = ec.margin
    wdx    = ec.wdx
    wdy    = ec.wdy
    print(f"{buttons=}, {modifiers=}, {vc=}, {dx=}, {dy=}, {x=}, {y=}, {type=}, {clicks=}, {margin=}, {wdx=}, {wdy=}")
    return 0

'''
    int main()
    {       Gpm_Connect conn;
            int c;
            conn.eventMask  = ~0;   /* Want to know about all the events */
            conn.defaultMask = 0;   /* don't handle anything by default  */
            conn.minMod     = 0;    /* want everything                   */
            conn.maxMod     = ~0;   /* all modifiers included            */

            if(Gpm_Open(&conn, 0) == -1)
                    printf("Cannot connect to mouse server\n");

            gpm_handler = my_handler;
            while((c = Gpm_Getc(stdin)) != EOF)
                    printf("%c", c);
            Gpm_Close();
            return 0;
    }
'''


def main():
    conn = Gpm_Connect()
    c = 0
    conn.eventMask   = ~0 # Want to know about all the events
    conn.defaultMask =  0 # don't handle anything by default
    conn.minMod      =  0 # want everything
    conn.maxMod      = ~0 # all modifiers included

    print("Open Connection")
    print(f"{libgpm.gpm_handler=} {gpm_handler=} {gpm_handler.value=} {HANDLER_FUNC(my_handler)=}")
    # RDFM;
    # This is one of the rare cases where "Readuing the Fucking Manual" was the only way to solve this issue
    # Not just that but a basic knowledge of c casting annd function pointers
    #   https://docs.python.org/3/library/ctypes.html#type-conversions
    gpm_handler.value = cast(HANDLER_FUNC(my_handler),c_void_p).value
    print(f"{libgpm.gpm_handler=} {gpm_handler=}")

    if (gpm_fd := libgpm.Gpm_Open(pointer(conn), 0)) == -1:
       print("Cannot connect to mouse server\n")

    print("Starting Loop")

    while c := libgpm.Gpm_Getc(cstdin):
        print(f"Key: {c=:04X} ")

    # event = Gpm_Event()
    # while libgpm.Gpm_GetEvent(pointer(event)) > 0:
    #     print(event)
    # print(event)

    libgpm.Gpm_Close()


if __name__ == "__main__":
    main()