#!/usr/bin/env bash

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


_PWD=`pwd`
_TOOLS_BASE_PATH=$(dirname $(readlink -f $0))
_BASE_PATH=$( readlink -f ${_TOOLS_BASE_PATH}/.. )
_TMP_PATH=$(  readlink -f  ${_BASE_PATH}/tmp     )

_MAJOR=$( git describe --tags | sed 's,\([0-9]*\)\..*,\1,'                     )
_MINOR=$( git describe --tags | sed 's,[0-9]*\.\([0-9]*\)\..*,\1,'             )
_PATCH=$( git describe --tags | sed 's,[0-9]*\.[0-9]*\.\([0-9]*\)[^0-9].*,\1,' )
_STAGE=$( git describe --tags | sed 's,[^-]*-a-\?\([0-9]*\).*,\1,'             )

_VERSION="${_MAJOR}.${_MINOR}.${_PATCH}-a${_STAGE}"
_DOCVERSION="${_MAJOR}.${_MINOR}.${_PATCH}-a"

echo Version: ${_VERSION}
echo Name: ${_NAME}

mkdir -p ${_TMP_PATH}
rm -rf ${_TMP_PATH}/* itchExport.zip

${_TOOLS_BASE_PATH}/prepareBuild.sh release

mkdir -p ${_TMP_PATH}/bin \
         ${_TMP_PATH}/www/pyodide \
         ${_TMP_PATH}/www/xterm/ \
         ${_TMP_PATH}/www/xterm-addon-fit \
         ${_TMP_PATH}/www/xterm-addon-canvas \
         ${_TMP_PATH}/www/xterm-addon-unicode11 \
         ${_TMP_PATH}/www/file-saver\
         ${_TMP_PATH}/www/webfonts \
         ${_TMP_PATH}/www/fonts/nerdfonts \
         ${_TMP_PATH}/www/fonts/opentype \
         ${_TMP_PATH}/www/fonts/unifont

function _download {
    _P=$1
    _F=$2
    if [ -f tests/sandbox/${_F} ] ;
    then cp tests/sandbox/${_F} ${_P} ;
    else wget -P ${_P} https://ceccopierangiolieugenio.github.io/binaryRepo/pyTermTk/${_F};
    fi ;
};

_download  ${_TMP_PATH}/www/pyodide/  www/pyodide/pyodide.js
# _download ${_TMP_PATH}/www/pyodide/   www/pyodide/pyodide.js.map
# _download ${_TMP_PATH}/www/pyodide/   www/pyodide/pyodide.js
_download ${_TMP_PATH}/www/pyodide/   www/pyodide/pyodide-lock.json
_download ${_TMP_PATH}/www/pyodide/   www/pyodide/python_stdlib.zip
_download ${_TMP_PATH}/www/pyodide/   www/pyodide/pyodide.asm.js
# _download ${_TMP_PATH}/www/pyodide/   www/pyodide/repodata.json
_download ${_TMP_PATH}/www/pyodide/   www/pyodide/pyodide.asm.wasm

_download ${_TMP_PATH}/www/xterm/    www/xterm/xterm.css
_download ${_TMP_PATH}/www/xterm/    www/xterm/xterm.js
_download ${_TMP_PATH}/www/xterm/    www/xterm/xterm.js.map

_download ${_TMP_PATH}/www/xterm-addon-fit/   www/xterm-addon-fit/xterm-addon-fit.js
_download ${_TMP_PATH}/www/xterm-addon-fit/   www/xterm-addon-fit/xterm-addon-fit.js.map

_download ${_TMP_PATH}/www/xterm-addon-canvas/   www/xterm-addon-canvas/xterm-addon-canvas.js
_download ${_TMP_PATH}/www/xterm-addon-canvas/   www/xterm-addon-canvas/xterm-addon-canvas.js.map

_download ${_TMP_PATH}/www/xterm-addon-unicode11/   www/xterm-addon-unicode11/xterm-addon-unicode11.js
_download ${_TMP_PATH}/www/xterm-addon-unicode11/   www/xterm-addon-unicode11/xterm-addon-unicode11.js.map

_download ${_TMP_PATH}/www/file-saver/   www/file-saver/FileSaver.js

# _download ${_TMP_PATH}/www/fonts/webfonts/   www/fonts/webfonts/fa-regular-400.woff2
# _download ${_TMP_PATH}/www/fonts/nerdfonts/  www/fonts/nerdfonts/HurmitNerdFontMono-Regular.otf
# _download ${_TMP_PATH}/www/fonts/nerdfonts/  www/fonts/nerdfonts/DejaVuSansMNerdFont-Regular.ttf
# _download ${_TMP_PATH}/www/fonts/opentype/   www/fonts/opentype/3270SemiCondensed-Regular.otf
_download ${_TMP_PATH}/www/fonts/opentype/   www/fonts/opentype/3270-Regular.otf
# _download ${_TMP_PATH}/www/fonts/unifont/   www/fonts/unifont/unifont_upper.ttf

_download ${_TMP_PATH}/www/   www/favicon.ico


tar cvzf ${_TMP_PATH}/bin/TermTk.tgz --exclude='__pycache__' --transform "s,^.*TermTk/,TermTk/," ${_TMP_PATH}/TermTk
tar cvzf ${_TMP_PATH}/bin/DPT.tgz    --exclude='__pycache__' --transform "s,^.*/dumb,dumb,"      ${_TOOLS_BASE_PATH}/dumb.paint.tool.py ${_TOOLS_BASE_PATH}/dumb_paint_lib

# find ${_TMP_PATH}/TermTk \
#     | grep -v __pycache__ | xargs tar cvzf ${_TMP_PATH}/bin/TermTk.tgz -C ${_TMP_PATH}
#
# find ${_TOOLS_BASE_PATH}/dumb.paint.tool.py ${_TOOLS_BASE_PATH}/dumb_paint_lib \
#     | grep -v __pycache__ | xargs tar cvzf ${_TMP_PATH}/bin/DPT.tgz -C ${_TOOLS_BASE_PATH}

cp -a ${_TOOLS_BASE_PATH}/webExporter/* ${_TMP_PATH}/

echo '{
    "libs" : [
            {"pkg" :"bin/TermTk.tgz",
             "name": "TermTk"},
             {"pkg" :"bin/DPT.tgz",
             "name": "Dumb Paint Tool"}
        ],
    "mainOld": "main.py",
    "main": "dumb.paint.tool.py"
}' > ${_TMP_PATH}/package.json

rm -rf ${_TMP_PATH}/TermTk
pushd ${_TMP_PATH}
zip -r ${_PWD}/itchExport.zip *
popd
