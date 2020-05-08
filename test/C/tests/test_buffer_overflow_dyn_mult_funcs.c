#include <stdlib.h>
#include <string.h>

int execute_command(char* command, int size)
{
    char* buffer = (char*)malloc(size * sizeof(char));
    strncpy(buffer, command, strlen(command));

    system(buffer);
}

int main(int argc, char** argv)
{
    if (argc != 3)
        return 1;

    char* size = argv[1];
    int command_size = atoi(size);

    execute_command(argv[2], command_size);

    return 0;
}
