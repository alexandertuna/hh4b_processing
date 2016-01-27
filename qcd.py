import copy
import os
import walk

import ROOT

def main():

    data_file  = ROOT.TFile.Open("hist/data15_13TeV/hadd.root")
    ttbar_file = ROOT.TFile.Open("hist/mc15_13TeV.410007.ttbar_allhad/hadd.root")
    
    if not os.path.isdir("hist/qcd"):
        os.makedirs("hist/qcd")
    outfile = ROOT.TFile.Open("hist/qcd/qcd.root", "recreate")

    for fullpath, dirnames, objnames, _ in walk.walk(data_file):

        if not "2tag" in fullpath:
            continue

        filepath, dirpath = fullpath.split(":/")
        rootdir = outfile.mkdir(dirpath)

        for name in objnames:

            histpath = os.path.join(dirpath, name)

            data_hist  = data_file.Get(histpath)
            ttbar_hist = ttbar_file.Get(histpath)

            qcd_hist = copy.copy(data_hist)
            ROOT.SetOwnership(qcd_hist, False)
            if ttbar_hist:
                qcd_hist.Add(ttbar_hist, -1.0)

            rootdir.cd()
            qcd_hist.Write()

if __name__ == "__main__":
    main()
