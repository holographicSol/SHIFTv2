SHIFTv2 is file backup software. Asynchronous & multiprocess.

    Useful for dealing with a lot of files automatically and with zero data collection, no
    signing your life away and open readable source code. Run manually or use a task schedular.


[ SHIFTv2 ]

    --copy      Copy New       Only copy source files that are not in destination.
    --update    Update         Copy (--copy) and Update (--update) (Compares modified times and file sizes in bytes).
    --mirror    Mirror         Copy, Update and Delete.
    --no-bin    No Recycle     Do not send files to a recycle bin. (Used with -mirror).
    --live      Live Mode      Enables continuous backup mode (Live Mode).
                                Use only if more suitable than manual/task-scheduling(Windows)/chron-job(Linux) (Recommended).
    -s          Source         Specify source PATH. Files will be copied from source PATH.
                                Omit a trailing single backslash or it will escape the -s string.
    -d          Destination    Specify destination PATH. Files will be copied to (and removed from) destination PATH.
                                Omit a trailing single backslash or it will escape the -d string.

    -cmax       CMAX           Specify async multiprocess chunk sizes in digits (Performance +-).
                                Optional. Default 100. Accepted values in range 1-100.
    -y          Assume Yes     Disables confirmation input prompts.
    -v          Verbosity      Increase Verbosity.
    -vv         Verbosity+     Further Increase Verbosity.
    -h          Help           Displays this help message.

        (Standard Example: shift -v -mirror --no-bin -s "D:\Documents" -d "X:\Documents")
        (Standard Example: shift -v -mirror --no-bin -s "/home/FooBar/Documents" -d "/media/FooBar/Documents")
        (Network Example:  shift --mirror -v -s "D:\Documents" -d "\\Desktop-FooBar\Documents")

    Written by Benjamin Jack Cullen.


[ SHIFTv2 ] Copy New, Update, Mirror:

   1. scandir source, scandir destination, scandir destination directories (3x async multiprocess).
   2. stat source, destination files for modified times, sizes. (2x(+pool) async multiprocess).
   3. enumerate tasks: copy new, update existing, delete. (3x(+pool) async multiprocess).
   4. run tasks: copy new, update existing, delete. (async only).
   5. finally if mirror then delete directories not exist in source. (synchronous because we're deleting tree's).

   Lists created during steps 1-3 are checked multiple times before allowing each sublist into step 4. These
   checks include list length checks and list index type checks.


IMPORTANT:

    Never use with systems that allow single quotes and or double quotes in file/directory paths.
