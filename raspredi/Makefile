CXX ?= g++
MPICXX = mpicxx
#CC = xlc

CXXFLAGS = -std=c++2a
XLCFLAGS = -qsmp=omp

BUILD ?= Debug

ifeq ($(BUILD), Release)
CXXFLAGS += -O3 -DNDEBUG -ffast-math -funroll-loops -ftree-vectorize -fno-asm -mavx2 -m64 -march=core-avx2 -g
endif

ifeq ($(BUILD), Debug)
CXXFLAGS += -O0 -Wall -Wextra
endif


all: clean prog format

prog:
	$(MPICXX) $(CXXFLAGS) main.cpp -o prog

format:
	clang-format -i -style=LLVM *.cpp

clean:
	rm -f prog
