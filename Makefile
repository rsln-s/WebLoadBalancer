all:
	g++ main.cpp -o main
	${RM} main.o
	python test.py
