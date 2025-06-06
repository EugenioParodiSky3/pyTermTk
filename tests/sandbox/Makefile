.PHONY: testSandbox buildSandbox

testSandbox:
	python3 -m http.server --directory ./

www:
	mkdir -p \
	    www/pyodide \
		www/xterm/ www/xterm/addon-fit \
		www/codemirror www/codemirror/theme www/codemirror/modes \
		www/fontawesome www/webfonts www/fonts/nerdfonts \
		www/w2ui

	wget  -P www/pyodide/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/pyodide/pyodide.js
	wget  -P www/pyodide/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/pyodide/python_stdlib.zip
	wget  -P www/pyodide/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/pyodide/pyodide.asm.js
	# wget  -P www/pyodide/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/pyodide/repodata.json
	wget  -P www/pyodide/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/pyodide/pyodide.asm.wasm

	wget  -P www/xterm/    https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/xterm/xterm.css
	wget  -P www/xterm/    https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/xterm/xterm.js
	wget  -P www/xterm/    https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/xterm/xterm.js.map

	wget  -P www/xterm/addon-fit/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/xterm/addon-fit/addon-fit.js
	wget  -P www/xterm/addon-fit/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/xterm/addon-fit/addon-fit.js.map

	wget  -P www/xterm/addon-unicode11/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/xterm/addon-unicode11/addon-unicode11.js

	wget  -P www/fontawesome/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/fontawesome/regular.min.css
	wget  -P www/fontawesome/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/fontawesome/fontawesome.min.css

	# wget  -P www/webfonts/      https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/webfonts/fa-regular-400.woff2
	# wget  -P www/fonts/nerdfonts/     https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/nerdfonts/HurmitNerdFontMono-Regular.otf
	wget  -P www/fonts/nerdfonts/     https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/fonts/nerdfonts/DejaVuSansMNerdFont-Regular.ttf


	wget  -P www/w2ui/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/w2ui/w2ui-2.0.min.js
	wget  -P www/w2ui/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/w2ui/w2ui-2.0.min.css

	wget  -P www/codemirror/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/codemirror/codemirror.js
	wget  -P www/codemirror/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/codemirror/codemirror.css
	wget  -P www/codemirror/theme/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/codemirror/theme/mbo.css
	wget  -P www/codemirror/modes/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/codemirror/modes/python.js

	wget  -P www/   https://ceccopierangiolieugenio.github.io/pyTermTk-Docs/sandbox/www/favicon.ico

updateXterm: www
	rm -rf node_modules package.json package-lock.json
	mkdir -p www/xterm/ www/xterm/addon-unicode11 www/xterm/addon-fit www/xterm/addon-canvas
	npm install @xterm/xterm
	npm install @xterm/addon-fit
	npm install @xterm/addon-unicode11
	npm install @xterm/addon-canvas
	cp node_modules/@xterm/xterm/css/xterm.css \
	   node_modules/@xterm/xterm/lib/xterm.js \
	   node_modules/@xterm/xterm/lib/xterm.js.map \
	   www/xterm/
	cp node_modules/@xterm/addon-unicode11/lib/addon-unicode11.js \
	   node_modules/@xterm/addon-unicode11/lib/addon-unicode11.js.map \
	   www/xterm/addon-unicode11/
	cp node_modules/@xterm/addon-fit/lib/addon-fit.js \
	   node_modules/@xterm/addon-fit/lib/addon-fit.js.map \
	   www/xterm/addon-fit/
	cp node_modules/@xterm/addon-canvas/lib/addon-canvas.js \
	   node_modules/@xterm/addon-canvas/lib/addon-canvas.js.map \
	   www/xterm/addon-canvas/
	rm -rf node_modules package.json package-lock.json

buildSandbox: www
	rm -rf bin
	mkdir -p bin

	$( cd ../../ ; tools/prepareBuild.sh release ; )

	find ../../tmp/TermTk/  -name "*.py" | sed 's,.*tmp/,,' | sort | xargs tar cvzf bin/TermTk.tgz -C ../../tmp
	find ../../tutorial -name '*.py' -o -name '*.json' | sort | xargs tar cvzf bin/tutorial.tgz
	find ../../demo/paint.py ../../demo/ttkode.py ../../demo/demo.py ../../demo/showcase/*.* | sort | xargs tar cvzf bin/demo.tgz
	find ../../tests/ansi.images.json ../../tests/t.ui/*.* | sort | xargs tar cvzf bin/tests.tgz

buildTestSandbox: www
	rm -rf bin
	mkdir -p bin

	$( cd ../../ ; tools/prepareBuild.sh release ; )

	find ../../TermTk/  -name "*.py" | sort | xargs tar cvzf bin/TermTk.tgz
	find ../../tutorial -name "*.py" | sort | xargs tar cvzf bin/tutorial.tgz
	find ../../demo/paint.py ../../demo/ttkode.py ../../demo/demo.py ../../demo/showcase/*.* | sort | xargs tar cvzf bin/demo.tgz
	find ../../tests/ansi.images.json ../../tests/t.ui/*.* | sort | xargs tar cvzf bin/tests.tgz
