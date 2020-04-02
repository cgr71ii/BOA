int main(int argc, char** argv)
{
    int a = argc;   // tainted
    int b = 2;      // not tainted

    for (int i = b; i < 10; i++)    // not tainted
    {
        if (a)  // tainted
        {
            a = b;  // still tainted
        }
        if (b)  // not tainted
        {
            a = b;  // from tainted to not tainted!
        }
    }

    char* d = argv[0];
    char* e = d;
    char f[5] = "hola\0";
    char copy[20];
    strcpy(copy, e);
    strcpy(copy, f);

    return 0;
}