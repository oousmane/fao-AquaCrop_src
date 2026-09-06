from ._global import _strip_quotes
import warnings

# Module: startunit.py

# List of functions:
#   GetListProjectsFile
#   GetNumberOfProjects
#   GetProjectFileName(iproject)

# List of subroutines:
#   fProjects_open(filename, mode)
#   fProjects_write(line, advance_in)
#   fProjects_close
#   GetRequestDailyResults
#   GetRequestParticularResults
#   GetTimeAggregationResults
#   GetProjectType(TheProjectFile, TheProjectType)
#   PrepareReport
#   InitializeTheProgram
#   InitializeProjectFileNames
#   InitializeProject(iproject, TheProjectFile, TheProjectType)
#   ComposeFileForProgramParameters(TheFileNameProgram, FullFileNameProgramParameters)
#   LoadProgramParametersProjectPlugIn(FullFileNameProgramParameters, ProgramParametersAvailable)
#   FinalizeTheProgram
#   WriteProjectsInfo(line)
#   StartTheProgram

import os
import numpy as np
from ._global import *
from .project_input import *
from .run import *
from .initialsettings import InitializeSettings
from .progresswindow import start_progress
from typing import Optional

fProjects = None
ProjectFileNames: Optional[list[str]] = None

# Función completa
def GetTimeAggregationResults():

    FullFileName: Optional[str] = None

    SetOutputAggregate(0)
    FullFileName = os.path.join(complete_path_dir, GetPathNameSimul().strip(), "AggregationResults.SIM")
    if os.path.isfile(FullFileName):
        try:
            with open(FullFileName, "r", encoding="utf-8", errors="ignore") as f:
                line = f.readline()
        except OSError:
            line = ""

        s = line.lstrip()
        SetOutputAggregate(int(s[0]))

# Función completa
def GetRequestDailyResults():

    FullFileName: Optional[str] = None

    SetOut1Wabal(False)
    SetOut2Crop(False)
    SetOut3Prof(False)
    SetOut4Salt(False)
    SetOut5CompWC(False)
    SetOut6CompEC(False)
    SetOut7Clim(False)
    SetOut8Irri(False)

    FullFileName = os.path.join(complete_path_dir, GetPathNameSimul().strip(), "DailyResults.SIM")
    if os.path.isfile(FullFileName):
        try:
            with open(FullFileName, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.lstrip()
                    if not line:
                        continue
                    c = line[0]

                    if c == '1':
                        SetOut1Wabal(True)
                    elif c == '2':
                        SetOut2Crop(True)
                    elif c == '3':
                        SetOut3Prof(True)
                    elif c == '4':
                        SetOut4Salt(True)
                    elif c == '5':
                        SetOut5CompWC(True)
                    elif c == '6':
                        SetOut6CompEC(True)
                    elif c == '7':
                        SetOut7Clim(True)
                    elif c == '8':
                        SetOut8Irri(True)
        except OSError:
            pass

    SetOutDaily(False)
    if (
        GetOut1Wabal() or
        GetOut2Crop() or
        GetOut3Prof() or
        GetOut4Salt() or
        GetOut5CompWC() or
        GetOut6CompEC() or
        GetOut7Clim()
    ):
        SetOutDaily(True)

# Función completa
def GetRequestParticularResults():

    FullFileName: Optional[str] = None

    SetPart1Mult(False)
    SetPart2Eval(False)

    FullFileName = os.path.join(complete_path_dir, GetPathNameSimul().strip(), "ParticularResults.SIM")
    if os.path.isfile(FullFileName):
        try:
            with open(FullFileName, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.lstrip()
                    if not line:
                        continue
                    c = line[0]

                    if c == '1':
                        SetPart1Mult(True)
                    elif c == '2':
                        SetPart2Eval(True)
        except OSError:
            pass

# Función completa
def fProjects_open(filename, mode):

    global fProjects
    try:
        fProjects = open(filename, mode)
    except OSError as exc:
        # Ne pas echouer silencieusement : sans ce signal, l'erreur ne se
        # manifeste que plus tard par un AttributeError sur fProjects.write
        warnings.warn(
            f"fProjects_open: impossible d'ouvrir {filename!r} ({exc.strerror})",
            RuntimeWarning,
            stacklevel=2,
        )
        fProjects = None

# Función completa
def fProjects_write(line, advance_in=None):

    global fProjects
    advance = True if advance_in is None else bool(advance_in)

    try:
        if advance:
            fProjects.write(line + "\n")
        else:
            fProjects.write(line)

        fProjects.flush()
    except OSError:
        pass

def fProjects_write_bulk(lines):
    global fProjects
    try:
        if not lines:
            return
        text = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
        fProjects.write(text)
        fProjects.flush()
    except OSError:
        pass


# Función completa
def fProjects_close():
    global fProjects
    if fProjects is not None:
        try:
            fProjects.close()
        except OSError:
            pass
    fProjects = None

# Función completa
def InitializeProjectFileNames() -> None:
    # Initializes the ProjectFileNames module variable array
    # by reading from a ListProjects.txt file.

    global ProjectFileNames

    ListProjectsFile = GetListProjectsFile()
    ListProjectFileExist = FileExists(os.path.join(complete_path_dir, ListProjectsFile))
    if ListProjectFileExist:
        with open(os.path.join(complete_path_dir, ListProjectsFile), "r", encoding="utf-8", errors="ignore") as f:
            ProjectFileNames = [line.strip() for line in f if line.strip()]
            
    else:
        # No project list file exists, so make a temporary one instead
        # from the available *.PRO and *.PRM files
        PathNameList = GetPathNameList()
        ListProjectsFileTemp = PathNameList[:-1] if PathNameList.endswith(os.sep) else PathNameList

        try:
            entries = os.listdir(ListProjectsFileTemp)
        except OSError as e:
            ProjectFileNames = []
            return

        ProjectFileNames = [
            name for name in entries
            if name.upper().endswith(".PRO") or name.upper().endswith(".PRM")
        ]

# Función completa
def GetNumberOfProjects():
    # Returns the total number of projects.
    global ProjectFileNames
    if ProjectFileNames is None:
        InitializeProjectFileNames()
    return len(ProjectFileNames)

# Función completa
def PrepareReport():

    # Report is not implemented yet
    fProjects_open(os.path.join(complete_path_dir, GetPathNameOutp().strip(), "ListProjectsLoaded.OUT"), "w")
    fProjects_write("Intermediate results: ", False)

    match GetOutputAggregate():
        case 1:
            fProjects_write("daily results")
        case 2:
            fProjects_write("10-daily results")
        case 3:
            fProjects_write("monthly results")
        case _:
            fProjects_write("None created")

    fProjects_write("")
    if GetOutDaily() or GetOut8Irri():
        fProjects_write("Daily output results:")
        if GetOut1Wabal():
            fProjects_write("1. - soil water balance")
        if GetOut2Crop():
            fProjects_write("2. - crop development and production")
        if GetOut3Prof():
            fProjects_write("3. - soil water content in the soil profile and root zone")
        if GetOut4Salt():
            fProjects_write("4. - soil salinity in the soil profile and root zone")
        if GetOut5CompWC():
            fProjects_write("5. - soil water content at various depths of the soil profile")
        if GetOut6CompEC():
            fProjects_write("6. - soil salinity at various depths of the soil profile")
        if GetOut7Clim():
            fProjects_write("7. - climate input parameters")
        if GetOut8Irri():
            fProjects_write("8. - irrigation events and intervals")
    else:
        fProjects_write("Daily output results: None created")

    fProjects_write("")
    if GetPart1Mult() or GetPart2Eval():
        fProjects_write("Particular results:")
        if GetPart1Mult():
            fProjects_write("1. - biomass and yield at multiple cuttings(for herbaceous forage crops)")
        if GetPart2Eval():
            fProjects_write("2. - evaluation of simulation results (when Field Data)")
    else:
        fProjects_write("Particular results: None created")

# Función terminada (POSIBLE BUG)
def WriteProjectsInfo(line):
    fProjects_write(line)

def GetProjectFileName(iproject):

    # Returns the project file name for the given project index.

    if ProjectFileNames is None:
        InitializeProjectFileNames()

    ProjectFileName_out = ProjectFileNames[iproject - 1].rstrip(' ')
    return ProjectFileName_out


def GetTotalSimulationRuns():
    total_runs = 0

    for iproject in range(1, GetNumberOfProjects() + 1):
        project_file = GetProjectFileName(iproject)
        project_type = GetProjectType(project_file)
        project_rel_path = os.path.join(GetPathNameList(), project_file)
        project_full_path = os.path.join(complete_path_dir, project_rel_path)

        if not FileExists(project_full_path):
            continue

        if project_type == typeproject_typepro:
            total_runs += 1
        elif project_type == typeproject_typeprm:
            try:
                total_runs += ReadNumberSimulationRuns(project_rel_path)
            except OSError:
                pass

    return total_runs

def InitializeTheProgram():

    # Decimalseparator = '.' GDL, 20220413, not used?
    SetPathNameOutp('OUTP/')
    SetPathNameSimul('SIMUL/')
    SetPathNameList('LIST/')
    SetPathNameParam('PARAM/')
    SetPathNameProg('')

    GetTimeAggregationResults()
    GetRequestDailyResults()
    GetRequestParticularResults()
    PrepareReport()

def GetListProjectsFile():
    return GetPathNameList() + "ListProjects.txt"

def GetProjectType(TheProjectFile: str):

    TheProjectType = typeproject_typenone

    lgth = len(TheProjectFile)
    if lgth > 0:
        i = 0 
        while (i < lgth) and (TheProjectFile[i] != '.'):
            i += 1

        if i == (lgth - 4):
            TheExtension = TheProjectFile[i+1:i+4].upper()  # 3 chars
            if TheExtension == 'PRO':
                TheProjectType = typeproject_typepro
            elif TheExtension == 'PRM':
                TheProjectType = typeproject_typeprm
            else:
                TheProjectType = typeproject_typenone

    return TheProjectType

def InitializeProject(iproject: int, TheProjectFile: str, TheProjectType: int):

    global typeproject_typepro

    NrString = TestFile = tempstring = ""
    FullFileNameProgramParametersLocal = ""
    CanSelect = ProgramParametersAvailable = MultipleRunWithKeepSWC_temp = True
    TotalSimRuns = SimNr = WrongSimNr = MultipleRunConstZrx_temp = 0
    FileOK = rep_FileOK()

    NrString = "{:8d}".format(iproject)
    CanSelect = True
    WrongSimNr = undef_int

    # Check if project file exists
    if TheProjectType != typeproject_typenone:
        TestFile = GetPathNameList() + TheProjectFile
        if not FileExists(os.path.join(complete_path_dir, TestFile)):
            CanSelect = False

    if TheProjectType != typeproject_typenone and CanSelect:
        # run the project after cheking environment and simumation files
        # 1. Set No specific project
        InitializeSettings(use_default_soil_file = True, use_default_crop_file = True)

        # select case(TheProjectType)
        if TheProjectType == typeproject_typepro:
            # 2. Assign single project file and read its contents
            SetProjectFile(TheProjectFile)
            SetProjectFileFull(GetPathNameList() + GetProjectFile())
            initialize_project_input(GetProjectFileFull(), NrRuns=1)

            # 3. Check if Environment and Simulation Files exist
            CanSelect = True
            CanSelect, FileOK = CheckFilesInProject(1, CanSelect, FileOK)

            # 4. load project parameters
            if CanSelect:
                SetProjectDescription("undefined")
                FullFileNameProgramParametersLocal = ComposeFileForProgramParameters(GetProjectFile())
                SetFullFileNameProgramParameters(FullFileNameProgramParametersLocal)
                ProgramParametersAvailable = LoadProgramParametersProjectPlugIn(
                    GetFullFileNameProgramParameters(),
                    ProgramParametersAvailable,
                )
                ComposeOutputFileName(GetProjectFile())
            else:
                WrongSimNr = 1  # 1_int32

        elif TheProjectType == typeproject_typeprm:
            # 2. Assign multiple project file and read its contents
            SetMultipleProjectFile(TheProjectFile)
            SetMultipleProjectFileFull(GetPathNameList() + GetMultipleProjectFile())
            initialize_project_input(GetMultipleProjectFileFull())

            # 2bis. Get number of Simulation Runs
            TotalSimRuns = GetNumberSimulationRuns()

            # 3. Check if Environment and Simulation Files exist for all runs
            CanSelect = True
            SimNr = 0  # 0_int32
            while CanSelect and (SimNr < TotalSimRuns):
                SimNr = SimNr + 1  # + 1_int32
                CanSelect, FileOK = CheckFilesInProject(SimNr, CanSelect, FileOK)
                if not CanSelect:
                    WrongSimNr = SimNr

            # 4. load project parameters
            if CanSelect:
                SetMultipleProjectDescription("undefined")
                FullFileNameProgramParametersLocal = ComposeFileForProgramParameters(GetMultipleProjectFile())
                SetFullFileNameProgramParameters(FullFileNameProgramParametersLocal)
                ProgramParametersAvailable = LoadProgramParametersProjectPlugIn(
                    GetFullFileNameProgramParameters(),
                    ProgramParametersAvailable,
                )
                ComposeOutputFileName(GetMultipleProjectFile())
                SetSimulation_MultipleRun(True)  # .true.
                SetSimulation_NrRuns(TotalSimRuns)
                MultipleRunWithKeepSWC_temp = GetSimulation_MultipleRunWithKeepSWC()     # Esta línea sobraría 
                MultipleRunConstZrx_temp = GetSimulation_MultipleRunConstZrx()          # Esta línea sobraría
                MultipleRunWithKeepSWC_temp, MultipleRunConstZrx_temp = CheckForKeepSWC()           
                SetSimulation_MultipleRunWithKeepSWC(MultipleRunWithKeepSWC_temp)
                SetSimulation_MultipleRunConstZrx(MultipleRunConstZrx_temp)
                                                 
        else:
            # default / unhandled project type
            pass

        # 5. Run
        if CanSelect:
            if ProgramParametersAvailable:
                tempstring = (
                    f"{NrString}. - {TheProjectFile.strip()}"
                    " : Project loaded - with its program parameters"
                )
                fProjects_write(tempstring)
            else:
                tempstring = (
                    f"{NrString}. - {TheProjectFile.strip()}"
                    " : Project loaded - default setting of program parameters"
                )
                fProjects_write(tempstring)
        else:
            lines_out = []

            tempstring = (
                f"{NrString}. - {TheProjectFile.strip()} : Project NOT loaded"
                " - Missing Environment and/or Simulation file(s) in Run number "
                f"{str(WrongSimNr)}: "
            )
            lines_out.append(tempstring)

            if not FileOK.Climate_Filename:
                lines_out.append("               Climate (CLI), ")
            if not FileOK.Temperature_Filename:
                lines_out.append("               Temperature (Tnx of TMP), ")
            if not FileOK.ETo_Filename:
                lines_out.append("               Reference ET (ETo), ")
            if not FileOK.Rain_Filename:
                lines_out.append("               Rainfall (PLU), ")
            if not FileOK.CO2_Filename:
                lines_out.append("               CO2 (CO2), ")
            if not FileOK.Calendar_Filename:
                lines_out.append("               Calendar (CAL), ")
            if not FileOK.Crop_Filename:
                lines_out.append("               Crop (CRO), ")
            if not FileOK.Irrigation_Filename:
                lines_out.append("               Irrigation (Irr), ")
            if not FileOK.Management_Filename:
                lines_out.append("               Field Management (MAN), ")
            if not FileOK.Soil_Filename:
                lines_out.append("               Soil profile (SOL), ")
            if not FileOK.GroundWater_Filename:
                lines_out.append("               Groundwater (GWT), ")
            if not FileOK.SWCIni_Filename:
                lines_out.append("               Initial conditions (SW0), ")
            if not FileOK.OffSeason_Filename:
                lines_out.append("               Off-season (OFF), ")
            if not FileOK.Observations_Filename:
                lines_out.append("               Field data (OBS), ")

            lines_out.append(
                "          - Check file Name(s), Path(s) or Structure of project file."
            )

            fProjects_write_bulk(lines_out)

            print("Missing Environment and/or Simulation file(s):")
            print("Check OUTP/ListProjectsLoaded.OUT for information.")
    else:
        # not a project file or missing in the LIST  dirtectory
        if CanSelect:
            tempstring = f"{NrString}. - {TheProjectFile.strip()} : is NOT a project file"
            fProjects_write(tempstring)
        else:
            tempstring = (
                f"{NrString}. - {TheProjectFile.strip()}"
                " : project file NOT available in LIST directory"
            )
            fProjects_write(tempstring)


def StartTheProgram():

    iproject, nprojects = 0, 0
    TheProjectType = 0
    ListProjectsFile = ""
    TheProjectFile = ""
    ListProjectFileExists = False

    InitializeGlobalStrings()
    InitializeTheProgram()

    ListProjectsFile = GetListProjectsFile()
    ListProjectFileExists = FileExists(os.path.join(complete_path_dir, ListProjectsFile))
    nprojects = GetNumberOfProjects()
    start_progress(GetTotalSimulationRuns())

    if nprojects > 0:
        WriteProjectsInfo("")
        WriteProjectsInfo("Projects handled:")

    for iproject in range(1, nprojects + 1):
        TheProjectFile = GetProjectFileName(iproject)
        TheProjectType = GetProjectType(TheProjectFile)
        InitializeProject(iproject, TheProjectFile, TheProjectType)
        RunSimulation(TheProjectFile, TheProjectType)

    if nprojects == 0:
        WriteProjectsInfo("")
        WriteProjectsInfo("Projects loaded: None")

        if ListProjectFileExists:
            WriteProjectsInfo('File "ListProjects.txt" does not contain ANY project file')
        else:
            WriteProjectsInfo('Missing File "ListProjects.txt" in LIST directory')

    FinalizeTheProgram()

def FinalizeTheProgram():
    fend = None

    fProjects_close()

    # all done
    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(GetPathNameOutp() + "AllDone.OUT").lstrip("/\\"),
        )
    )
    with open(full_path, "w", encoding="utf-8", errors="replace") as fend:
        fend.write("All done\n")

def LoadProgramParametersProjectPlugIn(FullFileNameProgramParameters, ProgramParametersAvailable):
    
    if FileExists(os.path.normpath(os.path.join(complete_path_dir, FullFileNameProgramParameters))):
        ProgramParametersAvailable = True

        with open(os.path.normpath(os.path.join(complete_path_dir, FullFileNameProgramParameters.strip()))) as f0:
            lines = f0.read().splitlines()

        idx = 0

        def next_token():
            nonlocal idx
            while idx < len(lines):
                s = lines[idx].strip()
                idx += 1
                if s != "":
                    return s.split()[0]
            return ""

        # crop
        simul_ed = int(next_token())  # evaporation decline factor in stage 2
        SetSimulParam_EvapDeclineFactor(simul_ed)

        simul_kcWB = float(next_token())  # Kc wet bare soil [-]
        SetSimulParam_KcWetBare(simul_kcWB)

        simul_pCCHIf = int(next_token())
        # CC threshold below which HI no longer increase(% of 100)
        SetSimulParam_PercCCxHIfinal(simul_pCCHIf)

        simul_RpZmi = int(next_token())
        # Starting depth of root sine function (% of Zmin)
        SetSimulParam_RootPercentZmin(simul_RpZmi)

        simul_RZEma = float(next_token())  # cm/day
        SetSimulParam_MaxRootZoneExpansion(simul_RZEma)

        SetSimulParam_MaxRootZoneExpansion(5.00)  # fixed at 5 cm/day

        simul_SFR = int(next_token())
        # Shape factor for effect water stress on rootzone expansion
        SetSimulParam_KsShapeFactorRoot(simul_SFR)

        simul_TAWg = int(next_token())
        # Soil water content (% TAW) required at sowing depth for germination
        SetSimulParam_TAWGermination(simul_TAWg)

        simul_pfao = float(next_token())
        # Adjustment factor for FAO-adjustment soil water depletion
        # (p) for various ET
        SetSimulParam_pAdjFAO(simul_pfao)

        simul_lowox = int(next_token())
        # number of days for full effect of deficient aeration
        SetSimulParam_DelayLowOxygen(simul_lowox)

        simul_expFsen = float(next_token())
        # exponent of senescence factor adjusting drop in
        # photosynthetic activity of dying crop
        SetSimulParam_ExpFsen(simul_expFsen)

        simul_beta = int(next_token())
        # Decrease (percentage) of p(senescence) once early
        # canopy senescence is triggered
        SetSimulParam_Beta(simul_beta)

        simul_Tswc = int(next_token())  # Thickness top soil (cm) in which
        # soil water depletion has to be determined
        SetSimulParam_ThicknessTopSWC(simul_Tswc)

        # field
        simul_EZma = int(next_token())
        # maximum water extraction depth by soil evaporation [cm]
        SetSimulParam_EvapZmax(simul_EZma)

        # soil
        simul_rod = float(next_token())
        # considered depth (m) of soil profile for calculation
        # of mean soil water content
        SetSimulParam_RunoffDepth(simul_rod)

        i = int(next_token())  # correction CN for Antecedent Moisture Class
        if i == 1:
            SetSimulParam_CNcorrection(True)
        else:
            SetSimulParam_CNcorrection(False)

        simul_saltdiff = int(next_token())  # salt diffusion factor (%)
        SetSimulParam_SaltDiff(simul_saltdiff)

        simul_saltsolub = int(next_token())  # salt solubility (g/liter)
        SetSimulParam_SaltSolub(simul_saltsolub)

        simul_root = int(next_token())  # shape factor capillary rise factor
        SetSimulParam_RootNrDF(simul_root)

        SetSimulParam_IniAbstract(5)
        # fixed in Version 5.0 cannot be changed since linked
        # with equations for CN AMCII and CN converions

        # Temperature
        simul_Tmi = float(next_token())
        # Default minimum temperature (degC) if no
        # temperature file is specified
        SetTmin(simul_Tmi)
        SetSimulParam_Tmin(simul_Tmi)

        simul_Tma = float(next_token())
        # Default maximum temperature (degC) if
        # no temperature file is specified
        SetTmax(simul_Tma)
        SetSimulParam_Tmax(simul_Tma)

        simul_GDD = int(next_token())  # Default method for GDD calculations
        SetSimulParam_GDDMethod(simul_GDD)

        if GetSimulParam_GDDMethod() > 3:
            SetSimulParam_GDDMethod(3)

        if GetSimulParam_GDDMethod() < 1:
            SetSimulParam_GDDMethod(1)

        # Rainfall
        i = int(next_token())
        if i == 0:
            SetSimulParam_EffectiveRain_Method(EffectiveRainMethod_Full)
        elif i == 1:
            SetSimulParam_EffectiveRain_Method(EffectiveRainMethod_USDA)
        elif i == 2:
            SetSimulParam_EffectiveRain_Method(EffectiveRainMethod_Percentage)

        effrainperc = int(next_token())  # IF Method is Percentage
        SetSimulParam_EffectiveRain_PercentEffRain(effrainperc)

        effrainshow = int(next_token())  # For estimation of surface run-off
        SetSimulParam_EffectiveRain_ShowersInDecade(effrainshow)

        effrainrootE = int(next_token())  # For reduction of soil evaporation
        SetSimulParam_EffectiveRain_RootNrEvap(effrainrootE)

    else:
        # take the default set of program parameters
        # (already read in InitializeSettings)
        ProgramParametersAvailable = False

    return ProgramParametersAvailable

