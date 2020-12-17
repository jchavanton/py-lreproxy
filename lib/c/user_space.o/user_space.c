#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <linux/netlink.h>
#include <ctype.h>
#include <time.h>
#include <time.h>

// NETLINK ------------------------------------------->
#define NETLINK_USER 31
#define MAX_PAYLOAD 1024 /* maximum payload size*/

struct sockaddr_nl src_addr, dest_addr;
struct nlmsghdr *nlh = NULL;
struct iovec iov;
int sock_fd;
struct msghdr msg;
// NETLINK <-------------------------------------------


void logger(const char *msg) {

    FILE *fp;
    fp = fopen("/var/log/pylreproxy/user_space.log", "a+");

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    char *res = (char *) malloc(sizeof(char) * 256);
    sprintf(res, "%d-%02d-%02d %02d:%02d:%02d %s:%d: %s\n", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour,
            tm.tm_min, tm.tm_sec, __FILE__, __LINE__, msg);
    printf("%s", res);
    fputs(res, fp);
    fclose(fp);
}


void error(const char *msg) {
    logger(msg);
    perror(msg);
    exit(1);
}



int main() {
    logger("Starting user_space.c");

    int sockfd, newsockfd, portno;
    socklen_t clilen;
    char buffer[1024];

    struct sockaddr_un serv_addr, cli_addr;
    int n;

    // Create unix socket
    sockfd = socket(AF_UNIX, SOCK_SEQPACKET, 0);
    if (sockfd < 0) {
     logger("Error opening unix socket");
     error("Error opening unix socket");
    }

    bzero((char *) &serv_addr, sizeof(serv_addr));

    serv_addr.sun_family = AF_UNIX;
    strcpy(serv_addr.sun_path, "/root/sock");
    serv_addr.sun_path[sizeof(serv_addr.sun_path) - 1] = '\0';


    // Create netlink socket
    sock_fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_USER);
    if (sock_fd < 0) {
        logger("Socket can't connected for netlink");
        return -1;
    }

    memset(&src_addr, 0, sizeof(src_addr));
    src_addr.nl_family = AF_NETLINK;
    src_addr.nl_pid = getpid(); /* self pid */;

    // bind socket
    bind(sock_fd, (struct sockaddr *) &src_addr, sizeof(src_addr));

    memset(&dest_addr, 0, sizeof(dest_addr));
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.nl_family = AF_NETLINK;
    dest_addr.nl_pid = 0; /* For Linux Kernel */
    dest_addr.nl_groups = 0; /* unicast */

    nlh = (struct nlmsghdr *) malloc(NLMSG_SPACE(MAX_PAYLOAD));
    memset(nlh, 0, NLMSG_SPACE(MAX_PAYLOAD));
    nlh->nlmsg_len = NLMSG_SPACE(MAX_PAYLOAD);
    nlh->nlmsg_pid = getpid();
    nlh->nlmsg_flags = 0;


    if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
        logger("Error on binding");
        error("Error on binding");
    }

    listen(sockfd, 5);

    newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);

    if (newsockfd < 0) {
        logger("Error on accept");
        error("Error on accept");
    }

    bzero(buffer, 1024);


    while (1) {
        logger("Waiting for send");

        n = read(newsockfd, buffer, 1024);
        if (n < 0) {
            logger("ERROR reading from socket");
            error("ERROR reading from socket");
        }
        printf("Get message of user_spaec: %s\n", buffer);
        // fflush(stdout);


        strcpy(NLMSG_DATA(nlh), buffer);

        iov.iov_base = (void *) nlh;
        iov.iov_len = nlh->nlmsg_len;
        msg.msg_name = (void *) &dest_addr;
        msg.msg_namelen = sizeof(dest_addr);
        msg.msg_iov = &iov;
        msg.msg_iovlen = 1;

        logger("Sending message to kernel");
        sendmsg(sock_fd, &msg, 0);

    }

    logger("Starting close socket");
    close(newsockfd);
    logger("Close socket of kernel");
    close(sockfd);
    logger("Close socket of Unix");
    return 0;
}
