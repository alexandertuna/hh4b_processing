file_data="hist/data15_13TeV/hadd.root"
file_ttbar="hist/mc15_13TeV.410007.ttbar_allhad/hadd.root"
file_qcd="hist/qcd/qcd.root"

path_3tag="sb_3tag77/j0_m"
path_4tag="sb_4tag77/j0_m"

path_2tag_4tag97="sb_2tag77_4tag97/j0_m"
path_2tag_N4tag97="sb_2tag77_N4tag97/j0_m"


echo
echo " 4tag"
python extract_norms.py --data=${file_data}:${path_4tag} --ttbar=${file_ttbar}:${path_4tag} --qcd=${file_qcd}:${path_2tag}        ; echo 
python extract_norms.py --data=${file_data}:${path_4tag} --ttbar=${file_ttbar}:${path_4tag} --qcd=${file_qcd}:${path_2tag_4tag97} ; echo 
python extract_norms.py --data=${file_data}:${path_4tag} --ttbar=${file_ttbar}:${path_4tag} --qcd=${file_qcd}:${path_2tag_N4tag97}; echo

echo
echo " 3tag"
python extract_norms.py --data=${file_data}:${path_3tag} --ttbar=${file_ttbar}:${path_3tag} --qcd=${file_qcd}:${path_2tag}        ; echo 
python extract_norms.py --data=${file_data}:${path_3tag} --ttbar=${file_ttbar}:${path_3tag} --qcd=${file_qcd}:${path_2tag_4tag97} ; echo 
python extract_norms.py --data=${file_data}:${path_3tag} --ttbar=${file_ttbar}:${path_3tag} --qcd=${file_qcd}:${path_2tag_N4tag97}; echo


