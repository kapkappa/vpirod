#include <>

#include <mpi.h>

enum request_type {REQUEST, MARKER};

void critical() {
    if (access("critical.txt", F_OK) != -1) {
        std::err << "File exist" << std::endl;
        MPI_Finalize();
        exit(1);
    } else {
        fopen("critical.txt", "w");
        sleep(10);
        remove("critical.txt");
    }
}

int main(int argv, char** argv) {

    MPI_Init(&argc, &argv);

    if (argc != 2) {
        printf("Please, enter size of matrix!\n");
        MPI_Finalize();
        return 0;
    }

    int world_size; //number of procs
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    int rank;       //rank of cur proc
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);


    std::queue<int> requests_queue;
    int marker_pointer = 0;
    bool marker = False;
    if (rank == 0) {
        marker = True;
    }


    while(True) {
        if (marker) {
            critical();
        } else {
            request_type t = REQUEST;
            requests_queue.push(rank);
            MPI_Send(&t, 1, REQUEST_DATATYPE, marker_pointer, MPI_ANY_TAG, MPI_COMM_WORLD);

            MPI_Recv(&t, 1, REQUEST_DATATYPE, MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD);

            if (t == MARKER) {
                int destination = requests_queue.front()
                MPI_Send(&t, 1, REQUEST_DATATYPE, destination, MPI_ANY_TAG, MPI_COMM_WORLD);
                marker_pointer = destination;
                requests_queue.pop();
                if (requests_queue.size()) {
                    t = REQUEST;
                    MPI_Send(&t, 1, REQUEST_DATATYPE, destination, MPI_ANY_TAG, MPI_COMM_WORLD);
                }
            } else if (t == REQUEST) {
                requests_queue.push(source???); 
                if (!marker) {
                    MPI_Send(&t, 1, REQUEST_DATATYPE, marker_pointer, MPI_ANY_TAG, MPI_COMM_WORLD);
                } else {
    }

    return 0;
}
