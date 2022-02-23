#THIS IS A PLACEHOLDER.  HAS NOT BEEN REWRITTEN TO ACCOMODATE MULTIPLE VISITS. :

#if you want to submit any structures besides facename you will need to figure out how to put 
#v1 back in src_subject_name per decision 10/26, and move version stuff out of file source or NDA will trigger need for associated files (for non facename structures)
#******
#facenamestructure had v1 appended to src_subject_name by hand in pinch and uploaded to GUI as singleton structure


#you will need your username/password to grab a jssession iD on intradb, as well as a valid REDCap token for the HCPA database, if doing the facename structure.
#read -s -p "ENTER PASSWORD: " PW;JSESSIONID=`curl -s -k -v -u plenzini:$PW http://hcpi-shadow21.nrg.wustl.edu:8080/data/JSESSIONID`;export JSESSIONID;echo $JSESSIONID
#requires subject xml and session xml saved in same folder
#./Stats2Structures.sh HCA 'acename ismotor arit' 1 hcpi-shadow21 plenzini
#./Stats2Structures.sh HCD 'uessing arit motion' 1 hcpi-shadow21 plenzini
#!/bin/bash

study=$1 #HCA
tasks=$2 #'acename ismotor arit' 'uessing arit motion'
visit=$3 # 1
HOST=$4  #hcpi-shadow21
username=$5 #plenzini

echo "WELCOME!!! This program merges the Tfmri Stats files with the PCP status, NDA fields, and (for facename) Redcap vars.  "
echo "You'll need a JSESSION ID..."
read -s -p "ENTER PASSWORD: " PW;JSESSIONID=`curl -s -k -v -u ${username}:$PW http://${HOST}.nrg.wustl.edu:8080/data/JSESSIONID`;export JSESSIONID;echo $JSESSIONID


#get a list of all of the task csv files inder the STG directory
#these are commented out right now because they take so long to run 
echo "Get listing of Tfmri stats files...(this can take 20 minutes on ZFS)..."
#ls -1a /data/intradb/archive/CCF_${study}_STG/arc001/${study}*_V${visit}_MR/RESOURCES/tfMRI*/LINKED_DATA/PSYCHOPY/*csv > TaskStatsFiles_${study}_V${visit}.csv
echo "Done"
#if HCD, need to grab a few more subjects that were sent but wont show up as prereqs met=yes (the 632 to put with 23)
#ls -a1 /data/intradb/tmp/NDAR/ndatransfer-202008040729-4268652529693431302/manifest | cut -d\_ -f1,2,3 | sort -u | tail -632 > found632

#use session id to pull PCP status from swagger - 
echo "Pulling PCP status..."
curl -X GET --cookie JSESSIONID=$JSESSIONID --header "Accept: application/json" "https://${HOST}.nrg.wustl.edu/xapi/pipelineControlPanel/project/CCF_${study}_STG/pipeline/NdaTransferPipeline/status?condensed=true&cached=true&dontWait=true&emailForEarlyReturn=false&limitedRefresh=false" > ${study}_NdaTransferPipelinePCP.json

#dont use xml from HCA as template...HCD is not the same format
echo "Grabbing the NDA fields from subject/session listing and giving them names that NDA structures expect..."
#session level table for nda_interview_age and nda_interview_date
curl -k -f -X POST --cookie JSESSIONID=$JSESSIONID "https://${HOST}.nrg.wustl.edu/data/search?inbody=true&format=csv" --data-binary "@sessionXML_${study}.xml" | awk -F, '$10 != ""' | cut -d, -f1,5,10,11 > NDAfields2.csv

#subject level table for nda_guid and nda_gender
curl -k -f -X POST --cookie JSESSIONID=$JSESSIONID "https://${HOST}.nrg.wustl.edu/data/search?inbody=true&format=csv" --data-binary "@subjectXML_${study}.xml" | awk -F, '$6 != ""' | cut -d, -f1,6,7 > NDAfields1.csv

#now make sure the structure definitions will have everything they need (NDA fields)
#note that there is a bug in the subject data and session data API grabber for the custom fields, whereby multiple rows (and all the custom fields) get output
#any fixes for that issue here will have to be unfixed later - use POST and XML instead
sort -k2 -o NDAfields2.csv NDAfields2.csv
sort -k1 -o NDAfields1.csv NDAfields1.csv
join -t, -1 1 -2 2 NDAfields1.csv NDAfields2.csv > NDAfields.csv
rm NDAfields1.csv NDAfields2.csv
echo "src_subject_id,subjectkey,gender,MR_ID,interview_age,interview_date" > NDAheader
sort -k4 -o NDAfields.csv NDAfields.csv

#this is currently commented out because it takes too long
#for task in $tasks
#do
#  echo "concatenating stats files for Task= [F/C/V/G/E]$task...please stand by"
#  grep -i $task TaskStatsFiles_${study}_V${visit}.csv | grep -i stats > StatsFiles.csv
#  echo "####" > testout2.txt
#  while read f; do   awk -F, 'NR==1{print "file_name",$0;next}{print FILENAME , $0}' OFS=, $f >> testout2.txt; done < StatsFiles.csv
#  head -2 testout2.txt > header
#  grep -v file_name testout2.txt > body
#  cat header body | grep -v '##' > testout3.txt
#  echo "MR_ID" > MR_ID
#  cut -d, -f1 testout3.txt | cut -d\/ -f7 | tail -n +2 >> MR_ID
#  paste -d, MR_ID testout3.txt > ${task}Stats_${study}_V${visit}.txt
#  rm testout2.txt testout3.txt header body MR_ID StatsFiles.csv
#  sort -k 1,1 -o ${task}Stats_${study}_V${visit}.txt ${task}Stats_${study}_V${visit}.txt
#  echo "Done: [F/C/V]${task}Stats_${study}_V${visit}.txt"
#done

#create your header and build out the jq selects so that you just get ids of the V1 sessions with prereqs met for the particular subgroup
#then remove the quotes from the output
for task in $tasks 
do
  echo "Selecting Visit=$visit, Prereqs=Yes, Tfmri sessions for Task= [F/C/V/G/E]$task..."
  echo "MR_ID" > ${task}${study}_V${visit}_PrereqsTrue.txt
  cat ${study}_NdaTransferPipelinePCP.json | jq -c --arg task "$task" --arg visit "V$visit" '.[] | select(.prereqs== true ) | select(.subGroup | contains("UnprocTfmri")) | select(.subGroup | contains($task)) | select(.entityLabel | contains($visit)) | "\(.entityLabel)"' >> ${task}${study}_V${visit}_PrereqsTrue.txt
  sed -i 's/\"//g' ${task}${study}_V${visit}_PrereqsTrue.txt
  if [ "$study" == "HCD" ] ; then 
    cat found632 ${task}${study}_V${visit}_PrereqsTrue.txt > temp
    mv temp ${task}${study}_V${visit}_PrereqsTrue.txt
  fi
  sort -k 1,1 -o ${task}${study}_V${visit}_PrereqsTrue.txt ${task}${study}_V${visit}_PrereqsTrue.txt
done


  
echo "Joining PCP info with stats by MR_ID, and then with NDA fields (by MR_ID)"
#make sure that duplications are preserved...e.g. where PA and AP scans were collected - there are! yay!
#join the stats and the PCP information for each task by MR_ID so that you only have the stats files from the individs whose prereqs are met
for task in $tasks 
do
  join -t , -j1 ${task}${study}_V${visit}_PrereqsTrue.txt ${task}Stats_${study}_V${visit}.txt > ${task}${study}_V${visit}_PrereqsTrueStats.txt
  sort -r -k 1,1 -o ${task}${study}_V${visit}_PrereqsTrueStats.txt ${task}${study}_V${visit}_PrereqsTrueStats.txt
done

#join the stats files with the NDA fields, by MR_ID
for task in $tasks 
do
  grep MR_ID ${task}${study}_V${visit}_PrereqsTrueStats.txt > Statsheader
  grep -v MR_ID ${task}${study}_V${visit}_PrereqsTrueStats.txt > bodybig
  sort -k1 -o bodybig bodybig
  join -t , -1 1 -2 4 bodybig NDAfields.csv > temp
  join -t , -1 1 -2 4 Statsheader NDAheader > newheader
  cat newheader temp > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
  rm Statsheader bodybig temp newheader 
done
#SPECIAL REDCAP MERGE FOR FACENAME TASK
#redcap stuff comes in with a subject (not an MR id).  Visit is implied by event name visit_1_arm1 in this case (not always the same event name in redcap)
#for facename, must stack and rename the cb* varialbs assign cb1 or cb2 to version element 
echo $'HCA8653186_V1\nHCA9354585_V1\nHCD1027126_V1\nHCD1784065_V1\nHCD2643456_V1' > facemaskfail_list.txt

#by getting get column number of src_subject_id (it was 88 for this task

#checked that the version from IntraDB is missing in cases where not missing in REDcap.  Use the redcap one.  Drop version from Intradb
for task in $tasks ; do 
  if [ "$task" == "acename" ] && [ "$study" == "HCA" ] ; then
    echo "Extra merge with REDCAP for Facename Task for HCA study"
    read -s -p "ENTER REDCAP TOKEN: " token
    DATA="token=${token}&content=record&format=csv&type=flat&fields[0]=cb1_10a&fields[1]=cb1_10a_other&fields[2]=cb1_1a&fields[3]=cb1_1a_other&fields[4]=cb1_2a&fields[5]=cb1_2a_other&fields[6]=cb1_3a&fields[7]=cb1_3a_other&fields[8]=cb1_4a&fields[9]=cb1_4a_other&fields[10]=cb1_5a&fields[11]=cb1_5a_other&fields[12]=cb1_6a&fields[13]=cb1_6a_other&fields[14]=cb1_7a&fields[15]=cb1_7a_other&fields[16]=cb1_8a&fields[17]=cb1_8a_other&fields[18]=cb1_9a&fields[19]=cb1_9a_other&fields[20]=subject_id&events[0]=visit_${visit}_arm_1&rawOrLabel=raw&rawOrLabelHeaders=raw&exportCheckboxLabel=false&exportSurveyFields=false&exportDataAccessGroups=false&returnFormat=json"
    CURL=`which curl`
    $CURL -H "Content-Type: application/x-www-form-urlencoded" \
      -H "Accept: application/json" \
      -X POST \
      -d $DATA \
      https://redcap.wustl.edu/redcap/srvrs/prod_v3_1_0_001/redcap/api/ | awk -F, '$2 != ""' | sed 's/$/,cb1/'  > redcapfacenamedataCB1.csv

    DATA="token=${token}&content=record&format=csv&type=flat&fields[0]=cb2_10a&fields[1]=cb2_10a_other&fields[2]=cb2_1a&fields[3]=cb2_1a_other&fields[4]=cb2_2a&fields[5]=cb2_2a_other&fields[6]=cb2_3a&fields[7]=cb2_3a_other&fields[8]=cb2_4a&fields[9]=cb2_4a_other&fields[10]=cb2_5a&fields[11]=cb2_5a_other&fields[12]=cb2_6a&fields[13]=cb2_6a_other&fields[14]=cb2_7a&fields[15]=cb2_7a_other&fields[16]=cb2_8a&fields[17]=cb2_8a_other&fields[18]=cb2_9a&fields[19]=cb2_9a_other&fields[20]=subject_id&events[0]=visit_${visit}_arm_1&rawOrLabel=raw&rawOrLabelHeaders=raw&exportCheckboxLabel=false&exportSurveyFields=false&exportDataAccessGroups=false&returnFormat=json"
    CURL=`which curl`
    $CURL -H "Content-Type: application/x-www-form-urlencoded" \
      -H "Accept: application/json" \
      -X POST \
      -d $DATA \
      https://redcap.wustl.edu/redcap/srvrs/prod_v3_1_0_001/redcap/api/ | awk -F, '$2 != ""' | sed 's/$/,cb2/' > redcapfacenamedataCB2.csv

    echo "check alignment of stacked vars:  "
    head -1 redcapfacenamedataCB2.csv > header2 
    head -1 redcapfacenamedataCB1.csv > header1
    echo "src_subject_id,f1_recall,f1_other,f2_recall,f2_other,f3_recall,f3_other,f4_recall,f4_other,f5_recall,f5_other,f6_recall,f6_other,f7_recall,f7_other,f8_recall,f8_other,f9_recall,f9_other,f10_recall,f10_other,redversion" > newheader
    cat header1 header2 newheader
    grep -v '_' redcapfacenamedataCB1.csv > CB1.csv #removes header row and any that aren't supposed to stay
    grep -v '_' redcapfacenamedataCB2.csv > CB2.csv #removes header row and any that aren't supposed to stay
    echo $'HCA8557796\nHCA8532174\nHCA6333158\nHCA7378993\nHCA6576487' > RedcapCbV1ExcludeList.txt # subjects with version discrepancies between scanner and post-scanner fu
    cat newheader CB1.csv CB2.csv | grep -v -f RedcapCbV1ExcludeList.txt > redcapvars.csv
    rm header1 header2 newheader CB1.csv CB2.csv redcapfacenamedataCB1.csv redcapfacenamedataCB2.csv
    column=`WORD="src_subject_id"; sort -r ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt | head -n1 | tr "," "\n" | grep -n $WORD | cut -d: -f1`
    echo "passed first cut"
    sort -k1 -o redcapvars.csv redcapvars.csv 
    echo $'HCA9515684_V1\nHCA9354585_V1\nHCA9373589_V1\nHCA9300057_V1\nHCA9286392_V1\nHCA9043770_V1\nHCA9007968_V1\nHCA6877300_V1\nHCA6848090_V1\nHCA6269377_V1\nHCA6685492_V1\nHCA6788199_V1\nHCA7502059_V1\nHCA7703372_V1\nHCA7995311_V1\nHCA8358689_V1\nHCA8983208_V1\nHCA6086369_V1\nHCA6166973_V1\nHCA6162662_V1' > CBversionBUTmissingStatsList.txt
    grep -v -f CBversionBUTmissingStatsList.txt ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > temp
    grep -v -f facemaskfail_list.txt temp > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    sort -k${column} -o ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt 
    join -t , -1 1 -2 ${column} redcapvars.csv ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfieldsREDCap.txt
    sort -r -k1 -o ${task}${study}_V${visit}_PrereqsTrueStatsNDAfieldsREDCap.txt ${task}${study}_V${visit}_PrereqsTrueStatsNDAfieldsREDCap.txt
    MR_ID_column=`WORD="MR_ID"; head -n1 ${task}${study}_V${visit}_PrereqsTrueStatsNDAfieldsREDCap.txt | tr "," "\n" | grep -n $WORD | cut -d: -f1`
    echo "passed second cut"
    cut -d, -f$MR_ID_column --complement ${task}${study}_V${visit}_PrereqsTrueStatsNDAfieldsREDCap.txt > test
    echo "passed third cut"
    filename_column=`WORD="file_name"; head -n1 test | tr "," "\n" | grep -n $WORD | cut -d: -f1`
    cp test test2
    echo "passed fourth cut"
    cut -d, -f$filename_column --complement test2 > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfieldsREDCap.txt 
    echo "passed fifth cut"
    echo "Producing NDA-formatted structure: HCPA_facename01_10_12_2020.csv"
    echo "facename,01" > facenameheader
    cat facenameheader ${task}${study}_V${visit}_PrereqsTrueStatsNDAfieldsREDCap.txt > HCPA_facename01_10_26_2020.csv
    column=`WORD="redversion"; head -n2 HCPA_facename01_10_26_2020.csv | tail -1 | tr "," "\n" | grep -n $WORD | cut -d: -f1`
    cut -d, -f$column --complement HCPA_facename01_10_26_2020.csv > tempc
    mv tempc HCPA_facename01_10_26_2020.csv
    sed -i 's/"""starts with H"""/starts_w_H/' HCPA_facename01_10_26_2020.csv
    rm facenameheader test
  fi
done
##put this line back in as appropriate when hear back from Greg about whether run needs to be strung with cb1 in redversion (stats file also had version variable)
#cut -d, -f$filename_column test | cut -d\/ -f12 | cut -d\_ -f5 | sed 's/^$/version_run/' > version_form
#cut -d, -f$filename_column test | cut -d\/ -f9 | sed 's/file_name/file_source/' > data_file1
#paste -d, test data_file1 version_form > test2
 
#the rest of the tasks are pretty straightforward to get past finish line
for task in $tasks ; do 
  if [ "$task" == "arit" ] && [ "$study" == "HCA" ] ; then
    echo "MR_ID,file_name,gng_hitrate,Miss_Prop,CR_Prop,gng_falsealarm,bs_cor_go_rt_total,FA_RT,pre2_CR_Prop,pre2_FA_Prop,pre2_FA_RT,pre3_CR_Prop,pre3_FA_Prop,pre3_FA_RT,pre4_CR_Prop,pre4_FA_Prop,pre4_FA_RT,src_subject_id,subjectkey,gender,interview_age,interview_date" > newheader
    grep -v "MR_ID" ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > bodybig
    cat newheader bodybig > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    cut -d, -f2 ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt | cut -d\/ -f9 | sed 's/file_name/file_source/' > data_file1
    cut -d, -f2 ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt | cut -d\/ -f12 | cut -d\_ -f5 | sed 's/^$/version_form/' > version_form
    paste -d, ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt data_file1 version_form > test
    cut -d, -f3- test > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    mv ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt temp
    grep -v -f facemaskfail_list.txt temp > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    echo "Producing NDA-formatted structure: HCPA_CARITgonogo_01_10_12_2020.csv"
    echo "gonogo,01" > caritheader
    cat caritheader ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > HCPA_CARITgonogo_01_10_12_2020.csv
  fi
  if [ "$task" == "ismotor" ] && [ "$study" == "HCA" ] ; then
    cut -d, -f2 ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt | cut -d\/ -f9 | sed 's/file_name/file_source/' > data_file1
    cut -d, -f2 ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt | cut -d\/ -f12 | cut -d\_ -f5 | sed 's/^$/version_form/' > version_form
    paste -d, ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt data_file1 version_form > test
    cut -d, -f3- test > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    mv ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt temp
    grep -v -f facemaskfail_list.txt temp > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    echo "Producing NDA-formatted structure: HCPA_vismotor_01_10_12_2020.csv"
    echo "vismotor,01" > vismotorheader
    cat vismotorheader ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > HCPA_vismotor_01_10_12_2020.csv
  fi
  if [ "$task" == "arit" ] && [ "$study" == "HCD" ] ; then
    echo "MR_ID,file_name,gng_hitrate,Miss_Prop,CR_Prop,gng_falsealarm,bs_cor_go_rt_total,FA_RT,Rew_CR_Prop,Rew_FA_Prop,Loss_CR_Prop,Loss_FA_Prop,Rew_FA_RT,Loss_FA_RT,pre2_CR_Prop,pre2_FA_Prop,pre2_FA_RT,pre3_CR_Prop,pre3_FA_Prop,pre3_FA_RT,pre4_CR_Prop,pre4_FA_Prop,pre4_FA_RT,src_subject_id,subjectkey,gender,interview_age,interview_date" > newheader
    grep -v "MR_ID" ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > bodybig
    cut -d, -f3- test > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    mv ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt temp
    grep -v -f facemaskfail_list.txt temp > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    echo "Producing NDA-formatted structure: HCPD_CARITgonogo_01_10_12_2020.csv"
    echo "gonogo,01" > caritheader
    cat caritheader ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > HCPD_CARITgonogo_01_10_12_2020.csv
  fi
  ##NEED TO ADD EXPERIMENT DESCRIPTION COLUMN
  if [ "$task" == "uessing" ] && [ "$study" == "HCD" ] ; then
    cut -d, -f2 ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt | cut -d\/ -f9 | sed 's/file_name/file_source/' > data_file1
    cut -d, -f2 ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt | cut -d\/ -f12 | cut -d\_ -f5 | sed 's/^$/version_form/' > version_form
    sed -e 's/$/,HCP-Developement Guessing Task/' ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > extra
    head -1 extra > header
    tail -n+2 extra > body
    sed -i 's/HCP-Developement Guessing Task/experiment_description/' header
    cat header body > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    paste -d, ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt data_file1 version_form > test
    cut -d, -f3- test > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    mv ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt temp
    grep -v -f facemaskfail_list.txt temp > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    echo "Producing NDA-formatted structure: HCPD_guessing_01_10_12_2020.csv"
    echo "guess_task,01" > guessheader
    cat guessheader ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > HCPD_guessing_01_10_12_2020.csv
  fi
  if [ "$task" == "motion" ] && [ "$study" == "HCD" ] ; then
    cut -d, -f2 ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt | cut -d\/ -f9 | sed 's/file_name/file_source/' > data_file1
    cut -d, -f2 ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt | cut -d\/ -f12 | cut -d\_ -f5 | sed 's/^$/version_form/' > version_form
    paste -d, ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt data_file1 version_form > test
    cut -d, -f3- test > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    mv ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt temp
    grep -v -f facemaskfail_list.txt temp > ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt
    echo "Producing NDA-formatted structure: HCPD_emotion_01_10_12_2020.csv"
    echo "emotion_task,01" > emotionheader
    cat emotionheader ${task}${study}_V${visit}_PrereqsTrueStatsNDAfields.txt > HCPD_emotion_01_10_12_2020.csv
  fi

done

#cleanup
rm test test2 NDAheader newheader caritheader emotionheader guessheader vismotorheader data_file1 version_form bodybig
echo "HAVE A WONDERFUL DAY"



