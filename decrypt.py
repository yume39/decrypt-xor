#!/usr/bin/env python3

import sys
import random
import hashlib
import argparse
from collections import Counter
from os import path


def main(args):
    if args.seed is not None:
        random.seed(args.seed)

    FILE_SIZE = path.getsize(args.infile)
    NUM_WHOLE_BLOCKS = FILE_SIZE // args.key_length

    block_counter = Counter()
    current_best = 0
    with open(args.infile, 'rb') as fin:
        print('looking for repeated blocks...')
        while True:
            offset = random.randint(0, NUM_WHOLE_BLOCKS - 1) * args.key_length
            fin.seek(offset)
            block = fin.read(args.key_length)
            assert len(block) == args.key_length
            digest = hashlib.sha256(block).digest()
            block_counter[digest] += 1
            count = block_counter[digest]
            if count > current_best:
                current_best = count
                print('found {}/{}'.format(current_best, args.min_duplicate))
            if current_best >= args.min_duplicate:
                key = block
                break
        fin.seek(0)

        with open(args.outfile, 'wb') as fout:
            short_read = False
            print('decrypting file')
            while True:
                block = fin.read(args.key_length)
                if not block:
                    break
                if len(block) < args.key_length:
                    assert not short_read
                    short_read = True
                buf = []
                for i, c in enumerate(block):
                    buf.append(c ^ key[i])
                fout.write(bytes(buf))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("outfile")
    parser.add_argument("--key_length", type=int, default=524288)
    parser.add_argument("--min_duplicate", type=int, default=5)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    main(args)
