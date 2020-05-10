import java.io.*;

class CommandExecution
{
    public static void execute(String command)
    {
        try
        {
            Process p = Runtime.getRuntime().exec(command);
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }
    }

    public static void main(String args[])
    {
        CommandExecution.execute(args[1]);
    }
}