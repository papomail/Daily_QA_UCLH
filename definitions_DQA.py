from pathlib import Path
import numpy as np
from datetime import datetime
from nilearn import plotting, image, masking
import pandas as pd
import subprocess
import json as js
from pandas import json_normalize
from skimage import filters
from scipy import ndimage
import plotly.express as px


def convert2NIFTI(base_folder, **kwargs):
    now = datetime.now()
    base_folder = Path(base_folder)

    # output_folder = kwargs.get('output_folder', 'NIFTI')
    default_outdir = str(
        base_folder / f'Results{now.strftime("_%d%b%Y")}' / "DQA_NIFTIs"
    )

    output_folder = kwargs.get("output_folder", default_outdir)
    dcm2niix_path = kwargs.get("dcm2niix_path", "dcm2niix")
    dcm2niix_flag = kwargs.get(
        "dcm2niix_flag", False
    )  # Set dcm2nixx_flag=True to skip redoing the NIFTI conversion. (Creates an empty file 'dcm2niix_done' in every folder were dcm2niix was used).

    #rename  folders if they contain spaces (dcm2niix does not like spaces)
    for folder in sorted(base_folder.rglob("*")):
            if folder.is_dir():
                nospaces = str(folder).replace(' ','_')
                folder.rename(nospaces)

    print("\nChecking if DICOM to NIFTI conversion is needed...\n")
    # get the testfolders in the base_folder (single child)
    testfolders = [folder for folder in sorted(base_folder.glob("*")) if folder.is_dir()]
    


    needs_dcm2niix = []
    for i, testfolder in enumerate(testfolders):
        # print(f'output_folder={output_folder}')
        nf = [str(k) for k in testfolder.glob(Path(output_folder).stem)]
        qf = [str(k) for k in testfolder.glob("dcm2niix_done")]
        # print(f'nf={nf}')
        # print(f'qf={qf}')

        if nf or qf:
            print(f"Skipping {testfolder.name}  (already converted)")

        if not (nf or qf):
            needs_dcm2niix.append(testfolder)

    output_folder2 = []
    for i, folder in enumerate(needs_dcm2niix):

        input_folder = (
            folder if folder.name.lower() != "dicom" else folder.parent
        )  # avoid using 'DICOM' as the output-folder name
        output_folder2.append(Path(output_folder) / input_folder.name)  # wip

        try:
            output_folder2[i].mkdir(parents=True, exist_ok=False)
            if i == 0:
                print("\nRunning dcm2niix on the following folder(s):")
            print(folder)
        except:
            print(f"Skipping {folder.name}  (already converted)")
            continue

        dcm2niix_command = " ".join(
            [
                dcm2niix_path, # -f %f_%p_%t_%s    remove %f_ to exclude the folder_name in .nii files
                "-f %p_%t_%s",
                "-ba n",
                "-o",
                str(output_folder2[i].resolve()),
                str(input_folder.resolve()),
            ]
        )
        subprocess.run(dcm2niix_command, capture_output=True, shell=True)

        if dcm2niix_flag:
            flag = folder / "dcm2niix_done"
            subprocess.run(["touch", flag.resolve()])

    print("\nNIFTI conversion step checked and completed.\n\n\n")
    return output_folder


def parse_files(folder, keywords, exclude='survey'):
    file_dic = []
    folder = Path(folder)


    ''' rename files with trailing zeros if needed. (e.g. 'file_12.nii' -> 'file_012.nii', 'file_3.json' -> 'file_003.json') '''
    for file in folder.rglob('*'): 
        if file.suffix == '.json' or file.suffix == '.nii':
            if file.stem[-3] == '_':
                new = file.parents[0]/''.join([file.stem[:-2],file.stem[-2:].zfill(3),file.suffix])
                print(f'\nrenaming file with trailing zeros:\n{file}\n{new}\n ')
                file.rename(new)
                
            elif file.stem[-2] == '_':
                new = file.parents[0]/''.join([file.stem[:-1],file.stem[-1:].zfill(3),file.suffix])
                print(f'\nrenaming file with trailing zeros:\n{file}\n{new}\n ')
                file.rename(new)



    """ Search for keywords to filter data with 
        and
        Make sure the NIFTI and JSON files correspond to each other 
    """
    for keword in keywords:
        nii_key=f"*{keword}*.nii"
        json_key=f"*{keword}*.json"
        
        for (nifti, json) in zip( sorted(folder.rglob(nii_key)), sorted(folder.rglob(json_key)) ):
            if exclude in nifti.stem.lower(): # Get rid of unwanted files
                continue
            elif nifti.stem == json.stem:
                file_dic.append({"nifti": nifti, "json": json})
            else:
                raise Exception(
                    f"NIFTI and JSON files do NOT match:\nNIFTI: {nifti.name}\nJSON:  {json.name}"
                )
        

    """ Make sure the NIFTIs correspond to the 1st and 2nd scans of the sequence (not from other sequences) 
    """
    itr = iter(file_dic)
    file_dic2 = []
    run_through= round(len(file_dic) / 2)
    if len(file_dic)%2 != 0:
        run_through=run_through-1

    for i in range(run_through):
        f1 = next(itr)
        f2 = next(itr)

        f1stem = f1["nifti"].stem
        f2stem = f2["nifti"].stem
        suffix_index = f2stem.rfind("_")
        f1_nosuffix = f1stem[0:suffix_index]
        f2_nosuffix = f2stem[0:suffix_index]



        ''' TO IMPLEMENT: Fix PBT naming mismatch by ignoring the additional number: 
        WIP_Head_DQA_2dynamics_20210406122325_202002_t110000
        when "StationName": "PHILIPS-499QHGT" '''
        # if self.j1['StationName'] == 'MRC25326':
        #     try:
        #         print(f'Excluding the top 3 slices of {self.name} (MR2 data).')
        #         i1_trimmed = self.i1.get_fdata()[:,:,0:-3]
        #         i2_trimmed = self.i2.get_fdata()[:,:,0:-3]
        #         self.i1 = image.new_img_like(self.i1, i1_trimmed)
        #         self.i2 = image.new_img_like(self.i2, i2_trimmed)
        #     except:
        #         print(f'Unable to exclude top slices. Clue: check {self.name} is multislice (there should be 11 slices)' )    
        

        if f1["nifti"] != f2["nifti"] and  f1_nosuffix == f2_nosuffix:
            file_dic2.append(
                {
                    "nifti1": f1["nifti"],
                    "nifti2": f2["nifti"],
                    "json1": f1["json"],
                    "json2": f2["json"],
                }
            )

        else:
            nif1 = f1["nifti"]
            nif2 = f2["nifti"]
            raise Exception(
                f"1st and 2nd NIFTI files do NOT match:\n1st NIFTI: {nif1.name}\n2nd NIFTI: {nif2.name}"
            )

    print(f"Files for {len(file_dic2)} SNR tests identified:")
    for test, files in enumerate(file_dic2):
        n1 = files["nifti1"]
        n2 = files["nifti2"]
        print(f"SNR test number {test+1}:")
        print(f"1st nifti: {n1.name}\n2nd nifti: {n2.name}")
        print(" ")
    return file_dic2


class SNR_test:
    """SNR_test class computes SNR test from two nilean images (substraction method). 
    """

    def __init__(self, files):
        """[summary]

        Keyword Arguments:
            i1 {[nilean image]} -- [1st volume] (default: {i1})
            i2 {[nilean image]} -- [2nd volume] (default: {i2})
        """
        self.script_version = 0.6
        self.im1_path = files["nifti1"]
        im2_path = str(files["nifti2"])
        j1 = str(files["json1"])
        name = str(files["nifti1"].stem)
        # self.name = name[0 : name.find("_DQA")]
        self.name = name[0 : name.find("_SNR")]
        # self.name = name[0 : name.find("_routine")]
        
# 
        self.i1 = image.load_img(str(self.im1_path))
        self.i2 = image.load_img(im2_path)
        self.j1 = self.load_json(j1)
    






        ''' remove the top 3 slices in MR2 data'''
        if self.j1['StationName'] == 'MRC25326':
            try:
                print(f'Excluding the top 3 slices of {self.name} (MR2 data).')
                i1_trimmed = self.i1.get_fdata()[:,:,0:-3]
                i2_trimmed = self.i2.get_fdata()[:,:,0:-3]
                self.i1 = image.new_img_like(self.i1, i1_trimmed)
                self.i2 = image.new_img_like(self.i2, i2_trimmed)
            except:
                print(f'Unable to exclude top slices. Clue: check {self.name} is multislice (there should be 11 slices)' )    
        






        self.calc_global_SNR()
        self.calc_nSNR()
        self.create_results_df()
        # self.calc_SNR_map()

    def load_json(self, jfile):
        with open(jfile) as f:
            j = js.load(f)
            j = json_normalize(j)
        return j.transpose().to_dict()[0]

    def calc_SNR(self, signal, noise):
        signal[signal == 0] = np.nan
        #         noise[signal==0]=np.nan
        # sig=np.nanmean(signal)
        sig=np.nanmedian(signal)
        noise_std=np.nanstd(noise) 
        SNR = sig / noise_std / np.sqrt(2)
        SNR_std = np.nanstd(signal) / noise_std / np.sqrt(2)
        return SNR, SNR_std, noise_std

    def calc_global_SNR(self):
        self.imean = image.mean_img([self.i1, self.i2])
        self.isub = image.math_img("(i2 - i1)", i1=self.i1, i2=self.i2)
        
        self.mask = masking.compute_epi_mask(self.imean)
        if not self.mask.get_fdata().any():
            im = self.imean.get_fdata()[:,:,0]
            thresh = filters.threshold_otsu(im)
            binary = im > thresh
            mask2 = self.imean.get_fdata().copy()
            mask2[:,:,0]=binary
            self.mask = image.new_img_like(self.imean, mask2)

        mean = masking.apply_mask(self.imean, self.mask)
        sub = masking.apply_mask(self.isub, self.mask)
        self.SNR_global, self.SNR_global_std, self.noise_std= self.calc_SNR(mean, sub)

    def calc_nSNR(self):
        # Slice_fact=1000*nfe*npe/(fovFE*fovPE*slide_thk)/sqrt(npe*TR);
        # nbw=sqrt(bw/30)
        # nSNR=SNR*nbw*Slice_fact
        info = self.j1
        try:
            npe = info["PhaseEncodingSteps"]
        except:
            npe = info["AcquisitionMatrixPE"]


        nfe = int(np.round(100 * npe / info["PercentSampling"]))
        self.sl_thk = info["SliceThickness"]
        self.TR = info["RepetitionTime"]
        if self.TR>3:
            self.TR = info["RepetitionTimeExcitation"]
            
        pdims = self.i1.header["pixdim"]
        self.recon_matrix = info["ReconMatrixPE"]
        pdim1 = (
            self.recon_matrix / nfe * pdims[1]
        )  # Acquired pixel width (pre-reconstruction)
        pdim2 = self.recon_matrix / npe * pdims[2]
        pdim3 = self.sl_thk
        self.acquisiton_matrix = (nfe, npe)
        self.acquisiton_pixdim = (pdim1, pdim2, pdim3)
        Slice_fact = 1000 / (pdim1 * pdim2 * pdim3) / np.sqrt(npe * self.TR)
        self.pixel_bandwidth = info["PixelBandwidth"]
        self.BW_KHz = (
            self.pixel_bandwidth * nfe / 1000
        )  # Or PixelBandwidth*info['ReconMatrixPE'] ?
        nBW = np.sqrt(self.BW_KHz / 30)
        # print(f"nBW: { nBW }, Slice_fact = {Slice_fact}\n")
        self.nSNR = self.SNR_global * nBW * Slice_fact
        self.nSNR_std = self.SNR_global_std * nBW * Slice_fact

    def create_results_df(self):
        results = {
            "Name": self.name,
            "NSNR": self.nSNR,
            "NSNR_std": self.nSNR_std,
            "SNR": self.SNR_global,
            "SNR_std": self.SNR_global_std,
            "noise_std": self.noise_std,
            "File": str(self.im1_path.stem),
            "AcquisitonMatrix": self.acquisiton_matrix,
            "AcquisitonPixdim": self.acquisiton_pixdim,
            "BW_KHz": self.BW_KHz,
            "ScriptVersion": self.script_version,
        }
        results_snr = results.items()
        results_snr_df = pd.DataFrame(data=results_snr).transpose()
        info = self.j1.items()
        info_df = pd.DataFrame(info).transpose()
        results_df = pd.concat([results_snr_df, info_df], axis=1)
        new_header = results_df.iloc[0]
        results_df = results_df[1:]
        results_df.columns = new_header
        file_name = f'DQA_Results{datetime.now().strftime("_%d%b%Y")}.csv'
        results_df.to_csv(self.im1_path.parent / file_name)
        self.results_df = results_df


        

    def df2mysql(self):
        self.results_df.to_sql(con=con, name='table_name_for_df', if_exists='replace', flavor='mysql')



    def calc_SNR_map(self):
        print(f'Generating SNR map. Please hold on...')
        mean = self.imean.get_fdata()
        sub = self.isub.get_fdata()

        mean_map = ndimage.generic_filter(mean,np.nanmean,size=[5,5,1])
        std_map = ndimage.generic_filter(sub,np.nanstd,size=[5,5,1])


        snr_map = mean_map/std_map
        # snr_map = image.new_img_like(self.imean, snr_map)
        # snr_map = masking.apply_mask(snr_map, self.mask)
        # snr_map = snr_map.get_fdata()

        fig = px.imshow(mean.transpose(), facet_col=0, binary_string=False, facet_col_wrap=6)
        fig.show()
        fig = px.imshow(std_map.transpose(), facet_col=0, binary_string=False, facet_col_wrap=6)
        fig.show()
        fig = px.imshow(snr_map.transpose(), facet_col=0, binary_string=False, facet_col_wrap=6)
        fig.show()
        print(f'SNR map completed.')


    def plot(self, out_file="SNR_roi.png"):
        # prod=image.math_img("(i2 * i1)", i1=self.mask, i2=self.imean)
        # html_view = plotting.view_img(prod, bg_img=self.imean, resampling_interpolation='linear',colorbar=False, title=f'{self.name}: nSNR={int(np.round(self.nSNR))}')
        # html_view.open_in_browser()
        plotting.plot_roi(
            self.mask,
            self.imean,
            draw_cross=False,
            output_file=out_file,
            display_mode="tiled",
            title=f"{self.name}: nSNR={int(np.round(self.nSNR))}",
        )

