
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

int I()
{
    return 1;
}

int J()
{
    return I();
}

int K()
{
    // Not invoked

    return J();
}

void M()
{
    // Not invoked

    exit();
}

void O()
{

}

void P()
{
    O();
    Q() + O();
}

void Q()
{
    O();
    O() + P();
}

void S()
{
    T();
}

void T()
{
    S();
}

void W()
{
    // Not invoked

    return;
}

void Z()
{
    // Not invoked
}

int main(int argc, char** argv)
{
    F(1);
    return 0;
}