#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv)
{
    if (argc != 3)
        return 1;

    char* size = argv[1];
    int command_size = atoi(size);
    char* command = argv[2];
    char* buffer = (char*)malloc(command_size * sizeof(char));
    strncpy(buffer, command, strlen(command));

    system(buffer);

    return 0;
}
