import array
import ROOT, rootlogon
ROOT.gROOT.SetBatch()

ROOT.gStyle.SetPadTopMargin(0.05)
ROOT.gStyle.SetPadRightMargin(0.19)
ROOT.gStyle.SetPadBottomMargin(0.14)
ROOT.gStyle.SetPadLeftMargin(0.20)

ncontours = 200
stops = array.array("d", [0.0, 0.3, 0.6, 1.0])
red   = array.array("d", [1.0, 1.0, 1.0, 0.0])
green = array.array("d", [1.0, 1.0, 0.0, 0.0])
blue  = array.array("d", [1.0, 0.0, 0.0, 0.0])
# ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, ncontours)
# ROOT.gStyle.SetNumberContours(ncontours)

filepath = "hist/qcd/qcd.root"
histpath = "sb_2tag77/j0_mv2"

rfile = ROOT.TFile.Open(filepath)
hist = rfile.Get(histpath)

hist.GetXaxis().SetTitle("MV2c20, lead track jet")
hist.GetYaxis().SetTitle("MV2c20, subl. track jet")
hist.GetZaxis().SetTitle("Events")

hist.GetXaxis().SetRangeUser(-1.0, -0.8)
hist.GetYaxis().SetRangeUser(-1.0, -0.8)

hist.SetLabelSize(0.05, "xyz")
hist.SetTitleSize(0.05, "xyz")
hist.GetXaxis().SetNdivisions(505)
hist.GetYaxis().SetNdivisions(505)
hist.GetXaxis().SetTitleOffset(1.3)
hist.GetYaxis().SetTitleOffset(1.9)
hist.GetZaxis().SetTitleOffset(1.4)

name = "mv2lead_vs_mv2subl"
canvas = ROOT.TCanvas(name, name, 800, 800)

canvas.Draw()
hist.Draw("colzsame")

canvas.SaveAs(canvas.GetName()+".pdf")
