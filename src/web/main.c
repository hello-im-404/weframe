#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>
#include <errno.h>

#define MAX_THREADS 5000
#define TIMEOUT_SEC 1
#define TIMEOUT_USEC 0

typedef struct {
    const char *target;
    int port;
    int is_open;
} scan_task_t;

typedef struct {
    const char *target;
    int start_port;
    int end_port;
    int thread_id;
    int *open_ports;
    int *open_count;
    pthread_mutex_t *mutex;
} thread_data_t;

int dns_lookup(const char *hostname, char *ip) {
    struct hostent *host = gethostbyname(hostname);
    if (host == NULL) return -1;
    strcpy(ip, inet_ntoa(*(struct in_addr*)host->h_addr_list[0]));
    return 0;
}

int scan_port(const char *ip, int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return 0;

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(port)
    };
    inet_pton(AF_INET, ip, &addr.sin_addr);

    struct timeval timeout = {TIMEOUT_SEC, TIMEOUT_USEC};
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    int result = connect(sock, (struct sockaddr*)&addr, sizeof(addr));
    close(sock);
    
    return (result == 0) ? 1 : 0;
}

void* scan_ports_range(void *arg) {
    thread_data_t *data = (thread_data_t*)arg;
    char ip[16];
    
    if (dns_lookup(data->target, ip) != 0) {
        printf("DNS lookup failed for %s\n", data->target);
        return NULL;
    }

    for (int port = data->start_port; port <= data->end_port; port++) {
        if (scan_port(ip, port)) {
            pthread_mutex_lock(data->mutex);
            data->open_ports[(*data->open_count)++] = port;
            pthread_mutex_unlock(data->mutex);
        }
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Usage: %s <target> <start_port> <end_port>\n", argv[0]);
        printf("Example: %s google.com 1 1000\n", argv[0]);
        return 1;
    }

    char *target = argv[1];
    int start_port = atoi(argv[2]);
    int end_port = atoi(argv[3]);
    int total_ports = end_port - start_port + 1;
    
    if (total_ports <= 0) {
        printf("Invalid port range\n");
        return 1;
    }

    int thread_count = (total_ports < MAX_THREADS) ? total_ports : MAX_THREADS;
    int ports_per_thread = total_ports / thread_count;
    
    printf("Scanning %s ports %d-%d with %d threads...\n", 
           target, start_port, end_port, thread_count);

    pthread_t threads[thread_count];
    thread_data_t thread_data[thread_count];
    int open_ports[total_ports];
    int open_count = 0;
    pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

    // Создаем потоки
    for (int i = 0; i < thread_count; i++) {
        thread_data[i] = (thread_data_t){
            .target = target,
            .start_port = start_port + (i * ports_per_thread),
            .end_port = (i == thread_count - 1) ? end_port : 
                       start_port + ((i + 1) * ports_per_thread) - 1,
            .thread_id = i,
            .open_ports = open_ports,
            .open_count = &open_count,
            .mutex = &mutex
        };
        pthread_create(&threads[i], NULL, scan_ports_range, &thread_data[i]);
    }

    // Ждем завершения всех потоков
    for (int i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
    }

    // Выводим результаты
    printf("\nOpen ports on %s:\n", target);
    for (int i = 0; i < open_count; i++) {
        printf("Port %d is open\n", open_ports[i]);
    }
    printf("Scan completed. Found %d open ports.\n", open_count);

    pthread_mutex_destroy(&mutex);
    return 0;
}
