from os import mkdir
try:
    from brain.binary.filesystem import start_filesystem, BrainStoreConfig
    from brain import connect, r
except ImportError:
    from .brain.binary.filesystem import start_filesystem, BrainStoreConfig
    from .brain import connect, r

# docker run -ti --rm --cap-add SYS_ADMIN --device /dev/fuse --security-opt apparmor:unconfined danfusetest
if __name__ == "__main__":
    try:
        mkdir("/tmp/tst")
    except FileExistsError:
        pass
    c = connect()
    try:
        r.db("Brain").table_create("Files").run(c)
    except:
        pass
    bsc = BrainStoreConfig(allow_remove=True, allow_list=True)
    start_filesystem("/tmp/tst", bsc)
