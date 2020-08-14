

# Running a Daily QA Test




The purpose of the DQA test is to acquire data from MR coils on a regular basis to monitor performance and alert of potential issues ahead of time.  
These tests are meant to be short and easy to reproduce so that they can be run without disrupting the daily clinical workload.

*As each DQA test provides a single time-point measurement, it is important to run them regularly.* 

## Acquisition

In order for the DQS tests to be effective they should be: 
1. Consistent (i.e. same phantom & sequence parameters for each test in the same system).
    * Use a TSE multi-slice sequence with a short echo-train length, e.g. 3.
    * Use the same scan parameters for consecutive tests, e.g.:   
TR  = 1000 ms   
TE = 30 ms   
BW = 130 Hz/Pix  
Image Filters: **off**   
distortion correction: **on** 
2.	Quick&Easy to run (<5min).
3.	Cover a wide sensitive volume (e.g. for the spine elements the FOV covers the entire bottle phantom volume). 
4.	Produce similar images per slice (e.g. sagittal scan for the foot phantom, coronal scan for breast phantom). 

  

 




## Labeling of acquisitions
In order to automatically identify the DICOM files with to the corresponding DQA datasets, the scans should be labelled using this *'Coil_Name_DQA'* pattern, e.g:
- When testing the head elements of a Head&Neck coil label the acquisition as:    **HN_Head_DQA...** 
- For the anterior part of a BodyMatrix coil: **BM_Anterior_DQA...**
- For a Large FlexCoil: **Flex_L_DQA...**

The data processing scrip will use the description before 'DQA' as the coil name. (You can add any descriptive comment *after* 'DQA' the acquisition, but this wont be used as the coil name in the code).

##  Notes
    
* Allow 10s recovery between the dynamic scans acquisitions.  
* Every time a phantom is positioned, wait for a couple of minutes before starting the acquisition to allow the fluid to stop moving inside the phantom.  
* Check that the correct coil elements are selected (if necessary unclick smart coil selection).  
* In the Geometry tab set ‘Homogeneity correction=none‘ and ‘Clear=No’ to reduce smoothing/filtering of signal.    
* For identical coils (e.g. flex coils, anterior, posterior elements) make a note of the serial number.   
* Export the data as ‘Single Frame’ DICOMS.
