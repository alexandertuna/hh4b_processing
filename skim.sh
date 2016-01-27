ntuplepath="/n/atlasfs/atlasdata/tuna/hh4b/hh4b-00-06-02"

for period in "periodD" "periodE" "periodF" "periodG" "periodH" "periodJ"; do

    echo
    # python skim.py --filesperjob=15 --input=${ntuplepath}/group.*.data15_13TeV.${period}.*/*.root* --output=./skim/data15_13TeV.${period}

done

python skim.py --filesperjob=1 --input=${ntuplepath}/group.*.mc15_13TeV.410007.*/*.root* --output=./skim/mc15_13TeV.410007.ttbar_allhad


