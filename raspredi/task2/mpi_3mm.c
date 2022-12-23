#include "3mm.h"
#include <signal.h>
#include <mpi.h>
#include <mpi-ext.h>

double bench_t_start, bench_t_end;
const int niters = NITERS;
int A_rows, B_rows, C_rows, D_rows, E_rows, F_rows;
int new_rank, rank, world_size;
unsigned error_occured = 0;
MPI_Comm main_comm;


static double rtclock() {
  struct timeval Tp;
  int stat;
  stat = gettimeofday(&Tp, NULL);
  if (stat != 0)
    printf("Error return from gettimeofday: %d", stat);
  return (Tp.tv_sec + Tp.tv_usec * 1.0e-6);
}

void bench_timer_start() { bench_t_start = MPI_Wtime(); }

void bench_timer_stop() { bench_t_end = MPI_Wtime(); }

void bench_timer_print() {
  printf("Time in seconds = %0.6lf\n", (bench_t_end - bench_t_start) / niters);
}

static void init_array(int ni, int nj, int nk, int nl, int nm, float *A,
                       float *B, float *C, float *D) {
  int i, j;

  for (i = 0; i < ni; i++)
    for (j = 0; j < nk; j++)
      A[i * nk + j] = (float)((i * j + 1) % ni) / (5 * ni);
  for (i = 0; i < nk; i++)
    for (j = 0; j < nj; j++)
      B[i * nj + j] = (float)((i * (j + 1) + 2) % nj) / (5 * nj);
  for (i = 0; i < nj; i++)
    for (j = 0; j < nm; j++)
      C[i * nm + j] = (float)(i * (j + 3) % nl) / (5 * nl);
  for (i = 0; i < nm; i++)
    for (j = 0; j < nl; j++)
      D[i * nl + j] = (float)((i * (j + 2) + 2) % nk) / (5 * nk);
}

static void print_matrix(int ni, int nl, float *M) {
  int i, j;
  for (i = 0; i < ni; i++) {
    for (j = 0; j < nl; j++)
      printf("%10.1f ", M[i * nl + j]);
    printf("\n");
  }
}

static double calculate_matrix_trace(int ni, int nl, float *G) {
  int min, i;
  if (ni < nl)
    min = ni;
  else
    min = nl;
  double trace = 0.0;
  for (i = 0; i < min; i++)
    trace += G[i * nl + i];
  return trace;
}





static void print_array(int size, int *array) {
  int i;
  for (i = 0; i < size; i++)
    printf("%d ", array[i]);
  printf("\n");
}



////////////////////////////



static void kernel_3mm(int ni, int nj, int nk, int nl, int nm, float *E,
                       float *A, float *B_recv, float *B_send,
                       int *B_sendcounts, float *F_recv, float *F_send,
                       int *F_sendcounts, float *C, float *D_recv,
                       float *D_send, int *D_sendcounts, float *G);

static void errhandler(MPI_Comm* pcomm, int* perr, ...);



////////////////////////////



int main(int argc, char **argv) {
  MPI_Init(&argc, &argv);
  MPI_Comm_size(MPI_COMM_WORLD, &world_size);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);

  main_comm = MPI_COMM_WORLD;

  MPI_Errhandler errh;
  MPI_Comm_create_errhandler(errhandler, &errh);
  MPI_Comm_set_errhandler(main_comm, errh);
  MPI_Barrier(main_comm);

  int i, k, l;
  int ni = NI;
  int nj = NJ;
  int nk = NK;
  int nl = NL;
  int nm = NM;

  // pointer for full-size matrices: A,B,C,D - source, G - result
  float *A, *B, *C, *D, *G;

  // pointer for local matrices on each process
  float *A_local, *B_to_recv, *B_to_send, *C_local, *D_to_recv, *D_to_send,
      *E_local, *F_to_recv, *F_to_send, *G_local;

  // Fill source matrices on master process
  if (rank == 0) {
    A = (float *)malloc(ni * nk * sizeof(float));
    B = (float *)malloc(nk * nj * sizeof(float));
    C = (float *)malloc(nj * nm * sizeof(float));
    D = (float *)malloc(nm * nl * sizeof(float));
    init_array(ni, nj, nk, nl, nm, A, B, C, D);
  }


  int A_block_rows, A_extra_rows;
  int B_block_rows, B_extra_rows;
  int C_block_rows, C_extra_rows;
  int D_block_rows, D_extra_rows;

  // Prepare arrays for MPI_Scatterv operation
  int A_sendcounts[world_size], B_sendcounts[world_size],
      C_sendcounts[world_size], D_sendcounts[world_size],
      F_sendcounts[world_size];
  int A_displs[world_size], B_displs[world_size], C_displs[world_size],
      D_displs[world_size], G_displs[world_size];
  int G_recvcounts[world_size];


  if (rank == (world_size - 1)) {
    printf("process %d has been killed", rank);
    raise(SIGKILL);
  }

checkpoint:

  // Master process contains extra rows of matrices, because elements cant be
  // divided across processes equally So here we calculate number of rows for
  // each process
  A_block_rows = ni / world_size, A_extra_rows = ni % world_size;
  B_block_rows = nk / world_size, B_extra_rows = nk % world_size;
  C_block_rows = nj / world_size, C_extra_rows = nj % world_size;
  D_block_rows = nm / world_size, D_extra_rows = nm % world_size;
  A_rows = A_block_rows;
  B_rows = B_block_rows;
  C_rows = C_block_rows;
  D_rows = D_block_rows;
  if (rank == 0) {
    A_rows += A_extra_rows;
    B_rows += B_extra_rows;
    C_rows += C_extra_rows;
    D_rows += D_extra_rows;
  }

  // Buffer arrays for cyclic shift of source matrices during computation
  B_to_send =
      (float *)malloc((B_block_rows + B_extra_rows) * nj * sizeof(float));
  D_to_send =
      (float *)malloc((D_block_rows + D_extra_rows) * nl * sizeof(float));

  // Create arrays on each slave process for their part of source matrices
  // On master process, only copying the pointer
  if (rank == 0) { A_local = A; B_to_recv = B; C_local = C; D_to_recv = D;
  } else {
    A_local = (float *)malloc(A_rows * nk * sizeof(float));
    C_local = (float *)malloc(C_rows * nm * sizeof(float));
    B_to_recv =
        (float *)malloc((B_block_rows + B_extra_rows) * nj * sizeof(float));
    D_to_recv =
        (float *)malloc((D_block_rows + D_extra_rows) * nl * sizeof(float));
  }

  // Fill these arrays
  for (i = 0; i < world_size; i++) {
    A_sendcounts[i] = A_block_rows * nk;
    B_sendcounts[i] = B_block_rows * nj;
    C_sendcounts[i] = C_block_rows * nm;
    D_sendcounts[i] = D_block_rows * nl;
    F_sendcounts[i] = C_block_rows * nl;
    G_recvcounts[i] = A_block_rows * nl;
    A_displs[i] = i * A_block_rows * nk + A_extra_rows * nk;
    B_displs[i] = i * B_block_rows * nj + B_extra_rows * nj;
    C_displs[i] = i * C_block_rows * nm + C_extra_rows * nm;
    D_displs[i] = i * D_block_rows * nl + D_extra_rows * nl;
    G_displs[i] = i * A_block_rows * nl + A_extra_rows * nl;
  }

  A_sendcounts[0] += A_extra_rows * nk;
  B_sendcounts[0] += B_extra_rows * nj;
  C_sendcounts[0] += C_extra_rows * nm;
  D_sendcounts[0] += D_extra_rows * nl;
  F_sendcounts[0] += C_extra_rows * nl;
  G_recvcounts[0] += A_extra_rows * nl;
  A_displs[0] = 0;
  B_displs[0] = 0;
  C_displs[0] = 0;
  D_displs[0] = 0;
  G_displs[0] = 0;
  // Distribute source matrices across processes
  MPI_Scatterv(A, A_sendcounts, A_displs, MPI_FLOAT, A_local,
               A_sendcounts[rank], MPI_FLOAT, 0, main_comm);
  MPI_Scatterv(B, B_sendcounts, B_displs, MPI_FLOAT, B_to_recv,
               B_sendcounts[rank], MPI_FLOAT, 0, main_comm);
  MPI_Scatterv(C, C_sendcounts, C_displs, MPI_FLOAT, C_local,
               C_sendcounts[rank], MPI_FLOAT, 0, main_comm);
  MPI_Scatterv(D, D_sendcounts, D_displs, MPI_FLOAT, D_to_recv,
               D_sendcounts[rank], MPI_FLOAT, 0, main_comm);

  E_local = (float *)calloc(A_rows * nj, sizeof(float));
  F_to_recv =
      (float *)calloc((C_block_rows + C_extra_rows) * nl, sizeof(float));
  F_to_send =
      (float *)calloc((C_block_rows + C_extra_rows) * nl, sizeof(float));

  G = (float *)calloc(ni * nl, sizeof(float));
  G_local = (float *)calloc(A_rows * nl, sizeof(float));

  MPI_Barrier(main_comm);
  bench_timer_start();

  kernel_3mm(ni, nj, nk, nl, nm, E_local, A_local, B_to_recv, B_to_send,
               B_sendcounts, F_to_recv, F_to_send, F_sendcounts, C_local,
               D_to_recv, D_to_send, D_sendcounts, G_local);

  MPI_Barrier(main_comm);

  if (error_occured == 1) {
    error_occured = 0;
    goto checkpoint;
  }

  MPI_Allgatherv(G_local, A_rows * nl, MPI_FLOAT, G, G_recvcounts, G_displs,
                   MPI_FLOAT, main_comm);

  MPI_Barrier(main_comm); bench_timer_stop();

  bench_timer_print();
  printf("Result matrix trace: %lf\n", calculate_matrix_trace(ni, nl, G));

  free(A_local);
  free(B_to_recv);
  free(B_to_send);
  free(C_local);
  free(D_to_recv);
  free(D_to_send);

  free(E_local);
  free(F_to_recv);
  free(F_to_send);
  free(G);
  free(G_local);
  MPI_Finalize();
  return 0;
}





////////////////////////






static void errhandler(MPI_Comm* pcomm, int* perr, ...) {
    printf("Proc №%d in errhandler\n", rank);

    error_occured = 1;
    int err = *perr;
    char errstr[MPI_MAX_ERROR_STRING];
    int size, nf, len;
    MPI_Group group_f;

    MPI_Comm_size(main_comm, &size);
    MPIX_Comm_failure_ack(main_comm);
    MPIX_Comm_failure_get_acked(main_comm, &group_f);
    MPI_Group_size(group_f, &nf);
    MPI_Error_string(err, errstr, &len);


    MPIX_Comm_shrink(main_comm, &main_comm);
    MPI_Comm_rank(main_comm, &new_rank);
    MPI_Comm_size(main_comm, &world_size);
}





static void kernel_3mm(int ni, int nj, int nk, int nl, int nm, float *E,
                       float *A, float *B_recv, float *B_send,
                       int *B_sendcounts, float *F_recv, float *F_send,
                       int *F_sendcounts, float *C, float *D_recv,
                       float *D_send, int *D_sendcounts, float *G) {
  int i, j, k, iter;

  int B_row_displs = 0;
  for (i = 0; i <= rank; i++)
    B_row_displs += nk / world_size;
  if (B_row_displs != 0)
    B_row_displs += nk % world_size;

  for (iter = 0; iter < world_size; iter++) {
    if (rank != iter)
      B_rows = nk / world_size;
    else
      B_rows = nk / world_size + (nk % world_size);

    B_row_displs = (B_row_displs - B_rows + nk) % nk;

    for (i = 0; i < A_rows; i++)
      for (j = 0; j < nj; j++) {
        for (k = 0; k < B_rows; ++k)
          E[i * nj + j] += A[i * nk + B_row_displs + k] * B_recv[k * nj + j];
      }
    float *tmp = B_recv;
    B_recv = B_send;
    B_send = tmp;

    if (error_occured == 1) {
      error_occured = 0;
      goto checkpoint;
    }

    MPI_Sendrecv(B_send, B_sendcounts[(world_size + rank - iter) % world_size],
                 MPI_FLOAT, (rank + 1) % world_size, 0, B_recv,
                 B_sendcounts[(world_size + rank - iter - 1) % world_size],
                 MPI_FLOAT, (world_size + rank - 1) % world_size, 0,
                 main_comm, MPI_STATUS_IGNORE);
  }

  int D_row_displs = 0;
  for (i = 0; i <= rank; i++)
    D_row_displs += nm / world_size;
  if (D_row_displs != 0)
    D_row_displs += nm % world_size;

  for (iter = 0; iter < world_size; iter++) {
    if (rank != iter)
      D_rows = nm / world_size;
    else
      D_rows = nm / world_size + (nm % world_size);

    D_row_displs = (D_row_displs - D_rows + nm) % nm;

    for (i = 0; i < C_rows; i++)
      for (j = 0; j < nl; j++) {
        for (k = 0; k < D_rows; ++k)
          F_recv[i * nl + j] +=
              C[i * nm + D_row_displs + k] * D_recv[k * nl + j];
      }
    float *tmp = D_recv;
    D_recv = D_send;
    D_send = tmp;

    if (error_occured == 1) {
      error_occured = 0;
      goto checkpoint;
    }

    MPI_Sendrecv(D_send, D_sendcounts[(world_size + rank - iter) % world_size],
                 MPI_FLOAT, (rank + 1) % world_size, 1, D_recv,
                 D_sendcounts[(world_size + rank - iter - 1) % world_size],
                 MPI_FLOAT, (world_size + rank - 1) % world_size, 1,
                 main_comm, MPI_STATUS_IGNORE);
  }

  int F_row_displs = 0;
  for (i = 0; i <= rank; i++)
    F_row_displs += nj / world_size;
  if (F_row_displs != 0)
    F_row_displs += nj % world_size;

  for (iter = 0; iter < world_size; iter++) {
    if (rank != iter)
      F_rows = nj / world_size;
    else
      F_rows = nj / world_size + (nj % world_size);

    F_row_displs = (F_row_displs - F_rows + nj) % nj;

    for (i = 0; i < A_rows; i++)
      for (j = 0; j < nl; j++) {
        for (k = 0; k < F_rows; ++k)
          G[i * nl + j] += E[i * nj + F_row_displs + k] * F_recv[k * nl + j];
      }
    float *tmp = F_recv;
    F_recv = F_send;
    F_send = tmp;
    MPI_Sendrecv(F_send, F_sendcounts[(world_size + rank - iter) % world_size],
                 MPI_FLOAT, (rank + 1) % world_size, 2, F_recv,
                 F_sendcounts[(world_size + rank - iter - 1) % world_size],
                 MPI_FLOAT, (world_size + rank - 1) % world_size, 2,
                 main_comm, MPI_STATUS_IGNORE);
  }
}
