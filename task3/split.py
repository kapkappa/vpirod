#!/usr/bin/env

import os, sys

divide = 10

count = 0

f0 = open("f0", "w+")
f1 = open("f1", "w+")
f2 = open("f2", "w+")
f3 = open("f3", "w+")
f4 = open("f4", "w+")
f5 = open("f5", "w+")
f6 = open("f6", "w+")
f7 = open("f7", "w+")
f8 = open("f8", "w+")
f9 = open("f9", "w+")

with open("bible.txt", "r") as f:
    for line in f:
        if (count == 0):
            f0.write(line)
        if (count == 1):
            f1.write(line)
        if (count == 2):
            f2.write(line)
        if (count == 3):
            f3.write(line)
        if (count == 4):
            f4.write(line)
        if (count == 5):
            f5.write(line)
        if (count == 6):
            f6.write(line)
        if (count == 7):
            f7.write(line)
        if (count == 8):
            f8.write(line)
        if (count == 9):
            f9.write(line)
        count = count + 1
        count = count % divide

f.close()
f0.close()
f1.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()
f7.close()
f8.close()
f9.close()
