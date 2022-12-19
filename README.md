# Compute Color Correction Matrix (CCM)
We compute Color Correction Matrix A.
In other words, we calculate a 4x3 matrix A which approximate the following equation.  

Let P be a reference color checker matrix (24 x 3) and O be a color checker 
matrix to correct (24 x 3).  
`P = [O 1] A`

## Dependency
- Python
    - numpy
    - matplotlib
    - Pillow 

## Usage
``` shell 
# python computeCCM.py reference_csv source_csv output_csv
```
This command generates optimal Color Correction Matrix as csv file (`ccm.csv`)

# References

* RGB coordinates of the Macbeth ColorChecker, Danny Pascale. June 1st, 2006 version. http://www.babelcolor.com/index_htm_files/RGB%20Coordinates%20of%20the%20Macbeth%20ColorChecker.pdf
* Color Correction Matrix http://www.imatest.com/docs/colormatrix/
* Raw-to-raw: Mapping between image sensor color responses. CVPR 2014. https://www.cv-foundation.org/openaccess/content_cvpr_2014/papers/Nguyen_Raw-to-Raw_Mapping_between_2014_CVPR_paper.pdf
