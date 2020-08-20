from pathlib import Path
import numpy as np
from datetime import datetime
from nilearn import plotting, image, masking
import pandas as pd
import subprocess
import json as js
from pandas import json_normalize


def convert2NIFTI(base_folder=Path.home() / "Sync/MRdata/Avanto_MR2", **kwargs):
    now = datetime.now()
    base_folder = Path(base_folder)

    # output_folder = kwargs.get('output_folder', 'NIFTI')
    default_outdir = str(
        base_folder / f'Results{now.strftime("_%d%b%Y")}' / "DQA_NIFTIs"
    )

    output_folder = kwargs.get("output_folder", default_outdir)
    dcm2niix_path = kwargs.get("dcm2niix_path", "dcm2niix")
    dcm2niix_flag = kwargs.get(
        "dcm2nixx_flag", False
    )  # Set dcm2nixx_flag=True to skip redoing the NIFTI conversion. (Creates an empty file 'dcm2niix_done' in every folder were dcm2niix was used).

    print("\nChecking if DICOM to NIFTI conversion is needed...\n")
    # get the testfolders in the base_folder (single child)
    testfolders = [
        folder for folder in sorted(base_folder.glob("*")) if folder.is_dir()
    ]
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
                dcm2niix_path,
                "-f %f_%p_%t_%s",
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


def parse_files(folder):
    file_dic = []
    folder = Path(folder)

    """ Make sure the NIFTI and JSON files correspond to each other 
    """
    for (nifti, json) in zip(
        sorted(folder.rglob("*DQA*.nii")), sorted(folder.rglob("*DQA*.json"))
    ):
        if nifti.stem == json.stem:
            file_dic.append({"nifti": nifti, "json": json})
        else:
            raise Exception(
                f"NIFTI and JSON files do NOT match:\nNIFTI: {nifti.name}\nJSON:  {json.name}"
            )

    """ Make sure the NIFTIs correspond to the 1st and 2nd scans of the sequence (not from other sequences) 
    """
    itr = iter(file_dic)
    file_dic2 = []
    for i in range(round(len(file_dic) / 2)):
        f1 = next(itr)
        f2 = next(itr)

        f2stem = f2["nifti"].stem
        suffix_index = f2stem.rfind("_")
        f2_nosuffix = f2stem[0:suffix_index]

        if f1["nifti"] != f2["nifti"] and f1["nifti"].stem == f2_nosuffix:
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
        self.name = name[0 : name.find("_DQA")]
        self.i1 = image.load_img(str(self.im1_path))
        self.i2 = image.load_img(im2_path)
        self.j1 = self.load_json(j1)
        self.calc_global_SNR()
        self.calc_nSNR()
        self.create_results_df()

    def load_json(self, jfile):
        with open(jfile) as f:
            j = js.load(f)
            j = json_normalize(j)
        return j.transpose().to_dict()[0]

    def calc_SNR(self, signal, noise):
        signal[signal == 0] = np.nan
        #         noise[signal==0]=np.nan
        SNR = np.nanmean(signal) / np.nanstd(noise) / np.sqrt(2)
        SNR_std = np.nanstd(signal) / np.nanstd(noise) / np.sqrt(2)
        return SNR, SNR_std

    def calc_global_SNR(self):
        self.imean = image.mean_img([self.i1, self.i2])
        self.isub = image.math_img("(i2 - i1)", i1=self.i1, i2=self.i2)
        self.mask = masking.compute_epi_mask(self.imean)
        imean = masking.apply_mask(self.imean, self.mask)
        isub = masking.apply_mask(self.isub, self.mask)
        self.SNR_global, self.SNR_global_std = self.calc_SNR(imean, isub)

    def calc_nSNR(self):
        # Slice_fact=1000*nfe*npe/(fovFE*fovPE*slide_thk)/sqrt(npe*TR);
        # nbw=sqrt(bw/30)
        # nSNR=SNR*nbw*Slice_fact
        info = self.j1
        npe = info["PhaseEncodingSteps"]
        nfe = int(np.round(100 * npe / info["PercentSampling"]))
        self.sl_thk = info["SliceThickness"]
        self.TR = info["RepetitionTime"]
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
        self.nSNR = self.SNR_global * nBW * Slice_fact
        self.nSNR_std = self.SNR_global_std * nBW * Slice_fact

    def create_results_df(self):
        results = {
            "Name": self.name,
            "NSNR": self.nSNR,
            "NSNR_std": self.nSNR_std,
            "SNR": self.SNR_global,
            "SNR_std": self.SNR_global_std,
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

    def calc_SNR_map(self):
        pass

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
