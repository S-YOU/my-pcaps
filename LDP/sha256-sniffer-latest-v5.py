#!/usr/bin/gdb -x
# This script is a sniffer for the IOU's internal sha256 implementation.
#
# Based on https://github.com/crossbowerbt/GDB-Python-Utils
#
# Tested on GDB 7.8 running on Ubuntu 14.10

import gdb
import binascii
import traceback
import struct


def usage():
    print("Usage:")
    print("\tsudo ./sha256-sniffer-latest-v5.py -p <pid>")
    gdb.execute('quit')


class SnifferBreakpoint(gdb.Breakpoint):

    # Initialize the breakpoint
    def __init__(self):
        # Can we discover the crypto functions (and Xrefs) automagically?
        # 50d1c5aaf1976e4622daf9eaa2632212  i86bi_linux-adventerprisek9-ms.154-2.T.bin
        # https://polarssl.org/sha-256-source-code
        super(SnifferBreakpoint, self).__init__('*0x0d7dea4c')  # sha256_process

    # Called when the breakpoint is hit
    def stop(self):
        registers = ["$edx"]
        for register in registers:
            try:
                length = int(gdb.parse_and_eval('$ecx'))  # IDA Demo 6.6 + GDB FTW!
                p = struct.pack(">i", length)
                length = struct.unpack("<I", p)[0]
                address = gdb.parse_and_eval(register)
                address = int(address)
                p = struct.pack(">i", address)
                u = struct.unpack("<I", p)
                address = u[0]
            except:
                traceback.print_exc()
                return True

            try:
                data = gdb.inferiors()[0].read_memory(address, length)
                print(register, binascii.hexlify(data), length)
                out.write("%s %s %s\n" % (register, binascii.hexlify(data), length))
                out.flush()
            except gdb.MemoryError:
                traceback.print_exc()
                return True
            except:
                traceback.print_exc()
                return True

        # return False to continue the execution of the program
        return False

out = open("log.txt", "a")

# GDB setup
gdb.execute("set print repeats unlimited")
gdb.execute("set print elements unlimited")
gdb.execute("set pagination off")

# generate sniffer breakpoint
SnifferBreakpoint()

# run and sniff
gdb.execute('continue')

# gdb.execute('detach')
# gdb.execute('quit')
