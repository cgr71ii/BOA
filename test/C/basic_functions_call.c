
void A()
{

}

int B()
{
    return 5;
}

float C()
{
    return (float)B();
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