NITERS ?= 1
DATASET ?= MINI
CC = gcc
MPIC = mpicc
#CC = xlc

CFLAGS = -O3 -w
XLCFLAGS = -qsmp=omp

ifeq ($(DATASET), MINI)
DFLAGS += -DMINI_DATASET
else
ifeq ($(DATASET), SMALL)
DFLAGS += -DSMALL_DATASET
else
ifeq ($(DATASET), MEDIUM)
DFLAGS += -DMEDIUM_DATASET
else
ifeq ($(DATASET), LARGE)
DFLAGS += -DLARGE_DATASET
else
ifeq ($(DATASET), EXTRALARGE)
DFLAGS += -DEXTRALARGE_DATASET
else
ifeq ($(DATASET), SUPER)
DFLAGS += -DSUPER_DATASET
endif
endif
endif
endif
endif
endif

DFLAGS += -DNITERS=$(NITERS)

all: clean prog format

prog:
	$(MPIC) $(CFLAGS) $(DFLAGS) mpi_3mm.c -o prog

format:
	clang-format -i -style=LLVM *.c

clean:
	rm -f prog
