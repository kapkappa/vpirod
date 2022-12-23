#include <iostream>
#include <queue>
#include <stdio.h>
#include <unistd.h>

#include <mpi.h>

enum message_type : int8_t { REQUEST, MARKER, SPECIAL };

struct tree {
  std::queue<int> request_queue;
  int rank;
  int root;
  int left;
  int right;
  int marker_pointer; // 0 - parent, 1 - left, 2 -right
  bool marker;

  tree() {}

  tree(int _rank, int _root, int _left, int _right, int _marker_pointer,
       bool _marker)
      : rank(_rank), root(_root), left(_left), right(_right),
        marker_pointer(_marker_pointer), marker(_marker) {}

  void critical() {
    if (access("critical.txt", F_OK) != -1) {
      std::cerr << "File exist" << std::endl;
      MPI_Finalize();
      exit(1);
    } else {
      fopen("critical.txt", "w");
      std::cout << "CRITICAL; rank: " << rank << std::endl;
      sleep(3);
      remove("critical.txt");
    }
  }

  void receive(message_type message, int sender) {

    if (message == MARKER) {

      if (!request_queue.empty()) {

        int requester = request_queue.front();
        request_queue.pop();

        std::cout << "send marker from " << rank << " to " << requester
                  << std::endl;

        if (requester == rank) {
          marker = true;
          critical();
        } else if (requester == root) {
          marker = false;
          marker_pointer = 0;
          message_type tmp = MARKER;
          MPI_Send(&tmp, 1, MPI_INT8_T, requester, 0, MPI_COMM_WORLD);
        } else if (requester == left) {
          marker = false;
          marker_pointer = 1;
          message_type tmp = MARKER;
          MPI_Send(&tmp, 1, MPI_INT8_T, requester, 0, MPI_COMM_WORLD);
        } else if (requester == right) {
          marker = false;
          marker_pointer = 2;
          message_type tmp = MARKER;
          MPI_Send(&tmp, 1, MPI_INT8_T, requester, 0, MPI_COMM_WORLD);
        } else {
          std::cerr << "Invalid rank in queue!" << std::endl;
          MPI_Finalize();
          exit(2);
        }

        if (!request_queue.empty()) {
          int receiver = request_queue.front();
          request_queue.pop();
          receive(REQUEST, receiver);
        }
      }
    } else if (message == REQUEST) {

      request_queue.push(sender);
      if (marker) {
        receive(MARKER, rank);
      } else {
        if (marker_pointer == 0) {
          message_type tmp = REQUEST;
          MPI_Send(&tmp, 1, MPI_INT8_T, root, 0, MPI_COMM_WORLD);
        } else if (marker_pointer == 1) {
          message_type tmp = REQUEST;
          MPI_Send(&tmp, 1, MPI_INT8_T, left, 0, MPI_COMM_WORLD);
        } else if (marker_pointer == 2) {
          message_type tmp = REQUEST;
          MPI_Send(&tmp, 1, MPI_INT8_T, right, 0, MPI_COMM_WORLD);
        } else {
          std::cerr << "Invalid marker pointer" << std::endl;
          MPI_Finalize();
          exit(3);
        }
      }
    }
  }

  void print() {
    std::cout << "rank: " << rank << ", root: " << root << ", left: " << left
              << ", right: " << right << ", marker pointer: " << marker_pointer
              << ", marker: " << marker << std::endl;
  }
};

int main(int argc, char **argv) {

  MPI_Init(&argc, &argv);

  int world_size; // number of processes
  MPI_Comm_size(MPI_COMM_WORLD, &world_size);

  int rank; // rank of current process
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);

  int tree_node_proc = 0;

  int marker_node = world_size - 1;

  int marker_cnt = marker_node;

  std::map<int, int> child_to_path;

  while (marker_cnt != tree_node_proc) {
    child_to_path[(marker_cnt - 1) / 2] = marker_cnt;
    marker_cnt = (marker_cnt - 1) / 2;
  }

  tree tree_elem;
  if (rank == 0) {
    tree_elem.rank = tree_node_proc;
    tree_elem.root = -1;
    tree_elem.left = 1;
    tree_elem.right = 2;
    tree_elem.marker_pointer = 0;
    tree_elem.marker = marker_node == tree_node_proc;
  } else {
    int left = 2 * rank + 1;
    if (left >= world_size)
      left = -1;

    int right = 2 * rank + 2;
    if (right >= world_size)
      right = -1;

    tree_elem.rank = rank;
    tree_elem.root = (rank - 1) / 2;
    tree_elem.left = left;
    tree_elem.right = right;
    tree_elem.marker_pointer = 0;
    tree_elem.marker = marker_node == rank;
  }

  if (child_to_path.contains(rank)) {
    int relative_marker_path = child_to_path[rank];
    if (tree_elem.left != -1 && relative_marker_path == tree_elem.left) {
      tree_elem.marker_pointer = 1;
    } else if (tree_elem.right != -1 &&
               relative_marker_path == tree_elem.right) {
      tree_elem.marker_pointer = 2;
    }
  }

  tree_elem.print();

  int previous_marker = marker_node;

  for (int request_sender = 0; request_sender < world_size; request_sender++) {

    MPI_Barrier(MPI_COMM_WORLD);

    MPI_Status status;

    if (rank == request_sender) {

      tree_elem.receive(REQUEST, rank);
      message_type tmp_m;
      if (tree_elem.marker_pointer == 0) {
        MPI_Recv(&tmp_m, 1, MPI_INT8_T, tree_elem.root, 0, MPI_COMM_WORLD,
                 &status);
      }
      if (tree_elem.marker_pointer == 1) {
        MPI_Recv(&tmp_m, 1, MPI_INT8_T, tree_elem.left, 0, MPI_COMM_WORLD,
                 &status);
      }
      if (tree_elem.marker_pointer == 2) {
        MPI_Recv(&tmp_m, 1, MPI_INT8_T, tree_elem.right, 0, MPI_COMM_WORLD,
                 &status);
      }

      if (tmp_m == MARKER) {
        tree_elem.receive(MARKER, tree_elem.root);
      } else {
        tree_elem.receive(REQUEST, tree_elem.root);
      }

      for (int i = 0; i < world_size; i++) {
        if (i != request_sender) {
          message_type tmp = SPECIAL;
          MPI_Send(&tmp, 1, MPI_INT8_T, i, 0, MPI_COMM_WORLD);
        }
      }
    } else {

      message_type inp = REQUEST;
      while (inp != SPECIAL) {
        message_type inp1;
        MPI_Status status;
        MPI_Recv(&inp1, 1, MPI_INT8_T, MPI_ANY_SOURCE, 0, MPI_COMM_WORLD,
                 &status);
        inp = inp1;
        if (inp == MARKER) {
          tree_elem.receive(MARKER, status.MPI_SOURCE);
        } else if (inp == REQUEST) {
          tree_elem.receive(REQUEST, status.MPI_SOURCE);
        }
      }
    }
    previous_marker = request_sender;

    MPI_Barrier(MPI_COMM_WORLD);
  }

  MPI_Finalize();
  return 0;
}
