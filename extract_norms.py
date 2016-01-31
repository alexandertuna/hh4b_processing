"""
python extract_norms.py

shoutout to https://github.com/makagan/Xhh4bUtils/
"""
import argparse
import copy
import math
import ROOT

def options():
    parser = argparse.ArgumentParser()
    for process in ["data", "qcd", "ttbar", "zjets"]:
        parser.add_argument("--%s" % process)
    return parser.parse_args()
ops = options()

filepath_data,  histpath_data  = ops.data.split(":")
filepath_qcd,   histpath_qcd   = ops.qcd.split(":")
filepath_ttbar, histpath_ttbar = ops.ttbar.split(":")

file_data  = ROOT.TFile.Open(filepath_data)
file_qcd   = ROOT.TFile.Open(filepath_qcd)
file_ttbar = ROOT.TFile.Open(filepath_ttbar)

data  = file_data.Get( histpath_data)
qcd   = file_qcd.Get(  histpath_qcd)
ttbar = file_ttbar.Get(histpath_ttbar)

# :(
zjets = copy.copy(ttbar)
zjets.Reset()

def main():

    parameters = ["muqcd", "mutop"]
    minuit = ROOT.TMinuit(len(parameters))
    minuit.SetPrintLevel(-1)
    minuit.SetErrorDef(0.5)
    minuit.SetFCN(negative_log_likelihood)

    clear(minuit)
    if minuit.Migrad():         print " ERROR: migrad status non-zero"
    if minuit.Command("MINOS"): print " ERROR:  minos status non-zero"

    muqcd_value, muqcd_error = ROOT.Double(0), ROOT.Double(0)
    mutop_value, mutop_error = ROOT.Double(0), ROOT.Double(0)

    minuit.GetParameter(0, muqcd_value, muqcd_error)
    minuit.GetParameter(1, mutop_value, mutop_error)

    print " muqcd: value, error = %9.6f %9.6f" % (muqcd_value, muqcd_error)
    print " mutop: value, error = %9.6f %9.6f" % (mutop_value, mutop_error)

def clear(minuit):
    minuit.Command("CLEAR")
    minuit.DefineParameter(0, "muqcd",  0.01, 0.01, 0.00001, 1)
    minuit.DefineParameter(1, "mutop",   1.3, 0.01, 0.00001, 5)
    
def negative_log_likelihood(npar, gin, f, parameters, iflag):
    """ https://root.cern.ch/phpBB3/viewtopic.php?t=13339 """

    neglogL = 0.0

    for ibin in xrange(0, data.GetNbinsX()+1):
        expected = parameters[0]*qcd.GetBinContent(ibin) + parameters[1]*ttbar.GetBinContent(ibin) + zjets.GetBinContent(ibin)
        if expected > 0:
            neglogL += expected - data.GetBinContent(ibin)*math.log(expected)

    f[0] = neglogL


if __name__ == "__main__":
    main()

