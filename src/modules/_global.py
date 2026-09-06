from typing import Optional
from sys import float_info
from dataclasses import dataclass, field
from .kinds import intEnum
from .utils import *
import numpy as np
import sys
import math
import os
from ctypes import c_float

ProjectInput: Optional[list["ProjectInput_type"]] = None
_PROJECT_FILE_CACHE = {}

PathNameList: Optional[str] = None
PathNameParam: Optional[str] = None

OutputName = ""

fTnxReference: Optional[TextIO] = None

TmaxTnxReference12MonthsRun: Optional[np.ndarray] = None
TminTnxReference12MonthsRun: Optional[np.ndarray] = None
TmaxTnxReference12MonthsRun = np.zeros(12, dtype=np.float32)
TminTnxReference12MonthsRun = np.zeros(12, dtype=np.float32)

# 1-based para imitar Fortran: índices 1..366 (0 sin usar)
TmaxRun: list[float] = [0.0] * (366 + 1)
TminRun: list[float] = [0.0] * (366 + 1)

# dimension(1:12)
TmaxTnxReference12MonthsRun: list[float] = [0.0] * (12 + 1)
TminTnxReference12MonthsRun: list[float] = [0.0] * (12 + 1)

# dimension(1:365)
TmaxCropReferenceRun: list[float] = [0.0] * (365 + 1)
TminCropReferenceRun: list[float] = [0.0] * (365 + 1)

# dimension(1:365)
TmaxTnxReference365DaysRun: list[float] = [0.0] * (365 + 1)
TminTnxReference365DaysRun: list[float] = [0.0] * (365 + 1)

#TmaxTnxReference365DaysRun = [0.0] * 365
#TminTnxReference365DaysRun = [0.0] * 365

Equiv: float = 0.64

EToDescription: str = ""

EvapZmin: float = 15.0
CO2Ref: float = 369.41

ac_zero_threshold = 0.000001
eps = 10e-08

ShapeFactor = 0

TimeCuttings_NA = 0
# index of NA in TimeCuttings enumerated type

TimeCuttings_IntDay = 1
# index of IntDay in TimeCuttings enumerated type

TimeCuttings_IntGDD = 2
# index of IntGDD in TimeCuttings enumerated type

TimeCuttings_DryB = 3
# index of DryB in TimeCuttings enumerated type

TimeCuttings_DryY = 4
# index of DryY in TimeCuttings enumerated type

TimeCuttings_FreshY = 5
# index of FreshY in TimeCuttings enumerated type

def epsilon(_x=0.0) -> float:
    # Fortran epsilon(real(dp)) equivalent
    return sys.float_info.epsilon

@dataclass
class ProjectInput_type:
    # Container for project file input data

    VersionNr: float = 0.0

    Description: Optional[str] = None

    Simulation_YearSeason: int = 0

    Simulation_DayNr1: int = 0
    Simulation_DayNrN: int = 0

    Crop_Day1: int = 0 # First day of cropping period
    #Crop_DayN: int = 0 # Last day of cropping period
    Crop_LastDayNr: int = 0 # Last day of cropping period (maturity or premature end when too cold to reach maturity)

    Climate_Info: Optional[str] = None
    Climate_Filename: Optional[str] = None
    Climate_Directory: Optional[str] = None
    Temperature_Info: Optional[str] = None
    Temperature_Filename: Optional[str] = None
    Temperature_Directory: Optional[str] = None

    ETo_Info: Optional[str] = None
    ETo_Filename: Optional[str] = None
    ETo_Directory: Optional[str] = None

    Rain_Info: Optional[str] = None
    Rain_Filename: Optional[str] = None
    Rain_Directory: Optional[str] = None

    CO2_Info: Optional[str] = None
    CO2_Filename: Optional[str] = None
    CO2_Directory: Optional[str] = None

    Calendar_Info: Optional[str] = None
    Calendar_Filename: Optional[str] = None
    Calendar_Directory: Optional[str] = None

    Crop_Info: Optional[str] = None
    Crop_Filename: Optional[str] = None
    Crop_Directory: Optional[str] = None

    Irrigation_Info: Optional[str] = None
    Irrigation_Filename: Optional[str] = None
    Irrigation_Directory: Optional[str] = None

    Management_Info: Optional[str] = None
    Management_Filename: Optional[str] = None
    Management_Directory: Optional[str] = None

    GroundWater_Info: Optional[str] = None
    GroundWater_Filename: Optional[str] = None
    GroundWater_Directory: Optional[str] = None

    Soil_Info: Optional[str] = None
    Soil_Filename: Optional[str] = None
    Soil_Directory: Optional[str] = None

    SWCIni_Info: Optional[str] = None
    SWCIni_Filename: Optional[str] = None
    SWCIni_Directory: Optional[str] = None

    OffSeason_Info: Optional[str] = None
    OffSeason_Filename: Optional[str] = None
    OffSeason_Directory: Optional[str] = None

    Observations_Info: Optional[str] = None
    Observations_Filename: Optional[str] = None
    Observations_Directory: Optional[str] = None

    def read_project_file(self, filename, NrRun):
        # Reads in the project file contents that apply to the given run index.

        # PRM or PRO file name

        # Run index (should be 1 in the case of a PRO file)

        lines = _get_project_lines(ResolvePath(filename))

        if len(lines) < 2:
            return

        buffer = lines[0]
        self.Description = buffer.strip()
        self.VersionNr = float(lines[1].split()[0])  # AquaCrop version Nr

        NrFileLines = 42  # Clim(15),Calendar(3),Crop(3),Irri(3),Field(3),Soil(3),Gwt(3),Inni(3),Off(3),FieldData(3)
        base = 2 + (NrRun - 1) * (NrFileLines + 5)
        idx = base

        if idx + (NrFileLines + 5) > len(lines):
            return

        # 0. Year of cultivation and Simulation and Cropping period
        self.Simulation_YearSeason = int(lines[idx].split()[0]); idx += 1
        self.Simulation_DayNr1 = int(lines[idx].split()[0]); idx += 1
        self.Simulation_DayNrN = int(lines[idx].split()[0]); idx += 1
        self.Crop_Day1 = int(lines[idx].split()[0]); idx += 1
        self.Crop_LastDayNr = int(lines[idx].split()[0]); idx += 1

        # 1. Climate
        buffer = lines[idx]; idx += 1
        self.Climate_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.Climate_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.Climate_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.Climate_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.Climate_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 1.1 Temperature
        buffer = lines[idx]; idx += 1
        self.Temperature_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.Temperature_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.Temperature_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.Temperature_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.Temperature_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 1.2 ETo
        buffer = lines[idx]; idx += 1
        self.ETo_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.ETo_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.ETo_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.ETo_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.ETo_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 1.3 Rain
        buffer = lines[idx]; idx += 1
        self.Rain_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.Rain_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.Rain_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.Rain_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.Rain_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 1.4 CO2
        buffer = lines[idx]; idx += 1
        self.CO2_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.CO2_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.CO2_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.CO2_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.CO2_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 2. Calendar
        buffer = lines[idx]; idx += 1
        self.Calendar_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.Calendar_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.Calendar_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.Calendar_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.Calendar_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 3. Crop
        buffer = lines[idx]; idx += 1
        self.Crop_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.Crop_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.Crop_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.Crop_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.Crop_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 4. Irrigation
        buffer = lines[idx]; idx += 1
        self.Irrigation_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.Irrigation_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.Irrigation_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.Irrigation_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.Irrigation_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 5. Field Management
        buffer = lines[idx]; idx += 1
        self.Management_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.Management_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.Management_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.Management_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.Management_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 6. Soil Profile
        buffer = lines[idx]; idx += 1
        self.Soil_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.Soil_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.Soil_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.Soil_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.Soil_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 7. GroundWater
        buffer = lines[idx]; idx += 1
        self.GroundWater_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.GroundWater_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.GroundWater_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.GroundWater_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.GroundWater_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 8. Initial conditions
        buffer = lines[idx]; idx += 1
        self.SWCIni_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.SWCIni_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.SWCIni_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.SWCIni_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.SWCIni_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 9. Off-season conditions
        buffer = lines[idx]; idx += 1
        self.OffSeason_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.OffSeason_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.OffSeason_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.OffSeason_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.OffSeason_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

        # 10. Field data
        buffer = lines[idx]; idx += 1
        self.Observations_Info = buffer.strip()
        buffer = lines[idx]; idx += 1
        #self.Observations_Filename = buffer.split()[0].strip() if buffer.strip() else ""
        self.Observations_Filename = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )
        buffer = lines[idx]; idx += 1
        #self.Observations_Directory = buffer.split()[0].strip() if buffer.strip() else ""
        self.Observations_Directory = (
            _strip_quotes(buffer.split()[0]).strip()
            if buffer.strip()
            else ""
        )

def _get_project_lines(filename):
    filename = filename.rstrip()
    lines = _PROJECT_FILE_CACHE.get(filename)
    if lines is None:
        with open(filename, "r") as fhandle:
            lines = fhandle.read().splitlines()
        _PROJECT_FILE_CACHE[filename] = lines
    return lines

def dbg_i(name, val):
    print(f"{name}={val}")

def dbg_r(name, val):   
    # 17 decimales tipo Fortran “alta precisión”, sin espacios
    print(f"{name}={val:.17f}")

# PATH

# Data dirs (LIST/, OUTP/, PARAM/, SIMUL/): next to the executable when frozen,
# else <project root>/testcase/. Trailing separator required: callers concatenate.
if getattr(sys, "frozen", False):
    complete_path_dir = os.path.dirname(os.path.abspath(sys.executable)) + os.sep
else:
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    complete_path_dir = os.path.join(_this_dir, "..", "..", "testcase") + os.sep


# Calendar -> Global variables
CalendarDescription: Optional[str] = None
CalendarFile: Optional[str] = None
CalendarFileFull: Optional[str] = None

# Climate -> Global variables
ClimateDescription: Optional[str] = None
ClimDescription: Optional[str] = None  # Posible variable repetida
ClimateFile: Optional[str] = None
ClimFile: Optional[str] = None  # Posible variable repetida
ClimateFileFull: Optional[str] = None

# CO2 -> Global variables
CO2Description: Optional[str] = None
CO2File: Optional[str] = None
CO2FileFull: Optional[str] = None

# Crop -> Global variables
CropDescription: Optional[str] = None
CropFile: Optional[str] = None
CropFileFull: Optional[str] = None

# ETo -> Global variables
EToDescription: Optional[str] = None
EToFile: Optional[str] = None
EToFileFull: Optional[str] = None

# Other global variables
FullFileNameProgramParameters: Optional[str] = None

# Groundwater -> global variables
GroundwaterDescription: Optional[str] = None
GroundWaterFile: Optional[str] = None
GroundWaterFileFull: Optional[str] = None

# Irrigation global variables
IrriDescription: Optional[str] = None
IrriFile: Optional[str] = None
IrriFileFull: Optional[str] = None

# Man -> global variables
ManDescription: Optional[str] = None
ManFile: Optional[str] = None
ManFileFull: Optional[str] = None

# Multiple project -> Global variables
MultipleProjectDescription: Optional[str] = None
MultipleProjectFile: Optional[str] = None
MultipleProjectFileFull: Optional[str] = None

# Observations -> Global variables
ObservationsDescription: Optional[str] = None
ObservationsFile: Optional[str] = None
ObservationsFilefull: Optional[str] = None

# Off season -> Global variables
OffSeasonDescription: Optional[str] = None
OffSeasonFile: Optional[str] = None
OffSeasonFilefull: Optional[str] = None

# Names -> Global variables
OutputName: Optional[str] = None
PathNameList: Optional[str] = None
PathNameOutp: Optional[str] = None
PathNameParam: Optional[str] = None
PathNameProg: Optional[str] = None
PathNameSimul: Optional[str] = None

# Prof -> Global variables
ProfDescription: Optional[str] = None
ProfFile: Optional[str] = None
ProfFilefull: Optional[str] = None

# Project -> Global variables
ProjectDescription: Optional[str] = None
ProjectFile: Optional[str] = None
ProjectFileFull: Optional[str] = None

# Rain -> Global variables
RainDescription: Optional[str] = None
RainFile: Optional[str] = None
RainFileFull: Optional[str] = None

# SWCini -> Global variables
SWCiniDescription: Optional[str] = None
SWCiniFile: Optional[str] = None
SWCiniFileFull: Optional[str] = None

# Temperature -> Global variables
TemperatureDescription: Optional[str] = None
TemperatureFile: Optional[str] = None
TemperatureFileFull: Optional[str] = None

# TnxReference -> Global variables
TnxReference365DaysFile: Optional[str] = None
TnxReference365DaysFileFull: Optional[str] = None
TnxReferenceFile: Optional[str] = None
TnxReferenceFileFull: Optional[str] = None

# OutputAggregate -> Global variable
OutputAggregate: int = 0

# Boolean global variables
EvapoEntireSoilSurface = False  # True if soil wetted by RAIN (False = IRRIGATION and fw < 1)
PreDay = False
OutDaily = False
Out8Irri = False
Out1Wabal = False
Out2Crop = False
Out3Prof = False
Out4Salt = False
Out5CompWC = False
Out6CompEC = False
Out7Clim = False
Part1Mult = False
Part2Eval = False

#Index of TypePRO in typeproject enumerated type
typeproject_typepro = intEnum(0)

# Index of TypePRM in typeproject enumerated type
typeproject_typeprm = intEnum(1)

# Index of TypeNone in typeproject enumerated type
typeproject_typenone = intEnum(2)


# index of ObsSimCC in typeObsSim enumerated type
typeObsSim_ObsSimCC = intEnum(0)

# index of ObsSimB in typeObsSim enumerated type
typeObsSim_ObsSimB = intEnum(1)

# index of ObsSimSWC in typeObsSim enumerated type
typeObsSim_ObsSimSWC = intEnum(2)

# Crop enum
# index of Vegetative in subkind enumerated type
subkind_Vegetative = intEnum(0)

# index of Grain in subkind enumerated type
subkind_Grain = intEnum(1)

# index of Tuber in subkind enumerated type
subkind_Tuber = intEnum(2)

# index of Forage in subkind enumerated type
subkind_Forage = intEnum(3)

# index of seed in planting enumerated type
plant_Seed = intEnum(0)

# index of transplant in planting enumerated type
plant_transplant = intEnum(1)

# index of regrowth in planting enumerated type
plant_regrowth = intEnum(2)

# index of GDDays in modeCycle enumerated type
ModeCycle_GDDays = intEnum(0)

# index of CalendarDays in modeCycle enumerated type
ModeCycle_CalendarDays = intEnum(1)

# index of NoCorrection in pMethod enumerated type
pMethod_NoCorrection = intEnum(0)

# index of FAOCorrection in pMethod enumerated type
pMethod_FAOCorrection = intEnum(1)

# index of NA in TimeCuttings enumerated type
TimeCuttings_NA = intEnum(0)

# index of daily in datatype enumerated type
datatype_Daily = intEnum(0)
# index of decadely in datatype enumerated type
datatype_Decadely = intEnum(1)
# index of monthly in datatype enumerated type
datatype_Monthly = intEnum(2)

IrriMode_NoIrri = intEnum(0)
IrriMode_Manual = intEnum(1)
IrriMode_Generate = intEnum(2)
IrriMode_Inet = intEnum(3)
IrriMode = intEnum(0)

GenerateDepthMode = intEnum(0)
GenerateDepthMode_ToFC = intEnum(0) # index of ToFC in GenerateDepthMode enumerated type
GenerateDepthMode_FixDepth = intEnum(1) # index of FixDepth in GenerateDepthMode enumerated type

# IrriMethod
IrriMethod = intEnum(0)

IrriMethod_MBasin = intEnum(0)
IrriMethod_MBorder = intEnum(1)
IrriMethod_MDrip = intEnum(2)
IrriMethod_MFurrow = intEnum(3)
IrriMethod_MSprinkler = intEnum(4) # index of MSprinkler in IrriMethod enumerated type

GenerateTimeMode = intEnum(0)
GenerateTimeMode_FixInt = intEnum(0) # index of FixInt in GenerateTimeMode enumerated type
GenerateTimeMode_AllDepl = intEnum(1) # index of AllDepl in GenerateTimeMode enumerated type
GenerateTimeMode_AllRAW = intEnum(2) # index of AllRAW in GenerateTimeMode enumerated type
GenerateTimeMode_WaterBetweenBunds = intEnum(3) # index of WaterBetweenBunds in GenerateTimeMode enumerated type

EffectiveRainMethod_Full = intEnum(0) # index of full in EffectiveRainMethod enumerated type
EffectiveRainMethod_USDA = intEnum(1) # index of usda in EffectiveRainMethod enumerated type
EffectiveRainMethod_Percentage = intEnum(2) # index of percentage in EffectiveRainMethod enumerated type

DaySubmerged: int = 0
MaxPlotNew: int = 0
MaxPlotTr: int = 0

AirTCriterion_TMinPeriod = 0    # index of TminPeriod in AirTCriterion enumerated type
AirTCriterion_TMeanPeriod = 1   # index of TmeanPeriod in AirTCriterion enumerated type
AirTCriterion_GDDPeriod = 2     # index of GDDPeriod in AirTCriterion enumerated type
AirTCriterion_CumulGDD = 3      # index of CumulGDD in AirTCriterion enumerated type

CCiActual: float = 0.0
CCiprev: float = 0.0
CCiTopEarlySen: float = 0.0
CRsalt: float = 0.0  # gram/m2
CRwater: float = 0.0  # mm/day
ECDrain: float = 0.0  # EC drain water dS/m
ECiAqua: float = 0.0  # EC of the groundwater table in dS/m
ECstorage: float = 0.0  #EC surface storage dS/m
Eact: float = 0.0  # mm/day
Epot: float = 0.0  # mm/day
ETo: float = 0.0  # mm/day
Drain: float = 0.0  # mm/day
Infiltrated: float = 0.0  # mm/day
Irrigation: float = 0.0  # mm/day
Rain: float = 0.0  # mm/day
RootingDepth: float = 0.0
Runoff: float = 0.0  # mm/day
SaltInfiltr: float = 0.0  # salt infiltrated in soil profile Mg/ha
Surf0: float = 0.0  # surface water [mm] begin day
SurfaceStorage: float = 0.0  #mm/day
Tact: float = 0.0  # mm/day
Tpot: float = 0.0  # mm/day
TactWeedInfested: float = 0.0  #mm/day
Tmax: float = 0.0  # degC
Tmin: float = 0.0  # degC
TmaxCropReference: float = 0.0  # degC
TminCropReference: float = 0.0  # degC
TmaxTnxReference365Days: float = 0.0  # degC
TminTnxReference365Days: float = 0.0  # degC

NoMoreCrop: bool = False

ElapsedDays = [
    0.0,     # January
    31.0,    # February
    59.25,   # March
    90.25,   # April
    120.25,  # May
    151.25,  # June
    181.25,  # July
    212.25,  # August
    243.25,  # September
    273.25,  # October
    304.25,  # November
    334.25,  # December
]

DaysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

NameMonth = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

NrCompartments: int = 0
max_No_compartments: int = 12
EffectiveRainMethod_USDA: int = 1
IniPercTAW: int = 0
# Depth of Groundwater table below soil surface in centimeter
ZiAqua = 0
IrriFirstDayNr: int = 0
max_SoilLayers = 5
undef_double = -9.9
undef_int = -9

TnxReferenceYear = 0

Criterion_RainPeriod = intEnum(1)

AirTCriterion_CumulGDD = intEnum(3)

@dataclass
class rep_DayEventDbl:
    DayNr: int
    """Undocumented"""
    Param: float
    """Undocumented"""

@dataclass
class rep_DayEventInt:
    DayNr: int
    # Undocumented

    param: int
    # Undocumented

EToDataSet = [rep_DayEventDbl(0, 0.0) for _ in range(31)]
RainDataSet = [rep_DayEventDbl(0, 0.0) for _ in range(31)]
TminDataSet = [rep_DayEventDbl(0, 0.0) for _ in range(31)]
TmaxDataSet = [rep_DayEventDbl(0, 0.0) for _ in range(31)]

IrriBeforeSeason = [rep_DayEventInt(0, 0) for _ in range(5)]
IrriAfterSeason = [rep_DayEventInt(0, 0) for _ in range(5)]

# Clases de datos
@dataclass
class rep_RootZoneWC:
    Actual: float = 0.0
    """actual soil water content in rootzone [mm]"""
    FC: float = 0.0
    """soil water content [mm] in rootzone at FC"""
    WP: float = 0.0
    """soil water content [mm] in rootzone at WP"""
    SAT: float = 0.0
    """soil water content [mm] in rootzone at Sat"""
    Leaf: float = 0.0
    """soil water content [mm] in rootzone at upper Threshold for leaf expansion"""
    Thresh: float = 0.0
    """soil water content [mm] in rootzone at Threshold for stomatal closure"""
    Sen: float = 0.0
    """soil water content [mm] in rootzone at Threshold for canopy senescence"""
    ZtopAct: float = 0.0
    """actual soil water content [mm] in top soil (= top compartment)"""
    ZtopFC: float = 0.0
    """soil water content [mm] at FC in top soil (= top compartment)"""
    ZtopWP: float = 0.0
    """soil water content [mm] at WP in top soil (= top compartment)"""
    ZtopThresh: float = 0.0
    """soil water content [mm] at Threshold for stomatal closure in top soil"""

RootZoneWC = rep_RootZoneWC()


@dataclass
class rep_clim:
    DataType: int = 0
    FromD: int = 0
    FromM: int = 0
    FromY: int = 0
    ToD: int = 0
    ToM: int = 0
    ToY: int = 0
    FromDayNr: int = 0
    ToDayNr: int = 0
    FromString: Optional[str] = None
    ToString: Optional[str] = None
    NrObs: int = 0

@dataclass
class rep_RootZoneSalt:
    ECe: float = 0.0
    # Electrical conductivity of the saturated soil-paste extract (dS/m)

    ECsw: float = 0.0
    # Electrical conductivity of the soil water (dS/m)

    ECswFC: float = 0.0
    # Electrical conductivity of the soil water at Field Capacity(dS/m)

    KsSalt: float = 0.0
    # stress coefficient for salinity

RootZoneSalt = rep_RootZoneSalt()

@dataclass
class rep_IniSWC:
    AtDepths: bool = False
    NrLoc: int = 0
    Loc: list[float] = field(default_factory=lambda: [undef_double] * max_No_compartments)       # depth or layer thickness [m]
    VolProc: list[float] = field(default_factory=lambda: [undef_double] * max_No_compartments)   # soil water content (vol%)
    SaltECe: list[float] = field(default_factory=lambda: [undef_double] * max_No_compartments)   # ECe in dS/m
    AtFC: bool = False


@dataclass
class rep_EffectStress:
    RedCGC: int = 0       # Reduction of CGC (%)
    RedCCX: int = 0       # Reduction of CCx (%)
    RedWP: int = 0        # Reduction of WP (%)
    CDecline: float = 0.0 # Average decrease of CCx in mid season (%/day)
    RedKsSto: int = 0     # Reduction of KsSto (%)


@dataclass
class rep_storage:
    Btotal: float = 0.0
    CropString: Optional[str] = None
    Season: int = 0

@dataclass
class rep_sim:
    FromDayNr: int = 0
    ToDayNr: int = 0
    IniSWC: rep_IniSWC = field(default_factory=rep_IniSWC)
    ThetaIni: list[float] = field(default_factory=lambda: [undef_double] * max_No_compartments)
    ECeIni: list[float] = field(default_factory=lambda: [undef_double] * max_No_compartments)
    SurfaceStorageIni: float = 0.0
    ECStorageIni: float = 0.0
    CCini: float = 0.0
    Bini: float = 0.0
    Zrini: float = 0.0
    LinkCropToSimPeriod: bool = False
    ResetIniSWC: bool = False
    InitialStep: int = 0
    EvapLimitON: bool = False
    EvapWCsurf: float = 0.0
    EvapStartStg2: int = 0
    EvapZ: float = 0.0
    HIfinal: int = 0
    DelayedDays: int = 0
    Germinate: bool = False
    SumEToStress: float = 0.0
    SumGDD: float = 0.0
    SumGDDfromDay1: float = 0.0
    SCor: float = 0.0
    MultipleRun: bool = False
    NrRuns: int = 0
    MultipleRunWithKeepSWC: bool = False
    MultipleRunConstZrx: float = 0.0
    IrriECw: float = 0.0
    DayAnaero: int = 0
    EffectStress: rep_EffectStress = field(default_factory=rep_EffectStress)
    SalinityConsidered: bool = False
    ProtectedSeedling: bool = False
    SWCtopSoilConsidered: bool = False
    LengthCuttingInterval: int = 0
    YearSeason: int = 0
    RCadj: int = 0
    Storage: rep_storage = field(default_factory=rep_storage)
    YearStartCropCycle: int = 0
    CropDay1Previous: int = 0

@dataclass
class rep_FileOK:
    Climate_Filename: bool = False
    Temperature_Filename: bool = False
    ETo_Filename: bool = False
    Rain_Filename: bool = False
    CO2_Filename: bool = False
    Calendar_Filename: bool = False
    Crop_Filename: bool = False
    Irrigation_Filename: bool = False
    Management_Filename: bool = False
    GroundWater_Filename: bool = False
    Soil_Filename: bool = False
    SWCIni_Filename: bool = False
    OffSeason_Filename: bool = False
    Observations_Filename: bool = False

@dataclass
class rep_sum:
    # Undocumented
    Epot: float = 0.0
    Tpot: float = 0.0
    Rain: float = 0.0
    Irrigation: float = 0.0
    Infiltrated: float = 0.0

    # mm
    Runoff: float = 0.0
    Drain: float = 0.0
    Eact: float = 0.0
    Tact: float = 0.0
    TrW: float = 0.0
    ECropCycle: float = 0.0
    CRwater: float = 0.0

    # ton/ha
    Biomass: float = 0.0
    YieldPart: float = 0.0
    BiomassPot: float = 0.0
    BiomassUnlim: float = 0.0
    BiomassTot: float = 0.0

    # ton/ha
    SaltIn: float = 0.0
    SaltOut: float = 0.0
    CRsalt: float = 0.0

@dataclass
class rep_EffectiveRain:
    ## for 10-day or monthly rainfall data
    Method: int = 0
    ## Undocumented

    PercentEffRain: int = 0
    ## IF Method = Percentage

    ShowersInDecade: int = 0
    ## adjustment of surface run-off

    RootNrEvap: int = 0
    ## Root for reduction in soil evaporation

@dataclass
class rep_param:
    ##  DEFAULT.PAR
    ## crop parameters IN CROP.PAR - with Reset option
    EvapDeclineFactor: int = 0
    ## exponential decline with relative soil water [1 = small ... 8 = sharp]

    KcWetBare: float = 0.0
    ## Soil evaporation coefficients from wet bare soil

    PercCCxHIfinal: int = 0
    ## CC threshold below which HI no longer increase (% of 100)

    RootPercentZmin: int = 0
    ## starting depth of root sine function in % of Zmin (sowing depth)

    MaxRootZoneExpansion: float = 0.0
    ## maximum root zone expansion in cm/day - fixed at 5 cm/day

    KsShapeFactorRoot: int = 0
    ## shape factor for the effect of water stress on root zone expansion

    TAWGermination: int = 0
    ## Soil water content (% TAW) required at sowing depth for germination

    pAdjFAO: float = 0.0
    ## Adjustment factor for FAO-adjustment of soil water depletion (p) for various ET

    DelayLowOxygen: int = 0
    ## delay [days] for full effect of anaeroby

    ExpFsen: float = 0.0
    ## exponent of senescence factor adjusting drop in photosynthetic activity of dying crop

    Beta: int = 0
    ## Percentage decrease of p(senescence) once early canopy senescence is triggered

    ThicknessTopSWC: int = 0
    ## Thickness of top soil for determination of its Soil Water Content (cm)

    ## Field parameter IN FIELD.PAR  - with Reset option
    EvapZmax: int = 0
    ## cm  maximum soil depth for water extraction by evaporation

    ## Runoff parameters IN RUNOFF.PAR  - with Reset option
    RunoffDepth: float = 0.0
    ## considered depth (m) of soil profile for calculation of mean soil water content for CN adjustment

    CNcorrection: bool = False
    ## correction Antecedent Moisture Class (On/Off)

    ## Temperature parameters IN TEMPERATURE.PAR  - with Reset option
    Tmin: float = 0.0
    ## Default Minimum and maximum air temperature (degC) if no temperature file

    Tmax: float = 0.0
    ## Default Minimum and maximum air temperature (degC) if no temperature file

    GDDMethod: int = 0
    ## 1 for Method 1, 2 for Method 2, 3 for Method 3

    ## General parameters IN GENERAL.PAR
    PercRAW: int = 0
    ## allowable percent RAW depletion for determination Inet

    CompDefThick: float = 0.0
    ## Default thickness of soil compartments [m]

    CropDay1: int = 0
    ## First day after sowing/transplanting (DAP = 1)

    Tbase: float = 0.0
    ## Default base and upper temperature (degC) assigned to crop

    Tupper: float = 0.0
    ## Default base and upper temperature (degC) assigned to crop

    IrriFwInSeason: int = 0
    ## Percentage of soil surface wetted by irrigation in crop season

    IrriFwOffSeason: int = 0
    ## Percentage of soil surface wetted by irrigation off-season

    ## Showers parameters (10-day or monthly rainfall) IN SHOWERS.PAR
    ShowersInDecade: list[int] = field(default_factory=lambda: [0]*12)
    ## 10-day or Monthly rainfall --> Runoff estimate

    EffectiveRain: rep_EffectiveRain = field(default_factory=rep_EffectiveRain)
    ## 10-day or Monthly rainfall --> Effective rainfall

    ## Salinity
    SaltDiff: int = 0
    ## salt diffusion factor (capacity for salt diffusion in micro pores) [%]

    SaltSolub: int = 0
    ## salt solubility [g/liter]

    ## Groundwater table
    ConstGwt: bool = False
    ## groundwater table is constant (or absent) during the simulation period

    ## Capillary rise
    RootNrDF: int = 0
    ## Undocumented

    ## Initial abstraction for surface runoff
    IniAbstract: int = 0
    ## Undocumented

@dataclass
class CompartmentIndividual:
    
    # meter
    Thickness: float = 0.0

    # m3/m3
    Theta: float = 0.0

    # mm/day         
    fluxout: float = 0.0

    # Undocumented     
    Layer: int = 0

    # Maximum root extraction m3/m3.day           
    Smax: float = 0.0

    # Vol % at Field Capacity adjusted to Aquifer
    FCadj: float = 0.0

    # Number of days under anaerobic conditions        
    DayAnaero: int = 0          
    
    # weighting factor 0 ... 1
    # Importance of compartment in calculation of
    # - relative wetness (RUNOFF)
    # - evaporation process
    # - transpiration process *)
    WFactor: float = 0.0

    # Maximum possible water extraction (with current water stress)
    SinkMajor: float = 0.0

    # Required extraction considering root distribution (no water stress)
    SinkMinor: float = 0.0

    # Salinity factors
    # Salt content in solution in cells (g/m2)
    Salt: list[float] = field(default_factory=lambda: [0.0]*11)

    # Salt deposit in cells (g/m2)
    Depo: list[float] = field(default_factory=lambda: [0.0]*11)

@dataclass
class rep_soil:    
    REW: int = 0          # Readily evaporable water (mm)
    NrSoilLayers: int = 0 # Number of soil layers
    CNvalue: int = 0      # Curve Number value
    RootMax: float = 0.0  # Maximum rooting depth in soil profile for selected crop

@dataclass
class SoilLayerIndividual:
    Description: str = ""            # Undocumented
    Thickness: float = undef_double           # meter
    SAT: float = undef_double                 # Vol % at Saturation
    FC: float = undef_double                  # Vol % at Field Capacity
    WP: float = undef_double                  # Vol % at Wilting Point
    tau: float = undef_double                 # drainage factor 0 ... 1
    InfRate: float = undef_double             # Infiltration rate at saturation (mm/day)
    Penetrability: int = undef_int            # root zone expansion rate (%)
    GravelMass: int = undef_int               # mass percentage of gravel
    GravelVol: float = undef_double           # volume percentage of gravel
    WaterContent: float = undef_double        # mm
    Macro: int = undef_int                    # Macropores: from Saturation to Macro [vol%]
    SaltMobility: list[float] = field(default_factory=lambda: [0.0]*11)  # Mobility of salt (11 cells)
    SC: int = undef_int                       # number of Salt cells (0..SC/(SC+2)*SAT vol%)
    SCP1: int = undef_int                     # SC + 1 (extra salt cell)
    UL: float = undef_double                  # Upper Limit of SC salt cells (m3/m3)
    Dx: float = undef_double                  # Size of SC salt cells [m3/m3]
    SoilClass: int = undef_int                # 1=sandy, 2=loamy, 3=sandy clayey, 4=silty clayey
    CRa: float = 0.0                 # Coefficient for Capillary Rise
    CRb: float = 0.0                 # Coefficient for Capillary Rise

@dataclass
class rep_Shapes:
    Stress: int = 0            # Percentage soil fertility stress for calibration
    ShapeCGC: float = 0.0      # Shape factor for response of Canopy Growth Coefficient
    ShapeCCX: float = 0.0      # Shape factor for response of Maximum Canopy Cover
    ShapeWP: float = 0.0       # Shape factor for response of Crop Water Productivity
    ShapeCDecline: float = 0.0 # Shape factor for response of Decline of Canopy Cover
    Calibrated: bool = False   # Undocumented

class rep_Assimilates:
    On: bool = False           # Undocumented
    Period: int = 0            # Number of days at end of season during which assimilates are stored in root system
    Stored: int = 0            # Percentage of assimilates transferred to root system at last day of season
    Mobilized: int = 0         # Percentage of stored assimilates transferred to above ground parts in next season

@dataclass
class rep_Crop:
    # intEnum -> int
    subkind: int = 0                     # Undocumented
    ModeCycle: int = 0                   # Undocumented
    Planting: int = 0                    # 1=sown, 0=transplanted, -9=regrowth
    pMethod: int = 0                     # Undocumented

    pdef: float = 0.0                    # soil water depletion fraction (ETo=5 mm/day)
    pActStom: float = 0.0                # actual p (ETo of the day)

    KsShapeFactorLeaf: float = 0.0       # Undocumented
    KsShapeFactorStomata: float = 0.0    # Undocumented
    KsShapeFactorSenescence: float = 0.0 # Undocumented

    pLeafDefUL: float = 0.0              # soil water depletion fraction (ETo=5)
    pLeafDefLL: float = 0.0              # soil water depletion fraction (ETo=5)
    pLeafAct: float = 0.0                # actual p for upper limit leaf expansion
    pSenescence: float = 0.0             # soil water depletion for canopy senescence
    pSenAct: float = 0.0                 # actual p for canopy senescence
    pPollination: float = 0.0            # depletion fraction for failure of pollination

    SumEToDelaySenescence: int = 0       # Undocumented
    AnaeroPoint: int = 0                 # (SAT - [vol%]) at which deficient aeration

    StressResponse: rep_Shapes = field(default_factory=rep_Shapes) # Undocumented

    ECemin: int = 0                      # lower threshold salinity stress (dS/m)
    ECemax: int = 0                      # upper threshold salinity stress (dS/m)
    CCsaltDistortion: int = 0            # canopy cover distortion for salinity (%)
    ResponseECsw: int = 0                # Ks stomata response to ECsw (0..200)

    SmaxTopQuarter: float = 0.0          # HOOGLAND
    SmaxBotQuarter: float = 0.0          # HOOGLAND
    SmaxTop: float = 0.0                 # HOOGLAND
    SmaxBot: float = 0.0                 # HOOGLAND

    KcTop: float = 0.0                   # Undocumented
    KcDecline: float = 0.0               # Reduction Kc (%CCx/day)

    CCEffectEvapLate: int = 0            # %
    Day1: int = 0                        # first day (from sowing/transplanting)
    DayN: int = 0                        # last day = harvest day
    Length: list[int] = field(default_factory=lambda: [0]*4)  # four growth stages

    RootMin: float = 0.0                 # m
    RootMax: float = 0.0                 # m
    RootShape: int = 0                   # 10 * root of root function

    Tbase: float = 0.0                   # °C
    Tupper: float = 0.0                  # °C
    Tcold: int = 0                       # °C (cold stress pollination fail)
    Theat: int = 0                       # °C (heat stress pollination fail)

    GDtranspLow: float = 0.0             # degC-day
    SizeSeedling: float = 0.0            # cm^2
    SizePlant: float = 0.0               # cm^2 (regrowth)

    PlantingDens: int = 0                # plants/ha

    CCo: float = 0.0                     # starting canopy (fraction)
    CCini: float = 0.0                   # starting canopy for regrowth (fraction)
    CGC: float = 0.0                     # canopy growth coeff (per day)
    GDDCGC: float = 0.0                  # canopy growth coeff (per GDD)
    CCx: float = 0.0                     # max canopy cover (fraction)
    CDC: float = 0.0                     # canopy decline coeff (per day)
    GDDCDC: float = 0.0                  # canopy decline coeff (per GDD)

    CCxAdjusted: float = 0.0             # max canopy under water stress
    CCxWithered: float = 0.0             # max existed CC during season
    CCoAdjusted: float = 0.0             # initial canopy after soil water stress

    DaysToCCini: int = 0
    DaysToGermination: int = 0
    DaysToFullCanopy: int = 0
    DaysToFullCanopySF: int = 0
    DaysToFlowering: int = 0
    LengthFlowering: int = 0
    DaysToSenescence: int = 0
    DaysToHarvest: int = 0
    DaysToMaxRooting: int = 0
    DaysToHIo: int = 0

    GDDaysToCCini: int = 0
    GDDaysToGermination: int = 0
    GDDaysToFullCanopy: int = 0
    GDDaysToFullCanopySF: int = 0
    GDDaysToFlowering: int = 0
    GDDLengthFlowering: int = 0
    GDDaysToSenescence: int = 0
    GDDaysToHarvest: int = 0
    GDDaysToMaxRooting: int = 0
    GDDaysToHIo: int = 0

    WP: float = 0.0                      # (normalized) water productivity (g/m^2)
    WPy: int = 0                         # during yield formation (% WP)
    AdaptedToCO2: int = 0                # performance under elevated CO2 (%)
    HI: int = 0                          # harvest index (%)
    dHIdt: float = 0.0                   # avg rate of change in HI (%/day)
    HIincrease: int = 0                  # possible increase (%) of HI
    aCoeff: float = 0.0                  # impact of restricted vegetative growth at flowering
    bCoeff: float = 0.0                  # impact of stomatal closure at flowering
    DHImax: int = 0                      # allowable maximum increase (%) of specified HI

    DeterminancyLinked: bool = False     # linkage of determinancy with flowering
    fExcess: int = 0                     # potential excess of fruits (%)
    DryMatter: int = 0                   # dry matter content (%) of fresh yield

    RootMinYear1: float = 0.0            # m (perennial crops)
    SownYear1: bool = False              # True=Sown, False=transplanted (perennials)
    YearCCx: int = 0                     # years to CCx decline to 90% (perennials)
    CCxRoot: float = 0.0                 # shape factor of CCx decline (perennials)

    Assimilates: rep_Assimilates = field(default_factory=rep_Assimilates) # Undocumented

@dataclass
class rep_Content:

    BeginDay:   float = 0.0  # at the beginning of the day
    EndDay:     float = 0.0    # at the end of the day
    ErrorDay:   float = 0.0  # error on WaterContent or SaltContent over the day

@dataclass
class rep_CropFileSet:
    # Undocumented
    DaysFromSenescenceToEnd: int = 0
    # given or calculated from GDD
    DaysToHarvest: int = 0
    # Undocumented
    GDDaysFromSenescenceToEnd: int = 0
    # given or calculated from Calendar Days
    GDDaysToHarvest: int = 0

@dataclass
class rep_Cuttings:
    Considered: bool = False            # Undocumented
    CCcut: int = 0                      # Canopy cover (%) after cutting
    Day1: int = 0                       # first day after time window for generating cuttings (1 = start crop cycle)
    NrDays: int = 0                     # number of days of time window for generate cuttings (-9 is whole crop cycle)
    Generate: bool = False              # true: generate cuttings; false: schedule for cuttings
    Criterion: int = 0                  # time criterion for generating cuttings (Fortran integer(intEnum))
    HarvestEnd: bool = False            # final harvest at crop maturity
    FirstDayNr: int = 0                 # first dayNr of list of specified cutting events (-9 = onset growing cycle)

@dataclass
class rep_Manag:
    Mulch: int = 0                      # percent soil cover by mulch in growing period
    SoilCoverBefore: int = 0            # percent soil cover by mulch before growing period
    SoilCoverAfter: int = 0             # percent soil cover by mulch after growing period
    EffectMulchOffS: int = 0            # effect Mulch on evaporation before and after growing period
    EffectMulchInS: int = 0             # effect Mulch on evaporation in growing period
    FertilityStress: int = 0            # Undocumented
    BundHeight: float = 0.0             # meter
    RunoffOn: bool = False              # surface runoff
    CNcorrection: int = 0               # percent increase/decrease of CN
    WeedRC: int = 0                     # Relative weed cover in percentage at canopy closure
    WeedDeltaRC: int = 0                # Increase/Decrease of Relative weed cover in percentage during mid season
    WeedShape: float = 0.0              # Shape factor for crop canopy suppression
    WeedAdj: int = 0                    # replacement (%) by weeds of the self-thinned part of the Canopy Cover - only for perennials
    Cuttings: rep_Cuttings = field(default_factory=rep_Cuttings)    # Multiple cuttings

@dataclass
class rep_Onset:
    GenerateOn: bool = False          # by rainfall or temperature criterion
    GenerateTempOn: bool = False      # by temperature criterion
    Criterion: int = 0                # Undocumented
    AirTCriterion: int = 0            # Undocumented
    StartSearchDayNr: int = 0         # daynumber
    StopSearchDayNr: int = 0          # daynumber
    LengthSearchPeriod: int = 0       # days

class rep_EndSeason:
    ExtraYears: int = 0               # to add to YearStartCropCycle
    GenerateTempOn: bool = False      # by temperature criterion
    AirTCriterion: int = 0            # Undocumented
    StartSearchDayNr: int = 0         # daynumber
    StopSearchDayNr: int = 0          # daynumber
    LengthSearchPeriod: int = 0       # days

@dataclass
class rep_DayEventInt:
    DayNr: int = 0   # Undocumented
    param: int = 0  # Undocumented

from dataclasses import dataclass

@dataclass
class rep_IrriECw:
    PreSeason: float = 0.0  # Undocumented
    PostSeason: float = 0.0 # Undocumented

@dataclass
class rep_DayEventDbl:
    DayNr: int = 0  # Undocumented
    Param: float = 0.0  # Undocumented

@dataclass
class rep_PerennialPeriod:
    # onset is generated by air temperature criterion
    GenerateOnset: bool = False
    # another docstring
    OnsetCriterion: int = 0  # intEnum in Fortran
    OnsetFirstDay: int = 0
    OnsetFirstMonth: int = 0
    OnsetStartSearchDayNr: int = 0  # daynumber
    OnsetStopSearchDayNr: int = 0   # daynumber
    OnsetLengthSearchPeriod: int = 0  # days
    OnsetThresholdValue: float = 0.0  # degC or degree-days
    OnsetPeriodValue: int = 0         # number of successive days
    OnsetOccurrence: int = 0          # int8: number of occurrences (1,2 or 3)

    # end is generated by air temperature criterion
    GenerateEnd: bool = False
    EndCriterion: int = 0  # intEnum in Fortran
    EndLastDay: int = 0
    EndLastMonth: int = 0
    ExtraYears: int = 0  # number of years to add to the onset year
    EndStartSearchDayNr: int = 0  # daynumber
    EndStopSearchDayNr: int = 0   # daynumber
    EndLengthSearchPeriod: int = 0  # days
    EndThresholdValue: float = 0.0  # degC or degree-days
    EndPeriodValue: int = 0         # number of successive days
    EndOccurrence: int = 0          # int8: number of occurrences (1,2 or 3)

    GeneratedDayNrOnset: int = 0
    GeneratedDayNrEnd: int = 0

#Value for 'undefined' int32 variables
undef_int = np.int32(-9)

# rep_clim variables
ClimRecord = rep_clim()
EToRecord = rep_clim()
RainRecord = rep_clim()
TemperatureRecord = rep_clim()

# rep_sim variables
simulation = rep_sim()
simulparam = rep_param()

# EffectiveRain variables
EffectiveRain = rep_EffectiveRain()

# Soil variables
Soil = rep_soil()
soillayer = [SoilLayerIndividual() for _ in range(max_SoilLayers)]
LayerData = SoilLayerIndividual()

# Compartment variables
Compartment = [CompartmentIndividual() for _ in range(max_No_compartments)]

# Crop variables
crop = rep_Crop()
CropFileSet = rep_CropFileSet()
TotalWaterContent = rep_Content()

# Management variables
Management = rep_Manag()

SumWaBal = rep_sum()

onset = rep_Onset()
endseason = rep_EndSeason()
Cuttings = rep_Cuttings()

IrriBeforeSeason = [rep_DayEventInt(0, 0) for _ in range(5)]
IrriAfterSeason  = [rep_DayEventInt(0, 0) for _ in range(5)]

IrriECw = rep_IrriECw()

perennialperiod = rep_PerennialPeriod()

TotalSaltContent = rep_Content()

def SetTmin(Tmin_in):
    # Setter for the "Tmin" global variable.
    global Tmin
    Tmin = Tmin_in

def GetTmin():
    # Getter for the "Tmin" global variable.
    return Tmin

def SetTmax(Tmax_in):
    # Setter for the "Tmax" global variable.
    global Tmax
    Tmax = Tmax_in

def GetTmax():
    # Getter for the "Tmax" global variable.
    return Tmax

# Calendar -> Functions
def SetCalendarDescription(s: str) -> None:
    # Setter for the "CalendarDescription" global variable.
    global CalendarDescription
    CalendarDescription = s

def GetCalendarDescription():
    # Getter for the "CalendarDescription" global variable.
    return CalendarDescription

def SetCalendarFile(s: str) -> None:
    # Setter for the "CalendarFile" global variable.
    global CalendarFile
    CalendarFile = s

def SetCalendarFileFull(s: str) -> None:
    # Setter for the "CalendarFileFull" global variable.
    global CalendarFileFull
    CalendarFileFull = s

def GetCalendarFileFull():
    # Getter for the "CalendarFileFull" global variable.
    return CalendarFileFull

def GetClimateFileFull():
    # Getter for the "ClimateFileFull" global variable.
    return ClimateFileFull

# Climate -> Functions
def SetClimateDescription(s: str) -> None:
    # Setter for the "ClimateDescription" global variable.
    global ClimateDescription
    ClimateDescription = s

def GetClimateDescription():
    # Getter for the "ClimateDescription" global variable.
    return ClimateDescription

# Posible función repetida
def SetClimDescription(s: str) -> None:
    # Setter for the "ClimDescription" global variable.
    global ClimDescription
    ClimDescription = s

def GetClimDescription():
    # Getter for the "ClimDescription" global variable.
    return ClimDescription

def SetClimateFile(s: str) -> None:
    # Setter for the "ClimateFile" global variable.
    global ClimateFile
    ClimateFile = s

def GetClimateFile():
    # Getter for the "ClimateFile" global variable.
    return ClimateFile

# Posible función repetida
def SetClimFile(s: str) -> None:
    # Setter for the "ClimFile" global variable.
    global ClimFile
    ClimFile = s

def GetClimFile():
    # Getter for the "ClimFile" global variable.
    return ClimFile

def SetClimateFileFull(s: str) -> None:
    # Setter for the "ClimateFileFull" global variable.
    global ClimateFileFull
    ClimateFileFull = s

def SetClimRecord_FromString(s: str) -> None:
    # Setter for the "FromString" attribute of the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.FromString = s

def SetClimRecord_ToString(s: str) -> None:
    # Setter for the "ToString" attribute of the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.ToString = s

def SetClimRecord_NrObs(NrObs):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.NrObs = NrObs

def SetClimRecord_DataType(DataType):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.DataType = DataType

def GetClimRecord_DataType():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.DataType

def SetClimRecord_FromY(FromY):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.FromY = FromY

def SetClimRecord_FromM(FromM):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.FromM = FromM

def SetClimRecord_FromD(FromD):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.FromD = FromD

def GetClimRecord_FromY():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.FromY

def SetClimRecord_FromDayNr(FromDayNr):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.FromDayNr = FromDayNr

def SetClimRecord_ToDayNr(ToDayNr):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.ToDayNr = ToDayNr

def GetClimRecord_FromDayNr():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.FromDayNr

def GetClimRecord_ToDayNr():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.ToDayNr

def SetClimRecord_ToD(ToD):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.ToD = ToD

def SetClimRecord_ToM(ToM):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.ToM = ToM

def SetClimRecord_ToY(ToY):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord.ToY = ToY

def GetClimRecord_FromD():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.FromD

def GetClimRecord_FromM():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.FromM

def GetClimRecord_FromY():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.FromY

def SetClimRecord(ClimRecord_in):
    # Setter for the "ClimRecord" global variable.
    global ClimRecord
    ClimRecord = ClimRecord_in

def GetClimRecord():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord

def GetClimRecord_ToD():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.ToD

def GetClimRecord_ToM():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.ToM

def GetClimRecord_ToY():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.ToY

def GetClimRecord_FromString():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.FromString

def GetClimRecord_ToString():
    # Getter for the "ClimRecord" global variable.
    return ClimRecord.ToString

def GetClimRecord_NrObs():
    # Getter for the "TemperatureRecord" global variable.
    return ClimRecord.NrObs


# CO2 -> Functions
def SetCO2Description(s: str) -> None:
    # Setter for the "CO2Description" global variable.
    global CO2Description
    CO2Description = s

def GetCO2Description():
    # Getter for the "CO2Description" global variable.
    return CO2Description

def GetCO2File():
    # Getter for the "CO2File" global variable.
    return CO2File

def SetCO2File(s: str) -> None:
    # Setter for the "CO2File" global variable.
    global CO2File
    CO2File = s

def GetCO2File():
    # Getter for the "CO2File" global variable.
    return CO2File

def SetCO2FileFull(s: str) -> None:
    # Setter for the "CO2FileFull" global variable.
    global CO2FileFull
    CO2FileFull = s

def GetCO2FileFull():
    # Getter for the "CO2FileFull" global variable.
    return CO2FileFull

def GenerateCO2Description(CO2FileFull, CO2Description):
    with open(complete_path_dir + CO2FileFull.strip(), "r") as fhandle:
        CO2Description = fhandle.readline().strip()

    if GetCO2File().strip() == 'MaunaLoa.CO2':
        # since this is an AquaCrop file, the Description is determined by AquaCrop
        CO2Description = 'Default atmospheric CO2 concentration from 1902 to 2099'

    return CO2Description

# Crop -> Global functions
def SetCropDescription(s: str) -> None:
    # Setter for the "CropDescription" global variable.
    global CropDescription
    CropDescription = s

def GetCropDescription():
    # Getter for the "CropDescription" global variable.
    return CropDescription

def SetCropFile(s: str) -> None:
    # Setter for the "CropFile" global variable.
    global CropFile
    CropFile = s

def GetCropFile():
    # Getter for the "CropFile" global variable.
    return CropFile

def SetCropFileFull(s: str) -> None:
    # Setter for the "CropFileFull" global variable.
    global CropFileFull
    CropFileFull = s

def GetCropFileFull():
    # Getter for the "CropFileFull" attribute of the global "crop" variable.
    return CropFileFull

# ETo -> Global functions
def GetEToDescription() -> str:
    return EToDescription

def SetEToDescription(s: str) -> None:
    # Setter for the "EToDescription" global variable.
    global EToDescription
    EToDescription = s

def SetEToFile(s: str) -> None:
    # Setter for the "EToFile" global variable.
    global EToFile
    EToFile = s

def GetEToFile():
    # Getter for the "EToFile" global variable.
    return EToFile

def GetEToFileFull():
    # Getter for the "EToFileFull" global variable.
    return EToFileFull

def SetEToFileFull(s: str) -> None:
    # Setter for the "EToFileFull" global variable.
    global EToFileFull
    EToFileFull = s

def SetEToRecord_FromString(s: str) -> None:
    # Setter for the "FromString" attribute of the "EToRecord" global variable.
    global EToRecord
    EToRecord.FromString = s

def SetEToRecord_ToString(s: str) -> None:
    # Setter for the "ToString" attribute of the "EToRecord" global variable.
    global EToRecord
    EToRecord.ToString = s

def GetEToRecord_DataType():
    # Getter for the "EToRecord" global variable.
    return EToRecord.DataType

def SetEToRecord_DataType(DataType):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.DataType = DataType

def GetEToRecord_NrObs():
    # Getter for the "EToRecord" global variable.
    return EToRecord.NrObs

def SetEToRecord_NrObs(NrObs):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.NrObs = NrObs

def SetEToRecord_FromD(FromD):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.FromD = FromD

def SetEToRecord_FromM(FromM):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.FromM = FromM

def SetEToRecord_FromY(FromY):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.FromY = FromY

def GetEToRecord_FromY():
    # Getter for the "EToRecord" global variable.
    return EToRecord.FromY

def SetEToRecord_FromDayNr(FromDayNr):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.FromDayNr = FromDayNr

def GetEToRecord_FromDayNr():
    # Getter for the "EToRecord" global variable.
    return EToRecord.FromDayNr

def SetEToRecord_ToDayNr(ToDayNr):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.ToDayNr = ToDayNr

def GetEToRecord_ToDayNr():
    # Getter for the "EToRecord" global variable.
    return EToRecord.ToDayNr

def GetEToRecord_FromString():
    # Getter for the "EToRecord" global variable.
    return EToRecord.FromString

def GetEToRecord_ToString():
    # Getter for the "EToRecord" global variable.
    return EToRecord.ToString

def GetEToRecord_FromD():
    # Getter for the "EToRecord" global variable.
    return EToRecord.FromD

def GetEToRecord_FromM():
    # Getter for the "EToRecord" global variable.
    return EToRecord.FromM

def GetEToRecord_ToD():
    # Getter for the "EToRecord" global variable.
    return EToRecord.ToD

def SetEToRecord_ToD(ToD):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.ToD = ToD

def GetEToRecord_ToM():
    # Getter for the "EToRecord" global variable.
    return EToRecord.ToM

def SetEToRecord_ToM(ToM):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.ToM = ToM

def GetEToRecord_ToY():
    # Getter for the "EToRecord" global variable.
    return EToRecord.ToY

def SetEToRecord_ToY(ToY):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord.ToY = ToY

def SetEToRecord(EToRecord_in):
    # Setter for the "EToRecord" global variable.
    global EToRecord
    EToRecord = EToRecord_in

def GetEToRecord():
    # Getter for the "EToRecord" global variable.
    return EToRecord

# Other functions
def SetFullFileNameProgramParameters(s: str) -> None:
    # Setter for the "FullFileNameProgramParameters" global variable.
    global FullFileNameProgramParameters
    FullFileNameProgramParameters = s

def GetFullFileNameProgramParameters():
    # Getter for the "FullFileNameProgramParameters" global variable.
    return FullFileNameProgramParameters

# Groundwater -> Global functions
def SetGroundWaterDescription(s: str) -> None:
    # Setter for the "GroundwaterDescription" global variable.
    global GroundwaterDescription
    GroundwaterDescription = s

def GetGroundWaterDescription():
    # Getter for the "GroundwaterDescription" global variable.
    return GroundwaterDescription

def GetGroundWaterFile():
    # Getter for the "GroundWaterFile" global variable.
    return GroundWaterFile

def SetGroundWaterFile(s: str) -> None:
    # Setter for the "GroundWaterFile" global variable.
    global GroundWaterFile
    GroundWaterFile = s

def GetGroundWaterFile():
    return GroundWaterFile

def GetGroundWaterFileFull():
    # Getter for the "GroundWaterFileFull" global variable.
    return GroundWaterFileFull

def SetGroundWaterFileFull(s: str) -> None:
    # Setter for the "GroundWaterFileFull" global variable.
    global GroundWaterFileFull
    GroundWaterFileFull = s

def GetGroundWaterFileFull():
    # Getter for the "GroundWaterFilefull" global variable.
    return GroundWaterFileFull

# Irrigation -> Global functions
def GetIrriDescription():
    # Getter for the "IrriDescription" global variable.
    return IrriDescription

def SetIrriDescription(s: str) -> None:
    # Setter for the "IrriDescription" global variable.
    global IrriDescription
    IrriDescription = s

def SetIrriFile(s: str) -> None:
    # Setter for the "IrriFile" global variable.
    global IrriFile
    IrriFile = s

def GetIrriFile():
    # Getter for the "IrriFile" global variable.
    return IrriFile

def SetIrriMethod(int_in):
    # Setter for the "IrriMethod" global variable.
    global IrriMethod
    IrriMethod = int_in

def GetIrriMethod():
    # Getter for the "IrriMethod" global variable.
    return IrriMethod

def GetIrriFileFull():
    # Getter for the "IrriFileFull" global variable.
    return IrriFileFull

def SetIrriFileFull(s: str) -> None:
    # Setter for the "IrriFileFull" global variable.
    global IrriFileFull
    IrriFileFull = s

# Man -> Global functions
def SetManDescription(s: str) -> None:
    # Setter for the "ManDescription" global variable.
    global ManDescription
    ManDescription = s

def GetManDescription():
    # Getter for the "ManDescription" global variable.
    return ManDescription

def SetManFile(s: str) -> None:
    # Setter for the "ManFile" global variable.
    global ManFile
    ManFile = s

def GetManFile():
    # Getter for the "ManFile" global variable.
    return ManFile

def SetManFileFull(s: str) -> None:
    # Setter for the "ManFileFull" global variable.
    global ManFileFull
    ManFileFull = s

def GetManFilefull():
    # Getter for the "ManFileFull" global variable.
    return ManFileFull

# Multiple project -> Global functions
def GetMultipleProjectDescription():
    # Getter for the "MultipleProjectDescription" global variable.
    return MultipleProjectDescription

def SetMultipleProjectDescription(s: str) -> None:
    # Setter for the "MultipleProjectDescription" global variable
    global MultipleProjectDescription
    MultipleProjectDescription = s

def SetMultipleProjectFile(s: str) -> None:
    # Setter for the "MultipleProjectFile" global variable
    global MultipleProjectFile
    MultipleProjectFile = s

def GetMultipleProjectFile():
    # Getter for the "MultipleProjectFile" global variable.
    return MultipleProjectFile

def SetMultipleProjectFileFull(s: str) -> None:
    # Setter for the "MultipleProjectFileFull" global variable
    global MultipleProjectFileFull
    MultipleProjectFileFull = s

def GetMultipleProjectFileFull():
    # Getter for the "MultipleProjectFileFull" global variable.
    return MultipleProjectFileFull

# Observations -> Global functions
def GetObservationsDescription():
    # Getter for the "ObservationsDescription" global variable.
    return ObservationsDescription

def SetObservationsDescription(s: str) -> None:
    # Setter for the "ObservationsDescription" global variable
    global ObservationsDescription
    ObservationsDescription = s

def SetObservationsFile(s: str) -> None:
    # Setter for the "ObservationsFile" global variable
    global ObservationsFile
    ObservationsFile = s

def GetObservationsFile():
    # Getter for the "ObservationsFile" global variable.
    return ObservationsFile

def GetObservationsFilefull():
    # Getter for the "ObservationsFilefull" global variable.
    return ObservationsFilefull

def SetObservationsFilefull(s: str) -> None:
    # Setter for the "ObservationsFilefull" global variable
    global ObservationsFilefull
    ObservationsFilefull = s

# Off season -> Global functions
def SetOffSeasonDescription(s: str) -> None:
    # Setter for the "OffSeasonDescription" global variable
    global OffSeasonDescription
    OffSeasonDescription = s

def GetOffSeasonDescription():
    # Getter for the "OffSeasonDescription" global variable.
    return OffSeasonDescription

def SetOffSeasonFile(s: str) -> None:
    # Setter for the "OffSeasonFile" global variable
    global OffSeasonFile
    OffSeasonFile = s

def GetOffSeasonFile():
    # Getter for the "OffSeasonFile" global variable.
    return OffSeasonFile

def GetOffSeasonFileFull():
    # Getter for the "OffSeasonFileFull" global variable.
    return OffSeasonFilefull

def SetOffSeasonFilefull(s: str) -> None:
    # Setter for the "OffSeasonFilefull" global variable
    global OffSeasonFilefull
    OffSeasonFilefull = s

# Names -> Global functions
def GetOutputName():
    # Getter for the "OutputName" global variable.
    return OutputName

def SetOutputName(s: str) -> None:
    # Setter for the "OutputName" global variable
    global OutputName
    OutputName = s

def SetPathNameList(s: str) -> None:
    # Setter for the "PathNameList" global variable
    global PathNameList
    PathNameList = s

def SetPathNameOutp(s: str) -> None:
    # Setter for the "PathNameOutp" global variable
    global PathNameOutp
    PathNameOutp = s

def GetPathNameParam():
    # Getter for the "PathNameParam" global variable.
    return PathNameParam

def SetPathNameParam(s: str) -> None:
    # Setter for the "PathNameParam" global variable
    global PathNameParam
    PathNameParam = s

def SetPathNameProg(s: str) -> None:
    # Setter for the "PathNameProg" global variable
    global PathNameProg
    PathNameProg = s

def GetPathNameProg():
    # Getter for the "PathNameProg" global variable
    return PathNameProg

def SetPathNameSimul(s: str) -> None:
    # Setter for the "PathNameSimul" global variable
    global PathNameSimul
    PathNameSimul = s

# Prof -> Global functions
def SetProfDescription(s: str) -> None:
    # Setter for the "ProfDescription" global variable
    global ProfDescription
    ProfDescription = s

def GetProfFile():
    # Getter for the "Profile" global variable.
    return ProfFile

def SetProfFile(s: str) -> None:
    # Setter for the "ProfFile" global variable
    global ProfFile
    ProfFile = s

def GetProfFile():
    # Getter for the "ProfFile" global variable.
    return ProfFile

def SetProfFilefull(s: str) -> None:
    # Setter for the "ProfFilefull" global variable
    global ProfFilefull
    ProfFilefull = s

def GetProfFilefull():
    # Getter for the "ProfFilefull" global variable.
    return ProfFilefull

# Project -> Global functions
def SetProjectDescription(s: str) -> None:
    # Setter for the "ProjectDescription" global variable
    global ProjectDescription
    ProjectDescription = s

def GetProjectDescription():
    # Getter for the "ProjectDescription" global variable.
    return ProjectDescription

def SetProjectFile(s: str) -> None:
    # Setter for the "ProjectFile" global variable
    global ProjectFile
    ProjectFile = s

def GetProjectFile():
    # Getter for the "ProjectFile" global variable.
    return ProjectFile

def SetProjectFileFull(s: str) -> None:
    # Setter for the "ProjectFileFull" global variable
    global ProjectFileFull
    ProjectFileFull = s

def GetProjectFileFull():
    # Getter for the "ProjectFileFull" global variable.
    return ProjectFileFull

# Rain -> Global functions
def GetRainDescription():
    # Getter for the "RainDescription" global variable.
    return RainDescription

def SetRainDescription(s: str) -> None:
    # Setter for the "RainDescription" global variable
    global RainDescription
    RainDescription = s

def SetRainFile(s: str) -> None:
    # Setter for the "RainFile" global variable
    global RainFile
    RainFile = s

def GetRainFile():
    # Getter for the "RainFile" global variable.
    return RainFile

def GetRainFileFull():
    # Getter for the "RainFileFull" global variable.
    return RainFileFull

def SetRainFileFull(s: str) -> None:
    # Setter for the "RainFileFull" global variable
    global RainFileFull
    RainFileFull = s

def SetRainRecord_FromString(s: str) -> None:
    # Setter for the "FromString" attribute of the "RainRecord" global variable.
    global RainRecord
    RainRecord.FromString = s

def SetRainRecord_ToString(s: str) -> None:
    # Setter for the "ToString" attribute of the "RainRecord" global variable.
    global RainRecord
    RainRecord.ToString = s

def GetRainRecord_DataType():
    # Getter for the "RainRecord" global variable.
    return RainRecord.DataType

def SetRainRecord_DataType(DataType):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.DataType = DataType

def GetRainRecord_NrObs():
    # Getter for the "RainRecord" global variable.
    return RainRecord.NrObs

def SetRainRecord_NrObs(NrObs):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.NrObs = NrObs

def SetRainRecord_FromD(FromD):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.FromD = FromD

def SetRainRecord_FromM(FromM):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.FromM = FromM

def SetRainRecord_FromY(FromY):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.FromY = FromY

def GetRainRecord_FromY():
    # Getter for the "RainRecord" global variable.
    return RainRecord.FromY

def GetRainRecord_FromDayNr():
    # Getter for the "RainRecord" global variable.
    return RainRecord.FromDayNr

def SetRainRecord_FromDayNr(FromDayNr):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.FromDayNr = FromDayNr

def GetRainRecord_ToDayNr():
    # Getter for the "RainRecord" global variable.
    return RainRecord.ToDayNr

def SetRainRecord_ToDayNr(ToDayNr):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.ToDayNr = ToDayNr

def GetRainRecord_FromString():
    # Getter for the "RainRecord" global variable.
    return RainRecord.FromString

def GetRainRecord_ToString():
    # Getter for the "RainRecord" global variable.
    return RainRecord.ToString

def GetRainRecord_FromD():
    # Getter for the "RainRecord" global variable.
    return RainRecord.FromD

def GetRainRecord_FromM():
    # Getter for the "RainRecord" global variable.
    return RainRecord.FromM

def GetRainRecord_ToD():
    # Getter for the "RainRecord" global variable.
    return RainRecord.ToD

def SetRainRecord_ToD(ToD):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.ToD = ToD

def GetRainRecord_ToM():
    # Getter for the "RainRecord" global variable.
    return RainRecord.ToM

def SetRainRecord_ToM(ToM):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.ToM = ToM

def GetRainRecord_ToY():
    # Getter for the "RainRecord" global variable.
    return RainRecord.ToY

def SetRainRecord_ToY(ToY):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord.ToY = ToY

def SetRainRecord(RainRecord_in):
    # Setter for the "RainRecord" global variable.
    global RainRecord
    RainRecord = RainRecord_in

def GetRainRecord():
    # Getter for the "RainRecord" global variable.
    return RainRecord

# Simulation -> Global functions
def GetSimulation():
    # Getter for the "simulation" global variable.
    return simulation

def SetSimulation(simulation_in):
    # Setter for the "simulation" global variable.
    global simulation
    simulation = simulation_in

def GetSimulation_Storage():
    # Getter for the "Storage" attribute of the "simulation" global variable.
    return simulation.Storage

def GetSimulation_DayNrPrematureEnd():
    # Getter for the "DayNrPrematureEnd" attribute of the "simulation" global variable.
    return simulation.DayNrPrematureEnd

def SetSimulation_DayNrPrematureEnd(DayNrPrematureEnd):
    # Setter for the "DayNrPrematureEnd" attribute of the "simulation" global variable.
    global simulation
    simulation.DayNrPrematureEnd = DayNrPrematureEnd

def SetSimulation_Storage(Storage_in):
    # Setter for the "Storage" attribute of the "simulation" global variable.
    global simulation
    simulation.Storage = Storage_in

def GetSimulation_Storage_Btotal():
    # Getter for the "Btotal" attribute of the "Storage" attribute of the "simulation" global variable.
    return simulation.Storage.Btotal

def SetSimulation_Storage_Btotal(Btotal):
    # Setter for the "Btotal" attribute of the "Storage" attribute of the "simulation" global variable.
    global simulation
    simulation.Storage.Btotal = Btotal

def SetSimulation_Storage_CropString(s: str) -> None:
    # Setter for the "CropString" attribute of the "Storage" attribute of the "simulation" global variable.
    global simulation
    simulation.Storage.CropString = s

def GetSimulation_Storage_CropString():
    # Getter for the "CropString" attribute of the "Storage" attribute of the "simulation" global variable.
    return simulation.Storage.CropString

def GetSimulation_Storage_Season():
    # Getter for the "Season" attribute of the "Storage" attribute of the "simulation" global variable.
    return simulation.Storage.Season

def SetSimulation_Storage_Season(Season):
    # Setter for the "Season" attribute of the "Storage" attribute of the "simulation" global variable.
    global simulation
    simulation.Storage.Season = Season

def SetSimulation_ResetIniSWC(ResetIniSWC):
    # Setter for the "ResetIniSWC" attribute of the "simulation" global variable.
    global simulation
    simulation.ResetIniSWC = ResetIniSWC

def GetSimulation_ResetIniSWC():
    # Getter for the "ResetIniSWC" attribute of the "simulation" global variable.
    return simulation.ResetIniSWC

def SetSimulation_ThetaIni_i(i, ThetaIni_i):
    # Setter for the "ThetaIni" attribute of the "simulation" global variable.
    global simulation
    i0 = i - 1
    simulation.ThetaIni[i0] = ThetaIni_i

def GetSimulation_ECeIni_i(i):
    # Getter for the "ECeIni" attribute of the "simulation" global variable.
    i0 = i - 1
    return simulation.ECeIni[i0]

def SetSimulation_ECeIni_i(i, ECeIni_i):
    # Setter for the "ECeIni" attribute of the "simulation" global variable.
    global simulation
    i0 = i - 1
    simulation.ECeIni[i0] = ECeIni_i

def GetSimulation_ThetaIni_i(i):
    # Getter for the "ThetaIni" attribute of the "simulation" global variable.
    i0 = i - 1
    return simulation.ThetaIni[i0]

def GetSimulation_IniSWC():
    # Getter for the "IniSWC" attribute of the "simulation" global variable.
    return simulation.IniSWC

def SetSimulation_IniSWC(IniSWC_in):
    # Setter for the "IniSWC" attribute of the "simulation" global variable.
    global simulation
    simulation.IniSWC = IniSWC_in

def SetSimulation_IniSWC_AtDepths(AtDepths):
    # Setter for the "AtDepths" attribute of the "IniSWC" attribute of the "simulation" global variable.
    global simulation
    simulation.IniSWC.AtDepths = AtDepths

def SetSimulation_IniSWC_NrLoc(NrLoc):
    # Setter for the "NrLoc" attribute of the "IniSWC" attribute of the "simulation" global variable.
    global simulation
    simulation.IniSWC.NrLoc = NrLoc

def GetSimulation_IniSWC_Loc_i(i):
    # Getter for the "Loc" attribute of the "IniSWC" attribute of the "simulation" global variable.
    i0 = i - 1
    return simulation.IniSWC.Loc[i0]

def SetSimulation_IniSWC_Loc_i(i, Loc_i):
    # Setter for the "Loc" attribute of the "IniSWC" attribute of the "simulation" global variable.
    global simulation
    i0 = i - 1
    simulation.IniSWC.Loc[i0] = Loc_i

def GetSimulation_IniSWC_VolProc_i(i):
    # Getter for the "VolProc" attribute of the "IniSWC" attribute of the "simulation" global variable
    i0 = i - 1
    return simulation.IniSWC.VolProc[i0]

def SetSimulation_IniSWC_VolProc_i(i, VolProc_i):
    # Setter for the "VolProc" attribute of the "IniSWC" attribute of the "simulation" global variable.
    global simulation
    i0 = i - 1
    simulation.IniSWC.VolProc[i0] = VolProc_i

def GetSimulation_IniSWC_SaltECe_i(i):
    # Getter for the "SaltECe" attribute of the "IniSWC" attribute of the "simulation" global variable
    i0 = i - 1
    return simulation.IniSWC.SaltECe[i0]

def SetSimulation_IniSWC_SaltECe_i(i, SaltECe_i):
    # Setter for the "SaltECe" attribute of the "IniSWC" attribute of the "simulation" global variable.
    global simulation
    i0 = i - 1
    simulation.IniSWC.SaltECe[i0] = SaltECe_i

def GetSimulation_DayAnaero():
    # Setter for the "DayAnaero" attribute of the "simulation" global variable.
    return simulation.DayAnaero

def SetSimulation_DayAnaero(DayAnaero):
    # Setter for the "DayAnaero" attribute of the "simulation" global variable.
    global simulation
    simulation.DayAnaero = DayAnaero

def SetSimulation_CCini(CCini):
    # Setter for the "CCini" attribute of the "simulation" global variable.
    global simulation
    simulation.CCini = CCini

def GetSimulation_CCini():
    # Getter for the "CCini" attribute of the "simulation" global variable.
    return simulation.CCini

def SetSimulation_Bini(Bini):
    # Setter for the "Bini" attribute of the "simulation" global variable.
    global simulation
    simulation.Bini = Bini

def GetSimulation_Bini():
    # Getter for the "Bini" attribute of the "simulation" global variable.
    return simulation.Bini

def SetSimulation_Zrini(Zrini):
    # Setter for the "Zrini" attribute of the "simulation" global variable.
    global simulation
    simulation.Zrini = Zrini

def GetSimulation_Zrini():
    # Getter for the "Zrini" attribute of the "simulation" global variable.
    return simulation.Zrini

def GetSimulation_FromDayNr():
    # Getter for the "FromDayNr" attribute of the "simulation" global variable.
    return simulation.FromDayNr

def SetSimulation_FromDayNr(FromDayNr):
    # Getter for the "FromDayNr" attribute of the "simulation" global variable.
    global simulation
    simulation.FromDayNr = FromDayNr

def GetSimulation_ToDayNr():
    # Getter for the "ToDayNr" attribute of the "simulation" global variable.
    return simulation.ToDayNr

def SetSimulation_ToDayNr(ToDayNr):
    # Getter for the "ToDayNr" attribute of the "simulation" global variable.
    global simulation
    simulation.ToDayNr = ToDayNr

def SetSimulation_IrriECw(IrriECw):
    # Setter for the "IrriECw" attribute of the "simulation" global variable.
    global simulation
    simulation.IrriECw = IrriECw

def GetSimulation_IrriECw():
    # Getter for the "IrriECw" attribute of the "simulation" global variable.
    return simulation.IrriECw

def SetGenerateTimeMode(int_in):
    # Setter for the "GenerateTimeMode" global variable.
    global GenerateTimeMode
    GenerateTimeMode = int_in

def SetGenerateDepthMode(int_in):
    # Setter for the "GenerateTimeMode" global variable.
    global GenerateDepthMode
    GenerateDepthMode = int_in

# SWCiniDescription -> Global functions
def GetSWCiniDescription():
    # Getter for the "SWCiniDescription" global variable.
    return SWCiniDescription

def SetSWCiniDescription(s: str) -> None:
    # Setter for the "SWCiniDescription" global variable
    global SWCiniDescription
    SWCiniDescription = s

def SetSWCIniFile(s: str) -> None:
    # Setter for the "SWCiniFile" global variable
    global SWCiniFile
    SWCiniFile = s

def GetSWCiniFile():
    # Getter for the "SWCiniFile" global variable.
    return SWCiniFile

def GetSWCiniFileFull():
    # Getter for the "SWCiniFileFull" global variable.
    return SWCiniFileFull

def SetSWCiniFileFull(s: str) -> None:
    # Setter for the "SWCiniFileFull" global variable
    global SWCiniFileFull
    SWCiniFileFull = s

# Temperature -> Global functions
def SetTemperatureDescription(s: str) -> None:
    # Setter for the "TemperatureDescription" global variable
    global TemperatureDescription
    TemperatureDescription = s

def GetTemperatureDescription():
    # Getter for the "TemperatureDescription" global variable.
    return TemperatureDescription

def SetTemperatureFile(s: str) -> None:
    # Setter for the "TemperatureFile" global variable
    global TemperatureFile
    TemperatureFile = s

def GetTemperatureFile():
    # Getter for the "TemperatureFile" global variable.
    return TemperatureFile

def SetTemperatureFileFull(s: str) -> None:
    # Setter for the "TemperatureFileFull" global variable
    global TemperatureFileFull
    TemperatureFileFull = s

def GetTemperatureFileFull():
    # Getter for the "TemperatureFileFull" global variable.
    return TemperatureFileFull

def SetTemperatureRecord(rec_in):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord = rec_in

def SetTemperatureRecord_FromString(s: str) -> None:
    # Setter for the "FromString" attribute of the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.FromString = s

def SetTemperatureRecord_ToString(s: str) -> None:
    # Setter for the "ToString" attribute of the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.ToString = s

def SetTemperatureRecord_DataType(DataType):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.DataType = DataType

def GetTemperatureRecord_DataType():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.DataType

def GetTemperatureRecord_NrObs():
    # Getter for the "NrObs" attribute of the "TemperatureRecord" global variable.
    return TemperatureRecord.NrObs

def SetTemperatureRecord_NrObs(NrObs):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.NrObs = NrObs

def SetTemperatureRecord_FromY(FromY):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.FromY = FromY

def GetTemperatureRecord_FromY():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.FromY

def SetTemperatureRecord_FromD(FromD_in):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.FromD = FromD_in

def GetTemperatureRecord_FromD():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.FromD

def SetTemperatureRecord_FromM(FromM_in):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.FromD = FromM_in

def GetTemperatureRecord_FromM():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.FromM

def SetTemperatureRecord_FromDayNr(FromDayNr_in):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.FromDayNr = FromDayNr_in

def GetTemperatureRecord_FromDayNr():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.FromDayNr

def SetTemperatureRecord_ToDayNr(ToDayNr_in):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.ToDayNr = ToDayNr_in

def GetTemperatureRecord_ToDayNr():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.ToDayNr

def GetTemperatureRecord_FromString():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.FromString

def GetTemperatureRecord_FromString():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.FromString

def GetTemperatureRecord_ToString():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.ToString

def SetTemperatureRecord_ToD(ToD_in):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.ToD = ToD_in

def GetTemperatureRecord_ToD():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.ToD

def SetTemperatureRecord_ToM(ToM_in):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.ToM = ToM_in

def GetTemperatureRecord_ToM():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.ToM

def SetTemperatureRecord_ToY(ToY_in):
    # Setter for the "TemperatureRecord" global variable.
    global TemperatureRecord
    TemperatureRecord.ToY = ToY_in

def GetTemperatureRecord_ToY():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord.ToY

def GetTemperatureRecord():
    # Getter for the "TemperatureRecord" global variable.
    return TemperatureRecord

# TnxReference -> Global functions
def GetTnxReference365DaysFile():
    # Getter for the "TnxReference365DaysFile" global variable.
    return TnxReference365DaysFile

def SetTnxReference365DaysFile(s: str) -> None:
    # Setter for the "TnxReference365DaysFile" global variable
    global TnxReference365DaysFile
    TnxReference365DaysFile = s

def GetTnxReference365DaysFileFull():
    # Getter for the "TnxReference365DaysFileFull" global variable.
    return TnxReference365DaysFileFull

def SetTnxReference365DaysFileFull(s: str) -> None:
    # Setter for the "TnxReference365DaysFileFull" global variable
    global TnxReference365DaysFileFull
    TnxReference365DaysFileFull = s

def SetTnxReferenceFile(s: str) -> None:
    # Setter for the "TnxReferenceFile" global variable
    global TnxReferenceFile
    TnxReferenceFile = s

def GetTnxReferenceFile():
    # Getter for the "TnxReferenceFile" global variable.
    return TnxReferenceFile

def GetTnxReferenceFileFull():
    # Getter for the "TnxReferenceFileFull" global variable.
    return TnxReferenceFileFull

def SetTnxReferenceFileFull(s: str) -> None:
    # Setter for the "TnxReferenceFileFull" global variable
    global TnxReferenceFileFull
    TnxReferenceFileFull = s

def SetTnxReferenceYear(TnxReferenceYear_in):
    # Setter for the "TnxReferenceYear" global variable.
    global TnxReferenceYear
    TnxReferenceYear = TnxReferenceYear_in

def GetTnxReferenceYear():
    # Getter for the "TnxReferenceYear" global variable.
    return TnxReferenceYear

# Boolean variables setters
def SetEvapoEntireSoilSurface(b: bool) -> None:
    # Setter for the 'EvapoEntireSoilSurface' global variable
    global EvapoEntireSoilSurface
    EvapoEntireSoilSurface = b

def SetPreDay(b: bool) -> None:
    # Setter for the 'PreDay' global variable
    global PreDay
    PreDay = b

def SetOutDaily(b: bool) -> None:
    # Setter for the 'OutDaily' global variable
    global OutDaily
    OutDaily = b

def SetOut8Irri(b: bool) -> None:
    # Setter for the 'Out8Irri' global variable
    global Out8Irri
    Out8Irri = b

def SetOut1Wabal(b: bool) -> None:
    # Setter for the 'Out1Wabal' global variable
    global Out1Wabal
    Out1Wabal = b

def SetOut2Crop(b: bool) -> None:
    # Setter for the 'Out2Crop' global variable
    global Out2Crop
    Out2Crop = b

def SetOut3Prof(b: bool) -> None:
    # Setter for the 'Out3Prof' global variable
    global Out3Prof
    Out3Prof = b

def SetOut4Salt(b: bool) -> None:
    # Setter for the 'Out4Salt' global variable
    global Out4Salt
    Out4Salt = b

def SetOut5CompWC(b: bool) -> None:
    # Setter for the 'Out5CompWC' global variable
    global Out5CompWC
    Out5CompWC = b

def SetOut6CompEC(b: bool) -> None:
    # Setter for the 'Out6CompEC' global variable
    global Out6CompEC
    Out6CompEC = b

def SetOut7Clim(b: bool) -> None:
    # Setter for the 'Out7Clim' global variable
    global Out7Clim
    Out7Clim = b

def SetPart1Mult(b: bool) -> None:
    # Setter for the 'Part1Mult' global variable
    global Part1Mult
    Part1Mult = b

def SetPart2Eval(b: bool) -> None:
    # Setter for the 'Part2Eval' global variable
    global Part2Eval
    Part2Eval = b

# Boolean variables getters
def GetEvapoEntireSoilSurface() -> bool:
    # Getter for the 'EvapoEntireSoilSurface' global variable
    return EvapoEntireSoilSurface

def GetPreDay() -> bool:
    # Getter for the 'PreDay' global variable
    return PreDay

def GetOutDaily() -> bool:
    # Getter for the 'OutDaily' global variable
    return OutDaily

def GetOut8Irri() -> bool:
    # Getter for the 'Out8Irri' global variable
    return Out8Irri

def GetOut1Wabal() -> bool:
    # Getter for the 'Out1Wabal' global variable
    return Out1Wabal

def GetOut2Crop() -> bool:
    # Getter for the 'Out2Crop' global variable
    return Out2Crop

def GetOut3Prof() -> bool:
    # Getter for the 'Out3Prof' global variable
    return Out3Prof

def GetOut4Salt() -> bool:
    # Getter for the 'Out4Salt' global variable
    return Out4Salt

def GetOut5CompWC() -> bool:
    # Getter for the 'Out5CompWC' global variable
    return Out5CompWC

def GetOut6CompEC() -> bool:
    # Getter for the 'Out6CompEC' global variable
    return Out6CompEC

def GetOut7Clim() -> bool:
    # Getter for the 'Out7Clim' global variable
    return Out7Clim

def GetPart1Mult() -> bool:
    # Getter for the 'Part1Mult' global variable
    return Part1Mult

def GetPart2Eval() -> bool:
    # Getter for the 'Part2Eval' global variable
    return Part2Eval

def GetPathNameOutp() -> str:
    # Getter for the "PathNameOutp" global variable.
    return PathNameOutp

def GetPathNameList() -> str:
    # Getter for the "PathNameList" global variable.
    return PathNameList

# Simulparam setters
def GetSimulParam():
    # Getter for the "simulparam" global variable.
    return simulparam

def SetSimulParam(simulparam_in):
    # Setter for the "simulparam" global variable.
    global simulparam
    simulparam = simulparam_in

def SetSimulParam_PercRAW(PercRAW):
    # Setter for the "PercRAW" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.PercRAW = PercRAW

def SetSimulParam_CompDefThick(CompDefThick):
    # Setter for the "CompDefThick" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.CompDefThick = CompDefThick

def GetSimulParam_CompDefThick():
    # Getter for the "CompDefThick" attribute of the "simulparam" global variable.
    return simulparam.CompDefThick

def SetSimulParam_CropDay1(CropDay1):
    # Setter for the "CropDay1" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.CropDay1 = CropDay1

def GetSimulParam_CropDay1():
    # Getter for the "CropDay1" attribute of the "simulparam" global variable.
    return simulparam.CropDay1

def SetSimulParam_Tbase(Tbase):
    # Setter for the "Tbase" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.Tbase = Tbase

def SetSimulParam_Tupper(Tupper):
    # Setter for the "Tupper" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.Tupper = Tupper

def SetSimulParam_IrriFwInSeason(IrriFwInSeason):
    # Setter for the "IrriFwInSeason" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.IrriFwInSeason = IrriFwInSeason

def SetSimulParam_IrriFwOffSeason(IrriFwOffSeason):
    # Setter for the "IrriFwOffSeason" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.IrriFwOffSeason = IrriFwOffSeason

def SetSimulParam_RunoffDepth(RunoffDepth):
    # Setter for the "RunoffDepth" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.RunoffDepth = RunoffDepth

def SetSimulParam_CNcorrection(CNcorrection):
    # Setter for the "CNcorrection" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.CNcorrection = CNcorrection

def SetSimulParam_SaltDiff(SaltDiff):
    # Setter for the "SaltDiff" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.SaltDiff = SaltDiff

def GetSimulParam_SaltDiff():
    # Getter for the "SaltDiff" attribute of the "simulparam" global variable.
    return simulparam.SaltDiff

def GetSimulParam_SaltSolub():
    # Getter for the "SaltSolub" attribute of the "simulparam" global variable.
    return simulparam.SaltSolub

def SetSimulParam_SaltSolub(SaltSolub):
    # Setter for the "SaltSolub" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.SaltSolub = SaltSolub

def SetSimulParam_RootNrDF(RootNrDF):
    # Setter for the "RootNrDF" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.RootNrDF = RootNrDF

def SetSimulParam_IniAbstract(IniAbstract):
    # Setter for the "IniAbstract" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.IniAbstract = IniAbstract

def GetSimulParam_EvapDeclineFactor():
    # Getter for the "EvapDeclineFactor" attribute of the "simulparam
    global simulparam
    return simulparam.EvapDeclineFactor

def SetSimulParam_EvapDeclineFactor(EvapDeclineFactor):
    # Setter for the "EvapDeclineFactor" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.EvapDeclineFactor = EvapDeclineFactor

def GetSimulParam_EffectiveRain():
    # Getter for the "EffectiveRain" attribute of the "simulparam" global variable
    return simulparam.EffectiveRain

def SetSimulParam_EffectiveRain(EffRain):
    # Setter for the "EffectiveRain" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.EffectiveRain = EffRain

def SetSimulParam_KcWetBare(KcWetBare):
    # Setter for the "KcWetBare" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.KcWetBare = KcWetBare

def SetSimulParam_PercCCxHIfinal(PercCCxHIfinal):
    # Setter for the "PercCCxHIfinal" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.PercCCxHIfinal = PercCCxHIfinal

def SetSimulParam_RootPercentZmin(RootPercentZmin):
    # Setter for the "RootPercentZmin" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.RootPercentZmin = RootPercentZmin

def SetSimulParam_MaxRootZoneExpansion(MaxRootZoneExpansion):
    # Setter for the "MaxRootZoneExpansion" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.MaxRootZoneExpansion = MaxRootZoneExpansion

def SetSimulParam_KsShapeFactorRoot(KsShapeFactorRoot):
    # Setter for the "KsShapeFactorRoot" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.KsShapeFactorRoot = KsShapeFactorRoot

def SetSimulParam_TAWGermination(TAWGermination):
    # Setter for the "TAWGermination" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.TAWGermination = TAWGermination

def SetSimulParam_pAdjFAO(pAdjFAO):
    # Setter for the "pAdjFAO" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.pAdjFAO = pAdjFAO

def SetSimulParam_DelayLowOxygen(DelayLowOxygen):
    # Setter for the "DelayLowOxygen" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.DelayLowOxygen = DelayLowOxygen

def SetSimulParam_ExpFsen(ExpFsen):
    # Setter for the "ExpFsen" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.ExpFsen = ExpFsen

def SetSimulParam_Beta(Beta):
    # Setter for the "Beta" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.Beta = Beta

def SetSimulParam_ThicknessTopSWC(ThicknessTopSWC):
    # Setter for the "ThicknessTopSWC" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.ThicknessTopSWC = ThicknessTopSWC

def SetSimulParam_EvapZmax(EvapZmax):
    # Setter for the "EvapZmax" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.EvapZmax = EvapZmax

def SetSimulParam_Tmin(Tmin):
    # Setter for the "Tmin" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.Tmin = Tmin

def SetSimulParam_Tmax(Tmax):
    # Setter for the "Tmax" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.Tmax = Tmax

def SetSimulParam_GDDMethod(GDDMethod):
    # Setter for the "GDDMethod" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.GDDMethod = GDDMethod

def GetSimulParam_GDDMethod():
    # Getter for the "GDDMethod" attribute of the "simulparam" global variable.
    return simulparam.GDDMethod

def SetSimulParam_ConstGwt(ConstGwt):
    # Setter for the "ConstGwt" attribute of the "simulparam" global variable.
    global simulparam
    simulparam.ConstGwt = ConstGwt

def GetSimulParam_ConstGwt():
    # Getter for the "ConstGwt" attribute of the "simulparam" global variable.
    return simulparam.ConstGwt

def GetSimulParam_Tmin():
    # Getter for the "Tmin" attribute of the "simulparam" global variable.
    return simulparam.Tmin

def GetSimulParam_Tmax():
    # Getter for the "Tmax" attribute of the "simulparam" global variable.
    return simulparam.Tmax

def GetSimulParam_KcWetBare():
    # Getter for the "KcWetBare" attribute of the "simulparam" global variable
    return simulparam.KcWetBare

def GetSimulParam_PercCCxHIfinal():
    # Getter for the "PercCCxHIfinal" attribute of the "simulparam" global variable
    return simulparam.PercCCxHIfinal

def GetSimulParam_RootPercentZmin():
    # Getter for the "RootPercentZmin" attribute of the "simulparam" global variable
    return simulparam.RootPercentZmin

def GetSimulParam_MaxRootZoneExpansion():
    # Getter for the "MaxRootZoneExpansion" attribute of the "simulparam" global variable
    return simulparam.MaxRootZoneExpansion

def GetSimulParam_KsShapeFactorRoot():
    # Getter for the "KsShapeFactorRoot" attribute of the "simulparam" global variable
    return simulparam.KsShapeFactorRoot

def GetSimulParam_TAWGermination():
    # Getter for the "TAWGermination" attribute of the "simulparam" global variable
    return simulparam.TAWGermination

def GetSimulParam_pAdjFAO():
    # Getter for the "pAdjFAO" attribute of the "simulparam" global variable
    return simulparam.pAdjFAO

def GetSimulParam_DelayLowOxygen():
    # Getter for the "DelayLowOxygen" attribute of the "simulparam" global variable
    return simulparam.DelayLowOxygen

def GetSimulParam_ExpFsen():
    # Getter for the "ExpFsen" attribute of the "simulparam" global variable
    return simulparam.ExpFsen

def GetSimulParam_Beta():
    # Getter for the "Beta" attribute of the "simulparam" global variable
    return simulparam.Beta

def GetSimulParam_ThicknessTopSWC():
    # Getter for the "ThicknessTopSWC" attribute of the "simulparam" global variable
    return simulparam.ThicknessTopSWC

def GetSimulParam_EvapZmax():
    # Getter for the "EvapZmax" attribute of the "simulparam" global variable
    return simulparam.EvapZmax

def GetSimulParam_RunoffDepth():
    # Getter for the "RunoffDepth" attribute of the "simulparam" global variable
    return simulparam.RunoffDepth

def GetSimulParam_CNcorrection():
    # Getter for the "CNcorrection" attribute of the "simulparam" global variable
    return simulparam.CNcorrection

def GetSimulParam_PercRAW():
    # Getter for the "PercRAW" attribute of the "simulparam" global variable
    return simulparam.PercRAW

def GetSimulParam_CropDay1():
    # Getter for the "CropDay1" attribute of the "simulparam" global variable
    return simulparam.CropDay1

def GetSimulParam_Tbase():
    # Getter for the "Tbase" attribute of the "simulparam" global variable
    return simulparam.Tbase

def GetSimulParam_Tupper():
    # Getter for the "Tupper" attribute of the "simulparam" global variable
    return simulparam.Tupper

def GetSimulParam_IrriFwInSeason():
    # Getter for the "IrriFwInSeason" attribute of the "simulparam" global variable
    return simulparam.IrriFwInSeason

def GetSimulParam_ConstGwt():
    # Getter for the "ConstGwt" attribute of the "simulparam" global variable
    return simulparam.ConstGwt

def GetSimulParam_RootNrDF():
    # Getter for the "RootNrDF" attribute of the "simulparam" global variable
    return simulparam.RootNrDF

def GetSimulParam_IniAbstract():
    # Getter for the "IniAbstract" attribute of the "simulparam" global variable
    return simulparam.IniAbstract

# EffectiveRain setters
def Geteffectiverain():
    # Getter for the "EffectiveRain" global variable.
    return EffectiveRain

def Seteffectiverain(EffectiveRain_in):
    # Setter for the "EffectiveRain" global variable.
    global EffectiveRain
    EffectiveRain = EffectiveRain_in

def Geteffectiverain_Method():
    # Getter for the "Method" attribute of the "EffectiveRain" global variable.
    return EffectiveRain.Method

def Seteffectiverain_Method(Method_in):
    # Setter for the "Method" attribute of the "EffectiveRain" global variable.
    global EffectiveRain
    EffectiveRain.Method = Method_in

def Geteffectiverain_PercentEffRain():
    # Getter for the "PercentEffRain" attribute of the "EffectiveRain" global variable.
    return EffectiveRain.PercentEffRain

def Seteffectiverain_PercentEffRain(PercentEffRain_in):
    # Setter for the "PercentEffRain" attribute of the "EffectiveRain" global variable.
    global EffectiveRain
    EffectiveRain.PercentEffRain = PercentEffRain_in

def Geteffectiverain_ShowersInDecade():
    # Getter for the "ShowersInDecade" attribute of the "EffectiveRain" global variable.
    return EffectiveRain.ShowersInDecade

def Seteffectiverain_ShowersInDecade(ShowersInDecade_in):
    # Setter for the "ShowersInDecade" attribute of the "EffectiveRain" global variable.
    global EffectiveRain
    EffectiveRain.ShowersInDecade = ShowersInDecade_in

def Geteffectiverain_RootNrEvap():
    # Getter for the "RootNrEvap" attribute of the "EffectiveRain" global variable.
    return EffectiveRain.RootNrEvap

def Seteffectiverain_RootNrEvap(RootNrEvap_in):
    # Setter for the "RootNrEvap" attribute of the "EffectiveRain" global variable.
    global EffectiveRain
    EffectiveRain.RootNrEvap = RootNrEvap_in

def GetSimulParam_EffectiveRain_Method():
    # Getter for the "Method" attribute of the "EffectiveRain" global variable.
    return EffectiveRain.Method

def SetSimulParam_EffectiveRain_Method(Method):
    # Setter for the "EffectiveRain" global variable.
    global EffectiveRain
    EffectiveRain.Method = Method

def GetSimulParam_EffectiveRain_PercentEffRain():
    # Getter for the "PercentEffRain" attribute of the "EffectiveRain" global variable.
    return EffectiveRain.PercentEffRain

def SetSimulParam_EffectiveRain_PercentEffRain(PercentEffRain):
    # Setter for the "EffectiveRain" global variable.
    global EffectiveRain
    EffectiveRain.PercentEffRain = PercentEffRain

def GetSimulParam_EffectiveRain_ShowersInDecade():
    # Getter for the "ShowersInDecade" attribute of the "EffectiveRain" global variable.
    return EffectiveRain.ShowersInDecade

def SetSimulParam_EffectiveRain_ShowersInDecade(ShowersInDecade):
    # Setter for the "EffectiveRain" global variable.
    global EffectiveRain
    EffectiveRain.ShowersInDecade= ShowersInDecade

def GetSimulParam_EffectiveRain_RootNrEvap():
    # Getter for the "RootNrEvap" attribute of the "EffectiveRain" global variable.
    return EffectiveRain.RootNrEvap

def SetSimulParam_EffectiveRain_RootNrEvap(RootNrEvap):
    # Setter for the "EffectiveRain" global variable.
    global EffectiveRain
    EffectiveRain.RootNrEvap= RootNrEvap


# Soil setters
def SetSoil_CNvalue(CNvalue):
    # Setter for the "Soil" global variable.
    global Soil
    Soil.CNvalue = CNvalue

def SetSoil_REW(REW):
    # Setter for the "Soil" global variable.
    global Soil
    Soil.REW = REW

def SetSoil_NrSoilLayers(NrSoilLayers):
    # Setter for the "Soil" global variable.
    global Soil
    Soil.NrSoilLayers = NrSoilLayers

def SetSoilLayer_SAT(i, SAT):
    # Setter for the "SAT" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].SAT = SAT

def GetSoilLayer_SAT(i):
    # Getter for the "SAT" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].SAT

def SetSoilLayer_FC(i, FC):
    # Setter for the "FC" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].FC = FC

def GetSoilLayer_FC(i):
    # Getter for the "FC" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].FC

def SetSoilLayer_WP(i, WP):
    # Setter for the "WP" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].WP = WP

def GetSoilLayer_WP(i):
    # Getter for the "WP" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].WP

def SetSoilLayer_tau(i, tau):
    # Setter for the "tau" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].tau = tau

def GetSoilLayer_tau(i):
    # Getter for the "tau" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].tau

def SetSoilLayer_InfRate(i, InfRate):
    # Setter for the "InfRate" attribute of the "soillayer" global variable
    global soillayer
    i0 = i - 1
    soillayer[i0].InfRate = InfRate

def GetSoilLayer_InfRate(i):
    # Getter for the "InfRate" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].InfRate

def SetSoilLayer_Penetrability(i, Penetrability):
    # Setter for the "Penetrability" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].Penetrability = Penetrability

def SetSoilLayer_GravelMass(i, GravelMass):
    # Setter for the "GravelMass" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].GravelMass = GravelMass

def SetSoilLayer_GravelVol(i, GravelVol):
    # Setter for the "GravelVol" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].GravelVol = GravelVol

def GetSoilLayer_GravelVol(i):
    # Getter for the "GravelVol" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].GravelVol

def SetSoilLayer_Description(i, Description):
    # Setter for the "Description" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].Description = Description

def SetSoilLayer_SoilClass(i, SoilClass):
    # Setter for the "SoilClass" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].SoilClass = SoilClass

def SetSoilLayer_Thickness(i, Thickness):
    # Setter for the "Thickness" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].Thickness = Thickness

def GetSoilLayer_SoilClass(i):
    # Getter for the "SoilClass" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].SoilClass

def GetSoilLayer_CRa(i):
    # Getter for the "CRa" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].CRa

def SetSoilLayer_CRa(i, CRa):
    # Setter for the "CRa" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].CRa = CRa

def GetSoilLayer_CRb(i):
    # Getter for the "CRb" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].CRb

def SetSoilLayer_CRb(i, CRb):
    # Setter for the "CRb" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].CRb = CRb

def GetSoilLayer_SCP1(i):
    # Getter for the "SCP1" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].SCP1

def SetSoilLayer_SCP1(i, SCP1):
    # Setter for the "SCP1" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].SCP1 = SCP1

def GetSoilLayer_SC(i):
    # Getter for the "SC" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].SC

def SetSoilLayer_UL(i, UL):
    # Setter for the "UL" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].UL = UL

def GetSoilLayer_UL(i):
    # Getter for the "UL" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].UL

def SetSoilLayer_Dx(i, Dx):
    # Setter for the "Dx" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].Dx = Dx

def GetSoilLayer_Dx(i):
    # Getter for the "Dx" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].Dx

def SetSoilLayer_SaltMobility(i, SaltMobility):
    # Setter for the "SaltMobility" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].SaltMobility = SaltMobility


def GetSoilLayer_SaltMobility(i):
    # Getter for the "SaltMobility" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].SaltMobility


def SetSoilLayer_SC(i, SC):
    # Setter for the "SC" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].SC = SC

def SetSoilLayer_Macro(i, Macro):
    # Setter for the "Macro" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].Macro = Macro

def GetSoilLayer_Macro(i):
    # Getter for the "Macro" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].Macro

def SetSoilLayer(SoilLayer_in):
    # Setter for the "soillayer" global variable.
    global soillayer
    soillayer = SoilLayer_in

def SetTotalWaterContent(TotalWaterContent_in):
    # Setter for the TotalWaterContent global variable.
    global TotalWaterContent
    TotalWaterContent = TotalWaterContent_in

def SetCompartment(Compartment_in):
    # Setter for the "compartment" global variable.
    global Compartment
    Compartment = Compartment_in

def SetNrCompartments(NrCompartments_in):
    # Setter for the "NrCompartments" global variable.
    global NrCompartments
    NrCompartments = NrCompartments_in

def GetNrCompartments():
    # Getter for the "NrCompartments" global variable.
    return NrCompartments

def GetIniPercTAW():
    # Getter for the "IniPercTAW" global variable.
    return IniPercTAW

def SetIniPercTAW(IniPercTAW_in):
    # Setter for the "IniPercTAW" global variable.
    global IniPercTAW
    IniPercTAW = IniPercTAW_in

def GetCompartment():
    # Getter for "Compartment" global variable.
    return Compartment

def GetCompartment_i(i):
    # Getter for individual element of the "Compartment" global variable.
    i0 = i - 1
    return Compartment[i0]

def SetCompartment_i(i, Compartment_i):
    # Setter for individual element of the "Compartment" global variable.
    global Compartment
    i0 = i - 1
    Compartment[i0] = Compartment_i

def GetCompartment_Thickness(i):
    # Getter for the "Thickness" attribute of the "Compartment" global variable.
    i0 = i - 1
    return Compartment[i0].Thickness

def SetCompartment_Thickness(i, Thickness):
    # Setter for the "Thickness" attribute of the "Compartment" global variable.
    global Compartment
    i0 = i - 1
    Compartment[i0].Thickness = Thickness

def GetCompartment_Layer(i):
    # Getter for the "Layer" attribute of the "compartment" global variable.
    i0 = i -1
    return Compartment[i0].Layer

def SetCompartment_Layer(i, Layer):
    # Setter for the "Layer" attribute of the "compartment" global variable.
    global Compartment
    i0 = i -1
    Compartment[i0].Layer = Layer


def GetCompartment_SinkMajor(i):
    # Getter for the "SinkMajor" attribute of the "compartment" global variable.
    i0 = i - 1
    return Compartment[i0].SinkMajor

def SetCompartment_SinkMajor(i, SinkMajor):
    # Setter for the "SinkMajor" attribute of the "compartment" global variable.
    global Compartment
    i0 = i - 1
    Compartment[i0].SinkMajor = SinkMajor

def GetCompartment_SinkMinor(i):
    # Getter for the "SinkMinor" attribute of the "compartment" global variable.
    i0 = i - 1
    return Compartment[i0].SinkMinor

def SetCompartment_SinkMinor(i, SinkMinor):
    # Setter for the "SinkMinor" attribute of the "compartment" global variable.
    global Compartment
    i0 = i - 1
    Compartment[i0].SinkMinor = SinkMinor

def GetCompartment_Salt(i1, i2):
    # Getter for individual elements of "Salt" attribute of the "compartment global variable.
    i01 = i1 - 1
    i02 = i2 - 1
    return Compartment[i01].Salt[i02]

def SetCompartment_Salt(i1, i2, Salt):
    # Setter for individual elements of "Salt" attribute of the "compartment global variable.
    global Compartment
    i01 = i1 - 1
    i02 = i2 - 1
    Compartment[i01].Salt[i02] = Salt

def GetCompartment_Depo(i1, i2):
    # Getter for individual elements of "Depo" attribute of the "compartment global variable.
    i01 = i1 - 1
    i02 = i2 - 1
    return Compartment[i01].Depo[i02]

def SetCompartment_Depo(i1, i2, Depo):
    # Setter for individual elements of "Depo" attribute of the "compartment global variable.
    global Compartment
    i01 = i1 - 1
    i02 = i2 - 1
    Compartment[i01].Depo[i02] = Depo

def GetCompartment_Smax(i):
    # Getter for the "Smax" attribute of the "compartment" global variable.
    i0 = i -1
    return Compartment[i0].Smax

def SetCompartment_Smax(i, Smax):
    # Setter for the "Smax" attribute of the "compartment" global variable.
    global Compartment
    i0 = i -1
    Compartment[i0].Smax = Smax

def GetCompartment_DayAnaero(i):
    # Getter for the "DayAnaero" attribute of the "compartment" global variable.
    i0 = i -1
    return Compartment[i0].DayAnaero

def SetCompartment_DayAnaero(i, DayAnaero):
    # Setter for the "DayAnaero" attribute of the "compartment" global variable.
    global Compartment
    i0 = i -1
    Compartment[i0].DayAnaero = DayAnaero

def GetCompartment_WFactor(i):
    # Getter for the "WFactor" attribute of the "compartment" global variable.
    i0 = i -1
    return Compartment[i0].WFactor

def SetCompartment_WFactor(i, WFactor):
    # Setter for the "WFactor" attribute of the "compartment" global variable.
    global Compartment
    i0 = i -1
    Compartment[i0].WFactor = WFactor

def GetCompartment_FCadj(i):
    # Getter for the "FCadj" attribute of the "compartment" global variable.
    i0 = i -1
    return Compartment[i0].FCadj

def SetCompartment_FCadj(i, FCadj):
    # Setter for the "FCadj" attribute of the "compartment" global variable.
    global Compartment
    i0 = i -1
    Compartment[i0].FCadj = FCadj

def GetCompartment_theta(i):
    # Getter for the "Theta" attribute of the "compartment" global variable.
    i0 = i -1
    return Compartment[i0].Theta

def SetCompartment_theta(i, Theta):
    # Setter for the "Theta" attribute of the "compartment" global variable.
    global Compartment
    i0 = i -1
    Compartment[i0].Theta = Theta

def GetCompartment_fluxout(i):
    # Getter for the "FluxOut" attribute of the "compartment" global variable.
    i0 = i -1
    return Compartment[i0].FluxOut

def SetCompartment_fluxout(i, FluxOut):
    # Setter for the "FluxOut" attribute of the "compartment" global variable.
    global Compartment
    i0 = i -1
    Compartment[i0].FluxOut = FluxOut

def SetZiAqua(ZiAqua_in):
    # Setter for the "ZiAqua" global variable.
    global ZiAqua
    ZiAqua = ZiAqua_in

def GetZiAqua():
    # Getter for the "ZiAqua" global variable.
    return ZiAqua

def SetECiAqua(ECiAqua_in):
    # Setter for the "ECiAqua" global variable.
    global ECiAqua
    ECiAqua = ECiAqua_in

def GetECiAqua():
    # Getter for the "ECiAqua" global variable.
    return ECiAqua

def GetEact():
    # Getter for the "Eact" global variable.
    return Eact

def SetEact(Eact_in):
    # Setter for the "Eact" global variable.
    global Eact
    Eact = Eact_in

def GetTminTnxReference365DaysRun():
    # Getter for the "TminTnxReference365DaysRun" global variable.
    global TminTnxReference365DaysRun
    return list(TminTnxReference365DaysRun)

def SetTminTnxReference365DaysRun(TminTnxReference365DaysRun_in):
    # Setter for the "TminTnxReference365DaysRun" global variable.
    global TminTnxReference365DaysRun
    TminTnxReference365DaysRun = list(TminTnxReference365DaysRun_in)

def GetTminTnxReference365DaysRun_i(i):
    # Getter for individual element of the "TminTnxReference365DaysRun" global variable.
    global TminTnxReference365DaysRun
    i0 = i - 1
    return TminTnxReference365DaysRun[i0]

def SetTminTnxReference365DaysRun_i(i, TminTnxReference365DaysRun_i):
    # Setter for individual element for the "TminTnxReference365DaysRun" global variable.
    global TminTnxReference365DaysRun
    i0 = i - 1
    TminTnxReference365DaysRun[i0] = TminTnxReference365DaysRun_i

def GetTmaxTnxReference365DaysRun():
    # Getter for the "TmaxTnxReference365DaysRun" global variable.
    global TmaxTnxReference365DaysRun
    return list(TmaxTnxReference365DaysRun)

def SetTmaxTnxReference365DaysRun(TmaxTnxReference365DaysRun_in):
    # Setter for the "TmaxTnxReference365DaysRun" global variable.
    global TmaxTnxReference365DaysRun
    TmaxTnxReference365DaysRun = list(TmaxTnxReference365DaysRun_in)

def GetTmaxTnxReference365DaysRun_i(i):
    # Getter for individual element of the "TmaxTnxReference365DaysRun" global variable.
    global TmaxTnxReference365DaysRun
    i0 = i - 1
    return TmaxTnxReference365DaysRun[i0]

def SetTmaxTnxReference365DaysRun_i(i, TmaxTnxReference365DaysRun_i):
    # Setter for individual element for the "TmaxTnxReference365DaysRun" global variable.
    global TmaxTnxReference365DaysRun
    i0 = i - 1
    TmaxTnxReference365DaysRun[i0] = TmaxTnxReference365DaysRun_i

def GetNoMoreCrop():
    # Getter for the "NoMoreCrop" global variable.
    return NoMoreCrop

def SetNoMoreCrop(NoMoreCrop_in):
    # Setter for the "NoMoreCrop" global variable.
    global NoMoreCrop
    NoMoreCrop = NoMoreCrop_in

def FileExists(full_name: str) -> bool:
    return os.path.isfile(full_name)

def set_layer_undef(LayerDataTemp):

    LayerDataTemp = SoilLayerIndividual()

    LayerDataTemp.Description = ''
    LayerDataTemp.Thickness = undef_double
    LayerDataTemp.SAT = undef_double
    LayerDataTemp.FC = undef_double
    LayerDataTemp.WP = undef_double
    LayerDataTemp.tau = undef_double
    LayerDataTemp.InfRate = undef_double
    LayerDataTemp.Penetrability = undef_int
    LayerDataTemp.GravelMass = undef_int
    LayerDataTemp.GravelVol = undef_int
    LayerDataTemp.Macro = undef_int
    LayerDataTemp.UL = undef_double
    LayerDataTemp.Dx = undef_double

    for i in range(11):  # máximo 11 celdas de sal
        LayerDataTemp.SaltMobility[i] = undef_double

    LayerDataTemp.SoilClass = undef_int
    LayerDataTemp.CRa = undef_int
    LayerDataTemp.CRb = undef_int
    LayerDataTemp.WaterContent = undef_double

    return LayerDataTemp

def NumberSoilClass(SatvolPro, FCvolPro, PWPvolPro, Ksatmm):

    if SatvolPro <= 55.0:
        if PWPvolPro >= 20.0:
            if (SatvolPro >= 49.0) and (FCvolPro >= 40.0):
                NumberSoilClass = 4  # silty clayey soils
            else:
                NumberSoilClass = 3  # sandy clayey soils
        else:
            if FCvolPro < 23.0:
                NumberSoilClass = 1  # sandy soils
            else:
                if (PWPvolPro > 16.0) and (Ksatmm < 100.0):
                    NumberSoilClass = 3  # sandy clayey soils
                else:
                    if (PWPvolPro < 6.0) and (FCvolPro < 28.0) and (Ksatmm > 750.0):
                        NumberSoilClass = 1  # sandy soils
                    else:
                        NumberSoilClass = 2  # loamy soils
    else:
        NumberSoilClass = 4  # silty clayey soils

    return NumberSoilClass

def DetermineParametersCR(SoilClass, KsatMM, aParam, bParam):

    # determine parameters
    if roundc(KsatMM * 1000.0, mold="int32") <= 0:
        aParam = undef_int
        bParam = undef_int
    else:
        if SoilClass == 1:  # sandy soils
            aParam = -0.3112 - KsatMM / 100000.0
            bParam = -1.4936 + 0.2416 * math.log(KsatMM)
        elif SoilClass == 2:  # loamy soils
            aParam = -0.4986 + 9.0 * KsatMM / 100000.0
            bParam = -2.1320 + 0.4778 * math.log(KsatMM)
        elif SoilClass == 3:  # sandy clayey soils
            aParam = -0.5677 - 4.0 * KsatMM / 100000.0
            bParam = -3.7189 + 0.5922 * math.log(KsatMM)
        else:  # silty clayey soils
            aParam = -0.6366 + 8.0 * KsatMM / 10000.0
            bParam = -1.9165 + 0.7063 * math.log(KsatMM)

    return aParam, bParam

def InitializeGlobalStrings():

    # Initializes all allocatable strings which are global variables
    # themselves or attributes of derived type global variables.
    
    SetCalendarDescription("")
    SetCalendarFile("")
    SetCalendarFileFull("")
    SetClimateDescription("")
    SetClimateFile("")
    SetClimateFileFull("")
    SetClimDescription("")
    SetClimFile("")
    SetClimRecord_FromString("")
    SetClimRecord_ToString("")
    SetCO2Description("")
    SetCO2File("")
    SetCO2FileFull("")
    SetCropDescription("")
    SetCropFile("")
    SetCropFileFull("")
    SetEToDescription("")
    SetEToFile("")
    SetEToFileFull("")
    SetEToRecord_FromString("")
    SetEToRecord_ToString("")
    SetFullFileNameProgramParameters("")
    SetGroundWaterDescription("")
    SetGroundWaterFile("")
    SetGroundWaterFileFull("")
    SetIrriDescription("")
    SetIrriFile("")
    SetIrriFileFull("")
    SetManDescription("")
    SetManFile("")
    SetManFileFull("")
    SetMultipleProjectDescription("")
    SetMultipleProjectFile("")
    SetMultipleProjectFileFull("")
    SetObservationsDescription("")
    SetObservationsFile("")
    SetObservationsFilefull("")
    SetOffSeasonDescription("")
    SetOffSeasonFile("")
    SetOffSeasonFilefull("")
    SetOutputName("")
    SetPathNameList("")
    SetPathNameOutp("")
    SetPathNameParam("")
    SetPathNameProg("")
    SetPathNameSimul("")
    SetProfDescription("")
    SetProfFile("")
    SetProfFilefull("")
    SetProjectDescription("")
    SetProjectFile("")
    SetProjectFileFull("")
    SetRainDescription("")
    SetRainFile("")
    SetRainFileFull("")
    SetRainRecord_FromString("")
    SetRainRecord_ToString("")
    SetSimulation_Storage_CropString("")
    SetSWCiniDescription("")
    SetSWCIniFile("")
    SetSWCiniFileFull("")
    SetTemperatureDescription("")
    SetTemperatureFile("")
    SetTemperatureFileFull("")
    SetTemperatureRecord_FromString("")
    SetTemperatureRecord_ToString("")
    SetTnxReference365DaysFile("")
    SetTnxReference365DaysFileFull("")
    SetTnxReferenceFile("")
    SetTnxReferenceFileFull("")

def SetOutputAggregate(value: int) -> None:
    # Setter for the "OutputAggregate" global variable.
    global OutputAggregate
    OutputAggregate = value

def GetOutputAggregate() -> int:
    # Getter for the "OutputAggregate" global variable.
    return OutputAggregate

def GetPathNameSimul() -> str:
    # Getter for the "PathNameSimul" global variable.
    return PathNameSimul

def GetProfDescription():
    # Getter for the "ProfDescription" global variable.
    return ProfDescription

def GetSoil():
    # Getter for the "soil" global variable.
    return Soil

def SetSoil(Soil_in):
    # Setter for the "soil" global variable.
    global Soil
    Soil = Soil_in

def GetSoil_CNvalue():
    # Getter for "CNvalue" attribute of the "soil" global variable.
    return Soil.CNvalue

def GetSoil_REW():
    # Getter for "REW" attribute of the "soil" global variable.
    return Soil.REW

def GetSoil_NrSoilLayers():
    # Getter for "NrSoilLayers" attribute of the "soil" global variable.
    return Soil.NrSoilLayers

def SetSoil_RootMax(RootMax):
    # Setter for the "Soil" global variable.
    global Soil
    Soil.RootMax = _f32(RootMax)

def GetSoil_RootMax():
    # Getter for "RootMax" attribute of the "soil" global variable.
    return Soil.RootMax

def GetSoilLayer_Thickness(i):
    # Getter for the "Thickness" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].Thickness

def GetSoilLayer_Penetrability(i):
    # Getter for the "Penetrability" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].Penetrability

def GetSoilLayer_GravelMass(i):
    # Getter for the "GravelMass" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].GravelMass

def GetSoilLayer_Description(i):
    # Getter for the "Description" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].Description

def GetSoilLayer_WaterContent(i):
    # Getter for the "WaterContent" attribute of the "soillayer" global variable.
    i0 = i - 1
    return soillayer[i0].WaterContent

def SetSoilLayer_WaterContent(i, WaterContent):
    # Setter for the "WaterContent" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    soillayer[i0].WaterContent = WaterContent

def GetSoilLayer_i(i):
    # Getter for the "soillayer" global variable (individual element)
    i0 = i - 1
    return soillayer[i0]

def SetSoilLayer_i(i, SoilLayer_i):
    # Setter for the "soillayer" global variable (individual element)
    global soillayer
    i0 = i - 1
    soillayer[i0] = SoilLayer_i

def GetSoilLayer_SaltMobility_i(i, j):
    # Getter for individual element of the "SaltMobility" attribute of the "soillayer" global variable.
    i0 = i - 1
    j0 = j - 1
    return soillayer[i0].SaltMobility[j0]

def SetSoilLayer_SaltMobility_i(i, j, SaltMobility):
    # Setter for individual element of the "SaltMobility" attribute of the "soillayer" global variable.
    global soillayer
    i0 = i - 1
    j0 = j - 1
    soillayer[i0].SaltMobility[j0] = SaltMobility

def GetSoilLayer():
    # Getter for the "soillayer" global variable.
    return soillayer

def GetCrop():
    # Getter for the "crop" global variable.
    return crop

def SetCrop(Crop_in):
    # Setter for the "crop" global variable.
    global crop
    crop = Crop_in

def GetCrop_Length_i(i):
    # Getter for individual element of the "Length" attribute of the "crop" global variable.
    i0 = i - 1
    return crop.Length[i0]

def SetCrop_Length_i(i, Length):
    # Setter for individual element of the "Length" attribute of the "crop" global variable.
    global crop
    i0 = i - 1
    crop.Length[i0] = Length

def SetCrop_RootMin(RootMin):
    # Setter for the "RootMin" attribute of the "crop" global variable.
    global crop
    crop.RootMin = RootMin

def GetCrop_RootMin():
    # Getter for the "RootMin" attribute of the "crop" global variable.
    return crop.RootMin

def SetCrop_RootMinYear1(RootMinYear1):
    # Setter for the "RootMinYear1" attribute of the global "crop" variable.
    global crop
    crop.RootMinYear1 = RootMinYear1

def GetCrop_RootMinYear1():
    # Getter for the "RootMinYear1" attribute of the global "crop" variable.
    return crop.RootMinYear1

def SetCrop_RootMax(RootMax):
    # Setter for the "RootMax" attribute of the "crop" global variable.
    global crop
    crop.RootMax = RootMax

def GetCrop_RootMax():
    # Getter for the "RootMax" attribute of the "crop" global variable.
    return crop.RootMax

def SetCrop_subkind(subkind):
    # Setter for the "subkind" attribute of the "crop" global variable.
    global crop
    crop.subkind = subkind

def GetCrop_subkind():
    # Getter for the "subkind" attribute of the "crop" global variable.
    return crop.subkind

def SetCrop_Planting(Planting):
    # Setter for the "Planting" attribute of the "crop" global variable.
    global crop
    crop.Planting = Planting

def GetCrop_Planting():
    # Getter for the "PlantingDens" attribute of the "crop" global variable.
    return crop.Planting

def SetCrop_ECemin(ECemin):
    # Setter for the "ECemin" attribute of the global "crop" variable.
    global crop
    crop.ECemin = ECemin

def GetCrop_ECemin():
    # Getter for the "ECemin" attribute of the global "crop" variable.
    return crop.ECemin

def SetCrop_ECemax(ECemax):
    # Setter for the "ECemax" attribute of the global "crop" variable.
    global crop
    crop.ECemax = ECemax

def GetCrop_ECemax():
    # Getter for the "ECemax" attribute of the global "crop" variable.
    return crop.ECemax

def SetCrop_CCsaltDistortion(CCsaltDistortion):
    # Setter for the "CCsaltDistortion" attribute of the global "crop" variable.
    global crop
    crop.CCsaltDistortion = CCsaltDistortion

def GetCrop_CCsaltDistortion():
    # Getter for the "CCsaltDistortion" attribute of the global "crop" variable.
    return crop.CCsaltDistortion

def SetCrop_ResponseECsw(ResponseECsw):
    # Setter for the "ResponseECsw" attribute of the global "crop" variable.
    global crop
    crop.ResponseECsw = ResponseECsw

def GetCrop_ResponseECsw():
    # Getter for the "ResponseECsw" attribute of the global "crop" variable.
    return crop.ResponseECsw

def SetCrop_Tcold(Tcold):
    # Setter for the "Tcold" attribute of the global "crop" variable.
    global crop
    crop.Tcold = Tcold

def GetCrop_Tcold():
    # Getter for the "Tcold" attribute of the global "crop" variable.
    return crop.Tcold

def SetCrop_Theat(Theat):
    # Setter for the "Theat" attribute of the global "crop" variable.
    global crop
    crop.Theat = Theat

def GetCrop_Theat():
    # Getter for the "Theat" attribute of the global "crop" variable.
    return crop.Theat

def SetCrop_SownYear1(SownYear1):
    # Setter for the "SownYear1" attribute of the "crop" global variable.
    global crop
    crop.SownYear1 = SownYear1

def GetCrop_SownYear1():
    # Getter for the "SownYear1" attribute of the "crop" global variable.
    return crop.SownYear1

def SetCrop_ModeCycle(ModeCycle):
    # Setter for the "ModeCycle" attribute of the global "crop" variable.
    global crop
    crop.ModeCycle = ModeCycle

def GetCrop_ModeCycle():
    # Getter for the "ModeCycle" attribute of the global "crop" variable.
    return crop.ModeCycle

def SetCrop_pMethod(pMethod):
    # Setter for the "pMethod" attribute of the global "crop" variable.
    global crop
    crop.pMethod = pMethod

def GetCrop_pMethod():
    # Getter for the "pMethod" attribute of the global "crop" variable.
    return crop.pMethod

def SetCrop_Tbase(Tbase):
    # Setter for the "Tbase" attribute of the global "crop" variable.
    global crop
    crop.Tbase = Tbase

def GetCrop_Tbase():
    # Getter for the "Tbase" attribute of the global "crop" variable.
    return crop.Tbase

def SetCrop_Tupper(Tupper):
    # Setter for the "Tupper" attribute of the global "crop" variable.
    global crop
    crop.Tupper = Tupper

def GetCrop_Tupper():
    # Getter for the "Tupper" attribute of the global "crop" variable.
    return crop.Tupper

def SetCrop_pLeafDefUL(pLeafDefUL):
    # Setter for the "pLeafDefUL" attribute of the global "crop" variable.
    global crop
    crop.pLeafDefUL = pLeafDefUL

def GetCrop_pLeafDefUL():
    # Getter for the "pLeafDefUL" attribute of the global "crop" variable.
    return crop.pLeafDefUL

def SetCrop_pLeafDefLL(pLeafDefLL):
    # Setter for the "pLeafDefLL" attribute of the global "crop" variable.
    global crop
    crop.pLeafDefLL = pLeafDefLL

def GetCrop_pLeafDefLL():
    # Getter for the "pLeafDefLL" attribute of the global "crop" variable.
    return crop.pLeafDefLL

def SetCrop_KsShapeFactorLeaf(KsShapeFactorLeaf):
    # Setter for the "KsShapeFactorLeaf" attribute of the global "crop" variable.
    global crop
    crop.KsShapeFactorLeaf = KsShapeFactorLeaf

def GetCrop_KsShapeFactorLeaf():
    # Getter for the "KsShapeFactorLeaf" attribute of the global "crop" variable.
    return crop.KsShapeFactorLeaf

def GetCrop_pActStom():
    # Getter for the "pActStom" attribute of the global "crop" variable.
    return crop.pActStom

def SetCrop_pActStom(pActStom):
    # Setter for the "pActStom" attribute of the global "crop" variable.
    global crop
    crop.pActStom = pActStom

def GetCrop_pLeafAct():
    # Getter for the "pLeafAct" global variable.
    return crop.pLeafAct

def SetCrop_pLeafAct(pLeafAct):
    # Setter for the "pLeafAct" global variable.
    global crop
    crop.pLeafAct = pLeafAct

def GetCrop_pSenAct():
    # Getter for the "pSenAct" global variable.
    return crop.pSenAct

def SetCrop_pSenAct(pSenAct):
    # Setter for the "pSenAct" global variable.
    global crop
    crop.pSenAct = pSenAct

def SetCrop_pdef(pdef):
    # Setter for the "pdef" attribute of the global "crop" variable.
    global crop
    crop.pdef = pdef

def GetCrop_pdef():
    # Getter for the "pdef" attribute of the global "crop" variable.
    return crop.pdef

def SetCrop_KsShapeFactorStomata(KsShapeFactorStomata):
    # Setter for the "KsShapeFactorStomata" attribute of the global "crop" variable.
    global crop
    crop.KsShapeFactorStomata = KsShapeFactorStomata

def GetCrop_KsShapeFactorStomata():
    # Getter for the "KsShapeFactorStomata" attribute of the global "crop" variable.
    return crop.KsShapeFactorStomata

def SetCrop_pSenescence(pSenescence):
    # Setter for the "pSenescence" attribute of the global "crop" variable.
    global crop
    crop.pSenescence = pSenescence

def GetCrop_pSenescence():
    # Getter for the "pSenescence" attribute of the global "crop" variable.
    return crop.pSenescence

def SetCrop_KsShapeFactorSenescence(KsShapeFactorSenescence):
    # Setter for the "KsShapeFactorSenescence" attribute of the global "crop" variable.
    global crop
    crop.KsShapeFactorSenescence = KsShapeFactorSenescence

def GetCrop_KsShapeFactorSenescence():
    # Getter for the "KsShapeFactorSenescence" attribute of the global "crop" variable.
    return crop.KsShapeFactorSenescence

def SetCrop_SumEToDelaySenescence(SumEToDelaySenescence):
    # Setter for the "SumEToDelaySenescence" attribute of the global "crop" variable.
    global crop
    crop.SumEToDelaySenescence = SumEToDelaySenescence

def GetCrop_SumEToDelaySenescence():
    # Getter for the "SumEToDelaySenescence" attribute of the global "crop" variable.
    return crop.SumEToDelaySenescence

def SetCrop_pPollination(pPollination):
    # Setter for the "pPollination" attribute of the global "crop" variable.
    global crop
    crop.pPollination = pPollination

def GetCrop_pPollination():
    # Getter for the "pPollination" attribute of the global "crop" variable.
    return crop.pPollination

def SetCrop_AnaeroPoint(AnaeroPoint):
    # Setter for the "AnaeroPoint" attribute of the global "crop" variable.
    global crop
    crop.AnaeroPoint = AnaeroPoint

def GetCrop_AnaeroPoint():
    # Getter for the "AnaeroPoint" attribute of the global "crop" variable.
    return crop.AnaeroPoint

def GetCrop_StressResponse():
    # Getter for the "StressResponse" attribute of the global "crop" variable.
    return crop.StressResponse

def SetCrop_StressResponse(StressResponse_in):
    # Setter for the "StressResponse" attribute of the global "crop" variable.
    global crop
    crop.StressResponse = StressResponse_in

def SetCrop_StressResponse_Stress(StressResponse_Stress):
    # Setter for the "StressResponse_Stress" attribute of the global "crop" variable.
    global crop
    crop.StressResponse.Stress = StressResponse_Stress

def GetCrop_StressResponse_Stress():
    # Getter for the "StressResponse_Stress" attribute of the global "crop" variable.
    return crop.StressResponse.Stress

def SetCrop_StressResponse_ShapeCGC(StressResponse_ShapeCGC):
    # Setter for the "StressResponse_ShapeCGC" attribute of the global "crop" variable.
    global crop
    crop.StressResponse.ShapeCGC = StressResponse_ShapeCGC

def GetCrop_StressResponse_ShapeCGC():
    # Getter for the "StressResponse_ShapeCGC" attribute of the global "crop" variable.
    return crop.StressResponse.ShapeCGC

def SetCrop_StressResponse_ShapeCCX(StressResponse_ShapeCCX):
    # Setter for the "StressResponse_ShapeCCX" attribute of the global "crop" variable.
    global crop
    crop.StressResponse.ShapeCCX = StressResponse_ShapeCCX

def GetCrop_StressResponse_ShapeCCX():
    # Getter for the "StressResponse_ShapeCCX" attribute of the global "crop" variable.
    return crop.StressResponse.ShapeCCX

def SetCrop_StressResponse_ShapeWP(StressResponse_ShapeWP):
    # Setter for the "StressResponse_ShapeWP" attribute of the global "crop" variable.
    global crop
    crop.StressResponse.ShapeWP = StressResponse_ShapeWP

def GetCrop_StressResponse_ShapeWP():
    # Getter for the "StressResponse_ShapeWP" attribute of the global "crop" variable.
    return crop.StressResponse.ShapeWP

def SetCrop_StressResponse_ShapeCDecline(StressResponse_ShapeCDecline):
    # Setter for the "StressResponse_ShapeCDecline" attribute of the global "crop" variable.
    global crop
    crop.StressResponse.ShapeCDecline = StressResponse_ShapeCDecline

def GetCrop_StressResponse_ShapeCDecline():
    # Getter for the "StressResponse_ShapeCDecline" attribute of the global "crop" variable.
    return crop.StressResponse.ShapeCDecline

def SetCrop_StressResponse_Calibrated(StressResponse_Calibrated):
    # Setter for the "StressResponse_Calibrated" attribute of the global "crop" variable.
    global crop
    crop.StressResponse.Calibrated = StressResponse_Calibrated

def GetCrop_StressResponse_Calibrated():
    # Getter for the "StressResponse_Calibrated" attribute of the global "crop" variable.
    return crop.StressResponse.Calibrated

def SetCrop_GDtranspLow(GDtranspLow):
    # Setter for the "GDtranspLow" attribute of the global "crop" variable.
    global crop
    crop.GDtranspLow = GDtranspLow

def GetCrop_GDtranspLow():
    # Getter for the "GDtranspLow" attribute of the global "crop" variable.
    return crop.GDtranspLow

def SetCrop_KcTop(KcTop):
    # Setter for the "KcTop" attribute of the global "crop" variable.
    global crop
    crop.KcTop = KcTop

def GetCrop_KcTop():
    # Getter for the "KcTop" attribute of the global "crop" variable.
    return crop.KcTop

def SetCrop_KcDeclineCumul(KcDeclineCumul):
    # Setter for the "KcDeclineCumul" attribute of the global "crop" variable.
    global crop
    crop.KcDeclineCumul = KcDeclineCumul

def GetCrop_KcDeclineCumul():
    # Getter for the "KcDeclineCumul" attribute of the global "crop" variable.
    return crop.KcDeclineCumul

def SetCrop_RootShape(RootShape):
    # Setter for the "RootShape" attribute of the global "crop" variable.
    global crop
    crop.RootShape = RootShape

def GetCrop_RootShape():
    # Getter for the "RootShape" attribute of the global "crop" variable.
    return crop.RootShape

def SetCrop_SmaxTopQuarter(SmaxTopQuarter):
    # Setter for the "SmaxTopQuarter" attribute of the global "crop" variable.
    global crop
    crop.SmaxTopQuarter = SmaxTopQuarter

def GetCrop_SmaxTopQuarter():
    # Getter for the "SmaxTopQuarter" attribute of the global "crop" variable.
    return crop.SmaxTopQuarter

def SetCrop_SmaxBotQuarter(SmaxBotQuarter):
    # Setter for the "SmaxBotQuarter" attribute of the global "crop" variable.
    global crop
    crop.SmaxBotQuarter = SmaxBotQuarter

def GetCrop_SmaxBotQuarter():
    # Getter for the "SmaxBotQuarter" attribute of the global "crop" variable.
    return crop.SmaxBotQuarter

def SetCrop_CCEffectEvapLate(CCEffectEvapLate):
    # Setter for the "CCEffectEvapLate" attribute of the global "crop" variable.
    global crop
    crop.CCEffectEvapLate = CCEffectEvapLate

def GetCrop_CCEffectEvapLate():
    # Getter for the "CCEffectEvapLate" attribute of the global "crop" variable.
    return crop.CCEffectEvapLate

def SetCrop_SizeSeedling(SizeSeedling):
    # Setter for the "SizeSeedling" attribute of the global "crop" variable.
    global crop
    crop.SizeSeedling = SizeSeedling

def GetCrop_SizeSeedling():
    # Getter for the "SizeSeedling" attribute of the global "crop" variable.
    return crop.SizeSeedling

def SetCrop_PlantingDens(PlantingDens):
    # Setter for the "PlantingDens" attribute of the global "crop" variable.
    global crop
    crop.PlantingDens = PlantingDens

def GetCrop_PlantingDens():
    # Getter for the "PlantingDens" attribute of the global "crop" variable.
    return crop.PlantingDens

def SetCrop_SizePlant(SizePlant):
    # Setter for the "SizePlant" attribute of the global "crop" variable.
    global crop
    crop.SizePlant = SizePlant

def GetCrop_SizePlant():
    # Getter for the "SizePlant" attribute of the global "crop" variable.
    return crop.SizePlant


def SetCrop_CCo(CCo):
    # Setter for the "CCo" attribute of the global "crop" variable.
    global crop
    crop.CCo = CCo

def GetCrop_CCo():
    # Getter for the "CCo" attribute of the global "crop" variable.
    return crop.CCo


def SetCrop_CCini(CCini):
    # Setter for the "CCini" attribute of the global "crop" variable.
    global crop
    crop.CCini = CCini

def GetCrop_CCini():
    # Getter for the "CCini" attribute of the global "crop" variable.
    return crop.CCini

def GetCrop_PrematureEnd():
    # Getter for the "PrematureEnd" attribute of the "crop" global variable.
    return crop.PrematureEnd

def SetCrop_PrematureEnd(PrematureEnd):
    # Setter for the "PrematureEnd" attribute of the "crop" global variable.
    global crop
    crop.PrematureEnd  = PrematureEnd

def GetCrop_LastDayNr():
    # Getter for the "LastDayNr" attribute of the "crop" global variable.
    return crop.LastDayNr

def SetCrop_LastDayNr(LastDayNr):
    # Setter for the "LastDayNr" attribute of the "crop" global variable.
    global crop
    crop.LastDayNr = LastDayNr

def SetCrop_CGC(CGC):
    # Setter for the "CGC" attribute of the global "crop" variable.
    global crop
    crop.CGC = CGC

def GetCrop_CGC():
    # Getter for the "CGC" attribute of the global "crop" variable.
    return crop.CGC

def SetCrop_YearCCx(YearCCx):
    # Setter for the "YearCCx" attribute of the global "crop" variable.
    global crop
    crop.YearCCx = YearCCx

def GetCrop_YearCCx():
    # Getter for the "YearCCx" attribute of the global "crop" variable.
    return crop.YearCCx

def SetCrop_CCxRoot(CCxRoot):
    # Setter for the "CCxRoot" attribute of the global "crop" variable.
    global crop
    crop.CCxRoot = CCxRoot

def GetCrop_CCxRoot():
    # Getter for the "CCxRoot" attribute of the global "crop" variable.
    return crop.CCxRoot

def SetCrop_CCx(CCx):
    # Setter for the "CCx" attribute of the global "crop" variable.
    global crop
    crop.CCx = CCx

def GetCrop_CCx():
    # Getter for the "CCx" attribute of the global "crop" variable.
    return crop.CCx

def SetCrop_CDC(CDC):
    # Setter for the "CDC" attribute of the global "crop" variable.
    global crop
    crop.CDC = CDC

def GetCrop_CDC():
    # Getter for the "CDC" attribute of the global "crop" variable.
    return crop.CDC

def SetCrop_DaysToCCini(DaysToCCini):
    # Setter for the "DaysToCCini" attribute of the global "crop" variable.
    global crop
    crop.DaysToCCini = DaysToCCini

def GetCrop_DaysToCCini():
    # Getter for the "DaysToCCini" attribute of the global "crop" variable.
    return crop.DaysToCCini

def SetCrop_DaysToGermination(DaysToGermination):
    # Setter for the "DaysToGermination" attribute of the global "crop" variable.
    global crop
    crop.DaysToGermination = DaysToGermination

def GetCrop_DaysToGermination():
    # Getter for the "DaysToGermination" attribute of the global "crop" variable.
    return crop.DaysToGermination

def SetCrop_DaysToMaxRooting(DaysToMaxRooting):
    # Setter for the "DaysToMaxRooting" attribute of the global "crop" variable.
    global crop
    crop.DaysToMaxRooting = DaysToMaxRooting

def GetCrop_DaysToMaxRooting():
    # Getter for the "DaysToMaxRooting" attribute of the global "crop" variable.
    return crop.DaysToMaxRooting

def SetCrop_DaysToSenescence(DaysToSenescence):
    # Setter for the "DaysToSenescence" attribute of the global "crop" variable.
    global crop
    crop.DaysToSenescence = DaysToSenescence

def GetCrop_DaysToSenescence():
    # Getter for the "DaysToSenescence" attribute of the global "crop" variable.
    return crop.DaysToSenescence

def SetCrop_DaysToHarvest(DaysToHarvest):
    # Setter for the "DaysToHarvest" attribute of the global "crop" variable.
    global crop
    crop.DaysToHarvest = DaysToHarvest

def GetCrop_DaysToHarvest():
    # Getter for the "DaysToHarvest" attribute of the global "crop" variable.
    return crop.DaysToHarvest

def SetCrop_DaysToFlowering(DaysToFlowering):
    # Setter for the "DaysToFlowering" attribute of the global "crop" variable.
    global crop
    crop.DaysToFlowering = DaysToFlowering

def GetCrop_DaysToFlowering():
    # Getter for the "DaysToFlowering" attribute of the global "crop" variable.
    return crop.DaysToFlowering

def SetCrop_LengthFlowering(LengthFlowering):
    # Setter for the "LengthFlowering" attribute of the global "crop" variable.
    global crop
    crop.LengthFlowering = LengthFlowering

def GetCrop_LengthFlowering():
    # Getter for the "LengthFlowering" attribute of the global "crop" variable.
    return crop.LengthFlowering

def SetCrop_DaysToHIo(DaysToHIo):
    # Setter for the "DaysToHIo" attribute of the global "crop" variable.
    global crop
    crop.DaysToHIo = DaysToHIo

def GetCrop_DaysToHIo():
    # Getter for the "DaysToHIo" attribute of the global "crop" variable.
    return crop.DaysToHIo

def SetCrop_DeterminancyLinked(DeterminancyLinked):
    # Setter for the "DeterminancyLinked" attribute of the global "crop" variable.
    global crop
    crop.DeterminancyLinked = DeterminancyLinked

def GetCrop_DeterminancyLinked():
    # Getter for the "DeterminancyLinked" attribute of the global "crop" variable.
    return crop.DeterminancyLinked

def SetCrop_fExcess(fExcess):
    # Setter for the "fExcess" attribute of the global "crop" variable.
    global crop
    crop.fExcess = fExcess

def GetCrop_fExcess():
    # Getter for the "fExcess" attribute of the global "crop" variable.
    return crop.fExcess

def SetCrop_WP(WP):
    # Setter for the "WP" attribute of the global "crop" variable.
    global crop
    crop.WP = WP

def GetCrop_WP():
    # Getter for the "WP" attribute of the global "crop" variable.
    return crop.WP

def SetCrop_WPy(WPy):
    # Setter for the "WPy" attribute of the global "crop" variable.
    global crop
    crop.WPy = WPy

def GetCrop_WPy():
    # Getter for the "WPy" attribute of the global "crop" variable.
    return crop.WPy

def SetCrop_AdaptedToCO2(AdaptedToCO2):
    # Setter for the "AdaptedToCO2" attribute of the global "crop" variable.
    global crop
    crop.AdaptedToCO2 = AdaptedToCO2

def GetCrop_AdaptedToCO2():
    # Getter for the "AdaptedToCO2" attribute of the global "crop" variable.
    return crop.AdaptedToCO2

def SetCrop_HI(HI):
    # Setter for the "HI" attribute of the global "crop" variable.
    global crop
    crop.HI = HI

def GetCrop_HI():
    # Getter for the "HI" attribute of the global "crop" variable.
    return crop.HI

def SetCrop_DryMatter(DryMatter):
    # Setter for the "DryMatter" attribute of the global "crop" variable.
    global crop
    crop.DryMatter = DryMatter

def GetCrop_DryMatter():
    # Getter for the "DryMatter" attribute of the global "crop" variable.
    return crop.DryMatter

def SetCrop_HIincrease(HIincrease):
    # Setter for the "HIincrease" attribute of the global "crop" variable.
    global crop
    crop.HIincrease = HIincrease

def GetCrop_HIincrease():
    # Getter for the "HIincrease" attribute of the global "crop" variable.
    return crop.HIincrease

def SetCrop_aCoeff(aCoeff):
    # Setter for the "aCoeff" attribute of the global "crop" variable.
    global crop
    crop.aCoeff = aCoeff

def GetCrop_aCoeff():
    # Getter for the "aCoeff" attribute of the global "crop" variable.
    return crop.aCoeff

def SetCrop_bCoeff(bCoeff):
    # Setter for the "bCoeff" attribute of the global "crop" variable.
    global crop
    crop.bCoeff = bCoeff

def GetCrop_bCoeff():
    # Getter for the "bCoeff" attribute of the global "crop" variable.
    return crop.bCoeff

def SetCrop_DHImax(DHImax):
    # Setter for the "DHImax" attribute of the global "crop" variable.
    global crop
    crop.DHImax = DHImax

def GetCrop_DHImax():
    # Getter for the "DHImax" attribute of the global "crop" variable.
    return crop.DHImax

def SetCrop_dHIdt(dHIdt):
    # Setter for the "dHIdt" attribute of the global "crop" variable.
    global crop
    crop.dHIdt = dHIdt

def GetCrop_dHIdt():
    # Getter for the "dHIdt" attribute of the global "crop" variable.
    return crop.dHIdt

def SetCrop_GDDaysToCCini(GDDaysToCCini):
    # Setter for the "GDDaysToCCini" attribute of the global "crop" variable.
    global crop
    crop.GDDaysToCCini = GDDaysToCCini

def GetCrop_GDDaysToCCini():
    # Getter for the "GDDaysToCCini" attribute of the global "crop" variable.
    return crop.GDDaysToCCini

def SetCrop_GDDaysToGermination(GDDaysToGermination):
    # Setter for the "GDDaysToGermination" attribute of the global "crop" variable.
    global crop
    crop.GDDaysToGermination = GDDaysToGermination

def GetCrop_GDDaysToGermination():
    # Getter for the "GDDaysToGermination" attribute of the global "crop" variable.
    return crop.GDDaysToGermination

def SetCrop_GDDaysToMaxRooting(GDDaysToMaxRooting):
    # Setter for the "GDDaysToMaxRooting" attribute of the global "crop" variable.
    global crop
    crop.GDDaysToMaxRooting = GDDaysToMaxRooting

def GetCrop_GDDaysToMaxRooting():
    # Getter for the "GDDaysToMaxRooting" attribute of the global "crop" variable.
    return crop.GDDaysToMaxRooting

def SetCrop_GDDaysToSenescence(GDDaysToSenescence):
    # Setter for the "GDDaysToSenescence" attribute of the global "crop" variable.
    global crop
    crop.GDDaysToSenescence = GDDaysToSenescence

def GetCrop_GDDaysToSenescence():
    # Getter for the "GDDaysToSenescence" attribute of the global "crop" variable.
    return crop.GDDaysToSenescence

def SetCrop_GDDaysToHarvest(GDDaysToHarvest):
    # Setter for the "GDDaysToHarvest" attribute of the global "crop" variable.
    global crop
    crop.GDDaysToHarvest = GDDaysToHarvest

def GetCrop_GDDaysToHarvest():
    # Getter for the "GDDaysToHarvest" attribute of the global "crop" variable.
    return crop.GDDaysToHarvest

def SetCrop_GDDaysToFlowering(GDDaysToFlowering):
    # Setter for the "GDDaysToFlowering" attribute of the global "crop" variable.
    global crop
    crop.GDDaysToFlowering = GDDaysToFlowering

def GetCrop_GDDaysToFlowering():
    # Getter for the "GDDaysToFlowering" attribute of the global "crop" variable.
    return crop.GDDaysToFlowering

def SetCrop_GDDLengthFlowering(GDDLengthFlowering):
    # Setter for the "GDDLengthFlowering" attribute of the global "crop" variable.
    global crop
    crop.GDDLengthFlowering = GDDLengthFlowering

def GetCrop_GDDLengthFlowering():
    # Getter for the "GDDLengthFlowering" attribute of the global "crop" variable.
    return crop.GDDLengthFlowering

def SetCrop_GDDaysToHIo(GDDaysToHIo):
    # Setter for the "GDDaysToHIo" attribute of the global "crop" variable.
    global crop
    crop.GDDaysToHIo = GDDaysToHIo

def GetCrop_GDDaysToHIo():
    # Getter for the "GDDaysToHIo" attribute of the global "crop" variable.
    return crop.GDDaysToHIo

def SetCrop_GDDCGC(GDDCGC):
    # Setter for the "GDDCGC" attribute of the global "crop" variable.
    global crop
    crop.GDDCGC = GDDCGC

def GetCrop_GDDCGC():
    # Getter for the "GDDCGC" attribute of the global "crop" variable.
    return crop.GDDCGC

def SetCrop_GDDCDC(GDDCDC):
    # Setter for the "GDDCDC" attribute of the global "crop" variable.
    global crop
    crop.GDDCDC = GDDCDC

def GetCrop_GDDCDC():
    # Getter for the "GDDCDC" attribute of the global "crop" variable.
    return crop.GDDCDC

def SetCrop_Assimilates_On(Assimilates_On):
    # Setter for the "Assimilates_On" attribute of the global "crop" variable.
    global crop
    crop.Assimilates.On = Assimilates_On

def GetCrop_Assimilates():
    # Getter for the "Assimilates" attribute of the global "crop" variable.
    return crop.Assimilates

def SetCrop_Assimilates(Assimilates_in):
    # Setter for the "Assimilates" attribute of the global "crop" variable.
    global crop
    crop.Assimilates = Assimilates_in

def GetCrop_Assimilates_On():
    # Getter for the "Assimilates_On" attribute of the global "crop" variable.
    return crop.Assimilates.On

def SetCrop_Assimilates_Period(Assimilates_Period):
    # Setter for the "Assimilates_Period" attribute of the global "crop" variable.
    global crop
    crop.Assimilates.Period = Assimilates_Period

def GetCrop_Assimilates_Period():
    # Getter for the "Assimilates_Period" attribute of the global "crop" variable.
    return crop.Assimilates.Period

def SetCrop_Assimilates_Stored(Assimilates_Stored):
    # Setter for the "Assimilates_Stored" attribute of the global "crop" variable.
    global crop
    crop.Assimilates.Stored = Assimilates_Stored

def GetCrop_Assimilates_Stored():
    # Getter for the "Assimilates_Stored" attribute of the global "crop" variable.
    return crop.Assimilates.Stored

def SetCrop_Assimilates_Mobilized(Assimilates_Mobilized):
    # Setter for the "Assimilates_Mobilized" attribute of the global "crop" variable.
    global crop
    crop.Assimilates.Mobilized = Assimilates_Mobilized

def GetCrop_Assimilates_Mobilized():
    # Getter for the "Assimilates_Mobilized" attribute of the global "crop" variable.
    return crop.Assimilates.Mobilized

def GetCrop_DaysToFullCanopy():
    # Getter for the "DaysToFullCanopy" attribute of the global "crop" variable.
    return crop.DaysToFullCanopy

def SetCrop_DaysToFullCanopy(DaysToFullCanopy):
    # Setter for the "DaysToFullCanopy" attribute of the global "crop" variable.
    global crop
    crop.DaysToFullCanopy = DaysToFullCanopy

def SetCrop_DaysToFullCanopySF(DaysToFullCanopySF):
    # Setter for the "DaysToFullCanopySF" attribute of the global "crop" variable.
    global crop
    crop.DaysToFullCanopySF = DaysToFullCanopySF

def GetCrop_DaysToFullCanopySF():
    # Getter for the "DaysToFullCanopySF" attribute of the global "crop" variable.
    return crop.DaysToFullCanopySF

def SetCrop_GDDaysToFullCanopy(GDDaysToFullCanopy):
    # Setter for the "GDDaysToFullCanopy" attribute of the global "crop" variable.
    global crop
    crop.GDDaysToFullCanopy = GDDaysToFullCanopy

def SetCrop_GDDaysToFullCanopySF(GDDaysToFullCanopySF):
    # Setter for the "GDDaysToFullCanopySF" attribute of the global "crop" variable.
    global crop
    crop.GDDaysToFullCanopySF = GDDaysToFullCanopySF

def GetCrop_Length():
    # Getter for the "Length" attribute of the global "crop" variable.
    return crop.Length

def SetCrop_Length(Length):
    # Setter for the "Length" attribute of the global "crop" variable.
    global crop
    crop.Length = Length

def GetCrop_CCoAdjusted():
    # Getter for the "CCoAdjusted" attribute of the global "crop" variable.
    return crop.CCoAdjusted

def SetCrop_CCoAdjusted(CCoAdjusted):
    # Setter for the "CCoAdjusted" attribute of the global "crop" variable.
    global crop
    crop.CCoAdjusted = CCoAdjusted

def GetCrop_CCxAdjusted():
    # Getter for the "CCxAdjusted" attribute of the global "crop" variable.
    return crop.CCxAdjusted

def SetCrop_CCxAdjusted(CCxAdjusted):
    # Setter for the "CCxAdjusted" attribute of the global "crop" variable.
    global crop
    crop.CCxAdjusted = CCxAdjusted

def GetCrop_CCxWithered():
    # Getter for the "CCxWithered" attribute of the global "crop" variable.
    return crop.CCxWithered

def SetCrop_CCxWithered(CCxWithered):
    # Setter for the "CCxWithered" attribute of the global "crop" variable.
    global crop
    crop.CCxWithered = CCxWithered

def GetCrop_GDDaysToFullCanopy():
    # Getter for the "GDDaysToFullCanopy" attribute of the global "crop" variable.
    return crop.GDDaysToFullCanopy

def GetCrop_GDDaysToFullCanopySF():
    # Getter for the "GDDaysToFullCanopySF" attribute of the global "crop" variable.
    return crop.GDDaysToFullCanopySF

def GetCrop_StressResponse():
    # Getter for the "StressResponse" attribute of the "crop" global variable.
    return crop.StressResponse

def GetCrop_Day1():
    # Getter for the "Day1" attribute of the "crop" global variable.
    return crop.Day1

def SetCrop_Day1(Day1):
    # Setter for the "Day1" attribute of the "crop" global variable.
    global crop
    crop.Day1 = Day1

def GetCrop_DayN():
    # Getter for the "DayN" attribute of the "crop" global variable.
    return crop.DayN

def SetCrop_DayN(DayN):
    # Setter for the "DayN" attribute of the "crop" global variable.
    global crop
    crop.DayN = DayN

def GetCrop_SmaxTop():
    # Getter for the "SmaxTop" attribute of the global "crop" variable.
    return crop.SmaxTop

def SetCrop_SmaxTop(SmaxTop):
    # Setter for the "SmaxTop" attribute of the global "crop" variable.
    global crop
    crop.SmaxTop = SmaxTop

def GetCrop_SmaxBot():
    # Getter for the "SmaxBot" attribute of the global "crop" variable.
    return crop.SmaxBot

def SetCrop_SmaxBot(SmaxBot):
    # Setter for the "SmaxBot" attribute of the global "crop" variable.
    global crop
    crop.SmaxBot = SmaxBot

def GetIrriInfoLastDay():
    # Getter for the "IrriInfoLastDay" global variable.
    return IrriInfoLastDay

def SetIrriInfoLastDay(IrriInfoLastDay_in):
    global IrriInfoLastDay
    IrriInfoLastDay = IrriInfoLastDay_in


def GetCropFileSet():
    # Getter for the "CropFileSet" global variable.
    return CropFileSet

def SetCropFileSet_DaysFromSenescenceToEnd(DaysFromSenescenceToEnd):
    # Setter for the "CropFileSet" global variable.
    global CropFileSet
    CropFileSet.DaysFromSenescenceToEnd = DaysFromSenescenceToEnd

def SetCropFileSet_DaysToHarvest(DaysToHarvest):
    # Setter for the "CropFileSet" global variable.
    global CropFileSet
    CropFileSet.DaysToHarvest = DaysToHarvest

def SetCropFileSet_GDDaysFromSenescenceToEnd(GDDaysFromSenescenceToEnd):
    # Setter for the "CropFileSet" global variable.
    global CropFileSet
    CropFileSet.GDDaysFromSenescenceToEnd = GDDaysFromSenescenceToEnd

def SetCropFileSet_GDDaysToHarvest(GDDaysToHarvest):
    # Setter for the "CropFileSet" global variable.
    global CropFileSet
    CropFileSet.GDDaysToHarvest = GDDaysToHarvest

def GetManagement():
    # Getter for the "Management" global variable.
    return Management

def SetManagement(management_in):
    # Setter for the "Management" global variable.
    global Management
    Management = management_in

def SetManagement_FertilityStress(FertilityStress):
    # Setter for the "Management" global variable.
    global Management
    Management.FertilityStress = FertilityStress

def GetManagement_FertilityStress():
    # Getter for the "Management" global variable.
    return Management.FertilityStress

def GetManagement_Cuttings():
    # Getter for the "Cuttings" global variable.
    return Management.Cuttings

def SetManagement_Cuttings(Cuttings_in):
    # Setter for the "Management" global variable.
    global Management
    Management.Cuttings = Cuttings_in

def SetManagement_Mulch(Mulch):
    # Setter for the "Management" global variable.
    global Management
    Management.Mulch = Mulch

def GetManagement_Mulch():
    # Getter for the "Management" global variable.
    return Management.Mulch

def SetManagement_EffectMulchInS(EffectMulchInS):
    # Setter for the "Management" global variable.
    global Management
    Management.EffectMulchInS = EffectMulchInS

def GetManagement_EffectMulchInS():
    # Getter for the "Management" global variable.
    return Management.EffectMulchInS

def SetManagement_BundHeight(BundHeight):
    # Setter for the "Management" global variable.
    global Management
    Management.BundHeight = BundHeight

def GetManagement_BundHeight():
    # etter for the "Management" global variable.
    return Management.BundHeight

def SetManagement_RunoffOn(RunoffOn):
    # Setter for the "Management" global variable.
    global Management
    Management.RunoffOn = RunoffOn

def GetManagement_RunoffOn():
    # Getter for the "Management" global variable.
    return Management.RunoffOn

def SetManagement_CNcorrection(CNcorrection):
    # Setter for the "Management" global variable.
    global Management
    Management.CNcorrection = CNcorrection

def GetManagement_CNcorrection():
    # Getter for the "Management" global variable.
    return Management.CNcorrection

def SetManagement_WeedRC(WeedRC):
    # Setter for the "Management" global variable.
    global Management
    Management.WeedRC = WeedRC

def GetManagement_WeedRC():
    # Getter for the "Management" global variable.
    return Management.WeedRC

def SetManagement_WeedDeltaRC(WeedDeltaRC):
    # Setter for the "Management" global variable.
    global Management
    Management.WeedDeltaRC = WeedDeltaRC

def GetManagement_WeedDeltaRC():
    # Getter for the "Management" global variable.
    return Management.WeedDeltaRC

def SetManagement_WeedShape(WeedShape):
    # Setter for the "Management" global variable.
    global Management
    Management.WeedShape = WeedShape

def GetManagement_WeedShape():
    # Getter for the "Management" global variable.
    return Management.WeedShape

def SetManagement_WeedAdj(WeedAdj):
    # Setter for the "Management" global variable.
    global Management
    Management.WeedAdj = WeedAdj

def GetManagement_WeedAdj():
    # Getter for the "Management" global variable.
    return Management.WeedAdj

def SetManagement_SoilCoverBefore(SoilCoverBefore):
    # Setter for the "Management" global variable.
    global Management
    Management.SoilCoverBefore = SoilCoverBefore

def GetManagement_SoilCoverBefore():
    # Getter for the "Management" global variable.
    return Management.SoilCoverBefore

def SetManagement_SoilCoverAfter(SoilCoverAfter):
    # Setter for the "Management" global variable.
    global Management
    Management.SoilCoverAfter = SoilCoverAfter

def GetManagement_SoilCoverAfter():
    # Getter for the "Management" global variable.
    return Management.SoilCoverAfter

def SetManagement_EffectMulchOffS(EffectMulchOffS):
    # Setter for the "Management" global variable.
    global Management
    Management.EffectMulchOffS = EffectMulchOffS

def GetManagement_EffectMulchOffS():
    # Getter for the "Management" global variable.
    return Management.EffectMulchOffS

def GetManagement_Cuttings_Considered():
    # Getter for the "Cuttings" global variable.
    return Cuttings.Considered

def SetManagement_Cuttings_Considered(Considered):
    # Setter for the "Cuttings" global variable.
    global Cuttings
    Cuttings.Considered = Considered

def GetSimulParam_IrriFwOffSeason():
    # Getter for the "SimulParam" global variable.
    return simulparam.IrriFwOffSeason

def SetManagement_Cuttings_CCcut(CCcut):
    # Setter for the "Cuttings" global variable.
    global Cuttings
    Cuttings.CCcut = CCcut

def GetManagement_Cuttings_CCcut():
    # Getter for the "Cuttings" global variable.
    return Cuttings.CCcut

def SetManagement_Cuttings_Day1(Day1):
    # Setter for the "Cuttings" global variable.
    global Cuttings
    Cuttings.Day1 = Day1

def GetManagement_Cuttings_Day1():
    # Getter for the "Cuttings" global variable.
    return Cuttings.Day1

def SetManagement_Cuttings_NrDays(NrDays):
    # Setter for the "Cuttings" global variable.
    global Cuttings
    Cuttings.NrDays = NrDays

def GetManagement_Cuttings_NrDays():
    # Getter for the "Cuttings" global variable.
    return Cuttings.NrDays

def SetManagement_Cuttings_Generate(Generate):
    # Setter for the "Cuttings" global variable.
    global Cuttings
    Cuttings.Generate = Generate

def GetManagement_Cuttings_Generate():
    # Getter for the "Management" global variable.
    return Cuttings.Generate

def SetManagement_Cuttings_Criterion(Criterion):
    # Setter for the "Cuttings" global variable.
    global Cuttings
    Cuttings.Criterion = Criterion

def GetManagement_Cuttings_Criterion():
    # Getter for the "Management" global variable.
    return Cuttings.Criterion

def SetManagement_Cuttings_HarvestEnd(HarvestEnd):
    # Setter for the "Cuttings" global variable.
    global Cuttings
    Cuttings.HarvestEnd = HarvestEnd

def GetManagement_Cuttings_HarvestEnd():
    # Getter for the "Cuttings" global variable.
    return Cuttings.HarvestEnd

def SetManagement_Cuttings_FirstDayNr(FirstDayNr):
    # Setter for the "Cuttings" global variable.
    global Cuttings
    Cuttings.FirstDayNr = FirstDayNr

def GetManagement_Cuttings_FirstDayNr():
    # Getter for the "Cuttings" global variable.
    return Cuttings.FirstDayNr

def GetEpot():
    # Getter for the "Epot" global variable.
    return Epot

def SetEpot(Epot_in):
    # Setter for the "Epot" global variable.
    global Epot
    Epot = Epot_in

def GetSumWaBal_Epot():
    # Getter for the "Epot" attribute of the "SumWaBal" global variable.
    return SumWaBal.Epot

def SetSumWaBal_Epot(Epot):
    # Setter for the "Epot" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Epot = Epot

def GetTpot():
    # Getter for the "Tpot" global variable.
    return Tpot

def SetTpot(Tpot_in):
    # Setter for the "Tpot" global variable.
    global Tpot
    Tpot = Tpot_in

def GetSumWaBal_Tpot():
    # Getter for the "Tpot" attribute of the "SumWaBal" global variable.
    return SumWaBal.Tpot

def SetSumWaBal_Tpot(Tpot):
    # Setter for the "Tpot" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Tpot = Tpot

def GetSumWaBal_Rain():
    # Getter for the "Rain" attribute of the "SumWaBal" global variable.
    return SumWaBal.Rain

def SetSumWaBal_Rain(Rain):
    # Setter for the "Rain" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Rain = Rain

def GetSumWaBal_Irrigation():
    # Getter for the "Irrigation" attribute of the "SumWaBal" global variable.
    return SumWaBal.Irrigation

def SetSumWaBal_Irrigation(Irrigation):
    # Setter for the "Irrigation" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Irrigation = Irrigation

def GetSumWaBal_Infiltrated():
    # Getter for the "Infiltrated" attribute of the "SumWaBal" global variable.
    return SumWaBal.Infiltrated

def SetSumWaBal_Infiltrated(Infiltrated):
    # Setter for the "Infiltrated" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Infiltrated = Infiltrated

def GetSumWaBal_Runoff():
    # Getter for the "Runoff" attribute of the "SumWaBal" global variable.
    return SumWaBal.Runoff

def SetSumWaBal_Runoff(Runoff):
    # Setter for the "Runoff" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Runoff = Runoff

def GetSumWaBal_Drain():
    # Getter for the "Drain" attribute of the "SumWaBal" global variable.
    return SumWaBal.Drain

def SetSumWaBal_Drain(Drain):
    # Setter for the "Drain" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Drain = Drain

def GetSumWaBal_Eact():
    # Getter for the "Eact" attribute of the "SumWaBal" global variable.
    return SumWaBal.Eact

def SetSumWaBal_Eact(Eact):
    # Setter for the "Eact" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Eact = Eact

def GetSumWaBal_Tact():
    # Getter for the "Tact" attribute of the "SumWaBal" global variable.
    return SumWaBal.Tact

def SetSumWaBal_Tact(Tact):
    # Setter for the "Tact" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Tact = Tact

def GetSumWaBal_TrW():
    # Getter for the "TrW" attribute of the "SumWaBal" global variable.
    return SumWaBal.TrW

def SetSumWaBal_TrW(TrW):
    # Setter for the "TrW" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.TrW = TrW

def GetSumWaBal_ECropCycle():
    # Getter for the "ECropCycle" attribute of the "SumWaBal" global variable.
    return SumWaBal.ECropCycle

def SetSumWaBal_ECropCycle(ECropCycle):
    # Setter for the "ECropCycle" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.ECropCycle = ECropCycle

def GetSumWaBal_CRwater():
    # Getter for the "CRwater" attribute of the "SumWaBal" global variable.
    return SumWaBal.CRwater

def SetSumWaBal_CRwater(CRwater):
    # Setter for the "CRwater" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.CRwater = CRwater

def GetSumWaBal_Biomass():
    # Getter for the "Biomass" attribute of the "SumWaBal" global variable.
    return SumWaBal.Biomass

def SetSumWaBal_Biomass(Biomass):
    # Setter for the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.Biomass = Biomass

def GetSumWaBal_BiomassPot():
    # Getter for the "BiomassPot" attribute of the "SumWaBal" global variable.
    return SumWaBal.BiomassPot

def SetSumWaBal_BiomassPot(BiomassPot):
    # Setter for the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.BiomassPot = BiomassPot

def GetSumWaBal_BiomassUnlim():
    # Getter for the "BiomassUnlim" attribute of the "SumWaBal" global variable.
    return SumWaBal.BiomassUnlim

def SetSumWaBal_BiomassUnlim(BiomassUnlim):
    # Setter for the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.BiomassUnlim = BiomassUnlim

def GetSumWaBal_BiomassTot():
    # Getter for the "BiomassTot" attribute of the "SumWaBal" global variable.
    return SumWaBal.BiomassTot

def SetSumWaBal_BiomassTot(BiomassTot):
    # Setter for the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.BiomassTot = BiomassTot

def GetSumWaBal_YieldPart():
    # Getter for the "YieldPart" attribute of the "SumWaBal" global variable.
    return SumWaBal.YieldPart

def SetSumWaBal_YieldPart(YieldPart):
    # Setter for the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.YieldPart = YieldPart

def SetSumWaBal(SumWaBal_in):
    # Setter for the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal = SumWaBal_in

def GetSumWaBal_SaltIn():
    # Getter for the "SaltIn" attribute of the "SumWaBal" global variable.
    return SumWaBal.SaltIn

def SetSumWaBal_SaltIn(SaltIn):
    # Setter for the "SaltIn" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.SaltIn = SaltIn

def GetSumWaBal_SaltOut():
    # Getter for the "SaltOut" attribute of the "SumWaBal" global variable.
    return SumWaBal.SaltOut

def SetSumWaBal_SaltOut(SaltOut):
    # Setter for the "SaltOut" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.SaltOut = SaltOut

def GetSumWaBal_CRSalt():
    # Getter for the "CRSalt" attribute of the "SumWaBal" global variable.
    return SumWaBal.CRsalt

def SetSumWaBal_CRSalt(CRSalt):
    # Setter for the "CRSalt" attribute of the "SumWaBal" global variable.
    global SumWaBal
    SumWaBal.CRsalt = CRSalt

def GetSumWaBal():
    # Getter for the "SumWaBal" global variable.
    return SumWaBal

def SetIrriMode(int_in):
    # Setter for the "IrriMode" global variable.
    global IrriMode
    IrriMode = int_in

def GetIrriMode():
    # Getter for the "IrriMode" global variable.
    return IrriMode

def SetETo(ETo_in):
    # Setter for the "ETo" global variable.
    global ETo
    ETo = ETo_in

def GetETo():
    # Getter for the "ETo" global variable.
    return ETo

def SetRain(Rain_in):
    # Setter for the "Rain" global variable.
    global Rain
    Rain = Rain_in

def GetRain():
    # Getter for the "Rain" global variable.
    return Rain

def SetIrrigation(Irrigation_in):
    # Setter for the "Irrigation" global variable.
    global Irrigation
    Irrigation = Irrigation_in

def GetIrrigation():
    # Getter for the "Irrigation" global variable.
    return Irrigation

def SetSurfaceStorage(SurfaceStorage_in):
    # Setter for the "SurfaceStorage" global variable.
    global SurfaceStorage
    SurfaceStorage = SurfaceStorage_in

def GetSurfaceStorage():
    # Getter for the "SurfaceStorage" global variable.
    return SurfaceStorage

def SetECstorage(ECstorage_in):
    # Setter for the "ECstorage" global variable.
    global ECstorage
    ECstorage = ECstorage_in

def GetECstorage():
    # Getter for the "ECstorage" global variable.
    return ECstorage

def SetDaySubmerged(DaySubmerged_in):
    # Setter for the "DaySubmerged" global variable.
    global DaySubmerged
    DaySubmerged = DaySubmerged_in

def GetDaySubmerged():
    # Getter for the "DaySubmerged" global variable.
    return DaySubmerged

def SetDrain(Drain_in):
    # Setter for the "Drain" global variable.
    global Drain
    Drain = Drain_in

def GetDrain():
    # Getter for the "Drain" global variable.
    return Drain

def SetRunoff(Runoff_in):
    # Setter for the "Runoff" global variable.
    global Runoff
    Runoff = Runoff_in

def GetRunoff():
    # Getter for the "Runoff" global variable.
    return Runoff

def SetInfiltrated(Infiltrated_in):
    # Setter for the "Infiltrated" global variable.
    global Infiltrated
    Infiltrated = Infiltrated_in

def GetInfiltrated():
    # Getter for the "Infiltrated" global variable.
    return Infiltrated

def SetCRwater(CRwater_in):
    # Setter for the "CRwater" global variable.
    global CRwater
    CRwater = CRwater_in

def GetCRwater():
    # Getter for the "CRwater" global variable.
    return CRwater

def GetCCiActual():
    # Getter for the "CCiActual" global variable.
    return CCiActual

def SetCCiActual(CCiActual_in):
    # Setter for the "CCiActual" global variable.
    global CCiActual
    CCiActual = CCiActual_in

def SetCRsalt(CRsalt_in):
    # Setter for the "CRsalt" global variable.
    global CRsalt
    CRsalt = CRsalt_in

def GetCRsalt():
    # Getter for the "CRsalt" global variable.
    return CRsalt

def SetMaxPlotNew(MaxPlotNew_in):
    # Setter for the "MaxPlotNew" global variable.
    global MaxPlotNew
    MaxPlotNew = MaxPlotNew_in

def GetMaxPlotNew():
    # Getter for the "MaxPlotNew" global variable.
    return MaxPlotNew

def SetMaxPlotTr(MaxPlotTr_in):
    # Setter for the "MaxPlotTr" global variable.
    global MaxPlotTr
    MaxPlotTr = MaxPlotTr_in

def GetMaxPlotTr():
    # Getter for the "MaxPlotTr" global variable.
    return MaxPlotTr

def GlobalZero(SumWabal):
    i = None

    SumWabal.Epot = 0.0
    SumWabal.Tpot = 0.0
    SumWabal.Rain = 0.0
    SumWabal.Irrigation = 0.0
    SumWabal.Infiltrated = 0.0
    SumWabal.Runoff = 0.0
    SumWabal.Drain = 0.0
    SumWabal.Eact = 0.0
    SumWabal.Tact = 0.0
    SumWabal.TrW = 0.0
    SumWabal.ECropCycle = 0.0
    SumWabal.Biomass = 0.0
    SumWabal.BiomassPot = 0.0
    SumWabal.BiomassUnlim = 0.0
    SumWabal.BiomassTot = 0.0  # crop and weeds (for soil fertility stress)
    SumWabal.YieldPart = 0.0
    SumWabal.SaltIn = 0.0
    SumWabal.SaltOut = 0.0
    SumWabal.CRwater = 0.0
    SumWabal.CRsalt = 0.0
    SetTotalWaterContent_BeginDay(0.0)

    for i in range(1, GetNrCompartments() + 1):
        SetTotalWaterContent_BeginDay(
            GetTotalWaterContent_BeginDay()
            + GetCompartment_theta(i) * 1000.0 * GetCompartment_Thickness(i)
        )

    return SumWabal


def KsAny(Wrel, pULActual, pLLActual, ShapeFactor):
    pULActual_local = pULActual
    # Wrel : WC in rootzone (negative .... 0=FC ..... 1=WP .... > 1)
    #        FC .. UpperLimit ... LowerLimit .. WP
    # p relative (negative .... O=UpperLimit ...... 1=LowerLimit .....>1)

    if (pLLActual - pULActual_local) < 0.0001:
        pULActual_local = pLLActual - 0.0001

    pRelativeLLUL = (Wrel - pULActual_local) / (pLLActual - pULActual_local)

    if pRelativeLLUL <= 0.0:
        KsVal = 1.0
    elif pRelativeLLUL >= 1.0:
        KsVal = 0.0
    else:
        if roundc(10 * ShapeFactor, mold="int32") == 0:  # straight line
            KsVal = 1.0 - (
                math.exp(pRelativeLLUL * 0.01) - 1.0
            ) / (math.exp(0.01) - 1.0)
        else:
            KsVal = 1.0 - (
                math.exp(pRelativeLLUL * ShapeFactor) - 1.0
            ) / (math.exp(ShapeFactor) - 1.0)
        if KsVal > 1.0:
            KsVal = 1.0
        if KsVal < 0.0:
            KsVal = 0.0

    return KsVal


def CropStressParametersSoilFertility(CropSResp, StressLevel, StressOUT):
    pLLActual = 1.0

    # decline canopy growth coefficient (CGC)
    pULActual = 0.0
    Ksi = KsAny(StressLevel / 100.0, pULActual, pLLActual, CropSResp.ShapeCGC)
    StressOUT.RedCGC = roundc((1.0 - Ksi) * 100.0, mold="int8")

    # decline maximum canopy cover (CCx)
    pULActual = 0.0
    Ksi = KsAny(StressLevel / 100.0, pULActual, pLLActual, CropSResp.ShapeCCX)
    StressOUT.RedCCX = roundc((1.0 - Ksi) * 100.0, mold="int8")

    # decline crop water productivity (WP)
    pULActual = 0.0
    Ksi = KsAny(StressLevel / 100.0, pULActual, pLLActual, CropSResp.ShapeWP)
    StressOUT.RedWP = roundc((1.0 - Ksi) * 100.0, mold="int8")

    # decline Canopy Cover (CDecline)
    pULActual = 0.0
    Ksi = KsAny(StressLevel / 100.0, pULActual, pLLActual, CropSResp.ShapeCDecline)
    StressOUT.CDecline = 1.0 - Ksi

    # inducing stomatal closure (KsSto) not applicable
    Ksi = 1.0
    StressOUT.RedKsSto = roundc((1.0 - Ksi) * 100.0, mold="int8")

    return StressOUT


def NoManagement():
    EffectStress_temp = rep_EffectStress()

    SetManDescription('No specific field management')
    # mulches
    SetManagement_Mulch(0)
    SetManagement_EffectMulchInS(50)
    # soil fertility
    SetManagement_FertilityStress(0)
    EffectStress_temp = GetSimulation_EffectStress()

    EffectStress_temp = CropStressParametersSoilFertility(
        GetCrop_StressResponse(),
        GetManagement_FertilityStress(),
        EffectStress_temp
    )

    SetSimulation_EffectStress(EffectStress_temp)
    # soil bunds
    SetManagement_BundHeight(0.0)
    SetSimulation_SurfaceStorageIni(0.0)
    SetSimulation_ECStorageIni(0.0)
    # surface run-off
    SetManagement_RunoffOn(True)
    SetManagement_CNcorrection(0)
    # weed infestation
    SetManagement_WeedRC(0)
    SetManagement_WeedDeltaRC(0)
    SetManagement_WeedShape(-0.01)
    SetManagement_WeedAdj(100)
    # multiple cuttings
    SetManagement_Cuttings_Considered(False)
    SetManagement_Cuttings_CCcut(30)
    SetManagement_Cuttings_Day1(1)
    SetManagement_Cuttings_NrDays(undef_int)
    SetManagement_Cuttings_Generate(False)
    SetManagement_Cuttings_Criterion(TimeCuttings_NA)
    SetManagement_Cuttings_HarvestEnd(False)
    SetManagement_Cuttings_FirstDayNr(undef_int)



def SaveCrop(totalname):

    lines = []
    lines.append(f"{GetCropDescription()}")
    lines.append(f"     {GetVersionString()}       : AquaCrop Version ({GetReleaseDate()})")
    lines.append("     1         : File not protected")

    # SubKind
    i = 2
    sk = GetCrop_subkind()
    if sk == subkind_Vegetative:
        i = 1
        TempString = '         : leafy vegetable crop'
    elif sk == subkind_Grain:
        i = 2
        TempString = '         : fruit/grain producing crop'
    elif sk == subkind_Tuber:
        i = 3
        TempString = '         : root/tuber crop'
    elif sk == subkind_Forage:
        i = 4
        TempString = '         : forage crop'
    lines.append(f"{i:6d}{TempString}")

    # Sown, transplanting or regrowth
    if GetCrop_Planting() == plant_Seed:
        i = 1
        if GetCrop_subkind() == subkind_Forage:
            lines.append(f"{i:6d}         : Crop is sown in 1st year")
        else:
            lines.append(f"{i:6d}         : Crop is sown")
    else:
        if GetCrop_Planting() == plant_transplant:
            i = 0
            if GetCrop_subkind() == subkind_Forage:
                lines.append(f"{i:6d}         : Crop is transplanted in 1st year")
            else:
                lines.append(f"{i:6d}         : Crop is transplanted")
        else:
            i = -9
            lines.append(f"{i:6d}         : Crop is regrowth")

    # Mode (description crop cycle)
    i = 1
    TempString = '         : Determination of crop cycle : by calendar days'
    if GetCrop_ModeCycle() == ModeCycle_GDDays:
        i = 0
        TempString = '         : Determination of crop cycle : by growing degree-days'
    lines.append(f"{i:6d}{TempString}")

    # p correction for ET
    if GetCrop_pMethod() == pMethod_NoCorrection:
        j = 0
        lines.append(f"{j:6d}         : No adjustment by ETo of soil water depletion factors (p)")
    else:
        j = 1
        lines.append(f"{j:6d}         : Soil water depletion factors (p) are adjusted by ETo")

    # temperatures controlling crop development
    lines.append(f"{GetCrop_Tbase():8.1f}       : Base temperature (degC) below which crop development does not progress")
    lines.append(f"{GetCrop_Tupper():8.1f}       : Upper temperature (degC) above which crop development no longer increases with an increase in temperature")

    # required growing degree days to complete the crop cycle (is identical as to maturity)
    lines.append(f"{int(GetCrop_GDDaysToHarvest()):6d}         : Total length of crop cycle in growing degree-days")

    # water stress
    lines.append(f"{GetCrop_pLeafDefUL():9.2f}      : Soil water depletion factor for canopy expansion (p-exp) - Upper threshold")
    lines.append(f"{GetCrop_pLeafDefLL():9.2f}      : Soil water depletion factor for canopy expansion (p-exp) - Lower threshold")
    lines.append(f"{GetCrop_KsShapeFactorLeaf():8.1f}       : Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)")
    lines.append(f"{GetCrop_pdef():9.2f}      : Soil water depletion fraction for stomatal control (p - sto) - Upper threshold")
    lines.append(f"{GetCrop_KsShapeFactorStomata():8.1f}       : Shape factor for water stress coefficient for stomatal control (0.0 = straight line)")
    lines.append(f"{GetCrop_pSenescence():9.2f}      : Soil water depletion factor for canopy senescence (p - sen) - Upper threshold")
    lines.append(f"{GetCrop_KsShapeFactorSenescence():8.1f}       : Shape factor for water stress coefficient for canopy senescence (0.0 = straight line)")
    lines.append(f"{int(GetCrop_SumEToDelaySenescence()):6d}         : Sum(ETo) during dormant period to be exceeded before crop is permanently wilted")

    val_p_pol = GetCrop_pPollination()
    if abs(val_p_pol - float(undef_int)) < sys.float_info.epsilon:
        lines.append(f"{val_p_pol:9.2f}      : Soil water depletion factor for pollination - Not Applicable")
    else:
        lines.append(f"{val_p_pol:9.2f}      : Soil water depletion factor for pollination (p - pol) - Upper threshold")

    lines.append(f"{GetCrop_AnaeroPoint():6d}         : Vol% for Anaerobiotic point (* (SAT - [vol%]) at which deficient aeration occurs *)")

    # stress response
    lines.append(f"{GetCrop_StressResponse_Stress():6d}         : Considered soil fertility stress for calibration of stress response (%)")
    if GetCrop_StressResponse_ShapeCGC() > 24.9:
        lines.append(f"{GetCrop_StressResponse_ShapeCGC():9.2f}      : Response of canopy expansion is not considered")
    else:
        lines.append(f"{GetCrop_StressResponse_ShapeCGC():9.2f}      : Shape factor for the response of canopy expansion to soil fertility stress")
    
    if GetCrop_StressResponse_ShapeCCX() > 24.9:
        lines.append(f"{GetCrop_StressResponse_ShapeCCX():9.2f}      : Response of maximum canopy cover is not considered")
    else:
        lines.append(f"{GetCrop_StressResponse_ShapeCCX():9.2f}      : Shape factor for the response of maximum canopy cover to soil fertility stress")

    if GetCrop_StressResponse_ShapeWP() > 24.9:
        lines.append(f"{GetCrop_StressResponse_ShapeWP():9.2f}      : Response of crop Water Productivity is not considered")
    else:
        lines.append(f"{GetCrop_StressResponse_ShapeWP():9.2f}      : Shape factor for the response of crop Water Productivity to soil fertility stress")

    if GetCrop_StressResponse_ShapeCDecline() > 24.9:
        lines.append(f"{GetCrop_StressResponse_ShapeCDecline():9.2f}      : Response of decline of canopy cover is not considered")
    else:
        lines.append(f"{GetCrop_StressResponse_ShapeCDecline():9.2f}      : Shape factor for the response of decline of canopy cover to soil fertility stress")

    # New 7.3 Premature end of growth of annual crops when too cold to reach maturity
    lines.append('    -9         : dummy - Parameter no Longer required')
    if GetCrop_subkind() == subkind_Forage:
        SetCrop_PrematureEnd(undef_int)

    lines.append(
        f"{int(GetCrop_PrematureEnd()):6d}         : DayNr Premature end (counting from 1 January of planting year) - only applicable for annual crops"
    )

    # temperature stress
    if int(GetCrop_Tcold()) == int(undef_int):
        lines.append(f"{int(GetCrop_Tcold()):6d}         : Cold (air temperature) stress affecting pollination - not considered")
    else:
        lines.append(f"{int(GetCrop_Tcold()):6d}         : Minimum air temperature below which pollination starts to fail (cold stress) (degC)")

    if int(GetCrop_Theat()) == int(undef_int):
        lines.append(f"{int(GetCrop_Theat()):6d}         : Heat (air temperature) stress affecting pollination - not considered")
    else:
        lines.append(f"{int(GetCrop_Theat()):6d}         : Maximum air temperature above which pollination starts to fail (heat stress) (degC)")

    if int(roundc(GetCrop_GDtranspLow(), mold="int32")) == int(undef_int):
        lines.append(f"{GetCrop_GDtranspLow():8.1f}       : Cold (air temperature) stress on crop transpiration not considered")
    else:
        lines.append(f"{GetCrop_GDtranspLow():8.1f}       : Minimum growing degrees required for full crop transpiration (degC - day)")

    # salinity stress
    lines.append(f"{GetCrop_ECemin():6d}         : Electrical Conductivity of soil saturation extract at which crop starts to be affected by soil salinity (dS/m)")
    lines.append(f"{GetCrop_ECemax():6d}         : Electrical Conductivity of soil saturation extract at which crop can no longer grow (dS/m)")
    lines.append('    -9         : Dummy - no longer applicable')  # shape factor Ks(salt)-ECe
    lines.append(f"{GetCrop_CCsaltDistortion():6d}         : Calibrated distortion (%) of CC due to salinity stress (Range: 0 (none) to +100 (very strong))")
    lines.append(f"{GetCrop_ResponseECsw():6d}         : Calibrated response (%) of stomata stress to ECsw (Range: 0 (none) to +200 (extreme))")

    # evapotranspiration
    lines.append(f"{GetCrop_KcTop():9.2f}      : Crop coefficient when canopy is complete but prior to senescence (KcTr,x)")
    lines.append(f"{GetCrop_KcDeclineCumul():6.0f}     : Cumulative decrease (%) at maturity of crop coefficient as a result of ageing, nitrogen deficiency, etc.")
    lines.append(f"{GetCrop_RootMin():9.2f}      : Minimum effective rooting depth (m)")
    lines.append(f"{GetCrop_RootMax():9.2f}      : Maximum effective rooting depth (m)")
    lines.append(f"{GetCrop_RootShape():6d}         : Shape factor describing root zone expansion")
    lines.append(f"{GetCrop_SmaxTopQuarter():10.3f}     : Maximum root water extraction (m3water/m3soil.day) in top quarter of root zone")
    lines.append(f"{GetCrop_SmaxBotQuarter():10.3f}     : Maximum root water extraction (m3water/m3soil.day) in bottom quarter of root zone")
    lines.append(f"{GetCrop_CCEffectEvapLate():6d}         : Effect of canopy cover in reducing soil evaporation in late season stage")

    # canopy development
    lines.append(f"{GetCrop_SizeSeedling():9.2f}      : Soil surface covered by an individual seedling at 90 % emergence (cm2)")
    lines.append(f"{GetCrop_SizePlant():9.2f}      : Canopy size of individual plant (re-growth) at 1st day (cm2)")
    lines.append(f"{GetCrop_PlantingDens():9d}      : Number of plants per hectare")
    lines.append(f"{GetCrop_CGC():12.5f}   : Canopy growth coefficient (CGC): Increase in canopy cover (fraction soil cover per day)")

    if GetCrop_YearCCx() == int(undef_int):
        lines.append(f"{GetCrop_YearCCx():6d}         : Number of years at which CCx declines to 90 % of its value due to self-thinning - Not Applicable")
    else:
        lines.append(f"{GetCrop_YearCCx():6d}         : Number of years at which CCx declines to 90 % of its value due to self-thinning - for Perennials")

    if int(roundc(GetCrop_CCxRoot(), mold="int32")) == int(undef_int):
        lines.append(f"{GetCrop_CCxRoot():9.2f}      : Shape factor of the decline of CCx over the years due to self-thinning - Not Applicable")
    else:
        lines.append(f"{GetCrop_CCxRoot():9.2f}      : Shape factor of the decline of CCx over the years due to self-thinning - for Perennials")

    lines.append('    -9         : dummy - Parameter no Longer required')

    lines.append(f"{GetCrop_CCx():9.2f}      : Maximum canopy cover (CCx) in fraction soil cover")
    lines.append(f"{GetCrop_CDC():12.5f}   : Canopy decline coefficient (CDC): Decrease in canopy cover (in fraction per day)")

    if GetCrop_Planting() == plant_Seed:
        lines.append(f"{GetCrop_DaysToGermination():6d}         : Calendar Days: from sowing to emergence")
        lines.append(f"{GetCrop_DaysToMaxRooting():6d}         : Calendar Days: from sowing to maximum rooting depth")
        lines.append(f"{GetCrop_DaysToSenescence():6d}         : Calendar Days: from sowing to start senescence")
        lines.append(f"{GetCrop_DaysToHarvest():6d}         : Calendar Days: from sowing to maturity (length of crop cycle)")
        if GetCrop_subkind() == subkind_Tuber:
            lines.append(f"{GetCrop_DaysToFlowering():6d}         : Calendar Days: from sowing to start of yield formation")
        else:
            lines.append(f"{GetCrop_DaysToFlowering():6d}         : Calendar Days: from sowing to flowering")
    else:
        if GetCrop_Planting() == plant_transplant:
            lines.append(f"{GetCrop_DaysToGermination():6d}         : Calendar Days: from transplanting to recovered transplant")
            lines.append(f"{GetCrop_DaysToMaxRooting():6d}         : Calendar Days: from transplanting to maximum rooting depth")
            lines.append(f"{GetCrop_DaysToSenescence():6d}         : Calendar Days: from transplanting to start senescence")
            lines.append(f"{GetCrop_DaysToHarvest():6d}         : Calendar Days: from transplanting to maturity")
            if GetCrop_subkind() == subkind_Tuber:
                lines.append(f"{GetCrop_DaysToFlowering():6d}         : Calendar Days: from transplanting to start of yield formation")
            else:
                lines.append(f"{GetCrop_DaysToFlowering():6d}         : Calendar Days: from transplanting to flowering")
        else:
            # planting = regrowth
            lines.append(f"{GetCrop_DaysToGermination():6d}         : Calendar Days: from regrowth to recovering")
            lines.append(f"{GetCrop_DaysToMaxRooting():6d}         : Calendar Days: from regrowth to maximum rooting depth")
            lines.append(f"{GetCrop_DaysToSenescence():6d}         : Calendar Days: from regrowth to start senescence")
            lines.append(f"{GetCrop_DaysToHarvest():6d}         : Calendar Days: from regrowth to maturity")
            if GetCrop_subkind() == subkind_Tuber:
                lines.append(f"{GetCrop_DaysToFlowering():6d}         : Calendar Days: from regrowth to start of yield formation")
            else:
                lines.append(f"{GetCrop_DaysToFlowering():6d}         : Calendar Days: from regrowth to flowering")

    lines.append(f"{GetCrop_LengthFlowering():6d}         : Length of the flowering stage (days)")

    # Crop.DeterminancyLinked
    if GetCrop_DeterminancyLinked() is True:
        i = 1
        TempString = '         : Crop determinancy linked with flowering'
    else:
        i = 0
        TempString = '         : Crop determinancy unlinked with flowering'
    lines.append(f"{i:6d}{TempString}")

    # Potential excess of fruits (%)
    if (GetCrop_subkind() == subkind_Vegetative) or (GetCrop_subkind() == subkind_Forage):
        lines.append(f"{undef_int:6d}         : parameter NO LONGER required")
    else:
        if GetCrop_fExcess() == undef_int:
            TempString = '         : Excess of potential fruits - Not Applicable'
        else:
            TempString = '         : Excess of potential fruits (%)'
        lines.append(f"{GetCrop_fExcess():6d}{TempString}")

    # Building-up of Harvest Index
    if GetCrop_DaysToHIo() == undef_int:
        TempString = '         : Building up of Harvest Index - Not Applicable'
    else:
        sc = GetCrop_subkind()
        if (sc == subkind_Vegetative) or (sc == subkind_Forage):
            TempString = '         : Building up of Harvest Index starting at sowing/transplanting (days)'
        elif sc == subkind_Grain:
            TempString = '         : Building up of Harvest Index starting at flowering (days)'
        elif sc == subkind_Tuber:
            TempString = '         : Building up of Harvest Index starting at root/tuber enlargement (days)'
        else:
            TempString = '         : Building up of Harvest Index during yield formation (days)'
    lines.append(f"{GetCrop_DaysToHIo():6d}{TempString}")

    # yield response to water
    lines.append(f"{GetCrop_WP():8.1f}       : Water Productivity normalized for ETo and CO2 (WP*) (gram/m2)")
    lines.append(f"{GetCrop_WPy():6d}         : Water Productivity normalized for ETo and CO2 during yield formation (as % WP*)")
    lines.append(f"{GetCrop_AdaptedToCO2():6d}         : Crop performance under elevated atmospheric CO2 concentration (%)")
    lines.append(f"{GetCrop_HI():6d}         : Reference Harvest Index (HIo) (%)")
    if GetCrop_subkind() == subkind_Tuber:
        lines.append(f"{GetCrop_HIincrease():6d}         : Possible increase (%) of HI due to water stress before start of yield formation")
    else:
        lines.append(f"{GetCrop_HIincrease():6d}         : Possible increase (%) of HI due to water stress before flowering")
    if int(roundc(GetCrop_aCoeff(), mold="int32")) == int(undef_int):
        lines.append(f"{GetCrop_aCoeff():8.1f}       : No impact on HI of restricted vegetative growth during yield formation ")
    else:
        lines.append(f"{GetCrop_aCoeff():8.1f}       : Coefficient describing positive impact on HI of restricted vegetative growth during yield formation")
    if int(roundc(GetCrop_bCoeff(), mold="int32")) == int(undef_int):
        lines.append(f"{GetCrop_bCoeff():8.1f}       : No effect on HI of stomatal closure during yield formation")
    else:
        lines.append(f"{GetCrop_bCoeff():8.1f}       : Coefficient describing negative impact on HI of stomatal closure during yield formation")
    lines.append(f"{GetCrop_DHImax():6d}         : Allowable maximum increase (%) of specified HI")

    # growing degree days
    if GetCrop_Planting() == plant_Seed:
        lines.append(f"{GetCrop_GDDaysToGermination():6d}         : GDDays: from sowing to emergence")
        lines.append(f"{GetCrop_GDDaysToMaxRooting():6d}         : GDDays: from sowing to maximum rooting depth")
        lines.append(f"{GetCrop_GDDaysToSenescence():6d}         : GDDays: from sowing to start senescence")
        lines.append(f"{GetCrop_GDDaysToHarvest():6d}         : GDDays: from sowing to maturity (length of crop cycle)")
        if GetCrop_subkind() == subkind_Tuber:
            lines.append(f"{GetCrop_GDDaysToFlowering():6d}         : GDDays: from sowing to start tuber formation")
        else:
            lines.append(f"{GetCrop_GDDaysToFlowering():6d}         : GDDays: from sowing to flowering")
    else:
        if GetCrop_Planting() == plant_transplant:
            lines.append(f"{GetCrop_GDDaysToGermination():6d}         : GDDays: from transplanting to recovered transplant")
            lines.append(f"{GetCrop_GDDaysToMaxRooting():6d}         : GDDays: from transplanting to maximum rooting depth")
            lines.append(f"{GetCrop_GDDaysToSenescence():6d}         : GDDays: from transplanting to start senescence")
            lines.append(f"{GetCrop_GDDaysToHarvest():6d}         : GDDays: from transplanting to maturity")
            if GetCrop_subkind() == subkind_Tuber:
                lines.append(f"{GetCrop_GDDaysToFlowering():6d}         : GDDays: from transplanting to start yield formation")
            else:
                lines.append(f"{GetCrop_GDDaysToFlowering():6d}         : GDDays: from transplanting to flowering")
        else:
            # Crop.Planting = regrowth
            lines.append(f"{GetCrop_GDDaysToGermination():6d}         : GDDays: from regrowth to recovering")
            lines.append(f"{GetCrop_GDDaysToMaxRooting():6d}         : GDDays: from regrowth to maximum rooting depth")
            lines.append(f"{GetCrop_GDDaysToSenescence():6d}         : GDDays: from regrowth to start senescence")
            lines.append(f"{GetCrop_GDDaysToHarvest():6d}         : GDDays: from regrowth to maturity")
            if GetCrop_subkind() == subkind_Tuber:
                lines.append(f"{GetCrop_GDDaysToFlowering():6d}         : GDDays: from regrowth to start yield formation")
            else:
                lines.append(f"{GetCrop_GDDaysToFlowering():6d}         : GDDays: from regrowth to flowering")

    lines.append(f"{GetCrop_GDDLengthFlowering():6d}         : Length of the flowering stage (growing degree days)")
    lines.append(f"{GetCrop_GDDCGC():13.6f}  : CGC for GGDays: Increase in canopy cover (in fraction soil cover per growing-degree day)")
    lines.append(f"{GetCrop_GDDCDC():13.6f}  : CDC for GGDays: Decrease in canopy cover (in fraction per growing-degree day)")
    lines.append(f"{GetCrop_GDDaysToHIo():6d}         : GDDays: building-up of Harvest Index during yield formation")

    # added to 6.2
    lines.append(f"{GetCrop_DryMatter():6d}         : dry matter content (%) of fresh yield")

    # added to 7.0 - Perennial crops
    if GetCrop_subkind() == subkind_Forage:
        lines.append(f"{GetCrop_RootMinYear1():9.2f}      : Minimum effective rooting depth (m) in first year (for perennials)")
    else:
        lines.append(f"{GetCrop_RootMinYear1():9.2f}      : Minimum effective rooting depth (m) in first year - required only in case of regrowth")

    if GetCrop_SownYear1():
        i = 1
        if GetCrop_subkind() == subkind_Forage:
            lines.append(f"{i:6d}         : Crop is sown in 1st year (for perennials)")
        else:
            lines.append(f"{i:6d}         : Crop is sown in 1st year - required only in case of regrowth")
    else:
        i = 0
        if GetCrop_subkind() == subkind_Forage:
            lines.append(f"{i:6d}         : Crop is transplanted in 1st year (for perennials)")
        else:
            lines.append(f"{i:6d}         : Crop is transplanted in 1st year - required only in case of regrowth")

    # added to 7.0 - Assimilates
    if not GetCrop_Assimilates_On():
        i = 0
        lines.append(f"{i:6d}         : Transfer of assimilates from above ground parts to root system is NOT considered")
        lines.append(f"{i:6d}         : Number of days at end of season during which assimilates are stored in root system")
        lines.append(f"{i:6d}         : Percentage of assimilates transferred to root system at last day of season")
        lines.append(f"{i:6d}         : Percentage of stored assimilates transferred to above ground parts in next season")
    else:
        i = 1
        lines.append(f"{i:6d}         : Transfer of assimilates from above ground parts to root system is considered")
        lines.append(f"{GetCrop_Assimilates_Period():6d}         : Number of days at end of season during which assimilates are stored in root system")
        lines.append(f"{GetCrop_Assimilates_Stored():6d}         : Percentage of assimilates transferred to root system at last day of season")
        lines.append(f"{GetCrop_Assimilates_Mobilized():6d}         : Percentage of stored assimilates transferred to above ground parts in next season")

    text = "\n".join(lines) + "\n"
    with open(complete_path_dir + totalname.strip(), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

    # maximum rooting depth in given soil profile
    SetSoil_RootMax(
        RootMaxInSoilProfile(GetCrop_RootMax(), GetSoil_NrSoilLayers(), GetSoilLayer())
    )

    # copy to CropFileSet
    SetCropFileSet_DaysFromSenescenceToEnd(
        GetCrop_DaysToHarvest() - GetCrop_DaysToSenescence()
    )
    SetCropFileSet_DaysToHarvest(GetCrop_DaysToHarvest())

    if GetCrop_ModeCycle() == ModeCycle_GDDays:
        SetCropFileSet_GDDaysFromSenescenceToEnd(
            GetCrop_GDDaysToHarvest() - GetCrop_GDDaysToSenescence()
        )
        SetCropFileSet_GDDaysToHarvest(GetCrop_GDDaysToHarvest())
    else:
        SetCropFileSet_GDDaysFromSenescenceToEnd(undef_int)
        SetCropFileSet_GDDaysToHarvest(undef_int)























































def SetSimulation_SurfaceStorageIni(SurfaceStorageIni):
    # Setter for the "SurfaceStorageIni" attribute of the "simulation" global variable.
    global simulation
    simulation.SurfaceStorageIni = SurfaceStorageIni

def GetSimulation_SurfaceStorageIni():
    # Getter for the "SurfaceStorageIni" attribute of the "simulation" global variable.
    return simulation.SurfaceStorageIni

def SetSimulation_ECStorageIni(ECStorageIni):
    # Setter for the "ECStorageIni" attribute of the "simulation" global variable.
    global simulation
    simulation.ECStorageIni = ECStorageIni

def GetSimulation_ECStorageIni():
    # Getter for the "ECStorageIni" attribute of the "simulation" global variable.
    return simulation.ECStorageIni

def SetSimulation_IniSWC_AtFC(AtFC):
    # Setter for the "AtFC" attribute of the "IniSWC" attribute of the "simulation" global variable.
    global simulation
    simulation.IniSWC.AtFC = AtFC

def SetSimulation_YearSeason(YearSeason):
    # Setter for the "YearSeason" attribute of the "simulation" global variable.
    global simulation
    simulation.YearSeason = YearSeason

def GetSimulation_RCadj():
    # Getter for the "RCadj" attribute of the "simulation" global variable.
    return simulation.RCadj

def SetSimulation_RCadj(RCadj):
    # Setter for the "RCadj" attribute of the "simulation" global variable.
    global simulation
    simulation.RCadj = RCadj

def GetSimulation_YearSeason():
    # Getter for the "YearSeason" attribute of the "simulation" global variable.
    return simulation.YearSeason

def GetSimulation_EffectStress_RedCGC():
    # Getter for the "RedCGC" attribute of the "EffectStress" attribute of the "simulation" global variable.
    return simulation.EffectStress.RedCGC

def SetSimulation_EffectStress_RedCGC(RedCGC):
    # Setter for the "RedCGC" attribute of the "EffectStress" attribute of the "simulation" global variable.
    global simulation
    simulation.EffectStress.RedCGC = RedCGC

def GetSimulation_EffectStress_RedCCX():
    # Getter for the "RedCCX" attribute of the "EffectStress" attribute of the "simulation" global variable.
    return simulation.EffectStress.RedCCX

def SetSimulation_EffectStress_RedCCX(RedCCX):
    # Setter for the "RedCCX" attribute of the "EffectStress" attribute of the "simulation" global variable.
    global simulation
    simulation.EffectStress.RedCCX = RedCCX

def GetSimulation_EffectStress_RedWP():
    # Getter for the "RedWP" attribute of the "EffectStress" attribute of the "simulation" global variable.
    return simulation.EffectStress.RedWP

def SetSimulation_EffectStress_RedWP(RedWP):
    # Setter for the "RedWP" attribute of the "EffectStress" attribute of the "simulation" global variable.
    global simulation
    simulation.EffectStress.RedWP = RedWP

def GetSimulation_EffectStress_CDecline():
    # Getter for the "CDecline" attribute of the "EffectStress" attribute of the "simulation" global variable.
    return simulation.EffectStress.CDecline

def SetSimulation_EffectStress_CDecline(CDecline):
    # Setter for the "CDecline" attribute of the "EffectStress" attribute of the "simulation" global variable.
    global simulation
    simulation.EffectStress.CDecline = CDecline

def GetSimulation_EffectStress_RedKsSto():
    # Getter for the "RedKsSto" attribute of the "EffectStress" attribute of the "simulation" global variable.
    return simulation.EffectStress.RedKsSto

def SetSimulation_EffectStress_RedKsSto(RedKsSto):
    # Setter for the "RedKsSto" attribute of the "EffectStress" attribute of the "simulation" global variable.
    global simulation
    simulation.EffectStress.RedKsSto = RedKsSto

def GetSimulation_EffectStress():
    # Getter for the "EffectStress" attribute of the "simulation" global variable.
    return simulation.EffectStress

def SetSimulation_EvapLimitON(EvapLimitON):
    # Setter for the "Simulation" global variable.
    global simulation
    simulation.EvapLimitON = EvapLimitON

def GetSimulation_EvapLimitON():
    # Getter for the "EvapLimitON" attribute of the "simulation" global variable.
    return simulation.EvapLimitON

def SetSimulation_EffectStress(EffectStress):
    # Setter for the "EffectStress" attribute of the "simulation" global variable.
    global simulation
    simulation.EffectStress = EffectStress

def SetSimulation_LinkCropToSimPeriod(LinkCropToSimPeriod):
    # Setter for the "LinkCropToSimPeriod" attribute of the global "simulation" variable.
    global simulation
    simulation.LinkCropToSimPeriod = LinkCropToSimPeriod

def GetSimulation_LinkCropToSimPeriod():
    # Getter for the "LinkCropToSimPeriod" attribute of the global "simulation" variable.
    return simulation.LinkCropToSimPeriod

def GetSimulation_IniSWC_AtFC():
    # Getter for the "AtFC" attribute of the "IniSWC" attribute of the "simulation" global variable.
    return simulation.IniSWC.AtFC

def GetSimulation_IniSWC_NrLoc():
    # Getter for the "NrLoc" attribute of the "IniSWC" attribute of the "simulation" global variable.
    return simulation.IniSWC.NrLoc

def GetSimulation_MultipleRun():
    # Getter for the "MultipleRun" attribute of the "simulation" global variable.
    return simulation.MultipleRun

def SetSimulation_MultipleRun(MultipleRun):
    # Setter for the "MultipleRun" attribute of the "simulation" global variable.
    global simulation
    simulation.MultipleRun = MultipleRun

def SetSimulation_NrRuns(NrRuns):
    # Setter for the "NrRuns" attribute of the "simulation" global variable.
    global simulation
    simulation.NrRuns = NrRuns

def GetSimulation_NrRuns():
    # Getter for the "NrRuns" attribute of the "simulation" global variable.
    return simulation.NrRuns

def SetSimulation_MultipleRunWithKeepSWC(MultipleRunWithKeepSWC):
    # Setter for the "MultipleRunWithKeepSWC" attribute of the "simulation" global variable.
    global simulation
    simulation.MultipleRunWithKeepSWC = MultipleRunWithKeepSWC

def GetSimulation_MultipleRunWithKeepSWC():
    # Getter for the "MultipleRunWithKeepSWC" attribute of the "simulation" global variable.
    return simulation.MultipleRunWithKeepSWC

def SetSimulation_MultipleRunConstZrx(MultipleRunConstZrx):
    # Setter for the "MultipleRunConstZrx" attribute of the "simulation" global variable.
    global simulation
    simulation.MultipleRunConstZrx = MultipleRunConstZrx

def GetSimulation_MultipleRunConstZrx():
    # Getter for the "MultipleRunConstZrx" attribute of the "simulation" global variable.
    return simulation.MultipleRunConstZrx

def GetSimulation_EvapWCsurf():
    # Getter for the "EvapWCsurf" attribute of the global "simulation" variable.
    return simulation.EvapWCsurf

def SetSimulation_EvapWCsurf(EvapWCsurf):
    # Setter for the "EvapWCsurf" attribute of the global "simulation" variable.
    global simulation
    simulation.EvapWCsurf = EvapWCsurf

def GetSimulation_EvapStartStg2():
    # Getter for the "EvapStartStg2" attribute of the global "simulation" variable.
    return simulation.EvapStartStg2

def SetSimulation_EvapStartStg2(EvapStartStg2):
    # Setter for the "EvapStartStg2" attribute of the global "simulation" variable.
    global simulation
    simulation.EvapStartStg2 = EvapStartStg2

def GetSimulation_EvapZ():
    # Getter for the "EvapZ" attribute of the global "simulation" variable.
    return simulation.EvapZ

def SetSimulation_EvapZ(EvapZ):
    # Setter for the "EvapZ" attribute of the global "simulation" variable.
    global simulation
    simulation.EvapZ = EvapZ

def GetSimulation_HIfinal():
    # Getter for the "HIfinal" attribute of the global "simulation" variable.
    return simulation.HIfinal

def SetSimulation_HIfinal(HIfinal):
    # Setter for the "HIfinal" attribute of the global "simulation" variable.
    global simulation
    simulation.HIfinal = HIfinal

def GetSimulation_DelayedDays():
    # Getter for the "DelayedDays" attribute of the global "simulation" variable.
    return simulation.DelayedDays

def SetSimulation_DelayedDays(DelayedDays):
    # Setter for the "DelayedDays" attribute of the global "simulation" variable.
    global simulation
    simulation.DelayedDays = DelayedDays

def GetSimulation_Germinate():
    # Getter for the "Germinate" attribute of the global "simulation" variable.
    return simulation.Germinate

def SetSimulation_Germinate(Germinate):
    # Setter for the "Germinate" attribute of the global "simulation" variable.
    global simulation
    simulation.Germinate = Germinate

def GetSimulation_SumEToStress():
    # Getter for the "SumEToStress" attribute of the global "simulation" variable.
    return simulation.SumEToStress

def SetSimulation_SumEToStress(SumEToStress):
    # Setter for the "SumEToStress" attribute of the global "simulation" variable.
    global simulation
    simulation.SumEToStress = SumEToStress

def GetSimulation_SumGDD():
    # Getter for the "SumGDD" attribute of the global "simulation" variable.
    return simulation.SumGDD

def SetSimulation_SumGDD(SumGDD):
    # Setter for the "SumGDD" attribute of the global "simulation" variable.
    global simulation
    simulation.SumGDD = SumGDD

def GetSimulation_SumGDDfromDay1():
    # Getter for the "SumGDDfromDay1" attribute of the global "simulation" variable.
    return simulation.SumGDDfromDay1

def SetSimulation_SumGDDfromDay1(SumGDDfromDay1):
    # Setter for the "SumGDDfromDay1" attribute of the global "simulation" variable.
    global simulation
    simulation.SumGDDfromDay1 = SumGDDfromDay1

def GetSimulation_SCor():
    # Getter for the "SCor" attribute of the global "simulation" variable.
    return simulation.SCor

def SetSimulation_SCor(SCor):
    # Setter for the "SCor" attribute of the global "simulation" variable.
    global simulation
    simulation.SCor = _f32(SCor)

def GetSimulation_CropDay1Previous():
    # Getter for the "CropDay1Previous" attribute of the global "simulation" variable.
    return simulation.CropDay1Previous

def SetSimulation_CropDay1Previous(CropDay1Previous):
    # Setter for the "CropDay1Previous" attribute of the global "simulation" variable.
    global simulation
    simulation.CropDay1Previous = CropDay1Previous

def GetSimulation_SalinityConsidered():
    # Getter for the "SalinityConsidered" attribute of the global "simulation" variable.
    return simulation.SalinityConsidered

def SetSimulation_SalinityConsidered(SalinityConsidered):
    # Setter for the "SalinityConsidered" attribute of the global "simulation" variable.
    global simulation
    simulation.SalinityConsidered = SalinityConsidered

def GetSimulation_ProtectedSeedling():
    # Getter for the "ProtectedSeedling" attribute of the global "simulation" variable.
    return simulation.ProtectedSeedling

def SetSimulation_ProtectedSeedling(ProtectedSeedling):
    # Setter for the "ProtectedSeedling" attribute of the global "simulation" variable.
    global simulation
    simulation.ProtectedSeedling = ProtectedSeedling

def GetSimulation_SWCtopSoilConsidered():
    # Getter for the "SWCtopSoilConsidered" attribute of the global "simulation" variable.
    return simulation.SWCtopSoilConsidered

def SetSimulation_SWCtopSoilConsidered(SWCtopSoilConsidered):
    # Setter for the "SWCtopSoilConsidered" attribute of the global "simulation" variable.
    global simulation
    simulation.SWCtopSoilConsidered = SWCtopSoilConsidered

def GetCCxWitheredTpotNoS():
    # Getter for the "CCxWitheredTpotNoS" global variable.
    return CCxWitheredTpotNoS

def SetCCxWitheredTpotNoS(CCxWitheredTpotNoS_in):
    # Setter for the "CCxWitheredTpotNoS" global variable.
    global CCxWitheredTpotNoS
    CCxWitheredTpotNoS = CCxWitheredTpotNoS_in

def GetTotalWaterContent():
    # Getter for the "TotalWaterContent" global variable.
    return TotalWaterContent

def GetSimulation_YearStartCropCycle():
    # Getter for the "YearStartCropCycle" attribute of the "simulation" global variable.
    return simulation.YearStartCropCycle

def SetSimulation_YearStartCropCycle(YearStartCropCycle):
    # Setter for the "YearStartCropCycle" attribute of the "simulation" global variable.
    global simulation
    simulation.YearStartCropCycle = YearStartCropCycle

def SetSimulation_InitialStep(InitialStep):
    # Setter for the "InitialStep" attribute of the "simulation" global variable.
    global simulation
    simulation.InitialStep = InitialStep

def GetSimulation_InitialStep():
    # Getter for the "InitialStep" attribute of the "simulation" global variable.
    return simulation.InitialStep

def SetSimulation_LengthCuttingInterval(LengthCuttingInterval):
    # Setter for the "LengthCuttingInterval" attribute of the "simulation" global variable.
    global simulation
    simulation.LengthCuttingInterval = LengthCuttingInterval

def GetSimulation_LengthCuttingInterval():
    # Getter for the "LengthCuttingInterval" attribute of the "simulation" global variable.
    return simulation.LengthCuttingInterval

def GetSimulation_IniSWC_AtDepths():
    # Getter for the "AtDepths" attribute of the "IniSWC" attribute of the "simulation" global variable.
    return simulation.IniSWC.AtDepths

def GetSimulation_IniSWC_Loc():
    # Getter for the "Loc" attribute of the "IniSWC" attribute of the "simulation" global variable.
    return simulation.IniSWC.Loc

def GetSimulation_IniSWC_VolProc():
    # Getter for the "VolProc" attribute of the "IniSWC" attribute of the "simulation" global variable.
    return simulation.IniSWC.VolProc

def GetSimulation_IniSWC_SaltECe():
    # Getter for the "SaltECe" attribute of the "IniSWC" attribute of the "simulation" global variable.
    return simulation.IniSWC.SaltECe



def SetTotalWaterContent_BeginDay(BeginDay):
    # Setter for the "TotalWaterContent" global variable.
    global TotalWaterContent
    TotalWaterContent.BeginDay = BeginDay

def GetTotalWaterContent_BeginDay():
    # Getter for the "BeginDay" attribute of the "TotalWaterContent" global variable.
    return TotalWaterContent.BeginDay

def GetTotalWaterContent_EndDay():
    # Getter for the "EndDay" attribute of the "TotalWaterContent" global variable.
    return TotalWaterContent.EndDay

def SetTotalWaterContent_EndDay(EndDay):
    # Setter for the "TotalWaterContent" global variable.
    global TotalWaterContent
    TotalWaterContent.EndDay = EndDay

def GetTotalWaterContent_ErrorDay():
    # Getter for the "ErrorDay" attribute of the "TotalWaterContent" global variable.
    return TotalWaterContent.ErrorDay

def SetTotalWaterContent_ErrorDay(ErrorDay):
    # Setter for the "TotalWaterContent" global variable.
    global TotalWaterContent
    TotalWaterContent.ErrorDay = ErrorDay

def GetCalendarFile():
    # Getter for the "CalendarFile" global variable.
    return CalendarFile

def GetOnset():
    # Getter for the "onset" global variable.
    return onset

def SetOnset(Onset_in):
    # Setter for the "onset" global variable.
    global onset
    onset = Onset_in

def SetOnset_GenerateOn(GenerateOn):
    # Setter for the "GenerateOn" attribute of the "onset" global variable.
    global onset
    onset.GenerateOn = GenerateOn

def GetOnset_GenerateOn():
    # Getter for the "GenerateOn" attribute of the "onset" global variable.
    return onset.GenerateOn

def SetOnset_GenerateTempOn(GenerateTempOn):
    # Setter for the "GenerateTempOn" attribute of the "onset" global variable.
    global onset
    onset.GenerateTempOn = GenerateTempOn

def GetOnset_GenerateTempOn():
    # Getter for the "GenerateTempOn" attribute of the "onset" global variable.
    return onset.GenerateTempOn

def GetOnset_Criterion():
    # Getter for the "Criterion" attribute of the "onset" global variable.
    return onset.Criterion

def SetOnset_Criterion(Criterion):
    # Setter for the "Criterion" attribute of the "onset" global variable.
    global onset
    onset.Criterion = Criterion

def GetOnset_AirTCriterion():
    # Getter for the "AirTCriterion" attribute of the "onset" global variable
    return onset.AirTCriterion

def SetOnset_AirTCriterion(AirTCriterion):
    # Setter for the "AirTCriterion" attribute of the "onset" global variable.
    global onset
    onset.AirTCriterion = AirTCriterion

def SetOnset_StartSearchDayNr(StartSearchDayNr):
    # Setter for the "StartSearchDayNr" attribute of the "onset" global variable.
    global onset
    onset.StartSearchDayNr = StartSearchDayNr

def SetOnset_StopSearchDayNr(StopSearchDayNr):
    # Setter for the "StopSearchDayNr" attribute of the "onset" global variable.
    global onset
    onset.StopSearchDayNr = StopSearchDayNr

def GetOnset_StartSearchDayNr():
    # Getter for the "StartSearchDayNr" attribute of the "onset" global variable.
    return onset.StartSearchDayNr

def GetOnset_LengthSearchPeriod():
    # Getter for the "LengthSearchPeriod" attribute of the "onset" global variable.
    return onset.LengthSearchPeriod

def GetOnset_StopSearchDayNr():
    # Getter for the "StopSearchDayNr" attribute of the "onset" global variable.
    return onset.StopSearchDayNr

def SetOnset_LengthSearchPeriod(LengthSearchPeriod):
    # Setter for the "LengthSearchPeriod" attribute of the "onset" global variable.
    global onset
    onset.LengthSearchPeriod = LengthSearchPeriod

def GetEndSeason():
    # Getter for the "endseason" global variable.
    return endseason

def SetEndSeason(EndSeason_in):
    # Setter for the "endseason" global variable.
    global endseason
    endseason = EndSeason_in

def GetEndSeason_GenerateTempOn():
    # Getter for the "GenerateTempOn" attribute of the "endseason" global variable.
    return endseason.GenerateTempOn

def SetEndSeason_GenerateTempOn(GenerateTempOn):
    # Setter for the "GenerateTempOn" attribute of the "endseason" global variable.
    global endseason
    endseason.GenerateTempOn = GenerateTempOn

def GetEndSeason_ExtraYears():
    # Getter for the "ExtraYears" attribute of the "endseason" global variable.
    return endseason.ExtraYears

def SetEndSeason_ExtraYears(ExtraYears):
    # Setter for the "ExtraYears" attribute of the "endseason" global variable.
    global endseason
    endseason.ExtraYears = ExtraYears

def GetEndSeason_AirTCriterion():
    # Getter for the "AirTCriterion" attribute of the "endseason" global variable.
    return endseason.AirTCriterion

def SetEndSeason_AirTCriterion(AirTCriterion_in):
    # Setter for the "AirTCriterion" attribute of the "endseason" global variable.
    global endseason
    endseason.AirTCriterion = AirTCriterion_in

def GetEndSeason_StartSearchDayNr():
    # Getter for the "StartSearchDayNr" attribute of the "endseason" global variable.
    return endseason.StartSearchDayNr

def SetEndSeason_StartSearchDayNr(StartSearchDayNr_in):
    # Setter for the "StartSearchDayNr" attribute of the "endseason" global variable.
    global endseason
    endseason.StartSearchDayNr = StartSearchDayNr_in

def GetEndSeason_StopSearchDayNr():
    # Getter for the "StopSearchDayNr" attribute of the "endseason" global variable.
    return endseason.StopSearchDayNr

def SetEndSeason_StopSearchDayNr(StopSearchDayNr_in):
    # Setter for the "StopSearchDayNr" attribute of the "endseason" global variable.
    global endseason
    endseason.StopSearchDayNr = StopSearchDayNr_in

def GetEndSeason_LengthSearchPeriod():
    # Getter for the "LengthSearchPeriod" attribute of the "endseason" global variable.
    return endseason.LengthSearchPeriod

def SetEndSeason_LengthSearchPeriod(LengthSearchPeriod_in):
    # Setter for the "LengthSearchPeriod" attribute of the "endseason" global variable.
    global endseason
    endseason.LengthSearchPeriod = LengthSearchPeriod_in

def SetIrriBeforeSeason_DayNr(i, DayNr):
    # Setter for the "DayNr" attribute of the "IrriBeforeSeason" global variable.
    global IrriBeforeSeason
    i0 = i - 1 
    IrriBeforeSeason[i0].DayNr = DayNr

def SetIrriBeforeSeason_Param(i, Param):
    # Setter for the "param" attribute of the "IrriBeforeSeason" global variable.
    global IrriBeforeSeason
    i0 = i - 1
    IrriBeforeSeason[i0].param = Param

def GetIrriAfterSeason():
    # Getter for the "IrriAfterSeason" global variable.
    return IrriAfterSeason

def SetIrriAfterSeason(IrriAfterSeason_in):
    # Setter for the "IrriAfterSeason" global variable.
    global IrriAfterSeason
    IrriAfterSeason = IrriAfterSeason_in

def SetIrriAfterSeason_DayNr(i, DayNr):
    # Setter for the "DayNr" attribute of the "IrriAfterSeason" global variable.
    global IrriAfterSeason
    i0 = i - 1
    IrriAfterSeason[i0].DayNr = DayNr

def SetIrriAfterSeason_Param(i, Param):
    # Setter for the "param" attribute of the "IrriAfterSeason" global variable.
    global IrriAfterSeason
    i0 = i - 1
    IrriAfterSeason[i0].param = Param

def GetIrriBeforeSeason():
    # Getter for the "IrriBeforeSeason" global variable.
    return IrriBeforeSeason

def SetIrriBeforeSeason(IrriBeforeSeason_in):
    # Setter for the "IrriBeforeSeason" global variable.
    global IrriBeforeSeason
    IrriBeforeSeason = IrriBeforeSeason_in

def GetIrriBeforeSeason_DayNr(i):
    # Getter for the "DayNr" attribute of the "IrriBeforeSeason" global variable.
    i0 = i - 1
    return IrriBeforeSeason[i0].DayNr

def GetIrriBeforeSeason_Param(i):
    # Getter for the "param" attribute of the "IrriBeforeSeason" global variable.
    i0 = i - 1
    return IrriBeforeSeason[i0].param

def GetIrriAfterSeason_i(i):
    # Getter for individual element for the "IrriAfterSeason" global variable.
    i0 = i - 1
    return IrriAfterSeason[i0]

def SetIrriAfterSeason_i(i, IrriAfterSeason_i):
    # Setter for individual element for the "IrriAfterSeason" global variable.
    global IrriAfterSeason
    i0 = i - 1
    IrriAfterSeason[i0] = IrriAfterSeason_i

def GetIrriBeforeSeason_i(i):
    # Getter for individual element for the "IrriBeforeSeason" global variable.
    i0 = i - 1
    return IrriBeforeSeason[i0]

def SetIrriBeforeSeason_i(i, IrriBeforeSeason_i):
    # Setter for individual element for the "IrriBeforeSeason" global variable.
    global IrriBeforeSeason
    i0 = i - 1
    IrriBeforeSeason[i0] = IrriBeforeSeason_i

def GetIrriAfterSeason_DayNr(i):
    # Getter for the "DayNr" attribute of the "IrriAfterSeason" global variable.
    i0 = i - 1
    return IrriAfterSeason[i0].DayNr

def GetIrriAfterSeason_Param(i):
    # Getter for the "param" attribute of the "IrriAfterSeason" global variable.
    i0 = i - 1
    return IrriAfterSeason[i0].param

def GetIrriFirstDayNr():
    # Getter for the "IrriFirstDayNr" global variable.
    return IrriFirstDayNr

def SetIrriFirstDayNr(IrriFirstDayNr_in):
    # Setter for the "IrriFirstDayNr" global variable.
    global IrriFirstDayNr
    IrriFirstDayNr = IrriFirstDayNr_in

def GetIrriECw():
    # Getter for the "IrriECw" global variable.
    return IrriECw

def SetIrriECw(IrriECw_in):
    # Setter for the "IrriECw" global variable.
    global IrriECw
    IrriECw = IrriECw_in

def GetIrriECw_PreSeason():
    # Getter for the "IrriECw" global variable.
    return IrriECw.PreSeason

def SetIrriECw_PreSeason(PreSeason):
    # Setter for the "IrriECw" global variable.
    global IrriECw
    IrriECw.PreSeason = PreSeason

def GetIrriECw_PostSeason():
    # Getter for the "IrriECw" global variable.
    return IrriECw.PostSeason

def SetIrriECw_PostSeason(PostSeason):
    # Setter for the "IrriECw" global variable.
    global IrriECw
    IrriECw.PostSeason = PostSeason


def GetGenerateTimeMode():
    # Getter for the "GenerateTimeMode" global variable.
    return GenerateTimeMode

def GetGenerateDepthMode():
    # Getter for the "GenerateDepthMode" global variable.
    return GenerateDepthMode

def SetTminTnxReference12MonthsRun_i(i, TminTnxReference12MonthsRun_i):
    # Setter for individual element for the "TminTnxReference12MonthsRun" global variable.
    global TminTnxReference12MonthsRun
    i0 = i - 1
    TminTnxReference12MonthsRun[i0] = TminTnxReference12MonthsRun_i

def GetTminTnxReference12MonthsRun():
    # Getter for the "TminTnxReference12MonthsRun" global variable.
    return TminTnxReference12MonthsRun

def SetTminTnxReference12MonthsRun(TminTnxReference12MonthsRun_in):
    # Setter for the "TminTnxReference12MonthsRun" global variable.
    global TminTnxReference12MonthsRun
    TminTnxReference12MonthsRun = TminTnxReference12MonthsRun_in

def GetTminTnxReference12MonthsRun_i(i):
    # Getter for individual element for the "TminTnxReference12MonthsRun" global variable.
    global TminTnxReference12MonthsRun
    i0 = i - 1
    return TminTnxReference12MonthsRun[i0]

def SetTmaxTnxReference12MonthsRun_i(i, TmaxTnxReference12MonthsRun_i):
    # Setter for individual element for the "TmaxTnxReference12MonthsRun" global variable.
    global TmaxTnxReference12MonthsRun
    i0 = i - 1
    TmaxTnxReference12MonthsRun[i0] = TmaxTnxReference12MonthsRun_i

def GetTmaxTnxReference12MonthsRun():
    # Getter for the "TmaxTnxReference12MonthsRun" global variable.
    return TmaxTnxReference12MonthsRun

def SetTmaxTnxReference12MonthsRun(TmaxTnxReference12MonthsRun_in):
    # Setter for the "TmaxTnxReference12MonthsRun" global variable.
    global TmaxTnxReference12MonthsRun
    TmaxTnxReference12MonthsRun = TmaxTnxReference12MonthsRun_in

def GetTmaxTnxReference12MonthsRun_i(i):
    # Getter for individual element for the "TmaxTnxReference12MonthsRun" global variable.
    global TmaxTnxReference12MonthsRun
    i0 = i - 1
    return TmaxTnxReference12MonthsRun[i0]

def GetSurf0():
    # Getter for the "Surf0" global variable.
    return Surf0

def SetSurf0(Surf0_in):
    # Setter for the "Surf0" global variable.
    global Surf0
    Surf0 = Surf0_in

def GetPerennialPeriod():
    # Getter for the "PerennialPeriod" global variable.
    return perennialperiod

def SetPerennialPeriod(PerennialPeriod_in):
    # Setter for the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod = PerennialPeriod_in

def GetPerennialPeriod_GenerateOnset():
    # Getter for the "GenerateOnset" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.GenerateOnset

def SetPerennialPeriod_GenerateOnset(GenerateOnset):
    # Setter for the "GenerateOnset" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.GenerateOnset = GenerateOnset

def GetPerennialPeriod_OnsetCriterion():
    # Getter for the "OnsetCriterion" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.OnsetCriterion

def SetPerennialPeriod_OnsetCriterion(OnsetCriterion):
    # Setter for the "OnsetCriterion" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.OnsetCriterion = OnsetCriterion

def GetPerennialPeriod_OnsetFirstDay():
    # Getter for the "OnsetFirstDay" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.OnsetFirstDay

def SetPerennialPeriod_OnsetFirstDay(OnsetFirstDay):
    # Setter for the "OnsetFirstDay" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.OnsetFirstDay = OnsetFirstDay

def GetPerennialPeriod_OnsetFirstMonth():
    # Getter for the "OnsetFirstMonth" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.OnsetFirstMonth

def SetPerennialPeriod_OnsetFirstMonth(OnsetFirstMonth):
    # Setter for the "OnsetFirstMonth" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.OnsetFirstMonth = OnsetFirstMonth

def GetPerennialPeriod_OnsetLengthSearchPeriod():
    # Getter for the "OnsetLengthSearchPeriod" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.OnsetLengthSearchPeriod

def SetPerennialPeriod_OnsetLengthSearchPeriod(OnsetLengthSearchPeriod):
    # Setter for the "OnsetLengthSearchPeriod" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.OnsetLengthSearchPeriod = OnsetLengthSearchPeriod

def GetPerennialPeriod_OnsetThresholdValue():
    # Getter for the "OnsetThresholdValue" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.OnsetThresholdValue

def SetPerennialPeriod_OnsetThresholdValue(OnsetThresholdValue):
    # Setter for the "OnsetThresholdValue" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.OnsetThresholdValue = OnsetThresholdValue

def GetPerennialPeriod_OnsetPeriodValue():
    # Getter for the "OnsetPeriodValue" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.OnsetPeriodValue

def SetPerennialPeriod_OnsetPeriodValue(OnsetPeriodValue):
    # Setter for the "OnsetPeriodValue" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.OnsetPeriodValue = OnsetPeriodValue

def GetPerennialPeriod_OnsetOccurrence():
    # Getter for the "OnsetOccurrence" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.OnsetOccurrence

def SetPerennialPeriod_OnsetOccurrence(OnsetOccurrence):
    # Setter for the "OnsetOccurrence" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.OnsetOccurrence = OnsetOccurrence

def GetPerennialPeriod_GenerateEnd():
    # Getter for the "GenerateEnd" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.GenerateEnd

def SetPerennialPeriod_GenerateEnd(GenerateEnd):
    # Setter for the "GenerateEnd" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.GenerateEnd = GenerateEnd

def GetPerennialPeriod_EndCriterion():
    # Getter for the "EndCriterion" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.EndCriterion

def SetPerennialPeriod_EndCriterion(EndCriterion):
    # Setter for the "EndCriterion" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.EndCriterion = EndCriterion

def GetPerennialPeriod_EndLastDay():
    # Getter for the "EndLastDay" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.EndLastDay

def SetPerennialPeriod_EndLastDay(EndLastDay):
    # Setter for the "EndLastDay" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.EndLastDay = EndLastDay

def GetPerennialPeriod_EndLastMonth():
    # Getter for the "EndLastMonth" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.EndLastMonth

def SetPerennialPeriod_EndLastMonth(EndLastMonth):
    # Setter for the "EndLastMonth" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.EndLastMonth = EndLastMonth

def GetPerennialPeriod_ExtraYears():
    # Getter for the "ExtraYears" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.ExtraYears

def SetPerennialPeriod_ExtraYears(ExtraYears):
    # Setter for the "ExtraYears" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.ExtraYears = ExtraYears    

def GetPerennialPeriod_EndLengthSearchPeriod():
    # Getter for the "EndLengthSearchPeriod" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.EndLengthSearchPeriod

def SetPerennialPeriod_EndLengthSearchPeriod(EndLengthSearchPeriod):
    # Setter for the "EndLengthSearchPeriod" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.EndLengthSearchPeriod = EndLengthSearchPeriod

def GetPerennialPeriod_EndThresholdValue():
    # Getter for the "EndThresholdValue" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.EndThresholdValue

def SetPerennialPeriod_EndThresholdValue(EndThresholdValue):
    # Setter for the "EndThresholdValue" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.EndThresholdValue = EndThresholdValue

def GetPerennialPeriod_EndPeriodValue():
    # Getter for the "EndPeriodValue" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.EndPeriodValue

def SetPerennialPeriod_EndPeriodValue(EndPeriodValue):
    # Setter for the "EndPeriodValue" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.EndPeriodValue = EndPeriodValue

def GetPerennialPeriod_EndOccurrence():
    # Getter for the "EndOccurrence" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.EndOccurrence

def SetPerennialPeriod_EndOccurrence(EndOccurrence):
    # Setter for the "EndOccurrence" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.EndOccurrence = EndOccurrence

def GetPerennialPeriod_OnsetStartSearchDayNr():
    # Getter for the "OnsetStartSearchDayNr" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.OnsetStartSearchDayNr

def SetPerennialPeriod_OnsetStopSearchDayNr(OnsetStopSearchDayNr):
    # Setter for the "OnsetStopSearchDayNr" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.OnsetStopSearchDayNr = OnsetStopSearchDayNr

def SetPerennialPeriod_OnsetStartSearchDayNr(OnsetStartSearchDayNr):
    # Setter for the "OnsetStartSearchDayNr" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.OnsetStartSearchDayNr = OnsetStartSearchDayNr

def GetPerennialPeriod_EndStartSearchDayNr():
    # Getter for the "EndStartSearchDayNr" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.EndStartSearchDayNr

def SetPerennialPeriod_EndStartSearchDayNr(EndStartSearchDayNr):
    # Setter for the "EndStartSearchDayNr" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.EndStartSearchDayNr = EndStartSearchDayNr

def GetPerennialPeriod_EndStopSearchDayNr():
    # Getter for the "EndStopSearchDayNr" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.EndStopSearchDayNr

def SetPerennialPeriod_EndStopSearchDayNr(EndStopSearchDayNr):
    # Setter for the "EndStopSearchDayNr" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.EndStopSearchDayNr = EndStopSearchDayNr

def SetPerennialPeriod_GeneratedDayNrOnset(GeneratedDayNrOnset):
    # Setter for the "GeneratedDayNrOnset" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.GeneratedDayNrOnset = GeneratedDayNrOnset

def GetPerennialPeriod_GeneratedDayNrOnset():
    # Getter for the "GeneratedDayNrOnset" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.GeneratedDayNrOnset

def SetPerennialPeriod_GeneratedDayNrEnd(GeneratedDayNrEnd):
    # Setter for the "GeneratedDayNrEnd" attribute of the "PerennialPeriod" global variable.
    global perennialperiod
    perennialperiod.GeneratedDayNrEnd = GeneratedDayNrEnd

def GetPerennialPeriod_GeneratedDayNrEnd():
    # Getter for the "GeneratedDayNrEnd" attribute of the "PerennialPeriod" global variable.
    return perennialperiod.GeneratedDayNrEnd

def GetTminRun():
    # Getter for the "TminRun" global variable.
    return TminRun

def SetTminRun(TminRun_in):
    # Setter for the "TminRun" global variable.
    global TminRun
    TminRun = TminRun_in

def SetTminRun_i(i, TminRun_i):
    # Setter for individual element for the "TminRun" global variable.
    global TminRun
    i0 = i - 1
    TminRun[i0] = TminRun_i

def GetTminRun_i(i):
    # Getter for individual element for the "TminRun" global variable.
    i0 = i - 1
    return TminRun[i0]

def GetTmaxRun():
    # Getter for the "TmaxRun" global variable.
    return TmaxRun

def SetTmaxRun(TmaxRun_in):
    # Setter for the "TmaxRun" global variable.
    global TmaxRun
    TmaxRun = TmaxRun_in

def SetTmaxRun_i(i, TmaxRun_i):
    # Setter for individual element for the "TmaxRun" global variable.
    global TmaxRun
    i0 = i - 1
    TmaxRun[i0] = TmaxRun_i

def GetTmaxRun_i(i):
    # Getter for individual element for the "TmaxRun" global variable.
    i0 = i - 1
    return TmaxRun[i0]

def GetTminCropReferenceRun():
    # Getter for the "TminCropReferenceRun" global variable.
    return TminCropReferenceRun

def SetTminCropReferenceRun(TminCropReferenceRun_in):
    # Setter for the "TminCropReferenceRun" global variable.
    global TminCropReferenceRun
    TminCropReferenceRun = TminCropReferenceRun_in

def SetTminCropReferenceRun_i(i, TminCropReferenceRun_i):
    # Setter for individual element for the "TminCropReferenceRun" global variable.
    global TminCropReferenceRun
    i0 = i - 1
    TminCropReferenceRun[i0] = TminCropReferenceRun_i

def GetTminCropReferenceRun_i(i):
    # Getter for individual elements of the "TminCropReferenceRun" global variable.
    i0 = i - 1
    return TminCropReferenceRun[i0]

def GetTmaxCropReferenceRun():
    # Getter for the "TmaxCropReferenceRun" global variable.
    return TmaxCropReferenceRun

def SetTmaxCropReferenceRun(TmaxCropReferenceRun_in):
    # Setter for the "TmaxCropReferenceRun" global variable.
    global TmaxCropReferenceRun
    TmaxCropReferenceRun = TmaxCropReferenceRun_in

def SetTmaxCropReferenceRun_i(i, TmaxCropReferenceRun_i):
    # Setter for individual element for the "TmaxCropReferenceRun" global variable.
    global TmaxCropReferenceRun
    i0 = i - 1
    TmaxCropReferenceRun[i0] = TmaxCropReferenceRun_i

def GetTmaxCropReferenceRun_i(i):
    # Getter for individual elements of the "TmaxCropReferenceRun" global variable.
    i0 = i - 1
    return TmaxCropReferenceRun[i0]

def GetCCiPrev():
    # Getter for the "CCiPrev" global variable.
    return CCiPrev

def SetCCiPrev(CCiPrev_in):
    # Setter for the "CCiPrev" global variable.
    global CCiPrev
    CCiPrev = CCiPrev_in

def GetRootingDepth():
    # Getter for the "RootingDepth" global variable.
    return RootingDepth

def SetRootingDepth(RootingDepth_in):
    # Setter for the "RootingDepth" global variable.
    global RootingDepth
    RootingDepth = RootingDepth_in

def GetRootZoneSalt():
    # Getter for the "RootZoneSalt" global variable.
    return RootZoneSalt

def SetRootZoneSalt(RootZoneSalt_in):
    # Setter for the "RootZoneSalt" global variable.
    global RootZoneSalt
    RootZoneSalt = RootZoneSalt_in

def GetRootZoneSalt_ECe():
    # Getter for the "RootZoneSalt" global variable.
    return RootZoneSalt.ECe

def SetRootZoneSalt_ECe(ECe):
    # Setter for the "RootZoneSalt" global variable.
    global RootZoneSalt
    RootZoneSalt.ECe = ECe

def GetRootZoneSalt_ECsw():
    # Getter for the "RootZoneSalt" global variable.
    return RootZoneSalt.ECsw

def SetRootZoneSalt_ECsw(ECsw):
    # Setter for the "RootZoneSalt" global variable.
    global RootZoneSalt
    RootZoneSalt.ECsw = ECsw

def GetRootZoneSalt_ECswFC():
    # Getter for the "RootZoneSalt" global variable.
    return RootZoneSalt.ECswFC

def SetRootZoneSalt_ECswFC(ECswFC):
    # Setter for the "RootZoneSalt" global variable.
    global RootZoneSalt
    RootZoneSalt.ECswFC = ECswFC

def GetRootZoneSalt_KsSalt():
    # Getter for the "RootZoneSalt" global variable.
    return RootZoneSalt.KsSalt

def SetRootZoneSalt_KsSalt(KsSalt):
    # Setter for the "RootZoneSalt" global variable.
    global RootZoneSalt
    RootZoneSalt.KsSalt = KsSalt

def GetTact():
    # Getter for the "Tact" global variable.
    return Tact

def SetTact(Tact_in):
    # Setter for the "Tact" global variable.
    global Tact
    Tact = Tact_in

def GetRootZoneWC():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC

def GetRootZoneWC_Actual():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.Actual

def SetRootZoneWC_Actual(Actual):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.Actual = Actual

def GetRootZoneWC_FC():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.FC

def SetRootZoneWC_FC(FC):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.FC = FC

def GetRootZoneWC_WP():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.WP

def SetRootZoneWC_WP(WP):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.WP = WP

def GetRootZoneWC_SAT():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.SAT

def SetRootZoneWC_SAT(SAT):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.SAT = SAT

def GetRootZoneWC_Leaf():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.Leaf

def SetRootZoneWC_Leaf(Leaf):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.Leaf = Leaf

def GetRootZoneWC_Thresh():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.Thresh

def SetRootZoneWC_Thresh(Thresh):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.Thresh = Thresh

def GetRootZoneWC_Sen():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.Sen

def SetRootZoneWC_Sen(Sen):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.Sen = Sen

def GetRootZoneWC_ZtopAct():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.ZtopAct

def SetRootZoneWC_ZtopAct(ZtopAct):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.ZtopAct = ZtopAct

def GetRootZoneWC_ZtopFC():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.ZtopFC

def SetRootZoneWC_ZtopFC(ZtopFC):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.ZtopFC = ZtopFC

def GetRootZoneWC_ZtopWP():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.ZtopWP

def SetRootZoneWC_ZtopWP(ZtopWP):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.ZtopWP = ZtopWP

def GetRootZoneWC_ZtopThresh():
    # Getter for the "RootZoneWC" global variable.

    return RootZoneWC.ZtopThresh

def SetRootZoneWC_ZtopThresh(ZtopThresh):
    # Setter for the "RootZoneWC" global variable.

    global RootZoneWC
    RootZoneWC.ZtopThresh = ZtopThresh

def GetECDrain():
    # Getter for the "ECDrain" global variable.
    return ECDrain

def SetECDrain(ECDrain_in):
    # Setter for the "ECDrain" global variable.
    global ECDrain
    ECDrain = ECDrain_in

def GetTotalSaltContent():
    # Getter for the "TotalSaltContent" global variable.

    return TotalSaltContent

def SetTotalSaltContent(TotalSaltContent_in):
    # Setter for the "TotalSaltContent" global variable.

    global TotalSaltContent
    TotalSaltContent = TotalSaltContent_in

def GetTotalSaltContent_BeginDay():
    # Getter for the "TotalSaltContent" global variable.

    return TotalSaltContent.BeginDay

def SetTotalSaltContent_BeginDay(BeginDay):
    # Setter for the "TotalSaltContent" global variable.

    global TotalSaltContent
    TotalSaltContent.BeginDay = BeginDay

def GetTotalSaltContent_EndDay():
    # Getter for the "TotalSaltContent" global variable.

    return TotalSaltContent.EndDay

def SetTotalSaltContent_EndDay(EndDay):
    # Setter for the "TotalSaltContent" global variable.

    global TotalSaltContent
    TotalSaltContent.EndDay = EndDay

def GetTotalSaltContent_ErrorDay():
    # Getter for the "TotalSaltContent" global variable.

    return TotalSaltContent.ErrorDay

def SetTotalSaltContent_ErrorDay(ErrorDay):
    # Setter for the "TotalSaltContent" global variable.

    global TotalSaltContent
    TotalSaltContent.ErrorDay = ErrorDay

def GetSaltInfiltr():
    # Getter for the "SaltInfiltr" global variable.
    return SaltInfiltr

def SetSaltInfiltr(SaltInfiltr_in):
    # Setter for the "SaltInfiltr" global variable.
    global SaltInfiltr
    SaltInfiltr = SaltInfiltr_in

def GetTactWeedInfested():
    # Getter for the "TactWeedInfested" global variable.
    return TactWeedInfested

def SetTactWeedInfested(TactWeedInfested_in):
    # Setter for the "TactWeedInfested" global variable.
    global TactWeedInfested
    TactWeedInfested = TactWeedInfested_in

def GetCCiTopEarlySen():
    # Getter for the "CCiTopEarlySen" global variable.
    return CCiTopEarlySen

def SetCCiTopEarlySen(CCiTopEarlySen_in):
    # Setter for the "CCiTopEarlySen" global variable.
    global CCiTopEarlySen
    CCiTopEarlySen = CCiTopEarlySen_in

def SumCalendarDaysReferenceTnx(
    ValGDDays: int,
    RefCropDay1: int,
    StartDayNr: int,
    Tbase: float,
    Tupper: float,
    TDayMin: float,
    TDayMax: float,
) -> int:
    i = 0
    NrCDays = 0
    RemainingGDDays = 0.0
    DayGDD = 0.0
    TDayMin_loc = float(TDayMin)
    TDayMax_loc = float(TDayMax)

    NrCDays = 0
    if ValGDDays > 0:
        if GetTnxReferenceFile() == "(None)":
            # given average Tmin and Tmax
            DayGDD = DegreesDay(
                Tbase,
                Tupper,
                TDayMin_loc,
                TDayMax_loc,
                GetSimulParam_GDDMethod(),
            )
            if abs(DayGDD) < 1e-12:
                NrCDays = 0
            else:
                NrCDays = int(roundc(float(ValGDDays) / DayGDD, mold="int32"))
        else:
            # Get TCropReference: mean daily Tnx (365 days) from RefCropDay1 onwards
            RemainingGDDays = float(ValGDDays)

            # TminCropReference and TmaxCropReference arrays contain the TemperatureFilefull data
            i = int(StartDayNr - RefCropDay1)

            _n = len(GetTminCropReferenceRun())
            if _n == 366:
                _n = 365

            while RemainingGDDays > 0.1:
                i += 1
                if i == _n:
                    i = 1

                TDayMin_loc = float(GetTminCropReferenceRun_i(i))
                TDayMax_loc = float(GetTmaxCropReferenceRun_i(i))

                DayGDD = DegreesDay(
                    Tbase,
                    Tupper,
                    TDayMin_loc,
                    TDayMax_loc,
                    GetSimulParam_GDDMethod(),
                )

                if DayGDD > RemainingGDDays:
                    if int(roundc((DayGDD - RemainingGDDays) / RemainingGDDays, mold="int32")) >= 1:
                        NrCDays += 1
                else:
                    NrCDays += 1

                RemainingGDDays -= DayGDD

    return int(NrCDays)



def NoCropCalendar():
    SetCalendarFile('(None)')
    SetCalendarFileFull(GetCalendarFile())  # no file
    SetCalendarDescription('')
    SetOnset_GenerateOn(False)
    SetOnset_GenerateTempOn(False)
    SetEndSeason_GenerateTempOn(False)
    SetCalendarDescription('No calendar for the Seeding/Planting year')


def Calculate_SaltMobility(layer: int, SaltDiffusion: int, Macro: int, Mobil: list[float]) -> None:
    Mix = SaltDiffusion / 100.0
    UL = GetSoilLayer_UL(layer) * 100.0

    if Macro > UL:
        CelMax = GetSoilLayer_SCP1(layer)
    else:
        CelMax = int(roundc((Macro / UL) * GetSoilLayer_SC(layer), mold="int32"))

    if CelMax <= 0:
        CelMax = 1

    if Mix < 0.5:
        a = Mix * 2.0
        b = math.exp(10.0 * (0.5 - Mix) * math.log(10.0))
    else:
        a = 2.0 * (1.0 - Mix)
        b = math.exp(10.0 * (Mix - 0.5) * math.log(10.0))

    for i in range(1, CelMax):
        xi = i * 1.0 / (CelMax - 1)
        if Mix > 0.0:
            if Mix < 0.5:
                yi = math.exp(math.log(a) + xi * math.log(b))
                Mobil[i-1] = (yi - a) / (a * b - a)
            elif (0.5 - 1e-12) <= Mix <= (0.5 + 1e-12):
                Mobil[i-1] = xi
            elif Mix < 1.0:
                yi = math.exp(math.log(a) + (1.0 - xi) * math.log(b))
                Mobil[i-1] = 1.0 - (yi - a) / (a * b - a)
            else:
                Mobil[i-1] = 1.0
        else:
            Mobil[i-1] = 0.0

    for i in range(CelMax, GetSoilLayer_SCP1(layer) + 1):
        Mobil[i-1] = 1.0

def DetermineNrandThicknessCompartments():
    from . import run
    TotalDepthL = 0.0
    for i in range(1, GetSoil_NrSoilLayers() + 1):
        TotalDepthL = TotalDepthL + GetSoilLayer_Thickness(i)
    TotalDepthC = 0.0
    SetNrCompartments(0)
    while True:
        DeltaZ = (TotalDepthL - TotalDepthC)
        SetNrCompartments(GetNrCompartments() + 1) # call SetNrCompartments(GetNrCompartments() + 1)
        if DeltaZ > GetSimulParam_CompDefThick():
            SetCompartment_Thickness(GetNrCompartments(), GetSimulParam_CompDefThick())
        else:
            SetCompartment_Thickness(GetNrCompartments(), DeltaZ)

        TotalDepthC = TotalDepthC + GetCompartment_Thickness(GetNrCompartments())
        if (GetNrCompartments() == max_No_compartments) or (abs(TotalDepthC - TotalDepthL) < 1e-4):
            break


def TauFromKsat(Ksat: float) -> float:
    if abs(Ksat) < epsilon(1.0):
        return 0.0
    else:
        TauTemp = roundc(100.0 * 0.0866 * math.exp(0.35 * math.log(Ksat)), mold="int32")
        if TauTemp < 0:
            TauTemp = 0
        if TauTemp > 100:
            TauTemp = 100
        return TauTemp / 100.0
    
def _f32(x: float) -> float:
    return c_float(x).value
    
def DesignateSoilLayerToCompartments(NrCompartments, NrSoilLayers, Compartment):

    depth = 0.0
    depthi = 0.0
    layeri = 1
    compi = 1

    while True:
        depth = depth + GetSoilLayer_Thickness(layeri)

        while True:
            half = Compartment[compi - 1].Thickness / 2.0
            depthi = depthi + half

            if depthi <= depth:
                Compartment[compi - 1].Layer = layeri
                NextLayer = False
                depthi = depthi + half
                compi = compi + 1
                finished = (compi > NrCompartments)
            else:
                depthi = depthi - half
                NextLayer = True
                layeri = layeri + 1
                finished = (layeri > NrSoilLayers)

            if finished or NextLayer:
                break

        if finished:
            break

    for i in range(compi, NrCompartments + 1):
        Compartment[i - 1].Layer = NrSoilLayers

    for i in range(NrCompartments + 1, max_No_compartments + 1):
        Compartment[i - 1].Thickness = undef_double

    return Compartment

def specify_soil_layer(NrCompartments, NrSoilLayers, SoilLayer, Compartment, TotalWaterContent):

    Compartment = DesignateSoilLayerToCompartments(NrCompartments, NrSoilLayers, Compartment)

    # Set soil layers and compartments at Field Capacity and determine Watercontent (mm)
    # No salinity in soil layers and compartmens
    # Absence of ground water table (FCadj = FC)
    Total = 0.0
    for layeri in range(1, NrSoilLayers + 1):
        SoilLayer[layeri-1].WaterContent = 0.0

    for compi in range(1, NrCompartments + 1):
        Compartment[compi-1].Theta = SoilLayer[Compartment[compi-1].Layer-1].FC / 100.0
        Compartment[compi-1].FCadj = SoilLayer[Compartment[compi-1].Layer-1].FC
        Compartment[compi-1].DayAnaero = 0

        for celli in range(1, SoilLayer[Compartment[compi-1].Layer-1].SCP1 + 1):
            # salinity in cells
            Compartment[compi-1].Salt[celli-1] = 0.0
            Compartment[compi-1].Depo[celli-1] = 0.0

        SetSimulation_ThetaIni_i(compi, Compartment[compi-1].Theta)
        SetSimulation_ECeIni_i(compi, 0.0)  # initial soil salinity in dS/m

        SoilLayer[Compartment[compi-1].Layer-1].WaterContent = (
            SoilLayer[Compartment[compi-1].Layer-1].WaterContent
            + GetSimulation_ThetaIni_i(compi) * 100.0 * 10.0 * Compartment[compi-1].Thickness
        )

    for layeri in range(1, NrSoilLayers + 1):
        Total = Total + SoilLayer[layeri-1].WaterContent
    SetTotalWaterContent_BeginDay(Total)

    # initial soil water content and no salts
    DeclareInitialCondAtFCandNoSalt()

    # Number of days with RootZone Anaerobic Conditions
    SetSimulation_DayAnaero(0)

    return SoilLayer, Compartment


def ZrAdjustedToRestrictiveLayers(ZrIN, TheNrSoilLayers, TheLayer, ZrOUT):
    ZrOUT = ZrIN

    layi = 1
    Zsoil = TheLayer[layi - 1].Thickness
    ZrAdj = 0.0
    ZrRemain = ZrIN
    DeltaZ = Zsoil
    TheEnd = False

    while not TheEnd:
        ZrTest = ZrAdj + ZrRemain * (TheLayer[layi - 1].Penetrability / 100.0)

        if ((layi == TheNrSoilLayers)
            or (TheLayer[layi - 1].Penetrability == 0)
            or (
                roundc(ZrTest * 10000.0, mold="int32")
                <= roundc(Zsoil * 10000.0, mold="int32")
            )):
            TheEnd = True
            ZrOUT = ZrTest
        else:
            ZrAdj = Zsoil
            ZrRemain = ZrRemain - DeltaZ / (TheLayer[layi - 1].Penetrability / 100.0)
            layi += 1
            Zsoil = Zsoil + TheLayer[layi - 1].Thickness
            DeltaZ = TheLayer[layi - 1].Thickness

    return ZrOUT

def RootMaxInSoilProfile(ZmaxCrop, TheNrSoilLayers, TheSoilLayer):

    Zmax = ZmaxCrop
    Zsoil = 0.0
    layi = 0

    while layi < TheNrSoilLayers and Zmax > 0.0:
        layi += 1

        layer = TheSoilLayer[layi - 1]

        if ((layer.Penetrability < 100)
            and (
                roundc(Zsoil * 1000.0, mold="int32")
                < roundc(ZmaxCrop * 1000.0, mold="int32")
            )):
            Zmax = float(undef_int)

        Zsoil += layer.Thickness

    if Zmax < 0.0:
        Zmax = ZrAdjustedToRestrictiveLayers(ZmaxCrop, TheNrSoilLayers, TheSoilLayer, Zmax)

    return float(Zmax)

def FromGravelMassToGravelVolume(PorosityPercent, GravelMassPercent):
    MineralBD = 2.65
    if GravelMassPercent > 0:
        MatrixBD = MineralBD * (1.0 - PorosityPercent / 100.0)
        SoilBD = 100.0 / (GravelMassPercent / MineralBD + (100.0 - GravelMassPercent) / MatrixBD)
        FromGravelMassToGravelVolume = GravelMassPercent * (SoilBD / MineralBD)
    else:
        FromGravelMassToGravelVolume = 0.0
    return FromGravelMassToGravelVolume

def SaveProfile(totalname: str):

    lines = []

    lines.append(f"{GetProfDescription()}\n")

    lines.append(f"        {GetVersionString()}                 : AquaCrop Version ({GetReleaseDate()})\n")

    lines.append(f"{GetSoil_CNvalue():9d}                   : CN (Curve Number)\n")
    lines.append(f"{GetSoil_REW():9d}                   : Readily evaporable water from top layer (mm)\n")
    lines.append(f"{GetSoil_NrSoilLayers():9d}                   : number of soil horizons\n")
    lines.append(f"{undef_int:9d}                   : variable no longer applicable\n")

    lines.append("  Thickness  Sat   FC    WP     Ksat   Penetrability  Gravel  CRa       CRb           description\n")
    lines.append("  ---(m)-   ----(vol %)-----  (mm/day)      (%)        (%)    -----------------------------------------\n")

    for i in range(1, GetSoil_NrSoilLayers() + 1):
        lines.append(
            f"{GetSoilLayer_Thickness(i):8.2f}"
            f"{GetSoilLayer_SAT(i):8.1f}"
            f"{GetSoilLayer_FC(i):6.1f}"
            f"{GetSoilLayer_WP(i):6.1f}"
            f"{GetSoilLayer_InfRate(i):8.1f}"
            f"{GetSoilLayer_Penetrability(i):11d}"
            f"{GetSoilLayer_GravelMass(i):10d}"
            f"{GetSoilLayer_CRa(i):14.6f}"
            f"{GetSoilLayer_CRb(i):10.6f}"
            f"   {GetSoilLayer_Description(i).strip()}\n"
        )

    with open(complete_path_dir + totalname.strip(), 'w', encoding='utf-8') as f:
        f.write(''.join(lines))

    SetSoil_RootMax(
        RootMaxInSoilProfile(
            GetCrop_RootMax(),
            GetSoil_NrSoilLayers(),
            GetSoilLayer()
        )
    )

def LoadProfile(FullName):
    # Reads in soil data from the given file.
    # Further initializations happen via a call to LoadProfileProcessing().
    full_name_clean = _strip_quotes(FullName).replace("'", "").replace('"', "").strip()

    fhandle = open(
        ResolvePath(full_name_clean),
        "r",
        encoding="utf-8",
    )

    ProfDescriptionLocal = fhandle.readline().strip()
    SetProfDescription(ProfDescriptionLocal)

    line = fhandle.readline().strip()
    VersionNr = float(line.split()[0])  # AquaCrop version

    line = fhandle.readline().strip()
    TempShortInt = int(line.split()[0]) # CN number
    SetSoil_CNvalue(TempShortInt)

    line = fhandle.readline().strip()
    TempShortInt = int(line.split()[0]) # Evaporate water from top layer
    SetSoil_REW(TempShortInt)

    line = fhandle.readline().strip()
    TempShortInt = int(line.split()[0]) # Number of soil horizons
    SetSoil_NrSoilLayers(TempShortInt)

    fhandle.readline() # depth of restrictive soil layer which is no longer applicable
    fhandle.readline()
    fhandle.readline()

    # Load characteristics of each soil layer
    for i in range(1, GetSoil_NrSoilLayers() + 1):
        # Parameters for capillary rise missing in Versions 3.0 and 3.1
        if roundc(VersionNr * 10.0, mold="int32") < 40:
            parts = fhandle.readline().strip().split()
            thickness_temp  = float(parts[0])
            SAT_temp        = float(parts[1])
            FC_temp         = float(parts[2])
            WP_temp         = float(parts[3])
            infrate_temp    = float(parts[4])
            description_temp = parts[6]  

            SetSoilLayer_Thickness(i, thickness_temp)
            SetSoilLayer_SAT(i, SAT_temp)
            SetSoilLayer_FC(i, FC_temp)
            SetSoilLayer_WP(i, WP_temp)
            SetSoilLayer_InfRate(i, infrate_temp)
            SetSoilLayer_Description(i, description_temp)

            # Default values for Penetrability and Gravel
            SetSoilLayer_Penetrability(i, 100)
            SetSoilLayer_GravelMass(i, 0)

            # determine volume gravel
            SetSoilLayer_GravelVol(i, 0.0)
        else:
            if roundc(VersionNr * 10.0, mold="int32") < 60:
                # UPDATE required for Version 6.0
                parts = fhandle.readline().strip().split()
                thickness_temp  = float(parts[0])
                SAT_temp        = float(parts[1])
                FC_temp         = float(parts[2])
                WP_temp         = float(parts[3])
                infrate_temp    = float(parts[4])
                cra_temp        = float(parts[5])
                crb_temp        = float(parts[6])
                description_temp = parts[8]

                SetSoilLayer_Thickness(i, thickness_temp)
                SetSoilLayer_SAT(i, SAT_temp)
                SetSoilLayer_FC(i, FC_temp)
                SetSoilLayer_WP(i, WP_temp)
                SetSoilLayer_InfRate(i, infrate_temp)
                SetSoilLayer_CRa(i, cra_temp)
                SetSoilLayer_CRb(i, crb_temp)
                SetSoilLayer_Description(i, description_temp)

                # Default values for Penetrability and Gravel
                SetSoilLayer_Penetrability(i, 100)
                SetSoilLayer_GravelMass(i, 0)

                # determine volume gravel
                SetSoilLayer_GravelVol(i, 0.0)
            else:
                parts = fhandle.readline().strip().split()
                thickness_temp     = float(parts[0])
                SAT_temp           = float(parts[1])
                FC_temp            = float(parts[2])
                WP_temp            = float(parts[3])
                infrate_temp       = float(parts[4])
                penetrability_temp = int(float(parts[5]))
                gravelm_temp       = int(float(parts[6]))
                cra_temp           = float(parts[7])
                crb_temp           = float(parts[8])
                description_temp    = parts[9]

                SetSoilLayer_Thickness(i, thickness_temp)
                SetSoilLayer_SAT(i, SAT_temp)
                SetSoilLayer_FC(i, FC_temp)
                SetSoilLayer_WP(i, WP_temp)
                SetSoilLayer_InfRate(i, infrate_temp)
                SetSoilLayer_Penetrability(i, penetrability_temp)
                SetSoilLayer_GravelMass(i, gravelm_temp)
                SetSoilLayer_CRa(i, cra_temp)
                SetSoilLayer_CRb(i, crb_temp)
                SetSoilLayer_Description(i, description_temp)

                # determine volume gravel
                SetSoilLayer_GravelVol(i,
                    FromGravelMassToGravelVolume(
                        GetSoilLayer_SAT(i),
                        GetSoilLayer_GravelMass(i)
                    )
                )

    fhandle.close()
    LoadProfileProcessing(VersionNr)

def LoadProfileProcessing(VersionNr):
    # Further initializations after soil profile attributes have been set
    # (e.g. via a call to LoadProfile()).
    # VersionNr - AquaCrop Version (e.g. 7.0)
    SetSimulation_SurfaceStorageIni(0.0)
    SetSimulation_ECStorageIni(0.0)

    for i in range(1, GetSoil_NrSoilLayers() + 1):
        # determine drainage coefficient
        SetSoilLayer_tau(i, TauFromKsat(GetSoilLayer_InfRate(i)))

        # determine number of salt cells based on infiltration rate
        if GetSoilLayer_InfRate(i) <= 112.0:
            SetSoilLayer_SCP1(i, 11)
        else:
            SetSoilLayer_SCP1(i, roundc(1.6 + 1000.0 / GetSoilLayer_InfRate(i), mold="int8"))
            if GetSoilLayer_SCP1(i) < 2:
                SetSoilLayer_SCP1(i, 2)

        # determine parameters for soil salinity
        SetSoilLayer_SC(i, GetSoilLayer_SCP1(i) - 1)
        SetSoilLayer_Macro(i, roundc(GetSoilLayer_FC(i), mold="int8"))
        SetSoilLayer_UL(i, (GetSoilLayer_SAT(i) / 100.0) * (GetSoilLayer_SC(i) / (GetSoilLayer_SC(i) + 2.0))) # ! m3/m3
        dx_temp = GetSoilLayer_UL(i) / GetSoilLayer_SC(i)
        SetSoilLayer_Dx(i, dx_temp) # ! m3/m3

        saltmob_temp = GetSoilLayer_SaltMobility(i)
        Calculate_SaltMobility(i, GetSimulParam_SaltDiff(), GetSoilLayer_Macro(i), saltmob_temp)
        SetSoilLayer_SaltMobility(i, saltmob_temp)

        # determine default parameters for capillary rise if missing
        SetSoilLayer_SoilClass(i, NumberSoilClass(GetSoilLayer_SAT(i),
                                                  GetSoilLayer_FC(i),
                                                  GetSoilLayer_WP(i),
                                                  GetSoilLayer_InfRate(i)))

        if roundc(VersionNr * 10.0, mold="int32") < 40:
            cra_temp = GetSoilLayer_CRa(i)
            crb_temp = GetSoilLayer_CRb(i)
            DetermineParametersCR(GetSoilLayer_SoilClass(i),
                                  GetSoilLayer_InfRate(i),
                                  cra_temp,
                                  crb_temp)
            SetSoilLayer_CRa(i, cra_temp)
            SetSoilLayer_CRb(i, crb_temp)

    DetermineNrandThicknessCompartments()
    SetSoil_RootMax(RootMaxInSoilProfile(GetCrop_RootMax(),
                                         GetSoil_NrSoilLayers(),
                                         GetSoilLayer()))

def DeclareInitialCondAtFCandNoSalt():

    SetSWCIniFile('(None)')
    SetSWCiniFileFull(GetSWCiniFile())  # no file
    SetSWCiniDescription('Soil water profile at Field Capacity')
    SetSimulation_IniSWC_AtDepths(False)
    SetSimulation_IniSWC_NrLoc(GetSoil_NrSoilLayers())
    for layeri in range(1, GetSoil_NrSoilLayers() + 1):
        SetSimulation_IniSWC_Loc_i(layeri, GetSoilLayer_Thickness(layeri))
        SetSimulation_IniSWC_VolProc_i(layeri, GetSoilLayer_FC(layeri))
        SetSimulation_IniSWC_SaltECe_i(layeri, 0.0)
    SetSimulation_IniSWC_AtFC(True)
    for layeri in range(GetSoil_NrSoilLayers() + 1, max_No_compartments + 1):
        SetSimulation_IniSWC_Loc_i(layeri, undef_double)
        SetSimulation_IniSWC_VolProc_i(layeri, undef_double)
        SetSimulation_IniSWC_SaltECe_i(layeri, undef_double)
    for compi in range(1, GetNrCompartments() + 1):
        if GetCompartment_Layer(compi) == 0:
            ind = 1  # LB: added an if statement to avoid having index=0
        else:
            ind = GetCompartment_Layer(compi)
        for celli in range(1, GetSoilLayer_SCP1(ind) + 1):
            # salinity in cells
            SetCompartment_Salt(compi, celli, 0.0)
            SetCompartment_Depo(compi, celli, 0.0)


def LengthCanopyDecline(CCx, CDC):
    ND = 0
    if CCx > 0:
        if CDC <= 2.220446049250313e-16:
            ND = undef_int
        else:
            ND = roundc(
                (((CCx + 2.29) / (CDC * 3.33)) * math.log(1.0 + 1.0 / 0.05) + 0.50),
                mold="int32",
            )  # + 0.50 to guarantee that CC is zero
    return ND

def DetermineLengthGrowthStages(
    CCoVal,
    CCxVal,
    CDCVal,
    L0,
    TotalLength,
    CGCgiven,
    TheDaysToCCini,
    ThePlanting,
    Length123,
    StLength,
    Length12,
    CGCVal,
):
    CCxVal_scaled = 0.0
    CCToReach = 0.0
    L12Adj = 0

    if Length123 < Length12:
        Length123 = Length12

    # 1. Initial and 2. Crop Development stage
    # CGC is given and Length12 is already adjusted to it
    # OR Length12 is given and CGC has to be determined
    if (CCoVal >= CCxVal) or (Length12 <= L0):
        Length12 = 0
        StLength[0] = 0
        StLength[1] = 0
        CGCVal = undef_int
    else:
        if not CGCgiven:  # Length12 is given and CGC has to be determined
            CGCVal = math.log((0.25 * CCxVal / CCoVal) / (1.0 - 0.98)) / float(
                Length12 - L0
            )
            # Check if CGC < maximum value (0.40) and adjust Length12 if required
            if CGCVal > 0.40:
                CGCVal = 0.40
                CCxVal_scaled = 0.98 * CCxVal
                Length12 = DaysToReachCCwithGivenCGC(
                    CCxVal_scaled, CCoVal, CCxVal, CGCVal, L0
                )
                if Length123 < Length12:
                    Length123 = Length12
        # find StLength[1]
        CCToReach = 0.10
        StLength[0] = DaysToReachCCwithGivenCGC(
            CCToReach, CCoVal, CCxVal, CGCVal, L0
        )
        # find StLength[2]
        StLength[1] = Length12 - StLength[0]

    L12Adj = Length12

    # adjust Initial and Crop Development stage, in case crop starts as regrowth
    if ThePlanting == plant_regrowth:
        if TheDaysToCCini == undef_int:
            # maximum canopy cover is already reached at start season
            L12Adj = 0
            StLength[0] = 0
            StLength[1] = 0
        else:
            if TheDaysToCCini == 0:
                # start at germination
                L12Adj = Length12 - L0
                StLength[0] = StLength[0] - L0
            else:
                # start after germination
                L12Adj = Length12 - (L0 + TheDaysToCCini)
                StLength[0] = StLength[0] - (L0 + TheDaysToCCini)
            if StLength[0] < 0:
                StLength[0] = 0
            StLength[1] = L12Adj - StLength[0]

    # 3. Mid season stage
    StLength[2] = Length123 - L12Adj

    # 4. Late season stage
    StLength[3] = LengthCanopyDecline(CCxVal, CDCVal)

    # final adjustment
    if StLength[0] > TotalLength:
        StLength[0] = TotalLength
        StLength[1] = 0
        StLength[2] = 0
        StLength[3] = 0
    else:
        if (StLength[0] + StLength[1]) > TotalLength:
            StLength[1] = TotalLength - StLength[0]
            StLength[2] = 0
            StLength[3] = 0
        else:
            if (StLength[0] + StLength[1] + StLength[2]) > TotalLength:
                StLength[2] = TotalLength - StLength[0] - StLength[1]
                StLength[3] = 0
            elif (StLength[0] + StLength[1] + StLength[2] + StLength[3]) > TotalLength:
                StLength[3] = (
                    TotalLength - StLength[0] - StLength[1] - StLength[2]
                )

    return Length123, StLength, Length12, CGCVal








def CompleteProfileDescription():

    for i in range(GetSoil_NrSoilLayers() + 1, max_SoilLayers + 1):
        soillayer_i_temp = GetSoilLayer_i(i)
        soillayer_i_temp2 = set_layer_undef(soillayer_i_temp)
        SetSoilLayer_i(i, soillayer_i_temp2)

    SetSimulation_ResetIniSWC(True)
    TotalWaterContent_temp = GetTotalWaterContent()
    Compartment_temp = GetCompartment()
    soillayer_temp = GetSoilLayer()

    soillayer_temp, Compartment_temp = specify_soil_layer(
        GetNrCompartments(),
        int(GetSoil_NrSoilLayers()),
        soillayer_temp,
        Compartment_temp,
        TotalWaterContent_temp
    )
    SetSoilLayer(soillayer_temp)
    SetTotalWaterContent(TotalWaterContent_temp)
    SetCompartment(Compartment_temp)


def TimeToCCini(ThePlantingType, TheCropPlantingDens, TheSizeSeedling, TheSizePlant, TheCropCCx, TheCropCGC):
    if (ThePlantingType == plant_Seed) or (ThePlantingType == plant_transplant) or (TheSizeSeedling >= TheSizePlant):
        ElapsedTime = 0
    else:
        TheCropCCo = (TheCropPlantingDens / 10000.0) * (TheSizeSeedling / 10000.0)
        TheCropCCini = (TheCropPlantingDens / 10000.0) * (TheSizePlant / 10000.0)
        if TheCropCCini >= (0.98 * TheCropCCx):
            ElapsedTime = undef_int
        else:
            ElapsedTime = DaysToReachCCwithGivenCGC(TheCropCCini, TheCropCCo, TheCropCCx, TheCropCGC, 0)
    return ElapsedTime


def DaysToReachCCwithGivenCGC(CCToReach, CCoVal, CCxVal, CGCVal, L0):
    L = 0.0
    CCToReach_local = CCToReach
    if (CCoVal > CCToReach_local) or (CCoVal >= CCxVal):
        L = 0.0
    else:
        if CCToReach_local > (0.98 * CCxVal):
            CCToReach_local = 0.98 * CCxVal
        if CCToReach_local <= CCxVal / 2.0:
            L = math.log(CCToReach_local / CCoVal) / CGCVal
        else:
            L = math.log((0.25 * CCxVal * CCxVal / CCoVal) / (CCxVal - CCToReach_local)) / CGCVal

    return L0 + roundc(L, mold=1)

def TimeToMaxCanopySF(
    CCo,
    CGC,
    CCx,
    L0,
    L12,
    L123,
    LToFlor,
    LFlor,
    DeterminantCrop,
    L12SF,
    RedCGC,
    RedCCx,
    ClassSF,
):
    CCToReach = 0.0
    L12SFmax = 0

    if (ClassSF == 0) or ((RedCCx == 0) and (RedCGC == 0)):
        L12SF = L12
    else:
        CCToReach = 0.98 * (1.0 - RedCCx / 100.0) * CCx
        L12SF = DaysToReachCCwithGivenCGC(
            CCToReach,
            CCo,
            (1.0 - RedCCx / 100.0) * CCx,
            CGC * (1.0 - RedCGC / 100.0),
            L0,
        )

        if DeterminantCrop:
            L12SFmax = LToFlor + roundc(LFlor / 2.0, mold="int32")
        else:
            L12SFmax = L123

        if L12SF > L12SFmax:
            while (L12SF > L12SFmax) and (RedCGC > 0):
                RedCGC -= 1
                L12SF = DaysToReachCCwithGivenCGC(
                    CCToReach,
                    CCo,
                    (1.0 - RedCCx / 100.0) * CCx,
                    CGC * (1.0 - RedCGC / 100.0),
                    L0,
                )

            while (
                (L12SF > L12SFmax)
                and ((1.0 - RedCCx / 100.0) * CCx > 0.10)
                and (RedCCx <= 50)
            ):
                RedCCx += 1
                CCToReach = 0.98 * (1.0 - RedCCx / 100.0) * CCx
                L12SF = DaysToReachCCwithGivenCGC(
                    CCToReach,
                    CCo,
                    (1.0 - RedCCx / 100.0) * CCx,
                    CGC * (1.0 - RedCGC / 100.0),
                    L0,
                )

    return L12SF, RedCGC, RedCCx, ClassSF


def FullUndefinedRecord(FromY, FromD, FromM, ToD, ToM):
    return (
        FromY == 1901
        and FromD == 1
        and FromM == 1
        and ToD == 31
        and ToM == 12
    )




def CompleteCropDescription():
    CGCisGiven = True
    FertStress = None
    RedCGC_temp = None
    RedCCX_temp = None
    Crop_DaysToSenescence_temp = None
    Crop_Length_temp = [0] * 4
    Crop_DaysToFullCanopy_temp = None
    Crop_CGC_temp = None
    Crop_DaysToFullCanopySF_temp = None

    # Determine dHIdt based on crop type
    if GetCrop_subkind() in (subkind_Vegetative, subkind_Forage):
        if GetCrop_DaysToHIo() > 0:
            if GetCrop_DaysToHIo() > GetCrop_DaysToHarvest():
                SetCrop_dHIdt(GetCrop_HI() / float(GetCrop_DaysToHarvest()))
            else:
                SetCrop_dHIdt(GetCrop_HI() / float(GetCrop_DaysToHIo()))
            if GetCrop_dHIdt() > 100.0:
                SetCrop_dHIdt(100.0)
        else:
            SetCrop_dHIdt(100.0)
    else:
        # Grain or tuber crops
        if GetCrop_DaysToHIo() > 0:
            SetCrop_dHIdt(GetCrop_HI() / float(GetCrop_DaysToHIo()))
        else:
            SetCrop_dHIdt(float(undef_int))

    if GetCrop_ModeCycle() == ModeCycle_CalendarDays:
        SetCrop_DaysToCCini(TimeToCCini(
            GetCrop_Planting(),
            GetCrop_PlantingDens(),
            GetCrop_SizeSeedling(),
            GetCrop_SizePlant(),
            GetCrop_CCx(),
            GetCrop_CGC()
        ))
        SetCrop_DaysToFullCanopy(DaysToReachCCwithGivenCGC(
            0.98 * GetCrop_CCx(),
            GetCrop_CCo(),
            GetCrop_CCx(),
            GetCrop_CGC(),
            GetCrop_DaysToGermination()
        ))

        if GetManagement_FertilityStress() != 0:
            FertStress = GetManagement_FertilityStress()
            Crop_DaysToFullCanopySF_temp = GetCrop_DaysToFullCanopySF()
            RedCGC_temp = GetSimulation_EffectStress_RedCGC()
            RedCCX_temp = GetSimulation_EffectStress_RedCCX()

            Crop_DaysToFullCanopySF_temp, RedCGC_temp, RedCCX_temp, FertStress = TimeToMaxCanopySF(
                GetCrop_CCo(),
                GetCrop_CGC(),
                GetCrop_CCx(),
                GetCrop_DaysToGermination(),
                GetCrop_DaysToFullCanopy(),
                GetCrop_DaysToSenescence(),
                GetCrop_DaysToFlowering(),
                GetCrop_LengthFlowering(),
                GetCrop_DeterminancyLinked(),
                Crop_DaysToFullCanopySF_temp,
                RedCGC_temp,
                RedCCX_temp,
                FertStress
            )

            SetManagement_FertilityStress(FertStress)
            SetSimulation_EffectStress_RedCGC(RedCGC_temp)
            SetSimulation_EffectStress_RedCCX(RedCCX_temp)
            SetCrop_DaysToFullCanopySF(Crop_DaysToFullCanopySF_temp)
        else:
            SetCrop_DaysToFullCanopySF(GetCrop_DaysToFullCanopy())

        SetCrop_GDDaysToCCini(undef_int)
        SetCrop_GDDaysToGermination(undef_int)
        SetCrop_GDDaysToFullCanopy(undef_int)
        SetCrop_GDDaysToFullCanopySF(undef_int)
        SetCrop_GDDaysToFlowering(undef_int)
        SetCrop_GDDLengthFlowering(undef_int)
        SetCrop_GDDaysToSenescence(undef_int)
        SetCrop_GDDaysToHarvest(undef_int)
        SetCrop_GDDaysToMaxRooting(undef_int)
        SetCrop_GDDCGC(float(undef_int))
        SetCrop_GDDCDC(float(undef_int))
    else:
        SetCrop_GDDaysToCCini(TimeToCCini(
            GetCrop_Planting(),
            GetCrop_PlantingDens(),
            GetCrop_SizeSeedling(),
            GetCrop_SizePlant(),
            GetCrop_CCx(),
            GetCrop_GDDCGC()
        ))
        SetCrop_DaysToCCini(TimeToCCini(
            GetCrop_Planting(),
            GetCrop_PlantingDens(),
            GetCrop_SizeSeedling(),
            GetCrop_SizePlant(),
            GetCrop_CCx(),
            GetCrop_CGC()
        ))
        SetCrop_GDDaysToFullCanopy(DaysToReachCCwithGivenCGC(
            0.98 * GetCrop_CCx(),
            GetCrop_CCo(),
            GetCrop_CCx(),
            GetCrop_GDDCGC(),
            GetCrop_GDDaysToGermination()
        ))
        # Crop.GDDaysToFullCanopySF is determined in RUN or ManagementUnit if required

    CGCisGiven = True
    Crop_DaysToSenescence_temp = GetCrop_DaysToSenescence()
    Crop_Length_temp = GetCrop_Length()
    Crop_DaysToFullCanopy_temp = GetCrop_DaysToFullCanopy()
    Crop_CGC_temp = GetCrop_CGC()

    Crop_DaysToSenescence_temp, Crop_Length_temp, Crop_DaysToFullCanopy_temp, Crop_CGC_temp = DetermineLengthGrowthStages(
        GetCrop_CCo(),
        GetCrop_CCx(),
        GetCrop_CDC(),
        GetCrop_DaysToGermination(),
        GetCrop_DaysToHarvest(),
        CGCisGiven,
        GetCrop_DaysToCCini(),
        GetCrop_Planting(),
        Crop_DaysToSenescence_temp,
        Crop_Length_temp,
        Crop_DaysToFullCanopy_temp,
        Crop_CGC_temp
    )

    SetCrop_DaysToSenescence(Crop_DaysToSenescence_temp)
    SetCrop_Length(Crop_Length_temp)
    SetCrop_DaysToFullCanopy(Crop_DaysToFullCanopy_temp)
    SetCrop_CGC(Crop_CGC_temp)

    SetCrop_CCoAdjusted(GetCrop_CCo())
    SetCrop_CCxAdjusted(GetCrop_CCx())
    SetCrop_CCxWithered(GetCrop_CCx())
    SetSumWaBal_Biomass(0.0)
    SetSumWaBal_BiomassPot(0.0)
    SetSumWaBal_BiomassUnlim(0.0)
    SetSumWaBal_BiomassTot(0.0)  # crop and weeds (for soil fertility stress)
    SetSumWaBal_YieldPart(0.0)
    SetSimulation_EvapLimitON(False)


def DetermineDayNr(Dayi, Monthi, Yeari):
    return math.trunc(
        (Yeari - 1901) * 365.25
        + ElapsedDays[Monthi - 1]  # mismo nombre, indexado desde 0
        + Dayi
        + 0.05
    )

def DayString(DNr):
    DNr_t = DNr
    if GetClimFile() == '(None)':
        while DNr_t > 365:
            DNr_t -= 365

    dayi, monthi, yeari = DetermineDate(DNr_t)

    strA = f"{dayi}"
    if GetClimRecord_FromY() == 1901:
        strB = ""
    else:
        strB = f"{yeari}"

    strB = strA.strip() + " " + NameMonth[monthi - 1].strip() + " " + strB.strip()
    while len(strB) < 17:
        strB = strB + " "

    return strB

def DetermineDate(DayNr):

    Yeari = math.trunc((DayNr - 0.05) / 365.25)
    SumDayMonth = DayNr - Yeari * 365.25
    Yeari = 1901 + Yeari
    Monthi = 1

    # ElapsedDays[0] -> mes 1, ElapsedDays[1] -> mes 2, etc.
    while Monthi < 12:
        if SumDayMonth <= ElapsedDays[Monthi]:  # ElapsedDays(Monthi+1)
            break
        Monthi += 1

    Dayi = roundc(
        SumDayMonth - ElapsedDays[Monthi - 1] + 0.25 + 0.06,
        mold="int32",
    )

    return Dayi, Monthi, Yeari

def EndGrowingPeriod(Day1, DayN):
    # This function determines Crop.DayN and the string
    DayN = Day1 + GetCrop_DaysToHarvest() - 1
    if DayN < Day1:
        DayN = Day1
    dayi, monthi, yeari = DetermineDate(DayN)
    Strday = f"{dayi:2d}"
    StrMonth = NameMonth[monthi - 1]
    EndGrowingPeriod_out = Strday + ' ' + StrMonth + '  '
    return EndGrowingPeriod_out, DayN

def AdjustCropYearToClimFile(CDay1, CDayN):
    dayi, monthi, yeari = DetermineDate(CDay1)
    if GetClimFile() == '(None)':
        yeari = 1901  # yeari = 1901 if undefined year
    else:
        yeari = GetClimRecord_FromY()  # yeari = 1901 if undefined year
    CDay1 = DetermineDayNr(dayi, monthi, yeari)
    temp_str, CDayN = EndGrowingPeriod(CDay1, CDayN)
    return CDay1, CDayN

def SetClimData():
    SetClimRecord_NrObs(999)  # (heeft geen belang)

    # Part A - ETo and Rain files --> ClimFile
    if (GetEToFile() == '(None)') and (GetRainFile() == '(None)'):
        SetClimFile('(None)')
        SetClimDescription('Specify Climatic data when Running AquaCrop')
        SetClimRecord_DataType(datatype_Daily)
        SetClimRecord_FromString('any date')
        SetClimRecord_ToString('any date')
        SetClimRecord_FromY(1901)
    else:
        SetClimFile('EToRainTempFile')
        SetClimDescription('Read ETo/RAIN/TEMP data set')
        if GetEToFile() == '(None)':
            SetClimRecord_FromY(GetRainRecord_FromY())
            SetClimRecord_FromDayNr(GetRainRecord_FromDayNr())
            SetClimRecord_ToDayNr(GetRainRecord_ToDayNr())
            SetClimRecord_FromString(GetRainRecord_FromString())
            SetClimRecord_ToString(GetRainRecord_ToString())
            if FullUndefinedRecord(
                GetRainRecord_FromY(),
                GetRainRecord_FromD(),
                GetRainRecord_FromM(),
                GetRainRecord_ToD(),
                GetRainRecord_ToM()
            ):
                SetClimRecord_NrObs(365)
        if GetRainFile() == '(None)':
            SetClimRecord_FromY(GetEToRecord_FromY())
            SetClimRecord_FromDayNr(GetEToRecord_FromDayNr())
            SetClimRecord_ToDayNr(GetEToRecord_ToDayNr())
            SetClimRecord_FromString(GetEToRecord_FromString())
            SetClimRecord_ToString(GetEToRecord_ToString())
            if FullUndefinedRecord(
                GetEToRecord_FromY(),
                GetEToRecord_FromD(),
                GetEToRecord_FromM(),
                GetEToRecord_ToD(),
                GetEToRecord_ToM()
            ):
                SetClimRecord_NrObs(365)

        if (GetEToFile() != '(None)') and (GetRainFile() != '(None)'):
            SetARecord = GetEToRecord()
            SetBRecord = GetRainRecord()
            if (
                (GetEToRecord_FromY() == 1901)
                and FullUndefinedRecord(
                    GetEToRecord_FromY(),
                    GetEToRecord_FromD(),
                    GetEToRecord_FromM(),
                    GetEToRecord_ToD(),
                    GetEToRecord_ToM()
                )
            ) and (
                (GetRainRecord_FromY() == 1901)
                and FullUndefinedRecord(
                    GetRainRecord_FromY(),
                    GetRainRecord_FromD(),
                    GetRainRecord_FromM(),
                    GetRainRecord_ToD(),
                    GetRainRecord_ToM()
                )
            ):
                SetClimRecord_NrObs(365)

            if (GetEToRecord_FromY() == 1901) and (GetRainRecord_FromY() != 1901):
                # Jaartal van RainRecord ---> SetARecord (= EToRecord)
                # FromY + adjust FromDayNr and FromString
                SetARecord.FromY = GetRainRecord_FromY()
                SetARecord.FromDayNr = DetermineDayNr(
                    GetEToRecord_FromD(),
                    GetEToRecord_FromM(),
                    SetARecord.FromY
                )
                if (
                    (SetARecord.FromDayNr < GetRainRecord_FromDayNr())
                    and (GetRainRecord_FromY() < GetRainRecord_ToY())
                ):
                    SetARecord.FromY = GetRainRecord_FromY() + 1
                    SetARecord.FromDayNr = DetermineDayNr(
                        GetEToRecord_FromD(),
                        GetEToRecord_FromM(),
                        SetARecord.FromY
                    )
                SetClimRecord_FromY(SetARecord.FromY)
                # nodig voor DayString (werkt met ClimRecord)
                SetARecord.FromString = DayString(SetARecord.FromDayNr)
                # ToY + adjust ToDayNr and ToString
                if FullUndefinedRecord(
                    GetEToRecord_FromY(),
                    GetEToRecord_FromD(),
                    GetEToRecord_FromM(),
                    GetEToRecord_ToD(),
                    GetEToRecord_ToM()
                ):
                    SetARecord.ToY = GetRainRecord_ToY()
                else:
                    SetARecord.ToY = SetARecord.FromY
                SetARecord.ToDayNr = DetermineDayNr(
                    GetEToRecord_ToD(),
                    GetEToRecord_ToM(),
                    SetARecord.ToY
                )
                SetARecord.ToString = DayString(SetARecord.ToDayNr)

            if (GetEToRecord_FromY() != 1901) and (GetRainRecord_FromY() == 1901):
                # Jaartal van EToRecord ---> SetBRecord (= RainRecord)
                # FromY + adjust FromDayNr and FromString
                SetBRecord.FromY = GetEToRecord_FromY()
                SetBRecord.FromDayNr = DetermineDayNr(
                    GetRainRecord_FromD(),
                    GetRainRecord_FromM(),
                    SetBRecord.FromY
                )
                if (
                    (SetBRecord.FromDayNr < GetEToRecord_FromDayNr())
                    and (GetEToRecord_FromY() < GetEToRecord_ToY())
                ):
                    SetBRecord.FromY = GetEToRecord_FromY() + 1
                    SetBRecord.FromDayNr = DetermineDayNr(
                        GetRainRecord_FromD(),
                        GetRainRecord_FromM(),
                        SetBRecord.FromY
                    )
                SetClimRecord_FromY(SetBRecord.FromY)
                # nodig voor DayString (werkt met ClimRecord)
                SetBRecord.FromString = DayString(SetBRecord.FromDayNr)
                # ToY + adjust ToDayNr and ToString
                if FullUndefinedRecord(
                    GetRainRecord_FromY(),
                    GetRainRecord_FromD(),
                    GetRainRecord_FromM(),
                    GetRainRecord_ToD(),
                    GetRainRecord_ToM()
                ):
                    SetBRecord.ToY = GetEToRecord_ToY()
                else:
                    SetBRecord.ToY = SetBRecord.FromY
                SetBRecord.ToDayNr = DetermineDayNr(
                    GetRainRecord_ToD(),
                    GetRainRecord_ToM(),
                    SetBRecord.ToY
                )
                SetBRecord.ToString = DayString(SetBRecord.ToDayNr)

            # bepaal characteristieken van ClimRecord
            SetClimRecord_FromY(SetARecord.FromY)
            SetClimRecord_FromDayNr(SetARecord.FromDayNr)
            tmpstr = SetARecord.FromString
            SetClimRecord_FromString(tmpstr)
            if GetClimRecord_FromDayNr() < SetBRecord.FromDayNr:
                SetClimRecord_FromY(SetBRecord.FromY)
                SetClimRecord_FromDayNr(SetBRecord.FromDayNr)
                SetClimRecord_FromString(SetBRecord.FromString)
            SetClimRecord_ToDayNr(SetARecord.ToDayNr)
            tmpstr = SetARecord.ToString
            SetClimRecord_ToString(tmpstr)
            if GetClimRecord_ToDayNr() > SetBRecord.ToDayNr:
                SetClimRecord_ToDayNr(SetBRecord.ToDayNr)
                SetClimRecord_ToString(SetBRecord.ToString)
            if GetClimRecord_ToDayNr() < GetClimRecord_FromDayNr():
                SetClimFile('(None)')
                SetClimDescription('ETo data set <--NO OVERLAP--> RAIN data set')
                SetClimRecord_NrObs(0)
                SetClimRecord_FromY(1901)

    # Part B - ClimFile and Temperature files --> ClimFile
    if (GetTemperatureFile() == '(None)') or (GetTemperatureFile() == '(External)'):
        # no adjustments are required
        pass
    else:
        if GetClimFile() == '(None)':
            SetClimFile('EToRainTempFile')
            SetClimDescription('Read ETo/RAIN/TEMP data set')
            SetClimRecord_FromY(GetTemperatureRecord_FromY())
            SetClimRecord_FromDayNr(GetTemperatureRecord_FromDayNr())
            SetClimRecord_ToDayNr(GetTemperatureRecord_ToDayNr())
            SetClimRecord_FromString(GetTemperatureRecord_FromString())
            SetClimRecord_ToString(GetTemperatureRecord_ToString())
            if (
                (GetTemperatureRecord_FromY() == 1901)
                and FullUndefinedRecord(
                    GetTemperatureRecord_FromY(),
                    GetTemperatureRecord_FromD(),
                    GetTemperatureRecord_FromM(),
                    GetTemperatureRecord_ToD(),
                    GetTemperatureRecord_ToM()
                )
            ):
                SetClimRecord_NrObs(365)
            else:
                SetClimRecord_NrObs(
                    GetTemperatureRecord_ToDayNr()
                    - GetTemperatureRecord_FromDayNr()
                    + 1
                )
        else:
            tmpFromD, tmpFromM, tmpFromY = DetermineDate(GetClimRecord_FromDayNr())
            SetClimRecord_FromD(tmpFromD)
            SetClimRecord_FromM(tmpFromM)
            SetClimRecord_FromY(tmpFromY)
            tmpToD, tmpToM, tmpToY = DetermineDate(GetClimRecord_ToDayNr())
            SetClimRecord_ToD(tmpToD)
            SetClimRecord_ToM(tmpToM)
            SetClimRecord_ToY(tmpToY)
            SetARecord = GetClimRecord()
            SetBRecord = GetTemperatureRecord()

            if (
                (GetClimRecord_FromY() == 1901)
                and (GetTemperatureRecord_FromY() == 1901)
                and (GetClimRecord_NrObs() == 365)
                and FullUndefinedRecord(
                    GetTemperatureRecord_FromY(),
                    GetTemperatureRecord_FromD(),
                    GetTemperatureRecord_FromM(),
                    GetTemperatureRecord_ToD(),
                    GetTemperatureRecord_ToM()
                )
            ):
                SetClimRecord_NrObs(365)
            else:
                SetClimRecord_NrObs(
                    GetTemperatureRecord_ToDayNr()
                    - GetTemperatureRecord_FromDayNr()
                    + 1
                )
            if (GetClimRecord_FromY() == 1901) and (GetTemperatureRecord_FromY() != 1901):
                # Jaartal van TemperatureRecord ---> SetARecord (= ClimRecord)
                # FromY + adjust FromDayNr and FromString
                SetARecord.FromY = GetTemperatureRecord_FromY()
                SetARecord.FromDayNr = DetermineDayNr(
                    GetClimRecord_FromD(),
                    GetClimRecord_FromM(),
                    SetARecord.FromY
                )
                if (
                    (SetARecord.FromDayNr < GetTemperatureRecord_FromDayNr())
                    and (
                        GetTemperatureRecord_FromY() < GetTemperatureRecord_ToY()
                    )
                ):
                    SetARecord.FromY = GetTemperatureRecord_FromY() + 1
                    SetARecord.FromDayNr = DetermineDayNr(
                        GetClimRecord_FromD(),
                        GetClimRecord_FromM(),
                        SetARecord.FromY
                    )
                SetARecord.FromString = DayString(SetARecord.FromDayNr)
                # ToY + adjust ToDayNr and ToString
                if FullUndefinedRecord(
                    GetClimRecord_FromY(),
                    GetClimRecord_FromD(),
                    GetClimRecord_FromM(),
                    GetClimRecord_ToD(),
                    GetClimRecord_ToM()
                ):
                    SetARecord.ToY = GetTemperatureRecord_ToY()
                else:
                    SetARecord.ToY = SetARecord.FromY
                SetARecord.ToDayNr = DetermineDayNr(
                    GetClimRecord_ToD(),
                    GetClimRecord_ToM(),
                    SetARecord.ToY
                )
                SetARecord.ToString = DayString(SetARecord.ToDayNr)

            if (GetClimRecord_FromY() != 1901) and (GetTemperatureRecord_FromY() == 1901):
                # Jaartal van ClimRecord ---> SetBRecord (= GetTemperatureRecord())
                # FromY + adjust FromDayNr and FromString
                SetBRecord.FromY = GetClimRecord_FromY()
                SetBRecord.FromDayNr = DetermineDayNr(
                    GetTemperatureRecord_FromD(),
                    GetTemperatureRecord_FromM(),
                    SetBRecord.FromY
                )
                if (
                    (SetBRecord.FromDayNr < GetClimRecord_FromDayNr())
                    and (GetClimRecord_FromY() < GetClimRecord_ToY())
                ):
                    SetBRecord.FromY = GetClimRecord_FromY() + 1
                    SetBRecord.FromDayNr = DetermineDayNr(
                        GetTemperatureRecord_FromD(),
                        GetTemperatureRecord_FromM(),
                        SetBRecord.FromY
                    )
                # SetClimRecord_FromY(SetBRecord.FromY); ! nodig voor DayString
                # (werkt met ClimRecord)
                SetBRecord.FromString = DayString(SetBRecord.FromDayNr)
                # ToY + adjust ToDayNr and ToString
                if FullUndefinedRecord(
                    GetTemperatureRecord_FromY(),
                    GetTemperatureRecord_FromD(),
                    GetTemperatureRecord_FromM(),
                    GetTemperatureRecord_ToD(),
                    GetTemperatureRecord_ToM()
                ):
                    SetBRecord.ToY = GetClimRecord_ToY()
                else:
                    SetBRecord.ToY = SetBRecord.FromY
                SetBRecord.ToDayNr = DetermineDayNr(
                    GetTemperatureRecord_ToD(),
                    GetTemperatureRecord_ToM(),
                    SetBRecord.ToY
                )
                SetBRecord.ToString = DayString(SetBRecord.ToDayNr)

            # bepaal nieuwe characteristieken van ClimRecord
            SetClimRecord_FromY(SetARecord.FromY)
            SetClimRecord_FromDayNr(SetARecord.FromDayNr)
            SetClimRecord_FromString(SetARecord.FromString)
            if GetClimRecord_FromDayNr() < SetBRecord.FromDayNr:
                SetClimRecord_FromY(SetBRecord.FromY)
                SetClimRecord_FromDayNr(SetBRecord.FromDayNr)
                SetClimRecord_FromString(SetBRecord.FromString)
            SetClimRecord_ToDayNr(SetARecord.ToDayNr)
            SetClimRecord_ToString(SetARecord.ToString)
            if GetClimRecord_ToDayNr() > SetBRecord.ToDayNr:
                SetClimRecord_ToDayNr(SetBRecord.ToDayNr)
                SetClimRecord_ToString(SetBRecord.ToString)
            if GetClimRecord_ToDayNr() < GetClimRecord_FromDayNr():
                SetClimFile('(None)')
                SetClimDescription('Clim data <--NO OVERLAP--> TEMPERATURE data')
                SetClimRecord_NrObs(0)
                SetClimRecord_FromY(1901)


def AdjustClimRecordTo(CDayN):
    dayi, monthi, yeari = DetermineDate(CDayN)
    SetClimRecord_ToD(31)
    SetClimRecord_ToM(12)
    SetClimRecord_ToY(yeari)
    ToDayNr_tmp = DetermineDayNr(
        GetClimRecord_ToD(),
        GetClimRecord_ToM(),
        GetClimRecord_ToY(),
    )
    SetClimRecord_ToDayNr(ToDayNr_tmp)

def AdjustSimPeriod():
    IniSimFromDayNr = GetSimulation_FromDayNr()
    dayi = 0
    monthi = 0
    ThePlantingYear = 0
    if GetSimulation_LinkCropToSimPeriod():
        FromDayNr_temp = GetSimulation_FromDayNr()
        FromDayNr_temp = DetermineLinkedSimDay1(GetCrop_Day1(), FromDayNr_temp)
        SetSimulation_FromDayNr(FromDayNr_temp)
        if GetCrop_Day1() == GetSimulation_FromDayNr():
            SetSimulation_ToDayNr(GetCrop_DayN())
        else:
            SetSimulation_ToDayNr(GetSimulation_FromDayNr() + 30)  # 30 days
        if GetClimFile() != '(None)':
            if GetSimulation_ToDayNr() > GetClimRecord_ToDayNr():
                SetSimulation_ToDayNr(GetClimRecord_ToDayNr())
            if GetSimulation_ToDayNr() < GetClimRecord_FromDayNr():
                SetSimulation_ToDayNr(GetClimRecord_FromDayNr())
    else:
        if GetSimulation_FromDayNr() > GetCrop_Day1():
            SetSimulation_FromDayNr(GetCrop_Day1())
        SetSimulation_ToDayNr(GetCrop_DayN())
        if (
            GetClimFile() != '(None)'
            and (
                GetSimulation_FromDayNr() <= GetClimRecord_FromDayNr()
                or GetSimulation_FromDayNr() >= GetClimRecord_ToDayNr()
            )
        ):
            SetSimulation_FromDayNr(GetClimRecord_FromDayNr())
            SetSimulation_ToDayNr(GetSimulation_FromDayNr() + 30)  # 30 days


    # Simulation period cannot exceed Premature End of crop growth  - Version 7.3
    dayi, monthi, ThePlantingYear = DetermineDate(GetCrop_Day1())  # planting year

    SetSimulation_DayNrPrematureEnd(TheDayNrPrematureEnd(GetCrop_PrematureEnd(), ThePlantingYear))

    if ((GetCrop_PrematureEnd() != undef_int) and
        (GetSimulation_ToDayNr() > (GetSimulation_DayNrPrematureEnd() - 1))):
        SetSimulation_ToDayNr(GetSimulation_DayNrPrematureEnd() - 1)
        SetCrop_LastDayNr(GetSimulation_DayNrPrematureEnd() - 1)
    else:
        SetCrop_LastDayNr(GetCrop_DayN())

    # adjust initial depth and quality of the groundwater when required
    if (not GetSimulParam_ConstGwt()) and (
        IniSimFromDayNr != GetSimulation_FromDayNr()
    ):
        if GetGroundWaterFile() == '(None)':
            FullFileName = GetPathNameProg() + 'GroundWater.AqC'
        else:
            FullFileName = GetGroundWaterFileFull()
        # initialize ZiAqua and ECiAqua
        ZiAqua_tmp = GetZiAqua()
        ECiAqua_tmp = GetECiAqua()
        ZiAqua_tmp, ECiAqua_tmp = LoadGroundWater(FullFileName, GetSimulation_FromDayNr(), ZiAqua_tmp, ECiAqua_tmp)
        SetZiAqua(ZiAqua_tmp)
        SetECiAqua(ECiAqua_tmp)
        Compartment_temp = GetCompartment()
        Compartment_temp = CalculateAdjustedFC(GetZiAqua() / 100.0, Compartment_temp)
        SetCompartment(Compartment_temp)
        if GetSimulation_IniSWC_AtFC():
            ResetSWCToFC()

def DetermineLinkedSimDay1(CropDay1, SimDay1):
    SimDay1 = CropDay1
    if GetClimFile() != '(None)':
        if (SimDay1 < GetClimRecord_FromDayNr()) or (SimDay1 > GetClimRecord_ToDayNr()):
            SetSimulation_LinkCropToSimPeriod(False)
            SimDay1 = GetClimRecord_FromDayNr()
    return SimDay1

def FindValues(AtDayNr, DayNr1, DayNr2, Z1, EC1, Z2, EC2):
    Zcm = roundc(
        100.0
        * (
            Z1
            + (Z2 - Z1)
            * float(AtDayNr - DayNr1)
            / float(DayNr2 - DayNr1)
        ),
        mold="int32",
    )
    ECdSm = EC1 + (EC2 - EC1) * float(AtDayNr - DayNr1) / float(DayNr2 - DayNr1)
    return Zcm, ECdSm

def LoadGroundWater(FullName, AtDayNr, Zcm, ECdSm):
    global GroundWaterDescription

    AtDayNr_local = AtDayNr
    # initialize
    TheEnd = False
    Year1Gwt = 1901
    DayNr1 = 1
    DayNr2 = 1

    FullName_stripped = FullName.strip()

    name = _strip_quotes(FullName_stripped).strip()
    if os.path.isabs(name):
        full_path = os.path.normpath(name)
    else:
        full_path = os.path.normpath(os.path.join(complete_path_dir, name.lstrip("/\\")))

    file_exists = FileExists(full_path)   # o: os.path.exists(full_path)

    if not file_exists:
        print("Groundwater file not found")
        return Zcm, ECdSm

    with open(full_path, "r") as f:
        lines = f.readlines()

    pos = 0

    def next_line():
        nonlocal pos
        if pos >= len(lines):
            return "", True
        line = lines[pos].rstrip("\n")
        pos += 1
        return line, False

    # GroundWaterDescription
    GroundWaterDescription, _ = next_line()
    # AquaCrop Version
    _, _ = next_line()

    # mode groundwater table
    line, eof = next_line()
    if eof or not line.strip():
        i = 0
    else:
        i = int(line.split()[0])

    if i == 0:
        # no groundwater table
        Zcm = undef_int
        ECdSm = float(undef_int)
        SetSimulParam_ConstGwt(True)
        TheEnd = True
    elif i == 1:
        # constant groundwater table
        SetSimulParam_ConstGwt(True)
    else:
        SetSimulParam_ConstGwt(False)

    # first day of observations (only for variable groundwater table)
    if not GetSimulParam_ConstGwt():
        line, _ = next_line()
        dayi = int(line.split()[0])
        line, _ = next_line()
        monthi = int(line.split()[0])
        line, _ = next_line()
        Year1Gwt = int(line.split()[0])
        DayNr1Gwt = DetermineDayNr(dayi, monthi, Year1Gwt)
    else:
        DayNr1Gwt = 0

    # single observation (Constant Gwt) or first observation (Variable Gwt)
    if i > 0:
        # groundwater table is present
        next_line()
        next_line()
        next_line()
        line, eof = next_line()
        if eof:
            StringREAD = ""
            rc_end = True
        else:
            StringREAD = line
            rc_end = False

        if StringREAD.strip():
            DayDouble, Z2, EC2 = SplitStringInThreeParams(StringREAD)
        else:
            DayDouble, Z2, EC2 = 0.0, 0.0, float(undef_int)

        if (i == 1) or rc_end:
            # Constant groundwater table or single observation
            Zcm = roundc(100.0 * Z2, mold="int32")
            ECdSm = EC2
            TheEnd = True
        else:
            DayNr2 = DayNr1Gwt + roundc(DayDouble, mold="int32") - 1

    # other observations
    if not TheEnd:
        # variable groundwater table with more than 1 observation
        # adjust AtDayNr
        dayi, monthi, yeari = DetermineDate(AtDayNr_local)
        if (yeari == 1901) and (Year1Gwt != 1901):
            # Make AtDayNr defined
            AtDayNr_local = DetermineDayNr(dayi, monthi, Year1Gwt)
        if (yeari != 1901) and (Year1Gwt == 1901):
            # Make AtDayNr undefined
            AtDayNr_local = DetermineDayNr(dayi, monthi, Year1Gwt)

        # get observation at AtDayNr
        if Year1Gwt != 1901:
            # year is defined
            if AtDayNr_local <= DayNr2:
                Zcm = roundc(100.0 * Z2, mold="int32")
                ECdSm = EC2
            else:
                while not TheEnd:
                    DayNr1 = DayNr2
                    Z1 = Z2
                    EC1 = EC2
                    line, eof = next_line()
                    if eof:
                        if not TheEnd:
                            Zcm = roundc(100.0 * Z2, mold="int32")
                            ECdSm = EC2
                            TheEnd = True
                        break
                    StringREAD = line
                    DayDouble, Z2, EC2 = SplitStringInThreeParams(StringREAD)
                    DayNr2 = DayNr1Gwt + roundc(DayDouble, mold="int32") - 1
                    if AtDayNr_local <= DayNr2:
                        Zcm, ECdSm = FindValues(
                            AtDayNr_local, DayNr1, DayNr2, Z1, EC1, Z2, EC2
                        )
                        TheEnd = True
        else:
            # year is undefined
            if AtDayNr_local <= DayNr2:
                DayNr2 = DayNr2 + 365
                AtDayNr_local = AtDayNr_local + 365
                while True:
                    line, eof = next_line()
                    if eof:
                        break
                    StringREAD = line
                    DayDouble, Z1, EC1 = SplitStringInThreeParams(StringREAD)
                    DayNr1 = DayNr1Gwt + roundc(DayDouble, mold="int32") - 1
                Zcm, ECdSm = FindValues(
                    AtDayNr_local, DayNr1, DayNr2, Z1, EC1, Z2, EC2
                )
            else:
                DayNrN = DayNr2 + 365
                ZN = Z2
                ECN = EC2
                while not TheEnd:
                    DayNr1 = DayNr2
                    Z1 = Z2
                    EC1 = EC2
                    line, eof = next_line()
                    if eof:
                        if not TheEnd:
                            Zcm, ECdSm = FindValues(
                                AtDayNr_local, DayNr2, DayNrN, Z2, EC2, ZN, ECN
                            )
                            TheEnd = True
                        break
                    StringREAD = line
                    DayDouble, Z2, EC2 = SplitStringInThreeParams(StringREAD)
                    DayNr2 = DayNr1Gwt + roundc(DayDouble, mold="int32") - 1
                    if AtDayNr_local <= DayNr2:
                        Zcm, ECdSm = FindValues(
                            AtDayNr_local, DayNr1, DayNr2, Z1, EC1, Z2, EC2
                        )
                        TheEnd = True

    return Zcm, ECdSm

def SplitStringInThreeParams(StringIN):
    Par1 = None
    Par2 = None
    Par3 = None

    LengthS = len(StringIN)
    i = 0
    Parami = 0
    # divide the line in parameters
    while (i < LengthS) and (Parami < 3):
        CharA = StringIN[i]
        if ord(CharA) > 32:
            # next Parameter
            Parami += 1
            StringNumber = ""
            while (ord(CharA) > 32) and (i < LengthS):
                StringNumber = (StringNumber.strip() + CharA).strip()
                i += 1
                if i < LengthS:
                    CharA = StringIN[i]
            if Parami == 1:
                Par1 = float(StringNumber)
            elif Parami == 2:
                Par2 = float(StringNumber)
            elif Parami == 3:
                Par3 = float(StringNumber)
        else:
            i += 1
        # end of line
    return Par1, Par2, Par3

def NoAdjustment(FCvolPr):
    if FCvolPr <= 10.0:
        return 1.0
    else:
        if FCvolPr >= 30.0:
            return 2.0
        else:
            pF = 2.0 + 0.3 * (FCvolPr - 10.0) / 20.0
            return math.exp(pF * math.log(10.0)) / 100.0
        
def CalculateAdjustedFC(DepthAquifer, CompartAdj):


    Depth = 0.0
    for compi in range(1, GetNrCompartments() + 1):
        Depth = Depth + CompartAdj[compi - 1].Thickness

    compi = GetNrCompartments()

    while True:
        Zi = Depth - CompartAdj[compi - 1].Thickness / 2.0
        Xmax = NoAdjustment(GetSoilLayer_FC(CompartAdj[compi - 1].Layer))

        if (DepthAquifer < 0.0) or ((DepthAquifer - Zi) >= Xmax):
            for ic in range(1, compi + 1):
                CompartAdj[ic - 1].FCadj = GetSoilLayer_FC(CompartAdj[ic - 1].Layer)
            compi = 0
        else:
            if (
                GetSoilLayer_FC(CompartAdj[compi - 1].Layer)
                >= GetSoilLayer_SAT(CompartAdj[compi - 1].Layer)
            ):
                CompartAdj[compi - 1].FCadj = GetSoilLayer_FC(
                    CompartAdj[compi - 1].Layer
                )
            else:
                if Zi >= DepthAquifer:
                    CompartAdj[compi - 1].FCadj = GetSoilLayer_SAT(
                        CompartAdj[compi - 1].Layer
                    )
                else:
                    DeltaV = (
                        GetSoilLayer_SAT(CompartAdj[compi - 1].Layer)
                        - GetSoilLayer_FC(CompartAdj[compi - 1].Layer)
                    )
                    DeltaFC = (DeltaV / (Xmax**2)) * (
                        Zi - (DepthAquifer - Xmax)
                    ) ** 2
                    CompartAdj[compi - 1].FCadj = GetSoilLayer_FC(
                        CompartAdj[compi - 1].Layer
                    ) + DeltaFC

            Depth = Depth - CompartAdj[compi - 1].Thickness
            compi = compi - 1

        if compi < 1:
            break

    return CompartAdj

def TheDayNrPrematureEnd(TheDayCropPrematureEnd, ThePlantingYear):
    TheDayNr = 0
    DayMax = 0
    MonthMax = 0
    yeari = 0
    YearMax = 0

    if TheDayCropPrematureEnd != undef_int:
        DayMax, MonthMax, yeari = DetermineDate(TheDayCropPrematureEnd)

        if TheDayCropPrematureEnd > 365:
            YearMax = ThePlantingYear + 1
        else:
            YearMax = ThePlantingYear

        TheDayNr = DetermineDayNr(DayMax, MonthMax, YearMax)
    else:
        TheDayNr = undef_int

    return TheDayNr

def ResetSWCToFC():
    SetSimulation_IniSWC_AtDepths(False)
    if GetZiAqua() < 0:  # no ground water table
        SetSimulation_IniSWC_NrLoc(GetSoil_NrSoilLayers())
        for layeri in range(1, GetSoil_NrSoilLayers() + 1):
            SetSimulation_IniSWC_Loc_i(layeri, GetSoilLayer_Thickness(layeri))
            SetSimulation_IniSWC_VolProc_i(layeri, GetSoilLayer_FC(layeri))
            SetSimulation_IniSWC_SaltECe_i(layeri, 0.0)
        for layeri in range(GetSoil_NrSoilLayers() + 1, max_No_compartments + 1):
            SetSimulation_IniSWC_Loc_i(layeri, undef_double)
            SetSimulation_IniSWC_VolProc_i(layeri, undef_double)
            SetSimulation_IniSWC_SaltECe_i(layeri, undef_double)
    else:
        SetSimulation_IniSWC_NrLoc(int(GetNrCompartments()))
        for Loci in range(1, GetSimulation_IniSWC_NrLoc() + 1):
            SetSimulation_IniSWC_Loc_i(Loci, GetCompartment_Thickness(Loci))
            SetSimulation_IniSWC_VolProc_i(Loci, GetCompartment_FCadj(Loci))
            SetSimulation_IniSWC_SaltECe_i(Loci, 0.0)

    for compi in range(1, GetNrCompartments() + 1):
        SetCompartment_theta(compi, GetCompartment_FCadj(compi) / 100.0)
        SetSimulation_ThetaIni_i(compi, GetCompartment_theta(compi))
        for celli in range(1, GetSoilLayer_SCP1(GetCompartment_Layer(compi)) + 1):
            # salinity in cells
            SetCompartment_Salt(compi, celli, 0.0)
            SetCompartment_Depo(compi, celli, 0.0)

def NoIrrigation():
    global IrriFirstDayNr
    global IrriInfoLastDay

    SetIrriMode(IrriMode_NoIrri)
    SetIrriDescription('Rainfed cropping')
    SetIrriMethod(IrriMethod_MSprinkler)
    SetSimulation_IrriECw(0.0)  # dS/m
    SetGenerateTimeMode(GenerateTimeMode_AllRAW)
    SetGenerateDepthMode(GenerateDepthMode_ToFC)
    IrriFirstDayNr = undef_int
    IrriInfoLastDay = undef_int
    for Nri in range(1, 6):
        SetIrriBeforeSeason_DayNr(Nri, 0)
        SetIrriBeforeSeason_Param(Nri, 0)
        SetIrriAfterSeason_DayNr(Nri, 0)
        SetIrriAfterSeason_Param(Nri, 0)
    SetIrriECw_PreSeason(0.0)  # dS/m
    SetIrriECw_PostSeason(0.0)  # dS/m

def NoManagementOffSeason():
    Nri = None

    SetOffSeasonDescription('No specific off-season conditions')
    # mulches
    SetManagement_SoilCoverBefore(0)
    SetManagement_SoilCoverAfter(0)
    SetManagement_EffectMulchOffS(50)
    # off-season irrigation
    SetSimulParam_IrriFwOffSeason(100)
    SetIrriECw_PreSeason(0.0)  # dS/m
    for Nri in range(1, 6):
        SetIrriBeforeSeason_DayNr(Nri, 0)
        SetIrriBeforeSeason_Param(Nri, 0)
    SetIrriECw_PostSeason(0.0)  # dS/m
    for Nri in range(1, 6):
        SetIrriAfterSeason_DayNr(Nri, 0)
        SetIrriAfterSeason_Param(Nri, 0)

def AdjustOnsetSearchPeriod():
    temp_Integer = None

    if GetClimFile() == '(None)':
        SetOnset_StartSearchDayNr(1)
        SetOnset_StopSearchDayNr(
            GetOnset_StartSearchDayNr() + GetOnset_LengthSearchPeriod() - 1
        )
    else:
        temp_Integer = GetOnset_StartSearchDayNr()
        temp_Integer = DetermineDayNr(
            1, 1, GetSimulation_YearStartCropCycle()
        )  # 1 January
        SetOnset_StartSearchDayNr(temp_Integer)
        if GetOnset_StartSearchDayNr() < GetClimRecord_FromDayNr():
            SetOnset_StartSearchDayNr(GetClimRecord_FromDayNr())
        SetOnset_StopSearchDayNr(
            GetOnset_StartSearchDayNr() + GetOnset_LengthSearchPeriod() - 1
        )
        if GetOnset_StopSearchDayNr() > GetClimRecord_ToDayNr():
            SetOnset_StopSearchDayNr(GetClimRecord_ToDayNr())
            SetOnset_LengthSearchPeriod(
                GetOnset_StopSearchDayNr() - GetOnset_StartSearchDayNr() + 1
            )

def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == "'" and s[-1] == "'") or (s[0] == '"' and s[-1] == '"')):
        s = s[1:-1]
    return s.strip()

def ResolvePath(name: str, base_dir: Optional[str] = None) -> str:
    target = _strip_quotes(name).strip()
    if os.path.isabs(target):
        return os.path.normpath(target)

    if base_dir is None:
        return os.path.normpath(os.path.join(complete_path_dir, target.lstrip("/\\")))

    base = _strip_quotes(base_dir).strip()
    if os.path.isabs(base):
        resolved_base = os.path.normpath(base)
    else:
        resolved_base = os.path.normpath(
            os.path.join(complete_path_dir, base.lstrip("/\\"))
        )

    if target:
        return os.path.normpath(os.path.join(resolved_base, target.lstrip("/\\")))

    return resolved_base

def check_file(directory, filename, AllOK, FileOK_tmp):
    # Sets AllOK to false if expected file does not exist.

    if filename != "(None)":
        directory = _strip_quotes(directory)
        filename = _strip_quotes(filename)

        full_name = ResolvePath(filename, directory)

        if not FileExists(full_name):
            AllOK = False
            FileOK_tmp = False
        else:
            FileOK_tmp = True

    return AllOK, FileOK_tmp


def CheckFilesInProject(Runi, AllOK, FileOK):
    FileOK_tmp = True

    AllOK = True
    FileOK_tmp = True

    # Check the 14 files
    input = ProjectInput[Runi - 1]

    AllOK, FileOK_tmp = check_file(input.Climate_Directory, input.Climate_Filename, AllOK, FileOK_tmp)
    FileOK.Climate_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.Temperature_Directory, input.Temperature_Filename, AllOK, FileOK_tmp)
    FileOK.Temperature_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.ETo_Directory, input.ETo_Filename, AllOK, FileOK_tmp)
    FileOK.ETo_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.Rain_Directory, input.Rain_Filename, AllOK, FileOK_tmp)
    FileOK.Rain_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.CO2_Directory, input.CO2_Filename, AllOK, FileOK_tmp)
    FileOK.CO2_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.Calendar_Directory, input.Calendar_Filename, AllOK, FileOK_tmp)
    FileOK.Calendar_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.Crop_Directory, input.Crop_Filename, AllOK, FileOK_tmp)
    FileOK.Crop_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.Irrigation_Directory, input.Irrigation_Filename, AllOK, FileOK_tmp)
    FileOK.Irrigation_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.Management_Directory, input.Management_Filename, AllOK, FileOK_tmp)
    FileOK.Management_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.GroundWater_Directory, input.GroundWater_Filename, AllOK, FileOK_tmp)
    FileOK.GroundWater_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.Soil_Directory, input.Soil_Filename, AllOK, FileOK_tmp)
    FileOK.Soil_Filename = FileOK_tmp

    if ProjectInput[Runi - 1].SWCIni_Filename != "KeepSWC":
        AllOK, FileOK_tmp = check_file(input.SWCIni_Directory, input.SWCIni_Filename, AllOK, FileOK_tmp)
        FileOK.SWCIni_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.OffSeason_Directory, input.OffSeason_Filename, AllOK, FileOK_tmp)
    FileOK.OffSeason_Filename = FileOK_tmp

    AllOK, FileOK_tmp = check_file(input.Observations_Directory, input.Observations_Filename, AllOK, FileOK_tmp)
    FileOK.Observations_Filename = FileOK_tmp

    return AllOK, FileOK

def ComposeFileForProgramParameters(TheFileNameProgram):
    FullFileNameProgramParameters = ""
    TheLength = len(TheFileNameProgram)
    tempstring = TheFileNameProgram
    TheExtension = tempstring[(TheLength - 3):TheLength]  # PRO or PRM

    # file name program parameters
    tempstring = TheFileNameProgram
    FullFileNameProgramParameters = tempstring[0:(TheLength - 3)].strip()

    # path file progrm parameters
    tempstring2 = f"{GetPathNameParam()}{FullFileNameProgramParameters.strip()}"
    FullFileNameProgramParameters = tempstring2

    # extension file program parameters
    if TheExtension == "PRO":
        tempstring2 = f"{FullFileNameProgramParameters.strip()}PP1"
        FullFileNameProgramParameters = tempstring2.strip()
    else:
        tempstring2 = f"{FullFileNameProgramParameters.strip()}PPn"
        FullFileNameProgramParameters = tempstring2.strip()

    return FullFileNameProgramParameters

def ComposeOutputFileName(TheProjectFileName):
    TempString = TheProjectFileName.strip()
    i = len(TempString)
    TempString2 = TempString[0:i - 4]
    SetOutputName(TempString2)


def CheckForKeepSWC():
    # @NOTE This procedure will try to read from the soil profile file.
    # If this file does not exist, the necessary information is gathered
    # from the attributes of the Soil global variable instead.

    fhandlex = None
    i = 0
    Runi = 0
    TotalNrOfRuns = 0
    FileName = ""
    FullFileName = ""
    Zrni = 0.0
    Zrxi = 0.0
    ZrSoili = 0.0
    VersionNrCrop = 0.0
    TheNrSoilLayers = 0
    TheSoilLayer = None
    PreviousProfFilefull = None
    has_external = False

    # 1. Initial settings
    RunWithKeepSWC = False
    ConstZrxForRun = float(undef_int)

    # 2. Look for restrictive soil layer
    # restricted to run 1 since with KeepSWC,
    # the soil file has to be common between runs
    PreviousProfFilefull = GetProfFilefull()  # keep name soil file
                                              # (to restore after check)

    FileName = ProjectInput[0].Soil_Filename
    has_external = (FileName == "(External)")

    if has_external:
        # Note: here we use the AquaCrop version number and assume that
        # the same version can be used in finalizing the soil settings.
        LoadProfileProcessing(ProjectInput[0].VersionNr)
    elif FileName.strip() == "(None)":
        FullFileName = GetPathNameSimul() + "DEFAULT.SOL"
        LoadProfile(FullFileName)
    else:
        FullFileName = ProjectInput[0].Soil_Directory + FileName
        LoadProfile(FullFileName)

    TheNrSoilLayers = GetSoil_NrSoilLayers()
    TheSoilLayer = GetSoilLayer()

    # 3. Check if runs with KeepSWC exist
    Runi = 1
    TotalNrOfRuns = GetNumberSimulationRuns()

    while (RunWithKeepSWC is False) and (Runi <= TotalNrOfRuns):
        if ProjectInput[Runi - 1].SWCIni_Filename == "KeepSWC":
            RunWithKeepSWC = True
        Runi = Runi + 1

    if RunWithKeepSWC is False:
        ConstZrxForRun = float(undef_int)  # reset

    # 4. Look for maximum root zone depth IF RunWithKeepSWC
    if RunWithKeepSWC is True:
        Runi = 1
        while Runi <= TotalNrOfRuns:
            # Obtain maximum rooting depth from the crop file
            FullFileName = (
                ProjectInput[Runi - 1].Crop_Directory
                + ProjectInput[Runi - 1].Crop_Filename
            )

            full_path = os.path.normpath(
                os.path.join(
                    complete_path_dir,
                    _strip_quotes(FullFileName).replace("'", "").replace('"', "").strip().lstrip("/\\"),
                )
            )

            try:
                with open(
                    full_path,
                    "r",
                    encoding="utf-8",
                ) as fhandlex:
                    lines = fhandlex.read().splitlines()
            except UnicodeDecodeError:
                with open(
                    full_path,
                    "r",
                    encoding="cp1252",
                ) as fhandlex:
                    lines = fhandlex.read().splitlines()

            idx = 0

            def next_line():
                nonlocal idx
                if idx >= len(lines):
                    return ""
                s = lines[idx]
                idx += 1
                return s

            def next_token_as_float():
                s = next_line().strip()
                return float(s.split()[0]) if s else 0.0

            # description
            _ = next_line()
            VersionNrCrop = next_token_as_float()

            if roundc(VersionNrCrop * 10, mold=1) <= 31:
                for i in range(1, 29 + 1):
                    _ = next_line()  # no Salinity stress
            else:
                if roundc(VersionNrCrop * 10, mold=1) <= 50:
                    for i in range(1, 32 + 1):
                        _ = next_line()
                else:
                    for i in range(1, 34 + 1):
                        _ = next_line()

            Zrni = next_token_as_float()  # minimum rooting depth
            Zrxi = next_token_as_float()  # maximum rooting depth

            ZrSoili = RootMaxInSoilProfile(Zrxi, TheNrSoilLayers, TheSoilLayer)
            if float(ZrSoili) > ConstZrxForRun:
                ConstZrxForRun = ZrSoili

            Runi = Runi + 1

    # 5. Reload existing soil file
    if not has_external:
        SetProfFilefull(PreviousProfFilefull)
        LoadProfile(GetProfFilefull())

    return RunWithKeepSWC, ConstZrxForRun

def GetNumberSimulationRuns():
    # Returns the total number of runs.

    return len(ProjectInput)

def GetOutputName():
    # Getter for the "OutputName" global variable.
    return OutputName

def LoadClim(FullName: str, ClimateDescription: str, ClimateRecord):
    # Returns updated (ClimateDescription, ClimateRecord) with a single disk read.

    name = _strip_quotes(FullName).strip()
    if os.path.isabs(name):
        full_path = os.path.normpath(name)
    else:
        full_path = os.path.normpath(
            os.path.join(complete_path_dir, name.lstrip("/\\"))
        )

    if not FileExists(full_path):
        print("Climate file not found: " + name)
        return ClimateDescription, ClimateRecord

    with open(full_path, "r", encoding="utf-8") as fhandle:
        lines = fhandle.read().splitlines()

    # read(fhandle, '(a)') ClimateDescription
    ClimateDescription = lines[0].strip() if len(lines) > 0 else ""

    # read(fhandle, *) Ni
    Ni = int(lines[1].split()[0]) if len(lines) > 1 and lines[1].strip() else 0

    if Ni == 1:
        ClimateRecord.DataType = datatype_Daily
    elif Ni == 2:
        ClimateRecord.DataType = datatype_Decadely
    else:
        ClimateRecord.DataType = datatype_Monthly

    # read(fhandle, *) ClimateRecord%FromD/FromM/FromY
    ClimateRecord.FromD = int(lines[2].split()[0]) if len(lines) > 2 and lines[2].strip() else 0
    ClimateRecord.FromM = int(lines[3].split()[0]) if len(lines) > 3 and lines[3].strip() else 0
    ClimateRecord.FromY = int(lines[4].split()[0]) if len(lines) > 4 and lines[4].strip() else 0

    # read(fhandle, *, iostat=rc) x 3  (skip lines 5,6,7)
    # ClimateRecord%NrObs = 0
    ClimateRecord.NrObs = 0

    # read(fhandle, *, iostat=rc) once BEFORE the loop, then loop until EOF.
    # That means the first observation line (index 8) is counted too if present.
    first_obs_idx = 8  # 0:desc,1:Ni,2:FromD,3:FromM,4:FromY,5,6,7 skipped,8 first obs pre-read
    if len(lines) > first_obs_idx:
        ClimateRecord.NrObs = len(lines) - first_obs_idx
    else:
        ClimateRecord.NrObs = 0

    CompleteClimateDescription(ClimateRecord)

    return ClimateDescription, ClimateRecord


def CompleteClimateDescription(ClimateRecord):
    ClimateRecord.FromDayNr = DetermineDayNr(
        ClimateRecord.FromD,
        ClimateRecord.FromM,
        ClimateRecord.FromY
    )

    if ClimateRecord.DataType == datatype_Daily:
        ClimateRecord.ToDayNr = ClimateRecord.FromDayNr + ClimateRecord.NrObs - 1
        ClimateRecord.ToD, ClimateRecord.ToM, ClimateRecord.ToY = DetermineDate(
            ClimateRecord.ToDayNr
        )

    elif ClimateRecord.DataType == datatype_Decadely:
        Deci = int(roundc((ClimateRecord.FromD + 9) / 10.0, mold=1)) + ClimateRecord.NrObs - 1

        ClimateRecord.ToM = ClimateRecord.FromM
        ClimateRecord.ToY = ClimateRecord.FromY

        while Deci > 3:
            Deci -= 3
            ClimateRecord.ToM += 1
            if ClimateRecord.ToM > 12:
                ClimateRecord.ToM = 1
                ClimateRecord.ToY += 1

        ClimateRecord.ToD = 10
        if Deci == 2:
            ClimateRecord.ToD = 20
        if Deci == 3:
            ClimateRecord.ToD = DaysInMonth(ClimateRecord.ToM)
            if (ClimateRecord.ToM == 2) and LeapYear(ClimateRecord.ToY):
                ClimateRecord.ToD += 1

        ClimateRecord.FromDayNr = DetermineDayNr(
            ClimateRecord.ToD,
            ClimateRecord.ToM,
            ClimateRecord.ToY
        )

    else:  # datatype_Monthly
        ClimateRecord.ToY = ClimateRecord.FromY
        ClimateRecord.ToM = ClimateRecord.FromM + ClimateRecord.NrObs - 1

        while ClimateRecord.ToM > 12:
            ClimateRecord.ToY += 1
            ClimateRecord.ToM -= 12

        ClimateRecord.ToD = DaysInMonth(ClimateRecord.ToM)
        if (ClimateRecord.ToM == 2) and LeapYear(ClimateRecord.ToY):
            ClimateRecord.ToD += 1

        ClimateRecord.FromDayNr = DetermineDayNr(
            ClimateRecord.ToD,
            ClimateRecord.ToM,
            ClimateRecord.ToY
        )

    dayStr = f"{ClimateRecord.FromD:2d}"
    if ClimateRecord.FromY == 1901:
        yearStr = ""
    else:
        yearStr = f"{ClimateRecord.FromY:4d}"
    ClimateRecord.FromString = dayStr + " " + NameMonth[ClimateRecord.FromM - 1] + " " + yearStr

    dayStr = f"{ClimateRecord.ToD:2d}"
    if ClimateRecord.FromY == 1901:
        yearStr = ""
    else:
        yearStr = f"{ClimateRecord.ToY:4d}"
    ClimateRecord.ToString = dayStr + " " + NameMonth[ClimateRecord.ToM - 1] + " " + yearStr

def LeapYear(Year: int) -> bool:
    LeapYear = False
    if frac(Year / 4.0) <= 0.01:
        LeapYear = True
    return LeapYear

def frac(val: float) -> float:
    return val - math.floor(val)


def AdjustSizeCompartments(CropZx: float):
    CropZx_eff = 0.0
    i = 0
    compi = 0
    TotDepthC = 0.0
    fAdd = 0.0
    PrevNrComp = 0

    PrevThickComp = [0.0] * (max_No_compartments + 1)
    PrevVolPrComp = [0.0] * (max_No_compartments + 1)
    PrevECdSComp = [0.0] * (max_No_compartments + 1)

    # esnures consistency for adjusted compartment sizes between Pascal and Fortran
    CropZx_eff = CropZx

    # 1. Save intial soil water profile (required when initial soil
    # water profile is NOT reset at start simulation - see 7.)
    PrevNrComp = int(GetNrCompartments())
    for compi in range(1, PrevNrComp + 1):
        PrevThickComp[compi] = GetCompartment_Thickness(compi)
        PrevVolPrComp[compi] = 100.0 * GetCompartment_theta(compi)

    # 2. Actual total depth of compartments
    TotDepthC = 0.0
    for i in range(1, GetNrCompartments() + 1):
        TotDepthC = TotDepthC + GetCompartment_Thickness(i)

    # 3. Increase number of compartments (if less than 12)
    if GetNrCompartments() < 12:
        while True:
            SetNrCompartments(GetNrCompartments() + 1)

            if (CropZx_eff - TotDepthC) > GetSimulParam_CompDefThick():
                SetCompartment_Thickness(GetNrCompartments(), GetSimulParam_CompDefThick())
            else:
                SetCompartment_Thickness(GetNrCompartments(), CropZx_eff - TotDepthC)
        
            TotDepthC = TotDepthC + GetCompartment_Thickness(GetNrCompartments())

            if (GetNrCompartments() == max_No_compartments) or ((TotDepthC + 0.00001) >= CropZx_eff):
                break

    # FIX BUG: _f32 (single precision) introducía error de ~1.5e-9 en las thicknesses
    # que rompía la asignación de compartimentos en frontera de capas SOL.
    # Pascal/Delphi usa Double, así que aquí también.
    sp01 = 0.1
    sp005 = 0.05

    # 4. Adjust size of compartments (if total depth of compartments < rooting depth)
    if (TotDepthC + 0.00001) < CropZx_eff:
        SetNrCompartments(12)
        fAdd = (CropZx_eff / 0.1 - 12.0) / 78.0

        for i in range(1, 12 + 1):
            SetCompartment_Thickness(i, sp01 * (1.0 + i * fAdd))
            SetCompartment_Thickness(
                i,
                sp005 * float(roundc(GetCompartment_Thickness(i) * 20.0, mold=1))
            )

        TotDepthC = 0.0
        for i in range(1, GetNrCompartments() + 1):
            TotDepthC = TotDepthC + GetCompartment_Thickness(i)

        if TotDepthC < CropZx_eff:
            while True:
                SetCompartment_Thickness(12, GetCompartment_Thickness(12) + sp005)
                TotDepthC = TotDepthC + sp005
                if TotDepthC >= CropZx_eff:
                    break
        else:
            while (TotDepthC - 0.04999999) >= CropZx_eff:
                SetCompartment_Thickness(12, GetCompartment_Thickness(12) - sp005)
                TotDepthC = TotDepthC - sp005



    # 5. Adjust soil water content and theta initial
    AdjustThetaInitial(PrevNrComp, PrevThickComp, PrevVolPrComp, PrevECdSComp)



def TranslateIniLayersToSWProfile(NrLay: int, LayThickness, LayVolPr, LayECdS, NrComp: int, Comp):
    Compi = 0
    Layeri = 0
    i = 0
    SDLay = 0.0
    SDComp = 0.0
    FracC = 0.0
    GoOn = True

    # from specific layers to Compartments
    for Compi in range(1, int(NrComp) + 1):
        Comp[Compi - 1].Theta = 0.0
        Comp[Compi - 1].WFactor = 0.0  # used for ECe in this procedure

    Compi = 0
    SDComp = 0.0
    Layeri = 1
    SDLay = float(LayThickness[Layeri - 1])
    GoOn = True

    while Compi < NrComp:
        FracC = 0.0
        Compi += 1
        SDComp += float(Comp[Compi - 1].Thickness)

        if SDLay >= SDComp:
            Comp[Compi - 1].Theta = Comp[Compi - 1].Theta + (1.0 - FracC) * float(LayVolPr[Layeri - 1]) / 100.0
            Comp[Compi - 1].WFactor = Comp[Compi - 1].WFactor + (1.0 - FracC) * float(LayECdS[Layeri - 1])
        else:
            # go to next layer
            while (SDLay < SDComp) and GoOn:
                # finish handling previous layer
                FracC = (SDLay - (SDComp - float(Comp[Compi - 1].Thickness))) / float(Comp[Compi - 1].Thickness) - FracC
                Comp[Compi - 1].Theta = Comp[Compi - 1].Theta + FracC * float(LayVolPr[Layeri - 1]) / 100.0
                Comp[Compi - 1].WFactor = Comp[Compi - 1].WFactor + FracC * float(LayECdS[Layeri - 1])

                FracC = (SDLay - (SDComp - float(Comp[Compi - 1].Thickness))) / float(Comp[Compi - 1].Thickness)

                # add next layer
                if Layeri < NrLay:
                    Layeri += 1
                    SDLay += float(LayThickness[Layeri - 1])
                else:
                    GoOn = False

            Comp[Compi - 1].Theta = Comp[Compi - 1].Theta + (1.0 - FracC) * float(LayVolPr[Layeri - 1]) / 100.0
            Comp[Compi - 1].WFactor = Comp[Compi - 1].WFactor + (1.0 - FracC) * float(LayECdS[Layeri - 1])

        # next Compartment

    if not GoOn:
        for i in range(Compi + 1, int(NrComp) + 1):
            Comp[i - 1].Theta = float(LayVolPr[NrLay - 1]) / 100.0
            Comp[i - 1].WFactor = float(LayECdS[NrLay - 1])

    # final check of SWC
    for Compi in range(1, int(NrComp) + 1):
        if Comp[Compi - 1].Theta > (GetSoilLayer_SAT(Comp[Compi - 1].Layer)) / 100.0:
            Comp[Compi - 1].Theta = (GetSoilLayer_SAT(Comp[Compi - 1].Layer)) / 100.0

    # salt distribution in cellls
    for Compi in range(1, int(NrComp) + 1):
        DetermineSaltContent(Comp[Compi - 1].WFactor, Comp[Compi - 1])

    return Comp



def AdjustThetaInitial(
    PrevNrComp: int,
    PrevThickComp,
    PrevVolPrComp,
    PrevECdSComp,
):
    layeri = 0
    compi = 0
    TotDepthC = 0.0
    TotDepthL = 0.0
    Total = 0.0

    # 1. Actual total depth of compartments
    TotDepthC = 0.0
    for compi in range(1, GetNrCompartments() + 1):
        TotDepthC += GetCompartment_Thickness(compi)

    # 2. Stretch thickness of bottom soil layer if required
    TotDepthL = 0.0
    for layeri in range(1, GetSoil_NrSoilLayers() + 1):
        TotDepthL += GetSoilLayer_Thickness(layeri)

    if TotDepthC > TotDepthL:
        last_layer = int(GetSoil_NrSoilLayers())
        SetSoilLayer_Thickness(
            last_layer,
            GetSoilLayer_Thickness(last_layer) + (TotDepthC - TotDepthL),
        )

    # 3. Assign a soil layer to each soil compartment
    Compartment_temp = GetCompartment()
    tmp = DesignateSoilLayerToCompartments(
        GetNrCompartments(),
        int(GetSoil_NrSoilLayers()),
        Compartment_temp,
    )
    if tmp is not None:
        Compartment_temp = tmp
    SetCompartment(Compartment_temp)

    # 4. Adjust initial Soil Water Content of soil compartments
    if GetSimulation_ResetIniSWC():
        if GetSimulation_IniSWC_AtDepths():
            Compartment_temp = GetCompartment()
            tmp = TranslateIniPointsToSWProfile(
                GetSimulation_IniSWC_NrLoc(),
                GetSimulation_IniSWC_Loc(),
                GetSimulation_IniSWC_VolProc(),
                GetSimulation_IniSWC_SaltECe(),
                GetNrCompartments(),
                Compartment_temp,
            )

            if tmp is not None:
                Compartment_temp = tmp
            SetCompartment(Compartment_temp)
        else:
            Compartment_temp = GetCompartment()
            tmp = TranslateIniLayersToSWProfile(
                GetSimulation_IniSWC_NrLoc(),
                GetSimulation_IniSWC_Loc(),
                GetSimulation_IniSWC_VolProc(),
                GetSimulation_IniSWC_SaltECe(),
                GetNrCompartments(),
                Compartment_temp,
            )
            if tmp is not None:
                Compartment_temp = tmp
            SetCompartment(Compartment_temp)
    else:
        Compartment_temp = GetCompartment()
        tmp = TranslateIniLayersToSWProfile(
            PrevNrComp,
            PrevThickComp,
            PrevVolPrComp,
            PrevECdSComp,
            GetNrCompartments(),
            Compartment_temp,
        )
        if tmp is not None:
            Compartment_temp = tmp
        SetCompartment(Compartment_temp)

    # 5. Adjust watercontent in soil layers and determine ThetaIni
    Total = 0.0
    for layeri in range(1, GetSoil_NrSoilLayers() + 1):
        SetSoilLayer_WaterContent(layeri, 0.0)

    for compi in range(1, GetNrCompartments() + 1):
        SetSimulation_ThetaIni_i(compi, GetCompartment_theta(compi))

        layer = GetCompartment_Layer(compi)
        SetSoilLayer_WaterContent(
            layer,
            GetSoilLayer_WaterContent(layer)
            + GetSimulation_ThetaIni_i(compi) * 100.0 * 10.0 * GetCompartment_Thickness(compi),
        )

    for layeri in range(1, GetSoil_NrSoilLayers() + 1):
        Total += GetSoilLayer_WaterContent(layeri)

    SetTotalWaterContent_BeginDay(Total)

def TranslateIniPointsToSWProfile(
    NrLoc: int,
    LocDepth,
    LocVolPr,
    LocECdS,
    NrComp: int,
    Comp,
):
    # Mirrors Fortran logic. Comp is assumed to be a normal Python list (0-based),
    # so any Fortran access Comp(Compi) becomes Comp[Compi-1].

    Compi = 0
    Loci = 0

    TotD = 0.0

    # TotD = 0
    # do Compi = 1, NrComp
    for Compi1 in range(1, NrComp + 1):
        c = Comp[Compi1 - 1]
        c.Theta = 0.0
        c.WFactor = 0.0  # used for salt in (10*VolSat*dZ * EC)
        TotD += c.Thickness

    Compi = 0
    Depthi = 0.0
    AddComp = True

    # Th2 = LocVolPr(1)
    Th2 = float(LocVolPr[0])

    # EC2 = LocECds(1)
    EC2 = float(LocECdS[0])

    D2 = 0.0
    Loci = 0

    # do while ((Compi < NrComp) .or. ((Compi == NrComp) .and. (AddComp .eqv. .false.)))
    while (Compi < NrComp) or ((Compi == NrComp) and (AddComp is False)):

        # upper and lower boundaries location
        D1 = D2
        Th1 = Th2
        EC1 = EC2

        if Loci < NrLoc:
            Loci += 1
            D2  = float(LocDepth[Loci - 1])
            Th2 = float(LocVolPr[Loci - 1])
            EC2 = float(LocECdS[Loci - 1])
        else:
            D2 = TotD

        # transfer water to compartment (SWC in mm) and salt in (10*VolSat*dZ * EC)
        TheEnd = False
        DTopComp = D1  # Depthi is the bottom depth
        ThBotComp = Th1
        ECBotComp = EC1

        while True:
            ThTopComp = ThBotComp
            ECTopComp = ECBotComp

            if AddComp:
                Compi += 1
                Depthi += Comp[Compi - 1].Thickness

            if Depthi < D2:
                # ThBotComp = Th1 + (Th2-Th1)*(Depthi-D1)/real(D2-D1, kind=dp)
                denom = (D2 - D1)
                ThBotComp = Th1 + (Th2 - Th1) * (Depthi - D1) / denom

                # Comp(Compi)%Theta = Comp(Compi)%Theta + 10*(Depthi-DTopComp)*((ThTopComp+ThBotComp)/2)
                c = Comp[Compi - 1]
                c.Theta = c.Theta + 10.0 * (Depthi - DTopComp) * ((ThTopComp + ThBotComp) / 2.0)

                # ECBotComp = EC1 + (EC2-EC1)*(Depthi-D1)/real(D2-D1, kind=dp)
                ECBotComp = EC1 + (EC2 - EC1) * (Depthi - D1) / denom

                # Comp(Compi)%WFactor = Comp(Compi)%WFactor + (10*(Depthi-DTopComp)*SAT(layer))*((ECTopComp+ECBotComp)/2)
                c.WFactor = c.WFactor + (
                    10.0 * (Depthi - DTopComp) * GetSoilLayer_SAT(c.Layer)
                ) * ((ECTopComp + ECBotComp) / 2.0)

                AddComp = True
                DTopComp = Depthi
                if Compi == NrComp:
                    TheEnd = True
            else:
                ThBotComp = Th2
                ECBotComp = EC2

                c = Comp[Compi - 1]
                c.Theta = c.Theta + 10.0 * (D2 - DTopComp) * ((ThTopComp + ThBotComp) / 2.0)
                c.WFactor = c.WFactor + (
                    10.0 * (D2 - DTopComp) * GetSoilLayer_SAT(c.Layer)
                ) * ((ECTopComp + ECBotComp) / 2.0)

                if abs(Depthi - D2) < float_info.epsilon:
                    AddComp = True
                else:
                    AddComp = False

                TheEnd = True

            if TheEnd:
                break

    # do Compi = 1, NrComp
    for Compi1 in range(1, NrComp + 1):
        c = Comp[Compi1 - 1]

        # from mm(water) to theta and final check
        c.Theta = c.Theta / (1000.0 * c.Thickness)

        sat_theta = GetSoilLayer_SAT(c.Layer) / 100.0
        if c.Theta > sat_theta:
            c.Theta = sat_theta
        if c.Theta < 0.0:
            c.Theta = 0.0

    # do Compi = 1, NrComp
    for Compi1 in range(1, NrComp + 1):
        c = Comp[Compi1 - 1]

        # from (10*VolSat*dZ * EC) to ECe and distribution in cellls
        c.WFactor = c.WFactor / (10.0 * c.Thickness * GetSoilLayer_SAT(c.Layer))
        DetermineSaltContent(c.WFactor, c)

    return Comp

def SaltSolutionDeposit(mm: float, SaltSolution: float, SaltDeposit: float):
    # mm = l/m2, SaltSolution/SaltDeposit = g/m2
    SaltSolution = SaltSolution + SaltDeposit

    if SaltSolution > (GetSimulParam_SaltSolub() * mm):
        SaltDeposit = SaltSolution - (GetSimulParam_SaltSolub() * mm)
        SaltSolution = GetSimulParam_SaltSolub() * mm
    else:
        SaltDeposit = 0.0

    return SaltSolution, SaltDeposit

def DetermineSaltContent(ECe: float, Comp):
    TotSalt = (
        ECe
        * Equiv
        * GetSoilLayer_SAT(Comp.Layer)
        * 10.0
        * Comp.Thickness
    )

    celn = ActiveCells(Comp)

    SAT = GetSoilLayer_SAT(Comp.Layer) / 100.0  # m3/m3
    UL = GetSoilLayer_UL(Comp.Layer)            # m3/m3
    Dx = GetSoilLayer_Dx(Comp.Layer)            # m3/m3

    gravel_fac = 1.0 - (GetSoilLayer_GravelVol(Comp.Layer) / 100.0)

    # volume [mm]=[l/m2] of cells
    mm1 = Dx * 1000.0 * Comp.Thickness * gravel_fac
    mmN = (SAT - UL) * 1000.0 * Comp.Thickness * gravel_fac

    SumDF = 0.0
    scp1 = int(GetSoilLayer_SCP1(Comp.Layer))

    for i in range(1, scp1 + 1):
        Comp.Salt[i - 1] = 0.0
        Comp.Depo[i - 1] = 0.0

    for i in range(1, celn + 1):
        SumDF += GetSoilLayer_SaltMobility_i(Comp.Layer, i)

    if SumDF == 0.0:
        return

    for i in range(1, celn + 1):
        Comp.Salt[i - 1] = TotSalt * GetSoilLayer_SaltMobility_i(Comp.Layer, i) / SumDF

        mm = mm1
        if i == scp1:
            mm = mmN

        res = SaltSolutionDeposit(mm, Comp.Salt[i - 1], Comp.Depo[i - 1])

        # Soporta implementaciones que devuelvan Depo o (Salt, Depo)
        if isinstance(res, tuple):
            if len(res) >= 2:
                Comp.Salt[i - 1], Comp.Depo[i - 1] = res[0], res[1]
            elif len(res) == 1:
                Comp.Depo[i - 1] = res[0]
        elif res is not None:
            Comp.Depo[i - 1] = res


def ActiveCells(Comp) -> int:
    if Comp.Theta <= GetSoilLayer_UL(Comp.Layer):
        celi = 1
        while Comp.Theta > (GetSoilLayer_Dx(Comp.Layer) * celi):
            celi += 1
    else:
        celi = GetSoilLayer_SCP1(Comp.Layer)

    return celi


def LoadCrop(FullName):
    fhandle = 0
    XX = 0
    YY = 0
    VersionNr = 0.0
    TempShortInt = 0
    perenperiod_onsetOcc_temp = 0
    perenperiod_endOcc_temp = 0
    TempInt = 0
    perenperiod_onsetFD_temp = 0
    perenperiod_onsetFM_temp = 0
    perenperiod_onsetLSP_temp = 0
    perenperiod_onsetPV_temp = 0
    perenperiod_endLD_temp = 0
    perenperiod_endLM_temp = 0
    perenperiod_extrayears_temp = 0
    perenperiod_endLSP_temp = 0
    perenperiod_endPV_temp = 0
    TempDouble = 0.0
    TempBoolean = False
    perenperiod_onsetTV_temp = 0.0
    perenperiod_endTV_temp = 0.0
    Crop_SmaxTop_temp = 0.0
    Crop_SmaxBot_temp = 0.0
    CropDescriptionLocal = ""
    
    full_path = ResolvePath(FullName)

    # bulk read (record-based)
    #with open(full_path, "r", encoding="utf-8") as f:
    with open(full_path, "r", encoding="cp1252") as f:
        lines = f.read().splitlines()

    idx = 0

    def _next_record():
        nonlocal idx
        if idx >= len(lines):
            return None
        s = lines[idx]
        idx += 1
        return s

    def _skip_record():
        _ = _next_record()

    def _read_str_a():
        s = _next_record()
        if s is None:
            raise EOFError("Unexpected EOF while reading string record")
        return s

    def _read_int():
        s = _next_record()
        if s is None:
            raise EOFError("Unexpected EOF while reading int record")
        parts = s.strip().split()
        if len(parts) == 0:
            raise ValueError("Empty record while reading int")
        return int(parts[0])

    def _read_float():
        s = _next_record()
        if s is None:
            raise EOFError("Unexpected EOF while reading float record")
        parts = s.strip().split()
        if len(parts) == 0:
            raise ValueError("Empty record while reading float")
        return float(parts[0])

    # read description
    CropDescriptionLocal = _read_str_a()
    SetCropDescription(CropDescriptionLocal.strip())

    # AquaCrop version
    VersionNr = _read_float()

    # Protected or Open file (skip record)
    _skip_record()

    # subkind
    XX = _read_int()
    if XX == 1:
        SetCrop_subkind(subkind_Vegetative)
    elif XX == 2:
        SetCrop_subkind(subkind_Grain)
    elif XX == 3:
        SetCrop_subkind(subkind_Tuber)
    elif XX == 4:
        SetCrop_subkind(subkind_Forage)

    # type of planting
    XX = _read_int()
    if XX == 1:
        SetCrop_Planting(plant_Seed)
    elif XX == 0:
        SetCrop_Planting(plant_transplant)
    elif XX == -9:
        SetCrop_Planting(plant_regrowth)
    else:
        SetCrop_Planting(plant_Seed)

    # mode
    XX = _read_int()
    if XX == 0:
        SetCrop_ModeCycle(ModeCycle_GDDays)
    else:
        SetCrop_ModeCycle(ModeCycle_CalendarDays)

    # adjustment p to ETo
    YY = _read_int()
    if YY == 0:
        SetCrop_pMethod(pMethod_NoCorrection)
    elif YY == 1:
        SetCrop_pMethod(pMethod_FAOCorrection)

    # temperatures controlling crop development
    TempDouble = _read_float()
    SetCrop_Tbase(TempDouble)
    TempDouble = _read_float()
    SetCrop_Tupper(TempDouble)

    # required growing degree days to complete the crop cycle
    TempInt = _read_int()
    SetCrop_GDDaysToHarvest(TempInt)

    # water stress
    TempDouble = _read_float()
    SetCrop_pLeafDefUL(TempDouble)
    TempDouble = _read_float()
    SetCrop_pLeafDefLL(TempDouble)
    TempDouble = _read_float()
    SetCrop_KsShapeFactorLeaf(TempDouble)
    TempDouble = _read_float()
    SetCrop_pdef(TempDouble)
    TempDouble = _read_float()
    SetCrop_KsShapeFactorStomata(TempDouble)
    TempDouble = _read_float()
    SetCrop_pSenescence(TempDouble)
    TempDouble = _read_float()
    SetCrop_KsShapeFactorSenescence(TempDouble)
    TempInt = _read_int()
    SetCrop_SumEToDelaySenescence(TempInt)
    TempDouble = _read_float()
    SetCrop_pPollination(TempDouble)
    TempInt = _read_int()
    SetCrop_AnaeroPoint(TempInt)

    # soil fertility/salinity stress
    TempShortInt = _read_int()
    SetCrop_StressResponse_Stress(TempShortInt)
    TempDouble = _read_float()
    SetCrop_StressResponse_ShapeCGC(TempDouble)
    TempDouble = _read_float()
    SetCrop_StressResponse_ShapeCCX(TempDouble)
    TempDouble = _read_float()
    SetCrop_StressResponse_ShapeWP(TempDouble)
    TempDouble = _read_float()
    SetCrop_StressResponse_ShapeCDecline(TempDouble)

    # ----- Version 7.3 Replacement of dummy by Premature end of annual
    # crops when too cold to reach maturity (Version 7.3)
    if roundc(VersionNr * 10.0, mold="int32") <= 72:
        SetCrop_PrematureEnd(undef_int)  # not implemented for earlier versions
        TempInt = _read_int()  # just for skipping this line
    else:
        # PrematureEnd: daynumber counting from 1 January of planting year
        TempInt = _read_int()
        SetCrop_PrematureEnd(TempInt)

    # continue with soil fertility/salinity stress
    if (
        (GetCrop_StressResponse_ShapeCGC() > 24.9)
        and (GetCrop_StressResponse_ShapeCCX() > 24.9)
        and (GetCrop_StressResponse_ShapeWP() > 24.9)
        and (GetCrop_StressResponse_ShapeCDecline() > 24.9)
    ):
        SetCrop_StressResponse_Calibrated(False)
    else:
        SetCrop_StressResponse_Calibrated(True)

    # temperature stress
    TempShortInt = _read_int()
    SetCrop_Tcold(TempShortInt)
    TempShortInt = _read_int()
    SetCrop_Theat(TempShortInt)
    TempDouble = _read_float()
    SetCrop_GDtranspLow(TempDouble)

    # salinity stress (Version 3.2 and higher)
    if roundc(VersionNr * 10.0, mold="int32") < 32:
        SetCrop_ECemin(2)
        SetCrop_ECemax(15)
    else:
        TempShortInt = _read_int()
        SetCrop_ECemin(TempShortInt)
        TempShortInt = _read_int()
        SetCrop_ECemax(TempShortInt)
        _skip_record()  # WAS shape factor (skip)

    # UPDATE salinity stress (Version 5.1 and higher)
    if roundc(VersionNr * 10.0, mold="int32") < 51:
        SetCrop_CCsaltDistortion(25)
        SetCrop_ResponseECsw(100)
    else:
        TempShortInt = _read_int()
        SetCrop_CCsaltDistortion(TempShortInt)
        TempInt = _read_int()
        SetCrop_ResponseECsw(TempInt)

    # evapotranspiration
    TempDouble = _read_float()
    SetCrop_KcTop(TempDouble)
    
    TempDouble = _read_float()
    if roundc(VersionNr * 10.0, mold=1) <= 72:
        # skip line with KcDecline (%/day)
        # specify default value for cumulative decrease (%) at maturity of crop coefficient due to ageing
        SetCrop_KcDeclineCumul(11.0)
    else:
        SetCrop_KcDeclineCumul(TempDouble)

    TempDouble = _read_float()
    SetCrop_RootMin(TempDouble)
    TempDouble = _read_float()
    SetCrop_RootMax(TempDouble)
    if GetCrop_RootMin() > GetCrop_RootMax():
        SetCrop_RootMin(GetCrop_RootMax())

    TempShortInt = _read_int()
    SetCrop_RootShape(TempShortInt)

    TempDouble = _read_float()
    SetCrop_SmaxTopQuarter(TempDouble)
    TempDouble = _read_float()
    SetCrop_SmaxBotQuarter(TempDouble)

    Crop_SmaxTop_temp = GetCrop_SmaxTop()
    Crop_SmaxBot_temp = GetCrop_SmaxBot()
    Crop_SmaxTop_temp, Crop_SmaxBot_temp = DeriveSmaxTopBottom(
        GetCrop_SmaxTopQuarter(),
        GetCrop_SmaxBotQuarter(),
        Crop_SmaxTop_temp,
        Crop_SmaxBot_temp,
    )
    SetCrop_SmaxTop(Crop_SmaxTop_temp)
    SetCrop_SmaxBot(Crop_SmaxBot_temp)

    TempInt = _read_int()
    SetCrop_CCEffectEvapLate(TempInt)

    # crop development
    TempDouble = _read_float()
    SetCrop_SizeSeedling(TempDouble)

    if roundc(VersionNr * 10.0, mold="int32") < 50:
        SetCrop_SizePlant(GetCrop_SizeSeedling())
    else:
        TempDouble = _read_float()
        SetCrop_SizePlant(TempDouble)

    TempInt = _read_int()
    SetCrop_PlantingDens(TempInt)

    SetCrop_CCo((GetCrop_PlantingDens() / 10000.0) * (GetCrop_SizeSeedling() / 10000.0))
    SetCrop_CCini((GetCrop_PlantingDens() / 10000.0) * (GetCrop_SizePlant() / 10000.0))

    TempDouble = _read_float()
    SetCrop_CGC(TempDouble)

    TempShortInt = _read_int()
    SetCrop_YearCCx(TempShortInt)

    TempDouble = _read_float()
    SetCrop_CCxRoot(TempDouble)

    _skip_record()  # skip record

    TempDouble = _read_float()
    SetCrop_CCx(TempDouble)
    TempDouble = _read_float()
    SetCrop_CDC(TempDouble)
    TempInt = _read_int()
    SetCrop_DaysToGermination(TempInt)
    TempInt = _read_int()
    SetCrop_DaysToMaxRooting(TempInt)
    TempInt = _read_int()
    SetCrop_DaysToSenescence(TempInt)
    TempInt = _read_int()
    SetCrop_DaysToHarvest(TempInt)
    TempInt = _read_int()
    SetCrop_DaysToFlowering(TempInt)
    TempInt = _read_int()
    SetCrop_LengthFlowering(TempInt)

    if (GetCrop_subkind() == subkind_Vegetative) or (GetCrop_subkind() == subkind_Forage):
        SetCrop_DaysToFlowering(0)
        SetCrop_LengthFlowering(0)

    # Crop.DeterminancyLinked
    XX = _read_int()
    if XX == 1:
        SetCrop_DeterminancyLinked(True)
    else:
        SetCrop_DeterminancyLinked(False)

    # Potential excess of fruits (%) and building up HI
    if (GetCrop_subkind() == subkind_Vegetative) or (GetCrop_subkind() == subkind_Forage):
        _skip_record()  # PercCycle no longer considered
        SetCrop_fExcess(int(undef_int))
    else:
        TempInt = _read_int()
        SetCrop_fExcess(int(TempInt))

    TempInt = _read_int()
    SetCrop_DaysToHIo(TempInt)

    # yield response to water
    TempDouble = _read_float()
    SetCrop_WP(TempDouble)
    TempInt = _read_int()
    SetCrop_WPy(TempInt)

    # adaptation to elevated CO2 (Version 3.2 and higher)
    if roundc(VersionNr * 10.0, mold="int32") < 32:
        SetCrop_AdaptedToCO2(50)
    else:
        TempShortInt = _read_int()
        SetCrop_AdaptedToCO2(TempShortInt)

    TempInt = _read_int()
    SetCrop_HI(TempInt)

    TempShortInt = _read_int()
    SetCrop_HIincrease(TempShortInt)

    TempDouble = _read_float()
    SetCrop_aCoeff(TempDouble)
    TempDouble = _read_float()
    SetCrop_bCoeff(TempDouble)

    TempShortInt = _read_int()
    SetCrop_DHImax(TempShortInt)

    if (
        (roundc(VersionNr * 10.0, mold="int32") == 30)
        and ((GetCrop_subkind() == subkind_Vegetative) or (GetCrop_subkind() == subkind_Forage))
    ):
        if GetCrop_HI() == undef_int:
            SetCrop_HI(85)

    # growing degree days
    TempInt = _read_int()
    SetCrop_GDDaysToGermination(TempInt)
    TempInt = _read_int()
    SetCrop_GDDaysToMaxRooting(TempInt)
    TempInt = _read_int()
    SetCrop_GDDaysToSenescence(TempInt)
    TempInt = _read_int()
    SetCrop_GDDaysToHarvest(TempInt)
    TempInt = _read_int()
    SetCrop_GDDaysToFlowering(TempInt)
    TempInt = _read_int()
    SetCrop_GDDLengthFlowering(TempInt)
    TempDouble = _read_float()
    SetCrop_GDDCGC(TempDouble)
    TempDouble = _read_float()
    SetCrop_GDDCDC(TempDouble)
    TempInt = _read_int()
    SetCrop_GDDaysToHIo(TempInt)

    if (
        (GetCrop_ModeCycle() == ModeCycle_GDDays)
        and ((GetCrop_subkind() == subkind_Vegetative) or (GetCrop_subkind() == subkind_Forage))
    ):
        SetCrop_GDDaysToFlowering(0)
        SetCrop_GDDLengthFlowering(0)

    # extra version 6.2
    if roundc(VersionNr * 10.0, mold="int32") < 62:
        SetCrop_DryMatter(int(undef_int))
    else:
        TempShortInt = _read_int()
        SetCrop_DryMatter(TempShortInt)

    # extra version 7.0
    if roundc(VersionNr * 10.0, mold="int32") < 62:
        SetCrop_RootMinYear1(GetCrop_RootMin())
        TempBoolean = (GetCrop_Planting() == plant_Seed)
        SetCrop_SownYear1(TempBoolean)
        SetCrop_Assimilates_On(False)
        SetCrop_Assimilates_Period(0)
        SetCrop_Assimilates_Stored(0)
        SetCrop_Assimilates_Mobilized(0)
    else:
        TempDouble = _read_float()
        SetCrop_RootMinYear1(TempDouble)

        XX = _read_int()
        if XX == 1:
            SetCrop_SownYear1(True)
        else:
            SetCrop_SownYear1(False)

        XX = _read_int()
        if XX == 1:
            SetCrop_Assimilates_On(True)
        else:
            SetCrop_Assimilates_On(False)

        TempInt = _read_int()
        SetCrop_Assimilates_Period(TempInt)

        TempShortInt = _read_int()
        SetCrop_Assimilates_Stored(TempShortInt)

        TempShortInt = _read_int()
        SetCrop_Assimilates_Mobilized(TempShortInt)

    if GetCrop_subkind() == subkind_Forage:
        # 1. Title
        for _ in range(1, 3 + 1):
            _skip_record()

        # 2. ONSET
        XX = _read_int()
        if XX == 0:
            SetPerennialPeriod_GenerateOnset(False)
        else:
            SetPerennialPeriod_GenerateOnset(True)
            if XX == 12:
                SetPerennialPeriod_OnsetCriterion(AirTCriterion_TMeanPeriod)
            elif XX == 13:
                SetPerennialPeriod_OnsetCriterion(AirTCriterion_GDDPeriod)
            else:
                SetPerennialPeriod_GenerateOnset(False)

        perenperiod_onsetFD_temp = _read_int()
        SetPerennialPeriod_OnsetFirstDay(perenperiod_onsetFD_temp)

        perenperiod_onsetFM_temp = _read_int()
        SetPerennialPeriod_OnsetFirstMonth(perenperiod_onsetFM_temp)

        perenperiod_onsetLSP_temp = _read_int()
        SetPerennialPeriod_OnsetLengthSearchPeriod(perenperiod_onsetLSP_temp)

        perenperiod_onsetTV_temp = _read_float()
        SetPerennialPeriod_OnsetThresholdValue(perenperiod_onsetTV_temp)

        perenperiod_onsetPV_temp = _read_int()
        SetPerennialPeriod_OnsetPeriodValue(perenperiod_onsetPV_temp)

        perenperiod_onsetOcc_temp = _read_int()
        SetPerennialPeriod_OnsetOccurrence(perenperiod_onsetOcc_temp)

        if GetPerennialPeriod_OnsetOccurrence() > 3:
            SetPerennialPeriod_OnsetOccurrence(3)

        # 3. END of growing period
        XX = _read_int()
        if XX == 0:
            SetPerennialPeriod_GenerateEnd(False)
        else:
            SetPerennialPeriod_GenerateEnd(True)
            if XX == 62:
                SetPerennialPeriod_EndCriterion(AirTCriterion_TMeanPeriod)
            elif XX == 63:
                SetPerennialPeriod_EndCriterion(AirTCriterion_GDDPeriod)
            else:
                SetPerennialPeriod_GenerateEnd(False)

        perenperiod_endLD_temp = _read_int()
        SetPerennialPeriod_EndLastDay(perenperiod_endLD_temp)

        perenperiod_endLM_temp = _read_int()
        SetPerennialPeriod_EndLastMonth(perenperiod_endLM_temp)

        perenperiod_extrayears_temp = _read_int()
        SetPerennialPeriod_ExtraYears(perenperiod_extrayears_temp)

        perenperiod_endLSP_temp = _read_int()
        SetPerennialPeriod_EndLengthSearchPeriod(perenperiod_endLSP_temp)

        perenperiod_endTV_temp = _read_float()
        SetPerennialPeriod_EndThresholdValue(perenperiod_endTV_temp)

        perenperiod_endPV_temp = _read_int()
        SetPerennialPeriod_EndPeriodValue(perenperiod_endPV_temp)

        perenperiod_endOcc_temp = _read_int()
        SetPerennialPeriod_EndOccurrence(perenperiod_endOcc_temp)

        if GetPerennialPeriod_EndOccurrence() > 3:
            SetPerennialPeriod_EndOccurrence(3)

    # close(fhandle)  -> handled by context manager already

    # maximum rooting depth in given soil profile
    SetSoil_RootMax(
        RootMaxInSoilProfile(
            GetCrop_RootMax(),
            GetSoil_NrSoilLayers(),
            GetSoilLayer(),
        )
    )

    # copy to CropFileSet
    SetCropFileSet_DaysFromSenescenceToEnd(GetCrop_DaysToHarvest() - GetCrop_DaysToSenescence())
    SetCropFileSet_DaysToHarvest(GetCrop_DaysToHarvest())

    if GetCrop_ModeCycle() == ModeCycle_GDDays:
        SetCropFileSet_GDDaysFromSenescenceToEnd(GetCrop_GDDaysToHarvest() - GetCrop_GDDaysToSenescence())
        SetCropFileSet_GDDaysToHarvest(GetCrop_GDDaysToHarvest())
    else:
        SetCropFileSet_GDDaysFromSenescenceToEnd(undef_int)
        SetCropFileSet_GDDaysToHarvest(undef_int)


def DeriveSmaxTopBottom(SxTopQ: float, SxBotQ: float, SxTop: float, SxBot: float):
    V1 = SxTopQ
    V2 = SxBotQ

    if abs(V1 - V2) < 1e-12:
        SxTop = V1
        SxBot = V2
    else:
        if SxTopQ < SxBotQ:
            V1 = SxBotQ
            V2 = SxTopQ

        x = 3.0 * V2 / (V1 - V2)

        if x < 0.5:
            V11 = (4.0 / 3.5) * V1
            V22 = 0.0
        else:
            V11 = (x + 3.5) * V1 / (x + 3.0)
            V22 = (x - 0.5) * V2 / x

        if SxTopQ > SxBotQ:
            SxTop = V11
            SxBot = V22
        else:
            SxTop = V22
            SxBot = V11

    return SxTop, SxBot

def DegreesDay(
    Tbase: float,
    Tupper: float,
    TDayMin: float,
    TDayMax: float,
    GDDSelectedMethod: int,
) -> float:
    TstarMax = 0.0
    TstarMin = 0.0
    Tavg = 0.0
    DgrD = 0.0

    if GDDSelectedMethod == 1:
        # Method 1. - No adjustment of Tmax, Tmin before calculation of Taverage
        Tavg = (TDayMax + TDayMin) / 2.0
        if Tavg > Tupper:
            Tavg = Tupper
        if Tavg < Tbase:
            Tavg = Tbase

    elif GDDSelectedMethod == 2:
        # Method 2. - Adjustment for Tbase before calculation of Taverage
        TstarMax = TDayMax
        if TDayMax < Tbase:
            TstarMax = Tbase
        if TDayMax > Tupper:
            TstarMax = Tupper

        TstarMin = TDayMin
        if TDayMin < Tbase:
            TstarMin = Tbase
        if TDayMin > Tupper:
            TstarMin = Tupper

        Tavg = (TstarMax + TstarMin) / 2.0

    else:
        # Method 3. (default)
        TstarMax = TDayMax
        if TDayMax < Tbase:
            TstarMax = Tbase
        if TDayMax > Tupper:
            TstarMax = Tupper

        TstarMin = TDayMin
        if TDayMin > Tupper:
            TstarMin = Tupper

        Tavg = (TstarMax + TstarMin) / 2.0
        if Tavg < Tbase:
            Tavg = Tbase

    DgrD = Tavg - Tbase

    return DgrD



def SplitStringInTwoParams(StringIN: str, Par1: float, Par2: float):
    LengthS = len(StringIN)
    i = 0
    Parami = 0

    # divide the line in parameters
    while (i < LengthS) and (Parami < 2):
        i += 1
        CharA = StringIN[i - 1]  # Fortran StringIN(i:i)

        if ord(CharA) > 32:
            # next Parameter
            Parami += 1
            StringNumber = ""

            while (ord(CharA) > 32) and (i <= LengthS):
                StringNumber = (StringNumber.strip() + CharA)
                i += 1
                if i <= LengthS:
                    CharA = StringIN[i - 1]

            if Parami == 1:
                Par1 = float(StringNumber)
            if Parami == 2:
                Par2 = float(StringNumber)

    return Par1, Par2

def LoadIrriScheduleInfo(FullName: str):
    global IrriDescription, IrriFirstDayNr, IrriInfoLastDay

    # Resolver ruta como en el resto del proyecto
    name = _strip_quotes(FullName).strip()
    if os.path.isabs(name):
        full_path = os.path.normpath(name)
    else:
        full_path = os.path.normpath(os.path.join(complete_path_dir, name.lstrip("/\\")))

    # 1 sola operación de lectura en disco
    with open(full_path, "r", encoding="utf-8") as fhandle:
        lines = fhandle.read().splitlines()

    pos = 0

    # read(fhandle, '(a)') IrriDescription
    IrriDescription = lines[pos].strip() if pos < len(lines) else ""
    pos += 1

    # read(fhandle, *) VersionNr
    VersionNr = float(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0.0
    pos += 1

    IrriInfoLastDay = undef_int

    # irrigation method: read i
    i = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0
    pos += 1

    if i == 1:
        SetIrriMethod(IrriMethod_MSprinkler)
    elif i == 2:
        SetIrriMethod(IrriMethod_MBasin)
    elif i == 3:
        SetIrriMethod(IrriMethod_MBorder)
    elif i == 4:
        SetIrriMethod(IrriMethod_MFurrow)
    else:
        SetIrriMethod(IrriMethod_MDrip)

    # fraction of soil surface wetted
    simul_irri_in = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0
    pos += 1
    SetSimulParam_IrriFwInSeason(simul_irri_in)

    # irrigation mode and parameters
    i = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0
    pos += 1
    if i == 0:
        SetIrriMode(IrriMode_NoIrri)  # rainfed
    elif i == 1:
        SetIrriMode(IrriMode_Manual)
    elif i == 2:
        SetIrriMode(IrriMode_Generate)
    else:
        SetIrriMode(IrriMode_Inet)

    # 1. Irrigation schedule
    if (i == 1) and (roundc(VersionNr * 10.0, mold="int32") >= 70):
        IrriFirstDayNr = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else undef_int
        pos += 1
    else:
        IrriFirstDayNr = undef_int  # start of growing period

    # 2. Generate
    if GetIrriMode() == IrriMode_Generate:
        i = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0
        pos += 1
        if i == 1:
            SetGenerateTimeMode(GenerateTimeMode_FixInt)
        elif i == 2:
            SetGenerateTimeMode(GenerateTimeMode_AllDepl)
        elif i == 3:
            SetGenerateTimeMode(GenerateTimeMode_AllRAW)
        elif i == 4:
            SetGenerateTimeMode(GenerateTimeMode_WaterBetweenBunds)
        else:
            SetGenerateTimeMode(GenerateTimeMode_AllRAW)

        i = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0
        pos += 1
        if i == 1:
            SetGenerateDepthMode(GenerateDepthMode_ToFC)
        else:
            SetGenerateDepthMode(GenerateDepthMode_FixDepth)

        if roundc(VersionNr * 10.0, mold="int32") >= 73:
            IrriInfoLastDay = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else undef_int
            pos += 1
        else:
            IrriInfoLastDay = undef_int  # start of growing period

        IrriFirstDayNr = undef_int  # start of growing period

    # 3. Net irrigation requirement
    if GetIrriMode() == IrriMode_Inet:
        simul_percraw = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0
        pos += 1
        SetSimulParam_PercRAW(simul_percraw)
        IrriFirstDayNr = undef_int  # start of growing period

def LoadManagement(FullName: str):
    i = 0
    VersionNr = 0.0
    TempShortInt = 0
    TempInt = 0
    TempDouble = 0.0
    mandescription_temp = ""

    # --- unified reading
    name = _strip_quotes(FullName).strip()
    full_path = os.path.normpath(
        os.path.join(complete_path_dir, name.lstrip("/\\"))
    )

    try:
        raw = open(full_path, "rb").read()
    except OSError:
        return

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode("cp1252")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")

    lines = text.splitlines()
    pos = 0

    def _next_line():
        nonlocal pos
        if pos >= len(lines):
            return ""
        s = lines[pos]
        pos += 1
        return s

    def _next_token(default=""):
        s = _next_line()
        parts = s.split()
        return parts[0] if parts else default

    # read '(a)' mandescription_temp
    mandescription_temp = _next_line()
    SetManDescription(mandescription_temp.strip())

    # VersionNr
    VersionNr = float(_next_token("0"))
    ver10 = int(roundc(VersionNr * 10.0, mold="int32"))

    # mulches
    TempShortInt = int(_next_token("0"))
    SetManagement_Mulch(TempShortInt)
    TempShortInt = int(_next_token("0"))
    SetManagement_EffectMulchInS(TempShortInt)

    # soil fertility
    TempInt = int(_next_token(str(undef_int)))
    SetManagement_FertilityStress(TempInt)

    EffectStress_temp = GetSimulation_EffectStress()
    _res = EffectStress_temp
    _res = CropStressParametersSoilFertility(
        GetCrop_StressResponse(),
        GetManagement_FertilityStress(),
        _res,
    )

    if _res is not None:
        EffectStress_temp = _res
    SetSimulation_EffectStress(EffectStress_temp)

    # soil bunds
    TempDouble = float(_next_token("0"))
    SetManagement_BundHeight(TempDouble)
    SetSimulation_SurfaceStorageIni(0.0)
    SetSimulation_ECStorageIni(0.0)

    # surface run-off
    i = int(_next_token("0"))
    if i == 1:
        SetManagement_RunoffOn(False)   # prevention of surface runoff
    else:
        SetManagement_RunoffOn(True)    # surface runoff is not prevented

    if ver10 < 50:
        SetManagement_CNcorrection(0)
    else:
        TempInt = int(_next_token("0"))
        SetManagement_CNcorrection(TempInt)

    # weed infestation
    if ver10 < 50:
        SetManagement_WeedRC(0)
        SetManagement_WeedDeltaRC(0)
        SetManagement_WeedShape(-0.01)
    else:
        TempShortInt = int(_next_token("0"))
        SetManagement_WeedRC(TempShortInt)
        if ver10 < 51:
            SetManagement_WeedDeltaRC(0)
        else:
            TempInt = int(_next_token("0"))
            SetManagement_WeedDeltaRC(TempInt)
        TempDouble = float(_next_token("0"))
        SetManagement_WeedShape(TempDouble)

    if ver10 < 70:
        SetManagement_WeedAdj(100)
    else:
        TempShortInt = int(_next_token("0"))
        SetManagement_WeedAdj(TempShortInt)

    # multiple cuttings
    if ver10 >= 70:
        i = int(_next_token("0"))  # Consider multiple cuttings
        if i == 0:
            SetManagement_Cuttings_Considered(False)
        else:
            SetManagement_Cuttings_Considered(True)

        TempInt = int(_next_token("0"))  # CC after cutting
        SetManagement_Cuttings_CCcut(TempInt)

        _ = _next_token("0")  # (parámetro ya no usado >= 7.1) Increase CGC after cutting

        TempInt = int(_next_token("0"))  # Day1 when generating cuttings
        SetManagement_Cuttings_Day1(TempInt)

        TempInt = int(_next_token(str(undef_int)))  # NrDays when generating cuttings
        SetManagement_Cuttings_NrDays(TempInt)

        i = int(_next_token("0"))  # Generate multiple cuttings
        if i == 1:
            SetManagement_Cuttings_Generate(True)
        else:
            SetManagement_Cuttings_Generate(False)

        i = int(_next_token("0"))  # Time criterion
        if i == 0:
            SetManagement_Cuttings_Criterion(TimeCuttings_NA)
        elif i == 1:
            SetManagement_Cuttings_Criterion(TimeCuttings_IntDay)
        elif i == 2:
            SetManagement_Cuttings_Criterion(TimeCuttings_IntGDD)
        elif i == 3:
            SetManagement_Cuttings_Criterion(TimeCuttings_DryB)
        elif i == 4:
            SetManagement_Cuttings_Criterion(TimeCuttings_DryY)
        elif i == 5:
            SetManagement_Cuttings_Criterion(TimeCuttings_FreshY)
        else:
            SetManagement_Cuttings_Criterion(TimeCuttings_NA)

        i = int(_next_token("0"))  # final harvest at maturity
        if i == 1:
            SetManagement_Cuttings_HarvestEnd(True)
        else:
            SetManagement_Cuttings_HarvestEnd(False)

        TempInt = int(_next_token(str(undef_int)))  # FirstDayNr of list of cuttings
        SetManagement_Cuttings_FirstDayNr(TempInt)

    else:
        SetManagement_Cuttings_Considered(False)
        SetManagement_Cuttings_CCcut(30)
        SetManagement_Cuttings_Day1(1)
        SetManagement_Cuttings_NrDays(undef_int)
        SetManagement_Cuttings_Generate(False)
        SetManagement_Cuttings_Criterion(TimeCuttings_NA)
        SetManagement_Cuttings_HarvestEnd(False)
        SetManagement_Cuttings_FirstDayNr(undef_int)


def LoadInitialConditions(SWCiniFileFull: str, IniSurfaceStorage: float):
    # IniSWCRead attribute of the function was removed to fix a
    # bug occurring when the function was called in TempProcessing.pas
    # Keep in mind that this could affect the graphical interface

    name = _strip_quotes(SWCiniFileFull).strip()
    if os.path.isabs(name):
        full_path = os.path.normpath(name)
    else:
        full_path = os.path.normpath(os.path.join(complete_path_dir, name.lstrip("/\\")))

    # One disk read
    with open(full_path, "r", encoding="utf-8", errors="replace") as fhandle:
        lines = fhandle.read().splitlines()

    pos = 0

    swcinidescr_temp = lines[pos] if pos < len(lines) else ""
    pos += 1
    SetSWCiniDescription(swcinidescr_temp)

    VersionNr = float(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0.0
    pos += 1

    if roundc(10.0 * VersionNr, mold="int32") < 41:
        SetSimulation_CCini(float(undef_int))
    else:
        CCini_temp = float(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0.0
        pos += 1
        SetSimulation_CCini(CCini_temp)

    if roundc(10.0 * VersionNr, mold="int32") < 41:
        SetSimulation_Bini(0.0)
    else:
        Bini_temp = float(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0.0
        pos += 1
        SetSimulation_Bini(Bini_temp)

    if roundc(10.0 * VersionNr, mold="int32") < 41:
        SetSimulation_Zrini(float(undef_int))
    else:
        Zrini_temp = float(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0.0
        pos += 1
        SetSimulation_Zrini(Zrini_temp)

    # read(fhandle, *) IniSurfaceStorage
    IniSurfaceStorage = float(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0.0
    pos += 1

    if roundc(10.0 * VersionNr, mold="int32") < 32:
        SetSimulation_ECStorageIni(0.0)
    else:
        ECStorageIni_temp = float(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0.0
        pos += 1
        SetSimulation_ECStorageIni(ECStorageIni_temp)

    i = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0
    pos += 1
    SetSimulation_IniSWC_AtDepths(i == 1)

    NrLoc_temp = int(lines[pos].split()[0]) if pos < len(lines) and lines[pos].strip() else 0
    pos += 1
    SetSimulation_IniSWC_NrLoc(NrLoc_temp)

    # skip 3 header lines
    pos += 3

    for i in range(1, GetSimulation_IniSWC_NrLoc() + 1):
        StringParam = lines[pos] if pos < len(lines) else ""
        pos += 1

        parts = StringParam.split()
        Loc_i_temp = float(parts[0]) if len(parts) > 0 else 0.0
        VolProc_i_temp = float(parts[1]) if len(parts) > 1 else 0.0

        if roundc(10.0 * VersionNr, mold="int32") < 32:
            SetSimulation_IniSWC_SaltECe_i(i, 0.0)
        else:
            SaltECe_i_temp = float(parts[2]) if len(parts) > 2 else 0.0
            SetSimulation_IniSWC_SaltECe_i(i, SaltECe_i_temp)

        SetSimulation_IniSWC_Loc_i(i, Loc_i_temp)
        SetSimulation_IniSWC_VolProc_i(i, VolProc_i_temp)

    SetSimulation_IniSWC_AtFC(False)
    return IniSurfaceStorage

def ECeComp(comp):
    vol_sat = GetSoilLayer_SAT(comp.Layer)
    tot_salt = 0.0

    for i in range(1, GetSoilLayer_SCP1(comp.Layer) + 1):
        tot_salt = tot_salt + comp.Salt[i - 1] + comp.Depo[i - 1]  # g/m2

    denominator = (
        vol_sat * 10.0
        * comp.Thickness
        * (1.0 - GetSoilLayer_GravelVol(comp.Layer) / 100.0)
    )
    tot_salt = tot_salt / denominator  # g/l

    if tot_salt > GetSimulParam_SaltSolub():
        tot_salt = GetSimulParam_SaltSolub()

    return tot_salt / Equiv  # dS/m


def CheckForWaterTableInProfile(DepthGWTmeter, ProfileComp, WaterTableInProfile):
    WaterTableInProfile = False
    Ztot = 0.0
    compi = 0

    if DepthGWTmeter >= 0.0:
        # groundwater table is present
        while (not WaterTableInProfile) and (compi < GetNrCompartments()):
            compi += 1
            Ztot += ProfileComp[compi - 1].Thickness
            Zi = Ztot - ProfileComp[compi - 1].Thickness / 2.0
            if Zi >= DepthGWTmeter:
                WaterTableInProfile = True

    return WaterTableInProfile

def CO2ForSimulationPeriod(FromDayNr: int, ToDayNr: int):
    i = 0
    Dayi = 0
    Monthi = 0
    FromYi = 0
    ToYi = 0
    rc = 0

    CO2From = 0.0
    CO2To = 0.0
    CO2a = 0.0
    CO2b = 0.0
    YearA = 0.0
    YearB = 0.0

    fhandle = None
    TempString = ""

    Dayi, Monthi, FromYi = DetermineDate(FromDayNr)
    Dayi, Monthi, ToYi = DetermineDate(ToDayNr)

    if (FromYi == 1901) or (ToYi == 1901):
        return float(CO2Ref)

    # Single disk read (bulk)
    name = _strip_quotes(GetCO2FileFull()).strip()
    if os.path.isabs(name):
        full_path = os.path.normpath(name)
    else:
        full_path = os.path.normpath(os.path.join(complete_path_dir, name.lstrip("/\\")))

    with open(full_path, "r", encoding="utf-8", errors="replace") as fhandle:
        lines = fhandle.read().splitlines()

    pos = 0

    # skip 3 header records (Description and Title)
    pos += 3

    # from year
    while pos < len(lines) and (lines[pos].strip() == ""):
        pos += 1
    TempString = lines[pos] if pos < len(lines) else ""
    pos += 1

    YearB, CO2b = SplitStringInTwoParams(TempString.strip(), 0.0, 0.0)
    if int(roundc(YearB, mold="int32")) >= FromYi:
        CO2From = CO2b
        YearA = YearB
        CO2a = CO2b
    else:
        while True:
            YearA = YearB
            CO2a = CO2b

            while pos < len(lines) and (lines[pos].strip() == ""):
                pos += 1
            if pos >= len(lines):
                # rc == iostat_end equivalent (no more records)
                break

            TempString = lines[pos]
            pos += 1
            YearB, CO2b = SplitStringInTwoParams(TempString.strip(), 0.0, 0.0)

            if int(roundc(YearB, mold="int32")) >= FromYi:
                break

        if FromYi > int(roundc(YearB, mold="int32")):
            CO2From = CO2b
        else:
            ya = int(roundc(YearA, mold="int32"))
            yb = int(roundc(YearB, mold="int32"))
            denom = float(yb - ya)
            if abs(denom) < 1e-12:
                CO2From = CO2b
            else:
                CO2From = CO2a + (CO2b - CO2a) * float(FromYi - ya) / denom

    # to year
    CO2To = CO2From
    if (ToYi > FromYi) and (ToYi > int(roundc(YearA, mold="int32"))):
        if int(roundc(YearB, mold="int32")) >= ToYi:
            ya = int(roundc(YearA, mold="int32"))
            yb = int(roundc(YearB, mold="int32"))
            denom = float(yb - ya)
            if abs(denom) < 1e-12:
                CO2To = CO2b
            else:
                CO2To = CO2a + (CO2b - CO2a) * float(ToYi - ya) / denom
        else:
            # only enter if we still can read more records
            while True:
                # if next read would be EOF -> rc == iostat_end
                while pos < len(lines) and (lines[pos].strip() == ""):
                    pos += 1
                if pos >= len(lines):
                    break

                YearA = YearB
                CO2a = CO2b

                TempString = lines[pos]
                pos += 1
                YearB, CO2b = SplitStringInTwoParams(TempString.strip(), 0.0, 0.0)

                if int(roundc(YearB, mold="int32")) >= ToYi:
                    break

            if ToYi > int(roundc(YearB, mold="int32")):
                CO2To = CO2b
            else:
                ya = int(roundc(YearA, mold="int32"))
                yb = int(roundc(YearB, mold="int32"))
                denom = float(yb - ya)
                if abs(denom) < 1e-12:
                    CO2To = CO2b
                else:
                    CO2To = CO2a + (CO2b - CO2a) * float(ToYi - ya) / denom

    return float((CO2From + CO2To) / 2.0)

def GetDaySwitchToLinear(HImax: int, dHIdt: float, HIGC: float):
    HIo = 1  # integer(int32), parameter :: HIo = 1

    tmax = int(roundc(HImax / dHIdt, mold="int32"))
    ti = 0
    HiM1 = float(HIo)

    if tmax > 0:
        while True:
            ti += 1
            HIi = (HIo * HImax) / (HIo + (HImax - HIo) * math.exp(-HIGC * ti))
            HIfinal = HIi + (tmax - ti) * (HIi - HiM1)
            HiM1 = HIi
            if (HIfinal > HImax) or (ti >= tmax):
                break
        tSwitch = ti - 1
    else:
        tSwitch = 0

    if tSwitch > 0:
        HIi = (HIo * HImax) / (HIo + (HImax - HIo) * math.exp(-HIGC * tSwitch))
    else:
        HIi = 0.0

    HIGClinear = (HImax - HIi) / (tmax - tSwitch)

    return tSwitch, HIGClinear

def HarvestIndexGrowthCoefficient(HImax: float, dHIdt: float) -> float:
    HIo = 1.0

    if HImax > HIo:
        t = HImax / dHIdt
        HIGC = 0.001
        HIGC = HIGC + 0.001
        HIvar = (HIo * HImax) / (HIo + (HImax - HIo) * math.exp(-HIGC * t))
        while HIvar <= (0.98 * HImax):
            HIGC = HIGC + 0.001
            HIvar = (HIo * HImax) / (HIo + (HImax - HIo) * math.exp(-HIGC * t))

        if HIvar >= HImax:
            HIGC = HIGC - 0.001
    else:
        HIGC = undef_int

    return HIGC

def SeasonalSumOfKcPot(
    TheDaysToCCini: int,
    TheGDDaysToCCini: int,
    L0: int,
    L12: int,
    L123: int,
    L1234: int,
    Lend: int,
    GDDL0: int,
    GDDL12: int,
    GDDL123: int,
    GDDL1234: int,
    CCo: float,
    CCx: float,
    CGC: float,
    GDDCGC: float,
    CDC: float,
    GDDCDC: float,
    KcTop: float,
    KcDeclAgeingCumul: float,
    CCeffectProcent: float,
    Tbase: float,
    Tupper: float,
    TDayMin: float,
    TDayMax: float,
    GDtranspLow: float,
    CO2i: float,
    TheModeCycle: int,
    ReferenceClimate: bool,
) -> float:

    EToStandard = 5

    SumGDD = float(undef_int)
    GDDi = 0.0
    SumKcPot = 0.0
    SumGDDforPlot = float(undef_int)
    SumGDDfromDay1 = 0.0
    Tndayi = 0.0
    Txdayi = 0.0
    CCi = 0.0
    CCxWitheredForB = 0.0
    TpotForB = 0.0
    EpotTotForB = 0.0
    CCinitial = 0.0
    DayFraction = float(undef_int)
    GDDayFraction = float(undef_int)
    DayCC = 0
    Tadj = 0
    GDDTadj = undef_int
    Dayi = 0
    rc = 0
    GrowthON = False
    i = 0

    # 1. Open Temperature file
    # (bulk read in Python: read TCrop*.SIM once and iterate in-memory)
    sim_pairs = None
    sim_idx = 0
    if (GetTemperatureFile() != "(None)") and (GetTemperatureFile() != "(External)"):
        sim_name = "TCropReference.SIM" if (ReferenceClimate is True) else "TCrop.SIM"
        base_sim = _strip_quotes(GetPathNameSimul()).strip()
        if os.path.isabs(base_sim):
            base_sim_dir = os.path.normpath(base_sim)
        else:
            base_sim_dir = os.path.normpath(os.path.join(complete_path_dir, base_sim.lstrip("/\\")))

        name = _strip_quotes(sim_name).strip()
        if os.path.isabs(name):
            full_path = os.path.normpath(name)
        else:
            full_path = os.path.normpath(os.path.join(base_sim_dir, name.lstrip("/\\")))

        with open(full_path, "r", encoding="utf-8", errors="replace") as fhandle:
            lines = fhandle.read().splitlines()

        sim_pairs = []
        for ln in lines:
            parts = ln.split()
            if len(parts) >= 2:
                try:
                    sim_pairs.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    pass

    # 2. Initialise global settings
    SetSimulation_DelayedDays(0)  # required for CalculateETpot
    SumKcPot = 0.0
    SumGDDforPlot = float(undef_int)
    SumGDD = float(undef_int)
    SumGDDfromDay1 = 0.0
    GrowthON = False
    GDDTadj = undef_int
    DayFraction = float(undef_int)
    GDDayFraction = float(undef_int)

    # 2.bis Initialise 1st day
    if TheDaysToCCini != 0:
        # regrowth
        if TheDaysToCCini == undef_int:
            # CCx on 1st day
            Tadj = L12 - L0
            if TheModeCycle == ModeCycle_GDDays:
                GDDTadj = GDDL12 - GDDL0
                SumGDD = float(GDDL12)
            CCinitial = CCx
        else:
            # CC on 1st day is < CCx
            Tadj = TheDaysToCCini
            DayCC = Tadj + L0
            if TheModeCycle == ModeCycle_GDDays:
                GDDTadj = TheGDDaysToCCini
                SumGDD = float(GDDL0 + TheGDDaysToCCini)
                SumGDDforPlot = SumGDD

            CCinitial = CanopyCoverNoStressSF(
                DayCC,
                L0,
                L123,
                L1234,
                GDDL0,
                GDDL123,
                GDDL1234,
                CCo,
                CCx,
                CGC,
                CDC,
                GDDCGC,
                GDDCDC,
                SumGDDforPlot,
                TheModeCycle,
                0,
                0,
            )

        # Time reduction for days between L12 and L123
        DayFraction = (L123 - L12) / float(Tadj + L0 + (L123 - L12))
        if TheModeCycle == ModeCycle_GDDays:
            GDDayFraction = (GDDL123 - GDDL12) / float(GDDTadj + GDDL0 + (GDDL123 - GDDL12))
    else:
        # sowing or transplanting
        Tadj = 0
        if TheModeCycle == ModeCycle_GDDays:
            GDDTadj = 0
            SumGDD = 0.0
        CCinitial = CCo

    # 3. Calculate Sum
    i = 0
    sim_idx = 0

    for Dayi in range(1, Lend + 1):
        # 3.1 calculate growing degrees for the day
        if GetTemperatureFile() == "(None)":
            GDDi = DegreesDay(Tbase, Tupper, TDayMin, TDayMax, GetSimulParam_GDDMethod())

        elif GetTemperatureFile() == "(External)":
            i += 1
            if i == len(GetTminCropReferenceRun()):
                i = 1

            Tndayi = float(GetTminCropReferenceRun_i(i))
            Txdayi = float(GetTmaxCropReferenceRun_i(i))
            GDDi = DegreesDay(Tbase, Tupper, Tndayi, Txdayi, GetSimulParam_GDDMethod())

        else:
            if not sim_pairs:
                raise RuntimeError("SeasonalSumOfKcPot: TCrop*.SIM could not be read (no valid data lines).")

            if sim_idx >= len(sim_pairs):
                if ReferenceClimate is True:
                    sim_idx = 0  # mimic reopen+read from start
                else:
                    raise RuntimeError("SeasonalSumOfKcPot: unexpected EOF in TCrop.SIM for non-reference climate.")

            Tndayi, Txdayi = sim_pairs[sim_idx]
            sim_idx += 1
            GDDi = DegreesDay(Tbase, Tupper, Tndayi, Txdayi, GetSimulParam_GDDMethod())

        if TheModeCycle == ModeCycle_GDDays:
            SumGDD += GDDi
            SumGDDfromDay1 += GDDi

        # 3.2 calculate CCi
        if GrowthON is False:
            # not yet canopy development
            CCi = 0.0
            DayCC = Dayi

            if TheDaysToCCini != 0:
                # regrowth on 1st day
                CCi = CCinitial
                GrowthON = True
            else:
                # wait for day of germination or recover of transplant
                if TheModeCycle == ModeCycle_CalendarDays:
                    if Dayi == (L0 + 1):
                        CCi = CCinitial
                        GrowthON = True
                else:
                    if SumGDD > GDDL0:
                        CCi = CCinitial
                        GrowthON = True
        else:
            if TheDaysToCCini == 0:
                DayCC = Dayi
            else:
                DayCC = Dayi + Tadj + L0  # adjusted time scale
                if DayCC > L1234:
                    DayCC = L1234  # special case where L123 > L1234

                if DayCC > L12:
                    if Dayi <= L123:
                        DayCC = L12 + int(roundc(DayFraction * (Dayi + Tadj + L0 - L12), mold="int32"))  # slow down
                    else:
                        DayCC = Dayi  # switch time scale

            if TheModeCycle == ModeCycle_GDDays:
                if TheGDDaysToCCini == 0:
                    SumGDDforPlot = SumGDDfromDay1
                else:
                    SumGDDforPlot = SumGDD
                    if SumGDDforPlot > GDDL1234:
                        SumGDDforPlot = float(GDDL1234)  # special case where L123 > L1234

                    if SumGDDforPlot > GDDL12:
                        if SumGDDfromDay1 <= GDDL123:
                            SumGDDforPlot = float(
                                GDDL12
                                + roundc(
                                    GDDayFraction * (SumGDDfromDay1 + GDDTadj + GDDL0 - GDDL12),
                                    mold="int32",
                                )
                            )  # slow down
                        else:
                            SumGDDforPlot = SumGDDfromDay1  # switch time scale


            CCi = CanopyCoverNoStressSF(
                DayCC,
                L0,
                L123,
                L1234,
                GDDL0,
                GDDL123,
                GDDL1234,
                CCo,
                CCx,
                CGC,
                CDC,
                GDDCGC,
                GDDCDC,
                SumGDDforPlot,
                TheModeCycle,
                0,
                0,
            )

        # 3.3 calculate CCxWithered
        CCxWitheredForB = CCi
        if Dayi >= L12:
            CCxWitheredForB = CCx

        # 3.4 Calculate Tpot + Adjust for Low temperature (no transpiration)
        if CCi > 0.0001:
            ret = CalculateETpot(
                DayCC,
                L0,
                L12,
                L123,
                L1234,
                0,
                CCi,
                float(EToStandard),
                KcTop,
                KcDeclAgeingCumul,
                CCx,
                CCxWitheredForB,
                CCeffectProcent,
                CO2i,
                GDDi,
                GDtranspLow,
                TpotForB,
                EpotTotForB,
            )
            if ret is not None:
                # common pattern in this port: return (TpotForB, EpotTotForB)
                if isinstance(ret, tuple) and len(ret) >= 2:
                    TpotForB, EpotTotForB = ret[0], ret[1]
        else:
            TpotForB = 0.0

        # 3.5 Sum of Sum Of KcPot
        SumKcPot += (TpotForB / float(EToStandard))

    # 6. final sum
    return float(SumKcPot)

def GetKs(T0: float, T1: float, Tin: float) -> float:
    Mo = 0.02
    Mx = 1.0

    Trel = (Tin - T0) / (T1 - T0)

    # derive rate of increase (MRate)
    MRate = (-1.0) * (math.log((Mo * Mx - 0.98 * Mo) / (0.98 * (Mx - Mo))))

    # get Ks from logistic equation
    Ksi = (Mo * Mx) / (Mo + (Mx - Mo) * math.exp(-MRate * Trel))

    # adjust for Mo
    Ksi = Ksi - Mo * (1.0 - Trel)

    return Ksi

def KsTemperature(T0: float, T1: float, Tin: float) -> float:
    M = 1.0  # no correction applied (T0 and/or T1 is undefined, or T0=T1)

    if (
        (roundc(T0, mold="int32") != undef_int)
        and (roundc(T1, mold="int32") != undef_int)
        and (abs(T0 - T1) > eps)
    ):
        if T0 < T1:
            a = 1   # cold stress
        else:
            a = -1  # heat stress

        if (a * Tin > a * T0) and (a * Tin < a * T1):
            # within range for correction
            M = GetKs(T0, T1, Tin)
            if M < 0.0:
                M = 0.0
            if M > 1.0:
                M = 1.0
        else:
            if a * Tin <= a * T0:
                M = 0.0
            if a * Tin >= a * T1:
                M = 1.0

    return M

def CalculateETpot(
    DAP: int,
    L0: int,
    L12: int,
    L123: int,
    LHarvest: int,
    DayLastCut: int,
    CCi: float,
    EToVal: float,
    KcVal: float,
    KcDeclineCumulVal: float,
    CCx: float,
    CCxWithered: float,
    CCeffectProcent: float,
    CO2i: float,
    GDDayi: float,
    TempGDtranspLow: float,
    TpotVal: float,
    EpotVal: float,
):
    # CalculateETpot

    VirtualDay = DAP - GetSimulation_DelayedDays()
    tRel = 0.0
    fShape = 1.0

    if (
        ((VirtualDay < L0) and (roundc(100.0 * CCi, mold="int32") == 0))
        or (VirtualDay > LHarvest)
    ):
        # To handlle Forage crops: Round(100*CCi) = 0
        TpotVal = 0.0
        EpotVal = GetSimulParam_KcWetBare() * EToVal
    else:
        # Correction for micro-advection
        CCiAdjusted = 1.72 * CCi - 1.0 * (CCi * CCi) + 0.30 * (CCi * CCi * CCi)
        if CCiAdjusted < 0.0:
            CCiAdjusted = 0.0
        if CCiAdjusted > 1.0:
            CCiAdjusted = 1.0

        # Correction for ageing effects - is a function of calendar days
        if (VirtualDay - DayLastCut) > L12:
            tRel = (VirtualDay - DayLastCut - L12) / float(LHarvest - L12)
            KcVal_local = KcVal - ((math.exp(fShape * tRel) - 1.0) / (math.exp(fShape) - 1.0)) * (
                KcDeclineCumulVal / 100.0
            ) * CCxWithered
        else:
            KcVal_local = KcVal

        # Correction for elevated atmospheric CO2 concentration
        if CO2i > 369.41:
            KcVal_local = KcVal_local * (
                1.0 - 0.05 * (CO2i - 369.41) / (550.0 - 369.41)
            )

        # Correction for Air temperature stress
        if (CCiAdjusted <= ac_zero_threshold) or (roundc(GDDayi, mold="int32") < 0):
            KsTrCold = 1.0
        else:
            KsTrCold = KsTemperature(0.0, TempGDtranspLow, GDDayi)

        # First estimate of Epot and Tpot
        TpotVal = CCiAdjusted * KsTrCold * KcVal_local * EToVal
        EpotVal = GetSimulParam_KcWetBare() * (1.0 - CCiAdjusted) * EToVal

        # Maximum Epot with withered canopy as a result of (early) senescence
        EpotMax = (
            GetSimulParam_KcWetBare()
            * EToVal
            * (1.0 - CCxWithered * CCeffectProcent / 100.0)
        )

        # Correction Epot for dying crop in late-season stage
        if (VirtualDay > L123) and (CCx > 0.0):
            if CCi > (CCx / 2.0):
                # not yet full effect
                if CCi > CCx:
                    Multiplier = 0.0  # no effect
                else:
                    Multiplier = (CCx - CCi) / (CCx / 2.0)
            else:
                Multiplier = 1.0  # full effect

            EpotVal = EpotVal * (
                1.0 - CCx * (CCeffectProcent / 100.0) * Multiplier
            )

            EpotMin = (
                GetSimulParam_KcWetBare()
                * (1.0 - 1.72 * CCx + 1.0 * (CCx * CCx) - 0.30 * (CCx * CCx * CCx))
                * EToVal
            )

            if EpotMin < 0.0:
                EpotMin = 0.0

            if EpotVal < EpotMin:
                EpotVal = EpotMin
            if EpotVal > EpotMax:
                EpotVal = EpotMax

        # Correction for canopy senescence before late-season stage
        if GetSimulation_EvapLimitON():
            if EpotVal > EpotMax:
                EpotVal = EpotMax

        # Correction for drop in photosynthetic capacity of a dying green canopy
        if CCi < CCxWithered:
            if (CCxWithered > 0.01) and (CCi > 0.001):
                TpotVal = TpotVal * math.exp(
                    GetSimulParam_ExpFsen() * math.log(CCi / CCxWithered)
                )

    return TpotVal, EpotVal

def CCatTime(Dayi: int, CCoIN: float, CGCIN: float, CCxIN: float) -> float:
    CCi = CCoIN * math.exp(CGCIN * Dayi)
    if CCi > (CCxIN / 2.0):
        CCi = CCxIN - 0.25 * (CCxIN / CCoIN) * CCxIN * math.exp(-CGCIN * Dayi)

    return float(CCi)

def CCatGDD(GDDi: float, CCoIN: float, GDDCGCIN: float, CCxIN: float) -> float:
    CCi = CCoIN * math.exp(GDDCGCIN * GDDi)
    if CCi > (CCxIN / 2.0):
        CCi = CCxIN - 0.25 * (CCxIN / CCoIN) * CCxIN * math.exp(-GDDCGCIN * GDDi)

    return CCi

def CanopyCoverNoStressGDDaysSF(
    GDDL0: int,
    GDDL123: int,
    GDDLMaturity: int,
    SumGDD: float,
    CCo: float,
    CCx: float,
    GDDCGC: float,
    GDDCDC: float,
    SFRedCGC: int,
    SFRedCCx: int,
) -> float:
    # SumGDD refers to the end of the day and Delayed days are not considered
    CC = 0.0

    if (
        (SumGDD > 0.0)
        and (int(roundc(SumGDD, mold="int32")) <= GDDLMaturity)
        and (CCo > 0.0)
    ):
        if SumGDD <= GDDL0:  # before germination or recovering of transplant
            CC = 0.0
        else:
            if SumGDD < GDDL123:  # Canopy development and Mid-season stage
                CC = CCatGDD(
                    float(SumGDD - GDDL0),
                    CCo,
                    (1.0 - SFRedCGC / 100.0) * GDDCGC,
                    (1.0 - SFRedCCx / 100.0) * CCx,
                )
            else:
                # Late-season stage  (SumGDD <= GDDLMaturity)
                if CCx < 0.001:
                    CC = 0.0
                else:
                    CCxAdj = CCatGDD(
                        float(GDDL123 - GDDL0),
                        CCo,
                        (1.0 - SFRedCGC / 100.0) * GDDCGC,
                        (1.0 - SFRedCCx / 100.0) * CCx,
                    )
                    GDDCDCadj = GDDCDC * (CCxAdj + 2.29) / (CCx + 2.29)

                    if CCxAdj < 0.001:
                        CC = 0.0
                    else:
                        CC = CCxAdj * (
                            1.0
                            - 0.05
                            * (
                                math.exp(
                                    (SumGDD - GDDL123)
                                    * 3.33
                                    * GDDCDCadj
                                    / (CCxAdj + 2.29)
                                )
                                - 1.0
                            )
                        )

    if CC > 1.0:
        CC = 1.0
    if CC < 0.0:
        CC = 0.0

    return CC

def CanopyCoverNoStressSF(
    DAP: int,
    L0: int,
    L123: int,
    LMaturity: int,
    GDDL0: int,
    GDDL123: int,
    GDDLMaturity: int,
    CCo: float,
    CCx: float,
    CGC: float,
    CDC: float,
    GDDCGC: float,
    GDDCDC: float,
    SumGDD: float,
    TypeDays: int,
    SFRedCGC: int,
    SFRedCCx: int,
) -> float:
    if TypeDays == ModeCycle_GDDays:
        return CanopyCoverNoStressGDDaysSF(
            GDDL0,
            GDDL123,
            GDDLMaturity,
            SumGDD,
            CCo,
            CCx,
            GDDCGC,
            GDDCDC,
            SFRedCGC,
            SFRedCCx,
        )
    else:
        return CanopyCoverNoStressDaysSF(
            DAP,
            L0,
            L123,
            LMaturity,
            CCo,
            CCx,
            CGC,
            CDC,
            SFRedCGC,
            SFRedCCx,
        )

def CanopyCoverNoStressDaysSF(
    DAP: int,
    L0: int,
    L123: int,
    LMaturity: int,
    CCo: float,
    CCx: float,
    CGC: float,
    CDC: float,
    SFRedCGC: int,
    SFRedCCx: int,
) -> float:
    # CanopyCoverNoStressDaysSF
    CC = 0.0
    t = DAP - GetSimulation_DelayedDays()
    # CC refers to canopy cover at the end of the day

    if (t >= 1) and (t <= LMaturity) and (CCo > epsilon(1.0)):
        if t <= L0:  # before germination or recovering of transplant
            CC = 0.0
        else:
            if t < L123:  # Canopy development and Mid-season stage
                CC = CCatTime(
                    (t - L0),
                    CCo,
                    ((1.0 - SFRedCGC / 100.0) * CGC),
                    ((1.0 - SFRedCCx / 100.0) * CCx),
                )
            else:
                # Late-season stage (t <= LMaturity)
                if CCx < 0.001:
                    CC = 0.0
                else:
                    CCxAdj = CCatTime(
                        (L123 - L0),
                        CCo,
                        ((1.0 - SFRedCGC / 100.0) * CGC),
                        ((1.0 - SFRedCCx / 100.0) * CCx),
                    )
                    CDCadj = CDC * (CCxAdj + 2.29) / (CCx + 2.29)
                    if CCxAdj < 0.001:
                        CC = 0.0
                    else:
                        CC = CCxAdj * (
                            1.0
                            - 0.05
                            * (math.exp((t - L123) * 3.33 * CDCadj / (CCxAdj + 2.29)) - 1.0)
                        )

    if CC > 1.0:
        CC = 1.0
    if CC < epsilon(1.0):
        CC = 0.0

    return float(CC)

def CCmultiplierWeed(ProcentWeedCover: int, CCxCrop: float, FshapeWeed: float) -> float:
    fWeed = 1.0

    if (ProcentWeedCover > 0) and (CCxCrop < 0.9999) and (CCxCrop > 0.001):
        if ProcentWeedCover == 100:
            fWeed = 1.0 / CCxCrop
        else:
            fWeed = 1.0 - (1.0 - 1.0 / CCxCrop) * (
                (math.exp(FshapeWeed * ProcentWeedCover / 100.0) - 1.0)
                / (math.exp(FshapeWeed) - 1.0)
            )
            if fWeed > (1.0 / CCxCrop):
                fWeed = 1.0 / CCxCrop
    else:
        fWeed = 1.0

    return fWeed


def GetWeedRC(
    TheDay: int,
    GDDayi: float,
    fCCx: float,
    TempWeedRCinput: int,
    TempWeedAdj: int,
    TempWeedDeltaRC: int,
    L12SF: int,
    TempL123: int,
    GDDL12SF: int,
    TempGDDL123: int,
    TheModeCycle: int,
):
    WeedRCDayCalc = float(TempWeedRCinput)

    if (TempWeedRCinput > 0) and (TempWeedDeltaRC != 0):
        # daily RC when increase/decline of RC in season (i.e. TempWeedDeltaRC <> 0)
        # adjust the slope of increase/decline of RC in case of self-thinning (i.e. fCCx < 1)
        if (TempWeedDeltaRC != 0) and (fCCx < 0.999):
            # only when self-thinning and there is increase/decline of RC
            if fCCx < 0.005:
                TempWeedDeltaRC = 0
            else:
                TempWeedDeltaRC = int(
                    roundc(
                        TempWeedDeltaRC
                        * math.exp(math.log(fCCx) * (1.0 + TempWeedAdj / 100.0)),
                        mold="int32",
                    )
                )

        # calculate WeedRCDay by considering (adjusted) decline/increase of RC
        if TheModeCycle == ModeCycle_CalendarDays:
            if TheDay > L12SF:
                if TheDay >= TempL123:
                    WeedRCDayCalc = float(TempWeedRCinput) * (
                        1.0 + TempWeedDeltaRC / 100.0
                    )
                else:
                    WeedRCDayCalc = float(TempWeedRCinput) * (
                        1.0
                        + (TempWeedDeltaRC / 100.0)
                        * (TheDay - L12SF)
                        / float(TempL123 - L12SF)
                    )
        else:
            if GDDayi > GDDL12SF:
                if GDDayi > TempGDDL123:
                    WeedRCDayCalc = float(TempWeedRCinput) * (
                        1.0 + TempWeedDeltaRC / 100.0
                    )
                else:
                    WeedRCDayCalc = float(TempWeedRCinput) * (
                        1.0
                        + (TempWeedDeltaRC / 100.0)
                        * (GDDayi - GDDL12SF)
                        / float(TempGDDL123 - GDDL12SF)
                    )

        # fine-tuning for over- or undershooting in case of self-thinning
        if fCCx < 0.999:
            # only for self-thinning
            if (fCCx < 1.0) and (fCCx > 0.0) and (WeedRCDayCalc > 98.0):
                WeedRCDayCalc = 98.0
            if WeedRCDayCalc < 0.0:
                WeedRCDayCalc = 0.0
            if fCCx <= 0.0:
                WeedRCDayCalc = 100.0

    return WeedRCDayCalc, TempWeedDeltaRC

def CCiNoWaterStressSF(
    Dayi: int,
    L0: int,
    L12SF: int,
    L123: int,
    L1234: int,
    GDDL0: int,
    GDDL12SF: int,
    GDDL123: int,
    GDDL1234: int,
    CCo: float,
    CCx: float,
    CGC: float,
    GDDCGC: float,
    CDC: float,
    GDDCDC: float,
    SumGDD: float,
    RatDGDD: float,
    SFRedCGC: int,
    SFRedCCx: int,
    SFCDecline: float,
    TheModeCycle: int,
) -> float:
    # Calculate CCi
    CCi = CanopyCoverNoStressSF(
        Dayi,
        L0,
        L123,
        L1234,
        GDDL0,
        GDDL123,
        GDDL1234,
        CCo,
        CCx,
        CGC,
        CDC,
        GDDCGC,
        GDDCDC,
        SumGDD,
        TheModeCycle,
        SFRedCGC,
        SFRedCCx,
    )

    # Consider CDecline for limited soil fertiltiy
    if (Dayi > L12SF) and (SFCDecline > ac_zero_threshold) and (L12SF < L123):
        if Dayi < L123:
            if TheModeCycle == ModeCycle_CalendarDays:
                CCi = CCi - (SFCDecline / 100.0) * math.exp(
                    2.0 * math.log(float(Dayi - L12SF))
                ) / float(L123 - L12SF)
            else:
                if (SumGDD > GDDL12SF) and (GDDL123 > GDDL12SF):
                    CCi = CCi - (RatDGDD * SFCDecline / 100.0) * math.exp(
                        2.0 * math.log(SumGDD - GDDL12SF)
                    ) / float(GDDL123 - GDDL12SF)

            if CCi < 0.0:
                CCi = 0.0

        else:
            if TheModeCycle == ModeCycle_CalendarDays:
                CCi = CCatTime(
                    (L123 - L0),
                    CCo,
                    (CGC * (1.0 - SFRedCGC / 100.0)),
                    ((1.0 - SFRedCCx / 100.0) * CCx),
                )

                # CCibis is CC in late season when Canopy decline continues
                CCibis = CCi - (SFCDecline / 100.0) * (
                    math.exp(2.0 * math.log(float(Dayi - L12SF))) / float(L123 - L12SF)
                )

                if CCibis < 0.0:
                    CCi = 0.0
                else:
                    CCi = CCi - ((SFCDecline / 100.0) * float(L123 - L12SF))

                if CCi < 0.001:
                    CCi = 0.0
                else:
                    # is CCx at start of late season, adjusted for canopy
                    # decline with soil fertility stress
                    CCxAdj = CCi
                    CDCadj = CDC * (CCxAdj + 2.29) / (CCx + 2.29)

                    if Dayi < (L123 + LengthCanopyDecline(CCxAdj, CDCadj)):
                        CCi = CCxAdj * (
                            1.0
                            - 0.05
                            * (
                                math.exp(
                                    (Dayi - L123) * 3.33 * CDCadj / (CCxAdj + 2.29)
                                )
                                - 1.0
                            )
                        )
                        if CCibis < CCi:
                            CCi = CCibis  # accept smallest Canopy Cover
                    else:
                        CCi = 0.0

            else:
                CCi = CCatTime(
                    (GDDL123 - GDDL0),
                    CCo,
                    (GDDCGC * (1.0 - SFRedCGC / 100.0)),
                    ((1.0 - SFRedCCx / 100.0) * CCx),
                )

                # CCibis is CC in late season when Canopy decline continues
                if (SumGDD > GDDL12SF) and (GDDL123 > GDDL12SF):
                    CCibis = CCi - (RatDGDD * SFCDecline / 100.0) * (
                        math.exp(2.0 * math.log(SumGDD - GDDL12SF))
                        / float(GDDL123 - GDDL12SF)
                    )
                else:
                    CCibis = CCi

                if CCibis < 0.0:
                    CCi = 0.0
                else:
                    CCi = CCi - ((RatDGDD * SFCDecline / 100.0) * float(GDDL123 - GDDL12SF))

                if CCi < 0.001:
                    CCi = 0.0
                else:
                    # is CCx at start of late season, adjusted for canopy
                    # decline with soil fertility stress
                    CCxAdj = CCi
                    GDDCDCadj = GDDCDC * (CCxAdj + 2.29) / (CCx + 2.29)

                    if SumGDD < (GDDL123 + LengthCanopyDecline(CCxAdj, GDDCDCadj)):
                        CCi = CCxAdj * (
                            1.0
                            - 0.05
                            * (
                                math.exp(
                                    (SumGDD - GDDL123)
                                    * 3.33
                                    * GDDCDCadj
                                    / (CCxAdj + 2.29)
                                )
                                - 1.0
                            )
                        )
                        if CCibis < CCi:
                            CCi = CCibis  # accept smallest Canopy Cover
                    else:
                        CCi = 0.0

            if CCi < 0.0:
                CCi = 0.0

    return CCi

def MultiplierCCoSelfThinning(Yeari, Yearx, ShapeFactor):
    fCCo = 1.0
    if (Yeari >= 1) and (Yearx >= 2) and (roundc(100 * ShapeFactor, mold=1) != 0):
        Year0 = 1.0 + (Yearx - 1) * math.exp(ShapeFactor * math.log(10.0))
        if (Yeari >= Year0) or (Year0 <= 1):
            fCCo = 0.0
        else:
            fCCo = 1.0 - (Yeari - 1) / (Year0 - 1.0)
        if fCCo < 0.0:
            fCCo = 0.0
    return fCCo

def ActualRootingDepthGDDays(DAP, L1234, GDDL0, GDDLZmax, SumGDD, Zmin, Zmax):
    # after sowing the crop has roots even when SumGDD = 0
    VirtualDay = DAP - GetSimulation_DelayedDays()
    global ShapeFactor

    if (VirtualDay < 1) or (VirtualDay > L1234):
        ActualRootingDepthGDDays = 0
    elif SumGDD >= GDDLZmax:
        ActualRootingDepthGDDays = Zmax
    elif Zmin < Zmax:
        Zini = Zmin * (GetSimulParam_RootPercentZmin() / 100.0)
        GDDT0 = GDDL0 / 2.0

        if GDDLZmax <= GDDT0:
            Zr = Zini + (Zmax - Zini) * SumGDD / GDDLZmax
        else:
            if SumGDD <= GDDT0:
                Zr = Zini
            else:
                Zr = Zini + (Zmax - Zini) \
                     * TimeRootFunction(SumGDD, ShapeFactor,
                                        float(GDDLZmax), GDDT0)

        if Zr > Zmin:
            ActualRootingDepthGDDays = Zr
        else:
            ActualRootingDepthGDDays = Zmin
    else:
        ActualRootingDepthGDDays = Zmax

    return ActualRootingDepthGDDays

def ActualRootingDepthDays(DAP, L0, LZmax, L1234, Zmin, Zmax):
    # Actual rooting depth at the end of Dayi
    VirtualDay = DAP - GetSimulation_DelayedDays()
    global ShapeFactor

    if (VirtualDay < 1) or (VirtualDay > L1234):
        ActualRootingDepthDays = 0
    elif VirtualDay >= LZmax:
        ActualRootingDepthDays = Zmax
    elif Zmin < Zmax:
        Zini = Zmin * (GetSimulParam_RootPercentZmin() / 100.0)
        T0 = 0
        T0 = roundc(L0 / 2.0, mold=T0)

        if LZmax <= T0:
            Zr = Zini + (Zmax - Zini) * VirtualDay * 1.0 / LZmax
        elif VirtualDay <= T0:
            Zr = Zini
        else:
            Zr = Zini + (Zmax - Zini) \
                 * TimeRootFunction(float(VirtualDay), ShapeFactor,
                                    float(LZmax), float(T0))

        if Zr > Zmin:
            ActualRootingDepthDays = Zr
        else:
            ActualRootingDepthDays = Zmin
    else:
        ActualRootingDepthDays = Zmax

    return ActualRootingDepthDays

def TimeRootFunction(t, ShapeFactor, tmax, t0):
    return math.exp((10.0 / ShapeFactor) * math.log((t - t0) / (tmax - t0)))

def ActualRootingDepth(DAP, L0, LZmax, L1234, GDDL0, GDDLZmax,
                       SumGDD, Zmin, Zmax, ShapeFactor_in,
                       TypeDays):
    Zini = 0.0
    Zr = 0.0
    VirtualDay = 0
    T0 = 0
    rootmax_rounded = 0
    zmax_rounded = 0
    global ShapeFactor
    ShapeFactor = ShapeFactor_in

    if TypeDays == ModeCycle_GDDays:
        Zr = ActualRootingDepthGDDays(DAP, L1234, GDDL0, GDDLZmax, SumGDD,
                                      Zmin, Zmax)
    else:
        Zr = ActualRootingDepthDays(DAP, L0, LZmax, L1234, Zmin, Zmax)

    # restrictive soil layer
    SetSimulation_SCor(1.0)

    rootmax_rounded = roundc(float(GetSoil_RootMax() * 1000), mold=rootmax_rounded)
    zmax_rounded = roundc(Zmax * 1000, mold=zmax_rounded)

    if rootmax_rounded < zmax_rounded:
        Zr = ZrAdjustedToRestrictiveLayers(Zr, GetSoil_NrSoilLayers(),
                                           GetSoilLayer(), Zr)

    ActualRootingDepth = Zr

    return ActualRootingDepth

def DetermineRootZoneSaltContent(RootingDepth, ZrECe, ZrECsw, ZrECswFC, ZrKsSalt):
    CumDepth = 0.0
    Factor = 0.0
    frac_value = 0.0
    compi = 0

    ZrECe = 0.0
    ZrECsw = 0.0
    ZrECswFC = 0.0
    ZrKsSalt = 1.0
    if RootingDepth >= GetCrop_RootMin():
        while True:
            compi = compi + 1
            CumDepth = CumDepth + GetCompartment_Thickness(compi)
            if CumDepth <= RootingDepth:
                Factor = 1.0
            else:
                frac_value = RootingDepth - (CumDepth - GetCompartment_Thickness(compi))
                if frac_value > 0.0:
                    Factor = frac_value / GetCompartment_Thickness(compi)
                else:
                    Factor = 0.0
            Factor = Factor * (GetCompartment_Thickness(compi)) / RootingDepth
            ZrECe = ZrECe + Factor * ECeComp(GetCompartment_i(compi))
            ZrECsw = ZrECsw + Factor * ECswComp(GetCompartment_i(compi), False)  # not at FC
            ZrECswFC = ZrECswFC + Factor * ECswComp(GetCompartment_i(compi), True)  # at FC
            if (CumDepth >= RootingDepth) or (compi == NrCompartments):
                break
        if ((GetCrop_ECemin() != undef_int) and (GetCrop_ECemax() != undef_int)) and \
           (GetCrop_ECemin() < GetCrop_ECemax()):
            ZrKsSalt = KsSalinity(True, GetCrop_ECemin(), GetCrop_ECemax(), ZrECe, 0.0)
        else:
            ZrKsSalt = KsSalinity(False, GetCrop_ECemin(), GetCrop_ECemax(), ZrECe, 0.0)
    else:
        ZrECe = undef_int
        ZrECsw = undef_int
        ZrECswFC = undef_int
        ZrKsSalt = undef_int

    return ZrECe, ZrECsw, ZrECswFC, ZrKsSalt

def ECswComp(Comp, atFC):
    TotSalt = 0.0

    for i in range(1, GetSoilLayer_SCP1(Comp.Layer) + 1):
        TotSalt = TotSalt + Comp.Salt[i - 1] + Comp.Depo[i - 1]  # g/m2

    if atFC == True:
        TotSalt = TotSalt / (GetSoilLayer_FC(Comp.Layer) * 10.0 * Comp.Thickness
                             * (1.0 - GetSoilLayer_GravelVol(Comp.Layer) / 100.0))  # g/l
    else:
        TotSalt = TotSalt / (Comp.Theta * 1000.0 * Comp.Thickness
                             * (1.0 - GetSoilLayer_GravelVol(Comp.Layer) / 100.0))  # g/l

    if TotSalt > GetSimulParam_SaltSolub():
        TotSalt = GetSimulParam_SaltSolub()

    ECswComp = TotSalt / Equiv
    return ECswComp

def KsSalinity(SalinityResponsConsidered, ECeN, ECeX, ECeVAR, KsShapeSalinity):
    M = 1.0
    tmp_var = 0.0

    M = 1.0  # no correction applied
    if SalinityResponsConsidered:
        if (ECeVAR > ECeN) and (ECeVAR < ECeX):
            # within range for correction
            if (roundc(KsShapeSalinity * 10.0, mold=1) != 0) and \
               (roundc(KsShapeSalinity * 10.0, mold=1) != 990):
                tmp_var = float(ECeN)
                M = KsAny(ECeVAR, tmp_var, float(ECeX), KsShapeSalinity)
                # convex or concave
            else:
                if roundc(KsShapeSalinity * 10.0, mold=1) == 0:
                    M = 1.0 - (ECeVAR - ECeN) / (ECeX - ECeN)
                    # linear (KsShapeSalinity = 0)
                else:
                    M = KsTemperature(float(ECeX), float(ECeN), ECeVAR)
                    # logistic equation (KsShapeSalinity = 99)
        else:
            if ECeVAR <= ECeN:
                M = 1.0  # no salinity stress
            if ECeVAR >= ECeX:
                M = 0.0  # full salinity stress
    if M > 1:
        M = 1.0
    if M < 0:
        M = 0.0

    KsSalinity = M
    return KsSalinity

def CCiniTotalFromTimeToCCini(TempDaysToCCini, TempGDDaysToCCini,
                              L0, L12, L12SF, L123, L1234, GDDL0,
                              GDDL12, GDDL12SF, GDDL123,
                              GDDL1234, CCo, CCx, CGC, GDDCGC,
                              CDC, GDDCDC, RatDGDD, SFRedCGC,
                              SFRedCCx, SFCDecline, fWeed,
                              TheModeCycle):
    DayCC = 0
    SumGDDforCCini = 0.0
    TempCCini = 0.0
    Tadj = 0
    GDDTadj = 0

    if TempDaysToCCini != 0:
        # regrowth
        SumGDDforCCini = float(undef_int)
        GDDTadj = undef_int
        # find adjusted calendar and GDD time
        if TempDaysToCCini == undef_int:
            # CCx on 1st day
            Tadj = L12 - L0
            if TheModeCycle == ModeCycle_GDDays:
                GDDTadj = GDDL12 - GDDL0
        else:
            # CC on 1st day is < CCx
            Tadj = TempDaysToCCini
            if TheModeCycle == ModeCycle_GDDays:
                GDDTadj = TempGDDaysToCCini

        # calculate CCini with adjusted time
        DayCC = L0 + Tadj
        if TheModeCycle == ModeCycle_GDDays:
            SumGDDforCCini = GDDL0 + GDDTadj

        TempCCini = CCiNoWaterStressSF(
            DayCC, L0, L12SF, L123, L1234, GDDL0,
            GDDL12SF, GDDL123, GDDL1234,
            (CCo * fWeed), (CCx * fWeed), CGC, GDDCGC,
            (CDC * (fWeed * CCx + 2.29) / (CCx + 2.29)),
            (GDDCDC * (fWeed * CCx + 2.29) / (CCx + 2.29)),
            SumGDDforCCini, RatDGDD, SFRedCGC,
            SFRedCCx, SFCDecline, TheModeCycle
        )
        # correction for fWeed is already in TempCCini (since DayCC > 0);
    else:
        TempCCini = (CCo * fWeed)  # sowing or transplanting

    CCiniTotalFromTimeToCCini = TempCCini
    return CCiniTotalFromTimeToCCini

def DetermineRootZoneWC(RootingDepth, ZtopSWCconsidered):
    CumDepth = 0.0
    Factor = 0.0
    frac_value = 0.0
    DrRel = 0.0
    DZtopRel = 0.0
    TopSoilInMeter = 0.0
    compi = 0

    # calculate SWC in root zone
    CumDepth = 0.0
    compi = 0
    SetRootZoneWC_Actual(0.0)
    SetRootZoneWC_FC(0.0)
    SetRootZoneWC_WP(0.0)
    SetRootZoneWC_SAT(0.0)
    SetRootZoneWC_Leaf(0.0)
    SetRootZoneWC_Thresh(0.0)
    SetRootZoneWC_Sen(0.0)

    while True:
        compi = compi + 1

        Thickness = GetCompartment_Thickness(compi)
        Layer = GetCompartment_Layer(compi)
        GravelFactor = 1.0 - GetSoilLayer_GravelVol(Layer) / 100.0
        Theta = GetCompartment_theta(compi)
        FC = GetSoilLayer_FC(Layer)
        WP = GetSoilLayer_WP(Layer)
        SAT = GetSoilLayer_SAT(Layer)

        CumDepth = CumDepth + Thickness

        if CumDepth <= RootingDepth:
            Factor = 1.0
        else:
            frac_value = RootingDepth - (CumDepth - Thickness)
            if frac_value > 0.0:
                Factor = frac_value / Thickness
            else:
                Factor = 0.0

        SetRootZoneWC_Actual(
            GetRootZoneWC_Actual() + Factor * 1000.0 * Theta * Thickness * GravelFactor
        )
        SetRootZoneWC_FC(
            GetRootZoneWC_FC() + Factor * 10.0 * FC * Thickness * GravelFactor
        )
        SetRootZoneWC_Leaf(
            GetRootZoneWC_Leaf()
            + Factor
            * 10.0
            * Thickness
            * (FC - GetCrop_pLeafAct() * (FC - WP))
            * GravelFactor
        )
        SetRootZoneWC_Thresh(
            GetRootZoneWC_Thresh()
            + Factor
            * 10.0
            * Thickness
            * (FC - GetCrop_pActStom() * (FC - WP))
            * GravelFactor
        )
        SetRootZoneWC_Sen(
            GetRootZoneWC_Sen()
            + Factor
            * 10.0
            * Thickness
            * (FC - GetCrop_pSenAct() * (FC - WP))
            * GravelFactor
        )
        SetRootZoneWC_WP(
            GetRootZoneWC_WP() + Factor * 10.0 * WP * Thickness * GravelFactor
        )
        SetRootZoneWC_SAT(
            GetRootZoneWC_SAT() + Factor * 10.0 * SAT * Thickness * GravelFactor
        )

        if (CumDepth >= RootingDepth) or (compi == NrCompartments):
            break

    # calculate SWC in top soil (top soil in meter = SimulParam.ThicknessTopSWC/100)
    if (RootingDepth * 100.0) <= GetSimulParam_ThicknessTopSWC():
        SetRootZoneWC_ZtopAct(GetRootZoneWC_Actual())
        SetRootZoneWC_ZtopFC(GetRootZoneWC_FC())
        SetRootZoneWC_ZtopWP(GetRootZoneWC_WP())
        SetRootZoneWC_ZtopThresh(GetRootZoneWC_Thresh())
    else:
        CumDepth = 0.0
        compi = 0
        SetRootZoneWC_ZtopAct(0.0)
        SetRootZoneWC_ZtopFC(0.0)
        SetRootZoneWC_ZtopWP(0.0)
        SetRootZoneWC_ZtopThresh(0.0)
        TopSoilInMeter = GetSimulParam_ThicknessTopSWC() / 100.0

        while True:
            compi = compi + 1

            Thickness = GetCompartment_Thickness(compi)
            Layer = GetCompartment_Layer(compi)
            GravelFactor = 1.0 - GetSoilLayer_GravelVol(Layer) / 100.0
            Theta = GetCompartment_theta(compi)
            FC = GetSoilLayer_FC(Layer)
            WP = GetSoilLayer_WP(Layer)

            CumDepth = CumDepth + Thickness

            if (CumDepth * 100.0) <= GetSimulParam_ThicknessTopSWC():
                Factor = 1.0
            else:
                frac_value = TopSoilInMeter - (CumDepth - Thickness)
                if frac_value > 0.0:
                    Factor = frac_value / Thickness
                else:
                    Factor = 0.0

            SetRootZoneWC_ZtopAct(
                GetRootZoneWC_ZtopAct() + Factor * 1000.0 * Theta * Thickness * GravelFactor
            )
            SetRootZoneWC_ZtopFC(
                GetRootZoneWC_ZtopFC() + Factor * 10.0 * FC * Thickness * GravelFactor
            )
            SetRootZoneWC_ZtopWP(
                GetRootZoneWC_ZtopWP() + Factor * 10.0 * WP * Thickness * GravelFactor
            )
            SetRootZoneWC_ZtopThresh(
                GetRootZoneWC_ZtopThresh()
                + Factor
                * 10.0
                * Thickness
                * (FC - GetCrop_pActStom() * (FC - WP))
                * GravelFactor
            )

            if (CumDepth >= TopSoilInMeter) or (compi == NrCompartments):
                break

    # Relative depletion in rootzone and in top soil
    if roundc(1000.0 * (GetRootZoneWC_FC() - GetRootZoneWC_WP()), mold=1) > 0:
        DrRel = (
            (GetRootZoneWC_FC() - GetRootZoneWC_Actual()) /
            (GetRootZoneWC_FC() - GetRootZoneWC_WP())
        )
    else:
        DrRel = 0.0

    if roundc(1000.0 * (GetRootZoneWC_ZtopFC() - GetRootZoneWC_ZtopWP()), mold=1) > 0:
        DZtopRel = (
            (GetRootZoneWC_ZtopFC() - GetRootZoneWC_ZtopAct()) /
            (GetRootZoneWC_ZtopFC() - GetRootZoneWC_ZtopWP())
        )
    else:
        DZtopRel = 0.0

    # Zone in soil profile considered for determining stress response
    if DZtopRel < DrRel:
        ZtopSWCconsidered = True  # top soil is relative wetter than root zone
    else:
        ZtopSWCconsidered = False

    return ZtopSWCconsidered

def MaxCRatDepth(ParamCRa, ParamCRb, Ksat, Zi, DepthGWT):
    CRmax = 0.0
    if (Ksat > 0.0) and (DepthGWT > 0.0) and ((DepthGWT - Zi) < 4.0):
        if Zi >= DepthGWT:
            CRmax = 99.0
        else:
            CRmax = math.exp((math.log(DepthGWT - Zi) - ParamCRb) / ParamCRa)
            if CRmax > 99.0:
                CRmax = 99.0
    return CRmax

def DetermineCNIandIII(CN2, CN1, CN3):
    CN1 = roundc(
        1.4 * (math.exp(-14 * math.log(10.0))) + 0.507 * CN2
        - 0.00374 * CN2 * CN2 + 0.0000867 * CN2 * CN2 * CN2,
        mold=1
    )
    CN3 = roundc(
        5.6 * (math.exp(-14 * math.log(10.0))) + 2.33 * CN2
        - 0.0209 * CN2 * CN2 + 0.000076 * CN2 * CN2 * CN2,
        mold=1
    )

    if CN1 <= 0:
        CN1 = 1
    elif CN1 > 100:
        CN1 = 100

    if CN3 <= 0:
        CN3 = 1
    elif CN3 > 100:
        CN3 = 100

    if CN3 < CN2:
        CN3 = CN2

    return CN1, CN3

import math


def SoilEvaporationReductionCoefficient(Wrel, Edecline):
    if Wrel <= 0.00001:
        return 0.0
    else:
        if Wrel >= 0.99999:
            return 1.0
        else:
            return (math.exp(Edecline * Wrel) - 1.0) / (math.exp(Edecline) - 1.0)

def AdjustedKsStoToECsw(ECeMin, ECeMax, ResponseECsw, ECei,
                        ECswi, ECswFCi, Wrel, Coeffb0Salt, Coeffb1Salt, Coeffb2Salt, KsStoIN):
    ECswRel = 0.0
    LocalKsShapeFactorSalt = 0.0
    KsSalti = 0.0
    SaltStressi = 0.0
    StoClosure = 0.0
    KsStoOut = 0.0

    if (ResponseECsw > 0) and (Wrel > epsilon(1.0)) and (GetSimulation_SalinityConsidered() == True):
        # adjustment to ECsw considered
        ECswRel = ECswi - (ECswFCi - ECei) + (ResponseECsw - 100.0) * Wrel
        if (ECswRel > ECeMin) and (ECswRel < ECeMax):
            # stomatal closure at ECsw relative
            LocalKsShapeFactorSalt = 3.0  # CONVEX give best ECsw response
            KsSalti = KsSalinity(GetSimulation_SalinityConsidered(), ECeMin, ECeMax, ECswRel, LocalKsShapeFactorSalt)
            SaltStressi = (1.0 - KsSalti) * 100.0
            StoClosure = Coeffb0Salt + Coeffb1Salt * SaltStressi + Coeffb2Salt * SaltStressi * SaltStressi
            # adjusted KsSto
            KsStoOut = (1.0 - StoClosure / 100.0)
            if KsStoOut < 0.0:
                KsStoOut = 0.0
            if KsStoOut > KsStoIN:
                KsStoOut = KsStoIN
        else:
            if ECswRel >= ECeMax:
                KsStoOut = 0.0  # full stress
            else:
                KsStoOut = KsStoIN  # no extra stress
    else:
        KsStoOut = KsStoIN  # no adjustment to ECsw

    return KsStoOut

def fAdjustedForCO2(CO2i, WPi, PercentA):
    # 1. Correction for crop type: fType
    if WPi >= 40.0:
        fType = 0.0  # no correction for C4 crops
    else:
        if WPi <= 20.0:
            fType = 1.0  # full correction for C3 crops
        else:
            fType = (40.0 - WPi) / (40.0 - 20.0)

    # 2. crop sink strength coefficient: fSink
    fSink = PercentA / 100.0
    if fSink < 0.0:
        fSink = 0.0  # based on FACE expirements
    if fSink > 1.0:
        fSink = 1.0  # theoretical adjustment

    # 3. Correction coefficient for CO2: fCO2Old
    fCO2Old = undef_int
    if CO2i <= 550.0:
        # 3.1 weighing factor for CO2
        if CO2i <= CO2Ref:
            fW = 0.0
        else:
            if CO2i >= 550.0:
                fW = 1.0
            else:
                fW = 1.0 - (550.0 - CO2i) / (550.0 - CO2Ref)

        # 3.2 adjustment for CO2
        fCO2Old = (CO2i / CO2Ref) / (
            1.0 + (CO2i - CO2Ref) * (
                (1.0 - fW) * 0.000138
                + fW * (0.000138 * fSink + 0.001165 * (1.0 - fSink))
            )
        )

    # 4. Adjusted correction coefficient for CO2: fCO2adj
    fCO2adj = undef_int
    if CO2i > CO2Ref:
        # 4.1 Shape factor
        fShape = -4.61824 - 3.43831 * fSink - 5.32587 * fSink * fSink

        # 4.2 adjustment for CO2
        if CO2i >= 2000.0:
            fCO2adj = 1.58  # maximum is reached
        else:
            CO2rel = (CO2i - CO2Ref) / (2000.0 - CO2Ref)
            fCO2adj = 1.0 + 0.58 * (
                (math.exp(CO2rel * fShape) - 1.0) / (math.exp(fShape) - 1.0)
            )

    # 5. Selected adjusted coefficient for CO2: fCO2
    if CO2i <= CO2Ref:
        fCO2 = fCO2Old
    else:
        fCO2 = fCO2adj
        if (CO2i <= 550.0) and (fCO2Old < fCO2adj):
            fCO2 = fCO2Old

    # 6. final adjustment
    return 1.0 + fType * (fCO2 - 1.0)


def HarvestIndexDay(DAP, DaysToFlower, HImax, dHIdt, CCi,
                    CCxadjusted, TheCCxWithered,
                    PercCCxHIfinal, TempPlanting,
                    PercentLagPhase, HIfinal):

    HIo = 1
    HIGC = 0.0
    HIday = 0.0
    HIGClinear = 0.0
    dHIdt_local = 0.0
    t = 0
    tMax = 0
    tSwitch = 0
    CCthreshold = 0.0

    dHIdt_local = dHIdt
    t = DAP - GetSimulation_DelayedDays() - DaysToFlower
    # Simulation.WPyON := false;
    PercentLagPhase = 0
    if t <= 0:
        HIday = 0.0
    else:
        if (GetCrop_subkind() == subkind_Vegetative) and (TempPlanting == plant_regrowth):
            dHIdt_local = 100.0
        if (GetCrop_subkind() == subkind_Forage) and (TempPlanting == plant_regrowth):
            dHIdt_local = 100.0

        if dHIdt_local > 99.0:
            HIday = HImax
            PercentLagPhase = 100
        else:
            HIGC = HarvestIndexGrowthCoefficient(float(HImax), dHIdt_local)
            tSwitch, HIGClinear = GetDaySwitchToLinear(HImax, dHIdt_local, HIGC)

            if t < tSwitch:
                PercentLagPhase = roundc(100.0 * (t / float(tSwitch)), mold=1)
                HIday = (HIo * HImax) / (HIo + (HImax - HIo) * math.exp(-HIGC * t))
            else:
                PercentLagPhase = 100
                if ((GetCrop_subkind() == subkind_Tuber)
                        or (GetCrop_subkind() == subkind_Vegetative)
                        or (GetCrop_subkind() == subkind_Forage)):
                    # continue with logistic equation
                    HIday = (HIo * HImax) / (HIo + (HImax - HIo) * math.exp(-HIGC * t))
                    if HIday >= 0.9799 * HImax:
                        HIday = HImax
                else:
                    # switch to linear increase
                    HIday = (HIo * HImax) / (HIo + (HImax - HIo) * math.exp(-HIGC * tSwitch))
                    HIday = HIday + HIGClinear * (t - tSwitch)

            if HIday > HImax:
                HIday = HImax
            if HIday <= (HIo + 0.4):
                HIday = 0.0
            if (HImax - HIday) < 0.4:
                HIday = HImax

        # adjust HIfinal if required for inadequate photosynthesis (unsufficient green canopy)
        tMax = roundc(HImax / dHIdt_local, mold=1)

        if (GetCrop_subkind() != subkind_Vegetative) and (GetCrop_subkind() != subkind_Forage):
            CCthreshold = PercCCxHIfinal
            if (100.0 * GetCrop_CCo()) > PercCCxHIfinal:
                CCthreshold = 100.0 * (1.1 * GetCrop_CCo())

            if ((HIfinal == HImax)
                and (t <= tMax)
                and ((CCi + epsilon(0.0)) <= (CCthreshold / 100.0))
                and (TheCCxWithered > epsilon(0.0))
                and (CCi < TheCCxWithered)):
                    HIfinal = roundc(HIday, mold=1)

        if HIday > HIfinal:
            HIday = HIfinal

    return HIday, PercentLagPhase, HIfinal

def MultiplierCCxSelfThinning(Yeari, Yearx, ShapeFactor):
    fCCx = 1.0

    if (Yeari >= 2) and (Yearx >= 2) and (roundc(100.0 * ShapeFactor, mold=1) != 0):
        Year0 = 1.0 + (Yearx - 1.0) * math.exp(ShapeFactor * math.log(10.0))
        if Yeari >= Year0:
            fCCx = 0.0
        else:
            fCCx = 0.9 + 0.1 * (
                1.0 - math.exp((1.0 / ShapeFactor) * math.log((Yeari - 1.0) / (Yearx - 1.0)))
            )
        if fCCx < 0:
            fCCx = 0.0

    return fCCx

def BMRange(HIadj):
    if HIadj <= 0:
        BMR = 0.0
    else:
        BMR = (math.log(float(HIadj)) / 0.0562) / 100.0

    if BMR > 1.0:
        BMR = 1.0

    return BMR

def HImultiplier(RatioBM, RangeBM, HIadj):
    Rini = 1.0 - RangeBM
    REnd = 1.0
    Rmax = Rini + (2.0 / 3.0) * (REnd - Rini)

    if RatioBM <= Rini:
        return 1.0
    elif RatioBM <= Rmax:
        return 1.0 + (
            1.0 + math.sin(math.pi * (1.5 - (RatioBM - Rini) / (Rmax - Rini)))
        ) * (HIadj / 200.0)
    elif RatioBM <= REnd:
        return 1.0 + (
            1.0 + math.sin(math.pi * (0.5 + (RatioBM - Rmax) / (REnd - Rmax)))
        ) * (HIadj / 200.0)
    else:
        return 1.0
