
void A()
{
    for (;;)
    {
        1;
        1 + 1;
        continue;
        1 + 1 + 1;
    }

    for (;;)
        continue;

    while (1)
        continue;

    while (1)
    {
        1;
        continue;
        1;
    }

    do
        continue;
    while (1);
}

void B()
{
    for (;;)
        for (;;)
            continue;
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
                        continue;
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
                continue;
        case 4:
            break;
    }
}

void D()
{
    while (1)
    {
        do
            continue;
        while (1);

        continue;

        for (;;)
        {
            continue;
        }

        for (; 1;)
            continue;

        continue;

        for (int i = 0;; i++)
            continue;

        continue;
    }
}