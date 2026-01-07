#!/usr/bin/env python

from __future__ import print_function

import sys
from rst2ansi import rst2ansi
import argparse
import io

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Prints a reStructuredText input in an ansi-decorated format suitable for console output.')
    parser.add_argument('file', type=str, nargs='?', help='A path to the file to open')

    args = parser.parse_args(argv)

    def process_file(f):
      out = rst2ansi(f.read())
      if out:
        try:
          print(out)
        except UnicodeEncodeError:
          print(out.encode('ascii', errors='backslashreplace').decode('ascii'))

    if args.file:
      with io.open(args.file, 'rb') as f:
        process_file(f)
    else:
      process_file(sys.stdin)

if __name__ == '__main__':
    main()
