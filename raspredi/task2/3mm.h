#ifndef _3MM_H
#define _3MM_H
# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(MEDIUM_DATASET) && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET) && !defined(SUPER_DATASET)
#define MINI_DATASET
# endif
# if !defined(NI) && !defined(NJ) && !defined(NK) && !defined(NL) && !defined(NM)
# ifdef MINI_DATASET
#define NI 16
#define NJ 18
#define NK 20
#define NL 22
#define NM 24
# endif
# ifdef SMALL_DATASET
#define NI 40
#define NJ 50
#define NK 60
#define NL 70
#define NM 80
# endif
# ifdef MEDIUM_DATASET
#define NI 180
#define NJ 190
#define NK 200
#define NL 210
#define NM 220
# endif
# ifdef LARGE_DATASET
#define NI 800
#define NJ 900
#define NK 1000
#define NL 1100
#define NM 1200
# endif
# ifdef EXTRALARGE_DATASET
#define NI 1600
#define NJ 1800
#define NK 2000
#define NL 2200
#define NM 2400
# endif
# ifdef SUPER_DATASET
#define NI 3200
#define NJ 3600
#define NK 4000
#define NL 4400
#define NM 4800
# endif
#endif
#if !defined(NITERS)
#define NITERS 1
#endif
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <sys/time.h>
#include <signal.h>
#endif
