# follow.py
#
# A generator that follows a log file like Unix 'tail -f'.
#
# Note: To see this example work, you need to apply to
# an active server log file.  Run the program "logsim.py"
# in the background to simulate such a file.  This program
# will write entries to a file "access-log".

import time


def follow(the_file):
    the_file.seek(0, 2)      # Go to the end of the file
    while True:
        line = the_file.readline()
        if not line:
            time.sleep(0.1)    # Sleep briefly
            continue
        yield line


# Example use
if __name__ == '__main__':
    with open("access-log.log") as logfile:
        for line in follow(logfile):
            print(line)
