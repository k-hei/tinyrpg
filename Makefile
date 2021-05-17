all:
	python3 src/main.py

demo-town:
	python3 src/demo-town.py

clean:
	rm -rf build dist main.spec

build: clean
	mv src/main.py src/tinyrpg.py
	pyinstaller --onefile -w src/tinyrpg.py
	mv src/tinyrpg.py src/main.py
