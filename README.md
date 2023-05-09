[ SHIFTv2 ]

     -copy      Copy           Only copy source files that are not in destination.
     -update    Update         Copy (-copy) and update (modified timestamp comparison).
     -mirror    Mirror         Copy, update and delete.
     --no-bin   No Recycle     Do not send files to a recycle bin. (Used with -mirror).
     -s         Source         Specify source PATH. Files will be copied from source PATH.
     -d         Destination    Specify destination PATH. Files will be copied to (and removed from) destination PATH.
    
     -v         Verbosity      Increase Verbosity.
     -h         Help           Displays this help message.

     Written by Benjamin Jack Cullen.


SHIFTv2: Copy, Update, Mirror. (File backup software).

   1. scandir source, scandir destination, scandir destination directories (3x async multiprocess).
   2. stat source, destination files for modified times, sizes. (2x async multiprocess).
   3. enumerate tasks: copy new, update existing, delete. (3x async multiprocess).
   4. run tasks: copy new, update existing, delete. (async only).
   5. finally if mirror then delete directories not exist in source. (synchronous because we're deleting tree's).
