
void A()
{
    for (;;)
    {
        1;
        1 + 1;
        break;
        1 + 1 + 1;
    }

    for (;;)
        break;

    while (1)
        break;

    while (1)
    {
        1;
        break;
        1;
    }

    do
        break;
    while (1);

    switch (1)
    {
        case 1:
            1;
            break;
            1;
        case 2:
            break;
        case 3:
        case 4:
        default:
            1;
            break;
            2;
    }
}

void B()
{
    for (;;)
        for (;;)
            break;
}

void B_2()
{
    for (;;)
    {
        break;
        for (;;)
            break;
        break;
    }
}

void C()
{
    switch (1)
    {
        case 2:
            switch (3)
            {
                case 5:
                    for (;;)
                        break;
                    break;
                case 4:
                    break;
                default:
                    switch (3)
                    {
                        case 4:
                            break;
                    }
            }
            break;
        case 3:
            for (;;)
                break;
        case 4:
            break;
    }
}

void D()
{
    switch (1 + 2)
    {
        switch (1)
            default:
                2 + 3;
                break;
        case 3:
            break;
        default:
            3 + 4;
    }
}

void E()
{
    switch (1)
    {
        default:
            break;
        case 1:
            break;
    }
}

void F()
{
    switch (1)
    {
        default:
            1;
        case 1:
            break;
    }
}