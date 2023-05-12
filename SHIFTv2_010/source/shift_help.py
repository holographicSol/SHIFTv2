import cprint

c_arg = 'BL'
c_tag = 'W'
c_des = 'BL'
c_exa = 'BL'


def display_help():
    print('')
    print('')
    print(f'{cprint.color(s="[ SHIFTv2 ]", c=c_tag)}')
    print('')
    print(f'{cprint.color(s=" --copy", c=c_arg)}      {cprint.color(s="Copy New", c=c_tag)}       {cprint.color(s="Only copy source files that are not in destination.", c=c_des)}')
    print(f'{cprint.color(s=" --update", c=c_arg)}    {cprint.color(s="Update", c=c_tag)}         {cprint.color(s="Copy (--copy) and Update (--update) (Compares modified times and file sizes in bytes).", c=c_des)}')
    print(f'{cprint.color(s=" --mirror", c=c_arg)}    {cprint.color(s="Mirror", c=c_tag)}         {cprint.color(s="Copy, Update and Delete.", c=c_des)}')
    print('')
    print(f'{cprint.color(s=" -s", c=c_arg)}          {cprint.color(s="Source", c=c_tag)}         {cprint.color(s="Specify source PATH. Files will be copied from source PATH.", c=c_des)}')
    print(f'{cprint.color(s="                            Omit a trailing single backslash or it will escape the -s string.", c=c_des)}')
    print(f'{cprint.color(s=" -d", c=c_arg)}          {cprint.color(s="Destination", c=c_tag)}    {cprint.color(s="Specify destination PATH. Files will be copied to (and removed from) destination PATH.", c=c_des)}')
    print(f'{cprint.color(s="                            Omit a trailing single backslash or it will escape the -d string.", c=c_des)}')
    print(f'{cprint.color(s=" --live", c=c_arg)}      {cprint.color(s="Live Mode", c=c_tag)}      {cprint.color(s="Enables continuous backup mode (Live Mode).", c=c_des)}')
    print(f'{cprint.color(s="                            Recommended to run manually/task-scheduling(Windows)/chron-job(Linux) however Live Mode is an option.", c=c_des)}')
    print(f'{cprint.color(s=" --no-bin", c=c_arg)}    {cprint.color(s="No Recycle", c=c_tag)}     {cprint.color(s="Do not send files to a recycle bin. (Used with -mirror).", c=c_des)}')
    print(f'{cprint.color(s=" -cmax", c=c_arg)}       {cprint.color(s="CMAX", c=c_tag)}           {cprint.color(s="Specify async multiprocess chunk sizes in digits (Performance +-).", c=c_des)}')
    print(f'{cprint.color(s="                            Optional. Default 100. Accepted values in range 1-100.", c=c_des)}')
    print('')
    print(f'{cprint.color(s=" -y", c=c_arg)}          {cprint.color(s="Assume Yes", c=c_tag)}     {cprint.color(s="Disables confirmation input prompts.", c=c_des)}')
    print(f'{cprint.color(s=" -v", c=c_arg)}          {cprint.color(s="Verbosity", c=c_tag)}      {cprint.color(s="Increase Verbosity.", c=c_des)}')
    print(f'{cprint.color(s=" -vv", c=c_arg)}         {cprint.color(s="Verbosity+", c=c_tag)}     {cprint.color(s="Further Increase Verbosity.", c=c_des)}')
    print(f'{cprint.color(s=" -h", c=c_arg)}          {cprint.color(s="Help", c=c_tag)}           {cprint.color(s="Displays this help message.", c=c_des)}')
    print('')
    print(cprint.color(s=' Standard Example:    shift -vv -mirror --no-bin -s "D:\\Documents" -d "X:\\Document"', c=c_exa))
    print(cprint.color(s=' Standard Example:    shift -vv -mirror --no-bin -s "/home/FooBar/Documents" -d "/media/FooBar/Documents"', c=c_exa))
    print(cprint.color(s=' Network Example:     shift --mirror -vv -s "D:\Documents" -d "\\\Desktop-FooBar\Documents"', c=c_exa))
    print(cprint.color(s=' Network Example:     shift --mirror -vv -s "\\\Desktop-Foo\Documents" -d "\\\Desktop-Bar\Documents"', c=c_exa))
    print('')
    print(cprint.color(s=' Written by Benjamin Jack Cullen.', c=c_arg))
    print('')
    print('')
