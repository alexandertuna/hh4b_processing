import copy
import math
import ROOT
ROOT.gROOT.SetBatch(True)

def show_overflow(hist):
    """ Show overflow and underflow on a TH1. h/t Josh """

    nbins          = hist.GetNbinsX()
    underflow      = hist.GetBinContent(   0   )
    underflowerror = hist.GetBinError  (   0   )
    overflow       = hist.GetBinContent(nbins+1)
    overflowerror  = hist.GetBinError  (nbins+1)
    firstbin       = hist.GetBinContent(   1   )
    firstbinerror  = hist.GetBinError  (   1   )
    lastbin        = hist.GetBinContent( nbins )
    lastbinerror   = hist.GetBinError  ( nbins )

    if underflow != 0 :
        newcontent = underflow + firstbin
        if firstbin == 0 :
            newerror = underflowerror
        else:
            newerror = math.sqrt( underflowerror * underflowerror + firstbinerror * firstbinerror )
        hist.SetBinContent(1, newcontent)
        hist.SetBinError  (1, newerror)

    if overflow != 0 :
        newcontent = overflow + lastbin
        if lastbin == 0 :
            newerror = overflowerror
        else:
            newerror = math.sqrt( overflowerror * overflowerror + lastbinerror * lastbinerror )
        hist.SetBinContent(nbins, newcontent)
        hist.SetBinError  (nbins, newerror)

def ratio(name, numers, denom, min, max, ytitle):

    canvas = ROOT.TCanvas(name, name, 800, 800)

    for inum, numer in enumerate(numers):

        numerdenom = copy.copy(numer)
        denomdenom = copy.copy(denom)
        
        numerdenom.SetName(numer.GetName()+str(inum)+"numerdenom")
        denomdenom.SetName(numer.GetName()+str(inum)+"denomdenom")
        
        for hist in [numerdenom, denomdenom]:
            hist.Reset()
            hist.SetMinimum(min)
            hist.SetMaximum(max)
            hist.GetYaxis().SetTitle(ytitle)
            
            ROOT.SetOwnership(hist, False)

        nbins = numer.GetNbinsX()
        for bin in xrange(0, nbins+2):
            
            nc = numer.GetBinContent(bin)
            dc = denom.GetBinContent(bin)
            ne = numer.GetBinError(bin)
            de = denom.GetBinError(bin)
            
            numerdenom.SetBinContent(bin, nc/dc if dc else 0)
            denomdenom.SetBinContent(bin, 1.0   if dc else 0)
            numerdenom.SetBinError(  bin, ne/dc if dc else 0)
            denomdenom.SetBinError(  bin, de/dc if dc else 0)

        denomdenom.SetFillColor(ROOT.kAzure-9)
        denomdenom.SetMarkerSize(0.0)
        if inum==0:
            denomdenom.Draw("E2, same")
        numerdenom.Draw("PE, same")

    return canvas

def same_xaxis(name, top_canvas, bottom_canvas, split=0.35, axissep=0.04, ndivs=[505, 505]):

    canvas = ROOT.TCanvas(name, name, 800, 800)
    canvas.cd()
    
    top_pad = ROOT.TPad(canvas.GetName()+"_top_pad", "",  0, split, 1, 1, 0, 0, 0)
    top_pad.Draw()

    bottom_pad = ROOT.TPad(canvas.GetName()+"_bottom_pad", "",  0, 0, 1, split, 0, 0, 0)
    bottom_pad.Draw()

    top_pad.cd()
    top_canvas.DrawClonePad()
    bottom_pad.cd()
    bottom_canvas.DrawClonePad()

    top_pad.SetTopMargin(canvas.GetTopMargin()*1.0/(1.0-split))
    top_pad.SetBottomMargin(axissep)
    top_pad.SetRightMargin(canvas.GetRightMargin())
    top_pad.SetLeftMargin(canvas.GetLeftMargin())
    top_pad.SetFillStyle(0) # transparent
    top_pad.SetBorderSize(0)

    bottom_pad.SetTopMargin(axissep)
    bottom_pad.SetBottomMargin(canvas.GetBottomMargin()*1.0/split)
    bottom_pad.SetRightMargin(canvas.GetRightMargin())
    bottom_pad.SetLeftMargin(canvas.GetLeftMargin())
    bottom_pad.SetFillStyle(0) # transparent
    bottom_pad.SetBorderSize(0)

    pads = [top_pad, bottom_pad]
    factors = [0.9/(1.0-split), 0.9/split]
    for i_pad, pad in enumerate(pads):
        ROOT.SetOwnership(pad, False)
        factor = factors[i_pad]
        ndiv = ndivs[i_pad]
        prims = [ p.GetName() for p in pad.GetListOfPrimitives() ]
        for name in prims:
            h = pad.GetPrimitive(name)
            if any([isinstance(h, obj) for obj in [ROOT.TH1, 
                                                   ROOT.THStack, 
                                                   ROOT.TGraphAsymmErrors,
                                                   ]]):
                h.SetLabelSize(0.055, "XY")
                h.SetTitleSize(0.055, "XY")
                try:
                    h = h.GetHistogram()
                except:
                    pass
                h.SetLabelSize(h.GetLabelSize("Y")*factor, "Y")
                h.SetTitleSize(h.GetTitleSize("X")*factor, "X")
                h.SetTitleSize(h.GetTitleSize("Y")*factor, "Y")
                # h.SetTitleOffset(h.GetTitleOffset("Y")/factor, "Y")
                h.SetTitleOffset(0.9 if i_pad==0 else 0.5, "Y")
                h.GetYaxis().SetNdivisions(ndiv)
                h.GetXaxis().SetNdivisions(ndiv)
                if i_pad == 0:
                    h.SetLabelSize(0.0001, "X")
                    h.GetXaxis().SetTitle("")
                else:
                    h.SetLabelSize(h.GetLabelSize("X")*factor, "X")

    canvas.cd()
    return canvas

def compare(data, pred):
    ks   = data.KolmogorovTest(pred)
    chi2 =        data.Chi2Test(pred, "QUW CHI2")
    ndf  = chi2 / data.Chi2Test(pred, "QUW CHI2/NDF") if chi2 else 0.0
    return ks, chi2, ndf

