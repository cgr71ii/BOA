void main()
{
    int x = source(i);
    int y = 0;

    while (x > 0)
    {
        y = y + 1;
        x = x - 1;
    }
    
    int z = y;

    sink1(y);
    sink2(z);
}