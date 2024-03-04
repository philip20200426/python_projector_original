import os
import sys
from ctypes import CDLL
from ctypes import *

from Constants import DIR_EVAL_ALGO

CALIB_DATA_PATH = 'asuFiles/interRefFiles/ex_cam_correct.yml'
sys.path.append("algo")
dll = None
try:
    if os.path.exists(DIR_EVAL_ALGO):
        dll = CDLL(DIR_EVAL_ALGO, winmode=0)
        print('Load evaluate_correction.dll')
    else:
        print('No found ', DIR_EVAL_ALGO)
except OSError:
    print('Load  error.', DIR_EVAL_ALGO)

# //output
# //  A|B
# // --|--
# //  C|D
# // dst[0] horizontal(UpDown) distortion error
# // dst[1] vertical(LeftRight) distortion error
# // dst[2] angle1
# // dst[3] angle2
# // dst[4] angle3
# // dst[5] angle4
# // dst[6] horizontal tilt
# // return 0 :ok else error
# EVA_CORRECTION_LIB_API int EvaluateCorrectionRst(const char* calib_data_path, const int img_r, const int img_c, const unsigned char* pattern_img,
# 	double* dst);
if hasattr(dll, 'EvaluateCorrectionRst'):
    def evaluate_correction_rst(img_size,
                                img,
                                dst):
        dll.EvaluateCorrectionRst.argtypes = [c_char_p,
                                              c_int, c_int,
                                              POINTER(c_ubyte),
                                              POINTER(c_double)]
        dll.EvaluateCorrectionRst.restype = c_int
        calib_data_path = create_string_buffer(CALIB_DATA_PATH.encode('utf-8'))
        img_r = c_int(img_size[0])
        img_c = c_int(img_size[1])
        ret_dst = (c_double * len(dst))(*list(map(float, dst)))
        ret = dll.EvaluateCorrectionRst(calib_data_path,
                                        img_r, img_c,
                                        img.ctypes.data_as(POINTER(c_ubyte)),
                                        ret_dst)
        for i in range(len(ret_dst)):
            dst[i] = ret_dst[i]
        return ret
