from typing import Sequence, Tuple, Optional, Dict, Any, Callable, Union

import warnings
import numpy as np
import skimage.exposure
import skimage.transform

from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.interpolation import map_coordinates
from scipy.ndimage.morphology import distance_transform_edt


from elektronn3.data.transforms import random_blurring
from elektronn3.data.transforms.random import Normal, HalfNormal, RandInt

import vigra as v
from scipy import ndimage as im


Transform = Callable[
    [np.ndarray, Optional[np.ndarray]],
    Tuple[np.ndarray, Optional[np.ndarray]]
]



class LSDGaussVdtCom:
    
        """Generates LSD for a segmented dataset with 10 channels"""
        def __init__(
            self,
            #func: Callable[[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]
    ):
        #self.func = func
        self.vdtTransformer = v.filters.boundaryVectorDistanceTransform
        self.gaussDiv = v.filters.gaussianDivergence
        self.labeller = im.label

    def __call__(
            self,
            inp: np.ndarray,
            target: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        
        vtarget = v.VigraArray(target, axistags = v.defaultAxistags('czyx'))
        #vector distance transform and norm
        vdt_target = self.vdtTransformer(vtarget.astype(np.uint32))
        vdt_norm_target = np.linalg.norm(vdt_target, axis=0)

        gauss_target = self.gaussDiv(vtarget)

        #center of mass transform
        labels = self.labeller(vtarget)[0]
        #print("labels: {}".format(labels))
        #print(np.nonzero(np.unique(labels)))
        
        com = np.array(im.measurements.center_of_mass(vtarget, labels,np.unique(labels)[1:]))
        #print("Center of masses type: {}".format(type(com)))
        #print("Centers of mass: \n{}".format(com))
        
        shape = vtarget.shape
        coords = np.mgrid[:shape[0], :shape[1], :shape[2]]
        coords[:, vtarget==0]=0
        com_lsd = np.copy(coords).astype(float)
        for i in np.unique(labels)[1:]:
            com_lsd[:, labels==i] = np.tile(com[i-1].reshape(-1,1), com_lsd[:, labels==i].shape[1])

        #now stack everything on top along 0th axis to form the 10D LSD
        output = np.stack((vdt_target, vdt_norm_target, gauss_target, com_lsd))
        return (inp, output)

