mkdir -p tests/assets/downloaded
wget "https://github.com/datalad/example-dicom-structural/blob/master/dicoms/N2D_0001.dcm?raw=true" -O tests/assets/downloaded/file.dcm
#wget https://github.com/mathiasbynens/small/raw/master/png-transparent.png -O tests/assets/downloaded/file.png
#wget https://nifti.nimh.nih.gov/nifti-1/data/minimal.nii.gz -O tests/assets/downloaded/file.nii.gz && gunzip tests/assets/downloaded/file.nii.gz
