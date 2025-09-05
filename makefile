CC=gcc
CFLAG= -Wall -I.. -I. -O3

EXECUTABLE=Mv

all: $(EXECUTABLE)

Mv: Mv.c ../microtime.h 
	$(CC) $(CFLAG) -o Mv Mv.c ../microtime.o

clean:
	rm -f *.o *~ core

realclean:
	rm -f *.o *~ core $(EXECUTABLE)
 
