all:
	python3 src/main.py

resolve:
	python3 src/savedata/build.py

clean:
	rm -rf build dist main.spec

build: clean
	mv src/main.py src/tinyrpg.py
	pyinstaller --onefile -w src/tinyrpg.py
	mv src/tinyrpg.py src/main.py
