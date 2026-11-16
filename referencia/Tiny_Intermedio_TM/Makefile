# Compilador TINY y simulador TM de Kenneth C. Louden
# Version adaptada a GCC (Linux/Windows con MinGW o MSYS2)
CC = gcc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Wpedantic
FUENTES_TINY = main.c util.c scan.c parse.c symtab.c analyze.c code.c cgen.c intermedio.c

.PHONY: all clean prueba
all: tiny tm

tiny: $(FUENTES_TINY) *.h
	$(CC) $(CFLAGS) $(FUENTES_TINY) -o tiny

tm: tm.c
	$(CC) $(CFLAGS) tm.c -o tm

prueba: all
	./tiny ejemplos/factorial.tny
	@echo "El archivo ejemplos/factorial.tm se genero correctamente."

clean:
	rm -f tiny tm
