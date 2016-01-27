"""
hist.py: a script to convert ntuples into histograms.

$ python hist.py --input=/ntuples/*.root* --output=/hists/
"""
import argparse
import array
import copy
import glob
import math
import multiprocessing
import os
import subprocess
import sys
import time

dphi = lambda phi1, phi2 : abs(math.fmod((math.fmod(phi1, 2*math.pi) - math.fmod(phi2, 2*math.pi)) + 3*math.pi, 2*math.pi) - math.pi)
dR   = lambda eta1, phi1, eta2, phi2: math.sqrt((eta1 - eta2)**2 + dphi(phi1, phi2)**2)
GeV  = 1000.0

treename = "XhhMiniNtuple"

import ROOT
ROOT.gROOT.SetBatch()

def main():

    ops = options()

    if not ops.input:                     fatal("Please give a path to --input files for processing")
    if not ops.output:                    fatal("Please give a path to a --output directory to write to.")
    if not ops.filesperjob:               fatal("Please give number of --filesperjob")
    if not ops.selection:                 fatal("Please give --selection for histogramming")
    # if not os.path.isfile(ops.selection): fatal("--selection file does not exist")

    input_files = configure_input(ops.input)

    # map
    configs = []
    for ijob, input_file_chunk in enumerate(chunkify(input_files, int(ops.filesperjob))):
        config = {}
        config["input_files"] = input_file_chunk
        config["output_file"] = os.path.join(ops.output, "hist_%04i.root" % (ijob))
        config["selection"]   = ops.selection
        configs.append(config)

    if len(configs) > 1:
        npool = min(len(configs), multiprocessing.cpu_count())
        pool = multiprocessing.Pool(npool)
        results = pool.map(hist, configs)
    else:
        hist(config)

    # reduce
    hadd(os.path.join(ops.output, "hist.root"), sorted(glob.glob(os.path.join(ops.output, "*.root*"))))

def hist(config):

    ops = options()

    input_files = config["input_files"]
    output_file = config["output_file"]
    selection   = config["selection"].split("_")

    # inputs
    tree = ROOT.TChain(treename)
    print
    for fi in input_files:
        print " + %s" % (fi)
        tree.Add(fi)
    tree.SetBranchStatus("resolvedJets_*",   0)
    tree.SetBranchStatus("hcand_resolved_*", 0)
    tree.SetBranchStatus("lepTopJets_*",     0)
    print

    # initialize
    start_time = time.time()
    hists = initialize_histograms()

    # loop
    entries = int(ops.entries) if ops.entries else tree.GetEntries()
    for ient in xrange(entries):

        tree.GetEntry(ient)
        if ient and ient % 1000 == 0:
            progress(start_time, ient, entries)

        weight = event_weight(tree)

        tags77_leadjet = count_tags(tree, jet=0, wp=77)
        tags77_subljet = count_tags(tree, jet=1, wp=77)
        if tags77_leadjet < 2 and tags77_subljet < 2:
            continue

        tags85_leadjet = count_tags(tree, jet=0, wp=85)
        tags85_subljet = count_tags(tree, jet=1, wp=85)

        tags90_leadjet = count_tags(tree, jet=0, wp=90)
        tags90_subljet = count_tags(tree, jet=1, wp=90)

        jet0 = ROOT.TLorentzVector()
        jet1 = ROOT.TLorentzVector()
        jet0.SetPtEtaPhiM(tree.hcand_boosted_pt[0], tree.hcand_boosted_eta[0], tree.hcand_boosted_phi[0], tree.hcand_boosted_m[0])
        jet1.SetPtEtaPhiM(tree.hcand_boosted_pt[1], tree.hcand_boosted_eta[1], tree.hcand_boosted_phi[1], tree.hcand_boosted_m[1])

        jet_ak2_00_eta, jet_ak2_00_phi = tree.jet_ak2track_asso_eta[0][0], tree.jet_ak2track_asso_phi[0][0]
        jet_ak2_01_eta, jet_ak2_01_phi = tree.jet_ak2track_asso_eta[0][1], tree.jet_ak2track_asso_phi[0][1]
        jet_ak2_10_eta, jet_ak2_10_phi = tree.jet_ak2track_asso_eta[1][0], tree.jet_ak2track_asso_phi[1][0]
        jet_ak2_11_eta, jet_ak2_11_phi = tree.jet_ak2track_asso_eta[1][1], tree.jet_ak2track_asso_phi[1][1]
        
        for imu in xrange(tree.nmuon):

            # NB: stored in GeV
            if tree.muon_pt[imu] < 4:         continue
            if abs(tree.muon_eta[imu]) > 2.5: continue
            if not tree.muon_isMedium[imu]:   continue

            # back to MeV
            muon_pt, muon_eta, muon_phi, muon_m = tree.muon_pt[imu]*GeV, tree.muon_eta[imu], tree.muon_phi[imu], tree.muon_m[imu]*GeV

            correct_leadjet = False
            if dR(muon_eta, muon_phi, jet_ak2_00_eta, jet_ak2_00_phi) < 0.2: correct_leadjet = True
            if dR(muon_eta, muon_phi, jet_ak2_01_eta, jet_ak2_01_phi) < 0.2: correct_leadjet = True

            correct_subljet = False
            if dR(muon_eta, muon_phi, jet_ak2_00_eta, jet_ak2_00_phi) < 0.2: correct_subljet = True
            if dR(muon_eta, muon_phi, jet_ak2_01_eta, jet_ak2_01_phi) < 0.2: correct_subljet = True

            if correct_leadjet or correct_subljet:
                muon = ROOT.TLorentzVector()
                muon.SetPtEtaPhiM(muon_pt, muon_eta, muon_phi, muon_m)
                if correct_leadjet: jet0 = jet0 + muon
                if correct_subljet: jet1 = jet1 + muon

        mass_window = evaluate_mass_window(jet0.M()/GeV, jet1.M()/GeV)

        # selection: gotta find a way to make this smarter
        accept = True

        if "sb" in selection and mass_window != "sideband": accept = False
        if "cr" in selection and mass_window != "control":  accept = False
        if "sr" in selection and mass_window != "signal":   accept = False

        if "2tag77"     in selection and tags77_leadjet+tags77_subljet != 2: accept = False
        if "2tag77lead" in selection and tags77_leadjet                != 2: accept = False
        if "2tag77subl" in selection and tags77_subljet                != 2: accept = False

        if  "3tag77"     in selection and tags77_leadjet+tags77_subljet != 3: accept = False
        if  "4tag77"     in selection and tags77_leadjet+tags77_subljet != 4: accept = False
        if  "4tag90"     in selection and tags90_leadjet+tags90_subljet != 4: accept = False
        if "N4tag90"     in selection and tags90_leadjet+tags90_subljet == 4: accept = False

        if not accept:
            continue

        # histogramming
        hists["m_jj"].Fill((jet0+jet1).M()/GeV, weight)

        hists["j0_pt"  ].Fill(jet0.Pt()/GeV,  weight)
        hists["j0_eta" ].Fill(jet0.Eta(),     weight)
        hists["j0_phi" ].Fill(jet0.Phi(),     weight)
        hists["j0_m"   ].Fill(jet0.M()/GeV,   weight)
        hists["j0_nb77"].Fill(tags77_leadjet, weight)
        hists["j0_nb90"].Fill(tags90_leadjet, weight)

        hists["j1_pt" ].Fill(jet1.Pt()/GeV,   weight)
        hists["j1_eta"].Fill(jet1.Eta(),      weight)
        hists["j1_phi"].Fill(jet1.Phi(),      weight)
        hists["j1_m"  ].Fill(jet1.M()/GeV,    weight)
        hists["j1_nb77"].Fill(tags77_subljet, weight)
        hists["j1_nb90"].Fill(tags90_subljet, weight)

        hists["j0_m_vs_j1_m"].Fill(jet0.M()/GeV, jet1.M()/GeV, weight)
        
    # write
    print
    print
    print " o %s" % (output_file)
    print

    outdir = os.path.dirname(output_file)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    outfile = ROOT.TFile.Open(output_file, "recreate")
    rootdir = outfile.mkdir(config["selection"])
    rootdir.cd()
    for hi in sorted(hists.keys()):
        hists[hi].Write()
    outfile.Close()

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--filesperjob")
    parser.add_argument("--entries")
    parser.add_argument("--selection")
    return parser.parse_args()

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

def chunkify(li, chunk_size):
    return (li[it : it+chunk_size] for it in xrange(0, len(li), chunk_size))

def progress(start_time, ievent, nevents):
    time_diff = time.time() - start_time
    rate = float(ievent+1)/time_diff
    sys.stdout.write("\r > %6i / %6i events | %2i%% | %6.2f Hz | %6.1fm elapsed | %6.1fm remaining" % (ievent, 
                                                                                                       nevents, 
                                                                                                       100*float(ievent)/float(nevents), 
                                                                                                       rate, 
                                                                                                       time_diff/60, 
                                                                                                       (nevents-ievent)/(rate*60)))
    sys.stdout.flush()

def event_weight(tree):

    if hasattr(tree, "mcEventWeight"): return tree.mcEventWeight * lumi_scaling(tree.mcChannelNumber)
    else:                              return 1.0

def lumi_scaling(channel, target_lumi=3230.0):

    if int(channel) == 410007: xsec, nevents = (695990.000/1000.0)*(4.5618E-01)*(1.1951), (6.958744E+00)

    return target_lumi * xsec / nevents

def initialize_histograms():

    hists = {}
    hists["m_jj"]   = ROOT.TH1F("m_JJ", ";m(JJ) [GeV];entries",        200, 0, 2000)

    hists["j0_pt"]   = ROOT.TH1F("j0_pt",   ";pt(lead J) [GeV];entries",   120,  200, 800)
    hists["j0_eta"]  = ROOT.TH1F("j0_eta",  ";eta(lead J);entries",        120, -3.0, 3.0)
    hists["j0_phi"]  = ROOT.TH1F("j0_phi",  ";phi(lead J);entries",        120, -3.2, 3.2)
    hists["j0_m"]    = ROOT.TH1F("j0_m",    ";m(lead J) [GeV];entries",    120,   40, 400)
    hists["j0_nb77"] = ROOT.TH1F("j0_nb77", ";Nb77(lead J) [GeV];entries",   3, -0.5, 2.5)
    hists["j0_nb90"] = ROOT.TH1F("j0_nb90", ";Nb90(lead J) [GeV];entries",   3, -0.5, 2.5)

    hists["j1_pt"]   = ROOT.TH1F("j1_pt",   ";pt(subl J) [GeV];entries",   120,  200, 800)
    hists["j1_eta"]  = ROOT.TH1F("j1_eta",  ";eta(subl J);entries",        120, -3.0, 3.0)
    hists["j1_phi"]  = ROOT.TH1F("j1_phi",  ";phi(subl J);entries",        120, -3.2, 3.2)
    hists["j1_m"]    = ROOT.TH1F("j1_m",    ";m(subl J) [GeV];entries",    120,   40, 400)
    hists["j1_nb77"] = ROOT.TH1F("j1_nb77", ";Nb77(subl J) [GeV];entries",   3, -0.5, 2.5)
    hists["j1_nb90"] = ROOT.TH1F("j1_nb90", ";Nb90(subl J) [GeV];entries",   3, -0.5, 2.5)

    hists["j0_m_vs_j1_m"] = ROOT.TH2F("j0_m_vs_j1_m", ";m(lead J) [GeV];m(subl J) [GeV];entries", 60, 40, 400, 60, 40, 400)

    for hist in hists.values():
        hist.Sumw2()
        ROOT.SetOwnership(hist, False)

    return hists

def hadd(output, inputs, delete=False):
    command = ["hadd", output] + inputs
    print
    print " ".join(command)
    print
    subprocess.call(command)
    print
    print "rm -f %s" % (" ".join(inputs))
    print

def configure_input(string):
    if "root://" in string and "*" in string:
        fatal("Sorry, wildcards not yet supported for root:// filesystems.")
    elif "*" in string:
        return sorted(glob.glob(string))
    else:
        return [string]

def mv2(wp):
    if wp == 77: return -0.6134
    if wp == 85: return -0.8433
    if wp == 90: return -0.9291

def count_tags(tree, jet, wp):
    tags = 0
    if tree.jet_ak2track_asso_MV2c20[jet][0] > mv2(wp): tags += 1
    if tree.jet_ak2track_asso_MV2c20[jet][1] > mv2(wp): tags += 1
    return tags

def evaluate_mass_window(m1, m2):
    if   Rhh(m1, m2) > 35.8: return "sideband"
    elif Xhh(m1, m2) > 1.6:  return "control"
    else:                    return "signal"

def Rhh(m1, m2):
    return math.sqrt(pow(m1-125.0, 2.0) + pow(m2-114.0, 2.0))

def Xhh(m1, m2):
    return math.sqrt(pow((m1-125.0)/(0.1*m1), 2.0) + pow((m2-114.0)/(0.1*m2), 2.0))

if __name__ == '__main__': 
    main()
