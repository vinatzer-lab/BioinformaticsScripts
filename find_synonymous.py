#!/usr/bin/env python
"""After you've got the VCF file from VarScan, this script will help get rid of synonymous changes and only
retain those non-synonymous changes.

WARNING: Make sure you have the VCF file, not the text file. If you are using VarScan, remember to add '--output-vcf 1'
in your command line.
"""

# IMPORT
from Bio import SeqIO
import argparse
import sys
import pandas as pd

# FUNCTIONS
def get_parsed_args():
    parser = argparse.ArgumentParser(
        description="Filter synonymous variants out."
    )
    parser.add_argument("-i", dest="vcf", help="The VCF file from VarScan.")
    parser.add_argument("-m", dest="cds", help="The annotated coding sequences from RAST server")
    parser.add_argument("-o", dest="output", help="The output file name. Default: filtered_{VCF file name}.txt")
    parser.add_argument("-t", dest="df", help="Optional, a spreadsheet containing gene IDs and functions, save as CSV format.")
    args = parser.parse_args()
    return args



# MAIN
if __name__ == '__main__':
    args = get_parsed_args()
    if args.vcf and args.cds:
        vcf = args.vcf
        cds = args.cds
        if args.output is None:
            output = "filtered_"+vcf+".txt"
        else:
            output = args.output
        if args.df:
            df = pd.read_table(args.df,sep=",",header=0,index_col=1)
        records = SeqIO.index(cds,"fasta")
        f = open(vcf,"r")
        lines = [i.strip().split("\t") for i in f.readlines()]
        f.close()
        if lines[0][0].startswith("#"):
            # This is a vcf file
            vcf_content = []
            n = 0
            while lines[i][0] != '#CHROM':
                n += 1
            vcf_content = lines[n+1:]
            gene_ids = [i[0] for i in vcf_content]
            positions = [int(i[1])-1 for i in vcf_content]
            refs = [i[3] for i in vcf_content]
            alts = [i[4] for i in vcf_content]
            def check_aa_change(idx):
                seq = records[gene_ids[idx]]
                pos = positions[idx]
                ref_len = len(refs[idx])
                alt_len = len(alts[idx])
                mutated = seq.seq[:pos] + alts[idx] + seq.seq[pos+ref_len:]
                return seq.seq, mutated
            f = open(output,"w")
            if df is not None:
                f.write("Gene\tFunction\tPosition\tRef\tAlt\tOriginal_seq\tMutated_seq\n")
            else:
                f.write("Gene\tPosition\tRef\tAlt\tOriginal_seq\tMutated_seq\n")
            for i in range(len(gene_ids)):
                orig, mutated = check_aa_change(i)
                if orig.translate() != mutated.translate():
                    if df is not None:
                        f.write("\t".join([gene_ids[i], str(df.get_value(gene_ids[i],"function")),str(positions[i] + 1), refs[i], alts[i], str(orig), str(mutated)]))
                    else:
                        f.write("\t".join([gene_ids[i],str(positions[i]+1), refs[i], alts[i], str(orig), str(mutated)]))
                    f.write("\n")
            f.close()
        else:
            print("Please use the VCF format output from VarScan!")
            sys.exit(0)
    else:
        sys.exit(0)