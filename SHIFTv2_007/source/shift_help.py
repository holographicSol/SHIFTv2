
def display_help():
    print()
    print()
    print('[ SHIFTv2 ]')
    print()
    print(' --copy      Copy           Only copy source files that are not in destination.')
    print(' --update    Update         Copy (--copy) and Update (modified timestamp comparison).')
    print(' --mirror    Mirror         Copy, Update and Delete.')
    print(' --no-bin    No Recycle     Do not send files to a recycle bin. (Used with -mirror).')
    print(' --live      Live Mode      Enables continuous backup mode (Live Mode).')
    print('                            Only if manual/task-scheduling(Windows)/chron-job(Linux) is less preferable.')
    print(' -s          Source         Specify source PATH. Files will be copied from source PATH.')
    print(' -d          Destination    Specify destination PATH. Files will be copied to (and removed from) destination PATH.')
    print('')
    print(' -cmax       CMAX           Specify async multiprocess chunk sizes in digits (Performance +-).')
    print('                            Optional. Default 100. Accepted values in range 1-100.')
    print(' -y          Assume Yes     Disables confirmation input prompts.')
    print(' -v          Verbosity      Increase Verbosity.')
    print(' -h          Help           Displays this help message.')
    print('')
    print(' (Example: shift -v -mirror --no-bin -s "D:\\Documents" -d "X:\\Documents")')
    print()
    print(' Written by Benjamin Jack Cullen.')
    print()
    print()
