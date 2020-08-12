

from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime 

from nilearn import plotting, image, masking
from nilearn.plotting import plot_roi

import pandas as pd
import subprocess

import json  
from pandas import json_normalize, read_json
import plotly
import plotly.express as px
from definitions_DailyQA import *
import sys


def run_tests(input_folder='/Users/papo/Sync/Projects/DQA_tests/DATA/RT_Ingenia_Coil_data'):

    input_folder=Path(input_folder)
    nifti_folder=convert2NIFTI(input_folder)
    print(f'nifti_folder={nifti_folder}')
    test_files=parse_files(nifti_folder)
    tests=[SNR_test(files) for files in test_files]
    

    # %%
    # Show results and combine them into a df
    # plt.close('all')
    frames=[]
    plt.close('all')
    for n,test in enumerate(tests):
        print(f'test {n+1}, {test.name}:\n   SNR={int(np.round(test.SNR_global))}\n   nSNR={int(np.round(test.nSNR))}\n')
        test.plot(out_file=nifti_folder/f'Test{n+1}_ROI.png')
        frames.append(test.results_df)

    # plt.show(block=False) 

    all_df=pd.concat(frames).reindex()
    all_df.reset_index(drop=True, inplace=True)
    all_df['Acquisition Date'] = pd.to_datetime(all_df['AcquisitionDateTime'])
    all_df.drop(columns=['AcquisitionDateTime'],inplace=True)
    all_df.to_hdf(nifti_folder/f'Results_Summary{datetime.now().strftime("_%d%b%Y")}')


    # %%
    barchart=px.bar(all_df, x='Acquisition Date', y='NSNR',error_y='NSNR_std',title=f'Daily QA: {all_df.ManufacturersModelName[0]} ({all_df.InstitutionAddress[0]})',color='Name')
    barchart.for_each_trace(lambda x: x.update(error_y_color=x.marker.color))
    barchart.show()

try:
    run_tests(sys.argv[1])
except:
    run_tests()
