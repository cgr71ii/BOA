
#include <stdio.h>

void A()
{
	int i;
	int j = 0;

	for (i = 0; i < 10; i++)
	{
		{
			if (i % 2 == 0)
				continue;
		}
		j++;
	}

	printf("j = %d\n", j);
}

void B()
{
	int i = 10;
	int j = 0;

	while (i--)
	{
		if (i % 2 == 0)
			j++;
		if (i == 100)
			break;
	}

	printf("j = %d\n", j);
}

void C()
{
	int i = 10;
	int j = 0;

	do
	{
		if (i % 2 == 0)
			j++;
	}
	while(--i);

	printf("j = %d\n", j);
}

void D()
{
    // 6
	for (;;)
		break;
    // 10
	for (;;)
	{
		printf(";;\n");
		break;
	}
    // 18
	for (int i = 0;;)
	{
		printf("int i = 0;;\n");
		break;
	}

	int i = 0;

    // 35
	for (; i < 10;)
	{
		printf("; i < 10;\n");
		break;
	}
    // 46
	for (;; i++)
	{
		printf(";; i++\n");
		break;
	}
    // 56
	for (int j = 0; j < 10;)
	{
		printf("int j = 0; j < 10;\n");
		break;
	}
    // 72
	for (int j = 0;; j++)
	{
		printf("int j = 0;; j++\n");
		break;
	}
    // 87
	for (; i < 10; i++)
	{
		printf("; i < 10; i++\n");
		break;
	}
    // 100
	for (int j = 0; j < 10; j++)
	{
		printf("int j = 0; j < 10; j++\n");
		break;
	}
    // 118
	// Infinite loop
	for (;;);

    // 122
    for (int j = 0; j < 10; j++)
    {
        // 134
        for (int j = 0; j + k < 20; k++)
        {
            continue;
        }
    }
}

int main(int argc, char** argv)
{
	A();
	B();
	C();
	D();

	return 0;
}