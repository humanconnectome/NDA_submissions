#functions to clean up prepared structures (e.g. if all meaningful variables are missing
# Ad hoc functions to clean up empty rows for particular instruments after generated (issue for redcap data)
import pandas as pd
import numpy as np
def redcleanup(structure="lbadl01", filePath="./prepped/hcd/", extraomitcol1='NO', extraomitcol2='NO',
               extraomitcol3='NO', extraomitcol4='NO', extraomitcol5='NO'):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]

    df = pd.read_csv(filePath + structure + ".csv", header=1)
    df.head()

    print("NumRows Before: " + str(df.shape[0]))
    subfields = df.columns.to_list()
    subfields.remove('subjectkey')
    subfields.remove('src_subject_id')
    subfields.remove('interview_date')
    subfields.remove('interview_age')
    subfields.remove('sex')
    try:
        subfields.remove('comqother')
    except:
        pass
    if structure=='bsc01':
        df=df.loc[~((df.ed1_blood==0) & (df.ed1_saliva==0))]
    if extraomitcol1 and extraomitcol1 != 'NO':
        subfields.remove(extraomitcol1)
    if extraomitcol2 and extraomitcol2 != 'NO':
        subfields.remove(extraomitcol2)
    if extraomitcol3 and extraomitcol3 != 'NO':
        subfields.remove(extraomitcol3)
    if extraomitcol4 and extraomitcol4 != 'NO':
        subfields.remove(extraomitcol4)
    if extraomitcol5 and extraomitcol5 != 'NO':
        subfields.remove(extraomitcol5)
    df = df.dropna(how='all', subset=subfields)
    print("NumRows After: " + str(df.shape[0]))

    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)







#these guys already set to 99s in map, so null finder wont work above
def asrover60(structure="asr01",filePath="./prepped/hca/"):
    print(structure)
    strucroot=structure[:-2]
    strucnum=structure[-2:]
    df=pd.read_csv(filePath+structure+".csv",header=1)
    print("NumRows Before: "+str(df.shape[0]))
    #df=df.loc[df.interview_age>719].copy()
    df=df.loc[~((df.asr2_2==-99)&(df.asr3_2==-99))]
    print("NumRows After: "+str(df.shape[0]))
    with open(filePath+structure+".csv",'w') as f:
        f.write(strucroot+","+str(int(strucnum))+"\n")
        df.to_csv(f,index=False)
    #print(subset)

# these guys already set to 99s in map, so null finder wont work above
def asr(structure="asr01", filePath="./prepped/hcd/"):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    print("NumRows Before: " + str(df.shape[0]))
    print("NumColumns Before: " + str(df.shape[1]))
    # df=df.loc[df.interview_age>719].copy()
    df = df.loc[~((df.asr2_2 == -99) & (df.asr3_2 == -99))]
    print("NumRows After: " + str(df.shape[0]))
    print("NumColunms After: " + str(df.shape[1]))
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)
    # print(subset)


def dropcols(structure="bsc01", filePath="./prepped/hcd/", dropcols=[]):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    print("NumColumns Before: " + str(df.shape[1]))
    df = df.drop(columns=dropcols)
    print("NumColumns After: " + str(df.shape[1]))
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)


# these guys already set to 99s in map, so null finder wont work above
def bisbasparent999(structure="bisbas01", filePath="./prepped/hcd/"):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    print("NumRows Before: " + str(df.shape[0]))
    df = df.loc[~(df.bissc_total == 999)].copy()
    print("NumRows After: " + str(df.shape[0]))
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)


# these guys already set to 99s in map, so null finder wont work above
def neo999(structure="neo_ffi_form_s_adult_200301", filePath="./prepped/hcd/"):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    print("NumRows Before: " + str(df.shape[0]))
    df = df.loc[~((df.neo_n == 999) & (df.neo_e == 999) & (df.neo_a == 999))].copy()
    print("NumRows After: " + str(df.shape[0]))
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)


def cbcl999(structure="cbcl01", filePath="./prepped/hcd/"):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    print("NumRows Before: " + str(df.shape[0]))
    df = df.loc[~((df.cbcl1 == 999) & (df.cbcl2 == 999) & (df.cbcl3 == 999) & (df.cbcl4 == 999))].copy()
    df = df.drop(
        columns=['cbcl1_2_text', 'cbcl2_3_text', 'cbcl5_2_text', 'cbcl6_6_text', 'cbcl7_3_text', 'cbcl9_2_text',
                 'cbcl56h_des', 'cbcl10_1_text', 'cbcl11_2_text', 'cbcl11_6_text', 'cbcl12_6_text', 'cbcl13_1_text',
                 'cbcl13_5_text', 'cbcl13_6_text', 'cbcl13_7_text', 'cbcl14_7_text', 'cbcl16_1_text', 'cbcl16_6_text',
                 'cbcl113a_des', 'cbcl113b_des', 'cbcl113c_des'])
    print("NumRows After: " + str(df.shape[0]))
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)


def cbcl1_5_999(structure="cbcl1_501", filePath="./prepped/hcd/"):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    print("NumRows Before: " + str(df.shape[0]))
    df = df.loc[~((df.cbcl1 == 999) & (df.cbcl56a == 999) & (df.cbcl_nt == 999) & (df.cbcl_eye == 999))].copy()
    df = df.drop(
        columns=['cbcl24b_text', 'cbcl31b_text', 'cbcl5_2_text', 'cbcl7_3_text', 'cbcl10_1_text', 'cbcl57b_text',
                 'cbcl65b_text', 'cbcl74b_text', 'cbcl13_1_text', 'cbcl13_6_text', 'cbcl92b_text', 'cbcl113a_des',
                 'cbcl113b_des', 'cbcl113c_des', 'cbclpre101_des', 'adis_concern_what', 'trf_best'])
    print("NumRows After: " + str(df.shape[0]))
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)


def psqi(structure="psqi01", filePath="./prepped/hcd/"):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    print("NumRows Before: " + str(df.shape[0]))
    df.loc[df.psqip6b_4.isnull() == True, 'psqip6b_4'] = 88
    print("NumRows After: " + str(df.shape[0]))
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)


def medhxdrops(structure="medh01", filePath="./prepped/hcd/"):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    print("NumRows Before: " + str(df.shape[0]))
    df = df.drop(columns=['medhis_6e_describe', 'medhis_6t_describe', 'medhis_8b_describe'])
    print("NumRows After: " + str(df.shape[0]))
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)


# these guys already set to 99s in map, so null finder wont work above
def phenx25(structure="phenx_su01", filePath="./prepped/hcd/"):
    print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    print("NumRows Before: " + str(df.shape[0]))
    df = df.loc[~((df.ale_total_number_nm == 25))].copy()
    print("NumRows After: " + str(df.shape[0]))
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)


def cleanlist(structurelist=['lbadl01', 'mchq01'],fPath="./prepped/hcd/"):
    for i in structurelist:
        redcleanup(structure=i, filePath=fPath)


def cleanzeros(structure='vitals01', filePath="./prepped/hcd/"):
    # print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    df.loc[df.vtl007 == 0, 'vtl007'] = np.NaN
    # df.loc[df.bp_stand=='11/80','bp_stand']=np.NaN
    # df.loc[df.bp_stand=='9999','bp_stand']=np.NaN
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)

def integercleanup(structure='asr01', filePath="./prepped/hcd/", varlist=['a']):
    # print(structure)
    strucroot = structure[:-2]
    strucnum = structure[-2:]
    df = pd.read_csv(filePath + structure + ".csv", header=1)
    for v in varlist:
        df[v] = df[v].fillna(-9999).astype(int).astype(str).str.replace('-9999', '')
    with open(filePath + structure + ".csv", 'w') as f:
        f.write(strucroot + "," + str(int(strucnum)) + "\n")
        df.to_csv(f, index=False)

def satisfy(structure='scan_debrief01',filePath="./prepped/hca/"):
    print(structure)
    strucroot=structure[:-2]
    strucnum=structure[-2:]
    df=pd.read_csv(filePath+structure+".csv",header=1)
    print("NumRows Before: "+str(df.shape[0]))
    df=df.drop(columns=['satisfaction1more','satisfaction2more','satisfaction4more','satisfaction5','satisfaction6'])
    print("NumRows After: "+str(df.shape[0]))
    with open(filePath+structure+".csv",'w') as f:
        f.write(strucroot+","+str(int(strucnum))+"\n")
        df.to_csv(f,index=False)

#cleanupfuncs = {
#    "redcleanup": redcleanup,
#    "asrover60": asrover60,
#    "asr": asr,
##    "dropcols": dropcols,
#    "bisbasparent999": bisbasparent999,
#    "neo999": neo999,
#    "cbcl999": cbcl999,
#    "cbcl1_5_999": cbcl1_5_999,
#    "psqi": psqi,
#    "medhxdrops": medhxdrops,
##    "phenx25": phenx25,
#    "cleanlist": cleanlist,
#    "cleanzeros": cleanzeros,
#    "integercleanup": integercleanup,
#    "satisfy": satisfy
#}

