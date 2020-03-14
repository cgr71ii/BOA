
#include <stdio.h>

void A()
{
	printf("1\n");
	goto a_label;
	printf("2\n");
	a_label:
	printf("3\n");
}

void B()
{
	int max = 10;

	for (int i = 0; i < max; i++)
	{
		printf("i = %d (max = %d)\n", i, max);

		if (i > max / 2)
		{
			goto b_out_of_scope;
		}
	}

	b_out_of_scope:
	printf("out of 'for' scope\n");
}

void C()
{
	int i = 0;
	c_loop:
	i++;
	printf("C: i = %d\n", i);
	if (i > 5)
	{
		printf("out of c\n");
		return;
	}
	goto c_loop;
}

int main(int argc, char** argv)
{
	A();
	B();
	C();

	return 0;
}