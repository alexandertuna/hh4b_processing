for mass in "sb_" "cr_" "sr_"; do
    for tag in "2tag77" "2tag77_4tag97" "2tag77_N4tag97" "3tag77" "4tag77"; do

        sel=${mass}${tag}
        python hist.py --input=skim/mc15_13TeV.410007.*/*.root*   --output=hist/${sel}/mc15_13TeV.410007.ttbar_allhad --filesperjob=1 --selection=${sel}
        python hist.py --input=skim/data15_13TeV.period*/*.root*  --output=hist/${sel}/data15_13TeV                   --filesperjob=3 --selection=${sel}

    done
done

mkdir hist/data15_13TeV/
mkdir hist/mc15_13TeV.410007.ttbar_allhad/

hadd hist/data15_13TeV/hadd.root                   hist/*/data15_13TeV/hist.root
hadd hist/mc15_13TeV.410007.ttbar_allhad/hadd.root hist/*/mc15_13TeV.410007.ttbar_allhad/hist.root

rm -f hist/*/data15_13TeV/hist*.root hist/*/mc15_13TeV.410007.ttbar_allhad/hist*.root
rmdir hist/*/data15_13TeV/ hist/*/mc15_13TeV.410007.ttbar_allhad/
rmdir hist/*/

python qcd.py


# python hist.py --input=skim/data15_13TeV.periodG/skim_0000.root --output=hist/test --filesperjob=1 --selection=sb_2tag77

