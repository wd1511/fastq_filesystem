#include<stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <string.h>
#include <linux/netlink.h>
#include <stdint.h>
#include <unistd.h>
#include <errno.h>
#define NETLINK_TEST     30
#define MSG_LEN          70000
#define MAX_PLOAD        70000
typedef struct _user_msg_info
{
    struct nlmsghdr hdr;
    char  msg[MSG_LEN];
} user_msg_info;

int main(int argc, char **argv)
{
    int skfd;
    int ret;
    user_msg_info u_info;
    socklen_t len;
    struct nlmsghdr *nlh = NULL;
    struct sockaddr_nl saddr, daddr;

    /* 创建NETLINK socket */
    skfd = socket(AF_NETLINK, SOCK_RAW, NETLINK_TEST);
    if(skfd == -1)
    {
        perror("create socket error\n");
        return -1;
    }

    memset(&saddr, 0, sizeof(saddr));
    saddr.nl_family = AF_NETLINK; //AF_NETLINK
    saddr.nl_pid = 100;  //端口号(port ID) 
    saddr.nl_groups = 0;
    if(bind(skfd, (struct sockaddr *)&saddr, sizeof(saddr)) != 0)
    {
        perror("bind() error\n");
        close(skfd);
        return -1;
    }

    memset(&daddr, 0, sizeof(daddr));
    daddr.nl_family = AF_NETLINK;
    daddr.nl_pid = 0; // to kernel 
    daddr.nl_groups = 0;

    nlh = (struct nlmsghdr *)malloc(NLMSG_SPACE(MAX_PLOAD));
    memset(nlh, 0, sizeof(struct nlmsghdr));
    nlh->nlmsg_len = NLMSG_SPACE(MAX_PLOAD);
    nlh->nlmsg_flags = 0;
    nlh->nlmsg_type = 0;
    nlh->nlmsg_seq = 0;
    nlh->nlmsg_pid = saddr.nl_pid; //self port



    memset(&u_info, 0, sizeof(u_info));
    len = sizeof(struct sockaddr_nl);
    char command[255];
    char op[10];
    char filepath[255];
    char dcmp_path[255];
    char info[100];
    long long pos=0;
    long long  count=0;
    const char *sep=",";
    char *handler=NULL;
    char buf[70000];
    //FILE *fp=fopen(dcmp_path,"r");
    FILE *fp=NULL;
    while(1)
    {
        ret = recvfrom(skfd, &u_info, sizeof(user_msg_info), 0, (struct sockaddr *)&daddr, &len);
	if(pos==66789376)
        {
            printf("CORE DUMP WARNING");
        }
        if(!ret)
        {
            perror("recv form kernel error\n");
            close(skfd);
            exit(-1);
        }

        handler=strtok(u_info.msg,sep);     
        memcpy(op,handler,strlen(handler));
	handler=strtok(NULL,sep);
        memcpy(filepath,handler,strlen(handler));
        handler=strtok(NULL,sep);
        count=atoll(handler);
	handler=strtok(NULL,sep);
        pos=atoll(handler);
        printf("%s,%s,%lld,%lld\n",op,filepath,count,pos);
        memcpy(dcmp_path,filepath,strlen(filepath));
        memcpy(dcmp_path+strlen(filepath),".dcmp",5);
        //printf("%s\n",dcmp_path);
	
        if(access(dcmp_path,0)==-1)
        {
            sprintf(command,"mv %s %s.cmp",filepath,filepath);
            ///printf("%s\n",command);
            system(command);
            
            sprintf(command,"./fqz_comp -d %s.cmp %s",filepath,dcmp_path);
            //printf("%s\n",command);
            system(command);

            sprintf(command,"mv %s.cmp %s",filepath,filepath);
            //printf("%s\n",command);
            system(command);
        }
        char *umsg=NLMSG_DATA(nlh);
        //if(fp==NULL)
        fp=fopen(dcmp_path,"r");
        int i=0;
        fseek(fp,pos,0);
        for(;i!=count&&( umsg[i]=fgetc(fp))!=EOF&&!feof(fp);i++);
        //printf("I %d\n",i);
        umsg[i]='\0';
	//if(feof(fp))
        fclose(fp);
	
        ret = sendto(skfd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&daddr, sizeof(struct sockaddr_nl));
	printf("send %d \n",strlen(NLMSG_DATA(nlh)));
        if(!ret)
        {
            perror("sendto error\n");
            close(skfd);
            exit(-1);
        }
        
    }
    close(skfd);
    free((void *)nlh);
    return 0;
}
