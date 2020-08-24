

# Running a Daily QA Test




The purpose of the DQA tests is to acquire data from MR coils on a regular basis to monitor their performance and alert of potential issues ahead of time. These tests are meant to be short and easy to reproduce so that they can be run with minimal impact to the daily workload.

*A single time-point measurement is useless out of context, please run the DQA tests regularly*.
## Acquisition

The DQA tests are based on the aquisition of a simple volumentric SpinEcho data with **2 dynamics** (repetitions).  
But bare in mind that for the DQA tests to be effective they have to be: 
* Consistent
    * Always use the same test phantoms 
    * Use the same scan parameters for consecutive tests, e.g.:   
TR  = 1000 ms   
TE = 30 ms   
BW = 130 Hz/Pix  
Image Filters: **off**   
Distortion Correction: on 
*	Quick&Easy to run (~5min)
    * Use small a Matrix Size (<t>&le;</t>256x256)
    * Use a TSE multi-slice sequence to keep the scan time under control but keep a short echo-train length (e.g. ETL=3).
*	Cover a wide sensitive volume 
    * e.g. for the spine elements the FOV covers the entire bottle-phantom volume, with multiple 5mm thick slices.



## Positioning the test phantoms
The test phatoms, which would normally be provided by the manufacturer (standard mineral oil bottles or more speficic phatoms for dedicated coils), should be placed in the centre of the coil's sensitive volume and scanned at the isocentre of the scanner.  

See sections below for examples on how to position the test phantom on different systems.

* [UCLH Radio Therapy](RT.md) (Philips Ingenia Ambition X) 
 




## Labeling the acquisitions
In order to automatically identify the DICOM files with the corresponding DQA datasets, the scans should be labelled using this *'Coil_Name_DQA'* pattern. Here are a few examples:
- When testing the head element of a Head&Neck coil label the acquisition as:    **HN_Head_DQA...** 
- For the anterior part of a BodyMatrix coil: **BM_Anterior_DQA...**
- For a Large FlexCoil: **Flex_L_DQA...**

The data processing scrip will use the text *before* '_DQA' as the coil name. (You can add any descriptive comment after '_DQA' for the acquisition, but it wont be used as the coil name in the code). 
<br/>

##  Good practices for best results

![](media/flow.png) 
*Visible flow patterns due to liquid moving inside the phantom. Wait a bit longer before starting the acquisition.* 

<br/>

![](media/no_flow.png)
*The liquid has now stopped moving and you are ready to scan.*



<br/>


* Every time a phantom is positioned, **wait 2 minutes before starting the acquisition** to allow the fluid inside the phantom to stop moving.  
* Allow **10s recovery between the dynamic scans**.  
* Check that the **correct coil elements** are selected (if necessary unclick *smart coil selection*).  
* Run the scans with **no parallel imaging** (no SENSE or GRAPPA).
* When testing similar coils (e.g. multiple flex coils, anterior, posterior elements) make sure to give each coil its own **unique tag**.   
* Export the data as ‘Single Frame’ DICOMS.
* **Save the protocol** so it is easy to reproduce.




