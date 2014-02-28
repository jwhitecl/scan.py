#!/usr/bin/python3

import argparse
import os
import os.path
import hashlib
import collections
import fnmatch

one_mb = 2 ** 20
ten_mb = 10 * one_mb

def _get_flat_file_list(directory):
    dirs = [i for i in os.listdir(directory) if i not in ('.', '..')]
    for f in dirs:
        full_path = os.path.join(directory, f)
        if os.path.islink(full_path):
            pass # do nothing with symlinks
        elif os.path.isdir(full_path):
            for i in _get_flat_file_list(full_path):
                yield i
        else:
            yield full_path

def _get_file_hash(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(one_mb), b''):
            md5.update(chunk)
    return md5.digest()

def _to_multi_dict(items):
    retval = {}
    for a, b in items:
        try:
            retval[a].append(b)
        except KeyError:
            retval[a] = [b]
    return retval

def length_dict(directory, skip_threshold, exclude_globs):
    lengths = {}

    for f in _get_flat_file_list(directory):
        if any(fnmatch.fnmatch(f, glob) for glob in exclude_globs):
            continue

        length = os.path.getsize(f)

        if length <= skip_threshold:
            continue

        if length in lengths:
            lengths[length].append(f)
        else:
            lengths[length] = [f]

    return lengths

def separate_into_duplicates(files):
    hash_dict = {}
    for f in files:
        try:
            hash = _get_file_hash(f)
            if hash in hash_dict:
                hash_dict[hash].append(f)
            else:
                hash_dict[hash] = [f]
        except:
            print("Error accessing", f)
    return [files for hash, files in hash_dict.items() if len(files) > 1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-path', help='path to start recursive scan', default=os.getcwd())
    parser.add_argument('--skip-threshold', 
                        help='do not scan files smaller than a this size in bytes', 
                        default=1, 
                        action='store', 
                        type=int)
    parser.add_argument('--exclude',
                        help='exclude files from the scan. (globbing allowed)',
                        action='append',
                        default=[],
                        type=str)

    args = parser.parse_args()
    start_path = args.start_path
    skip_threshold = args.skip_threshold
    print("Scanning %s" % start_path)
    
    if skip_threshold > 0:
        print('Skipping files smaller than %d bytes' % skip_threshold)

    lengths_dict = length_dict(start_path, skip_threshold, args.exclude)
    lengths = sorted(lengths_dict.keys())
    
    for length in lengths:
        files = lengths_dict[length]
        if len(files) <= 1:
            continue
        print("Checking files of length", length, "bytes")
        duplicates = separate_into_duplicates(files)
        for dups in duplicates:
            print('The following files are duplicates:')
            for d in dups:
                print(' -', d)
    print('done')
        

