
void Z()
{
    // Not invoked
}

void W()
{
    return;
}

void A()
{

}

int B()
{
    return 5;
}

float C()
{
    return (float)B() + (float)B() + 1.1f;
}

double D()
{
    return (double)C();
}

char E()
{
    A();
}

int F(int max)
{
    E();
    (int)D();

    if (max > 0)
    {
        F(max--);
    }
}

int main(int argc, char** argv)
{
    F(1);
    return 0;
}