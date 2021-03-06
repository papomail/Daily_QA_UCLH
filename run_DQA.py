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

# coil_list=['Spine1','Spine2','Spine3', 'Spine4','Spine5','Spine6','Spine7','Spine8']
coil_list=['SP1','SP2','SP3', 'SP4','SP5','SP6','SP7', 'BM_', 'BMlong', 'Breast_r', 'Breast_Biopsy', 'FlexSmall', 'FlexLarge','Hand','Foot','Knee']

def run_tests(input_folder):
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



run_tests(sys.argv[1])