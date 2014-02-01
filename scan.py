#!/usr/bin/python3

import argparse
import os
import os.path
import hashlib

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

def _find_large_files(directory, max_size=ten_mb):
    large_files = [i for i in _get_flat_file_list(directory) if os.path.getsize(i) > max_size]
    return large_files

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

def _find_duplicate_files(lengths_dict):
    hashes = [(_get_file_hash(f), f) for f in _get_flat_file_list(directory)]
    hash_multi_dict = _to_multi_dict(hashes)
    duplicate_files = [file_names for file_has, file_names in hash_multi_dict.items() if len(file_names) > 1]
    return duplicate_files

def length_dict(directory):
    lengths = {}

    for f in _get_flat_file_list(directory):
        length = os.path.getsize(f)
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
    args = parser.parse_args()
    start_path = args.start_path
    print(start_path)

    lengths_dict = length_dict(start_path)
    
    for length, files in lengths_dict.items():
        if len(files) <= 1:
            continue
        if length == 0:
            #print("Files of length 0:", files)
            continue
        print("Checking files of length", length, "bytes")
        duplicates = separate_into_duplicates(files)
        for dups in duplicates:
            print('The following files are duplicates:')
            for d in dups:
                print(' -', d)
        

