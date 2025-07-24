# greenhouse_m5
Notebooks for processing data from the NPEC greenhouse (Module 5)

Notebook list:
planteye.ipynb
snapscan_preprocessing.ipynb

# planteye
# snapscan_preprocessing
This notebook processes hyperspectral ENVI images to segment green leaves, extract their spectral information, and save visual and quantitative results. 

For each image in the specified folder, it loads the data, crops the image to just include the plant, and applies a segmentation algorithm that identifies green leaf pixels. 

The code then calculates the average and standard deviation of the spectra for those pixels, and saves both the segmentation mask and an NDVI image as PNG files. Finally, it compiles the results for all images into an Excel spreadsheet, including the filename, average spectra, and standard deviation per wavelength, enabling further analysis or visualization.
