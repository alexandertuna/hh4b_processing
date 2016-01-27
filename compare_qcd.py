import copy
import os
import walk

import ROOT
ROOT.gROOT.SetBatch()

mu_qcd_3b = 0.1620
mu_qcd_4b = 0.0087

def main():

    qcd = ROOT.TFile.Open("hist/qcd/qcd.root")

    for fullpath, dirnames, objnames, _ in walk.walk(qcd):

        filepath, dirpath = fullpath.split(":/")

        if not "2tag" in fullpath:
            continue
        if dirpath != "sb_2tag77":
            continue

        for name in objnames:

            histpath = os.path.join(dirpath, name)

            nominal      = qcd.Get(histpath)
            vary_4tag90  = qcd.Get(histpath.replace("sb_2tag77", "sb_2tag77_4tag90"))
            vary_N4tag90 = qcd.Get(histpath.replace("sb_2tag77", "sb_2tag77_N4tag90"))

            if isinstance(nominal, ROOT.TH2):
                continue

            for hist in [nominal, vary_4tag90, vary_N4tag90]:
                hist.Rebin(rebin(name))
                hist.Scale(mu_qcd_4b)
                hist.Scale(nominal.Integral() / hist.Integral())
                hist.SetMinimum(0.0)
                hist.SetMaximum(ymax(name))
                hist.GetXaxis().SetTitle(xtitle(name))

            nominal.SetLineColor(ROOT.kBlack)
            vary_4tag90.SetLineColor(ROOT.kBlue)
            vary_N4tag90.SetLineColor(ROOT.kRed)

            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()

            for hist in [nominal, vary_4tag90, vary_N4tag90]:
                hist.Draw("histesame" if hist!=nominal else "histsame")

            canvas.SaveAs(os.path.join("plot", canvas.GetName()+".pdf"))

def rebin(name):
    if name in ["j0_eta", "j1_eta"]: return 4
    if name in ["j0_phi", "j1_phi"]: return 4
    if name in ["j0_pt",  "j1_pt" ]: return 4
    if name in ["j0_m",   "j1_m"  ]: return 4
    if name in ["m_JJ"]:             return 4
    return 1

def ymax(name):
    if name in ["j0_eta", "j1_eta"]: return 30
    if name in ["j0_phi", "j1_phi"]: return 15
    if name == "j0_pt": return 45
    if name == "j1_pt": return 40
    if name == "j0_m":  return 50
    if name == "j1_m":  return 50
    if name == "m_JJ":  return 35
    if "_nb" in name: return 300
    return 1

def xtitle(name):
    if name == "m_JJ"    : return "#it{m}(JJ) [GeV]"
    if name == "j0_pt"   : return "#it{p}_{T}(lead j) [GeV]"
    if name == "j0_eta"  : return "#it{#eta}(lead J)"
    if name == "j0_phi"  : return "#it{#phi}(lead J)"
    if name == "j0_m"    : return "#it{m}(lead J) [GeV]"
    if name == "j0_nb77" : return "N(b-tags 77%, lead jet)"
    if name == "j0_nb90" : return "N(b-tags 90%, lead jet)"
    if name == "j1_pt"   : return "#it{p}_{T}(sub-lead j) [GeV]"
    if name == "j1_eta"  : return "#it{#eta}(sub-lead J)"
    if name == "j1_phi"  : return "#it{#phi}(sub-lead J)"
    if name == "j1_m"    : return "#it{m}(sub-lead J) [GeV]"
    if name == "j1_nb77" : return "N(b-tags 77%, lead jet)"
    if name == "j1_nb90" : return "N(b-tags 90%, lead jet)"

if __name__ == "__main__":
    main()
