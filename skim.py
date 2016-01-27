"""
skim.py: a script to convert ntuples into a preselected ntuple

$ python skim.py --input=/ntuples/*.root* --output=/skims/file.root
"""
import argparse
import array
import copy
import glob
import os
import sys
import ROOT

treename  = "XhhMiniNtuple"

ROOT.gROOT.SetBatch()

def main():

    ops = options()

    if not ops.input:
        fatal("Please give a path to --input files for processing")
    if not ops.output:
        fatal("Please give a path to a --output directory to write to.")
    if not ops.filesperjob:
        fatal("Please give number of --filesperjob")

    input_files = configure_input(ops.input)

    for ijob, input_file_chunk in enumerate(chunkify(input_files, int(ops.filesperjob))):

        output_file = os.path.join(ops.output, "skim_%04i.root" % (ijob))
        skim(input_file_chunk, output_file)

def skim(input_files, output_file):

    # select >=2 fat jet sample
    selection = ["hcand_boosted_n >= 2",
                 "hcand_boosted_pt[0] > 350*1000",
                 "hcand_boosted_pt[1] > 250*1000",
                 "abs(hcand_boosted_eta[0]) < 2",
                 "abs(hcand_boosted_eta[1]) < 2",
                 "hcand_boosted_m[0] > 50*1000",
                 "hcand_boosted_m[1] > 50*1000",
                 "jet_ak2track_asso_n[0] >= 2",
                 "jet_ak2track_asso_n[1] >= 2",
                 "jet_ak2track_asso_pt[0][0] > 10*1000",
                 "jet_ak2track_asso_pt[0][1] > 10*1000",
                 "jet_ak2track_asso_pt[1][0] > 10*1000",
                 "jet_ak2track_asso_pt[1][1] > 10*1000",
                 "abs(jet_ak2track_asso_eta[0][0]) < 2.5",
                 "abs(jet_ak2track_asso_eta[0][1]) < 2.5",
                 "abs(jet_ak2track_asso_eta[1][0]) < 2.5",
                 "abs(jet_ak2track_asso_eta[1][1]) < 2.5",
                 "abs(hcand_boosted_eta[0] - hcand_boosted_eta[1]) < 1.7",
                 ]
    selection = " && ".join(["(%s)" % sel for sel in selection])

    # inputs
    tree = ROOT.TChain(treename)
    print
    for fi in input_files:
        print " + %s" % (fi)
        tree.Add(fi)

    # skim
    if tree.GetEntries() > 0:
        skim = tree.CopyTree(selection)
    else:
        skim = tree

    # write
    print " o %s" % (output_file)
    print

    outdir = os.path.dirname(output_file)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    outfile = ROOT.TFile.Open(output_file, "recreate")
    outfile.cd()
    skim.Write()

    # summarize
    template = "%15s | %12s"
    print
    print " skim summary"
    print "-"*45
    print template % ("", "entries")
    print "-"*45
    print template % (" input", tree.GetEntries())
    print template % ("output", skim.GetEntries())
    print
    print
    print " output filesize"
    print "-"*45
    print " %.4f MB" % (outfile.GetSize()/pow(1024.0, 2))
    print

    outfile.Close()

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--filesperjob")
    return parser.parse_args()

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

def chunkify(li, chunk_size):
    return (li[it : it+chunk_size] for it in xrange(0, len(li), chunk_size))

def configure_input(string):
    if "root://" in string and "*" in string:
        fatal("Sorry, wildcards not yet supported for root:// filesystems.")
    elif "*" in string:
        return sorted(glob.glob(string))
    else:
        return [string]

if __name__ == '__main__': 
    main()
