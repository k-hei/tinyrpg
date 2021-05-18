all:
	python3 src/main.py

demo-dungeon:
	python3 src/demo-dungeon.py

demo-town:
	python3 src/demo-town.py

demo-gen:
	python3 src/demo-gen.py

demo-nameentry:
	python3 src/demo-nameentry.py

demo-prompt:
	python3 src/demo-prompt.py

clean:
	rm -rf build dist main.spec

build: clean
	mv src/main.py src/tinyrpg.py
	pyinstaller --onefile -w src/tinyrpg.py
	mv src/tinyrpg.py src/main.py
