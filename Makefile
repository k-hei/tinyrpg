all:
	python3 src/demo.py

imports:
	python3 src/colors/build.py
	python3 src/resolve/__init__.py

clean:
	rm -rf build dist tinyrpg.spec

build: clean
	mv src/demo.py src/tinyrpg.py
	pyinstaller --onefile -w src/tinyrpg.py
	mv src/tinyrpg.py src/demo.py

test:
	pytest
