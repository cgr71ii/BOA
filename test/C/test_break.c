
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