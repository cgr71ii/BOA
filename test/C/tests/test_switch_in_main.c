int main(int argc, char** argv)
{
    int a;                      // 1
    int b = 2;                  // 2
    
    switch (1 + 2)              // 3
    {                           // 4
        {                       // 5
            {                   // 6
                case 0:         // 7
                    1 + 2;      // 8
                    break;      // 9
                case 1:         // 10
                    1 + 2;      // 11
                case 2 + 3 * 2: // 12
                    1 + 2;      // 13
                    break;      // 14
            }

            2 + 3;              // 15

            case 2:             // 16
                break;          // 17
        }

        default:                // 18
            3 + 4;              // 19
    }

    for (;;);                   // 20, 21, 22

    return 0;                   // 23
}                               // 24