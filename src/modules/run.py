import os
import sys
import numpy as np
from ._global import *
from ._global import _strip_quotes
from . import _global as G
from typing import Optional, TextIO
from dataclasses import dataclass
from .tempprocessing import *
from .utils import *
from .preparefertilitysalinity import *
from .climprocessing import GetDecadeEToDataSet
from .climprocessing import GetMonthlyEToDataSet
from .climprocessing import GetDecadeRainDataSet
from .climprocessing import GetMonthlyRainDataSet
from .rootunit import *
from .simul import BUDGET_module
from .simul import DeterminePotentialBiomass
from .simul import DetermineBiomassAndYield
from .infosresults import WriteAssessmentSimulation
from .progresswindow import advance_progress

fCuts_lines = []
fCuts_pos = 0
fCuts_iostat = 0

fIrri_lines = []
fIrri_pos = 0
fIrri_iostat = 0

fObs_lines = []
fObs_pos = 0
fObs_iostat = 0

fEToSIM_lines = []
fEToSIM_pos = 0
fEToSIM_iostat = 0

fRainSIM_lines = []
fRainSIM_pos = 0
fRainSIM_iostat = 0

fTempSIM_lines = []
fTempSIM_pos = 0
fTempSIM_iostat = 0


# the Simulation.FromDayNr for next run if delayed germination and KeepSWC
NextSimFromDayNr: int = 0
TheProjectFile: str = ""
fRun: Optional[TextIO] = None
fIrrInfo_filename: str = ""
fIrrInfo: Optional[TextIO] = None

fHarvest_filename: str = ""
fHarvest: Optional[TextIO] = None

fEval_filename: str = ""
fEval: Optional[TextIO] = None

WaterTableInProfile = False
StartMode = False
#NoMoreCrop = False
GlobalIrriECw = False  # for versions before 3.2 where EC of
                       # irrigation water was not yet recorded
LastIrriDAP = 0

# Evaluation
DayNr1Eval = 0
DayNrEval = 0
LineNrEval = 0

Bin = 0.0
Bout = 0.0
GDDayi = 0.0
CO2i = 0.0
FracBiomassPotSF = 0.0
SumETo = 0.0
SumGDD = 0.0
Ziprev = 0.0
SumGDDPrev = 0.0
CCxWitheredTpotNoS = 0.0
Coeffb0 = 0.0
Coeffb1 = 0.0
Coeffb2 = 0.0
Coeffb0Salt = 0.0
Coeffb1Salt = 0.0
Coeffb2Salt = 0.0
StressLeaf = 0.0
StressSenescence = 0.0
DayFraction = 0.0
GDDayFraction = 0.0
CGCref = 0.0
GDDCGCref = 0.0
TimeSenescence = 0.0
SumKcTop = 0.0
SumKcTopStress = 0.0
SumKci = 0.0
CCoTotal = 0.0
CCxTotal = 0.0
CDCTotal = 0.0
GDDCDCTotal = 0.0
CCxCropWeedsNoSFstress = 0.0
WeedRCi = 0.0
CCiActualWeedInfested = 0.0
fWeedNoS = 0.0
Zeval = 0.0
BprevSum = 0.0
YprevSum = 0.0
SumGDDcuts = 0.0
HItimesBEF = 0.0
ScorAT1 = 0.0
ScorAT2 = 0.0
HItimesAT1 = 0.0
HItimesAT2 = 0.0
HItimesAT = 0.0
alfaHI = 0.0
alfaHIAdj = 0.0
tDaysZmin = 0.0
tGDDZmin = 0.0

# specific for StandAlone
PreviousSumETo = 0.0
PreviousSumGDD = 0.0
PreviousBmob = 0.0
PreviousBsto = 0.0
StageCode = 0
PreviousDayNr = 0
NoYear = False

DayNri = 0
RepeatToDay = 0
IrriInterval = 0
Tadj = 0
GDDTadj = 0
DayLastCut = 0
NrCut = 0
SumInterval = 0
PreviousStressLevel = 0
StressSFadjNEW = 0

RainDataSet = [rep_DayEventDbl() for _ in range(31)]

@dataclass
class rep_Transfer:
    Store: bool = False
    # transfer of assimilates from above ground parts to root system is active

    Mobilize: bool = False
    # transfer of assimialtes from root system to above ground parts is active

    ToMobilize: float = 0.0
    # Total mass of assimilates (ton/ha) to mobilize at start of the season

    Bmobilized: float = 0.0
    # Cumulative sum of assimilates (ton/ha) mobilized form root system

@dataclass
class rep_StressTot:
    Salt: float = 0.0
    # Undocumented

    Temp: float = 0.0
    # Undocumented

    Exp: float = 0.0
    # Undocumented

    Sto: float = 0.0
    # Undocumented

    Weed: float = 0.0
    # Undocumented

    NrD: int = 0
    # Undocumented

@dataclass
class repIrriInfoRecord:
    NoMoreInfo: bool = False
    # Undocumented

    FromDay: int = 0
    # Undocumented

    ToDay: int = 0
    # Undocumented

    TimeInfo: int = 0
    # Undocumented

    DepthInfo: int = 0
    # Undocumented

@dataclass
class rep_plotPar:
    PotVal: float = 0.0
    ActVal: float = 0.0
    # Undocumented

@dataclass
class rep_GwTable:
    DNr1: int = 0
    DNr2: int = 0
    # Undocumented

    Z1: int = 0
    Z2: int = 0
    # cm

    EC1: float = 0.0
    EC2: float = 0.0
    # dS/m


@dataclass
class repCutInfoRecord:
    NoMoreInfo: bool = False
    # Undocumented

    FromDay: int = 0
    # Undocumented

    ToDay: int = 0
    # Undocumented

    IntervalInfo: int = 0
    # Undocumented

    IntervalGDD: float = 0.0
    # Undocumented

    MassInfo: float = 0.0
    # Undocumented

PreviousSum = rep_sum()
GwTable = rep_GwTable()
PlotVarCrop = rep_plotPar()

IrriInfoRecord1 = repIrriInfoRecord()
IrriInfoRecord2 = repIrriInfoRecord()

StressTot = rep_StressTot()

CutInfoRecord1 = repCutInfoRecord()
CutInfoRecord2 = repCutInfoRecord()

Transfer = rep_Transfer()

def GetDayNri():
    return DayNri

def SetDayNri(DayNri_in):
    global DayNri
    DayNri = DayNri_in

def GetRepeatToDay():
    return RepeatToDay

def SetRepeatToDay(RepeatToDay_in):
    global RepeatToDay
    RepeatToDay = RepeatToDay_in

def GetTransfer():
    # Getter for the "Transfer" global variable.
    return Transfer

def SetTransfer(value):
    # Setter for the "Transfer" global variable.
    global Transfer
    Transfer = value

def GetTransfer_Store():
    # Getter for the "Store" field of the "Transfer" global variable.
    return Transfer.Store

def SetTransfer_Store(Store):
    # Setter for the "Store" field of the "Transfer" global variable.
    global Transfer
    Transfer.Store = Store

def GetTransfer_Mobilize():
    # Getter for the "Mobilize" field of the "Transfer" global variable.
    return Transfer.Mobilize

def SetTransfer_Mobilize(Mobilize):
    # Setter for the "Mobilize" field of the "Transfer" global variable.
    global Transfer
    Transfer.Mobilize = Mobilize

def GetTransfer_ToMobilize():
    # Getter for the "ToMobilize" field of the "Transfer" global variable.
    return Transfer.ToMobilize

def SetTransfer_ToMobilize(ToMobilize):
    # Setter for the "ToMobilize" field of the "Transfer" global variable.
    global Transfer
    Transfer.ToMobilize = ToMobilize

def GetTransfer_Bmobilized():
    # Getter for the "Bmobilized" field of the "Transfer" global variable.
    return Transfer.Bmobilized

def SetTransfer_Bmobilized(Bmobilized):
    # Setter for the "Bmobilized" field of the "Transfer" global variable.
    global Transfer
    Transfer.Bmobilized = Bmobilized

"""
def GetIrriInfoRecord1():
    # Getter for the "IrriInfoRecord1" global variable.
    return IrriInfoRecord1

def SetIrriInfoRecord1(value):
    # Setter for the "IrriInfoRecord1" global variable.
    global IrriInfoRecord1
    IrriInfoRecord1 = value
"""

def GetIrriInfoRecord1():
    # Getter for the "IrriInfoRecord1" global variable.
    return repIrriInfoRecord(
        NoMoreInfo=IrriInfoRecord1.NoMoreInfo,
        FromDay=IrriInfoRecord1.FromDay,
        ToDay=IrriInfoRecord1.ToDay,
        TimeInfo=IrriInfoRecord1.TimeInfo,
        DepthInfo=IrriInfoRecord1.DepthInfo,
    )


def SetIrriInfoRecord1(value):
    # Setter for the "IrriInfoRecord1" global variable.
    global IrriInfoRecord1
    IrriInfoRecord1 = repIrriInfoRecord(
        NoMoreInfo=value.NoMoreInfo,
        FromDay=value.FromDay,
        ToDay=value.ToDay,
        TimeInfo=value.TimeInfo,
        DepthInfo=value.DepthInfo,
    )

def GetIrriInfoRecord1_NoMoreInfo():
    # Getter for the "NoMoreInfo" field of the "IrriInfoRecord1" global variable.
    return IrriInfoRecord1.NoMoreInfo

def SetIrriInfoRecord1_NoMoreInfo(NoMoreInfo):
    # Setter for the "NoMoreInfo" field of the "IrriInfoRecord1" global variable.
    global IrriInfoRecord1
    IrriInfoRecord1.NoMoreInfo = NoMoreInfo

def GetIrriInfoRecord1_FromDay():
    # Getter for the "FromDay" field of the "IrriInfoRecord1" global variable.
    return IrriInfoRecord1.FromDay

def SetIrriInfoRecord1_FromDay(FromDay):
    # Setter for the "FromDay" field of the "IrriInfoRecord1" global variable.
    global IrriInfoRecord1
    IrriInfoRecord1.FromDay = FromDay

def GetIrriInfoRecord1_ToDay():
    # Getter for the "ToDay" field of the "IrriInfoRecord1" global variable.
    return IrriInfoRecord1.ToDay

def SetIrriInfoRecord1_ToDay(ToDay):
    # Setter for the "ToDay" field of the "IrriInfoRecord1" global variable.
    global IrriInfoRecord1
    IrriInfoRecord1.ToDay = ToDay

def GetIrriInfoRecord1_TimeInfo():
    # Getter for the "TimeInfo" field of the "IrriInfoRecord1" global variable.
    return IrriInfoRecord1.TimeInfo

def SetIrriInfoRecord1_TimeInfo(TimeInfo):
    # Setter for the "TimeInfo" field of the "IrriInfoRecord1" global variable.
    global IrriInfoRecord1
    IrriInfoRecord1.TimeInfo = TimeInfo

def GetIrriInfoRecord1_DepthInfo():
    # Getter for the "DepthInfo" field of the "IrriInfoRecord1" global variable.
    return IrriInfoRecord1.DepthInfo

def SetIrriInfoRecord1_DepthInfo(DepthInfo):
    # Setter for the "DepthInfo" field of the "IrriInfoRecord1" global variable.
    global IrriInfoRecord1
    IrriInfoRecord1.DepthInfo = DepthInfo

"""
def GetIrriInfoRecord2():
    # Getter for the "IrriInfoRecord2" global variable.
    return IrriInfoRecord2
"""

def GetIrriInfoRecord2():
    # Getter for the "IrriInfoRecord2" global variable.
    return repIrriInfoRecord(
        NoMoreInfo=IrriInfoRecord2.NoMoreInfo,
        FromDay=IrriInfoRecord2.FromDay,
        ToDay=IrriInfoRecord2.ToDay,
        TimeInfo=IrriInfoRecord2.TimeInfo,
        DepthInfo=IrriInfoRecord2.DepthInfo,
    )

"""
def SetIrriInfoRecord2(value):
    # Setter for the "IrriInfoRecord2" global variable.
    global IrriInfoRecord2
    IrriInfoRecord2 = value
"""

def SetIrriInfoRecord2(value):
    # Setter for the "IrriInfoRecord2" global variable.
    global IrriInfoRecord2
    IrriInfoRecord2 = repIrriInfoRecord(
        NoMoreInfo=value.NoMoreInfo,
        FromDay=value.FromDay,
        ToDay=value.ToDay,
        TimeInfo=value.TimeInfo,
        DepthInfo=value.DepthInfo,
    )

def GetIrriInfoRecord2_NoMoreInfo():
    # Getter for the "NoMoreInfo" field of the "IrriInfoRecord2" global variable.
    return IrriInfoRecord2.NoMoreInfo

def SetIrriInfoRecord2_NoMoreInfo(NoMoreInfo):
    # Setter for the "NoMoreInfo" field of the "IrriInfoRecord2" global variable.
    global IrriInfoRecord2
    IrriInfoRecord2.NoMoreInfo = NoMoreInfo

def GetIrriInfoRecord2_FromDay():
    # Getter for the "FromDay" field of the "IrriInfoRecord2" global variable.
    return IrriInfoRecord2.FromDay

def SetIrriInfoRecord2_FromDay(FromDay):
    # Setter for the "FromDay" field of the "IrriInfoRecord2" global variable.
    global IrriInfoRecord2
    IrriInfoRecord2.FromDay = FromDay

def GetIrriInfoRecord2_ToDay():
    # Getter for the "ToDay" field of the "IrriInfoRecord2" global variable.
    return IrriInfoRecord2.ToDay

def SetIrriInfoRecord2_ToDay(ToDay):
    # Setter for the "ToDay" field of the "IrriInfoRecord2" global variable.
    global IrriInfoRecord2
    IrriInfoRecord2.ToDay = ToDay

def GetIrriInfoRecord2_TimeInfo():
    # Getter for the "TimeInfo" field of the "IrriInfoRecord2" global variable.
    return IrriInfoRecord2.TimeInfo

def SetIrriInfoRecord2_TimeInfo(TimeInfo):
    # Setter for the "TimeInfo" field of the "IrriInfoRecord2" global variable.
    global IrriInfoRecord2
    IrriInfoRecord2.TimeInfo = TimeInfo

def GetIrriInfoRecord2_DepthInfo():
    # Getter for the "DepthInfo" field of the "IrriInfoRecord2" global variable.
    return IrriInfoRecord2.DepthInfo

def SetIrriInfoRecord2_DepthInfo(DepthInfo):
    # Setter for the "DepthInfo" field of the "IrriInfoRecord2" global variable.
    global IrriInfoRecord2
    IrriInfoRecord2.DepthInfo = DepthInfo

def GetPlotVarCrop ():
    # Getter for the "PlotVarCrop" global variable.
    return PlotVarCrop

def SetPlotVarCrop (PlotVarCrop_in):
    # Getter for the "PlotVarCrop" global variable.
    global PlotVarCrop
    PlotVarCrop = PlotVarCrop_in

def SetPlotVarCrop_PotVal(PotVal):
    # Setter for the "PlotVarCrop" global variable.
    global PlotVarCrop
    PlotVarCrop.PotVal = PotVal

def SetPlotVarCrop_ActVal(ActVal):
    # Setter for the "PlotVarCrop" global variable.
    global PlotVarCrop
    PlotVarCrop.ActVal = ActVal

def GetPlotVarCrop_ActVal():
    # Getter for the "PlotVarCrop" global variable.
    global PlotVarCrop
    return PlotVarCrop.ActVal

def GetPlotVarCrop_PotVal():
    # Getter for the "PlotVarCrop" global variable.
    global PlotVarCrop
    return PlotVarCrop.PotVal

def GetZeval():
    # Getter for the "Zeval" global variable.
    return Zeval

def SetZeval(Zeval_in):
    # Setter for the "Zeval" global variable.
    global Zeval
    Zeval = Zeval_in

def GetDayNr1Eval():
    # Getter for the "DayNr1Eval" global variable.
    return DayNr1Eval

def SetDayNr1Eval(DayNr1Eval_in):
    # Setter for the "DayNr1Eval" global variable.
    global DayNr1Eval
    DayNr1Eval = DayNr1Eval_in

def GetDayNrEval():
    # Getter for the "DayNrEval" global variable.
    return DayNrEval

def SetDayNrEval(DayNrEval_in):
    # Setter for the "DayNrEval" global variable.
    global DayNrEval
    DayNrEval = DayNrEval_in

def GetLineNrEval():
    # Getter for the "LineNrEval" global variable.
    return LineNrEval

def SetLineNrEval(LineNrEval_in):
    # Setter for the "LineNrEval" global variable.
    global LineNrEval
    LineNrEval = LineNrEval_in

def GetGwTable():
    # Getter for the "GetGwTable" global variable.
    return GwTable

def SetGwTable(GwTable_in):
    # Setter for the "GetGwTable" global variable.
    global GwTable
    GwTable = GwTable_in

def GetGwTable_DNr1():
    # Getter for the "GwTable" global variable.
    return GwTable.DNr1

def SetGwTable_DNr1(DNr1):
    # Setter for the "GwTable" global variable.
    global GwTable
    GwTable.DNr1 = DNr1

def GetGwTable_DNr2():
    # Getter for the "GwTable" global variable.
    return GwTable.DNr2

def SetGwTable_DNr2(DNr2):
    # Setter for the "GwTable" global variable.
    global GwTable
    GwTable.DNr2 = DNr2

def GetGwTable_Z1():
    # Getter for the "GwTable" global variable.
    return GwTable.Z1

def SetGwTable_Z1(Z1):
    # Setter for the "GwTable" global variable.
    global GwTable
    GwTable.Z1 = Z1

def GetGwTable_Z2():
    # Getter for the "GwTable" global variable.
    return GwTable.Z2

def SetGwTable_Z2(Z2):
    # Setter for the "GwTable" global variable.
    global GwTable
    GwTable.Z2 = Z2

def GetGwTable_EC1():
    # Getter for the "GwTable" global variable.
    return GwTable.EC1

def SetGwTable_EC1(EC1):
    # Setter for the "GwTable" global variable.
    global GwTable
    GwTable.EC1 = EC1

def GetGwTable_EC2():
    # Getter for the "GwTable" global variable.
    return GwTable.EC2

def SetGwTable_EC2(EC2):
    # Setter for the "GwTable" global variable.
    global GwTable
    GwTable.EC2 = EC2

def GetNextSimFromDayNr():
    # Getter for the "NextSimFromDayNr" global variable.
    return NextSimFromDayNr

def SetNextSimFromDayNr(NextSimFromDayNr_in):
    # Setter for the "NextSimFromDayNr " global variable.
    global NextSimFromDayNr
    NextSimFromDayNr = NextSimFromDayNr_in

def GetStageCode():
    # Getter for the "StageCode" global variable.
    return StageCode

def SetStageCode(StageCode_in):
    # Setter for the "StageCode" global variable.
    global StageCode
    StageCode = StageCode_in

def GetPreviousDayNr():
    # Getter for the "PreviousDayNr" global variable.
    return PreviousDayNr

def SetPreviousDayNr(PreviousDayNr_in):
    # Setter for the "PreviousDayNr" global variable.
    global PreviousDayNr
    PreviousDayNr = PreviousDayNr_in

def GetLastIrriDAP():
    # Getter for the "LastIrriDAP" global variable.
    return LastIrriDAP

def SetLastIrriDAP(LastIrriDAP_in):
    # Setter for the "LastIrriDAP" global variable.
    global LastIrriDAP
    LastIrriDAP = LastIrriDAP_in

def GetNoYear():
    # Getter for the "NoYear" global variable.
    return NoYear

def SetNoYear(NoYear_in):
    # Setter for the "NoYear" global variable.
    global NoYear
    NoYear = NoYear_in

def GetBin():
    # Getter for the "Bin" global variable.
    return Bin

def SetBin(Bin_in):
    # Setter for the "Bin" global variable.
    global Bin
    Bin = Bin_in

def GetBout():
    # Getter for the "Bout" global variable.
    return Bout

def SetBout(Bout_in):
    # Setter for the "Bout" global variable.
    global Bout
    Bout = Bout_in

def GetGDDayi():
    # Getter for the "GDDayi" global variable.
    return GDDayi

def SetGDDayi(GDDayi_in):
    # Setter for the "GDDayi" global variable.
    global GDDayi
    GDDayi = GDDayi_in

def GetFracBiomassPotSF():
    # Getter for the "FracBiomassPotSF" global variable.
    return FracBiomassPotSF

def SetFracBiomassPotSF(FracBiomassPotSF_in):
    # Setter for the "FracBiomassPotSF" global variable.
    global FracBiomassPotSF
    FracBiomassPotSF = FracBiomassPotSF_in

def GetCO2i():
    # Getter for the "CO2i" global variable.
    return CO2i

def SetCO2i(CO2i_in):
    # Setter for the "CO2i" global variable.
    global CO2i
    CO2i = CO2i_in

def GetStressTot():
    # Getter for the "StressTot" global variable.
    return StressTot

def SetStressTot(value):
    # Setter for the "StressTot" global variable.
    global StressTot
    StressTot = value

def GetStressTot_Salt():
    # Getter for the "Salt" field of the "StressTot" global variable.
    return StressTot.Salt

def SetStressTot_Salt(Salt):
    # Setter for the "Salt" field of the "StressTot" global variable.
    global StressTot
    StressTot.Salt = Salt

def GetStressTot_Temp():
    # Getter for the "Temp" field of the "StressTot" global variable.
    return StressTot.Temp

def SetStressTot_Temp(Temp):
    # Setter for the "Temp" field of the "StressTot" global variable.
    global StressTot
    StressTot.Temp = Temp

def GetStressTot_Exp():
    # Getter for the "Exp" field of the "StressTot" global variable.
    return StressTot.Exp

def SetStressTot_Exp(Exp):
    # Setter for the "Exp" field of the "StressTot" global variable.
    global StressTot
    StressTot.Exp = Exp

def GetStressTot_Sto():
    # Getter for the "Sto" field of the "StressTot" global variable.
    return StressTot.Sto

def SetStressTot_Sto(Sto):
    # Setter for the "Sto" field of the "StressTot" global variable.
    global StressTot
    StressTot.Sto = Sto

def GetStressTot_Weed():
    # Getter for the "Weed" field of the "StressTot" global variable.
    return StressTot.Weed

def SetStressTot_Weed(Weed):
    # Setter for the "Weed" field of the "StressTot" global variable.
    global StressTot
    StressTot.Weed = Weed

def GetStressTot_NrD():
    # Getter for the "NrD" field of the "StressTot" global variable.
    return StressTot.NrD

def SetStressTot_NrD(NrD):
    # Setter for the "NrD" field of the "StressTot" global variable.
    global StressTot
    StressTot.NrD = NrD

def SetTheProjectFile(str_):
    global TheProjectFile
    TheProjectFile = str_

def GetTheProjectFile():
    return TheProjectFile

def SetfIrrInfo_filename(s: str):
    global fIrrInfo_filename
    fIrrInfo_filename = s

def GetfIrrInfo_filename() -> str:
    return fIrrInfo_filename

def SetfHarvest_filename(s: str):
    global fHarvest_filename
    fHarvest_filename = s

def GetfHarvest_filename() -> str:
    return fHarvest_filename

def SetfEval_filename(s: str):
    global fEval_filename
    fEval_filename = s

def GetfEval_filename() -> str:
    return fEval_filename

def fRun_open(filename: str, mode: str):
    global fRun
    full_path = ResolvePath(filename)
    fRun = open_file(full_path, mode)

def fDaily_open(filename: str, mode: str):
    global fDaily
    full_path = ResolvePath(filename)
    fDaily = open_file(full_path, mode)

def fIrrInfo_open(filename: str, mode: str):
    global fIrrInfo
    full_path = ResolvePath(filename)
    fIrrInfo = open_file(full_path, mode)

def fHarvest_open(filename: str, mode: str):
    global fHarvest
    full_path = ResolvePath(filename)
    fHarvest = open_file(full_path, mode)

def fEval_open(filename: str, mode: str):
    global fEval
    full_path = ResolvePath(filename)
    fEval = open_file(full_path, mode)

def fEval_close():
    global fEval_lines, fEval_pos, fEval_iostat, fEval

    fEval_lines = []
    fEval_pos = 0
    fEval_iostat = 0

    if fEval is not None:
        try:
            fEval.close()
        except Exception:
            pass

        fEval = None

def fEval_erase():
    full_path = ResolvePath(GetfEval_filename())
    os.unlink(full_path)

def GetPreviousSum():
    # Getter for the "PreviousSum" global variable.
    return PreviousSum

def SetPreviousSum(PreviusSum_in):
    # Setter for the "PreviousSum" global variable.
    global PreviusSum
    PreviusSum = PreviusSum_in

def GetPreviousSum_Epot():
    # Getter for the "Epot" attribute of the global "PreviousSum" variable.
    return PreviousSum.Epot

def SetPreviousSum_Epot(Epot):
    # Setter for the "Epot" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Epot = Epot

def GetPreviousSum_Tpot():
    # Getter for the "Tpot" attribute of the global "PreviousSum" variable.
    return PreviousSum.Tpot

def SetPreviousSum_Tpot(Tpot):
    # Setter for the "Tpot" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Tpot = Tpot

def GetPreviousSum_Rain():
    # Getter for the "Rain" attribute of the global "PreviousSum" variable.
    return PreviousSum.Rain

def SetPreviousSum_Rain(Rain):
    # Setter for the "Rain" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Rain = Rain

def GetPreviousSum_Irrigation():
    # Getter for the "Irrigation" attribute of the global "PreviousSum" variable.
    return PreviousSum.Irrigation

def SetPreviousSum_Irrigation(Irrigation):
    # Setter for the "Irrigation" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Irrigation = Irrigation

def GetPreviousSum_Infiltrated():
    # Getter for the "Infiltrated" attribute of the global "PreviousSum" variable.
    return PreviousSum.Infiltrated

def SetPreviousSum_Infiltrated(Infiltrated):
    # Setter for the "Infiltrated" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Infiltrated = Infiltrated

def GetPreviousSum_Runoff():
    # Getter for the "Runoff" attribute of the global "PreviousSum" variable.
    return PreviousSum.Runoff

def SetPreviousSum_Runoff(Runoff):
    # Setter for the "Runoff" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Runoff = Runoff

def GetPreviousSum_Drain():
    # Getter for the "Drain" attribute of the global "PreviousSum" variable.
    return PreviousSum.Drain

def SetPreviousSum_Drain(Drain):
    # Setter for the "Drain" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Drain = Drain

def GetPreviousSum_Eact():
    # Getter for the "Eact" attribute of the global "PreviousSum" variable.
    return PreviousSum.Eact

def SetPreviousSum_Eact(Eact):
    # Setter for the "Eact" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Eact = Eact

def GetPreviousSum_Tact():
    # Getter for the "Tact" attribute of the global "PreviousSum" variable.
    return PreviousSum.Tact

def SetPreviousSum_Tact(Tact):
    # Setter for the "Tact" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Tact = Tact

def GetPreviousSum_TrW():
    # Getter for the "TrW" attribute of the global "PreviousSum" variable.
    return PreviousSum.TrW

def SetPreviousSum_TrW(TrW):
    # Setter for the "TrW" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.TrW = TrW

def GetPreviousSum_ECropCycle():
    # Getter for the "ECropCycle" attribute of the global "PreviousSum" variable.
    return PreviousSum.ECropCycle

def SetPreviousSum_ECropCycle(ECropCycle):
    # Setter for the "ECropCycle" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.ECropCycle = ECropCycle

def GetPreviousSum_CRwater():
    # Getter for the "CRwater" attribute of the global "PreviousSum" variable.
    return PreviousSum.CRwater

def SetPreviousSum_CRwater(CRwater):
    # Setter for the "CRwater" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.CRwater = CRwater

def GetPreviousSum_Biomass():
    # Getter for the "Biomass" attribute of the global "PreviousSum" variable.
    return PreviousSum.Biomass

def SetPreviousSum_Biomass(Biomass):
    # Setter for the "Biomass" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.Biomass = Biomass

def GetPreviousSum_YieldPart():
    # Getter for the "YieldPart" attribute of the global "PreviousSum" variable.
    return PreviousSum.YieldPart

def SetPreviousSum_YieldPart(YieldPart):
    # Setter for the "YieldPart" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.YieldPart = YieldPart

def GetPreviousSum_BiomassPot():
    # Getter for the "BiomassPot" attribute of the global "PreviousSum" variable.
    return PreviousSum.BiomassPot

def SetPreviousSum_BiomassPot(BiomassPot):
    # Setter for the "BiomassPot" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.BiomassPot = BiomassPot

def GetPreviousSum_BiomassUnlim():
    # Getter for the "BiomassUnlim" attribute of the global "PreviousSum" variable.
    return PreviousSum.BiomassUnlim

def SetPreviousSum_BiomassUnlim(BiomassUnlim):
    # Setter for the "BiomassUnlim" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.BiomassUnlim = BiomassUnlim

def GetPreviousSum_BiomassTot():
    # Getter for the "BiomassTot" attribute of the global "PreviousSum" variable.
    return PreviousSum.BiomassTot

def SetPreviousSum_BiomassTot(BiomassTot):
    # Setter for the "BiomassTot" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.BiomassTot = BiomassTot

def GetPreviousSum_SaltIn():
    # Getter for the "SaltIn" attribute of the global "PreviousSum" variable.
    return PreviousSum.SaltIn

def SetPreviousSum_SaltIn(SaltIn):
    # Setter for the "SaltIn" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.SaltIn = SaltIn

def GetPreviousSum_SaltOut():
    # Getter for the "SaltOut" attribute of the global "PreviousSum" variable.
    return PreviousSum.SaltOut

def SetPreviousSum_SaltOut(SaltOut):
    # Setter for the "SaltOut" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.SaltOut = SaltOut

def GetPreviousSum_CRSalt():
    # Getter for the "CRSalt" attribute of the global "PreviousSum" variable.
    return PreviousSum.CRSalt

def SetPreviousSum_CRSalt(CRSalt):
    # Setter for the "CRSalt" attribute of the global "PreviousSum" variable.
    global PreviousSum
    PreviousSum.CRSalt = CRSalt

def GetSumETo():
    # Getter for the "SumETo" global variable.
    return SumETo

def SetSumETo(SumETo_in):
    # Setter for the "SumETo" global variable.
    global SumETo
    SumETo = SumETo_in

def GetSumGDD():
    # Getter for the "SumGDD" global variable.
    return SumGDD

def SetSumGDD(SumGDD_in):
    # Setter for the "SumGDD" global variable.
    global SumGDD
    SumGDD = SumGDD_in

def GetPreviousSumETo():
    # Getter for the "PreviousSumETo" global variable.
    return PreviousSumETo

def SetPreviousSumETo(PreviousSumETo_in):
    # Setter for the "PreviousSumETo" global variable.
    global PreviousSumETo
    PreviousSumETo = PreviousSumETo_in

def GetPreviousSumGDD():
    # Getter for the "PreviousSumGDD" global variable.
    return PreviousSumGDD

def SetPreviousSumGDD(PreviousSumGDD_in):
    # Setter for the "PreviousSumGDD" global variable.
    global PreviousSumGDD
    PreviousSumGDD = PreviousSumGDD_in

def GetPreviousBmob():
    # Getter for the "PreviousBmob" global variable.
    return PreviousBmob

def SetPreviousBmob(PreviousBmob_in):
    # Setter for the "PreviousBmob" global variable.
    global PreviousBmob
    PreviousBmob = PreviousBmob_in

def GetPreviousBsto():
    # Getter for the "PreviousBsto" global variable.
    return PreviousBsto

def SetPreviousBsto(PreviousBsto_in):
    # Setter for the "PreviousBsto" global variable.
    global PreviousBsto
    PreviousBsto = PreviousBsto_in

def GetWaterTableInProfile():
    # Getter for the "WaterTableInProfile" global variable.
    return WaterTableInProfile

def SetWaterTableInProfile(WaterTableInProfile_in):
    # Setter for the "WaterTableInProfile" global variable.
    global WaterTableInProfile
    WaterTableInProfile = WaterTableInProfile_in

def GetCutInfoRecord1():
    # Getter for the "CutInfoRecord1" global variable.
    return CutInfoRecord1

def SetCutInfoRecord1(value):
    # Setter for the "CutInfoRecord1" global variable.
    global CutInfoRecord1
    CutInfoRecord1 = value

def GetCutInfoRecord1_NoMoreInfo():
    # Getter for the "NoMoreInfo" field of the "CutInfoRecord1" global variable.
    return CutInfoRecord1.NoMoreInfo

def SetCutInfoRecord1_NoMoreInfo(NoMoreInfo):
    # Setter for the "NoMoreInfo" field of the "CutInfoRecord1" global variable.
    global CutInfoRecord1
    CutInfoRecord1.NoMoreInfo = NoMoreInfo

def GetCutInfoRecord1_FromDay():
    # Getter for the "FromDay" field of the "CutInfoRecord1" global variable.
    return CutInfoRecord1.FromDay

def SetCutInfoRecord1_FromDay(FromDay):
    # Setter for the "FromDay" field of the "CutInfoRecord1" global variable.
    global CutInfoRecord1
    CutInfoRecord1.FromDay = FromDay

def GetCutInfoRecord1_ToDay():
    # Getter for the "ToDay" field of the "CutInfoRecord1" global variable.
    return CutInfoRecord1.ToDay

def SetCutInfoRecord1_ToDay(ToDay):
    # Setter for the "ToDay" field of the "CutInfoRecord1" global variable.
    global CutInfoRecord1
    CutInfoRecord1.ToDay = ToDay

def GetCutInfoRecord1_IntervalInfo():
    # Getter for the "IntervalInfo" field of the "CutInfoRecord1" global variable.
    return CutInfoRecord1.IntervalInfo

def SetCutInfoRecord1_IntervalInfo(IntervalInfo):
    # Setter for the "IntervalInfo" field of the "CutInfoRecord1" global variable.
    global CutInfoRecord1
    CutInfoRecord1.IntervalInfo = IntervalInfo

def GetCutInfoRecord1_IntervalGDD():
    # Getter for the "IntervalGDD" field of the "CutInfoRecord1" global variable.
    return CutInfoRecord1.IntervalGDD

def SetCutInfoRecord1_IntervalGDD(IntervalGDD):
    # Setter for the "IntervalGDD" field of the "CutInfoRecord1" global variable.
    global CutInfoRecord1
    CutInfoRecord1.IntervalGDD = IntervalGDD

def GetCutInfoRecord1_MassInfo():
    # Getter for the "MassInfo" field of the "CutInfoRecord1" global variable.
    return CutInfoRecord1.MassInfo

def SetCutInfoRecord1_MassInfo(MassInfo):
    # Setter for the "MassInfo" field of the "CutInfoRecord1" global variable.
    global CutInfoRecord1
    CutInfoRecord1.MassInfo = MassInfo

def GetCutInfoRecord2():
    # Getter for the "CutInfoRecord2" global variable.
    return CutInfoRecord2

def SetCutInfoRecord2(value):
    # Setter for the "CutInfoRecord2" global variable.
    global CutInfoRecord2
    CutInfoRecord2 = value

def GetCutInfoRecord2_NoMoreInfo():
    # Getter for the "NoMoreInfo" field of the "CutInfoRecord2" global variable.
    return CutInfoRecord2.NoMoreInfo

def SetCutInfoRecord2_NoMoreInfo(NoMoreInfo):
    # Setter for the "NoMoreInfo" field of the "CutInfoRecord2" global variable.
    global CutInfoRecord2
    CutInfoRecord2.NoMoreInfo = NoMoreInfo

def GetCutInfoRecord2_FromDay():
    # Getter for the "FromDay" field of the "CutInfoRecord2" global variable.
    return CutInfoRecord2.FromDay

def SetCutInfoRecord2_FromDay(FromDay):
    # Setter for the "FromDay" field of the "CutInfoRecord2" global variable.
    global CutInfoRecord2
    CutInfoRecord2.FromDay = FromDay

def GetCutInfoRecord2_ToDay():
    # Getter for the "ToDay" field of the "CutInfoRecord2" global variable.
    return CutInfoRecord2.ToDay

def SetCutInfoRecord2_ToDay(ToDay):
    # Setter for the "ToDay" field of the "CutInfoRecord2" global variable.
    global CutInfoRecord2
    CutInfoRecord2.ToDay = ToDay

def GetCutInfoRecord2_IntervalInfo():
    # Getter for the "IntervalInfo" field of the "CutInfoRecord2" global variable.
    return CutInfoRecord2.IntervalInfo

def SetCutInfoRecord2_IntervalInfo(IntervalInfo):
    # Setter for the "IntervalInfo" field of the "CutInfoRecord2" global variable.
    global CutInfoRecord2
    CutInfoRecord2.IntervalInfo = IntervalInfo

def GetCutInfoRecord2_IntervalGDD():
    # Getter for the "IntervalGDD" field of the "CutInfoRecord2" global variable.
    return CutInfoRecord2.IntervalGDD

def SetCutInfoRecord2_IntervalGDD(IntervalGDD):
    # Setter for the "IntervalGDD" field of the "CutInfoRecord2" global variable.
    global CutInfoRecord2
    CutInfoRecord2.IntervalGDD = IntervalGDD

def GetCutInfoRecord2_MassInfo():
    # Getter for the "MassInfo" field of the "CutInfoRecord2" global variable.
    return CutInfoRecord2.MassInfo

def SetCutInfoRecord2_MassInfo(MassInfo):
    # Setter for the "MassInfo" field of the "CutInfoRecord2" global variable.
    global CutInfoRecord2
    CutInfoRecord2.MassInfo = MassInfo

def GetCoeffb0():
    # Getter for the "Coeffb0" global variable.
    return Coeffb0

def SetCoeffb0(Coeffb0_in):
    # Setter for the "Coeffb0" global variable.
    global Coeffb0
    Coeffb0 = Coeffb0_in

def GetCoeffb1():
    # Getter for the "Coeffb1" global variable.
    return Coeffb1

def SetCoeffb1(Coeffb1_in):
    # Setter for the "Coeffb1" global variable.
    global Coeffb1
    Coeffb1 = Coeffb1_in

def GetCoeffb2():
    # Getter for the "Coeffb2" global variable.
    return Coeffb2

def SetCoeffb2(Coeffb2_in):
    # Setter for the "Coeffb2" global variable.
    global Coeffb2
    Coeffb2 = Coeffb2_in

def GetCoeffb0Salt():
    # Getter for the "Coeffb0Salt" global variable.
    return Coeffb0Salt

def SetCoeffb0Salt(Coeffb0Salt_in):
    # Setter for the "Coeffb0Salt" global variable.
    global Coeffb0Salt
    Coeffb0Salt = Coeffb0Salt_in

def GetCoeffb1Salt():
    # Getter for the "Coeffb1Salt" global variable.
    return Coeffb1Salt

def SetCoeffb1Salt(Coeffb1Salt_in):
    # Setter for the "Coeffb1Salt" global variable.
    global Coeffb1Salt
    Coeffb1Salt = Coeffb1Salt_in

def GetCoeffb2Salt():
    # Getter for the "Coeffb2Salt" global variable.
    return Coeffb2Salt

def SetCoeffb2Salt(Coeffb2Salt_in):
    # Setter for the "Coeffb2Salt" global variable.
    global Coeffb2Salt
    Coeffb2Salt = Coeffb2Salt_in

def GetPreviousStressLevel():
    # Getter for the "PreviousStressLevel" global variable.
    return PreviousStressLevel

def SetPreviousStressLevel(PreviousStressLevel_in):
    # Setter for the "PreviousStressLevel" global variable.
    global PreviousStressLevel
    PreviousStressLevel = PreviousStressLevel_in

def GetStressSFadjNEW():
    # Getter for the "StressSFadjNEW" global variable.
    return StressSFadjNEW

def SetStressSFadjNEW(StressSFadjNEW_in):
    # Setter for the "StressSFadjNEW" global variable.
    global StressSFadjNEW
    StressSFadjNEW = StressSFadjNEW_in

def GetSumKcTop():
    # Getter for the "SumKcTop" global variable.
    return SumKcTop

def SetSumKcTop(SumKcTop_in):
    # Setter for the "SumKcTop" global variable.
    global SumKcTop
    
    SumKcTop = SumKcTop_in

def GetSumKcTopStress():
    # Getter for the "SumKcTopStress" global variable.
    return SumKcTopStress

def SetSumKcTopStress(SumKcTopStress_in):
    # Setter for the "SumKcTopStress" global variable.
    global SumKcTopStress
    SumKcTopStress = SumKcTopStress_in

def GetSumKci():
    # Getter for the "SumKci" global variable.
    return SumKci

def SetSumKci(SumKci_in):
    # Setter for the "SumKci" global variable.
    global SumKci
    SumKci = SumKci_in

def GetfWeedNoS():
    # Getter for the "fWeedNoS" global variable.
    return fWeedNoS

def SetfWeedNoS(fWeedNoS_in):
    # Setter for the "fWeedNoS" global variable.
    global fWeedNoS
    fWeedNoS = fWeedNoS_in

def GetCCxCropWeedsNoSFstress():
    # Getter for the "CCxCropWeedsNoSFstress" global variable.
    return CCxCropWeedsNoSFstress

def SetCCxCropWeedsNoSFstress(CCxCropWeedsNoSFstress_in):
    # Setter for the "CCxCropWeedsNoSFstress" global variable.
    global CCxCropWeedsNoSFstress
    CCxCropWeedsNoSFstress = CCxCropWeedsNoSFstress_in

def GetCCxTotal():
    # Getter for the "CCxTotal" global variable.
    return CCxTotal

def SetCCxTotal(CCxTotal_in):
    # Setter for the "CCxTotal" global variable.
    global CCxTotal
    CCxTotal = CCxTotal_in

def GetCDCTotal():
    # Getter for the "CDCTotal" global variable.
    return CDCTotal

def SetCDCTotal(CDCTotal_in):
    # Setter for the "CDCTotal" global variable.
    global CDCTotal
    CDCTotal = CDCTotal_in

def GetGDDCDCTotal():
    # Getter for the "GDDCDCTotal" global variable.
    return GDDCDCTotal

def SetGDDCDCTotal(GDDCDCTotal_in):
    # Setter for the "GDDCDCTotal" global variable.
    global GDDCDCTotal
    GDDCDCTotal = GDDCDCTotal_in

def GetCCoTotal():
    # Getter for the "CCoTotal" global variable.
    return CCoTotal

def SetCCoTotal(CCoTotal_in):
    # Setter for the "CCoTotal" global variable.
    global CCoTotal
    CCoTotal = CCoTotal_in

def GetStartMode():
    # Getter for the "StartMode" global variable.
    return StartMode

def SetStartMode(StartMode_in):
    # Setter for the "StartMode" global variable.
    global StartMode
    StartMode = StartMode_in

def GetEToDataSet():
    # Getter for the "EToDataSet" global variable.
    return EToDataSet

def SetEToDataSet(EToDataSet_in):
    # Setter for the "EToDataSet" global variable.
    global EToDataSet
    EToDataSet = EToDataSet_in

def GetEToDataSet_i(i):
    # Getter for individual elements of the "EToDataSet" global variable.
    i0 = i - 1
    return EToDataSet[i0]

def SetEToDataSet_i(i, EToDataSet_i):
    # Setter for individual element for the "EToDataSet" global variable.
    global EToDataSet
    i0 = i - 1
    EToDataSet[i0] = EToDataSet_i 

def GetEToDataSet_DayNr(i):
    # Getter for individual elements of the "EToDataSet" global variable.
    i0 = i - 1
    return EToDataSet[i0].DayNr

def SetEToDataSet_DayNr(i, DayNr_in):
    # Setter for individual elements of the "EToDataSet" global variable.
    global EToDataSet
    i0 = i - 1
    EToDataSet[i0].DayNr = DayNr_in

def GetEToDataSet_Param(i):
    # Getter for individual elements of the "EToDataSet" global variable.
    i0 = i - 1
    return EToDataSet[i0].Param

def SetEToDataSet_Param(i, Param_in):
    # Setter for individual elements of the "EToDataSet" global variable.
    global EToDataSet
    i0 = i - 1
    EToDataSet[i0].Param = Param_in

def GetRainDataSet():
    # Getter for the "RainDataSet" global variable.
    return RainDataSet

def SetRainDataSet(RainDataSet_in):
    # Setter for the "RainDatSet" global variable.
    global RainDataSet
    RainDataSet = RainDataSet_in

def GetRainDataSet_i(i):
    # Getter for individual elements of the "RainDataSet" global variable.
    i0 = i - 1
    return RainDataSet[i0]

def SetRainDataSet_i(i, RainDataSet_i):
    # Setter for individual element for the "RainDataSet" global variable.
    global RainDataSet
    i0 = i - 1
    RainDataSet[i0] = RainDataSet_i

def GetRainDataSet_DayNr(i):
    # Getter for individual elements of the "RainDataSet" global variable.
    i0 = i - 1
    return RainDataSet[i0].DayNr

def SetRainDataSet_DayNr(i, DayNr_in):
    # Setter for individual element for the "RainDataSet" global variable.
    global RainDataSet
    i0 = i - 1
    RainDataSet[i0].DayNr = DayNr_in

def GetRainDataSet_Param(i):
    # Getter for individual elements of the "RainDataSet" global variable.
    i0 = i - 1
    return RainDataSet[i0].Param

def SetRainDataSet_Param(i, Param_in):
    # Setter for individual element for the "RainDataSet" global variable.
    global RainDataSet
    i0 = i - 1
    RainDataSet[i0].Param = Param_in

def GetSumGDDPrev():
    # Getter for the "SumGDDPrev" global variable.
    return SumGDDPrev

def SetSumGDDPrev(SumGDDPrev_in):
    # Setter for the "SumGDDPrev" global variable.
    global SumGDDPrev
    SumGDDPrev = SumGDDPrev_in

def GetIrriInterval():
    # Getter for the "IrriInterval" global variable.
    return IrriInterval

def SetIrriInterval(IrriInterval_in):
    # Setter for the "IrriInterval" global variable.
    global IrriInterval
    IrriInterval = IrriInterval_in

def GetGlobalIrriECw():
    # etter for the "IrriInterval" global variable.
    return GlobalIrriECw

def SetGlobalIrriECw(GlobalIrriECw_in):
    # Setter for the "IrriInterval" global variable.
    global GlobalIrriECw
    GlobalIrriECw = GlobalIrriECw_in

def GetGDDTadj():
    # Getter for the "GDDTadj" global variable.
    return GDDTadj

def SetGDDTadj(GDDTadj_in):
    # Setter for the "GDDTadj" global variable.
    global GDDTadj
    GDDTadj = GDDTadj_in

def GetGDDayFraction():
    # Setter for the "GDDayFraction" global variable.
    return GDDayFraction

def SetGDDayFraction(GDDayFraction_in):
    # Setter for the "GDDayFraction" global variable.
    global GDDayFraction
    GDDayFraction = GDDayFraction_in

def GetTadj():
    # Getter for the "Tadj" global variable.
    return Tadj

def SetTadj(Tadj_in):
    # Setter for the "Tadj" global variable.
    global Tadj
    Tadj = Tadj_in

def GetDayFraction():
    # Getter for the "DayFraction" global variable.
    return DayFraction

def SetDayFraction(DayFraction_in):
    # Setter for the "DayFraction" global variable.
    global DayFraction
    DayFraction = DayFraction_in

def GetTimeSenescence():
    # Getter for the "TimeSenescence" global variable.
    return TimeSenescence

def SetTimeSenescence(TimeSenescence_in):
    # Setter for the "TimeSenescence" global variable.
    global TimeSenescence
    TimeSenescence = TimeSenescence_in

"""
def GetNoMoreCrop():
    # Setter for the "NoMoreCrop" global variable.
    return NoMoreCrop
"""

"""
def SetNoMoreCrop(NoMoreCrop_in):
    # Setter for the "NoMoreCrop" global variable.
    global NoMoreCrop
    NoMoreCrop = NoMoreCrop_in
"""

def GetZiprev():
    # Getter for the "Ziprev" global variable.
    return Ziprev

def SetZiprev(Ziprev_in):
    # Setter for the "Ziprev" global variable.
    global Ziprev
    Ziprev = Ziprev_in

def GetNrCut():
    # Getter for the "NrCut" global variable.
    return NrCut

def SetNrCut(NrCut_in):
    # Setter for the "NrCut" global variable.
    global NrCut
    NrCut = NrCut_in

def GetSumInterval():
    # Getter for the "SumInterval" global variable.
    return SumInterval

def SetSumInterval(SumInterval_in):
    # Setter for the "SumInterval" global variable.
    global SumInterval
    SumInterval = SumInterval_in

def GetSumGDDcuts():
    # Getter for the "SumGDDcuts" global variable.
    return SumGDDcuts

def SetSumGDDcuts(SumGDDcuts_in):
    # Setter for the "SumGDDcuts" global variable.
    global SumGDDcuts
    SumGDDcuts = SumGDDcuts_in

def GetBprevSum():
    # Getter for the "BprevSum" global variable.
    return BprevSum

def SetBprevSum(BprevSum_in):
    # Setter for the "BprevSum" global variable.
    global BprevSum
    BprevSum = BprevSum_in

def GetYprevSum():
    # Getter for the "YprevSum" global variable.
    return YprevSum

def SetYprevSum(YprevSum_in):
    # Setter for the "YprevSum" global variable.
    global YprevSum
    YprevSum = YprevSum_in

def GetDayLastCut():
    # Getter for the "DayLastCut" global variable.
    return DayLastCut

def SetDayLastCut(DayLastCut_in):
    # Setter for the "DayLastCut" global variable.
    global DayLastCut
    DayLastCut = DayLastCut_in

def GetCGCref():
    # Getter for the "CGCref" global variable.
    return CGCref

def SetCGCref(CGCref_in):
    # Setter for the "CGCref" global variable.
    global CGCref
    CGCref = CGCref_in

def GetGDDCGCref():
    # Getter for the "GDDCGCref" global variable.
    return GDDCGCref

def SetGDDCGCref(GDDCGCref_in):
    # Setter for the "GDDCGCref" global variable.
    global GDDCGCref
    GDDCGCref = GDDCGCref_in

def GetHItimesBEF():
    # Getter for the "HItimesBEF" global variable.
    return HItimesBEF

def SetHItimesBEF(HItimesBEF_in):
    # Setter for the "HItimesBEF" global variable.
    global HItimesBEF
    HItimesBEF = HItimesBEF_in

def GetHItimesAT1():
    # Getter for the "HItimesAT1" global variable.
    return HItimesAT1

def SetHItimesAT1(HItimesAT1_in):
    # Setter for the "HItimesAT1" global variable.
    global HItimesAT1
    HItimesAT1 = HItimesAT1_in

def GetHItimesAT2():
    # Getter for the "HItimesAT2" global variable.
    return HItimesAT2

def SetHItimesAT2(HItimesAT2_in):
    # Setter for the "HItimesAT2" global variable.
    global HItimesAT2
    HItimesAT2 = HItimesAT2_in

def GetHItimesAT():
    # Getter for the "HItimesAT" global variable.
    return HItimesAT

def SetHItimesAT(HItimesAT_in):
    # Setter for the "HItimesAT" global variable.
    global HItimesAT
    HItimesAT = HItimesAT_in

def GetalfaHI():
    # Getter for the "alfaHI" global variable.
    return alfaHI

def SetalfaHI(alfaHI_in):
    # Setter for the "alfaHI" global variable.
    global alfaHI
    alfaHI = alfaHI_in

def GetalfaHIAdj():
    # Getter for the "alfaHIAdj" global variable.
    return alfaHIAdj

def SetalfaHIAdj(alfaHIAdj_in):
    # Setter for the "alfaHIAdj" global variable.
    global alfaHIAdj
    alfaHIAdj = alfaHIAdj_in

def GetScorAT1():
    # Getter for the "ScorAT1" global variable.
    return ScorAT1

def SetScorAT1(ScorAT1_in):
    # Setter for the "ScorAT1" global variable.
    global ScorAT1
    ScorAT1 = ScorAT1_in

def GetScorAT2():
    # Getter for the "ScorAT2" global variable.
    return ScorAT2

def SetScorAT2(ScorAT2_in):
    # Setter for the "ScorAT2" global variable.
    global ScorAT2
    ScorAT2 = ScorAT2_in

def GetStressLeaf():
    # Getter for the "StressLeaf" global variable.
    return StressLeaf

def SetStressLeaf(StressLeaf_in):
    # Setter for the "StressLeaf" global variable.
    global StressLeaf
    StressLeaf = StressLeaf_in

def GetStressSenescence():
    # Getter for the "StressSenescence" global variable.
    return StressSenescence

def SetStressSenescence(StressSenescence_in):
    # Setter for the "StressSenescence" global variable.
    global StressSenescence
    StressSenescence = StressSenescence_in

def GetWeedRCi():
    # Getter for the "WeedRCi" global variable.
    return WeedRCi

def SetWeedRCi(WeedRCi_in):
    # Setter for the "WeedRCi" global variable.
    global WeedRCi
    WeedRCi = WeedRCi_in

def GetCCiActualWeedInfested():
    # Getter for the "CCiActualWeedInfested" global variable.
    return CCiActualWeedInfested

def SetCCiActualWeedInfested(CCiActualWeedInfested_in):
    # Setter for the "CCiActualWeedInfested" global variable.
    global CCiActualWeedInfested
    CCiActualWeedInfested = CCiActualWeedInfested_in




def fRun_write_bulk(items, default_advance=True, flush=True):
    global fRun

    if fRun is None:
        return

    try:
        chunks = []
        for it in items:
            if isinstance(it, tuple):
                line, advance = it
            else:
                line, advance = it, default_advance

            line = "" if line is None else str(line)
            line = line.rstrip("\n")  # evita duplicar saltos de línea

            chunks.append(line + "\n" if advance else line)

        fRun.write("".join(chunks))
        if flush:
            fRun.flush()
    except OSError:
        pass

def fDaily_write_bulk(items, default_advance=True, flush=True):
    global fDaily

    if fDaily is None:
        return

    try:
        chunks = []
        for it in items:
            if isinstance(it, tuple):
                line, advance = it
            else:
                line, advance = it, default_advance

            line = "" if line is None else str(line)
            line = line.rstrip("\n")

            chunks.append(line + "\n" if advance else line)

        fDaily.write("".join(chunks))
        if flush:
            fDaily.flush()
    except OSError:
        pass

def fIrrInfo_write_bulk(items, default_advance=True):
    global fIrrInfo

    if fIrrInfo is None:
        return

    try:
        chunks = []
        for it in items:
            if isinstance(it, tuple):
                line, advance = it
            else:
                line, advance = it, default_advance

            s = "" if line is None else str(line)
            s = s.rstrip("\n")
            chunks.append(s + ("\n" if advance else ""))

        fIrrInfo.write("".join(chunks))
    except OSError:
        pass

def fHarvest_write_bulk(items, default_advance=True):
    global fHarvest

    if fHarvest is None:
        return

    try:
        chunks = []
        for it in items:
            if isinstance(it, tuple):
                line, advance = it
            else:
                line, advance = it, default_advance

            s = "" if line is None else str(line)
            s = s.rstrip("\n")
            chunks.append(s + ("\n" if advance else ""))

        fHarvest.write("".join(chunks))
    except OSError:
        pass

def fEval_write_bulk(items, default_advance=True):
    global fEval

    if fEval is None:
        return

    try:
        chunks = []
        for it in items:
            if isinstance(it, tuple):
                line, advance = it
            else:
                line, advance = it, default_advance

            s = "" if line is None else str(line)
            s = s.rstrip("\n")
            chunks.append(s + ("\n" if advance else ""))

        fEval.write("".join(chunks))
    except OSError:
        pass


def OpenOutputRun(TheProjectType: int):
    totalname = ""
    tempstring = ""

    # select case (TheProjectType)
    if TheProjectType == typeproject_typepro:
        totalname = GetPathNameOutp() + GetOutputName() + "PROseason.OUT"
    elif TheProjectType == typeproject_typeprm:
        totalname = GetPathNameOutp() + GetOutputName() + "PRMseason.OUT"

    fRun_open(totalname, "w")

    # Unify writes (minimize I/O)
    header_lines = []

    tempstring = str(GetAquaCropDescriptionWithTimeStamp())
    header_lines.append(tempstring.rstrip())

    header_lines.append("")

    header_lines.append(
        "    RunNr     Day1   Month1    Year1     Rain      ETo       GD     CO2"
        "      Irri   Infilt   Runoff    Drain   Upflow        E     E/Ex       Tr      TrW   Tr/Trx"
        "    SaltIn   SaltOut    SaltUp  SaltProf"
        "     Cycle   SaltStr  FertStr  WeedStr  TempStr   ExpStr   StoStr"
        "  BioMass  Brelative   HI    Y(dry)  Y(fresh)    WPet      Bin     Bout     DayN   MonthN    YearN"
    )

    header_lines.append(
        "                                           mm       mm  degC.day    ppm"
        "        mm       mm       mm       mm       mm       mm        %       mm       mm        %"
        "    ton/ha    ton/ha    ton/ha    ton/ha"
        "      days       %        %        %        %        %        %  "
        "  ton/ha        %       %    ton/ha   ton/ha    kg/m3   ton/ha   ton/ha"
    )

    fRun_write_bulk(header_lines)

def OpenOutputDaily(TheProjectType: int):
    if TheProjectType == typeproject_typepro:
        totalname = GetPathNameOutp() + GetOutputName() + "PROday.OUT"
    elif TheProjectType == typeproject_typeprm:
        totalname = GetPathNameOutp() + GetOutputName() + "PRMday.OUT"
    else:
        totalname = ""

    fDaily_open(totalname, "w")

    fDaily_write_bulk([
        str(GetAquaCropDescriptionWithTimeStamp()).rstrip(),
    ])

def OpenOutputIrrInfo(TheProjectType: int):
    totalname = ""
    tempstring = ""

    # select case (TheProjectType)
    if TheProjectType == typeproject_typepro:
        totalname = GetPathNameOutp() + GetOutputName() + "PROirrInfo.OUT"
    elif TheProjectType == typeproject_typeprm:
        totalname = GetPathNameOutp() + GetOutputName() + "PRMirrInfo.OUT"

    SetfIrrInfo_filename(totalname)
    fIrrInfo_open(GetfIrrInfo_filename(), "w")

    tempstring = str(GetAquaCropDescriptionWithTimeStamp()).rstrip()
    fIrrInfo_write_bulk([tempstring])

def OpenPart1MultResults(TheProjectType: int):
    totalname = ""
    tempstring = ""

    # select case (TheProjectType)
    if TheProjectType == typeproject_typepro:
        totalname = GetPathNameOutp() + GetOutputName() + "PROharvests.OUT"
    elif TheProjectType == typeproject_typeprm:
        totalname = GetPathNameOutp() + GetOutputName() + "PRMharvests.OUT"

    SetfHarvest_filename(totalname)
    fHarvest_open(GetfHarvest_filename(), "w")

    tempstring = str(GetAquaCropDescriptionWithTimeStamp()).rstrip()

    fHarvest_write_bulk([
        tempstring,
        "Biomass and Yield at Multiple cuttings",
    ])

def InitializeSimulation(TheProjectFileStr: str, TheProjectType: int):
    SetTheProjectFile(TheProjectFileStr.strip())
    SetTactWeedInfested(0.0)
    OpenOutputRun(TheProjectType)  # open seasonal results .out

    if GetOutDaily():
        OpenOutputDaily(TheProjectType)  # Open Daily results .OUT
    if GetOut8Irri():
        OpenOutputIrrInfo(TheProjectType)  # Open Irrigation info results .OUT
    if GetPart1Mult():
        OpenPart1MultResults(TheProjectType)  # Open Multiple harvests in season .OUT

def InitializeRunPart1(NrRun: int, TheProjectType: int):
    # Part1 (before reading the climate) of the run initialization
    # Loads the run input from the project file
    # Initializes parameters and states
    # Calls InitializeSimulationRunPart1

    if TheProjectType == typeproject_typenone:
        # Do nothing
        return

    LoadSimulationRunProject(int(NrRun))

    AdjustCompartments()

    SumWaBal_temp = GetSumWaBal()
    GlobalZero(SumWaBal_temp)
    SetSumWaBal(SumWaBal_temp)

    PreviousSum_temp = GetPreviousSum()
    ResetPreviousSum(PreviousSum_temp)
    SetPreviousSum(PreviousSum_temp)

    InitializeSimulationRunPart1()

def AdjustForWatertable():
    Ztot = 0.0

    for compi in range(1, GetNrCompartments() + 1):
        Ztot = Ztot + GetCompartment_Thickness(compi)
        Zi = Ztot - GetCompartment_Thickness(compi) / 2.0

        if Zi >= (GetZiAqua() / 100.0):
            # compartment at or below groundwater table
            SetCompartment_theta(
                compi,
                GetSoilLayer_SAT(GetCompartment_Layer(compi)) / 100.0
            )
            Compi_temp = GetCompartment_i(compi)
            DetermineSaltContent(GetECiAqua(), Compi_temp)
            SetCompartment_i(compi, Compi_temp)

def GetGwtSet(DayNrIN: int, GwT):
    f0 = None
    FileNameFull = ""
    DayNr1Gwt = 0
    DNrini = 0
    i = 0
    dayi = 0
    monthi = 0
    yeari = 0
    Zini = 0
    yearACT = 0
    DayDouble = 0.0
    Zm = 0.0
    ECini = 0.0
    StringREAD = ""
    TheEnd = False

    # FileNameFull
    if GetGroundWaterFile() != "(None)":
        FileNameFull = GetGroundWaterFileFull()
    else:
        FileNameFull = GetPathNameProg().strip() + "GroundWater.AqC"

    # Bulk read (single disk I/O)
    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(FileNameFull).lstrip("/\\"),
        )
    )
    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        lines = f0.read().splitlines()

    pos = 0

    # Get DayNr1Gwt
    # read(f0,*) description / version / mode  (3 records)
    pos += 3

    # Fortran expects 3 more list-directed reads: dayi, monthi, yeari.
    # But some files (like the one you showed) don't have them.
    # We only consume them if the next 3 records are parseable as integers.
    def _can_parse_int_line(s: str) -> bool:
        if not s.strip():
            return False
        tok = s.split()[0]
        try:
            int(float(tok))
            return True
        except Exception:
            return False

    if (pos + 2) < len(lines) and _can_parse_int_line(lines[pos]) and _can_parse_int_line(lines[pos + 1]) and _can_parse_int_line(lines[pos + 2]):
        dayi = int(float(lines[pos].split()[0])); pos += 1
        monthi = int(float(lines[pos].split()[0])); pos += 1
        yeari = int(float(lines[pos].split()[0])); pos += 1
        DayNr1Gwt = DetermineDayNr(dayi, monthi, yeari)
    else:
        # Missing explicit day/month/year block in file:
        # keep pos as-is so the next "skip 3" lands on the first observation line.
        # Use an "undefined-year style" base similar to what these files implicitly represent.
        DayNr1Gwt = 1  # base day number (acts like 1 Jan 1901 in many parts of the codebase)

    # Read first observation
    # do i=1,3 read(f0,*)  -> skip 3 records
    pos += 3

    if pos >= len(lines):
        # no observation lines at all
        TheEnd = True
    else:
        StringREAD = lines[pos]; pos += 1
        # call SplitStringInThreeParams(StringREAD, DayDouble, Zm, GwT%EC2)
        DayDouble, Zm, GwT.EC2 = SplitStringInThreeParams(StringREAD)

        GwT.DNr2 = DayNr1Gwt + int(roundc(DayDouble, mold="int32")) - 1
        GwT.Z2 = int(roundc(Zm * 100.0, mold="int32"))
        TheEnd = False  # in Fortran this would only be true if read hit iostat_end here

    # Read next observations
    if TheEnd:
        # only one observation (or no observations)
        GwT.DNr1 = GetSimulation_FromDayNr()
        GwT.Z1 = GwT.Z2
        GwT.EC1 = GwT.EC2
        GwT.DNr2 = GetSimulation_ToDayNr()
        return GwT

    else:
        # defined year
        if DayNr1Gwt > 365:
            if DayNrIN < GwT.DNr2:
                # DayNrIN before 1st observation
                GwT.DNr1 = GetSimulation_FromDayNr()
                GwT.Z1 = GwT.Z2
                GwT.EC1 = GwT.EC2
            else:
                # DayNrIN after or at 1st observation
                while True:
                    GwT.DNr1 = GwT.DNr2
                    GwT.Z1 = GwT.Z2
                    GwT.EC1 = GwT.EC2

                    if pos >= len(lines):
                        break

                    StringREAD = lines[pos]; pos += 1
                    DayDouble = 0.0
                    Zm = 0.0
                    DayDouble, Zm, GwT.EC2 = SplitStringInThreeParams(StringREAD)

                    GwT.DNr2 = DayNr1Gwt + int(roundc(DayDouble, mold="int32")) - 1
                    GwT.Z2 = int(roundc(Zm * 100.0, mold="int32"))

                    if DayNrIN < GwT.DNr2:
                        TheEnd = True

                    if TheEnd:
                        break

                if not TheEnd:
                    # DayNrIN after last observation
                    GwT.DNr1 = GwT.DNr2
                    GwT.Z1 = GwT.Z2
                    GwT.EC1 = GwT.EC2
                    GwT.DNr2 = GetSimulation_ToDayNr()

        # undefined year
        if DayNr1Gwt <= 365:
            dayi, monthi, yearACT = DetermineDate(DayNrIN)

            if yearACT != 1901:
                # make 1st observation defined
                dtmp, mtmp, ytmp = DetermineDate(GwT.DNr2)
                GwT.DNr2 = DetermineDayNr(dtmp, mtmp, yearACT)

            if DayNrIN < GwT.DNr2:
                # DayNrIN before 1st observation
                while True:
                    if pos >= len(lines):
                        break

                    StringREAD = lines[pos]; pos += 1
                    DayDouble = 0.0
                    Zm = 0.0
                    DayDouble, Zm, GwT.EC1 = SplitStringInThreeParams(StringREAD)

                    GwT.DNr1 = DayNr1Gwt + int(roundc(DayDouble, mold="int32")) - 1
                    dtmp, mtmp, ytmp = DetermineDate(GwT.DNr1)
                    GwT.DNr1 = DetermineDayNr(dtmp, mtmp, yearACT)
                    GwT.Z1 = int(roundc(Zm * 100.0, mold="int32"))

                GwT.DNr1 = GwT.DNr1 - 365

            else:
                # save 1st observation
                DNrini = GwT.DNr2
                Zini = GwT.Z2
                ECini = GwT.EC2

                # DayNrIN after or at 1st observation
                while True:
                    GwT.DNr1 = GwT.DNr2
                    GwT.Z1 = GwT.Z2
                    GwT.EC1 = GwT.EC2

                    if pos >= len(lines):
                        break

                    StringREAD = lines[pos]; pos += 1
                    DayDouble = 0.0
                    Zm = 0.0
                    DayDouble, Zm, GwT.EC2 = SplitStringInThreeParams(StringREAD)

                    GwT.DNr2 = DayNr1Gwt + int(roundc(DayDouble, mold="int32")) - 1

                    if yearACT != 1901:
                        dtmp, mtmp, ytmp = DetermineDate(GwT.DNr2)
                        GwT.DNr2 = DetermineDayNr(dtmp, mtmp, yearACT)

                    GwT.Z2 = int(roundc(Zm * 100.0, mold="int32"))

                    if DayNrIN < GwT.DNr2:
                        TheEnd = True

                    if TheEnd:
                        break

                if not TheEnd:
                    # DayNrIN after last observation
                    GwT.DNr1 = GwT.DNr2
                    GwT.Z1 = GwT.Z2
                    GwT.EC1 = GwT.EC2
                    GwT.DNr2 = DNrini + 365
                    GwT.Z2 = Zini
                    GwT.EC2 = ECini

    return GwT

def InitializeSimulationRunPart1():
    # !! Part1 (before reading the climate) of the initialization of a run
    # !! Initializes parameters and states

    DNr1 = 0
    DNr2 = 0
    fWeed = 0.0
    fi = 0.0
    Cweed = 0
    Day1 = 0
    Month1 = 0
    Year1 = 0
    FertStress = 0
    GwTable_temp = None
    RedCGC_temp = 0
    RedCCX_temp = 0
    RCadj_temp = 0
    EffectStress_temp = None
    bool_temp = False
    Crop_DaysToFullCanopySF_temp = 0
    WaterTableInProfile_temp = False

    # ! 1. Adjustments at start
    # ! 1.1 Adjust soil water and salt content if water table IN soil profile
    WaterTableInProfile_temp = GetWaterTableInProfile()
    _res = CheckForWaterTableInProfile((GetZiAqua() / 100.0), GetCompartment(), WaterTableInProfile_temp)
    if _res is not None:
        WaterTableInProfile_temp = _res
    SetWaterTableInProfile(WaterTableInProfile_temp)
    if GetWaterTableInProfile():
        AdjustForWatertable()
    if not GetSimulParam_ConstGwt():
        GwTable_temp = GetGwTable()
        _res = GetGwtSet(GetSimulation_FromDayNr(), GwTable_temp)
        if _res is not None:
            GwTable_temp = _res
        SetGwTable(GwTable_temp)

    # ! 1.2 Check if FromDayNr simulation needs to be adjusted
    # ! from previous run if Keep initial SWC
    if (GetSWCiniFile() == "KeepSWC") and (GetNextSimFromDayNr() != undef_int):
        # ! assign the adjusted DayNr defined in previous run
        if GetNextSimFromDayNr() <= GetCrop_Day1():
            SetSimulation_FromDayNr(GetNextSimFromDayNr())
    SetNextSimFromDayNr(undef_int)

    # ! 2. initial settings for Crop
    SetCrop_pActStom(GetCrop_pdef())
    SetCrop_pSenAct(GetCrop_pSenescence())
    SetCrop_pLeafAct(GetCrop_pLeafDefUL())
    SetEvapoEntireSoilSurface(True)
    SetSimulation_EvapLimitON(False)
    SetSimulation_EvapWCsurf(0.0)
    SetSimulation_EvapZ(EvapZmin / 100.0)
    SetSimulation_SumEToStress(0.0)
    SetCCxWitheredTpotNoS(0.0)  # ! for calculation Maximum Biomass
                                # ! unlimited soil fertility
    SetSimulation_DayAnaero(0)  # ! days of anaerobic conditions in
                               # ! global root zone

    # ! germination
    if (GetCrop_Planting() == plant_Seed) and (GetSimulation_FromDayNr() <= GetCrop_Day1()):
        SetSimulation_Germinate(False)
    else:
        SetSimulation_Germinate(True)
        # ! since already germinated no protection required
        SetSimulation_ProtectedSeedling(False)

    # ! delayed germination
    SetSimulation_DelayedDays(0)

    # ! 3. create temperature file covering crop cycle
    if (GetTemperatureFile() != "(None)") and (GetTemperatureFile() != "(External)"):
        if GetSimulation_ToDayNr() < GetCrop_DayN():
            TemperatureFileCoveringCropPeriod(GetCrop_Day1(), GetSimulation_ToDayNr())
        else:
            TemperatureFileCoveringCropPeriod(GetCrop_Day1(), GetCrop_DayN())

    # ! 4. CO2 concentration during cropping period
    DNr1 = GetSimulation_FromDayNr()
    if GetCrop_Day1() > GetSimulation_FromDayNr():
        DNr1 = GetCrop_Day1()
    DNr2 = GetSimulation_ToDayNr()
    if GetCrop_DayN() < GetSimulation_ToDayNr():
        DNr2 = GetCrop_DayN()
    SetCO2i(CO2ForSimulationPeriod(DNr1, DNr2))

    # ! 5. seasonals stress coefficients
    bool_temp = (
        (GetCrop_ECemin() != undef_int)
        and (GetCrop_ECemax() != undef_int)
        and (GetCrop_ECemin() < GetCrop_ECemax())
    )
    SetSimulation_SalinityConsidered(bool_temp)
    if GetIrriMode() == IrriMode_Inet:
        SetSimulation_SalinityConsidered(False)

    SetStressTot_NrD(undef_int)
    SetStressTot_Salt(0.0)
    SetStressTot_Temp(0.0)
    SetStressTot_Exp(0.0)
    SetStressTot_Sto(0.0)
    SetStressTot_Weed(0.0)

    # ! 6. Soil fertility stress
    # ! Coefficients for soil fertility - biomass relationship
    # ! AND for Soil salinity - CCx/KsSto relationship
    RelationshipsForFertilityAndSaltStress()

    # ! No soil fertility stress
    if GetManagement_FertilityStress() <= 0:
        SetManagement_FertilityStress(0)

    # ! Reset soil fertility parameters to selected value in management
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

    FertStress = GetManagement_FertilityStress()
    RedCGC_temp = GetSimulation_EffectStress_RedCGC()
    RedCCX_temp = GetSimulation_EffectStress_RedCCX()
    Crop_DaysToFullCanopySF_temp = GetCrop_DaysToFullCanopySF()

    _res = TimeToMaxCanopySF(
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
        FertStress,
    )
    if isinstance(_res, tuple):
        if len(_res) >= 1:
            Crop_DaysToFullCanopySF_temp = _res[0]
        if len(_res) >= 2:
            RedCGC_temp = _res[1]
        if len(_res) >= 3:
            RedCCX_temp = _res[2]
        if len(_res) >= 4:
            FertStress = _res[3]

    SetCrop_DaysToFullCanopySF(Crop_DaysToFullCanopySF_temp)
    SetManagement_FertilityStress(FertStress)
    SetSimulation_EffectStress_RedCGC(RedCGC_temp)
    SetSimulation_EffectStress_RedCCX(RedCCX_temp)
    SetPreviousStressLevel(int(GetManagement_FertilityStress()))
    SetStressSFadjNEW(int(GetManagement_FertilityStress()))

    # ! soil fertility and GDDays
    if GetCrop_ModeCycle() == ModeCycle_GDDays:
        if GetManagement_FertilityStress() != 0:
            SetCrop_GDDaysToFullCanopySF(
                GrowingDegreeDays(
                    GetCrop_DaysToFullCanopySF(),
                    GetCrop_Day1(),
                    GetCrop_Tbase(),
                    GetCrop_Tupper(),
                    GetSimulParam_Tmin(),
                    GetSimulParam_Tmax(),
                )
            )
        else:
            SetCrop_GDDaysToFullCanopySF(GetCrop_GDDaysToFullCanopy())

    # ! Maximum sum Kc (for reduction WP in season if soil fertility stress)
    if (GetCrop_StressResponse_Calibrated() is True) and (GetManagement_FertilityStress() > 0):
        SetSumKcTop(
            SeasonalSumOfKcPot(
                GetCrop_DaysToCCini(),
                GetCrop_GDDaysToCCini(),
                GetCrop_DaysToGermination(),
                GetCrop_DaysToFullCanopy(),
                GetCrop_DaysToSenescence(),
                GetCrop_DaysToHarvest(),
                GetCrop_DaysToHarvest(),
                GetCrop_GDDaysToGermination(),
                GetCrop_GDDaysToFullCanopy(),
                GetCrop_GDDaysToSenescence(),
                GetCrop_GDDaysToHarvest(),
                GetCrop_CCo(),
                GetCrop_CCx(),
                GetCrop_CGC(),
                GetCrop_GDDCGC(),
                GetCrop_CDC(),
                GetCrop_GDDCDC(),
                GetCrop_KcTop(),
                GetCrop_KcDeclineCumul(),
                float(GetCrop_CCEffectEvapLate()),
                GetCrop_Tbase(),
                GetCrop_Tupper(),
                GetSimulParam_Tmin(),
                GetSimulParam_Tmax(),
                GetCrop_GDtranspLow(),
                GetCO2i(),
                GetCrop_ModeCycle(),
                True,
            )
        )
        SetSumKcTopStress(GetSumKcTop() * GetFracBiomassPotSF())
    else:
        SetSumKcTop(float(undef_int))
        SetSumKcTopStress(float(undef_int))
    SetSumKci(0.0)

    # ! 7. weed infestation and self-thinning of herbaceous perennial forage crops
    # ! CC expansion due to weed infestation and/or CC decrease as a result of
    # ! self-thinning
    # ! 7.1 initialize
    SetSimulation_RCadj(GetManagement_WeedRC())
    Cweed = 0
    if GetCrop_subkind() == subkind_Forage:
        fi = MultiplierCCxSelfThinning(
            int(GetSimulation_YearSeason()),
            int(GetCrop_YearCCx()),
            GetCrop_CCxRoot(),
        )
    else:
        fi = 1.0

    # ! 7.2 fweed
    if GetManagement_WeedRC() > 0:
        SetfWeedNoS(
            CCmultiplierWeed(
                GetManagement_WeedRC(),
                GetCrop_CCx(),
                GetManagement_WeedShape(),
            )
        )
        SetCCxCropWeedsNoSFstress(
            roundc(((100.0 * GetCrop_CCx() * GetfWeedNoS()) + 0.49), mold="int32") / 100.0
        )
        if GetManagement_FertilityStress() > 0:
            fWeed = 1.0
            if (fi > 0.0) and (GetCrop_subkind() == subkind_Forage):
                Cweed = 1
                if fi > 0.005:
                    SetSimulation_RCadj(
                        roundc(
                            GetManagement_WeedRC()
                            + Cweed
                            * (1.0 - fi)
                            * GetCrop_CCx()
                            * (1.0 - GetSimulation_EffectStress_RedCCX() / 100.0)
                            * GetManagement_WeedAdj()
                            / 100.0,
                            mold="int8",
                        )
                    )
                    if GetSimulation_RCadj() < (
                        100.0
                        * (
                            1.0
                            - fi
                            / (
                                fi
                                + (1.0 - fi) * (GetManagement_WeedAdj() / 100.0)
                            )
                        )
                    ):
                        SetSimulation_RCadj(
                            roundc(
                                100.0
                                * (
                                    1.0
                                    - fi
                                    / (
                                        fi
                                        + (1.0 - fi)
                                        * (GetManagement_WeedAdj() / 100.0)
                                    )
                                ),
                                mold="int8",
                            )
                        )
                    if GetSimulation_RCadj() > 100:
                        SetSimulation_RCadj(98)
                else:
                    SetSimulation_RCadj(100)
        else:
            if GetCrop_subkind() == subkind_Forage:
                RCadj_temp = GetSimulation_RCadj()
                _res = CCmultiplierWeedAdjusted(
                    GetManagement_WeedRC(),
                    GetCrop_CCx(),
                    GetManagement_WeedShape(),
                    fi,
                    GetSimulation_YearSeason(),
                    GetManagement_WeedAdj(),
                    RCadj_temp,
                )
                if isinstance(_res, tuple):
                    if len(_res) >= 1:
                        fWeed = _res[0]
                    if len(_res) >= 2:
                        RCadj_temp = _res[1]
                else:
                    fWeed = _res
                SetSimulation_RCadj(RCadj_temp)
            else:
                fWeed = GetfWeedNoS()

    else:
        SetfWeedNoS(1.0)
        fWeed = 1.0
        SetCCxCropWeedsNoSFstress(GetCrop_CCx())

    # ! 7.3 CC total due to weed infestation
    SetCCxTotal(
        fWeed
        * GetCrop_CCx()
        * (fi + Cweed * (1.0 - fi) * (GetManagement_WeedAdj() / 100.0))
    )

    _den = (
        GetCrop_CCx()
        * (fi + Cweed * (1.0 - fi) * (GetManagement_WeedAdj() / 100.0))
        + 2.29
    )
    SetCDCTotal(
        GetCrop_CDC()
        * (
            fWeed
            * GetCrop_CCx()
            * (fi + Cweed * (1.0 - fi) * (GetManagement_WeedAdj() / 100.0))
            + 2.29
        )
        / _den
    )
    SetGDDCDCTotal(
        GetCrop_GDDCDC()
        * (
            fWeed
            * GetCrop_CCx()
            * (fi + Cweed * (1.0 - fi) * (GetManagement_WeedAdj() / 100.0))
            + 2.29
        )
        / _den
    )

    if GetCrop_subkind() == subkind_Forage:
        fi = MultiplierCCoSelfThinning(
            int(GetSimulation_YearSeason()),
            int(GetCrop_YearCCx()),
            GetCrop_CCxRoot(),
        )
    else:
        fi = 1.0

    SetCCoTotal(
        fWeed
        * GetCrop_CCo()
        * (fi + Cweed * (1.0 - fi) * (GetManagement_WeedAdj() / 100.0))
    )

    # ! 8. prepare output files
    # ! Not applicable

    # ! 9. first day
    SetStartMode(True)
    bool_temp = (not GetSimulation_ResetIniSWC())
    SetPreDay(bool_temp)
    SetDayNri(GetSimulation_FromDayNr())

    Day1 = ""
    Month1 = ""
    Year1 = ""

    _res = DetermineDate(GetSimulation_FromDayNr())
    if isinstance(_res, tuple) and len(_res) >= 3:
        Day1, Month1, Year1 = _res[0], _res[1], _res[2]

    SetNoYear(Year1 == 1901)  # ! for output file


def ResetPreviousSum(PreviousSum):

    PreviousSum.Epot = 0.0
    PreviousSum.Tpot = 0.0
    PreviousSum.Rain = 0.0
    PreviousSum.Irrigation = 0.0
    PreviousSum.Infiltrated = 0.0
    PreviousSum.Runoff = 0.0
    PreviousSum.Drain = 0.0
    PreviousSum.Eact = 0.0
    PreviousSum.Tact = 0.0
    PreviousSum.TrW = 0.0
    PreviousSum.ECropCycle = 0.0
    PreviousSum.CRwater = 0.0
    PreviousSum.Biomass = 0.0
    PreviousSum.YieldPart = 0.0
    PreviousSum.BiomassPot = 0.0
    PreviousSum.BiomassUnlim = 0.0
    PreviousSum.SaltIn = 0.0
    PreviousSum.SaltOut = 0.0
    PreviousSum.CRsalt = 0.0

    SetSumETo(0.0)
    SetSumGDD(0.0)
    SetPreviousSumETo(0.0)
    SetPreviousSumGDD(0.0)
    SetPreviousBmob(0.0)
    SetPreviousBsto(0.0)

    return PreviousSum


def AdjustCompartments():
    # Adjust size of compartments if required
    TotDepth = 0.0
    for i in range(1, GetNrCompartments() + 1):
        TotDepth = TotDepth + GetCompartment_Thickness(i)

    if GetSimulation_MultipleRunWithKeepSWC():
        # Project with a sequence of simulation runs and KeepSWC
        if roundc(GetSimulation_MultipleRunConstZrx() * 1000.0, mold=1) > roundc(
            TotDepth * 1000.0, mold=1
        ):
            AdjustSizeCompartments(GetSimulation_MultipleRunConstZrx())
    else:
        if roundc(GetCrop_RootMax() * 1000.0, mold=1) > roundc(TotDepth * 1000.0, mold=1):
            if roundc(GetSoil_RootMax() * 1000.0, mold=1) == roundc(
                GetCrop_RootMax() * 1000.0, mold=1
            ):
                # no restrictive soil layer
                AdjustSizeCompartments(GetCrop_RootMax())
                # adjust soil water content
                Comp_temp = GetCompartment()
                maybe = CalculateAdjustedFC(GetZiAqua() / 100.0, Comp_temp)
                if maybe is not None:
                    Comp_temp = maybe
                SetCompartment(Comp_temp)
                if GetSimulation_IniSWC_AtFC():
                    ResetSWCToFC()
            else:
                # restrictive soil layer
                if roundc(GetSoil_RootMax() * 1000.0, mold=1) > roundc(
                    TotDepth * 1000.0, mold=1
                ):
                    AdjustSizeCompartments(float(GetSoil_RootMax()))
                    # adjust soil water content
                    Comp_temp = GetCompartment()
                    maybe = CalculateAdjustedFC(GetZiAqua() / 100.0, Comp_temp)
                    if maybe is not None:
                        Comp_temp = maybe
                    SetCompartment(Comp_temp)
                    if GetSimulation_IniSWC_AtFC():
                        ResetSWCToFC()


def RunSimulation(TheProjectFile_: str, TheProjectType: int):

    NrRun = 0
    NrRuns = 0

    SetNextSimFromDayNr(undef_int)
    InitializeSimulation(TheProjectFile_, TheProjectType)

    # select case (TheProjectType)
    if TheProjectType == typeproject_typepro:
        NrRuns = 1
    elif TheProjectType == typeproject_typeprm:
        NrRuns = GetSimulation_NrRuns()

    for NrRun in range(1, NrRuns + 1):
        InitializeRunPart1(NrRun, TheProjectType)
        InitializeClimate()
        InitializeRunPart2(NrRun, TheProjectType)
        FileManagement()
        FinalizeRun1(NrRun, GetTheProjectFile(), TheProjectType)
        FinalizeRun2(NrRun, TheProjectType)
        advance_progress()

    FinalizeSimulation()

def FinalizeSimulation():
    # fRun_close()  # Close Run.out
    if GetOutDaily():
        # fDaily_close()  # Close Daily.OUT
        pass
    if GetOut8Irri():
        # fIrrInfo_close()  # Close Irrigation info results .OUT
        pass
    if GetPart1Mult():
        # fHarvest_close()  # Close Multiple harvests in season
        pass

def FinalizeRun2(NrRun, TheProjectType):
    #CloseClimateFiles()
    #CloseIrrigationFile()
    #CloseManagementFile()

    if GetPart2Eval() and (GetObservationsFile() != "(None)"):
        CloseEvalDataPerformEvaluation(NrRun, TheProjectType)

def CloseEvalDataPerformEvaluation(NrRun, TheProjectType):
    totalnameEvalStat = ""
    StrNr = ""

    # 1. Close Evaluation data file and file with observations
    fEval_close()
    if GetLineNrEval() != undef_int:
        fObs_close()

    # 2. Specify File name Evaluation of simulation results - Statistics
    StrNr = ""
    if GetSimulation_MultipleRun() and (GetSimulation_NrRuns() > 1):
        StrNr = str(NrRun)

    if TheProjectType == typeproject_typepro:
        totalnameEvalStat = GetPathNameOutp() + GetOutputName() + 'PROevaluation.OUT'
    elif TheProjectType == typeproject_typeprm:
        StrNr = str(NrRun)
        totalnameEvalStat = GetPathNameOutp() + GetOutputName() + 'PRM' + StrNr.strip() + 'evaluation.OUT'

    # 3. Create Evaluation statistics file
    WriteAssessmentSimulation(
        StrNr.strip(),
        totalnameEvalStat,
        TheProjectType,
        GetSimulation_FromDayNr(),
        GetSimulation_ToDayNr()
    )

    # 4. Delete Evaluation data file
    fEval_erase()

def FinalizeRun1(NrRun, TheProjectFile, TheProjectType):
    # 16. Finalise
    if (GetDayNri() - 1) == GetSimulation_ToDayNr():

        # multiple cuttings
        if GetPart1Mult():
            if GetManagement_Cuttings_HarvestEnd():
                # final harvest at crop maturity
                SetNrCut(GetNrCut() + 1)
                RecordHarvest(
                    GetNrCut(),
                    (GetDayNri() - GetCrop_Day1() + 1)
                )

            # last line at end of season
            RecordHarvest(
                9999,
                (GetDayNri() - GetCrop_Day1() + 1)
            )

        # intermediate results
        if (
            (GetOutputAggregate() == 2 or GetOutputAggregate() == 3)
            and ((GetDayNri() - 1) > GetPreviousDayNr())
        ):
            SetDayNri(GetDayNri() - 1)
            WriteIntermediatePeriod(TheProjectFile)

        WriteSimPeriod(NrRun, TheProjectFile)

def WriteSimPeriod(NrRun, TheProjectFile):
    Day1 = 0
    Month1 = 0
    Year1 = 0
    DayN = 0
    MonthN = 0
    YearN = 0

    Day1, Month1, Year1 = DetermineDate(GetSimulation_FromDayNr())
    # Start simulation run

    DayN, MonthN, YearN = DetermineDate(GetSimulation_ToDayNr())
    # End simulation run

    WriteTheResults(
        NrRun,
        Day1, Month1, Year1,
        DayN, MonthN, YearN,
        GetSumWaBal_Rain(),
        GetSumETo(),
        GetSumGDD(),
        GetSumWaBal_Irrigation(),
        GetSumWaBal_Infiltrated(),
        GetSumWaBal_Runoff(),
        GetSumWaBal_Drain(),
        GetSumWaBal_CRwater(),
        GetSumWaBal_Eact(),
        GetSumWaBal_Epot(),
        GetSumWaBal_Tact(),
        GetSumWaBal_TrW(),
        GetSumWaBal_Tpot(),
        GetSumWaBal_SaltIn(),
        GetSumWaBal_SaltOut(),
        GetSumWaBal_CRSalt(),
        GetSumWaBal_Biomass(),
        GetSumWaBal_BiomassUnlim(),
        GetTransfer_Bmobilized(),
        GetSimulation_Storage_Btotal(),
        TheProjectFile
    )

def FileManagement():
    WPi = 0.0
    HarvestNow = False
    SetRepeatToDay(GetSimulation_ToDayNr())

    while True:
        WPi, HarvestNow = AdvanceOneTimeStep(WPi, HarvestNow)
        ReadClimateNextDay()
        SetGDDVariablesNextDay()
        if (GetDayNri() - 1) == GetRepeatToDay():
            break

def SetGDDVariablesNextDay():
    if GetDayNri() <= GetSimulation_ToDayNr():
        SetGDDayi(
            DegreesDay(
                GetCrop_Tbase(),
                GetCrop_Tupper(),
                GetTmin(),
                GetTmax(),
                GetSimulParam_GDDMethod()
            )
        )

        if GetDayNri() >= GetCrop_Day1():
            SetSimulation_SumGDD(GetSimulation_SumGDD() + GetGDDayi())
            SetSimulation_SumGDDfromDay1(
                GetSimulation_SumGDDfromDay1() + GetGDDayi()
            )

def ReadClimateNextDay():
    ETo_tmp = 0.0
    tmpRain = 0.0
    Tmin_temp = 0.0
    Tmax_temp = 0.0
    line = ""
    parts = None

    # Read Climate next day, Get GDDays and update SumGDDays
    if GetDayNri() <= GetSimulation_ToDayNr():
        if GetEToFile() != '(None)':
            line = fEToSIM_read()
            if line != "":
                parts = line.split()
                if len(parts) > 0:
                    ETo_tmp = float(parts[0])
                    SetETo(ETo_tmp)

        if GetRainFile() != '(None)':
            line = fRainSIM_read()
            if line != "":
                parts = line.split()
                if len(parts) > 0:
                    tmpRain = float(parts[0])
                    SetRain(tmpRain)

        if (GetTemperatureFile() == '(None)') or (GetTemperatureFile() == '(External)'):
            SetTmin(GetSimulParam_Tmin())
            SetTmax(GetSimulParam_Tmax())
        else:
            line = fTempSIM_read()
            if line != "":
                parts = line.split()
                if len(parts) >= 2:
                    Tmin_temp = float(parts[0])
                    Tmax_temp = float(parts[1])
                    SetTmin(Tmin_temp)
                    SetTmax(Tmax_temp)


def RelationshipsForFertilityAndSaltStress():
    Coeffb0_temp = 0.0
    Coeffb1_temp = 0.0
    Coeffb2_temp = 0.0
    Coeffb0Salt_temp = 0.0
    Coeffb1Salt_temp = 0.0
    Coeffb2Salt_temp = 0.0

    X10 = 0.0
    X20 = 0.0
    X30 = 0.0
    X40 = 0.0
    X50 = 0.0
    X60 = 0.0
    X70 = 0.0
    X80 = 0.0
    X90 = 0.0

    BioTop = 0
    BioLow = 0
    StrTop = 0.0
    StrLow = 0.0

    # 1. Soil fertility
    SetFracBiomassPotSF(1.0)

    # 1.a Soil fertility (Coeffb0,Coeffb1,Coeffb2 : Biomass-Soil Fertility stress)
    if GetCrop_StressResponse_Calibrated():
        Coeffb0_temp = GetCoeffb0()
        Coeffb1_temp = GetCoeffb1()
        Coeffb2_temp = GetCoeffb2()

        (
            Coeffb0_temp,
            Coeffb1_temp,
            Coeffb2_temp,
            X10,
            X20,
            X30,
            X40,
            X50,
            X60,
            X70,
        ) = ReferenceStressBiomassRelationship(
            GetCrop_DaysToCCini(),
            GetCrop_GDDaysToCCini(),
            GetCrop_DaysToGermination(),
            GetCrop_DaysToFullCanopy(),
            GetCrop_DaysToSenescence(),
            GetCrop_DaysToHarvest(),
            GetCrop_DaysToFlowering(),
            GetCrop_LengthFlowering(),
            GetCrop_GDDaysToGermination(),
            GetCrop_GDDaysToFullCanopy(),
            GetCrop_GDDaysToSenescence(),
            GetCrop_GDDaysToHarvest(),
            GetCrop_WPy(),
            GetCrop_HI(),
            GetCrop_CCo(),
            GetCrop_CCx(),
            GetCrop_CGC(),
            GetCrop_GDDCGC(),
            GetCrop_CDC(),
            GetCrop_GDDCDC(),
            GetCrop_KcTop(),
            GetCrop_KcDeclineCumul(),
            float(GetCrop_CCEffectEvapLate()),
            GetCrop_Tbase(),
            GetCrop_Tupper(),
            GetSimulParam_Tmin(),
            GetSimulParam_Tmax(),
            GetCrop_GDtranspLow(),
            GetCrop_WP(),
            GetCrop_dHIdt(),
            GetCrop_Day1(),
            GetCrop_DeterminancyLinked(),
            GetCrop_StressResponse(),
            GetCrop_subkind(),
            GetCrop_ModeCycle(),
            Coeffb0_temp,
            Coeffb1_temp,
            Coeffb2_temp,
            X10,
            X20,
            X30,
            X40,
            X50,
            X60,
            X70,
            GetCrop_GDDaysToFlowering(),
            GetCrop_GDDLengthFlowering(),
            GetCrop_GDDaysToHIo(),
            GetCrop_Planting(),
            GetCrop_DaysToHIo(),
        )

        SetCoeffb0(Coeffb0_temp)
        SetCoeffb1(Coeffb1_temp)
        SetCoeffb2(Coeffb2_temp)
    else:
        SetCoeffb0(float(undef_int))
        SetCoeffb1(float(undef_int))
        SetCoeffb2(float(undef_int))

    # 1.b Soil fertility : FracBiomassPotSF
    if (abs(GetManagement_FertilityStress()) > epsilon(0.0)) and GetCrop_StressResponse_Calibrated():
        BioLow = 100
        StrLow = 0.0

        while True:
            BioTop = BioLow
            StrTop = StrLow
            BioLow = BioLow - 1
            StrLow = GetCoeffb0() + GetCoeffb1() * BioLow + GetCoeffb2() * BioLow * BioLow

            if (StrLow >= GetManagement_FertilityStress()) or (BioLow <= 0) or (StrLow >= 99.99):
                break

        if StrLow >= 99.99:
            StrLow = 100.0

        if abs(StrLow - StrTop) < 0.001:
            SetFracBiomassPotSF(float(BioTop))
        else:
            SetFracBiomassPotSF(
                float(BioTop)
                - (GetManagement_FertilityStress() - StrTop) / (StrLow - StrTop)
            )

        SetFracBiomassPotSF(GetFracBiomassPotSF() / 100.0)

    # 2. soil salinity (Coeffb0Salt,Coeffb1Salt,Coeffb2Salt : CCx/KsSto - Salt stress)
    if GetSimulation_SalinityConsidered() is True:
        Coeffb0Salt_temp = GetCoeffb0Salt()
        Coeffb1Salt_temp = GetCoeffb1Salt()
        Coeffb2Salt_temp = GetCoeffb2Salt()

        (
            Coeffb0Salt_temp,
            Coeffb1Salt_temp,
            Coeffb2Salt_temp,
            X10,
            X20,
            X30,
            X40,
            X50,
            X60,
            X70,
            X80,
            X90,
        ) = ReferenceCCxSaltStressRelationship(
            GetCrop_DaysToCCini(),
            GetCrop_GDDaysToCCini(),
            GetCrop_DaysToGermination(),
            GetCrop_DaysToFullCanopy(),
            GetCrop_DaysToSenescence(),
            GetCrop_DaysToHarvest(),
            GetCrop_DaysToFlowering(),
            GetCrop_LengthFlowering(),
            GetCrop_GDDaysToFlowering(),
            GetCrop_GDDLengthFlowering(),
            GetCrop_GDDaysToGermination(),
            GetCrop_GDDaysToFullCanopy(),
            GetCrop_GDDaysToSenescence(),
            GetCrop_GDDaysToHarvest(),
            GetCrop_WPy(),
            GetCrop_HI(),
            GetCrop_CCo(),
            GetCrop_CCx(),
            GetCrop_CGC(),
            GetCrop_GDDCGC(),
            GetCrop_CDC(),
            GetCrop_GDDCDC(),
            GetCrop_KcTop(),
            GetCrop_KcDeclineCumul(),
            float(GetCrop_CCEffectEvapLate()),
            GetCrop_Tbase(),
            GetCrop_Tupper(),
            GetSimulParam_Tmin(),
            GetSimulParam_Tmax(),
            GetCrop_GDtranspLow(),
            GetCrop_WP(),
            GetCrop_dHIdt(),
            GetCrop_Day1(),
            GetCrop_DeterminancyLinked(),
            GetCrop_subkind(),
            GetCrop_ModeCycle(),
            GetCrop_CCsaltDistortion(),
            Coeffb0Salt_temp,
            Coeffb1Salt_temp,
            Coeffb2Salt_temp,
            X10,
            X20,
            X30,
            X40,
            X50,
            X60,
            X70,
            X80,
            X90,
            GetCrop_GDDaysToHIo(),
            GetCrop_Planting(),
            GetCrop_DaysToHIo(),
        )

        SetCoeffb0Salt(Coeffb0Salt_temp)
        SetCoeffb1Salt(Coeffb1Salt_temp)
        SetCoeffb2Salt(Coeffb2Salt_temp)
    else:
        SetCoeffb0Salt(float(undef_int))
        SetCoeffb1Salt(float(undef_int))
        SetCoeffb2Salt(float(undef_int))


def InitializeClimate():
    # Creates the Climate SIM files and reads climate of first day

    # 10. Climate
    # create climate files
    CreateDailyClimFiles(
        GetSimulation_FromDayNr(),
        GetSimulation_ToDayNr()
    )
    # climatic data for first day
    OpenClimFilesAndGetDataFirstDay(GetDayNri())


def CreateDailyClimFiles(FromSimDay, ToSimDay):
    # 1. ETo file
    if GetEToFile() != '(None)':
        totalname = GetEToFileFull()
        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(totalname).lstrip("/\\"),
            )
        )
        if os.path.isfile(full_path):
            # open file and find first day of simulation period
            if GetEToRecord_DataType() == datatype_Daily:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
                    lines = f0.read().splitlines()

                data_lines = lines[8:]
                i = FromSimDay - GetEToRecord_FromDayNr()
                ETo_temp = float(data_lines[i].split()[0])
                SetETo(ETo_temp)

            elif GetEToRecord_DataType() == datatype_Decadely:
                EToDataSet_temp = GetEToDataSet()
                EToDataSet_temp = GetDecadeEToDataSet(FromSimDay, EToDataSet_temp)
                SetEToDataSet(EToDataSet_temp)
                i = 1
                while GetEToDataSet_DayNr(i) != FromSimDay:
                    i = i + 1
                SetETo(GetEToDataSet_Param(i))

            elif GetEToRecord_DataType() == datatype_Monthly:
                EToDataSet_temp = GetEToDataSet()
                GetMonthlyEToDataSet(FromSimDay, EToDataSet_temp)
                SetEToDataSet(EToDataSet_temp)
                i = 1
                while GetEToDataSet_DayNr(i) != FromSimDay:
                    i = i + 1
                SetETo(GetEToDataSet_Param(i))

            # create SIM file and record first day
            totalnameOUT = GetPathNameSimul() + 'EToData.SIM'
            full_path_out = os.path.normpath(
                os.path.join(
                    complete_path_dir,
                    _strip_quotes(totalnameOUT).lstrip("/\\"),
                )
            )
            EtoSimLines = [f"{GetETo():10.4f}"]

            # next days of simulation period
            for RunningDay in range(FromSimDay + 1, ToSimDay + 1):
                if GetEToRecord_DataType() == datatype_Daily:
                    i = i + 1
                    if i >= len(data_lines):
                        i = 0
                    ETo_temp = float(data_lines[i].split()[0])
                    SetETo(ETo_temp)

                elif GetEToRecord_DataType() == datatype_Decadely:
                    if RunningDay > GetEToDataSet_DayNr(31):
                        EToDataSet_temp = GetEToDataSet()
                        GetDecadeEToDataSet(RunningDay, EToDataSet_temp)
                        SetEToDataSet(EToDataSet_temp)
                    i = 1
                    while GetEToDataSet_DayNr(i) != RunningDay:
                        i = i + 1
                    SetETo(GetEToDataSet_Param(i))

                elif GetEToRecord_DataType() == datatype_Monthly:
                    if RunningDay > GetEToDataSet_DayNr(31):
                        EToDataSet_temp = GetEToDataSet()
                        GetMonthlyEToDataSet(RunningDay, EToDataSet_temp)
                        SetEToDataSet(EToDataSet_temp)
                    i = 1
                    while GetEToDataSet_DayNr(i) != RunningDay:
                        i = i + 1
                    SetETo(GetEToDataSet_Param(i))

                EtoSimLines.append(f"{GetETo():10.4f}")

            with open(full_path_out, "w", encoding="utf-8", errors="replace") as f0:
                f0.write("\n".join(EtoSimLines) + "\n")
            if os.environ.get("AQUACROP_DEBUG_TRACE", "").strip():
                from .debugtrace import append_file_preview
                append_file_preview(complete_path_dir, "EToData.SIM", full_path_out)

    # 2. Rain File
    if GetRainFile() != '(None)':
        totalname = GetRainFileFull()
        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(totalname).lstrip("/\\"),
            )
        )
        if os.path.isfile(full_path):
            # open file and find first day of simulation period
            if GetRainRecord_DataType() == datatype_Daily:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
                    lines = f0.read().splitlines()

                data_lines = lines[8:]
                i = FromSimDay - GetRainRecord_FromDayNr()
                tmpRain = float(data_lines[i].split()[0])
                SetRain(tmpRain)

            elif GetRainRecord_DataType() == datatype_Decadely:
                RainDataSet_temp = GetRainDataSet()
                GetDecadeRainDataSet(FromSimDay, RainDataSet_temp)
                SetRainDataSet(RainDataSet_temp)
                i = 1
                while GetRainDataSet_DayNr(i) != FromSimDay:
                    i = i + 1
                SetRain(GetRainDataSet_Param(i))

            elif GetRainRecord_DataType() == datatype_Monthly:
                RainDataSet_temp = GetRainDataSet()
                GetMonthlyRainDataSet(FromSimDay, RainDataSet_temp)
                SetRainDataSet(RainDataSet_temp)
                i = 1
                while GetRainDataSet_DayNr(i) != FromSimDay:
                    i = i + 1
                SetRain(GetRainDataSet_Param(i))

            # create SIM file and record first day
            totalnameOUT = GetPathNameSimul() + 'RainData.SIM'
            full_path_out = os.path.normpath(
                os.path.join(
                    complete_path_dir,
                    _strip_quotes(totalnameOUT).lstrip("/\\"),
                )
            )
            RainSimLines = [f"{GetRain():10.4f}"]

            # next days of simulation period
            for RunningDay in range(FromSimDay + 1, ToSimDay + 1):
                if GetRainRecord_DataType() == datatype_Daily:
                    i = i + 1
                    if i >= len(data_lines):
                        i = 0
                    tmpRain = float(data_lines[i].split()[0])
                    SetRain(tmpRain)

                elif GetRainRecord_DataType() == datatype_Decadely:
                    if RunningDay > GetRainDataSet_DayNr(31):
                        RainDataSet_temp = GetRainDataSet()
                        GetDecadeRainDataSet(RunningDay, RainDataSet_temp)
                        SetRainDataSet(RainDataSet_temp)
                    i = 1
                    while GetRainDataSet_DayNr(i) != RunningDay:
                        i = i + 1
                    SetRain(GetRainDataSet_Param(i))

                elif GetRainRecord_DataType() == datatype_Monthly:
                    if RunningDay > GetRainDataSet_DayNr(31):
                        RainDataSet_temp = GetRainDataSet()
                        GetMonthlyRainDataSet(RunningDay, RainDataSet_temp)
                        SetRainDataSet(RainDataSet_temp)
                    i = 1
                    while GetRainDataSet_DayNr(i) != RunningDay:
                        i = i + 1
                    SetRain(GetRainDataSet_Param(i))

                RainSimLines.append(f"{GetRain():10.4f}")

            with open(full_path_out, "w", encoding="utf-8", errors="replace") as f0:
                f0.write("\n".join(RainSimLines) + "\n")
            if os.environ.get("AQUACROP_DEBUG_TRACE", "").strip():
                from .debugtrace import append_file_preview
                append_file_preview(complete_path_dir, "RainData.SIM", full_path_out)

    # 3. Temperature file
    if (GetTemperatureFile() != '(None)') and (GetTemperatureFile() != '(External)'):
        totalname = GetTemperatureFileFull()
        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(totalname).lstrip("/\\"),
            )
        )
        if os.path.isfile(full_path):
            # open file and find first day of simulation period
            if GetTemperatureRecord_DataType() == datatype_Daily:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
                    lines = f0.read().splitlines()

                data_lines = lines[8:]
                i = FromSimDay - GetTemperatureRecord_FromDayNr()
                StringREAD = data_lines[i]
                Tmin_temp = GetTmin()
                Tmax_temp = GetTmax()
                Tmin_temp, Tmax_temp = SplitStringInTwoParams(StringREAD, Tmin_temp, Tmax_temp)
                SetTmin(Tmin_temp)
                SetTmax(Tmax_temp)

            elif GetTemperatureRecord_DataType() == datatype_Decadely:
                TminDataSet_temp = GetTminDataSet()
                TmaxDataSet_temp = GetTmaxDataSet()
                GetDecadeTemperatureDataSet(FromSimDay, TminDataSet_temp, TmaxDataSet_temp)
                SetTminDataSet(TminDataSet_temp)
                SetTmaxDataSet(TmaxDataSet_temp)
                i = 1
                while GetTminDataSet_DayNr(i) != FromSimDay:
                    i = i + 1
                SetTmin(GetTminDataSet_Param(i))
                SetTmax(GetTmaxDataSet_Param(i))

            elif GetTemperatureRecord_DataType() == datatype_Monthly:
                TminDataSet_temp = GetTminDataSet()
                TmaxDataSet_temp = GetTmaxDataSet()
                GetMonthlyTemperatureDataSet(FromSimDay, TminDataSet_temp, TmaxDataSet_temp)
                SetTminDataSet(TminDataSet_temp)
                SetTmaxDataSet(TmaxDataSet_temp)
                i = 1
                while GetTminDataSet_DayNr(i) != FromSimDay:
                    i = i + 1
                SetTmin(GetTminDataSet_Param(i))
                SetTmax(GetTmaxDataSet_Param(i))

            # create SIM file and record first day
            totalnameOUT = GetPathNameSimul() + 'TempData.SIM'
            full_path_out = os.path.normpath(
                os.path.join(
                    complete_path_dir,
                    _strip_quotes(totalnameOUT).lstrip("/\\"),
                )
            )
            TempSimLines = [f"{GetTmin():10.4f}{GetTmax():10.4f}"]

            # next days of simulation period
            for RunningDay in range(FromSimDay + 1, ToSimDay + 1):
                if GetTemperatureRecord_DataType() == datatype_Daily:
                    i = i + 1
                    if i >= len(data_lines):
                        i = 0
                        StringREAD = data_lines[i]
                        Tmin_temp = GetTmin()
                        Tmax_temp = GetTmax()
                        Tmin_temp, Tmax_temp = SplitStringInTwoParams(StringREAD, Tmin_temp, Tmax_temp)
                        SetTmin(Tmin_temp)
                        SetTmax(Tmax_temp)
                    else:
                        parts = data_lines[i].split()
                        Tmin_temp = float(parts[0])
                        Tmax_temp = float(parts[1])
                        SetTmin(Tmin_temp)
                        SetTmax(Tmax_temp)

                elif GetTemperatureRecord_DataType() == datatype_Decadely:
                    if RunningDay > GetTminDataSet_DayNr(31):
                        TminDataSet_temp = GetTminDataSet()
                        TmaxDataSet_temp = GetTmaxDataSet()
                        GetDecadeTemperatureDataSet(RunningDay, TminDataSet_temp, TmaxDataSet_temp)
                        SetTminDataSet(TminDataSet_temp)
                        SetTmaxDataSet(TmaxDataSet_temp)
                    i = 1
                    while GetTminDataSet_DayNr(i) != RunningDay:
                        i = i + 1
                    SetTmin(GetTminDataSet_Param(i))
                    SetTmax(GetTmaxDataSet_Param(i))

                elif GetTemperatureRecord_DataType() == datatype_Monthly:
                    if RunningDay > GetTminDataSet_DayNr(31):
                        TminDataSet_temp = GetTminDataSet()
                        TmaxDataSet_temp = GetTmaxDataSet()
                        GetMonthlyTemperatureDataSet(RunningDay, TminDataSet_temp, TmaxDataSet_temp)
                        SetTminDataSet(TminDataSet_temp)
                        SetTmaxDataSet(TmaxDataSet_temp)
                    i = 1
                    while GetTminDataSet_DayNr(i) != RunningDay:
                        i = i + 1
                    SetTmin(GetTminDataSet_Param(i))
                    SetTmax(GetTmaxDataSet_Param(i))

                TempSimLines.append(f"{GetTmin():10.4f}{GetTmax():10.4f}")

            with open(full_path_out, "w", encoding="utf-8", errors="replace") as f0:
                f0.write("\n".join(TempSimLines) + "\n")
            if os.environ.get("AQUACROP_DEBUG_TRACE", "").strip():
                from .debugtrace import append_file_preview
                append_file_preview(complete_path_dir, "TempData.SIM", full_path_out)

def OpenClimFilesAndGetDataFirstDay(FirstDayNr):
    totalname = ""
    i = 0
    tmpRain = 0.0
    ETo_temp = 0.0
    Tmin_temp = 0.0
    Tmax_temp = 0.0
    TempString = ""

    # ETo file
    if GetEToFile() != '(None)':
        totalname = GetPathNameSimul() + 'EToData.SIM'
        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(totalname).lstrip("/\\"),
            )
        )

        fEToSIM_open(full_path, 'r')
        for i in range(GetSimulation_FromDayNr(), FirstDayNr):
            fEToSIM_read()
        TempString = fEToSIM_read()
        if TempString != "":
            ETo_temp = float(TempString.split()[0])
            SetETo(ETo_temp)

    # Rain file
    if GetRainFile() != '(None)':
        totalname = GetPathNameSimul() + 'RainData.SIM'
        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(totalname).lstrip("/\\"),
            )
        )

        fRainSIM_open(full_path, 'r')
        for i in range(GetSimulation_FromDayNr(), FirstDayNr):
            fRainSIM_read()
        TempString = fRainSIM_read()
        if TempString != "":
            tmpRain = float(TempString.split()[0])
            SetRain(tmpRain)

    # Temperature file
    if (GetTemperatureFile() != '(None)') and (GetTemperatureFile() != '(External)'):
        totalname = GetPathNameSimul() + 'TempData.SIM'
        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(totalname).lstrip("/\\"),
            )
        )
        
        fTempSIM_open(full_path, 'r')
        for i in range(GetSimulation_FromDayNr(), FirstDayNr):
            fTempSIM_read()
        TempString = fTempSIM_read()
        if TempString != "":
            parts = TempString.split()
            Tmin_temp = float(parts[0])
            Tmax_temp = float(parts[1])
            SetTmin(Tmin_temp)
            SetTmax(Tmax_temp)
    else:
        SetTmin(GetSimulParam_Tmin())
        SetTmax(GetSimulParam_Tmax())

def InitializeRunPart2(NrRun, TheProjectType):
    # Part2 (after reading the climate) of the run initialization
    # Calls InitializeSimulationRunPart2
    # Initializes write out for the run

    InitializeSimulationRunPart2()

    if GetOutDaily():
        WriteTitleDailyResults(TheProjectType, NrRun)

    if GetOut8Irri():
        WriteTitleIrriInfo(TheProjectType, NrRun)

    if GetPart1Mult():
        WriteTitlePart1MultResults(TheProjectType, NrRun)

    if GetPart2Eval() and (GetObservationsFile() != '(None)'):
        CreateEvalData(NrRun)

def CreateEvalData(NrRun):
    dayi = 0
    monthi = 0
    yeari = 0
    integer_temp = 0
    TempString = ""
    StrNr = ""
    tempstring2 = ""
    lines_to_write = []

    # open input file with field data
    fObs_open(GetObservationsFilefull(), 'r')  # Observations recorded in File
    TempString = fObs_read()  # description
    TempString = fObs_read()  # AquaCrop Version number
    TempString = fObs_read()
    SetZeval(float(TempString.split()[0]))
    TempString = fObs_read()
    dayi = int(TempString.split()[0])
    TempString = fObs_read()
    monthi = int(TempString.split()[0])
    TempString = fObs_read()
    yeari = int(TempString.split()[0])

    integer_temp = GetDayNr1Eval()
    integer_temp = DetermineDayNr(dayi, monthi, yeari)
    SetDayNr1Eval(integer_temp)

    TempString = fObs_read()  # title
    TempString = fObs_read()  # title
    TempString = fObs_read()  # title
    TempString = fObs_read()  # title

    SetLineNrEval(undef_int)
    TempString = fObs_read()
    if not fObs_eof():
        SetLineNrEval(11)
        integer_temp = int(TempString.split()[0])
        SetDayNrEval(integer_temp)
        SetDayNrEval(GetDayNr1Eval() + GetDayNrEval() - 1)
        while ((GetDayNrEval() < GetSimulation_FromDayNr())
               and (GetLineNrEval() != undef_int)):
            TempString = fObs_read()
            if fObs_eof():
                SetLineNrEval(undef_int)
            else:
                SetLineNrEval(GetLineNrEval() + 1)
                integer_temp = int(TempString.split()[0])
                SetDayNrEval(integer_temp)
                SetDayNrEval(GetDayNr1Eval() + GetDayNrEval() - 1)

    if GetLineNrEval() == undef_int:
        fObs_close()

    # open file with simulation results, field data
    if GetSimulation_MultipleRun() and (GetSimulation_NrRuns() > 1):
        StrNr = f"{NrRun}"
    else:
        StrNr = ""
    SetfEval_filename(GetPathNameSimul() + 'EvalData' + StrNr + '.OUT')

    fEval_open(GetfEval_filename(), 'w')
    tempstring2 = f"{GetAquaCropDescriptionWithTimeStamp()}"
    TempString = f"{GetZeval():5.2f}"

    lines_to_write.append(tempstring2.rstrip())
    lines_to_write.append('Evaluation of simulation results - Data')
    lines_to_write.append(
        '                                                                                     for soil depth: '
        + TempString.rstrip() + ' m'
    )
    lines_to_write.append(
        '   Day Month  Year   DAP Stage   CCsim   CCobs   CCstd    Bsim      '
        'Bobs      Bstd   SWCsim  SWCobs   SWstd'
    )
    lines_to_write.append(
        '                                   %       %       %     ton/ha    '
        'ton/ha    ton/ha    mm       mm      mm'
    )

    fEval_write_bulk(lines_to_write)

def WriteTitlePart1MultResults(TheProjectType, TheNrRun):
    Dayi = 0
    Monthi = 0
    Yeari = 0
    Nr = 0.0
    tempstring = ""
    lines_to_write = []

    # A. Run number
    lines_to_write.append("")
    if TheProjectType == typeproject_typeprm:
        tempstring = f"{TheNrRun:4d}"
        lines_to_write.append("   Run:" + tempstring.rstrip())

    # B. Title
    lines_to_write.append(
        "    Nr   Day  Month Year   DAP Interval  Biomass    "
        "Sum(B)   Dry-Yield  Sum(Y) Fresh-Yield  Sum(Y)"
    )
    lines_to_write.append(
        "                                 days     ton/ha    "
        "ton/ha    ton/ha    ton/ha    ton/ha    ton/ha"
    )

    # C. start crop cycle
    Dayi, Monthi, Yeari = DetermineDate(GetCrop_Day1())
    SetNoYear(Yeari == 1901)
    if GetNoYear():
        if Dayi == 0:
            Dayi = 1
        Yeari = 9999

    Nr = 0.0
    tempstring = f"{0:6d}{Dayi:6d}{Monthi:6d}{Yeari:6d}{Nr:34.3f}{Nr:20.3f}{Nr:20.3f}"
    lines_to_write.append(tempstring.rstrip())

    fHarvest_write_bulk(lines_to_write)

def WriteTitleIrriInfo(TheProjectType, TheNrRun):
    tempstring = ""
    lines_to_write = []

    # A. Run number
    lines_to_write.append("")
    if TheProjectType == typeproject_typeprm:
        tempstring = f"{TheNrRun:4d}"
        lines_to_write.append("   Run:" + tempstring.rstrip())

    # B. Title
    lines_to_write.append("   Day Month  Year   DAP Stage    Irri  IrrInt")
    lines_to_write.append("                                    mm    days")

    fIrrInfo_write_bulk(lines_to_write)

def WriteTitleDailyResults(TheProjectType, TheNrRun):
    Str1 = ""
    Str2 = ""
    tempstring = ""
    tempstring_piece = ""
    NodeD = 0.0
    Zprof = 0.0
    Compi = 0
    lines_to_write = []

    # A. Run number
    lines_to_write.append("")
    if TheProjectType == typeproject_typeprm:
        Str1 = f"{TheNrRun:4d}"
        lines_to_write.append("   Run:" + Str1.rstrip())

    # B. thickness of soil profile and root zone
    if GetOut1Wabal() or GetOut3Prof() or GetOut4Salt():
        Zprof = 0.0
        for compi in range(1, GetNrCompartments() + 1):
            Zprof = Zprof + GetCompartment_Thickness(compi)
        Str1 = f"{Zprof:4.2f}"
        if roundc(GetSoil_RootMax() * 1000.0, mold=1) == \
           roundc(GetCrop_RootMax() * 1000.0, mold=1):
            Str2 = f"{GetCrop_RootMax():4.2f}"
        else:
            Str2 = f"{GetSoil_RootMax():4.2f}"

    # C. 1st line title
    tempstring = "   Day Month  Year   DAP Stage"

    # C1. Water balance
    if GetOut1Wabal():
        tempstring = tempstring + \
            f"   WC({Str1.rstrip()})   Rain     Irri   Surf   Infilt   RO    Drain       CR    Zgwt" + \
            "       Ex       E     E/Ex     Trx       Tr  Tr/Trx    ETx      ET  ET/ETx"

    # C2. Crop development and yield
    if GetOut2Crop():
        tempstring = tempstring + \
            "      GD       Z     StExp  StSto  StSen StSalt StWeed   CC      CCw     StTr  Kc(Tr)" + \
            "     Trx       Tr      TrW  Tr/Trx   WP" + \
            "    Biomass     HI    Y(dry)  Y(fresh)  Brelative" + \
            "    WPet      Bin     Bout"

    # C3. Profile/Root zone - Soil water content
    if GetOut3Prof():
        tempstring = tempstring + \
            f"  WC({Str1.rstrip()}) Wr({Str2.rstrip()})     Z       Wr    Wr(SAT)    Wr(FC)   Wr(exp)   Wr(sto)   Wr(sen)   Wr(PWP)"

    # C4. Profile/Root zone - soil salinity
    if GetOut4Salt():
        tempstring = tempstring + \
            f"    SaltIn    SaltOut   SaltUp   Salt({Str1.rstrip()})  SaltZ     Z       ECe    ECsw   StSalt  Zgwt    ECgw"

    # C5. Compartments - Soil water content
    if GetOut5CompWC():
        tempstring = tempstring + "       WC01"
        for Compi in range(2, GetNrCompartments()):
            Str1 = f"{Compi:2d}"
            tempstring = tempstring + "       WC" + Str1.rstrip()
        Str1 = f"{GetNrCompartments():2d}"
        tempstring = tempstring + "       WC" + Str1.rstrip()

    # C6. Compartmens - Electrical conductivity of the saturated soil-paste extract
    if GetOut6CompEC():
        tempstring = tempstring + "      ECe01"
        for Compi in range(2, GetNrCompartments()):
            Str1 = f"{Compi:2d}"
            tempstring = tempstring + "      ECe" + Str1.rstrip()
        Str1 = f"{GetNrCompartments():2d}"
        tempstring = tempstring + "      ECe" + Str1.rstrip()

    # C7. Climate input parameters
    if GetOut7Clim():
        tempstring = tempstring + "     Rain       ETo      Tmin      Tavg      Tmax      CO2"

    lines_to_write.append(tempstring)

    tempstring = "                              "

    # D1. Water balance
    if GetOut1Wabal():
        tempstring = tempstring + \
            "        mm      mm       mm     mm     mm     mm       mm       mm      m " + \
            "       mm       mm     %        mm       mm    %        mm      mm       %"

    # D2. Crop development and yield
    if GetOut2Crop():
        tempstring = tempstring + \
            "  degC-day     m       %      %      %      %      %      %       %       %       -" + \
            "        mm       mm       mm    %     g/m2" + \
            "    ton/ha      %    ton/ha   ton/ha" + \
            "       %       kg/m3   ton/ha   ton/ha"

    # D3. Profile/Root zone - Soil water content
    if GetOut3Prof():
        tempstring = tempstring + \
            "      mm       mm       m       mm        mm        mm        mm        mm        mm         mm"

    # D4. Profile/Root zone - soil salinity
    if GetOut4Salt():
        tempstring = tempstring + \
            "    ton/ha    ton/ha    ton/ha    ton/ha    ton/ha     m      dS/m    dS/m      %     m      dS/m"

    # D5. Compartments - Soil water content
    if GetOut5CompWC():
        NodeD = GetCompartment_Thickness(1) / 2.0
        tempstring_piece = f"{NodeD:11.2f}"
        tempstring = tempstring + tempstring_piece.rstrip()

        for Compi in range(2, GetNrCompartments()):
            NodeD = NodeD + (GetCompartment_Thickness(Compi - 1) / 2.0) + \
                    (GetCompartment_Thickness(Compi) / 2.0)
            tempstring_piece = f"{NodeD:11.2f}"
            tempstring = tempstring + tempstring_piece.rstrip()

        NodeD = NodeD + (GetCompartment_Thickness(GetNrCompartments() - 1) / 2.0) + \
                (GetCompartment_Thickness(GetNrCompartments()) / 2.0)
        tempstring_piece = f"{NodeD:11.2f}"
        tempstring = tempstring + tempstring_piece.rstrip()

    # D6. Compartmens - Electrical conductivity of the saturated soil-paste extract
    if GetOut6CompEC():
        NodeD = GetCompartment_Thickness(1) / 2.0
        tempstring_piece = f"{NodeD:11.2f}"
        tempstring = tempstring + tempstring_piece.rstrip()

        for Compi in range(2, GetNrCompartments()):
            NodeD = NodeD + (GetCompartment_Thickness(Compi - 1) / 2.0) + \
                    (GetCompartment_Thickness(Compi) / 2.0)
            tempstring_piece = f"{NodeD:11.2f}"
            tempstring = tempstring + tempstring_piece.rstrip()

        NodeD = NodeD + (GetCompartment_Thickness(GetNrCompartments() - 1) / 2.0) + \
                (GetCompartment_Thickness(GetNrCompartments()) / 2.0)
        tempstring_piece = f"{NodeD:11.2f}"
        tempstring = tempstring + tempstring_piece.rstrip()

    # D7. Climate input parameters
    if GetOut7Clim():
        tempstring = tempstring + "       mm        mm     degC      degC      degC       ppm"

    lines_to_write.append(tempstring)

    fDaily_write_bulk(lines_to_write)
    
def InitializeSimulationRunPart2():
    # Part2 (after reading the climate) of the initialization of a run
    # Initializes parameters and states

    global tDaysZmin, tGDDZmin

    # Sum of GDD before start of simulation
    SetSimulation_SumGDD(0.0)
    SetSimulation_SumGDDfromDay1(0.0)
    if (GetCrop_ModeCycle() == ModeCycle_GDDays) and (GetCrop_Day1() < GetDayNri()):
        SumGDD_temp = GetSimulation_SumGDD()
        SumGDDfromDay1_temp = GetSimulation_SumGDDfromDay1()
        SumGDD_temp, SumGDDfromDay1_temp = GetSumGDDBeforeSimulation(SumGDD_temp, SumGDDfromDay1_temp)
        # GDDays before start of simulation
        SetSimulation_SumGDD(SumGDD_temp)
        SetSimulation_SumGDDfromDay1(SumGDDfromDay1_temp)
    SetSumGDDPrev(GetSimulation_SumGDDfromDay1())

    # Sum of GDD at end of first day
    SetGDDayi(DegreesDay(GetCrop_Tbase(), GetCrop_Tupper(), GetTmin(),
                         GetTmax(), GetSimulParam_GDDMethod()))
    if GetDayNri() >= GetCrop_Day1():
        if GetDayNri() == GetCrop_Day1():
            SetSimulation_SumGDD(GetSimulation_SumGDD() + GetGDDayi())
        SetSimulation_SumGDDfromDay1(GetSimulation_SumGDDfromDay1() + GetGDDayi())
    # Reset cummulative sums of ETo and GDD for Run output
    SetSumETo(0.0)
    SetSumGDD(0.0)

    # 11. Irrigation
    SetIrriInterval(1)
    SetGlobalIrriECw(True)  # In Versions < 3.2 - Irrigation water
                            # quality is not yet recorded on file
    OpenIrrigationFile()
    SetLastIrriDAP(0)

    # 12. Adjusted time when starting as regrowth
    if GetCrop_DaysToCCini() != 0:
        # regrowth
        SetGDDTadj(undef_int)
        SetGDDayFraction(float(undef_int))
        if GetCrop_DaysToCCini() == undef_int:
            SetTadj(GetCrop_DaysToFullCanopy() - GetCrop_DaysToGermination())
        else:
            SetTadj(GetCrop_DaysToCCini())
        SetDayFraction(float(GetCrop_DaysToSenescence() - GetCrop_DaysToFullCanopy()) /
                       float(GetTadj() + GetCrop_DaysToGermination() +
                             (GetCrop_DaysToSenescence() - GetCrop_DaysToFullCanopy())))
        if GetCrop_ModeCycle() == ModeCycle_GDDays:
            if GetCrop_GDDaysToCCini() == undef_int:
                SetGDDTadj(GetCrop_GDDaysToFullCanopy() - GetCrop_GDDaysToGermination())
            else:
                SetGDDTadj(GetCrop_GDDaysToCCini())
            SetGDDayFraction(float(GetCrop_GDDaysToSenescence() - GetCrop_GDDaysToFullCanopy()) /
                             float(GetGDDTadj() + GetCrop_GDDaysToGermination() +
                                   (GetCrop_GDDaysToSenescence() -
                                    GetCrop_GDDaysToFullCanopy())))
    else:
        # sowing or transplanting
        SetTadj(0)
        SetGDDTadj(0)
        SetDayFraction(float(undef_int))
        SetGDDayFraction(float(undef_int))

    # 13. Initial canopy cover
    # 13.1 default value
    # 13.1a RatDGDD for simulation of CanopyCoverNoStressSF (CCi with decline)
    RatDGDD = 1.0
    if GetCrop_ModeCycle() == ModeCycle_GDDays:
        if GetCrop_GDDaysToFullCanopySF() < GetCrop_GDDaysToSenescence():
            RatDGDD = (GetCrop_DaysToSenescence() -
                       GetCrop_DaysToFullCanopySF()) / float(GetCrop_GDDaysToSenescence() -
                                                             GetCrop_GDDaysToFullCanopySF())
    # 13.1b DayCC for initial canopy cover
    Dayi = GetDayNri() - GetCrop_Day1()
    if GetCrop_DaysToCCini() == 0:
        # sowing or transplant
        DayCC = Dayi
        SetDayFraction(float(undef_int))
    else:
        # adjust time (calendar days) for regrowth
        DayCC = Dayi + GetTadj() + GetCrop_DaysToGermination()  # adjusted time scale
        if DayCC > GetCrop_DaysToHarvest():
            DayCC = GetCrop_DaysToHarvest()  # special case where L123 > L1234
        if DayCC > GetCrop_DaysToFullCanopy():
            if Dayi <= GetCrop_DaysToSenescence():
                DayCC = GetCrop_DaysToFullCanopy() + roundc(
                    GetDayFraction() *
                    (Dayi + GetTadj() + GetCrop_DaysToGermination() -
                     GetCrop_DaysToFullCanopy()),
                    mold=1
                )  # slow down
            else:
                DayCC = Dayi  # switch time scale
    # 13.1c SumGDDayCC for initial canopy cover
    SumGDDforDayCC = undef_int
    if GetCrop_ModeCycle() == ModeCycle_GDDays:
        if GetCrop_GDDaysToCCini() == 0:
            SumGDDforDayCC = GetSimulation_SumGDDfromDay1() - GetGDDayi()
        else:
            # adjust time (Growing Degree Days) for regrowth
            SumGDDforDayCC = GetSimulation_SumGDDfromDay1() - GetGDDayi() + \
                             GetGDDTadj() + GetCrop_GDDaysToGermination()
            if SumGDDforDayCC > GetCrop_GDDaysToHarvest():
                SumGDDforDayCC = GetCrop_GDDaysToHarvest()
                # special case where L123 > L1234
            if SumGDDforDayCC > GetCrop_GDDaysToFullCanopy():
                if GetSimulation_SumGDDfromDay1() <= GetCrop_GDDaysToSenescence():
                    SumGDDforDayCC = GetCrop_GDDaysToFullCanopy() + roundc(
                        GetGDDayFraction() *
                        (GetSimulation_SumGDDfromDay1() + GetGDDTadj() +
                         GetCrop_GDDaysToGermination() -
                         GetCrop_GDDaysToFullCanopy()),
                        mold=1
                    )
                    # slow down
                else:
                    SumGDDforDayCC = GetSimulation_SumGDDfromDay1() - GetGDDayi()
                    # switch time scale
    # 13.1d CCi at start of day (is CCi at end of previous day)
    if GetDayNri() <= GetCrop_Day1():
        if GetCrop_DaysToCCini() != 0:
            # regrowth which starts on 1st day
            if GetDayNri() == GetCrop_Day1():
                SetCCiPrev(CCiNoWaterStressSF(
                    DayCC,
                    GetCrop_DaysToGermination(),
                    GetCrop_DaysToFullCanopySF(),
                    GetCrop_DaysToSenescence(), GetCrop_DaysToHarvest(),
                    GetCrop_GDDaysToGermination(),
                    GetCrop_GDDaysToFullCanopySF(),
                    GetCrop_GDDaysToSenescence(), GetCrop_GDDaysToHarvest(),
                    GetCCoTotal(), GetCCxTotal(), GetCrop_CGC(),
                    GetCrop_GDDCGC(), GetCDCTotal(), GetGDDCDCTotal(),
                    SumGDDforDayCC, RatDGDD,
                    GetSimulation_EffectStress_RedCGC(),
                    GetSimulation_EffectStress_RedCCX(),
                    GetSimulation_EffectStress_CDecline(), GetCrop_ModeCycle()
                ))
            else:
                SetCCiPrev(0.0)
        else:
            # sowing or transplanting
            SetCCiPrev(0.0)
            if GetDayNri() == (GetCrop_Day1() + GetCrop_DaysToGermination()):
                SetCCiPrev(GetCCoTotal())
    else:
        if GetDayNri() > GetCrop_DayN():
            SetCCiPrev(0.0)  # after cropping period
        else:
            SetCCiPrev(CCiNoWaterStressSF(
                DayCC,
                GetCrop_DaysToGermination(),
                GetCrop_DaysToFullCanopySF(), GetCrop_DaysToSenescence(),
                GetCrop_DaysToHarvest(), GetCrop_GDDaysToGermination(),
                GetCrop_GDDaysToFullCanopySF(), GetCrop_GDDaysToSenescence(),
                GetCrop_GDDaysToHarvest(), GetCCoTotal(), GetCCxTotal(),
                GetCrop_CGC(), GetCrop_GDDCGC(), GetCDCTotal(),
                GetGDDCDCTotal(), SumGDDforDayCC, RatDGDD,
                GetSimulation_EffectStress_RedCGC(),
                GetSimulation_EffectStress_RedCCX(),
                GetSimulation_EffectStress_CDecline(), GetCrop_ModeCycle()
            ))
    # 13.2 specified CCini (%)
    if (GetSimulation_CCini() > 0.0) and \
       (roundc(10000.0 * GetCCiPrev(), mold=1) > 0) and \
       (roundc(GetSimulation_CCini(), mold=1) !=
        roundc(100.0 * GetCCiPrev(), mold=1)):
        # 13.2a Minimum CC
        CCiniMin = 100.0 * (GetCrop_SizeSeedling() / 10000.0) * \
                   (GetCrop_PlantingDens() / 10000.0)
        if CCiniMin - math.floor(CCiniMin * 100.0) / 100.0 >= 0.00001:
            CCiniMin = math.floor(CCiniMin * 100.0 + 1.0) / 100.0
        else:
            CCiniMin = math.floor(CCiniMin * 100.0) / 100.0
        # 13.2b Maximum CC
        CCiniMax = 100.0 * GetCCiPrev()
        CCiniMax = math.floor(CCiniMax * 100.0) / 100.0
        # 13.2c accept specified CCini
        if (GetSimulation_CCini() >= CCiniMin) and \
           (GetSimulation_CCini() <= CCiniMax):
            SetCCiPrev(GetSimulation_CCini() / 100.0)
    # 13.3
    SetCrop_CCxAdjusted(GetCCxTotal())
    SetCrop_CCoAdjusted(GetCCoTotal())
    SetTimeSenescence(0.0)
    SetCrop_CCxWithered(0.0)
    SetNoMoreCrop(False)
    SetCCiActual(GetCCiPrev())

    # 14. Biomass and re-setting of GlobalZero
    if roundc(1000.0 * GetSimulation_Bini(), mold=1) > 0:
        # overwrite settings in GlobalZero (in Global)
        SetSumWaBal_Biomass(GetSimulation_Bini())
        SetSumWaBal_BiomassPot(GetSimulation_Bini())
        SetSumWaBal_BiomassUnlim(GetSimulation_Bini())
        SetSumWaBal_BiomassTot(GetSimulation_Bini())

    # 15. Transfer of assimilates
    if (GetCrop_subkind() == subkind_Forage) and \
       (GetCropFileFull().strip() ==
        GetSimulation_Storage_CropString().strip()) and \
       (GetSimulation_YearSeason() > 1) and \
       (GetSimulation_YearSeason() ==
        (GetSimulation_Storage_Season() + 1)):
        # only valid for perennial herbaceous forage crops
        # only for the same crop
        # mobilization not possible in season 1
        # season next to season in which storage took place
        # mobilization of assimilates
        if GetSimulation_YearSeason() == 2:
            SetTransfer_ToMobilize(GetSimulation_Storage_Btotal() *
                                   0.2 * GetCrop_Assimilates_Mobilized() / 100.0)
        else:
            SetTransfer_ToMobilize(GetSimulation_Storage_Btotal() *
                                   GetCrop_Assimilates_Mobilized() / 100.0)
        if roundc(1000.0 * GetTransfer_ToMobilize(), mold=1) > 0:  # minimum 1 kg
            SetTransfer_Mobilize(True)
        else:
            SetTransfer_Mobilize(False)
    else:
        SetSimulation_Storage_CropString(GetCropFileFull())
        # no mobilization of assimilates
        SetTransfer_ToMobilize(0.0)
        SetTransfer_Mobilize(False)
    # Storage is off and zero at start of season
    SetSimulation_Storage_Season(GetSimulation_YearSeason())
    SetSimulation_Storage_Btotal(0.0)
    SetTransfer_Store(False)
    # Nothing yet mobilized at start of season
    SetTransfer_Bmobilized(0.0)

    # 16. Initial rooting depth
    # 16.1 default value
    if GetDayNri() <= GetCrop_Day1():
        SetZiprev(float(undef_int))
    else:
        if GetDayNri() > GetCrop_DayN():
            SetZiprev(float(undef_int))
        else:
            SetZiprev(ActualRootingDepth(
                GetDayNri() - GetCrop_Day1(),
                GetCrop_DaysToGermination(),
                GetCrop_DaysToMaxRooting(),
                GetCrop_DaysToHarvest(),
                GetCrop_GDDaysToGermination(),
                GetCrop_GDDaysToMaxRooting(),
                GetSumGDDPrev(),
                GetCrop_RootMin(),
                GetCrop_RootMax(),
                GetCrop_RootShape(),
                GetCrop_ModeCycle()
            ))
    # 16.2 specified or default Zrini (m)
    if (GetSimulation_Zrini() > 0.0) and \
       (GetZiprev() > 0.0) and \
       (GetSimulation_Zrini() <= GetZiprev()):
        if (GetSimulation_Zrini() >= GetCrop_RootMin()) and \
           (GetSimulation_Zrini() <= GetCrop_RootMax()):
            SetZiprev(GetSimulation_Zrini())
        else:
            if GetSimulation_Zrini() < GetCrop_RootMin():
                SetZiprev(GetCrop_RootMin())
            else:
                SetZiprev(GetCrop_RootMax())
        if (roundc(GetSoil_RootMax() * 1000.0, mold=1) <
            roundc(GetCrop_RootMax() * 1000.0, mold=1)) and \
           (GetZiprev() > GetSoil_RootMax()):
            SetZiprev(float(GetSoil_RootMax()))
        SetRootingDepth(GetZiprev())
        # NOT NEEDED since RootingDepth is calculated in the RUN by considering
        # Ziprev
    else:
        SetRootingDepth(ActualRootingDepth(
            GetDayNri() - GetCrop_Day1() + 1,
            GetCrop_DaysToGermination(),
            GetCrop_DaysToMaxRooting(),
            GetCrop_DaysToHarvest(),
            GetCrop_GDDaysToGermination(),
            GetCrop_GDDaysToMaxRooting(),
            GetSumGDDPrev(),
            GetCrop_RootMin(),
            GetCrop_RootMax(),
            GetCrop_RootShape(),
            GetCrop_ModeCycle()
        ))

    # 16.3 Time to reach Zmin
    tDaysZmin, tGDDZmin = CalculateTimeToReachZmin(
        GetCrop_RootMin(),
        GetCrop_RootMax(),
        GetCrop_RootShape(),
        GetCrop_DaysToGermination(),
        GetCrop_DaysToMaxRooting(),
        GetCrop_GDDaysToGermination(),
        GetCrop_GDDaysToMaxRooting(),
        GetCrop_ModeCycle(),
        tDaysZmin,
        tGDDZmin
    )

    # 17. Multiple cuttings
    SetNrCut(0)
    SetSumInterval(0)
    SetSumGDDcuts(0.0)
    SetBprevSum(0.0)
    SetYprevSum(0.0)
    SetCutInfoRecord1_IntervalInfo(0)
    SetCutInfoRecord2_IntervalInfo(0)
    SetCutInfoRecord1_MassInfo(0.0)
    SetCutInfoRecord2_MassInfo(0.0)
    SetDayLastCut(0)
    SetCGCref(GetCrop_CGC())
    SetGDDCGCref(GetCrop_GDDCGC())
    
    if GetManagement_Cuttings_Considered():
        OpenHarvestInfo()

    # 18. Tab sheets

    # 19. Labels, Plots and displays
    if GetManagement_BundHeight() < 0.01:
        SetSurfaceStorage(0.0)
        SetECstorage(0.0)

    if GetRootingDepth() > 0.0:
        # salinity in root zone
        ECe_temp = GetRootZoneSalt_ECe()
        ECsw_temp = GetRootZoneSalt_ECsw()
        ECswFC_temp = GetRootZoneSalt_ECswFC()
        KsSalt_temp = GetRootZoneSalt_KsSalt()
        ECe_temp, ECsw_temp, ECswFC_temp, KsSalt_temp = DetermineRootZoneSaltContent(
            GetRootingDepth(), ECe_temp, ECsw_temp, ECswFC_temp, KsSalt_temp
        )
        SetRootZoneSalt_ECe(ECe_temp)
        SetRootZoneSalt_ECsw(ECsw_temp)
        SetRootZoneSalt_ECswFC(ECswFC_temp)
        SetRootZoneSalt_KsSalt(KsSalt_temp)
        SetStressTot_Salt(((GetStressTot_NrD() - 1.0) * GetStressTot_Salt() +
                          100.0 * (1.0 - GetRootZoneSalt_KsSalt())) /
                          float(GetStressTot_NrD()))

    # Harvest Index
    SetSimulation_HIfinal(GetCrop_HI())
    SetHItimesBEF(float(undef_int))
    SetHItimesAT1(1.0)
    SetHItimesAT2(1.0)
    SetHItimesAT(1.0)
    SetalfaHI(float(undef_int))
    SetalfaHIAdj(0.0)
    if GetSimulation_FromDayNr() <= (GetSimulation_DelayedDays() +
                                     GetCrop_Day1() + GetCrop_DaysToFlowering()):
        # not yet flowering
        SetScorAT1(0.0)
        SetScorAT2(0.0)
    else:
        # water stress affecting leaf expansion
        # NOTE: time to reach end determinancy  is tHImax (i.e. flowering/2 or
        # senescence)
        if GetCrop_DeterminancyLinked():
            tHImax = roundc(GetCrop_LengthFlowering() / 2.0, mold=1)
        else:
            tHImax = GetCrop_DaysToSenescence() - GetCrop_DaysToFlowering()
        if (GetSimulation_FromDayNr() <= (GetSimulation_DelayedDays() +
                                          GetCrop_Day1() + GetCrop_DaysToFlowering() + tHImax)) and \
           (tHImax > 0):
            # not yet end determinancy
            SetScorAT1(1.0 / tHImax)
            SetScorAT1(GetScorAT1() * (GetSimulation_FromDayNr() -
                       (GetSimulation_DelayedDays() + GetCrop_Day1() +
                        GetCrop_DaysToFlowering())))
            if GetScorAT1() > 1.0:
                SetScorAT1(1.0)
        else:
            SetScorAT1(1.0)  # after period of effect
        # water stress affecting stomatal closure
        # period of effect is yield formation
        if GetCrop_dHIdt() > 99.0:
            tHImax = 0
        else:
            tHImax = roundc(GetCrop_HI() / GetCrop_dHIdt(), mold=1)
        if (GetSimulation_FromDayNr() <= (GetSimulation_DelayedDays() +
                                          GetCrop_Day1() + GetCrop_DaysToFlowering() + tHImax)) and \
           (tHImax > 0):
            # not yet end yield formation
            SetScorAT2(1.0 / float(tHImax))
            SetScorAT2(GetScorAT2() * (GetSimulation_FromDayNr() -
                       (GetSimulation_DelayedDays() + GetCrop_Day1() +
                        GetCrop_DaysToFlowering())))
            if GetScorAT2() > 1.0:
                SetScorAT2(1.0)
        else:
            SetScorAT2(1.0)  # after period of effect

    if GetOutDaily():
        DetermineGrowthStage(GetDayNri(), GetCCiPrev())

    # 20. Settings for start
    SetStartMode(True)
    SetStressLeaf(float(undef_int))
    SetStressSenescence(float(undef_int))


def CalculateTimeToReachZmin(ZMin, ZMax, RootShape, L0, LZmax, GGDL0, GDDLZmax,
                             TheModeCycle, tDaysZmin, tGDDZmin):
    Zini = 0.0
    Zfunction = 0.0

    tDaysZmin = float(L0)
    tGDDZmin = float(GGDL0)

    if (GetSimulParam_RootPercentZmin() < 100) and (ZMin < ZMax):
        Zini = ZMin * (float(GetSimulParam_RootPercentZmin()) / 100.0)

        Zfunction = math.exp(
            (float(RootShape) / 10.0)
            * math.log((ZMin - Zini) / (ZMax - Zini))
        )

        if TheModeCycle == ModeCycle_GDDays:
            if GDDLZmax > (GGDL0 / 2.0):
                tGDDZmin = (
                    Zfunction * float(GDDLZmax - (GGDL0 / 2.0))
                    + float(GGDL0 / 2.0)
                )
        else:
            if LZmax > (L0 / 2.0):
                tDaysZmin = (
                    Zfunction * float(LZmax - (L0 / 2.0))
                    + float(L0 / 2.0)
                )

    return tDaysZmin, tGDDZmin

def CalculateRootingDepth(tDaysZmin, tGDDZmin, ZiPrev, GDDayi, RootingDepth):
    tCalDayReal = 0.0
    tCalGDD = 0.0
    CalSumGDDPrev = 0.0
    Zini = 0.0
    Zfunction = 0.0
    tCalDay = 0
    tCalDayNow = 0

    # initialize
    tCalDayNow = GetDayNri() - GetCrop_Day1() + 1            # actual time (calendar day)
    tCalDay = tCalDayNow
    tCalGDD = GetSimulation_SumGDD()                         # actual time (sum of GDD)
    CalSumGDDPrev = GetSumGDDPrev()                          # sum of GDD at previous day

    # Adjust time after planting (tCalDay OR tCalGDD) to simulate root zone expansion
    Zini = GetCrop_RootMin() * (float(GetSimulParam_RootPercentZmin()) / 100.0)

    if (GetCrop_RootMin() < GetCrop_RootMax()) and (ZiPrev > Zini):
        # valid for calendar and GDD time
        Zfunction = math.exp(
            (float(GetCrop_RootShape()) / 10.0)
            * math.log((ZiPrev - Zini) / (GetCrop_RootMax() - Zini))
        )

        if GetCrop_ModeCycle() == ModeCycle_GDDays:
            # growing degree days
            if GetSimulation_SumGDD() > tGDDZmin:
                # root zone expansion can exceed Zmin
                # time to simulate root zone expansion is given by Zr of previous day (ZiPrev)
                CalSumGDDPrev = (
                    Zfunction
                    * float(GetCrop_GDDaysToMaxRooting() - (GetCrop_GDDaysToGermination() / 2.0))
                    + float(GetCrop_GDDaysToGermination() / 2.0)
                )

                tCalGDD = CalSumGDDPrev + GDDayi   # add GDD of today to get adjusted sum GDD
                if tCalGDD > GetSimulation_SumGDD():
                    tCalGDD = GetSimulation_SumGDD()

        else:
            # calendar days
            if float(tCalDayNow) > tDaysZmin:
                # root zone expansion can exceed Zmin
                # time to simulate root zone expansion is given by Zr of previous day (ZiPrev)
                tCalDayReal = (
                    Zfunction
                    * float(GetCrop_DaysToMaxRooting() - (GetCrop_DaysToGermination() / 2.0))
                    + float(GetCrop_DaysToGermination() / 2.0)
                )

                tCalDay = roundc(tCalDayReal, mold=1) + 1  # integer value + 1 day
                if tCalDay > tCalDayNow:
                    tCalDay = tCalDayNow

    # calculate root zone expansion with time after planting given by Zr of previous day (ZiPrev)
    RootingDepth = AdjustedRootingDepth(
        GetPlotVarCrop_ActVal(), GetPlotVarCrop_PotVal(), GetTpot(), GetTact(), GetStressLeaf(),
        GetStressSenescence(), tCalDay, GetCrop_DaysToGermination(), GetCrop_DaysToMaxRooting(), GetCrop_DaysToHarvest(),
        GetCrop_GDDaysToGermination(), GetCrop_GDDaysToMaxRooting(), GetCrop_GDDaysToHarvest(),
        CalSumGDDPrev, tCalGDD,
        GetCrop_RootMin(), GetCrop_RootMax(), ZiPrev, GetCrop_RootShape(),
        GetCrop_ModeCycle()
    )

    if RootingDepth < ZiPrev:
        RootingDepth = ZiPrev

    return RootingDepth


def GetSumGDDBeforeSimulation(SumGDDtillDay, SumGDDtillDayM1):
    SetSimulation_SumGDD(0.0)
    if (GetTemperatureFile() != '(None)') and (GetTemperatureFile() != '(External)'):
        totalname = GetTemperatureFileFull()

        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(totalname).lstrip("/\\"),
            )
        )

        if os.path.isfile(full_path):
            if GetTemperatureRecord_DataType() == datatype_Daily:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
                    lines = f0.read().splitlines()

                data_lines = lines[8:]

                # days before first day of simulation (= DayNri)
                for i in range(max(GetTemperatureRecord_FromDayNr(), GetCrop_Day1()), DayNri):
                    StringREAD = data_lines[i - GetTemperatureRecord_FromDayNr()]
                    Tmin_temp = GetTmin()
                    Tmax_temp = GetTmax()
                    Tmin_temp, Tmax_temp = SplitStringInTwoParams(StringREAD, Tmin_temp, Tmax_temp)
                    SetTmin(Tmin_temp)
                    SetTmax(Tmax_temp)
                    SetSimulation_SumGDD(
                        GetSimulation_SumGDD()
                        + DegreesDay(
                            GetCrop_Tbase(),
                            GetCrop_Tupper(),
                            GetTmin(),
                            GetTmax(),
                            GetSimulParam_GDDMethod(),
                        )
                    )

            elif GetTemperatureRecord_DataType() == datatype_Decadely:
                DayX = GetCrop_Day1()
                # first day of cropping
                TminDataSet_temp = GetTminDataSet()
                TmaxDataSet_temp = GetTmaxDataSet()
                TminDataSet_temp, TmaxDataSet_temp = GetDecadeTemperatureDataSet(
                    DayX, TminDataSet_temp, TmaxDataSet_temp
                )
                SetTminDataSet(TminDataSet_temp)
                SetTmaxDataSet(TmaxDataSet_temp)
                i = 1
                while GetTminDataSet_DayNr(i) != DayX:
                    i = i + 1
                SetTmin(GetTminDataSet_Param(i))
                SetTmax(GetTmaxDataSet_Param(i))
                SetSimulation_SumGDD(
                    DegreesDay(
                        GetCrop_Tbase(),
                        GetCrop_Tupper(),
                        GetTmin(),
                        GetTmax(),
                        GetSimulParam_GDDMethod(),
                    )
                )
                # next days
                while DayX < DayNri:
                    DayX = DayX + 1
                    if DayX > GetTminDataSet_DayNr(31):
                        TminDataSet_temp = GetTminDataSet()
                        TmaxDataSet_temp = GetTmaxDataSet()
                        TminDataSet_temp, TmaxDataSet_temp = GetDecadeTemperatureDataSet(
                            DayX, TminDataSet_temp, TmaxDataSet_temp
                        )
                        SetTminDataSet(TminDataSet_temp)
                        SetTmaxDataSet(TmaxDataSet_temp)
                        i = 0
                    i = i + 1
                    SetTmin(GetTminDataSet_Param(i))
                    SetTmax(GetTmaxDataSet_Param(i))
                    SetSimulation_SumGDD(
                        GetSimulation_SumGDD()
                        + DegreesDay(
                            GetCrop_Tbase(),
                            GetCrop_Tupper(),
                            GetTmin(),
                            GetTmax(),
                            GetSimulParam_GDDMethod(),
                        )
                    )

            elif GetTemperatureRecord_DataType() == datatype_Monthly:
                DayX = GetCrop_Day1()
                # first day of cropping
                TminDataSet_temp = GetTminDataSet()
                TmaxDataSet_temp = GetTmaxDataSet()
                TminDataSet_temp, TmaxDataSet_temp = GetMonthlyTemperatureDataSet(
                    DayX, TminDataSet_temp, TmaxDataSet_temp
                )
                SetTminDataSet(TminDataSet_temp)
                SetTmaxDataSet(TmaxDataSet_temp)
                i = 1
                while GetTminDataSet_DayNr(i) != DayX:
                    i = i + 1
                SetTmin(GetTminDataSet_Param(i))
                SetTmax(GetTmaxDataSet_Param(i))
                SetSimulation_SumGDD(
                    DegreesDay(
                        GetCrop_Tbase(),
                        GetCrop_Tupper(),
                        GetTmin(),
                        GetTmax(),
                        GetSimulParam_GDDMethod(),
                    )
                )
                # next days
                while DayX < DayNri:
                    DayX = DayX + 1
                    if DayX > GetTminDataSet_DayNr(31):
                        TminDataSet_temp = GetTminDataSet()
                        TmaxDataSet_temp = GetTmaxDataSet()
                        TminDataSet_temp, TmaxDataSet_temp = GetMonthlyTemperatureDataSet(
                            DayX, TminDataSet_temp, TmaxDataSet_temp
                        )
                        SetTminDataSet(TminDataSet_temp)
                        SetTmaxDataSet(TmaxDataSet_temp)
                        i = 0
                    i = i + 1
                    SetTmin(GetTminDataSet_Param(i))
                    SetTmax(GetTmaxDataSet_Param(i))
                    SetSimulation_SumGDD(
                        GetSimulation_SumGDD()
                        + DegreesDay(
                            GetCrop_Tbase(),
                            GetCrop_Tupper(),
                            GetTmin(),
                            GetTmax(),
                            GetSimulParam_GDDMethod(),
                        )
                    )

    if GetTemperatureFile() == '(None)':
        SetSimulation_SumGDD(
            DegreesDay(
                GetCrop_Tbase(),
                GetCrop_Tupper(),
                GetSimulParam_Tmin(),
                GetSimulParam_Tmax(),
                GetSimulParam_GDDMethod(),
            )
            * (DayNri - GetCrop_Day1() + 1)
        )
        if GetSimulation_SumGDD() < 0.0:
            SetSimulation_SumGDD(0.0)
        SumGDDtillDay = GetSimulation_SumGDD()
        SumGDDtillDayM1 = (
            DegreesDay(
                GetCrop_Tbase(),
                GetCrop_Tupper(),
                GetSimulParam_Tmin(),
                GetSimulParam_Tmax(),
                GetSimulParam_GDDMethod(),
            )
            * (DayNri - GetCrop_Day1())
        )
        if SumGDDtillDayM1 < 0.0:
            SumGDDtillDayM1 = 0.0
    elif GetTemperatureFile() == '(External)':
        SumGDDtillDay = GetSimulation_SumGDD()
        SumGDDtillDayM1 = SumGDDtillDay - DegreesDay(
            GetCrop_Tbase(),
            GetCrop_Tupper(),
            GetTmin(),
            GetTmax(),
            GetSimulParam_GDDMethod(),
        )
    else:
        SumGDDtillDay = GetSimulation_SumGDD()
        SumGDDtillDayM1 = SumGDDtillDay - DegreesDay(
            GetCrop_Tbase(),
            GetCrop_Tupper(),
            GetTmin(),
            GetTmax(),
            GetSimulParam_GDDMethod(),
        )

    return SumGDDtillDay, SumGDDtillDayM1

def OpenIrrigationFile():
    totalname = ""
    StringREAD = ""
    DNr = 0
    Ir1 = 0.0
    Ir2 = 0.0
    VersionNr = 0.0
    FromDay_temp = 0
    TimeInfo_temp = 0
    DepthInfo_temp = 0
    IrriECw_temp = 0.0
    TempString = ""

    if ((GetIrriMode() == IrriMode_Manual)
        or (GetIrriMode() == IrriMode_Generate)):

        if GetIrriFile() != '(None)':
            totalname = GetIrriFileFull()
        else:
            totalname = GetPathNameProg() + 'IrriSchedule.AqC'

        fIrri_open(totalname, 'r')

        TempString = fIrri_read()  # description
        TempString = fIrri_read()  # AquaCrop version
        VersionNr = float(TempString.split()[0])

        if roundc(VersionNr * 10, mold=1) < 32:
            SetGlobalIrriECw(True)
        else:
            SetGlobalIrriECw(False)

        for i in range(1, 7):
            TempString = fIrri_read()  # irrigation info (already loaded)

        if ((roundc(VersionNr * 10, mold=1) >= 73)
            and (GetIrriMode() == IrriMode_Generate)):
            TempString = fIrri_read()  # just skipping, already set in global.f90
        else:
            SetIrriInfoLastDay(undef_int)

        if GetIrriMode() == IrriMode_Manual:
            if GetIrriFirstDayNr() == undef_int:
                DNr = GetDayNri() - GetCrop_Day1() + 1
            else:
                DNr = GetDayNri() - GetIrriFirstDayNr() + 1

            while True:
                StringREAD = fIrri_read()
                if fIrri_eof():
                    SetIrriInfoRecord1_NoMoreInfo(True)
                else:
                    SetIrriInfoRecord1_NoMoreInfo(False)
                    if GetGlobalIrriECw():
                        Ir1, Ir2 = SplitStringInTwoParams(StringREAD, Ir1, Ir2)
                    else:
                        IrriECw_temp = GetSimulation_IrriECw()
                        Ir1, Ir2, IrriECw_temp = SplitStringInThreeParams(StringREAD)
                        SetSimulation_IrriECw(IrriECw_temp)

                    SetIrriInfoRecord1_TimeInfo(roundc(Ir1, mold=1))
                    SetIrriInfoRecord1_DepthInfo(roundc(Ir2, mold=1))

                if (GetIrriInfoRecord1_NoMoreInfo()
                    or (GetIrriInfoRecord1_TimeInfo() >= DNr)):
                    break

        elif GetIrriMode() == IrriMode_Generate:
            for i in range(1, 3):
                TempString = fIrri_read()
                # time and depth criterion (already loaded)

            SetIrriInfoRecord1_NoMoreInfo(False)

            if roundc(VersionNr * 10, mold=1) < 32:
                TempString = fIrri_read()
                parts = TempString.split()
                FromDay_temp = int(parts[0])
                TimeInfo_temp = int(parts[1])
                DepthInfo_temp = int(parts[2])

                SetIrriInfoRecord1_FromDay(FromDay_temp)
                SetIrriInfoRecord1_TimeInfo(TimeInfo_temp)
                SetIrriInfoRecord1_DepthInfo(DepthInfo_temp)
            else:
                TempString = fIrri_read()
                parts = TempString.split()
                FromDay_temp = int(parts[0])
                TimeInfo_temp = int(parts[1])
                DepthInfo_temp = int(parts[2])
                IrriECw_temp = float(parts[3])

                SetIrriInfoRecord1_FromDay(FromDay_temp)
                SetIrriInfoRecord1_TimeInfo(TimeInfo_temp)
                SetIrriInfoRecord1_DepthInfo(DepthInfo_temp)
                SetSimulation_IrriECw(IrriECw_temp)

            TempString = fIrri_read()
            if fIrri_eof():
                SetIrriInfoRecord1_ToDay(GetCrop_DayN() - GetCrop_Day1() + 1)
            else:
                SetIrriInfoRecord2_NoMoreInfo(False)

                if GetGlobalIrriECw():
                    parts = TempString.split()
                    FromDay_temp = int(parts[0])
                    TimeInfo_temp = int(parts[1])
                    DepthInfo_temp = int(parts[2])

                    SetIrriInfoRecord2_FromDay(FromDay_temp)
                    SetIrriInfoRecord2_TimeInfo(TimeInfo_temp)
                    SetIrriInfoRecord2_DepthInfo(DepthInfo_temp)
                else:
                    parts = TempString.split()
                    FromDay_temp = int(parts[0])
                    TimeInfo_temp = int(parts[1])
                    DepthInfo_temp = int(parts[2])
                    IrriECw_temp = float(parts[3])

                    SetIrriInfoRecord2_FromDay(FromDay_temp)
                    SetIrriInfoRecord2_TimeInfo(TimeInfo_temp)
                    SetIrriInfoRecord2_DepthInfo(DepthInfo_temp)
                    SetSimulation_IrriECw(IrriECw_temp)

                SetIrriInfoRecord1_ToDay(GetIrriInfoRecord2_FromDay() - 1)

def OpenHarvestInfo():
    totalname = ""
    TempString = ""

    if GetManFile() != "(None)":
        totalname = GetManFilefull()
    else:
        totalname = GetPathNameSimul() + "Cuttings.AqC"

    fCuts_open(totalname, "r")

    TempString = fCuts_read()  # description
    TempString = fCuts_read()  # AquaCrop version

    if GetManFile() != "(None)":
        for _ in range(10):
            TempString = fCuts_read()  # management info

    for _ in range(12):
        TempString = fCuts_read()  # cuttings info (already loaded)

    GetNextHarvest()



def GetNextHarvest():
    InfoLoaded = False
    DayNrXX = 0
    FromDay_temp = 0
    IntervalInfo_temp = 0.0
    IntervalGDD_temp = 0.0
    MassInfo_temp = 0.0
    TempString = ""

    if not GetManagement_Cuttings_Generate():
        TempString = fCuts_read()
        if not fCuts_eof():
            FromDay_temp = int(TempString.split()[0])
            SetCutInfoRecord1_FromDay(FromDay_temp)
            SetCutInfoRecord1_NoMoreInfo(False)
            if GetManagement_Cuttings_FirstDayNr() != undef_int:
                # scroll to start growing cycle
                DayNrXX = GetManagement_Cuttings_FirstDayNr() + GetCutInfoRecord1_FromDay() - 1
                while (DayNrXX < GetCrop_Day1()) and (GetCutInfoRecord1_NoMoreInfo() == False):
                    TempString = fCuts_read()
                    if not fCuts_eof():
                        FromDay_temp = int(TempString.split()[0])
                        SetCutInfoRecord1_FromDay(FromDay_temp)
                        DayNrXX = GetManagement_Cuttings_FirstDayNr() + GetCutInfoRecord1_FromDay() - 1
                    else:
                        SetCutInfoRecord1_NoMoreInfo(True)
        else:
            SetCutInfoRecord1_NoMoreInfo(True)
    else:
        if GetNrCut() == 0:
            if GetManagement_Cuttings_Criterion() == TimeCuttings_IntDay:
                TempString = fCuts_read()
                parts = TempString.split()
                FromDay_temp = int(parts[0])
                IntervalInfo_temp = float(parts[1])
                SetCutInfoRecord1_FromDay(FromDay_temp)
                SetCutInfoRecord1_IntervalInfo(roundc(IntervalInfo_temp, mold=1))
            elif GetManagement_Cuttings_Criterion() == TimeCuttings_IntGDD:
                TempString = fCuts_read()
                parts = TempString.split()
                FromDay_temp = int(parts[0])
                IntervalGDD_temp = float(parts[1])
                SetCutInfoRecord1_FromDay(FromDay_temp)
                SetCutInfoRecord1_IntervalGDD(IntervalGDD_temp)
            elif ((GetManagement_Cuttings_Criterion() == TimeCuttings_DryB)
                  or (GetManagement_Cuttings_Criterion() == TimeCuttings_DryY)
                  or (GetManagement_Cuttings_Criterion() == TimeCuttings_FreshY)):
                TempString = fCuts_read()
                parts = TempString.split()
                FromDay_temp = int(parts[0])
                MassInfo_temp = float(parts[1])
                SetCutInfoRecord1_FromDay(FromDay_temp)
                SetCutInfoRecord1_MassInfo(MassInfo_temp)

            if GetCutInfoRecord1_FromDay() < GetManagement_Cuttings_Day1():
                SetCutInfoRecord1_FromDay(GetManagement_Cuttings_Day1())

            InfoLoaded = False

        while True:
            TempString = fCuts_read()
            if not fCuts_eof():
                if GetManagement_Cuttings_Criterion() == TimeCuttings_IntDay:
                    parts = TempString.split()
                    FromDay_temp = int(parts[0])
                    IntervalInfo_temp = float(parts[1])
                    SetCutInfoRecord2_FromDay(FromDay_temp)
                    SetCutInfoRecord2_IntervalInfo(roundc(IntervalInfo_temp, mold=1))
                elif GetManagement_Cuttings_Criterion() == TimeCuttings_IntGDD:
                    parts = TempString.split()
                    FromDay_temp = int(parts[0])
                    IntervalGDD_temp = float(parts[1])
                    SetCutInfoRecord2_FromDay(FromDay_temp)
                    SetCutInfoRecord2_IntervalGDD(IntervalGDD_temp)
                elif ((GetManagement_Cuttings_Criterion() == TimeCuttings_DryB)
                      or (GetManagement_Cuttings_Criterion() == TimeCuttings_DryY)
                      or (GetManagement_Cuttings_Criterion() == TimeCuttings_FreshY)):
                    parts = TempString.split()
                    FromDay_temp = int(parts[0])
                    MassInfo_temp = float(parts[1])
                    SetCutInfoRecord2_FromDay(FromDay_temp)
                    SetCutInfoRecord2_MassInfo(MassInfo_temp)

                if GetCutInfoRecord2_FromDay() < GetManagement_Cuttings_Day1():
                    SetCutInfoRecord2_FromDay(GetManagement_Cuttings_Day1())

                if GetCutInfoRecord2_FromDay() <= GetCutInfoRecord1_FromDay():
                    # CutInfoRecord2 becomes CutInfoRecord1
                    SetCutInfoRecord1_FromDay(GetCutInfoRecord2_FromDay())
                    if GetManagement_Cuttings_Criterion() == TimeCuttings_IntDay:
                        SetCutInfoRecord1_IntervalInfo(GetCutInfoRecord2_IntervalInfo())
                    elif GetManagement_Cuttings_Criterion() == TimeCuttings_IntGDD:
                        SetCutInfoRecord1_IntervalGDD(GetCutInfoRecord2_IntervalGDD())
                    elif ((GetManagement_Cuttings_Criterion() == TimeCuttings_DryB)
                          or (GetManagement_Cuttings_Criterion() == TimeCuttings_DryY)
                          or (GetManagement_Cuttings_Criterion() == TimeCuttings_FreshY)):
                        SetCutInfoRecord1_MassInfo(GetCutInfoRecord2_MassInfo())
                    SetCutInfoRecord1_NoMoreInfo(False)
                else:
                    SetCutInfoRecord1_ToDay(GetCutInfoRecord2_FromDay() - 1)
                    SetCutInfoRecord1_NoMoreInfo(False)
                    if GetManagement_Cuttings_NrDays() != undef_int:
                        if GetCutInfoRecord1_ToDay() > (GetManagement_Cuttings_Day1() + GetManagement_Cuttings_NrDays() - 1):
                            SetCutInfoRecord1_ToDay(GetManagement_Cuttings_Day1() + GetManagement_Cuttings_NrDays() - 1)
                            SetCutInfoRecord1_NoMoreInfo(True)
                    InfoLoaded = True
            else:
                if GetNrCut() > 0:
                    SetCutInfoRecord1_FromDay(GetCutInfoRecord2_FromDay())
                    if GetManagement_Cuttings_Criterion() == TimeCuttings_IntDay:
                        SetCutInfoRecord1_IntervalInfo(GetCutInfoRecord2_IntervalInfo())
                    elif GetManagement_Cuttings_Criterion() == TimeCuttings_IntGDD:
                        SetCutInfoRecord1_IntervalGDD(GetCutInfoRecord2_IntervalGDD())
                    elif ((GetManagement_Cuttings_Criterion() == TimeCuttings_DryB)
                          or (GetManagement_Cuttings_Criterion() == TimeCuttings_DryY)
                          or (GetManagement_Cuttings_Criterion() == TimeCuttings_FreshY)):
                        SetCutInfoRecord1_MassInfo(GetCutInfoRecord2_MassInfo())

                SetCutInfoRecord1_ToDay(GetCrop_DaysToHarvest())
                if GetManagement_Cuttings_NrDays() != undef_int:
                    if GetCutInfoRecord1_ToDay() > (GetManagement_Cuttings_Day1() + GetManagement_Cuttings_NrDays() - 1):
                        SetCutInfoRecord1_ToDay(GetManagement_Cuttings_Day1() + GetManagement_Cuttings_NrDays() - 1)

                SetCutInfoRecord1_NoMoreInfo(True)
                InfoLoaded = True

            if InfoLoaded == True:
                break


def DetermineGrowthStage(Dayi, CCiPrev):
    VirtualDay = Dayi - GetSimulation_DelayedDays() - GetCrop_Day1()
    if VirtualDay < 0:
        SetStageCode(0)  # before cropping period
    else:
        if VirtualDay < GetCrop_DaysToGermination():
            SetStageCode(1)  # sown --> emergence OR transplant recovering
        else:
            SetStageCode(2)  # vegetative development
            if (GetCrop_subkind() == subkind_Grain) and \
               (VirtualDay >= GetCrop_DaysToFlowering()):
                if VirtualDay < (GetCrop_DaysToFlowering() +
                                 GetCrop_LengthFlowering()):
                    SetStageCode(3)  # flowering
                else:
                    SetStageCode(4)  # yield formation
            if (GetCrop_subkind() == subkind_Tuber) and \
               (VirtualDay >= GetCrop_DaysToFlowering()):
                SetStageCode(4)  # yield formation
            if (VirtualDay > GetCrop_DaysToGermination()) and \
               (CCiPrev < sys.float_info.epsilon):
                SetStageCode(int(undef_int))  # no growth stage
            if VirtualDay >= \
               (GetCrop_Length_i(1) + GetCrop_Length_i(2) +
                GetCrop_Length_i(3) + GetCrop_Length_i(4)):
                SetStageCode(0)  # after cropping period

def GetZandECgwt(ZiAqua, ECiAqua):
    ZiIN = ZiAqua
    if GetGwTable_DNr1() == GetGwTable_DNr2():
        ZiAqua = GetGwTable_Z1()
        ECiAqua = GetGwTable_EC1()
    else:
        ZiAqua = GetGwTable_Z1() + roundc(
            (GetDayNri() - GetGwTable_DNr1())
            * (GetGwTable_Z2() - GetGwTable_Z1())
            / float(GetGwTable_DNr2() - GetGwTable_DNr1()),
            mold=1
        )
        ECiAqua = GetGwTable_EC1() + (
            (GetDayNri() - GetGwTable_DNr1())
            * (GetGwTable_EC2() - GetGwTable_EC1())
            / float(GetGwTable_DNr2() - GetGwTable_DNr1())
        )

    if ZiAqua != ZiIN:
        Comp_temp = GetCompartment()
        Comp_temp = CalculateAdjustedFC((ZiAqua / 100.0), Comp_temp)
        SetCompartment(Comp_temp)

    return ZiAqua, ECiAqua

def AdvanceOneTimeStep(WPi, HarvestNow):
    PotValSF = 0.0
    KsTr = 0.0
    TESTVALY = 0.0
    PreIrri = 0.0
    StressStomata = 0.0
    FracAssim = 0.0
    VirtualTimeCC = 0
    DayInSeason = 0
    SumGDDadjCC = 0.0
    RatDGDD = 0.0
    Biomass_temp = 0.0
    BiomassPot_temp = 0.0
    BiomassUnlim_temp = 0.0
    BiomassTot_temp = 0.0
    YieldPart_temp = 0.0
    ECe_temp = 0.0
    ECsw_temp = 0.0
    ECswFC_temp = 0.0
    KsSalt_temp = 0.0
    GwTable_temp = rep_GwTable()
    Store_temp = False
    Mobilize_temp = False
    ToMobilize_temp = 0.0
    Bmobilized_temp = 0.0
    EffectStress_temp = rep_EffectStress()
    SWCtopSoilConsidered_temp = False
    ZiAqua_temp = 0
    ECiAqua_temp = 0.0
    TactWeedInfested_temp = 0.0
    Bin_temp = 0.0
    Bout_temp = 0.0
    TargetTimeVal = 0
    TargetDepthVal = 0
    PreviousStressLevel_temp = 0
    StressSFadjNEW_temp = 0
    CCxWitheredTpotNoS_temp = 0.0
    StressLeaf_temp = 0.0
    StressSenescence_temp = 0.0
    TimeSenescence_temp = 0.0
    SumKcTopStress_temp = 0.0
    SumKci_temp = 0.0
    WeedRCi_temp = 0.0
    CCiActualWeedInfested_temp = 0.0
    HItimesBEF_temp = 0.0
    ScorAT1_temp = 0.0
    ScorAT2_temp = 0.0
    HItimesAT1_temp = 0.0
    HItimesAT2_temp = 0.0
    HItimesAT_temp = 0.0
    alfaHI_temp = 0.0
    alfaHIAdj_temp = 0.0
    TESTVAL = 0.0
    RootingDepth_temp = 0.0
    WaterTableInProfile_temp = False
    NoMoreCrop_temp = False

    # 1. Get ETo
    if GetEToFile() == '(None)':
        SetETo(5.0)

    # 2. Get Rain
    if GetRainFile() == '(None)':
        SetRain(0.0)

    # 3. Start mode
    if GetStartMode():
        SetStartMode(False)

    # 4. Get depth and quality of the groundwater
    if not GetSimulParam_ConstGwt():
        if GetDayNri() > GetGwTable_DNr2():
            GwTable_temp = GetGwTable()
            GwTable_temp = GetGwtSet(GetDayNri(), GwTable_temp)
            SetGwTable(GwTable_temp)
        ZiAqua_temp = GetZiAqua()
        ECiAqua_temp = GetECiAqua()
        ZiAqua_temp, ECiAqua_temp = GetZandECgwt(ZiAqua_temp, ECiAqua_temp)
        SetZiAqua(ZiAqua_temp)
        SetECiAqua(ECiAqua_temp)
        WaterTableInProfile_temp = GetWaterTableInProfile()
        WaterTableInProfile_temp = CheckForWaterTableInProfile(
            (GetZiAqua() / 100.0),
            GetCompartment(),
            WaterTableInProfile_temp,
        )
        SetWaterTableInProfile(WaterTableInProfile_temp)
        if GetWaterTableInProfile():
            AdjustForWatertable()

    # 5. Get Irrigation
    SetIrrigation(0.0)
    TargetTimeVal, TargetDepthVal = GetIrriParam(TargetTimeVal, TargetDepthVal)

    # 6. get virtual time for CC development
    SumGDDadjCC = float(undef_int)
    if GetCrop_DaysToCCini() != 0:
        # regrowth
        if GetDayNri() >= GetCrop_Day1():
            # time setting for canopy development
            VirtualTimeCC = (
                (GetDayNri() - GetSimulation_DelayedDays() - GetCrop_Day1())
                + GetTadj()
                + GetCrop_DaysToGermination()
            )
            # adjusted time scale
            if VirtualTimeCC > GetCrop_DaysToHarvest():
                VirtualTimeCC = GetCrop_DaysToHarvest()
                # special case where L123 > L1234
            if VirtualTimeCC > GetCrop_DaysToFullCanopy():
                if (GetDayNri() - GetSimulation_DelayedDays() - GetCrop_Day1()) <= GetCrop_DaysToSenescence():
                    VirtualTimeCC = GetCrop_DaysToFullCanopy() + roundc(
                        GetDayFraction()
                        * (
                            (GetDayNri() - GetSimulation_DelayedDays() - GetCrop_Day1())
                            + GetTadj()
                            + GetCrop_DaysToGermination()
                            - GetCrop_DaysToFullCanopy()
                        ),
                        mold=1,
                    )  # slow down
                else:
                    VirtualTimeCC = GetDayNri() - GetSimulation_DelayedDays() - GetCrop_Day1()  # switch time scale
            if GetCrop_ModeCycle() == ModeCycle_GDDays:
                SumGDDadjCC = GetSimulation_SumGDDfromDay1() + GetGDDTadj() + GetCrop_GDDaysToGermination()
                if SumGDDadjCC > GetCrop_GDDaysToHarvest():
                    SumGDDadjCC = GetCrop_GDDaysToHarvest()
                    # special case where L123 > L1234
                if SumGDDadjCC > GetCrop_GDDaysToFullCanopy():
                    if GetSimulation_SumGDDfromDay1() <= GetCrop_GDDaysToSenescence():
                        SumGDDadjCC = GetCrop_GDDaysToFullCanopy() + roundc(
                            GetGDDayFraction()
                            * (
                                GetSimulation_SumGDDfromDay1()
                                + GetGDDTadj()
                                + GetCrop_GDDaysToGermination()
                                - GetCrop_GDDaysToFullCanopy()
                            ),
                            mold=1,
                        )  # slow down
                    else:
                        SumGDDadjCC = GetSimulation_SumGDDfromDay1()
                        # switch time scale
            # CC initial (at the end of previous day) when simulation starts
            # before regrowth,
            if (GetDayNri() == GetCrop_Day1()) and (GetDayNri() > GetSimulation_FromDayNr()):
                RatDGDD = 1.0
                if ((GetCrop_ModeCycle() == ModeCycle_GDDays)
                    and (GetCrop_GDDaysToFullCanopySF() < GetCrop_GDDaysToSenescence())):
                    RatDGDD = (
                        (GetCrop_DaysToSenescence() - GetCrop_DaysToFullCanopySF())
                        / float(GetCrop_GDDaysToSenescence() - GetCrop_GDDaysToFullCanopySF())
                    )
                EffectStress_temp = GetSimulation_EffectStress()
                EffectStress_temp = CropStressParametersSoilFertility(
                    GetCrop_StressResponse(),
                    GetStressSFadjNEW(),
                    EffectStress_temp,
                )
                SetSimulation_EffectStress(EffectStress_temp)
                SetCCiPrev(
                    CCiniTotalFromTimeToCCini(
                        GetCrop_DaysToCCini(),
                        GetCrop_GDDaysToCCini(),
                        GetCrop_DaysToGermination(),
                        GetCrop_DaysToFullCanopy(),
                        GetCrop_DaysToFullCanopySF(),
                        GetCrop_DaysToSenescence(),
                        GetCrop_DaysToHarvest(),
                        GetCrop_GDDaysToGermination(),
                        GetCrop_GDDaysToFullCanopy(),
                        GetCrop_GDDaysToFullCanopySF(),
                        GetCrop_GDDaysToSenescence(),
                        GetCrop_GDDaysToHarvest(),
                        GetCrop_CCo(),
                        GetCrop_CCx(),
                        GetCrop_CGC(),
                        GetCrop_GDDCGC(),
                        GetCrop_CDC(),
                        GetCrop_GDDCDC(),
                        RatDGDD,
                        GetSimulation_EffectStress_RedCGC(),
                        GetSimulation_EffectStress_RedCCX(),
                        GetSimulation_EffectStress_CDecline(),
                        (GetCCxTotal() / GetCrop_CCx()),
                        GetCrop_ModeCycle(),
                    )
                )
                # (CCxTotal/Crop.CCx) = fWeed
        else:
            # before start crop
            VirtualTimeCC = GetDayNri() - GetSimulation_DelayedDays() - GetCrop_Day1()
            if GetCrop_ModeCycle() == ModeCycle_GDDays:
                SumGDDadjCC = GetSimulation_SumGDD()
    else:
        # sown or transplanted
        VirtualTimeCC = GetDayNri() - GetSimulation_DelayedDays() - GetCrop_Day1()
        if GetCrop_ModeCycle() == ModeCycle_GDDays:
            SumGDDadjCC = GetSimulation_SumGDD()
        # CC initial (at the end of previous day) when simulation starts
        # before sowing/transplanting,
        if ((GetDayNri() == (GetCrop_Day1() + GetCrop_DaysToGermination()))
            and (GetDayNri() > GetSimulation_FromDayNr())):
            SetCCiPrev(GetCCoTotal())

    # 7. Rooting depth AND Inet day 1
    if (((GetCrop_ModeCycle() == ModeCycle_CalendarDays)
         and ((GetDayNri() - GetCrop_Day1() + 1) < GetCrop_DaysToHarvest()))
        or ((GetCrop_ModeCycle() == ModeCycle_GDDays)
            and (GetSimulation_SumGDD() < GetCrop_GDDaysToHarvest()))):
        if (((GetDayNri() - GetSimulation_DelayedDays()) >= GetCrop_Day1())
            and ((GetDayNri() - GetSimulation_DelayedDays()) <= GetCrop_DayN())):
            # rooting depth at DAP (at Crop.Day1, DAP = 1)

            """
            SetRootingDepth(
                AdjustedRootingDepth(
                    GetPlotVarCrop_ActVal(),
                    GetPlotVarCrop_PotVal(),
                    GetTpot(),
                    GetTact(),
                    GetStressLeaf(),
                    GetStressSenescence(),
                    (GetDayNri() - GetCrop_Day1() + 1),
                    GetCrop_DaysToGermination(),
                    GetCrop_DaysToMaxRooting(),
                    GetCrop_DaysToHarvest(),
                    GetCrop_GDDaysToGermination(),
                    GetCrop_GDDaysToMaxRooting(),
                    GetCrop_GDDaysToHarvest(),
                    GetSumGDDPrev(),
                    GetSimulation_SumGDD(),
                    GetCrop_RootMin(),
                    GetCrop_RootMax(),
                    GetZiprev(),
                    GetCrop_RootShape(),
                    GetCrop_ModeCycle(),
                )
            )
            """
            RootingDepth_temp = CalculateRootingDepth(tDaysZmin, tGDDZmin, GetZiprev(), GetGDDayi(), RootingDepth_temp)
            SetRootingDepth(RootingDepth_temp)
            SetZiprev(GetRootingDepth())
            # IN CASE rootzone drops below groundwate table
            if ((GetZiAqua() >= 0.0)
                and (GetRootingDepth() > (GetZiAqua() / 100.0))
                and (GetCrop_AnaeroPoint() > 0)):
                SetRootingDepth(GetZiAqua() / 100.0)
                if GetRootingDepth() < GetCrop_RootMin():
                    SetRootingDepth(GetCrop_RootMin())
        else:
            # In GDD mode, SumGDD needs to be higher than GDDaysToHarvest to prevent reset to zero before harvest
            if (GetCrop_ModeCycle() == ModeCycle_GDDays) and (GetSimulation_SumGDD() <= 0.0):
                SetRootingDepth(0.0)
            else:
                SetRootingDepth(GetZiprev())
    else:
        SetRootingDepth(GetZiprev())

    if (GetRootingDepth() > 0.0) and (GetDayNri() == GetCrop_Day1()):
        # initial root zone depletion day1 (for WRITE Output)
        SWCtopSoilConsidered_temp = GetSimulation_SWCtopSoilConsidered()
        SWCtopSoilConsidered_temp = DetermineRootZoneWC(GetRootingDepth(), SWCtopSoilConsidered_temp)
        SetSimulation_SWCtopSoilConsidered(SWCtopSoilConsidered_temp)
        if GetIrriMode() == IrriMode_Inet:
            PreIrri = AdjustSWCRootZone(PreIrri)  # required to start germination

    # 8. Transfer of Assimilates
    ToMobilize_temp = GetTransfer_ToMobilize()
    Bmobilized_temp = GetTransfer_Bmobilized()
    Store_temp = GetTransfer_Store()
    Mobilize_temp = GetTransfer_Mobilize()
    Bin_temp = GetBin()
    Bout_temp = GetBout()

    Bin_temp, Bout_temp, ToMobilize_temp, Bmobilized_temp, FracAssim, Store_temp, Mobilize_temp = InitializeTransferAssimilates(
        Bin_temp,
        Bout_temp,
        ToMobilize_temp,
        Bmobilized_temp,
        FracAssim,
        Store_temp,
        Mobilize_temp,
        HarvestNow,
    )
    SetTransfer_ToMobilize(ToMobilize_temp)
    SetTransfer_Bmobilized(Bmobilized_temp)
    SetTransfer_Store(Store_temp)
    SetTransfer_Mobilize(Mobilize_temp)
    SetBin(Bin_temp)
    SetBout(Bout_temp)

    # 9. RUN Soil water balance and actual Canopy Cover
    StressLeaf_temp = GetStressLeaf()
    StressSenescence_temp = GetStressSenescence()
    TimeSenescence_temp = GetTimeSenescence()
    NoMoreCrop_temp = GetNoMoreCrop()

    StressLeaf_temp, StressSenescence_temp, TimeSenescence_temp, NoMoreCrop_temp, TESTVAL = BUDGET_module(
        GetDayNri(),
        TargetTimeVal,
        TargetDepthVal,
        VirtualTimeCC,
        GetSumInterval(),
        GetDayLastCut(),
        GetStressTot_NrD(),
        GetTadj(),
        GetGDDTadj(),
        GetGDDayi(),
        GetCGCref(),
        GetGDDCGCref(),
        GetCO2i(),
        GetCCxTotal(),
        GetCCoTotal(),
        GetCDCTotal(),
        GetGDDCDCTotal(),
        SumGDDadjCC,
        GetCoeffb0Salt(),
        GetCoeffb1Salt(),
        GetCoeffb2Salt(),
        GetStressTot_Salt(),
        GetDayFraction(),
        GetGDDayFraction(),
        FracAssim,
        GetStressSFadjNEW(),
        GetTransfer_Store(),
        GetTransfer_Mobilize(),
        StressLeaf_temp,
        StressSenescence_temp,
        TimeSenescence_temp,
        NoMoreCrop_temp,
        TESTVAL,
    )

    SetStressLeaf(StressLeaf_temp)
    SetStressSenescence(StressSenescence_temp)
    SetTimeSenescence(TimeSenescence_temp)
    SetNoMoreCrop(NoMoreCrop_temp)

    # consider Pre-irrigation (6.) if IrriMode = Inet
    if ((GetRootingDepth() > 0.0) and (GetDayNri() == GetCrop_Day1())
        and (GetIrriMode() == IrriMode_Inet)):
        SetIrrigation(GetIrrigation() + PreIrri)
        SetSumWaBal_Irrigation(GetSumWaBal_Irrigation() + PreIrri)
        PreIrri = 0.0

    # total number of days in the season
    if GetCCiActual() > 0.0:
        if GetStressTot_NrD() < 0:
            SetStressTot_NrD(1)
        else:
            SetStressTot_NrD(GetStressTot_NrD() + 1)

    # 10. Potential biomass
    BiomassUnlim_temp = GetSumWaBal_BiomassUnlim()
    CCxWitheredTpotNoS_temp = GetCCxWitheredTpotNoS()
    CCxWitheredTpotNoS_temp, BiomassUnlim_temp = DeterminePotentialBiomass(
        VirtualTimeCC,
        SumGDDadjCC,
        GetCO2i(),
        GetGDDayi(),
        CCxWitheredTpotNoS_temp,
        BiomassUnlim_temp,
    )
    SetCCxWitheredTpotNoS(CCxWitheredTpotNoS_temp)
    SetSumWaBal_BiomassUnlim(BiomassUnlim_temp)

    # 11. Biomass and yield
    if ((GetRootingDepth() > 0.0) and (GetNoMoreCrop() == False)):
        SWCtopSoilConsidered_temp = GetSimulation_SWCtopSoilConsidered()
        SWCtopSoilConsidered_temp = DetermineRootZoneWC(GetRootingDepth(), SWCtopSoilConsidered_temp)
        SetSimulation_SWCtopSoilConsidered(SWCtopSoilConsidered_temp)
        # temperature stress affecting crop transpiration
        if GetCCiActual() <= ac_zero_threshold:
            KsTr = 1.0
        else:
            KsTr = KsTemperature(0.0, GetCrop_GDtranspLow(), GetGDDayi())
        SetStressTot_Temp(
            ((GetStressTot_NrD() - 1.0) * GetStressTot_Temp() + 100.0 * (1.0 - KsTr))
            / float(GetStressTot_NrD())
        )
        # soil salinity stress
        ECe_temp = GetRootZoneSalt_ECe()
        ECsw_temp = GetRootZoneSalt_ECsw()
        ECswFC_temp = GetRootZoneSalt_ECswFC()
        KsSalt_temp = GetRootZoneSalt_KsSalt()
        ECe_temp, ECsw_temp, ECswFC_temp, KsSalt_temp = DetermineRootZoneSaltContent(
            GetRootingDepth(),
            ECe_temp,
            ECsw_temp,
            ECswFC_temp,
            KsSalt_temp,
        )
        SetRootZoneSalt_ECe(ECe_temp)
        SetRootZoneSalt_ECsw(ECsw_temp)
        SetRootZoneSalt_ECswFC(ECswFC_temp)
        SetRootZoneSalt_KsSalt(KsSalt_temp)
        SetStressTot_Salt(
            ((GetStressTot_NrD() - 1.0) * GetStressTot_Salt()
             + 100.0 * (1.0 - GetRootZoneSalt_KsSalt()))
            / float(GetStressTot_NrD())
        )
        # Biomass and yield
        Store_temp = GetTransfer_Store()
        Mobilize_temp = GetTransfer_Mobilize()
        ToMobilize_temp = GetTransfer_ToMobilize()
        Bmobilized_temp = GetTransfer_Bmobilized()
        Biomass_temp = GetSumWaBal_Biomass()
        BiomassPot_temp = GetSumWaBal_BiomassPot()
        BiomassUnlim_temp = GetSumWaBal_BiomassUnlim()
        BiomassTot_temp = GetSumWaBal_BiomassTot()
        YieldPart_temp = GetSumWaBal_YieldPart()
        TactWeedInfested_temp = GetTactWeedInfested()
        PreviousStressLevel_temp = GetPreviousStressLevel()
        StressSFadjNEW_temp = GetStressSFadjNEW()
        CCxWitheredTpotNoS_temp = GetCCxWitheredTpotNoS()
        Bin_temp = GetBin()
        Bout_temp = GetBout()
        SumKcTopStress_temp = GetSumKcTopStress()
        SumKci_temp = GetSumKci()
        WeedRCi_temp = GetWeedRCi()
        CCiActualWeedInfested_temp = GetCCiActualWeedInfested()
        HItimesBEF_temp = GetHItimesBEF()
        ScorAT1_temp = GetScorAT1()
        ScorAT2_temp = GetScorAT2()
        HItimesAT1_temp = GetHItimesAT1()
        HItimesAT2_temp = GetHItimesAT2()
        HItimesAT_temp = GetHItimesAT()
        alfaHI_temp = GetalfaHI()
        alfaHIAdj_temp = GetalfaHIAdj()
        (
            FracAssim,
            Biomass_temp,
            BiomassPot_temp,
            BiomassUnlim_temp,
            BiomassTot_temp,
            YieldPart_temp,
            WPi,
            HItimesBEF_temp,
            ScorAT1_temp,
            ScorAT2_temp,
            HItimesAT1_temp,
            HItimesAT2_temp,
            HItimesAT_temp,
            alfaHI_temp,
            alfaHIAdj_temp,
            SumKcTopStress_temp,
            SumKci_temp,
            WeedRCi_temp,
            CCiActualWeedInfested_temp,
            TactWeedInfested_temp,
            StressSFadjNEW_temp,
            PreviousStressLevel_temp,
            Store_temp,
            Mobilize_temp,
            ToMobilize_temp,
            Bmobilized_temp,
            Bin_temp,
            Bout_temp,
            TESTVALY,
        ) = DetermineBiomassAndYield(
            GetDayNri(),
            GetETo(),
            GetTmin(),
            GetTmax(),
            GetCO2i(),
            GetGDDayi(),
            GetTact(),
            GetSumKcTop(),
            GetCGCref(),
            GetGDDCGCref(),
            GetCoeffb0(),
            GetCoeffb1(),
            GetCoeffb2(),
            GetFracBiomassPotSF(),
            GetCoeffb0Salt(),
            GetCoeffb1Salt(),
            GetCoeffb2Salt(),
            GetStressTot_Salt(),
            SumGDDadjCC,
            GetCCiActual(),
            FracAssim,
            VirtualTimeCC,
            GetSumInterval(),
            Biomass_temp,
            BiomassPot_temp,
            BiomassUnlim_temp,
            BiomassTot_temp,
            YieldPart_temp,
            WPi,
            HItimesBEF_temp,
            ScorAT1_temp,
            ScorAT2_temp,
            HItimesAT1_temp,
            HItimesAT2_temp,
            HItimesAT_temp,
            alfaHI_temp,
            alfaHIAdj_temp,
            SumKcTopStress_temp,
            SumKci_temp,
            WeedRCi_temp,
            CCiActualWeedInfested_temp,
            TactWeedInfested_temp,
            StressSFadjNEW_temp,
            PreviousStressLevel_temp,
            Store_temp,
            Mobilize_temp,
            ToMobilize_temp,
            Bmobilized_temp,
            Bin_temp,
            Bout_temp,
            TESTVALY,
        )

        SetTransfer_Store(Store_temp)
        SetTransfer_Mobilize(Mobilize_temp)
        SetTransfer_ToMobilize(ToMobilize_temp)
        SetTransfer_Bmobilized(Bmobilized_temp)
        SetSumWaBal_Biomass(Biomass_temp)
        SetSumWaBal_BiomassPot(BiomassPot_temp)
        SetSumWaBal_BiomassUnlim(BiomassUnlim_temp)
        SetSumWaBal_BiomassTot(BiomassTot_temp)
        SetSumWaBal_YieldPart(YieldPart_temp)
        SetTactWeedInfested(TactWeedInfested_temp)
        SetBin(Bin_temp)
        SetBout(Bout_temp)
        SetPreviousStressLevel(int(PreviousStressLevel_temp))
        SetStressSFadjNEW(int(StressSFadjNEW_temp))
        SetCCxWitheredTpotNoS(CCxWitheredTpotNoS_temp)
        SetSumKcTopStress(SumKcTopStress_temp)
        SetSumKci(SumKci_temp)
        SetWeedRCi(WeedRCi_temp)
        SetCCiActualWeedInfested(CCiActualWeedInfested_temp)
        SetHItimesBEF(HItimesBEF_temp)
        SetScorAT1(ScorAT1_temp)
        SetScorAT2(ScorAT2_temp)
        SetHItimesAT1(HItimesAT1_temp)
        SetHItimesAT2(HItimesAT2_temp)
        SetHItimesAT(HItimesAT_temp)
        SetalfaHI(alfaHI_temp)
        SetalfaHIAdj(alfaHIAdj_temp)
    else:
        # SenStage = undef_int !GDL, 20220423, not used
        SetWeedRCi(float(undef_int))  # no crop and no weed infestation
        SetCCiActualWeedInfested(0.0)  # no crop
        SetTactWeedInfested(0.0)  # no crop

    # 12. Reset after RUN
    if GetPreDay() == False:
        SetPreviousDayNr(GetSimulation_FromDayNr() - 1)
    SetPreDay(True)
    if GetDayNri() >= GetCrop_Day1():
        SetCCiPrev(GetCCiActual())
        if GetZiprev() < GetRootingDepth():
            SetZiprev(GetRootingDepth())
            # IN CASE groundwater table does not affect root development
        SetSumGDDPrev(GetSimulation_SumGDD())
    if TargetTimeVal == 1:
        SetIrriInterval(0)

    # 13. Cuttings
    if GetManagement_Cuttings_Considered():
        HarvestNow = False
        DayInSeason = GetDayNri() - GetCrop_Day1() + 1
        SetSumInterval(GetSumInterval() + 1)
        SetSumGDDcuts(GetSumGDDcuts() + GetGDDayi())
        if GetManagement_Cuttings_Generate() == False:
            if GetManagement_Cuttings_FirstDayNr() != undef_int:
                # adjust DayInSeason
                DayInSeason = GetDayNri() - GetManagement_Cuttings_FirstDayNr() + 1
            if ((DayInSeason >= GetCutInfoRecord1_FromDay())
                and (GetCutInfoRecord1_NoMoreInfo() == False)):
                HarvestNow = True
                GetNextHarvest()
            if GetManagement_Cuttings_FirstDayNr() != undef_int:
                # reset DayInSeason
                DayInSeason = GetDayNri() - GetCrop_Day1() + 1
        else:
            if ((DayInSeason > GetCutInfoRecord1_ToDay())
                and (GetCutInfoRecord1_NoMoreInfo() == False)):
                GetNextHarvest()
            if GetManagement_Cuttings_Criterion() == TimeCuttings_IntDay:
                if ((GetSumInterval() >= GetCutInfoRecord1_IntervalInfo())
                    and (DayInSeason >= GetCutInfoRecord1_FromDay())
                    and (DayInSeason <= GetCutInfoRecord1_ToDay())):
                    HarvestNow = True
            elif GetManagement_Cuttings_Criterion() == TimeCuttings_IntGDD:
                if ((GetSumGDDcuts() >= GetCutInfoRecord1_IntervalGDD())
                    and (DayInSeason >= GetCutInfoRecord1_FromDay())
                    and (DayInSeason <= GetCutInfoRecord1_ToDay())):
                    HarvestNow = True
            elif GetManagement_Cuttings_Criterion() == TimeCuttings_DryB:
                if (((GetSumWaBal_Biomass() - GetBprevSum()) >= GetCutInfoRecord1_MassInfo())
                    and (DayInSeason >= GetCutInfoRecord1_FromDay())
                    and (DayInSeason <= GetCutInfoRecord1_ToDay())):
                    HarvestNow = True
            elif GetManagement_Cuttings_Criterion() == TimeCuttings_DryY:
                if (((GetSumWaBal_YieldPart() - GetYprevSum()) >= GetCutInfoRecord1_MassInfo())
                    and (DayInSeason >= GetCutInfoRecord1_FromDay())
                    and (DayInSeason <= GetCutInfoRecord1_ToDay())):
                    HarvestNow = True
            elif GetManagement_Cuttings_Criterion() == TimeCuttings_FreshY:
                # OK if Crop.DryMatter = undef_int (not specified) HarvestNow
                # remains false
                if ((((GetSumWaBal_YieldPart() - GetYprevSum()) / (GetCrop_DryMatter() / 100.0)) >= GetCutInfoRecord1_MassInfo())
                    and (DayInSeason >= GetCutInfoRecord1_FromDay())
                    and (DayInSeason <= GetCutInfoRecord1_ToDay())):
                    HarvestNow = True

        if HarvestNow == True:
            SetNrCut(GetNrCut() + 1)
            SetDayLastCut(DayInSeason)
            if GetCCiPrev() > (GetManagement_Cuttings_CCcut() / 100.0):
                SetCCiPrev(GetManagement_Cuttings_CCcut() / 100.0)
                # ook nog CCwithered
                SetCrop_CCxWithered(0.0)  # or CCiPrev ??
                SetCCxWitheredTpotNoS(0.0)
                # for calculation Maximum Biomass unlimited soil fertility
                SetCrop_CCxAdjusted(GetCCiPrev())  # new
            # Record harvest
            if GetPart1Mult():
                RecordHarvest(GetNrCut(), DayInSeason)
            # Reset
            SetSumInterval(0)
            SetSumGDDcuts(0.0)
            SetBprevSum(GetSumWaBal_Biomass())
            SetYprevSum(GetSumWaBal_YieldPart())

    # 14. Write results
    # 14.a Summation
    SetSumETo(GetSumETo() + GetETo())
    SetSumGDD(GetSumGDD() + GetGDDayi())
    # 14.b Stress totals
    if GetCCiActual() > 0.0:
        # leaf expansion growth
        if GetStressLeaf() > -ac_zero_threshold:
            SetStressTot_Exp(
                ((GetStressTot_NrD() - 1.0) * GetStressTot_Exp() + GetStressLeaf())
                / float(GetStressTot_NrD())
            )
        # stomatal closure
        if GetTpot() > 0.0:
            StressStomata = 100.0 * (1.0 - GetTact() / GetTpot())
            if StressStomata > -ac_zero_threshold:
                SetStressTot_Sto(
                    ((GetStressTot_NrD() - 1.0) * GetStressTot_Sto() + StressStomata)
                    / float(GetStressTot_NrD())
                )
    # weed stress
    if GetWeedRCi() > -ac_zero_threshold:
        SetStressTot_Weed(
            ((GetStressTot_NrD() - 1.0) * GetStressTot_Weed() + GetWeedRCi())
            / float(GetStressTot_NrD())
        )
    # 14.c Assign crop parameters
    SetPlotVarCrop_ActVal(
        GetCCiActual() / GetCCxCropWeedsNoSFstress() * 100.0
    )
    SetPlotVarCrop_PotVal(
        100.0 * (1.0 / GetCCxCropWeedsNoSFstress()) *
        CanopyCoverNoStressSF(
            (VirtualTimeCC + GetSimulation_DelayedDays() + 1),
            GetCrop_DaysToGermination(),
            GetCrop_DaysToSenescence(),
            GetCrop_DaysToHarvest(),
            GetCrop_GDDaysToGermination(),
            GetCrop_GDDaysToSenescence(),
            GetCrop_GDDaysToHarvest(),
            (GetfWeedNoS() * GetCrop_CCo()),
            (GetfWeedNoS() * GetCrop_CCx()),
            GetCGCref(),
            (GetCrop_CDC() * (GetfWeedNoS() * GetCrop_CCx() + 2.29) /
             (GetCrop_CCx() + 2.29)),
            GetGDDCGCref(),
            (GetCrop_GDDCDC() * (GetfWeedNoS() * GetCrop_CCx() + 2.29) /
             (GetCrop_CCx() + 2.29)),
            SumGDDadjCC,
            GetCrop_ModeCycle(),
            0,
            0,
        )
    )
    if ((VirtualTimeCC + GetSimulation_DelayedDays() + 1) <= GetCrop_DaysToFullCanopySF()):
        # not yet canopy decline with soil fertility stress
        PotValSF = (
            100.0 * (1.0 / GetCCxCropWeedsNoSFstress()) *
            CanopyCoverNoStressSF(
                (VirtualTimeCC + GetSimulation_DelayedDays() + 1),
                GetCrop_DaysToGermination(),
                GetCrop_DaysToSenescence(),
                GetCrop_DaysToHarvest(),
                GetCrop_GDDaysToGermination(),
                GetCrop_GDDaysToSenescence(),
                GetCrop_GDDaysToHarvest(),
                GetCCoTotal(),
                GetCCxTotal(),
                GetCrop_CGC(),
                GetCDCTotal(),
                GetCrop_GDDCGC(),
                GetGDDCDCTotal(),
                SumGDDadjCC,
                GetCrop_ModeCycle(),
                GetSimulation_EffectStress_RedCGC(),
                GetSimulation_EffectStress_RedCCX(),
            )
        )
    else:
        PotValSF = GetPotValSF(
            (VirtualTimeCC + GetSimulation_DelayedDays() + 1),
            SumGDDadjCC,
            PotValSF,
        )
    # Adjust crop cycle and simulation period to delayed days after germination
    if ((GetSimulation_DelayedDays() > 0) and (GetSimulation_Germinate() == True)):
        ResetCropAndSimulationPeriod(GetDayNri())
        SetRepeatToDay(GetSimulation_ToDayNr())

    # 14.d Print ---------------------------------------
    if GetOutputAggregate() > 0:
        CheckForPrint(GetTheProjectFile())
    if GetOutDaily():
        WriteDailyResults((GetDayNri() - GetSimulation_DelayedDays() - GetCrop_Day1() + 1), WPi)
    if GetOut8Irri():
        WriteIrrInfo()
    if GetPart2Eval() and (GetObservationsFile() != '(None)'):
        WriteEvaluationData((GetDayNri() - GetSimulation_DelayedDays() - GetCrop_Day1() + 1))

    # 15. Prepare Next day
    # 15.a Date
    SetDayNri(GetDayNri() + 1)
    # 15.b Irrigation
    if GetDayNri() == GetCrop_Day1():
        SetIrriInterval(1)
    else:
        SetIrriInterval(GetIrriInterval() + 1)
    # 15.c Rooting depth
    # 15.bis extra line for standalone
    if GetOutDaily():
        DetermineGrowthStage(GetDayNri(), GetCCiPrev())
    # 15.extra - reset ageing of Kc at recovery after full senescence
    if GetSimulation_SumEToStress() >= 0.1:
        SetDayLastCut(GetDayNri())

    return WPi, HarvestNow


def WriteEvaluationData(DAP):
    CCfield = float(undef_int)
    CCstd = float(undef_int)
    Bfield = float(undef_int)
    Bstd = float(undef_int)
    SWCfield = float(undef_int)
    SWCstd = float(undef_int)
    Di = 0
    Mi = 0
    Yi = 0
    DayNrEval_temp = 0
    DAP_temp = DAP

    # 1. Prepare field data
    if (GetLineNrEval() != undef_int) and (GetDayNrEval() == GetDayNri()):
        # read field data
        fObs_rewind()
        last_line = ""
        for _ in range(1, GetLineNrEval() + 1):
            last_line = fObs_read()

        vals = last_line.split()
        Nr = int(vals[0])
        CCfield = float(vals[1])
        CCstd = float(vals[2])
        Bfield = float(vals[3])
        Bstd = float(vals[4])
        SWCfield = float(vals[5])
        SWCstd = float(vals[6])

        # get Day Nr for next field data
        next_line = fObs_read()
        if fObs_eof():
            SetLineNrEval(undef_int)
            fObs_close()
        else:
            SetLineNrEval(GetLineNrEval() + 1)
            DayNrEval_temp = int(next_line.split()[0])
            SetDayNrEval(DayNrEval_temp)
            SetDayNrEval(GetDayNr1Eval() + GetDayNrEval() - 1)

    # 2. Date
    Di, Mi, Yi = DetermineDate(GetDayNri())
    if GetClimRecord_FromY() == 1901:
        Yi = Yi - 1901 + 1
    if GetStageCode() == 0:
        DAP_temp = undef_int  # before or after cropping

    # 3. Write simulation results and field data
    SWCi = SWCZsoil(GetZeval())
    line = (
        f"{Di:6d}{Mi:6d}{Yi:6d}{DAP_temp:6d}{GetStageCode():5d}"
        f"{(GetCCiActual() * 100.0):8.1f}{CCfield:8.1f}{CCstd:8.1f}"
        f"{GetSumWaBal_Biomass():10.3f}{Bfield:10.3f}{Bstd:10.3f}"
        f"{SWCi:8.1f}{SWCfield:8.1f}{SWCstd:8.1f}"
    )
    fEval_write_bulk(line)

def SWCZsoil(Zsoil):
    compi = 0
    CumDepth = 0.0
    Factor = 0.0
    frac_value = 0.0
    SWCact = 0.0

    CumDepth = 0.0
    compi = 0
    SWCact = 0.0
    while True:
        compi = compi + 1
        CumDepth = CumDepth + GetCompartment_Thickness(compi)
        if CumDepth <= Zsoil:
            Factor = 1.0
        else:
            frac_value = Zsoil - (CumDepth - GetCompartment_Thickness(compi))
            if frac_value > 0.0:
                Factor = frac_value / GetCompartment_Thickness(compi)
            else:
                Factor = 0.0

        SWCact = SWCact + Factor * 10.0 * (GetCompartment_theta(compi) * 100.0) * GetCompartment_Thickness(compi)

        if (roundc(100.0 * CumDepth, mold=1) >= roundc(100.0 * Zsoil, mold=1)) or (compi == GetNrCompartments()):
            break

    return SWCact

def WriteIrrInfo():
    Di = 0
    Mi = 0
    Yi = 0
    DAPi = 0
    IrriON = False
    IRRmm = 0.0

    items = []

    Di, Mi, Yi = DetermineDate(GetDayNri())
    if GetClimRecord_FromY() == 1901:
        Yi = Yi - 1901 + 1

    if (GetDayNri() < GetCrop_Day1()) or (GetDayNri() > GetCrop_DayN()):
        tempstring = (
            f"{Di:6d}{Mi:6d}{Yi:6d}{undef_int:6d}{undef_int:6d}"
            f"{GetIrrigation():8.1f}{undef_int:6d}"
        )
        items.append(tempstring)
    else:
        if ((GetDayNri() == GetCrop_DayN())
            or ((GetIrrigation() > 0.0) and (GetIrriMode() != IrriMode_Inet))):
            if (GetIrrigation() <= 0.0001) and (GetDayNri() == GetCrop_DayN()):
                IrriON = False
            else:
                IrriON = True

            DAPi = GetDayNri() - GetCrop_Day1() + 1

            for i in range(GetLastIrriDAP() + 1, DAPi + 1):
                Di, Mi, Yi = DetermineDate(
                    (GetDayNri() - (DAPi - GetLastIrriDAP()) + (i - GetLastIrriDAP()))
                )
                if GetClimRecord_FromY() == 1901:
                    Yi = Yi - 1901 + 1

                if i == DAPi:
                    IRRmm = GetIrrigation()
                else:
                    IRRmm = 0.0

                if GetIrriMode() == IrriMode_Inet:
                    IRRmm = undef_int
                    IrriON = False

                if IrriON == True:
                    tempstring = (
                        f"{Di:6d}{Mi:6d}{Yi:6d}{i:6d}{undef_int:6d}"
                        f"{IRRmm:8.1f}{(DAPi - GetLastIrriDAP()):6d}"
                    )
                    items.append(tempstring)
                else:
                    tempstring = (
                        f"{Di:6d}{Mi:6d}{Yi:6d}{i:6d}{undef_int:6d}"
                        f"{IRRmm:8.1f}{undef_int:6d}"
                    )
                    items.append(tempstring)

            if IrriON == True:
                SetLastIrriDAP(DAPi)

    fIrrInfo_write_bulk(items)

def WriteDailyResults(DAP, WPi):
    NoValD = undef_double
    NoValI = undef_int
    Di = 0
    Mi = 0
    Yi = 0
    StrExp = 0
    StrSto = 0
    StrSalt = 0
    StrTr = 0
    StrW = 0
    Brel = 0
    Nr = 0
    DAP_loc = 0
    Ratio1 = 0
    Ratio2 = 0
    Ratio3 = 0
    KsTr = 0.0
    HI = 0.0
    KcVal = 0.0
    WPy = 0.0
    SaltVal = 0.0
    WPi_loc = 0.0
    tempreal = 0.0
    SWCtopSoilConsidered_temp = False

    DAP_loc = DAP
    WPi_loc = WPi

    Di, Mi, Yi = DetermineDate(GetDayNri())
    if GetClimRecord_FromY() == 1901:
        Yi = Yi - 1901 + 1
    if GetStageCode() == 0:
        DAP_loc = undef_int

    items = []

    # 0. info day
    tempstring = f"{Di:6d}{Mi:6d}{Yi:6d}{DAP_loc:6d}{GetStageCode():6d}"
    if GetTemperatureFile() != '(External)':
        items.append((tempstring, False))

    # 1. Water balance
    if GetOut1Wabal():
        if GetZiAqua() == undef_int:
            tempstring = (
                f"{GetTotalWaterContent_EndDay():10.1f}{GetRain():8.1f}{GetIrrigation():9.1f}"
                f"{GetSurfaceStorage():7.1f}{GetInfiltrated():7.1f}{GetRunoff():7.1f}"
                f"{GetDrain():9.1f}{GetCRwater():9.1f}{undef_double:8.2f}"
            )
        else:
            tempstring = (
                f"{GetTotalWaterContent_EndDay():10.1f}{GetRain():8.1f}{GetIrrigation():9.1f}"
                f"{GetSurfaceStorage():7.1f}{GetInfiltrated():7.1f}{GetRunoff():7.1f}"
                f"{GetDrain():9.1f}{GetCRwater():9.1f}{(GetZiAqua() / 100.0):8.2f}"
            )
        items.append((tempstring, False))

        if GetTpot() > 0.0:
            Ratio1 = roundc(100.0 * GetTact() / GetTpot(), mold=1)
        else:
            Ratio1 = 100

        if (GetEpot() + GetTpot()) > 0.0:
            Ratio2 = roundc(100.0 * (GetEact() + GetTact()) / (GetEpot() + GetTpot()), mold=1)
        else:
            Ratio2 = 100

        if GetEpot() > 0.0:
            Ratio3 = roundc(100.0 * GetEact() / GetEpot(), mold=1)
        else:
            Ratio3 = 100

        tempstring = (
            f"{GetEpot():9.1f}{GetEact():9.1f}{Ratio3:7d}"
            f"{GetTpot():9.1f}{GetTact():9.1f}{Ratio1:6d}"
            f"{(GetEpot() + GetTpot()):9.1f}{(GetEact() + GetTact()):8.1f}{Ratio2:8d}"
        )
        if (GetOut2Crop()) or (GetOut3Prof()) or (GetOut4Salt()) or (GetOut5CompWC()) or (GetOut6CompEC()) or (GetOut7Clim()):
            items.append((tempstring, False))
        else:
            items.append(tempstring)

    # 2. Crop development and yield
    if GetOut2Crop():
        if GetTpot() > 0.0:
            Ratio1 = roundc(100.0 * GetTact() / GetTpot(), mold=1)
        else:
            Ratio1 = 100

        if GetStressLeaf() < 0.0:
            StrExp = undef_int
        else:
            StrExp = roundc(GetStressLeaf(), mold=1)

        if GetTpot() < epsilon(0.0):
            StrSto = undef_int
        else:
            StrSto = roundc(100.0 * (1.0 - GetTact() / GetTpot()), mold=1)

        if GetRootZoneSalt_KsSalt() < 0.0:
            StrSalt = undef_int
        else:
            StrSalt = roundc(100.0 * (1.0 - GetRootZoneSalt_KsSalt()), mold=1)

        if GetCCiActual() <= ac_zero_threshold:
            KsTr = 1.0
        else:
            KsTr = KsTemperature(0.0, GetCrop_GDtranspLow(), GetGDDayi())

        if KsTr < 1.0:
            StrTr = roundc((1.0 - KsTr) * 100.0, mold=1)
        else:
            StrTr = 0

        if GetCCiActual() <= ac_zero_threshold:
            StrW = undef_int
        else:
            StrW = roundc(GetWeedRCi(), mold=1)

        if GetSumWaBal_Biomass() <= ac_zero_threshold:
            WPi_loc = 0.0

        if (GetSumWaBal_Biomass() > 0.0) and (GetSumWaBal_YieldPart() > 0.0):
            HI = 100.0 * (GetSumWaBal_YieldPart()) / (GetSumWaBal_Biomass())
        else:
            HI = undef_double

        if (GetSumWaBal_Biomass() > 0.0) and (GetSumWaBal_BiomassUnlim() > 0.0):
            Brel = roundc(100.0 * GetSumWaBal_Biomass() / GetSumWaBal_BiomassUnlim(), mold=1)
            if Brel > 100.0:
                Brel = 100
        else:
            Brel = undef_int

        if (GetETo() > 0.0) and (GetTpot() > 0.0) and (StrTr < 100):
            KcVal = GetTpot() / (GetETo() * KsTr)
        else:
            KcVal = undef_int

        if (((GetSumWaBal_Tact() > 0.0) or (GetSumWaBal_ECropCycle() > 0.0))
            and (GetSumWaBal_YieldPart() > 0.0)):
            WPy = (GetSumWaBal_YieldPart() * 1000.0) / ((GetSumWaBal_Tact() + GetSumWaBal_ECropCycle()) * 10.0)
        else:
            WPy = 0.0

        tempstring = (
            f"{GetGDDayi():9.1f}{GetRootingDepth():8.2f}"
            f"{StrExp:7d}{StrSto:7d}{roundc(GetStressSenescence(), mold=1):7d}{StrSalt:7d}{StrW:7d}"
            f"{(GetCCiActual() * 100.0):8.1f}{(GetCCiActualWeedInfested() * 100.0):8.1f}"
            f"{StrTr:7d}{KcVal:9.2f}{GetTpot():9.1f}{GetTact():9.1f}{GetTactWeedInfested():9.1f}"
            f"{Ratio1:6d}{(100.0 * WPi_loc):8.1f}{GetSumWaBal_Biomass():10.3f}"
            f"{HI:8.1f}{GetSumWaBal_YieldPart():9.3f}"
        )
        items.append((tempstring, False))

        if (GetCrop_DryMatter() == undef_int) or (GetCrop_DryMatter() < epsilon(0.0)):
            tempstring = f"{undef_double:9.3f}"
            items.append((tempstring, False))
        else:
            tempstring = f"{(GetSumWaBal_YieldPart() / (GetCrop_DryMatter() / 100.0)):9.3f}"
            items.append((tempstring, False))

        tempstring = f"{Brel:8d}{WPy:12.2f}{GetBin():9.3f}{GetBout():9.3f}"
        if (GetOut3Prof()) or (GetOut4Salt()) or (GetOut5CompWC()) or (GetOut6CompEC()) or (GetOut7Clim()):
            items.append((tempstring, False))
        else:
            items.append(tempstring)

    # 3. Profile/Root zone - Soil water content
    if GetOut3Prof():
        tempstring = f"{GetTotalWaterContent_EndDay():10.1f}"
        if GetTemperatureFile() != '(External)':
            items.append((tempstring, False))

        if GetRootingDepth() < epsilon(0.0):
            SetRootZoneWC_Actual(undef_double)
        else:
            if roundc(GetSoil_RootMax() * 1000.0, mold=1) == roundc(GetCrop_RootMax() * 1000.0, mold=1):
                SWCtopSoilConsidered_temp = GetSimulation_SWCtopSoilConsidered()
                SWCtopSoilConsidered_temp = DetermineRootZoneWC(GetCrop_RootMax(), SWCtopSoilConsidered_temp)
                SetSimulation_SWCtopSoilConsidered(SWCtopSoilConsidered_temp)
            else:
                SWCtopSoilConsidered_temp = GetSimulation_SWCtopSoilConsidered()
                SWCtopSoilConsidered_temp = DetermineRootZoneWC(float(GetSoil_RootMax()), SWCtopSoilConsidered_temp)
                SetSimulation_SWCtopSoilConsidered(SWCtopSoilConsidered_temp)

        tempstring = f"{GetRootZoneWC_Actual():9.1f}{GetRootingDepth():8.2f}"
        if GetTemperatureFile() != '(External)':
            items.append((tempstring, False))

        if GetRootingDepth() < epsilon(0.0):
            SetRootZoneWC_Actual(undef_double)
            SetRootZoneWC_FC(undef_double)
            SetRootZoneWC_WP(undef_double)
            SetRootZoneWC_SAT(undef_double)
            SetRootZoneWC_Thresh(undef_double)
            SetRootZoneWC_Leaf(undef_double)
            SetRootZoneWC_Sen(undef_double)
        else:
            SWCtopSoilConsidered_temp = GetSimulation_SWCtopSoilConsidered()
            SWCtopSoilConsidered_temp = DetermineRootZoneWC(GetRootingDepth(), SWCtopSoilConsidered_temp)
            SetSimulation_SWCtopSoilConsidered(SWCtopSoilConsidered_temp)

        tempstring = (
            f"{GetRootZoneWC_Actual():8.1f}{GetRootZoneWC_SAT():10.1f}{GetRootZoneWC_FC():10.1f}"
            f"{GetRootZoneWC_Leaf():10.1f}{GetRootZoneWC_Thresh():10.1f}{GetRootZoneWC_Sen():10.1f}"
        )
        if GetTemperatureFile() != '(External)':
            items.append((tempstring, False))

        tempstring = f"{GetRootZoneWC_WP():10.1f}"
        if (GetOut4Salt()) or (GetOut5CompWC()) or (GetOut6CompEC()) or (GetOut7Clim()):
            items.append((tempstring, False))
        else:
            if GetTemperatureFile() != '(External)':
                items.append(tempstring)

    # 4. Profile/Root zone - soil salinity
    if GetOut4Salt():
        tempstring = (
            f"{GetSaltInfiltr():9.3f}{(GetDrain() * GetECDrain() * Equiv / 100.0):10.3f}"
            f"{(GetCRsalt() / 100.0):10.3f}{GetTotalSaltContent_EndDay():10.3f}"
        )
        items.append((tempstring, False))

        if GetRootingDepth() < epsilon(0.0):
            SaltVal = undef_int
            SetRootZoneSalt_ECe(float(undef_int))
            SetRootZoneSalt_ECsw(float(undef_int))
            SetRootZoneSalt_KsSalt(1.0)
        else:
            SaltVal = (GetRootZoneWC_SAT() * GetRootZoneSalt_ECe() * Equiv) / 100.0

        if GetZiAqua() == undef_int:
            tempstring = (
                f"{SaltVal:10.3f}{GetRootingDepth():8.2f}{GetRootZoneSalt_ECe():9.2f}"
                f"{GetRootZoneSalt_ECsw():8.2f}{roundc(100.0 * (1.0 - GetRootZoneSalt_KsSalt()), mold=1):7d}"
                f"{undef_double:8.2f}"
            )
        else:
            tempstring = (
                f"{SaltVal:10.3f}{GetRootingDepth():8.2f}{GetRootZoneSalt_ECe():9.2f}"
                f"{GetRootZoneSalt_ECsw():8.2f}{roundc(100.0 * (1.0 - GetRootZoneSalt_KsSalt()), mold=1):7d}"
                f"{(GetZiAqua() / 100.0):8.2f}"
            )
        items.append((tempstring, False))

        tempstring = f"{GetECiAqua():8.2f}"
        if (GetOut5CompWC()) or (GetOut6CompEC()) or (GetOut7Clim()):
            items.append((tempstring, False))
        else:
            items.append(tempstring)

    # 5. Compartments - Soil water content
    if GetOut5CompWC():
        tempstring = f"{(GetCompartment_theta(1) * 100.0):11.1f}"
        items.append((tempstring, False))

        for Nr in range(2, GetNrCompartments()):
            tempstring = f"{(GetCompartment_theta(Nr) * 100.0):11.1f}"
            items.append((tempstring, False))

        tempstring = f"{(GetCompartment_theta(GetNrCompartments()) * 100.0):11.1f}"
        if (GetOut6CompEC()) or (GetOut7Clim()):
            items.append((tempstring, False))
        else:
            items.append(tempstring)

    # 6. Compartmens - Electrical conductivity of the saturated soil-paste extract
    if GetOut6CompEC():
        SaltVal = ECeComp(GetCompartment_i(1))
        tempstring = f"{SaltVal:11.1f}"
        items.append((tempstring, False))

        for Nr in range(2, GetNrCompartments()):
            SaltVal = ECeComp(GetCompartment_i(Nr))
            tempstring = f"{SaltVal:11.1f}"
            items.append((tempstring, False))

        SaltVal = ECeComp(GetCompartment_i(GetNrCompartments()))
        tempstring = f"{SaltVal:11.1f}"
        if GetOut7Clim():
            items.append((tempstring, False))
        else:
            items.append(tempstring)

    # 7. Climate input parameters
    if GetOut7Clim():
        tempreal = (GetTmin() + GetTmax()) / 2.0
        tempstring = (
            f"{GetRain():9.1f}{GetETo():10.1f}{GetTmin():10.1f}"
            f"{tempreal:10.1f}{GetTmax():10.1f}{GetCO2i():10.2f}"
        )
        items.append(tempstring)

    fDaily_write_bulk(items)

def ResetCropAndSimulationPeriod(NewCropDay1):
    ResettedCropDay1 = 0
    GDDAvailable = 0.0
    LseasonDays = 0
    Crop_DaysToSenescence_temp = 0
    Crop_DaysToHarvest_temp = 0
    Crop_GDDaysToSenescence_temp = 0
    Crop_GDDaysToHarvest_temp = 0
    FertStress = 0
    RedCGC_temp = 0
    RedCCX_temp = 0
    Crop_DaysToFullCanopySF_temp = 0
    TDayMin_temp = 0.0
    TDayMax_temp = 0.0

    # 1. Reset Day1 of Crop cycle
    SetCrop_Day1(NewCropDay1)

    # 2. Adjust crop calendar
    if GetCrop_subkind() == subkind_Forage:
        LseasonDays = GetCrop_DayN() - GetCrop_Day1() + 1
        Crop_DaysToSenescence_temp = GetCrop_DaysToSenescence()
        Crop_DaysToHarvest_temp = GetCrop_DaysToHarvest()
        Crop_GDDaysToSenescence_temp = GetCrop_GDDaysToSenescence()
        Crop_GDDaysToHarvest_temp = GetCrop_GDDaysToHarvest()
        Crop_DaysToSenescence_temp, Crop_DaysToHarvest_temp, Crop_GDDaysToSenescence_temp, Crop_GDDaysToHarvest_temp = AdjustCropFileParameters(
            GetCropFileSet(),
            LseasonDays, GetCrop_Day1(),
            GetCrop_ModeCycle(), GetCrop_Tbase(), GetCrop_Tupper(),
            Crop_DaysToSenescence_temp, Crop_DaysToHarvest_temp,
            Crop_GDDaysToSenescence_temp, Crop_GDDaysToHarvest_temp
        )
        SetCrop_DaysToSenescence(Crop_DaysToSenescence_temp)
        SetCrop_DaysToHarvest(Crop_DaysToHarvest_temp)
        SetCrop_GDDaysToSenescence(Crop_GDDaysToSenescence_temp)
        SetCrop_GDDaysToHarvest(Crop_GDDaysToHarvest_temp)
        CompleteCropDescription()
    else:
        # 2. Adjust crop calendar (in days) to thermal regime when running in GDDays
        if (GetCrop_ModeCycle() == ModeCycle_GDDays) and (GetClimateFile() != '(None)'):
            # GDDays 1.1 Check available GDDays
            ResettedCropDay1 = ResetCropDay1(NewCropDay1, False)
            TDayMin_temp = GetSimulParam_Tmin()
            TDayMax_temp = GetSimulParam_Tmax()
            GDDAvailable, ResettedCropDay1, TDayMin_temp, TDayMax_temp = MaxAvailableGDD(
                ResettedCropDay1, GetCrop_Tbase(), GetCrop_Tupper(), TDayMin_temp, TDayMax_temp
            )
            SetSimulParam_Tmin(TDayMin_temp)
            SetSimulParam_Tmax(TDayMax_temp)

            # GDDays 1.2. Adjust crop calendar to thermal regime if sufficient GDDays
            if GDDAvailable >= GetCrop_GDDaysToHarvest():
                AdjustCalendarCrop(GetCrop_Day1())

    # 3. Reset DayN of Crop
    SetCrop_DayN(GetCrop_Day1() + GetCrop_DaysToHarvest() - 1)

    # 4. Adjust end of Simulation period
    if GetCrop_DayN() > GetSimulation_ToDayNr():
        SetSimulation_ToDayNr(GetCrop_DayN())

        # adjusting ClimRecord.'TO' for undefined year with 365 days
        if ((GetClimFile() != '(None)') and (GetClimRecord_FromY() == 1901) and (GetClimRecord_NrObs() == 365)):
            AdjustClimRecordTo(GetCrop_DayN())

        SetNextSimFromDayNr(GetCrop_DayN() + 1)  # The Simulation.FromDayNr for next run if KeepSWC
    else:
        SetNextSimFromDayNr(undef_int)

    # 5. reset canopy development to soil fertility
    FertStress = GetManagement_FertilityStress()
    RedCGC_temp = GetSimulation_EffectStress_RedCGC()
    RedCCX_temp = GetSimulation_EffectStress_RedCCX()
    Crop_DaysToFullCanopySF_temp = GetCrop_DaysToFullCanopySF()
    Crop_DaysToFullCanopySF_temp, RedCGC_temp, RedCCX_temp, FertStress = TimeToMaxCanopySF(
        GetCrop_CCo(), GetCrop_CGC(), GetCrop_CCx(),
        GetCrop_DaysToGermination(), GetCrop_DaysToFullCanopy(),
        GetCrop_DaysToSenescence(), GetCrop_DaysToFlowering(),
        GetCrop_LengthFlowering(), GetCrop_DeterminancyLinked(),
        Crop_DaysToFullCanopySF_temp, RedCGC_temp, RedCCX_temp, FertStress
    )
    SetCrop_DaysToFullCanopySF(Crop_DaysToFullCanopySF_temp)
    SetManagement_FertilityStress(FertStress)
    SetSimulation_EffectStress_RedCGC(RedCGC_temp)
    SetSimulation_EffectStress_RedCCX(RedCCX_temp)

    # 6. Renew Tcrop.SIM (Temperature file covering crop cycle, used for display crop development in environment)
    if GetTemperatureFile() != '(None)':
        TemperatureFileCoveringCropPeriod(GetCrop_Day1(), GetCrop_DayN())

    # 7. Renew daily climate files (EToData.SIM; RainData.SIM and TempData.SIM) if required
    if GetNextSimFromDayNr() != undef_int:
        # If Simulation period was adjusted as well
        # rewrite ETo, Rain and Temperture file for the whole simulation period
        # Close files
        # CloseClimateFiles()

        # Create files
        CreateDailyClimFiles(GetSimulation_FromDayNr(), GetSimulation_ToDayNr())

        # Open files and Find current day
        OpenClimFilesAndGetDataFirstDay(GetCrop_Day1())

    # 8. reset delayed days
    SetSimulation_DelayedDays(0)
    # ResetCropAndSimulationPeriod



def GetPotValSF(DAP, SumGDDAdjCC, PotValSF):
    RatDGDD = 1.0

    if ((GetCrop_ModeCycle() == ModeCycle_GDDays)
        and (GetCrop_GDDaysToFullCanopySF() < GetCrop_GDDaysToSenescence())):
        RatDGDD = (GetCrop_DaysToSenescence() - GetCrop_DaysToFullCanopySF()) \
                    / (GetCrop_GDDaysToSenescence() - GetCrop_GDDaysToFullCanopySF())

    PotValSF = CCiNoWaterStressSF(
        DAP,
        GetCrop_DaysToGermination(),
        GetCrop_DaysToFullCanopySF(),
        GetCrop_DaysToSenescence(),
        GetCrop_DaysToHarvest(),
        GetCrop_GDDaysToGermination(),
        GetCrop_GDDaysToFullCanopySF(),
        GetCrop_GDDaysToSenescence(),
        GetCrop_GDDaysToHarvest(),
        GetCCoTotal(),
        GetCCxTotal(),
        GetCrop_CGC(),
        GetCrop_GDDCGC(),
        GetCDCTotal(),
        GetGDDCDCTotal(),
        SumGDDAdjCC,
        RatDGDD,
        GetSimulation_EffectStress_RedCGC(),
        GetSimulation_EffectStress_RedCCX(),
        GetSimulation_EffectStress_CDecline(),
        GetCrop_ModeCycle()
    )
    PotValSF = 100.0 * (1.0 / GetCCxCropWeedsNoSFstress()) * PotValSF

    return PotValSF

def GetIrriParam(TargetTimeVal, TargetDepthVal):
    DayInSeason = 0
    FromDay_temp = 0
    TimeInfo_temp = 0
    DepthInfo_temp = 0
    IrriECw_temp = 0.0
    TempString = ""

    TargetTimeVal = -999
    TargetDepthVal = -999
    if (GetDayNri() < GetCrop_Day1()) or \
       (GetDayNri() > GetCrop_DayN()):
        SetIrrigation(float(IrriOutSeason()))
    elif GetIrriMode() == IrriMode_Manual:
        SetIrrigation(float(IrriManual()))

    if (GetIrriMode() == IrriMode_Generate) and \
       ((GetDayNri() >= GetCrop_Day1()) and \
        (GetDayNri() <= GetCrop_DayN())):
        # read next line if required
        DayInSeason = GetDayNri() - GetCrop_Day1() + 1
        if DayInSeason > GetIrriInfoRecord1_ToDay():
            # read next line
            SetIrriInfoRecord1(GetIrriInfoRecord2())

            TempString = fIrri_read()
            if fIrri_eof():
                SetIrriInfoRecord1_ToDay(GetCrop_DayN() - GetCrop_Day1() + 1)
            else:
                SetIrriInfoRecord2_NoMoreInfo(False)
                if GetGlobalIrriECw():  # Versions before 3.2
                    parts = TempString.split()
                    FromDay_temp = int(parts[0])
                    TimeInfo_temp = int(parts[1])
                    DepthInfo_temp = int(parts[2])
                    SetIrriInfoRecord2_FromDay(FromDay_temp)
                    SetIrriInfoRecord2_TimeInfo(TimeInfo_temp)
                    SetIrriInfoRecord2_DepthInfo(DepthInfo_temp)
                else:
                    parts = TempString.split()
                    FromDay_temp = int(parts[0])
                    TimeInfo_temp = int(parts[1])
                    DepthInfo_temp = int(parts[2])
                    IrriECw_temp = float(parts[3])
                    SetIrriInfoRecord2_FromDay(FromDay_temp)
                    SetIrriInfoRecord2_TimeInfo(TimeInfo_temp)
                    SetIrriInfoRecord2_DepthInfo(DepthInfo_temp)
                    SetSimulation_IrriECw(IrriECw_temp)
                SetIrriInfoRecord1_ToDay(GetIrriInfoRecord2_FromDay() - 1)

        # get TargetValues
        TargetDepthVal = GetIrriInfoRecord1_DepthInfo()
        if GetGenerateTimeMode() == GenerateTimeMode_AllDepl:
            TargetTimeVal = GetIrriInfoRecord1_TimeInfo()
        elif GetGenerateTimeMode() == GenerateTimeMode_AllRAW:
            TargetTimeVal = GetIrriInfoRecord1_TimeInfo()
        elif GetGenerateTimeMode() == GenerateTimeMode_FixInt:
            TargetTimeVal = GetIrriInfoRecord1_TimeInfo()
            if TargetTimeVal > GetIrriInterval():  # do not yet irrigate
                TargetTimeVal = 0
            elif TargetTimeVal == GetIrriInterval():  # irrigate
                TargetTimeVal = 1
            else:
                # still to solve
                TargetTimeVal = 1  # temporary solution
            if (TargetTimeVal == 1) and \
               (GetGenerateDepthMode() == GenerateDepthMode_FixDepth):
                SetIrrigation(float(TargetDepthVal))
        elif GetGenerateTimeMode() == GenerateTimeMode_WaterBetweenBunds:
            TargetTimeVal = GetIrriInfoRecord1_TimeInfo()
            if (GetManagement_BundHeight() >= 0.01) and \
               (GetGenerateDepthMode() == GenerateDepthMode_FixDepth) and \
               (TargetTimeVal < (1000.0 * GetManagement_BundHeight())) and \
               (TargetTimeVal >= roundc(GetSurfaceStorage(), mold=1)):
                SetIrrigation(float(TargetDepthVal))
            else:
                SetIrrigation(0.0)
            TargetTimeVal = -999  # no need for check in SIMUL

    return TargetTimeVal, TargetDepthVal

def IrriOutSeason():
    DNr = 0
    Nri = 0
    i = 0
    IrriEvents = [rep_DayEventInt() for _ in range(5)]
    TheEnd = False

    DNr = GetDayNri() - GetSimulation_FromDayNr() + 1
    for i in range(1, 5 + 1):
        IrriEvents[i - 1] = GetIrriBeforeSeason_i(i)

    if GetDayNri() > GetCrop_DayN():
        DNr = GetDayNri() - GetCrop_DayN()
        for i in range(1, 5 + 1):
            IrriEvents[i - 1] = GetIrriAfterSeason_i(i)

    if DNr < 1:
        IrriOutSeason = 0
    else:
        TheEnd = False
        Nri = 0
        while True:
            Nri = Nri + 1
            if IrriEvents[Nri - 1].DayNr == DNr:
                IrriOutSeason = IrriEvents[Nri - 1].param
                TheEnd = True
            else:
                IrriOutSeason = 0

            if ((Nri == 5) or (IrriEvents[Nri - 1].DayNr == 0)
                or (IrriEvents[Nri - 1].DayNr > DNr)
                or TheEnd):
                break

    return IrriOutSeason

def IrriManual():
    DNr = 0
    StringREAD = ""
    Ir1 = 0.0
    Ir2 = 0.0
    IrriECw_temp = 0.0

    if GetIrriFirstDayNr() == undef_int:
        DNr = GetDayNri() - GetCrop_Day1() + 1
    else:
        DNr = GetDayNri() - GetIrriFirstDayNr() + 1

    if GetIrriInfoRecord1_NoMoreInfo():
        IrriManual = 0
    else:
        IrriManual = 0
        if GetIrriInfoRecord1_TimeInfo() == DNr:
            IrriManual = GetIrriInfoRecord1_DepthInfo()
            StringREAD = fIrri_read()
            if fIrri_eof():
                SetIrriInfoRecord1_NoMoreInfo(True)
            else:
                SetIrriInfoRecord1_NoMoreInfo(False)
                if GetGlobalIrriECw():  # Versions before 3.2
                    Ir1, Ir2 = SplitStringInTwoParams(StringREAD, Ir1, Ir2)
                else:
                    IrriECw_temp = GetSimulation_IrriECw()
                    Ir1, Ir2, IrriECw_temp = SplitStringInThreeParams(StringREAD)
                    SetSimulation_IrriECw(IrriECw_temp)
                SetIrriInfoRecord1_TimeInfo(roundc(Ir1, mold=1))
                SetIrriInfoRecord1_DepthInfo(roundc(Ir2, mold=1))

    return IrriManual

def AdjustSWCRootZone(PreIrri):
    compi = 0
    SumDepth = 0.0
    PreIrri = 0.0
    while True:
        compi = compi + 1
        SumDepth = SumDepth + GetCompartment_Thickness(compi)
        layeri = GetCompartment_Layer(compi)
        ThetaPercRAW = (
            GetSoilLayer_FC(layeri) / 100.0
            - GetSimulParam_PercRAW() / 100.0
            * GetCrop_pdef()
            * (GetSoilLayer_FC(layeri) / 100.0 - GetSoilLayer_WP(layeri) / 100.0)
        )
        if GetCompartment_theta(compi) < ThetaPercRAW:
            PreIrri = (
                PreIrri
                + (ThetaPercRAW - GetCompartment_theta(compi))
                * 1000.0
                * GetCompartment_Thickness(compi)
            )
            SetCompartment_theta(compi, ThetaPercRAW)
        if (SumDepth >= GetRootingDepth()) or (compi == GetNrCompartments()):
            break
    return PreIrri

def InitializeTransferAssimilates(Bin, Bout, AssimToMobilize,
                                 AssimMobilized, FracAssim,
                                 StorageON, MobilizationON,
                                 HarvestNow):
    Bin = 0.0
    Bout = 0.0
    FracAssim = 0.0
    if GetCrop_subkind() == subkind_Forage:
        # only for perennial herbaceous forage crops
        FracAssim = 0.0
        if GetNoMoreCrop():
            StorageON = False
            MobilizationON = False
        else:
            # Start of storage period ?
            if ((GetDayNri() - GetSimulation_DelayedDays() - GetCrop_Day1() + 1)
                == (GetCrop_DaysToHarvest() - GetCrop_Assimilates_Period() + 1)):
                # switch storage on
                StorageON = True
                # switch mobilization off
                if MobilizationON:
                    AssimToMobilize = AssimMobilized
                MobilizationON = False
            # Fraction of assimilates transferred
            if MobilizationON:
                tmob = (AssimToMobilize - AssimMobilized) / AssimToMobilize
                if AssimToMobilize > AssimMobilized:
                    FracAssim = (math.exp(-5.0 * tmob) - 1.0) / (math.exp(-5.0) - 1.0)
                    if GetCCiActual() > (0.9 * (GetCCxTotal()
                        * (1.0 - float(GetSimulation_EffectStress_RedCCX()) / 100.0))):
                        FracAssim = FracAssim * ((GetCCxTotal() * (1.0
                        - float(GetSimulation_EffectStress_RedCCX()) / 100.0))
                        - GetCCiActual()) \
                        / (0.1 * (GetCCxTotal() * (1.0
                        - float(GetSimulation_EffectStress_RedCCX()) / 100.0)))
                    if FracAssim < epsilon(0.0):
                        FracAssim = 0.0
                else:
                    # everything is mobilized
                    FracAssim = 0.0

            if (StorageON) and (GetCrop_Assimilates_Period() > 0):
                if HarvestNow:
                    FracSto = 0.0
                else:
                    if ((GetCCiActual() > GetManagement_Cuttings_CCcut() / 100.0)
                        and (GetCCiActual() < (GetCCxTotal() * (1.0
                        - float(GetSimulation_EffectStress_RedCCX()) / 100.0)))):
                        FracSto = (GetCCiActual() - GetManagement_Cuttings_CCcut() / 100.0) \
                            / ((GetCCxTotal() * (1.0 - float(GetSimulation_EffectStress_RedCCX()) / 100.0))
                            - GetManagement_Cuttings_CCcut() / 100.0)
                    else:
                        FracSto = 1.0
                # Use convex function
                FracAssim = FracSto * (GetCrop_Assimilates_Stored() / 100.0) \
                    * (1.0 - KsAny((((GetDayNri() - GetSimulation_DelayedDays()
                    - GetCrop_Day1() + 1.0)
                    - (GetCrop_DaysToHarvest() - GetCrop_Assimilates_Period()))
                    / float(GetCrop_Assimilates_Period())), 0.0, 1.0, -5.0))
            if FracAssim < 0.0:
                FracAssim = 0.0
            if FracAssim > 1.0:
                FracAssim = 1.0

    return Bin, Bout, AssimToMobilize, AssimMobilized, FracAssim, StorageON, MobilizationON


def WriteTheResults(ANumber, Day1, Month1, Year1, DayN, MonthN,
                    YearN, RPer, EToPer, GDDPer, IrriPer, InfiltPer,
                    ROPer, DrainPer, CRwPer, EPer, ExPer, TrPer, TrWPer,
                    TrxPer, SalInPer, SalOutPer,
                    SalCRPer, BiomassPer, BUnlimPer, BmobPer, BstoPer,
                    TheProjectFile):

    BrSF = 0
    RatioE = 0
    RatioT = 0
    Year1_loc = Year1
    YearN_loc = YearN
    WPy = 0.0
    HI = 0.0
    tempreal = 0.0

    if GetNoYear():
        Year1_loc = 9999
        YearN_loc = 9999

    items = []

    if ANumber == int(undef_int):
        if GetOutputAggregate() == 1:
            tempstring = f"{'Day':>9}{Day1:9d}{Month1:9d}{Year1_loc:9d}"
        elif GetOutputAggregate() == 2:
            tempstring = f"{'10Day':>9}{Day1:9d}{Month1:9d}{Year1_loc:9d}"
        elif GetOutputAggregate() == 3:
            tempstring = f"{'Month':>9}{Day1:9d}{Month1:9d}{Year1_loc:9d}"
        else:
            tempstring = f"{'':>9}{Day1:9d}{Month1:9d}{Year1_loc:9d}"
        items.append((tempstring, False))
    else:
        tempstring = f"Tot({ANumber})"
        tempstring = tempstring.rjust(9)
        items.append((tempstring, False))
        tempstring = f"{Day1:9d}{Month1:9d}{Year1_loc:9d}"
        items.append((tempstring, False))

    tempreal = roundc(GDDPer * 10.0, mold=1)

    tempstring = f"{RPer:9.1f}{EToPer:9.1f}{(tempreal / 10.0):9.1f}{GetCO2i():9.2f}"
    items.append((tempstring, False))

    if ExPer > 0.0:
        RatioE = roundc(100.0 * EPer / ExPer, mold=1)
    else:
        RatioE = undef_int

    if TrxPer > 0.0:
        RatioT = roundc(100.0 * TrPer / TrxPer, mold=1)
    else:
        RatioT = undef_int

    tempstring = (
        f"{IrriPer:9.1f}{InfiltPer:9.1f}{ROPer:9.1f}"
        f"{DrainPer:9.1f}{CRwPer:9.1f}{EPer:9.1f}"
        f"{RatioE:9d}{TrPer:9.1f}{TrWPer:9.1f}{RatioT:9d}"
    )
    items.append((tempstring, False))

    tempstring = (
        f"{SalInPer:10.3f}{SalOutPer:10.3f}"
        f"{SalCRPer:10.3f}{GetTotalSaltContent_EndDay():10.3f}"
    )
    items.append((tempstring, False))

    tempstring = (
        f"{GetStressTot_NrD():9d}"
        f"{roundc(GetStressTot_Salt(), mold=1):9d}"
        f"{GetManagement_FertilityStress():9d}"
        f"{roundc(GetStressTot_Weed(), mold=1):9d}"
        f"{roundc(GetStressTot_Temp(), mold=1):9d}"
        f"{roundc(GetStressTot_Exp(), mold=1):9d}"
        f"{roundc(GetStressTot_Sto(), mold=1):9d}"
    )
    items.append((tempstring, False))

    if (BiomassPer > 0.0) and (BUnlimPer > 0.0):
        BrSF = roundc(100.0 * BiomassPer / BUnlimPer, mold=1)
        if BrSF > 100:
            BrSF = 100
    else:
        BrSF = undef_int

    tempstring = f"{BiomassPer:10.3f}{BrSF:9d}"
    items.append((tempstring, False))

    if (GetSumWaBal_Biomass() > epsilon(0.0)) and (GetSumWaBal_YieldPart() > epsilon(0.0)):
        HI = 100.0 * GetSumWaBal_YieldPart() / GetSumWaBal_Biomass()
    else:
        if GetSumWaBal_Biomass() > epsilon(0.0):
            HI = 0.0
        else:
            HI = undef_double

    if ANumber != int(undef_int):
        if (((GetSumWaBal_Tact() > 0.0) or (GetSumWaBal_ECropCycle() > 0.0))
                and (GetSumWaBal_YieldPart() > 0.0)):
            WPy = (GetSumWaBal_YieldPart() * 1000.0) / (
                (GetSumWaBal_Tact() + GetSumWaBal_ECropCycle()) * 10.0
            )
        else:
            WPy = 0.0

        if ((GetCrop_DryMatter() == int(undef_int))
                or (GetCrop_DryMatter() < epsilon(0.0))):
            tempstring = (
                f"{HI:9.1f}{GetSumWaBal_YieldPart():9.3f}"
                f"{undef_double:9.3f}{WPy:9.2f}"
            )
        else:
            tempstring = (
                f"{HI:9.1f}{GetSumWaBal_YieldPart():9.3f}"
                f"{(GetSumWaBal_YieldPart() / (GetCrop_DryMatter() / 100.0)):9.3f}"
                f"{WPy:9.2f}"
            )
        items.append((tempstring, False))

        tempstring = f"{GetTransfer_Bmobilized():9.3f}{GetSimulation_Storage_Btotal():9.3f}"
        items.append((tempstring, False))
    else:
        tempstring = (
            f"{HI:9.1f}{undef_int:9d}{undef_int:9d}"
            f"{undef_int:9d}{undef_int:9d}"
            f"{BmobPer:9.3f}{BstoPer:9.3f}"
        )
        items.append((tempstring, False))

    tempstring = f"{DayN:9d}{MonthN:9d}{YearN_loc:9d}"
    items.append((tempstring, False))

    items.append("  " + TheProjectFile)

    fRun_write_bulk(items)


def CheckForPrint(TheProjectFile):
    DayN = 0
    MonthN = 0
    YearN = 0
    DayEndM = 0
    SaltIn = 0.0
    SaltOut = 0.0
    CRsalt = 0.0
    BiomassDay = 0.0
    BUnlimDay = 0.0
    WriteNow = False

    DayN, MonthN, YearN = DetermineDate(GetDayNri())

    if GetOutputAggregate() == 1:
        # 1: daily output
        BiomassDay = GetSumWaBal_Biomass() - GetPreviousSum_Biomass()
        BUnlimDay = GetSumWaBal_BiomassUnlim() - GetPreviousSum_BiomassUnlim()
        SaltIn = GetSumWaBal_SaltIn() - GetPreviousSum_SaltIn()
        SaltOut = GetSumWaBal_SaltOut() - GetPreviousSum_SaltOut()
        CRsalt = GetSumWaBal_CRSalt() - GetPreviousSum_CRSalt()
        WriteTheResults(
            int(undef_int),
            DayN, MonthN, YearN, DayN, MonthN,
            YearN, GetRain(), GetETo(), GetGDDayi(), GetIrrigation(),
            GetInfiltrated(), GetRunoff(), GetDrain(),
            GetCRwater(), GetEact(), GetEpot(), GetTact(),
            GetTactWeedInfested(), GetTpot(), SaltIn, SaltOut,
            CRsalt, BiomassDay, BUnlimDay, GetBin(), GetBout(),
            TheProjectFile
        )
        SetPreviousSum_Biomass(GetSumWaBal_Biomass())
        SetPreviousSum_BiomassUnlim(GetSumWaBal_BiomassUnlim())
        SetPreviousSum_SaltIn(GetSumWaBal_SaltIn())
        SetPreviousSum_SaltOut(GetSumWaBal_SaltOut())
        SetPreviousSum_CRSalt(GetSumWaBal_CRSalt())

    elif (GetOutputAggregate() == 2) or (GetOutputAggregate() == 3):
        # 2 or 3: 10-day or monthly output
        WriteNow = False
        DayEndM = DaysInMonth(MonthN)
        if LeapYear(YearN) and (MonthN == 2):
            DayEndM = 29
        if DayN == DayEndM:
            WriteNow = True  # 10-day and month
        if (GetOutputAggregate() == 2) and ((DayN == 10) or (DayN == 20)):
            WriteNow = True  # 10-day
        if WriteNow:
            WriteIntermediatePeriod(TheProjectFile)

def WriteIntermediatePeriod(TheProjectFile):
    Day1 = 0
    Month1 = 0
    Year1 = 0
    DayN = 0
    MonthN = 0
    YearN = 0
    RPer = 0.0
    EToPer = 0.0
    GDDPer = 0.0
    IrriPer = 0.0
    InfiltPer = 0.0
    EPer = 0.0
    ExPer = 0.0
    TrPer = 0.0
    TrWPer = 0.0
    TrxPer = 0.0
    DrainPer = 0.0
    BiomassPer = 0.0
    BUnlimPer = 0.0
    ROPer = 0.0
    CRwPer = 0.0
    SalInPer = 0.0
    SalOutPer = 0.0
    SalCRPer = 0.0
    BmobPer = 0.0
    BstoPer = 0.0

    # determine intermediate results
    Day1, Month1, Year1 = DetermineDate((GetPreviousDayNr() + 1))
    DayN, MonthN, YearN = DetermineDate(GetDayNri())
    RPer = GetSumWaBal_Rain() - GetPreviousSum_Rain()
    EToPer = GetSumETo() - GetPreviousSumETo()
    GDDPer = GetSumGDD() - GetPreviousSumGDD()
    IrriPer = GetSumWaBal_Irrigation() - GetPreviousSum_Irrigation()
    InfiltPer = GetSumWaBal_Infiltrated() - GetPreviousSum_Infiltrated()
    EPer = GetSumWaBal_Eact() - GetPreviousSum_Eact()
    ExPer = GetSumWaBal_Epot() - GetPreviousSum_Epot()
    TrPer = GetSumWaBal_Tact() - GetPreviousSum_Tact()
    TrWPer = GetSumWaBal_TrW() - GetPreviousSum_TrW()
    TrxPer = GetSumWaBal_Tpot() - GetPreviousSum_Tpot()
    DrainPer = GetSumWaBal_Drain() - GetPreviousSum_Drain()
    BiomassPer = GetSumWaBal_Biomass() - GetPreviousSum_Biomass()
    BUnlimPer = GetSumWaBal_BiomassUnlim() - GetPreviousSum_BiomassUnlim()

    ROPer = GetSumWaBal_Runoff() - GetPreviousSum_Runoff()
    CRwPer = GetSumWaBal_CRwater() - GetPreviousSum_CRwater()
    SalInPer = GetSumWaBal_SaltIn() - GetPreviousSum_SaltIn()
    SalOutPer = GetSumWaBal_SaltOut() - GetPreviousSum_SaltOut()
    SalCRPer = GetSumWaBal_CRSalt() - GetPreviousSum_CRSalt()

    BmobPer = GetTransfer_Bmobilized() - GetPreviousBmob()
    BstoPer = GetSimulation_Storage_Btotal() - GetPreviousBsto()

    # write
    WriteTheResults(
        int(undef_int),
        Day1, Month1, Year1, DayN,
        MonthN, YearN, RPer, EToPer, GDDPer, IrriPer, InfiltPer,
        ROPer, DrainPer, CRwPer, EPer, ExPer, TrPer, TrWPer,
        TrxPer, SalInPer, SalOutPer, SalCRPer, BiomassPer,
        BUnlimPer, BmobPer, BstoPer, TheProjectFile
    )

    # reset previous sums
    SetPreviousDayNr(GetDayNri())
    SetPreviousSum_Rain(GetSumWaBal_Rain())
    SetPreviousSumETo(GetSumETo())
    SetPreviousSumGDD(GetSumGDD())
    SetPreviousSum_Irrigation(GetSumWaBal_Irrigation())
    SetPreviousSum_Infiltrated(GetSumWaBal_Infiltrated())
    SetPreviousSum_Eact(GetSumWaBal_Eact())
    SetPreviousSum_Epot(GetSumWaBal_Epot())
    SetPreviousSum_Tact(GetSumWaBal_Tact())
    SetPreviousSum_TrW(GetSumWaBal_TrW())
    SetPreviousSum_Tpot(GetSumWaBal_Tpot())
    SetPreviousSum_Drain(GetSumWaBal_Drain())
    SetPreviousSum_Biomass(GetSumWaBal_Biomass())
    SetPreviousSum_BiomassPot(GetSumWaBal_BiomassPot())
    SetPreviousSum_BiomassUnlim(GetSumWaBal_BiomassUnlim())

    SetPreviousSum_Runoff(GetSumWaBal_Runoff())
    SetPreviousSum_CRwater(GetSumWaBal_CRwater())
    SetPreviousSum_SaltIn(GetSumWaBal_SaltIn())
    SetPreviousSum_SaltOut(GetSumWaBal_SaltOut())
    SetPreviousSum_CRSalt(GetSumWaBal_CRSalt())

    SetPreviousBmob(GetTransfer_Bmobilized())
    SetPreviousBsto(GetSimulation_Storage_Btotal())


def RecordHarvest(NrCut, DayInSeason):
    Dayi = 0
    Monthi = 0
    Yeari = 0
    NoYear = False

    fHarvest_open(GetfHarvest_filename(), 'a')

    Dayi, Monthi, Yeari = DetermineDate(GetCrop_Day1())
    NoYear = (Yeari == 1901)

    Dayi, Monthi, Yeari = DetermineDate(GetDayNri())
    if NoYear:
        Yeari = 9999

    items = []

    if NrCut == 9999:
        # last line at end of season
        items.append((
            f"{NrCut:6d}{Dayi:6d}{Monthi:6d}{Yeari:6d}"
            f"{GetSumWaBal_Biomass():34.3f}",
            False
        ))

        if GetCrop_DryMatter() == undef_int:
            items.append(f"{GetSumWaBal_YieldPart():20.3f}")
        else:
            items.append(
                f"{GetSumWaBal_YieldPart():20.3f}"
                f"{(GetSumWaBal_YieldPart() / (GetCrop_DryMatter() / 100.0)):20.3f}"
            )
    else:
        items.append((
            f"{NrCut:6d}{Dayi:6d}{Monthi:6d}{Yeari:6d}"
            f"{DayInSeason:6d}{GetSumInterval():6d}"
            f"{(GetSumWaBal_Biomass() - GetBprevSum()):12.3f}"
            f"{GetSumWaBal_Biomass():10.3f}"
            f"{(GetSumWaBal_YieldPart() - GetYprevSum()):10.3f}",
            False
        ))

        if GetCrop_DryMatter() == undef_int:
            items.append(f"{GetSumWaBal_YieldPart():10.3f}")
        else:
            items.append(
                f"{GetSumWaBal_YieldPart():10.3f}"
                f"{((GetSumWaBal_YieldPart() - GetYprevSum()) / (GetCrop_DryMatter() / 100.0)):10.3f}"
                f"{(GetSumWaBal_YieldPart() / (GetCrop_DryMatter() / 100.0)):10.3f}"
            )

    fHarvest_write_bulk(items)

def fObs_open(FileNameFull, mode):
    global fObs_lines, fObs_pos, fObs_iostat

    full_path = ResolvePath(FileNameFull)
    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        fObs_lines = f0.read().splitlines()

    fObs_pos = 0
    fObs_iostat = 0


def fObs_read():
    global fObs_lines, fObs_pos, fObs_iostat

    if fObs_pos < len(fObs_lines):
        line = fObs_lines[fObs_pos].strip()
        fObs_pos = fObs_pos + 1
        fObs_iostat = 0
    else:
        line = ""
        fObs_iostat = -1

    return line


def fObs_eof():
    return fObs_iostat != 0


def fObs_close():
    global fObs_lines, fObs_pos, fObs_iostat

    fObs_lines = []
    fObs_pos = 0
    fObs_iostat = 0

def fObs_rewind():
    global fObs_pos, fObs_iostat

    fObs_pos = 0
    fObs_iostat = 0

def fCuts_open(FileNameFull, mode):
    global fCuts_lines, fCuts_pos, fCuts_iostat

    full_path = ResolvePath(FileNameFull)
    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        fCuts_lines = f0.read().splitlines()

    fCuts_pos = 0
    fCuts_iostat = 0


def fCuts_read():
    global fCuts_lines, fCuts_pos, fCuts_iostat

    if fCuts_pos < len(fCuts_lines):
        line = fCuts_lines[fCuts_pos].strip()
        fCuts_pos = fCuts_pos + 1
        fCuts_iostat = 0
    else:
        line = ""
        fCuts_iostat = -1

    return line

def fCuts_eof():
    return fCuts_iostat != 0

def fIrri_open(FileNameFull, mode):
    global fIrri_lines, fIrri_pos, fIrri_iostat

    full_path = ResolvePath(FileNameFull)
    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        fIrri_lines = f0.read().splitlines()

    fIrri_pos = 0
    fIrri_iostat = 0


def fIrri_read():
    global fIrri_lines, fIrri_pos, fIrri_iostat

    if fIrri_pos < len(fIrri_lines):
        line = fIrri_lines[fIrri_pos].strip()
        fIrri_pos = fIrri_pos + 1
        fIrri_iostat = 0
    else:
        line = ""
        fIrri_iostat = -1

    return line


def fIrri_eof():
    return fIrri_iostat != 0

def fEToSIM_open(FileNameFull, mode):
    global fEToSIM_lines, fEToSIM_pos, fEToSIM_iostat

    full_path = ResolvePath(FileNameFull)

    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
            fEToSIM_lines = f0.read().splitlines()
        fEToSIM_pos = 0
        fEToSIM_iostat = 0
    except OSError:
        fEToSIM_lines = []
        fEToSIM_pos = 0
        fEToSIM_iostat = -1


def fEToSIM_read():
    global fEToSIM_lines, fEToSIM_pos, fEToSIM_iostat

    if fEToSIM_pos < len(fEToSIM_lines):
        line = fEToSIM_lines[fEToSIM_pos]
        fEToSIM_pos = fEToSIM_pos + 1
        fEToSIM_iostat = 0
    else:
        line = ""
        fEToSIM_iostat = -1

    return line

def fTempSIM_open(FileNameFull, mode):
    global fTempSIM_lines, fTempSIM_pos, fTempSIM_iostat

    full_path = ResolvePath(FileNameFull)

    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
            fTempSIM_lines = f0.read().splitlines()
        fTempSIM_pos = 0
        fTempSIM_iostat = 0
    except OSError:
        fTempSIM_lines = []
        fTempSIM_pos = 0
        fTempSIM_iostat = -1

def fTempSIM_read():
    global fTempSIM_lines, fTempSIM_pos, fTempSIM_iostat

    if fTempSIM_pos < len(fTempSIM_lines):
        line = fTempSIM_lines[fTempSIM_pos]
        fTempSIM_pos = fTempSIM_pos + 1
        fTempSIM_iostat = 0
    else:
        line = ""
        fTempSIM_iostat = -1

    return line


def fRainSIM_open(FileNameFull, mode):
    global fRainSIM_lines, fRainSIM_pos, fRainSIM_iostat

    full_path = ResolvePath(FileNameFull)

    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
            fRainSIM_lines = f0.read().splitlines()
        fRainSIM_pos = 0
        fRainSIM_iostat = 0
    except OSError:
        fRainSIM_lines = []
        fRainSIM_pos = 0
        fRainSIM_iostat = -1


def fRainSIM_read():
    global fRainSIM_lines, fRainSIM_pos, fRainSIM_iostat

    if fRainSIM_pos < len(fRainSIM_lines):
        line = fRainSIM_lines[fRainSIM_pos]
        fRainSIM_pos = fRainSIM_pos + 1
        fRainSIM_iostat = 0
    else:
        line = ""
        fRainSIM_iostat = -1

    return line
