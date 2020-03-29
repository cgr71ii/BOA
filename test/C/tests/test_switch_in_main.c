int main(int argc, char** argv)
{
    int a;
    int b = 2;
    
    switch (1 + 2)
    {
        {
            {
                case 0:
                    1 + 2;
                    break;
                case 1:
                    1 + 2;
                case 2 + 3 * 2:
                    1 + 2;
                    break;
            }

            2 + 3;

            case 2:
                break;
        }

        default:
            3 + 4;
    }

    for (;;);

    return 0;
}