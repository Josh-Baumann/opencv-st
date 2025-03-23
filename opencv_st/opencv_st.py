from typing import Callable, Any
from enum import Enum
import streamlit as st
import cv2
from PIL import Image
import numpy as np

from cvarg import CvArg, CvInt, CvTuple, CvEnum, CvBool

st.set_page_config(layout="wide")


class ImageProcess:
    def __init__(self, func: Callable, args: list[CvArg]):
        self.name = func.__name__
        self._func = func
        self._args = args

    def run(self, image):
        tmp = {}
        for arg in self._args:
            if isinstance(arg, CvArg):
                tmp[arg.name] = arg.get()
            else:
                raise RuntimeError("Invalid argument type")
        return self._func(image, **tmp)


class ProcessContainer:
    def __init__(self, proc: ImageProcess, image: np.ndarray):
        self.name = proc.name
        self.proc = proc
        self.image = image
        self._args = proc._args
        with st.container(border=True):
            st.header(self.name)
            self.left, self.right = st.columns(2, vertical_alignment="center")

    def make_ux(self):
        for arg in self._args:
            if isinstance(arg, CvArg):
                arg.value = arg.ux(self.right)
            else:
                raise RuntimeError("Invalid argument type")

    def run(self):
        self.image = self.proc.run(self.image)

    def display(self):
        self.left.image(self.image, clamp=True)


color_flags = [
    i for i in dir(cv2) if i.startswith("COLOR_") and not "BAYER" in i.upper()
]
color_values = [getattr(cv2, flag) for flag in color_flags]
my_dict = {key: value for key, value in zip(color_flags, color_values)}
gray = ImageProcess(
    cv2.cvtColor,
    [
        CvEnum(
            "code",
            cv2.COLOR_RGB2GRAY,
            my_dict,
            help="Color conversion code",
        )
    ],
)

blur = ImageProcess(
    cv2.GaussianBlur,
    [
        CvTuple("ksize", (5, 5), range=(1, 255), step=2, help="Kernel size"),
        CvInt("sigmaX", 0, range=(0, 10), step=1, help="Standard deviation in X"),
        CvInt("sigmaY", 0, range=(0, 10), step=1, help="Standard deviation in Y"),
    ],
)

lines = ImageProcess(
    cv2.HoughLinesP,
    [
        CvInt(
            "rho",
            1,
            range=(1, 10),
            step=1,
            help="Distance resolution of the accumulator in pixels.",
        ),
        CvInt(
            "theta",
            1,
            range=(1, 10),
            step=1,
            help="Angle resolution of the accumulator in radians.",
        ),
        CvInt(
            "threshold",
            100,
            range=(1, 1000),
            step=1,
            help="Accumulator threshold parameter.",
        ),
        CvInt(
            "minLineLength",
            100,
            range=(1, 1000),
            step=1,
            help="Minimum line length. Line segments shorter than this are rejected.",
        ),
        CvInt(
            "maxLineGap",
            10,
            range=(1, 1000),
            step=1,
            help="Maximum allowed gap between points on the same line to link them.",
        ),
    ],
)

dilate = ImageProcess(
    cv2.dilate,
    [
        CvTuple("kernel", (5, 5), range=(1, 255), step=2, help="Kernel size"),
        CvInt("iterations", 1, range=(1, 10), step=1, help="Number of iterations"),
    ],
)

edges = ImageProcess(
    cv2.Canny,
    [
        CvInt("apertureSize", 3, range=(3, 7), step=2, help="Aperture size"),
        CvInt("threshold1", 100, range=(1, 255), step=1, help="First threshold"),
        CvInt("threshold2", 200, range=(1, 255), step=1, help="Second threshold"),
        CvBool("L2gradient", False, help="Use L2 norm for gradient calculation"),
    ],
)


def _new_container(proc, cv_image):
    container = ProcessContainer(proc, cv_image)
    container.make_ux()
    container.run()
    container.display()
    return container.image


def main():
    uploaded_file = st.file_uploader("Choose an image...", type="png")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")
        cv_image = np.array(image)

        processes = [gray, dilate, edges]
        for proc in processes:
            cv_image = _new_container(proc, cv_image)


if __name__ == "__main__":
    main()
