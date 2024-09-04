#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
   const char* script_dir = "C:\\Users\\Gavin\\OneDrive\\Documents\\gvim";
   const char* cmd = "python gvim.py";
   char full_cmd[512];

   // create the full command to change directory and run the script
   snprintf(full_cmd, sizeof(full_cmd), "cd /d %s && %s", script_dir, cmd);

   // execute the command
   system(full_cmd);

   return 0;
}
