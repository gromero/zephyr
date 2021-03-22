#!/usr/bin/python3

import re
import sys
import os.path
import time

FAIL = 1
PASS = 0

argv = sys.argv
argc = len(sys.argv)

if argc != 3:
    print("Usage: %s <INPUT_FIFO_FILE> <OUTPUT_FIFO_FILE>" % (argv[0],))
    exit(1)

ff_in = argv[1]
ff_out = argv[2]

if not os.path.exists(ff_in):
    print("Error: input fifo %s not found" % ff_in)
    exit(1)

if not os.path.exists(ff_out):
    print("Error: output fifo %s not found" % ff_out)
    exit(1)

print("input FIFO:", ff_in)
print("output FIFO:", ff_out)

try:
    fd_in = open(ff_in)
except IOError:
    print("Error: could not open fifo %s to read" % ff_in)
    exit(1)

try:
    fd_out = open(ff_out, "w")
except IOError:
    print("Error: could not open fifo %s to write" % ff_out)
    exit(1)

# n = 1024*1024*1 # 1M
# pattern = re.compile("^A{%s}$" % str(n)) # 'A' sequence

pattern0 = re.compile(".*Please send word SYN to serial console.*")
pattern1 = re.compile(".*Please send characters to serial console.*")
pass_pattern = re.compile(".*PASS -.*")
fail_pattern = re.compile(".*TC_PASS is false.*")
echo_pattern = re.compile(".*SYN.*")

try:
    log = open("/tmp/outz", "w")
except:
    print("borken")

matches = 0 ## TODO: matched?
passed = 0
failed = 0
while(matches < 3):
    line = fd_in.readline()
    log.write(f"matches = {matches}")
    log.write(line)
    log.flush()
    if pattern0.match(line) or pattern1.match(line):
        matches += 1
        print("Received ask for SYN word, sending it...")
        log.write("Received ask for SYN word, sending it...")
        log.flush()
        fd_out.write("SYN\n")
        fd_out.flush()

        _ = fd_in.readline()
        line = fd_in.readline()
        log.write(line)
        log.flush()
        if pass_pattern.match(line):
            passed += 1
        else:
            failed += 1

# XXX: delete
log.write("\nFINISHED\n")
log.write(f"TESTS: {matches}\n")
log.write(f"PASS: {passed}\n")
log.write(f"FAIL: {failed}\n")
log.flush()

fd_in.close()
fd_out.close()

if matches == passed:
    exit(0)
else:
    exit(1)
