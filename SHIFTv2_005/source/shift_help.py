
def display_help():
    print()
    print()
    print('[ SHIFTv2 ]')
    print()
    print(' -copy      Copy           Only copy source files that are not in destination.')
    print(' -update    Update         Copy (-copy) and update (modified timestamp comparison).')
    print(' -mirror    Mirror         Copy, update and delete.')
    print(' --no-bin   No Recycle     Do not send files to a recycle bin. (Used with -mirror).')
    print(' -s         Source         Specify source PATH. Files will be copied from source PATH.')
    print(' -d         Destination    Specify destination PATH. Files will be copied to (and removed from) destination PATH.')
    print('')
    print(' -y         Assume Yes     Disables confirmation input prompts.')
    print(' -v         Verbosity      Increase Verbosity.')
    print(' -h         Help           Displays this help message.')
    print('')
    print(' (Example: shift -v -mirror --no-bin -s "D:\\Documents" -d "X:\\Documents")')
    print()
    print(' Written by Benjamin Jack Cullen.')
    print()
    print()
