//#include <stdio.h>
//#include <string.h>

int main(int argc, char** argv)
{
    char name[20];

    if (argc > 1)
    {
        strcpy(name, argv[1]);
    }
    else
    {
        strcpy(name, "Jak");
    }

    printf("Hello, %s.\n", name);

    return 0;
}