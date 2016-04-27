all:
	g++ main.cpp -o main
	${RM} main.o
	./main 0 0 0
