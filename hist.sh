for sel in "sb_2tag77" "sb_2tag77_4tag97" "sb_2tag77_N4tag97"; do

    python hist.py --input=skim/mc15_13TeV.410007.*/*.root*   --output=hist/${sel}/mc15_13TeV.410007.ttbar_allhad --filesperjob=1 --selection=${sel}
    python hist.py --input=skim/data15_13TeV.period*/*.root*  --output=hist/${sel}/data15_13TeV                   --filesperjob=3 --selection=${sel}

done

# python hist.py --input=skim/mc*/skim_0000.root --output=hist/test --filesperjob=1 --selection=sb_2tag77

