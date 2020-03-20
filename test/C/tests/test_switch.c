void A()
{
    int i = 0;

    switch (i)
    {
        case 0:
            1 + 2;
            break;
        case 1:
            2 + 3;
            break;
        default:
            5 + 2;
    }
}

void B()
{
    switch (2 + 3)
        case 1:
            break;
}

void C()
{
    switch(1 + 2)
    {
        // This Switch will not be executed, but is shown in the CFG!
        switch (2 + 3)
            default:
                3 + 4;
        default:
            4 + 5;
    }
}

void Z()
{
    switch (1)
    {
        {
            {
                case 0:
                    break;
                case 1:
                    1 + 2;
            }

            2 + 3;

            case 2:
                break;
        }

        default:
            3 + 4;
    }
}