void main()
{
    int x = source(i);  // 1 -> 2
    int y = x;          // 2 -> 3
    int z;              // 3 -> 4

    if (y == 0)         // 4 -> 5, 8
    {                   // 5 -> 6
        z = 0;          // 6 -> 7
    }                   // 7 -> 11
    else
    {                   // 8 -> 9
        z = 1;          // 9 -> 10
    }                   // 10 -> 11

    sink(z);            // 11 -> 12
}                       // 12 -> 13
                        // 13 -> End Of Program