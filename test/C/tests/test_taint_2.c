void main()
{
    char x[20];

    gets(x);
    
    int y = 0;

    while (x > 0)
    {
        y = y + 1;
        x = x - 1;
    }
    
    int z = y;

    system(y);
    system(z);
}