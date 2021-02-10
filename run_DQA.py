import sys
try:
    sys.argv[1]
except:     
    print('Please indicate which folder contains the DQA data?\ne.g. "run_DQA ~/DATA/test7"')
    exit()


import definitions_DQA as dqa
from pathlib import Path
import numpy as np
from datetime import datetime
import pandas as pd
import plotly.express as px
import sys
import sqlite3 as db
# Create your connection.
# conn = db.connect(Path(__file__).resolve().parent/'db'/'app.db')
conn = db.connect('/Users/papo/Sync/Projects/DQA_WEB_APP/app/db/app.db')

# coil_list = ['Spine1','Spine2','Spine3', 'Spine4','Spine5','Spine6','Spine7','Spine8']
# coil_list = ['SP1','SP2','SP3', 'SP4','SP5','SP6','SP7', 'BM_', 'BMlong', 'Breast_r', 'Breast_Biopsy', 'FlexSmall', 'FlexLarge','Hand','Foot','Knee']
coil_list = ['DQA']


def run_tests(input_folder='/Users/papo/Sync/MRdata/DQA'):
    '''
    run_tests:
    Run the DQA tests for all the datasets found inside the 'input_folder' (recursively).
    Parameter: input_folder. Path to the folder with the DQA dataset.
    Usage: run_tests input_folder
    E.g.: 'run_tests ~/DATA/'
    '''

    input_folder = Path(input_folder)
    nifti_folder = dqa.convert2NIFTI(input_folder)
    test_files = dqa.parse_files(nifti_folder,coil_list)
    tests = [dqa.SNR_test(files) for files in test_files]

    # Show results and combine them into a df
    frames = []
    # plt.close('all')
    for n, test in enumerate(tests):
        print(f"test {n+1}, {test.name}:")
        print(f"   SNR={int(np.round(test.SNR_global))}")
        print(f"   nSNR={int(np.round(test.nSNR))}\n")
        test.plot(out_file=Path(nifti_folder).parent / f"Test{n+1}_ROI.png")
        frames.append(test.results_df)

    all_df = pd.concat(frames).reindex()
    all_df.reset_index(drop=True, inplace=True)
    all_df["Acquisition Date"] = pd.to_datetime(all_df["AcquisitionDateTime"])
    all_df.drop(columns=["AcquisitionDateTime"], inplace=True)
    df_name = f'Results_Summary{datetime.now().strftime("_%d%b%Y")}.csv'
    all_df.to_csv(Path(nifti_folder).parent / df_name)


    

    # NSNR bar plot (HTML)
    barchart = px.bar(
        all_df,
        x="Acquisition Date",
        y="NSNR",
        error_y="NSNR_std",
        title=f"Daily QA: {all_df.ManufacturersModelName[0]} ({all_df.InstitutionAddress[0]})",
        color="Name",
        )

    barchart.for_each_trace(lambda x: x.update(error_y_color=x.marker.color))
    barchart.show()

    all_df['NSNR'] = all_df['NSNR'].astype(float).round(0)
    barchart2 = px.bar(
        all_df,
        x="Name",
        y="NSNR",
        error_y="NSNR_std",
        text="NSNR",
        title=f"Spine Coils: {all_df.ManufacturersModelName[0]} ({all_df.InstitutionAddress[0]})",
        # color="Name",
    )
    barchart2.for_each_trace(lambda x: x.update(error_y_color=x.marker.color))
    barchart2.show()

    return all_df



def small_df(df):
    small_df = df[['Acquisition Date', 'Name','NSNR','NSNR_std','Manufacturer','ManufacturersModelName','InstitutionName','InstitutionalDepartmentName','InstitutionAddress','StationName','ProtocolName','CoilString']]
    small_df.columns = ['Date','Coil','NSNR','NSNR_std','Manufacturer','ManufacturersModelName','InstitutionName','InstitutionalDepartmentName','InstitutionAddress','StationName','ProtocolName','CoilString']
    try:
        small_df[['ReceiveCoilName','ReceiveCoilActiveElements']] = df[['ReceiveCoilName','ReceiveCoilActiveElements']]
    except:
        pass
    csv_name = f'small_df{datetime.now().strftime("_%d%b%Y")}.csv'
    db_name = f'small_df{datetime.now().strftime("_%d%b%Y")}.db'

    small_df.to_csv(Path(__file__).resolve().parent/'db'/  csv_name)
    small_df.to_sql(name='DQA', con=conn, if_exists='append', index=False)


# def update_db(new_csv, old_csv):
#     data = pd.read_csv(Path(new_csv)
    





# script execution 
large_df = run_tests(sys.argv[1])
small_df(large_df)



