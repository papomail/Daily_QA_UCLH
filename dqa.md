

# Running a Daily QA Test




The purpose of the DQA test is to acquire data from MR coils on a regular basis to monitor performance and alert of potential issues ahead of time.  
These tests are meant to be short and easy to reproduce so that they can be run with minimal impact to the daily workload.

*As each DQA test provides a single time-point measurement, it is important to run them regularly.* 

## Acquisitions

In order for the DQA tests to be effective they should be: 
* Consistent (i.e. use the same phantom & sequence parameters for each test in the same system).
    * Use a TSE multi-slice sequence with a short echo-train length, e.g. 3.
    * Use the same scan parameters for consecutive tests, e.g.:   
TR  = 1000 ms   
TE = 30 ms   
BW = 130 Hz/Pix  
Image Filters: **off**   
Distortion Correction: on 
*	Quick&Easy to run (<5min).
*	Cover a wide sensitive volume (e.g. for the spine elements the FOV covers the entire bottle phantom volume). 
*	Produce similar images per slice (e.g. sagittal scan for the foot phantom, coronal scan for breast phantom).  See section below.



## Positioning the test phantoms

 




## Labeling the acquisitions
In order to automatically identify the DICOM files with to the corresponding DQA datasets, the scans should be labelled using this *'Coil_Name_DQA'* pattern, e.g:
- When testing the head elements of a Head&Neck coil label the acquisition as:    **HN_Head_DQA...** 
- For the anterior part of a BodyMatrix coil: **BM_Anterior_DQA...**
- For a Large FlexCoil: **Flex_L_DQA...**

The data processing scrip will use the text *before* '_DQA' as the coil name. (You can add any descriptive comment after '_DQA' for the acquisition, but it wont be used as the coil name in the code).

##  Notes
    
* Allow **10s recovery between the dynamic scans** acquisitions.  
* Every time a phantom is positioned, **wait 2 minutes before starting the acquisition** to allow the fluid inside the phantom to stop moving.  
* Check that the correct coil elements are selected (if necessary unclick *smart coil selection*).  
* Run the scans with **no parallel imaging** (eg. SENSE or GRAPPA).
* When testing similar coils (e.g. multiple flex coils, anterior, posterior elements) make sure to give each coil its own identifiable tag.   
* Export the data as ‘Single Frame’ DICOMS.
* **Save the protocol** so it is easy to reproduce.


