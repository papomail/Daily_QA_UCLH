import subprocess
from pathlib import Path



def fsl_split(nii):
    nii = Path(nii)
    #check input is correct
    if nii.suffix != '.nii':
        raise Exception(f'The input file format is not "nii": {nii.name}')
    #define filenames
    nii_original = f'{str(nii)}'
    nii_out = f'{str(nii)[0:-4]}_.nii'
    original_json = f'{str(nii)[0:-4]}.json'
    json1 = f'{str(nii)[0:-4]}_0000.json'
    json2 = f'{str(nii)[0:-4]}_0001.json'
    #run fslsplit
    subprocess.run(['fslsplit', nii_original, nii_out])
    #create copy of the json file for the automated script
    subprocess.run(['cp', original_json, json1])
    subprocess.run(['cp', original_json, json2])
    #delete the original nii and json files
    subprocess.run(['rm', nii])
    subprocess.run(['rm', original_json])
    return

def run_fsl_split(data_folder):
    print('\nSplitting 4D data')
    return [fsl_split(nii) for nii in Path(data_folder).rglob('*.nii') if '_DQA_2dynamics_' in str(nii)]

if __name__=="__main__":
    folder = input('Select the folder with the 4D data ')
    [fsl_split(nii) for nii in Path(folder).rglob('*.nii') if '_DQA_2dynamics_' in str(nii)]






