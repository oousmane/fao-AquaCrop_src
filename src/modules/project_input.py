import os
import numpy as np
from ._global import *
from . import _global as G
from typing import Optional
from dataclasses import dataclass

def allocate_project_input(NrRuns):
    # Simply (re)allocates the ProjectInput module variable,
    global ProjectInput
    G.ProjectInput = [ProjectInput_type() for _ in range(NrRuns)]
    ProjectInput = G.ProjectInput

def ReadNumberSimulationRuns(TempFileNameFull):
    # Reads the project file to get the total number of runs.

    NrRuns = 1

    with open(ResolvePath(TempFileNameFull.strip()), "r") as fhandle:
        lines = fhandle.read().splitlines()

    NrFileLines = 42  # Clim(15),Calendar(3),Crop(3),Irri(3),Field(3),Soil(3),Gwt(3),Inni(3),Off(3),FieldData(3)

    idx = 0

    if idx >= len(lines):
        return NrRuns
    idx += 1  # Description

    if idx >= len(lines):
        return NrRuns
    idx += 1  # AquaCrop version Nr

    for i in range(1, 5 + 1):
        if idx >= len(lines):
            return NrRuns
        idx += 1  # Type year and Simulation and Cropping period Run 1

    for i in range(1, NrFileLines + 1):
        if idx >= len(lines):
            return NrRuns
        idx += 1  # Files Run 1

    while True:
        block = NrFileLines + 5
        if idx + block > len(lines):
            break
        idx += block
        NrRuns += 1

    return NrRuns


def initialize_project_input(filename, NrRuns=None):
    # Initializes the ProjectInput module variable,
    # if it has not yet been allocated.

    # PRM or PRO file name

    # total number of runs (if known beforehand)

    global ProjectInput

    if NrRuns is not None:
        NrRuns_local = NrRuns
    else:
        NrRuns_local = ReadNumberSimulationRuns(filename)

    allocate_project_input(NrRuns_local)

    for i in range(1, NrRuns_local + 1):
        ProjectInput[i - 1].read_project_file(filename, i)
