#!/usr/bin/python
"""
"""

# IMPORT
from Bio import Entrez
from Bio import SeqIO
from os.path import join
import argparse
import os
import urllib.request


# VARIABLES
Entrez.email = 'aaa@bbb.ccc'
wgs_base_url = 'ftp://ftp.ncbi.nlm.nih.gov/sra/wgs_aux/'

# FUNCTIONS
def get_parsed_args():
    parser = argparse.ArgumentParser(
        description="Download sequence by accession numbers or so, input is always a file with accession numbers, each per line.")
    parser.add_argument("-i", dest='file', help="File with accession numbers, one per line.")
    parser.add_argument("-o", dest='out_dir', help="Target file folder.")
    args = parser.parse_args()
    return args

def download_from_accession_file(accession_file,out_dir):
    with open(accession_file, "r") as f:
        names = [i.strip().split('\t')[0] for i in f.readlines()]
        accession_numbers = [i.strip().split('\t')[1] for i in f.readlines()]
    for i in range(len(accession_numbers)):
        accession = accession_numbers[i]
        name = names[i]
        first_two = accession[:2]
        second_two = accession[2:4]
        project = first_two+second_two+"01"
        url = "/".join([wgs_base_url, first_two, second_two, project, project+".1.fsa_nt.gz"])
        urllib.request.urlretrieve(url, join(out_dir, name+".fasta.gz"))

def main():
    args = get_parsed_args()
    accession_file = args.file
    out_dir = args.out_dir
    download_from_accession_file(accession_file,out_dir)

# MAIN
if __name__ == '__main__':
    main()