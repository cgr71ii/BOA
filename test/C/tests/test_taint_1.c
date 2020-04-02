void main()
{
    char x[20];

    gets(x);

    char* y = x;
    int z;

    if (y == 0)
    {
        z = 0;
    }
    else
    {
        z = 1;
    }

    system(z);
}
