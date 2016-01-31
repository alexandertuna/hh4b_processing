import copy
import os
import walk

import ROOT, rootlogon
ROOT.gROOT.SetBatch()

import helpers

mu_qcd_4b_nomin = 0.009251
mu_qcd_4b_tight = 0.074007
mu_qcd_4b_loose = 0.010562

mu_top_4b_nomin = 0.952299
mu_top_4b_tight = 1.078631
mu_top_4b_loose = 0.940893

def main():

    qcd = ROOT.TFile.Open("hist/qcd/qcd.root")

    for fullpath, dirnames, objnames, _ in walk.walk(qcd):

        filepath, dirpath = fullpath.split(":/")

        if not "2tag" in fullpath:
            continue
        if dirpath not in ["sb_2tag77", "cr_2tag77", "sr_2tag77"]:
            continue

        for name in objnames:

            histpath = os.path.join(dirpath, name)

            qcd_nomin = qcd.Get(histpath)
            qcd_tight = qcd.Get(histpath.replace("_2tag77", "_2tag77_4tag97"))
            qcd_loose = qcd.Get(histpath.replace("_2tag77", "_2tag77_N4tag97"))

            if isinstance(qcd_nomin, ROOT.TH2):
                continue

            qcd_nomin.Scale(mu_qcd_4b_nomin)
            qcd_tight.Scale(mu_qcd_4b_tight)
            qcd_loose.Scale(mu_qcd_4b_loose)

            if "m_JJ" in histpath:
                bins = qcd_nomin.GetNbinsX()+1
                error = ROOT.Double(0)
                print
                print " nomin: %9.3f (%.3f)" % (qcd_nomin.IntegralAndError(0, bins, error), error)
                print " tight: %9.3f (%.3f)" % (qcd_tight.IntegralAndError(0, bins, error), error)
                print " loose: %9.3f (%.3f)" % (qcd_loose.IntegralAndError(0, bins, error), error)
                print

            for hist in [qcd_nomin, qcd_tight, qcd_loose]:
                hist.Rebin(rebin(name))
                helpers.show_overflow(hist)
                hist.SetMinimum(0.0)
                hist.SetMaximum(ymax(histpath))
                hist.GetXaxis().SetTitle(xtitle(name))
                hist.GetYaxis().SetTitle("Events")
                hist.SetLineWidth(3)
                hist.SetLabelSize(0.05, "xyz")
                hist.SetTitleSize(0.05, "xyz")
                hist.GetXaxis().SetNdivisions(505)

            for bin in xrange(0, qcd_nomin.GetNbinsX()+1):
                qcd_nomin.SetBinError(bin, 0.00001)

            qcd_nomin.SetLineColor(ROOT.kBlack)
            qcd_tight.SetLineColor(ROOT.kBlue)
            qcd_loose.SetLineColor(ROOT.kRed)

            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()

            for hist in [qcd_nomin, qcd_tight, qcd_loose]:
                hist.Draw("histesame" if hist!=qcd_nomin else "histsame")

            if True:

                ratio = helpers.ratio(name   = canvas.GetName()+"_ratio",
                                      numers = [qcd_tight, qcd_loose],
                                      denom  = qcd_nomin,
                                      min    = 0.1,
                                      max    = 1.9,
                                      ytitle = "varied / nom."
                                      )
                share = helpers.same_xaxis(name          = canvas.GetName()+"_share",
                                           top_canvas    = canvas,
                                           bottom_canvas = ratio,
                                           )
                canvas.SetName(canvas.GetName()+"_noratio")
                share.SetName(share.GetName().replace("_share", ""))
                canvas = share

            ks = qcd_tight.KolmogorovTest(qcd_loose)

            xatlas, yatlas = 0.19, 0.96
            xleg, yleg     = 0.68, 0.84
            atlas         = ROOT.TLatex(xatlas,     yatlas,    "ATLAS Internal")
            kolmo         = ROOT.TLatex(xatlas+0.4, yatlas,    "KS(tight, loose): %.3f" % ks)
            legend_nomin  = ROOT.TLatex(xleg,       yleg,      "nominal")
            legend_tight  = ROOT.TLatex(xleg,       yleg-0.05, "tight 2-tag")
            legend_loose  = ROOT.TLatex(xleg,       yleg-0.10, "loose 2-tag")
            legend_nomin.SetTextColor(ROOT.kBlack)
            legend_tight.SetTextColor(ROOT.kBlue)
            legend_loose.SetTextColor(ROOT.kRed)
            for logo in [atlas, kolmo, legend_nomin, legend_tight, legend_loose]:
                logo.SetTextSize(0.035 if logo in [atlas, kolmo] else 0.04)
                logo.SetTextFont(42)
                logo.SetNDC()
                logo.Draw()

            outdir = os.path.join("plot", dirpath)
            if not os.path.isdir(outdir):
                os.makedirs(outdir)
            canvas.SaveAs(os.path.join(outdir, canvas.GetName()+".pdf"))

            canvas.Close()

def rebin(name):
    if name in ["j0_eta", "j1_eta"]: return 8
    if name in ["j0_phi", "j1_phi"]: return 8
    if name in ["j0_pt",  "j1_pt" ]: return 8
    if name in ["j0_m",   "j1_m"  ]: return 8
    if name in ["m_JJ", "dr_JJ"]:    return 8
    return 1

def ymax(histpath):
    if "j0_eta" in histpath and "sb" in histpath: return 50
    if "j0_phi" in histpath and "sb" in histpath: return 30
    if "j1_eta" in histpath and "sb" in histpath: return 50
    if "j1_phi" in histpath and "sb" in histpath: return 30
    if "j0_pt"  in histpath and "sb" in histpath: return 80
    if "j1_pt"  in histpath and "sb" in histpath: return 70
    if "j0_m"   in histpath and "sb" in histpath: return 80
    if "j1_m"   in histpath and "sb" in histpath: return 80
    if "m_JJ"   in histpath and "sb" in histpath: return 50
    if "dr_JJ"  in histpath and "sb" in histpath: return 50
    if "_nb"    in histpath and "sb" in histpath: return 200

    if "j0_eta" in histpath and "cr" in histpath: return  8
    if "j0_phi" in histpath and "cr" in histpath: return  6
    if "j1_eta" in histpath and "cr" in histpath: return  8
    if "j1_phi" in histpath and "cr" in histpath: return  6
    if "j0_pt"  in histpath and "cr" in histpath: return 15
    if "j1_pt"  in histpath and "cr" in histpath: return 15
    if "j0_m"   in histpath and "cr" in histpath: return 20
    if "j1_m"   in histpath and "cr" in histpath: return 20
    if "m_JJ"   in histpath and "cr" in histpath: return 10
    if "dr_JJ"  in histpath and "cr" in histpath: return 10
    if "_nb"    in histpath and "cr" in histpath: return 200

    if "j0_eta" in histpath and "sr" in histpath: return 3
    if "j0_phi" in histpath and "sr" in histpath: return 2
    if "j1_eta" in histpath and "sr" in histpath: return 3
    if "j1_phi" in histpath and "sr" in histpath: return 2
    if "j0_pt"  in histpath and "sr" in histpath: return 5
    if "j1_pt"  in histpath and "sr" in histpath: return 4
    if "j0_m"   in histpath and "sr" in histpath: return 12
    if "j1_m"   in histpath and "sr" in histpath: return 8
    if "m_JJ"   in histpath and "sr" in histpath: return 5
    if "dr_JJ"  in histpath and "sr" in histpath: return 5
    if "_nb"    in histpath and "sr" in histpath: return 10

    if "sr" in histpath: return 5

    return 1

def xtitle(name):
    if name == "m_JJ"    : return "#it{m}(JJ) [GeV]"
    if name == "dr_JJ"   : return "#Delta#it{R}(JJ)"
    if name == "j0_pt"   : return "#it{p}_{T}(lead J) [GeV]"
    if name == "j0_eta"  : return "#it{#eta}(lead J)"
    if name == "j0_phi"  : return "#it{#phi}(lead J)"
    if name == "j0_m"    : return "#it{m}(lead J) [GeV]"
    if name == "j0_nb77" : return "N(b-tags 77%, lead J)"
    if name == "j0_nb90" : return "N(b-tags 90%, lead J)"
    if name == "j1_pt"   : return "#it{p}_{T}(subl. J) [GeV]"
    if name == "j1_eta"  : return "#it{#eta}(subl. J)"
    if name == "j1_phi"  : return "#it{#phi}(subl. J)"
    if name == "j1_m"    : return "#it{m}(subl. J) [GeV]"
    if name == "j1_nb77" : return "N(b-tags 77%, lead J)"
    if name == "j1_nb90" : return "N(b-tags 90%, lead J)"
    return "fuck"

if __name__ == "__main__":
    main()
