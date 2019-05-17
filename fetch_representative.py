#!/usr/bin/python
"""Given a LINgroup and a position, this script retrieve the representative genome of
each selected position LINgroup that has the prefix of the given LINgroup
"""

# IMPORT
from MySQLdb import Connect
import argparse
import pandas as pd
import string
import numpy as np

# FUNCTIONS
def get_parsed_args():
    parser = argparse.ArgumentParser(
        description="""
        Given a LINgroup L and a position X, where X should be in a latter position of L,
        fetch one representative genome of each A-X LINgroup that belongs to L.
        """)
    parser.add_argument("-l", dest='LINgroup', help="A parent LINgorup")
    parser.add_argument("-x", dest='position', help="A LIN position")
    args = parser.parse_args()
    return args

def connect_to_db():
    conn = Connect("127.0.0.1", "LINbase","Latham@537")
    c = conn.cursor()
    c.execute("use LINdb_NCBI_RefSeq_test")
    return conn, c

def get_LINgroup(LINgroup,c):
    c.execute("SELECT Genome_ID,LIN FROM LIN WHERE LIN LIKE '{0},%'".format(LINgroup))
    tmp = c.fetchall()
    Genome_ID = [int(i[0]) for i in tmp]
    LIN = [i[1] for i in tmp]
    df = pd.DataFrame()
    df["LIN"] = [lin.split(",") for lin in LIN]
    df.index = Genome_ID
    return df

def get_subLINgroup(df,position):
    positions = string.ascii_uppercase[:20]
    idx = positions.index(position.upper())
    sub = [",".join(i[:idx+1]) for i in df['LIN']]
    distinct_sub = list(set(sub))
    return distinct_sub

def get_rep_subLINgroup(distinct_sub,c):
    recycle = []
    df = pd.DataFrame()
    Genome_ID = []
    LIN = []
    FilePath = []
    NCBI_Tax_ID = []
    for i in distinct_sub:
        c.execute("SELECT Genome.Genome_ID,LIN.LIN,Genome.FilePath,Taxonomy.NCBI_Tax_ID FROM Genome "
                  "JOIN LIN ON Genome.Genome_ID=LIN.Genome_ID "
                  "JOIN Taxonomy ON Genome.Genome_ID=Taxonomy.Genome_ID "
                  "WHERE LIN.LIN LIKE '{0},%' AND "
                  "Taxonomy.Genome_ID IN "
                  "(SELECT Genome_ID FROM Taxonomy WHERE Rank_ID=20 AND NCBI_Tax_ID<>0) AND "
                  "Taxonomy.Rank_ID=20 "
                  "LIMIT 1".format(i))
        tmp = c.fetchone()
        try:
            [genome_id, lin,filepath,tax_id] = tmp
            Genome_ID.append(genome_id)
            LIN.append(lin)
            FilePath.append(filepath)
            NCBI_Tax_ID.append(tax_id)
        except:
            recycle.append(i)
    for i in recycle:
        c.execute("SELECT Genome.Genome_ID,LIN.LIN,Genome.FilePath,Taxonomy.NCBI_Tax_ID FROM Genome "
                  "JOIN LIN ON Genome.Genome_ID=LIN.Genome_ID "
                  "JOIN Taxonomy ON Genome.Genome_ID=Taxonomy.Genome_ID "
                  "WHERE LIN.LIN LIKE '{0},%'"
                  "LIMIT 1".format(i))
        tmp = c.fetchone()
        [genome_id, lin, filepath, tax_id] = tmp
        Genome_ID.append(genome_id)
        LIN.append(lin)
        FilePath.append(filepath)
        NCBI_Tax_ID.append(0)
    df['Genome_ID'] = Genome_ID
    df['LIN'] = LIN
    df['FilePath'] = FilePath
    df['NCBI_Tax_ID'] = NCBI_Tax_ID
    return df




# MAIN