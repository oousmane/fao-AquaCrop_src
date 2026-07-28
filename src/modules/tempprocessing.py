from ._global import *
from . import project_input as PI
from ._global import _strip_quotes
import math

TemperatureFilefull_exists = False

TminDataSet = [rep_DayEventDbl(0, 0.0) for _ in range(31)]
TmaxDataSet = [rep_DayEventDbl(0, 0.0) for _ in range(31)]

def GetTminDataSet():
    # Getter for the "TminDataSet" global variable.
    return TminDataSet

def SetTminDataSet(TminDataSet_in):
    # Getter for the "TminDataSet" global variable.
    global TminDataSet
    TminDataSet = TminDataSet_in

def GetTminDataSet_i(i):
    # Getter for the "TminDataSet" global variable.
    i0 = i - 1
    return TminDataSet[i0]

def SetTminDataSet_i(i, TheTminDataSet_i):
    # Setter for the "TminDataSet" global variable.
    global TminDataSet
    i0 = i - 1
    TminDataSet[i0] = TheTminDataSet_i

def GetTminDataSet_DayNr(i):
    # Getter for the "TminDataSet" global variable.
    i0 = i - 1
    return TminDataSet[i0].DayNr

def GetTminDataSet_Param(i):
    # Getter for the "TminDataSet" global variable.
    i0 = i - 1
    return TminDataSet[i0].Param

def SetTminDataSet_DayNr(i, TheDayNr):
    # Setter for the "TminDataSet" global variable.
    global TminDataSet
    i0 = i - 1
    TminDataSet[i0].DayNr = TheDayNr

def SetTminDataSet_Param(i, TheParam):
    # Setter for the "TminDataSet" global variable.
    global TminDataSet
    i0 = i - 1
    TminDataSet[i0].Param = TheParam

def GetTmaxDataSet():
    # Getter for the "TmaxDataSet" global variable.
    return TmaxDataSet

def SetTmaxDataSet(TheTmaxDataSet):
    # Setter for the "TmaxDataSet" global variable.
    global TmaxDataSet
    TmaxDataSet = TheTmaxDataSet

def GetTmaxDataSet_i(i):
    # Getter for the "TmaxDataSet" global variable.
    i0 = i - 1
    return TmaxDataSet[i0]

def SetTmaxDataSet_i(i, TheTmaxDataSet_i):
    # Setter for the "TmaxDataSet" global variable.
    global TmaxDataSet
    i0 = i - 1
    TmaxDataSet[i0] = TheTmaxDataSet_i

def GetTmaxDataSet_DayNr(i):
    # Getter for the "TmaxDataSet" global variable.
    i0 = i - 1
    return TmaxDataSet[i0].DayNr

def SetTmaxDataSet_DayNr(i, TheDayNr):
    # Setter for the "TmaxDataSet" global variable.
    global TmaxDataSet
    i0 = i - 1
    TmaxDataSet[i0].DayNr = TheDayNr

def GetTmaxDataSet_Param(i):
    # Getter for the "TmaxDataSet" global variable.
    i0 = i - 1
    return TmaxDataSet[i0].Param

def SetTmaxDataSet_Param(i, TheParam):
    # Setter for the "TmaxDataSet" global variable.
    global TmaxDataSet
    i0 = i - 1
    TmaxDataSet[i0].Param = TheParam

def LoadSimulationRunProject(NrRun: int):

    global TemperatureFilefull_exists

    if PI.ProjectInput is None:
        print("DBG PI.ProjectInput is None")
        raise SystemExit

    p = PI.ProjectInput

    # 0. Year of cultivation and Simulation and Cropping period
    SetSimulation_YearSeason(p[NrRun - 1].Simulation_YearSeason)
    SetSimulation_FromDayNr(p[NrRun - 1].Simulation_DayNr1)
    SetSimulation_ToDayNr(p[NrRun - 1].Simulation_DayNrN)
    SetCrop_Day1(p[NrRun - 1].Crop_Day1)
    # Last day of cropping period (maturity or premature end when too cold to reach maturity
    SetCrop_LastDayNr(p[NrRun - 1].Crop_LastDayNr)
    
    # 1. Climate
    SetClimateFile(PI.ProjectInput[NrRun - 1].Climate_Filename)

    if (GetClimateFile() == "(None)") or (GetClimateFile() == "(External)"):
        SetClimateFileFull(GetClimateFile())
    else:
        SetClimateFileFull(PI.ProjectInput[NrRun - 1].Climate_Directory + GetClimateFile())

        rc = 0
        try:
            full_path = ResolvePath(GetClimateFileFull())
            with open(full_path, "r", encoding="utf-8") as fClim:
                # 1.0 Description
                TempString = fClim.readline()
                SetClimateDescription(TempString.strip())
        except OSError:
            rc = 1

    # 1.1 Temperature
    SetTemperatureFile(PI.ProjectInput[NrRun - 1].Temperature_Filename)

    if (GetTemperatureFile() == "(None)") or (GetTemperatureFile() == "(External)"):
        SetTemperatureFileFull(GetTemperatureFile())  # no file

        TempString1 = "{:8.1f}".format(GetSimulParam_Tmin())
        TempString2 = "{:8.1f}".format(GetSimulParam_Tmax())

        SetTemperatureDescription(
            ("Default temperature data: Tmin = " + TempString1.strip()
            + " and Tmax = " + TempString2.strip() + " deg")
        )
    else:
        SetTemperatureFileFull(
            PI.ProjectInput[NrRun - 1].Temperature_Directory + GetTemperatureFile()
        )

        TemperatureFilefull_exists = FileExists(
            ResolvePath(GetTemperatureFileFull())
        )

        if TemperatureFilefull_exists:
            ReadTemperatureFileFull()

        temperature_record = GetTemperatureRecord()
        TemperatureDescriptionLocal = GetTemperatureDescription()

        TemperatureDescriptionLocal, temperature_record = LoadClim(
            GetTemperatureFileFull(),
            TemperatureDescriptionLocal,
            temperature_record,
        )

        SetTemperatureDescription(TemperatureDescriptionLocal)
        CompleteClimateDescription(temperature_record)
        SetTemperatureRecord(temperature_record)

    # Create Temperature Reference file
    if GetTemperatureFile() != "(External)":
        CreateTnxReferenceFile(
            GetTemperatureFile(),
            GetTnxReferenceFile(),
            GetTnxReferenceYear(),
        )

    CreateTnxReference365Days()

    # 1.2 ETo
    SetEToFile(PI.ProjectInput[NrRun - 1].ETo_Filename)

    if (GetEToFile() == "(None)") or (GetEToFile() == "(External)"):
        SetEToFileFull(GetEToFile())  # no file
        SetEToDescription("Specify ETo data when Running AquaCrop")
    else:
        SetEToFileFull(PI.ProjectInput[NrRun - 1].ETo_Directory + GetEToFile())

        eto_descr = GetEToDescription()
        etorecord_tmp = GetEToRecord()

        eto_descr, etorecord_tmp = LoadClim(
            GetEToFileFull(),
            eto_descr,
            etorecord_tmp,
        )

        SetEToDescription(eto_descr)
        CompleteClimateDescription(etorecord_tmp)
        SetEToRecord(etorecord_tmp)

    # 1.3 Rain
    SetRainFile(PI.ProjectInput[NrRun - 1].Rain_Filename)

    if (GetRainFile() == "(None)") or (GetRainFile() == "(External)"):
        SetRainFileFull(GetRainFile())  # no file
        SetRainDescription("Specify Rain data when Running AquaCrop")
    else:
        SetRainFileFull(PI.ProjectInput[NrRun - 1].Rain_Directory + GetRainFile())

        rain_descr = GetRainDescription()
        rainrecord_tmp = GetRainRecord()

        rain_descr, rainrecord_tmp = LoadClim(
            GetRainFileFull(),
            rain_descr,
            rainrecord_tmp,
        )

        SetRainDescription(rain_descr)
        CompleteClimateDescription(rainrecord_tmp)
        SetRainRecord(rainrecord_tmp)

    # 1.4 CO2
    SetCO2File(PI.ProjectInput[NrRun - 1].CO2_Filename)

    if GetCO2File() != "(None)":
        SetCO2FileFull(PI.ProjectInput[NrRun - 1].CO2_Directory + GetCO2File())

        CO2descr = GetCO2Description()
        CO2descr = GenerateCO2Description(GetCO2FileFull(), CO2descr)
        SetCO2Description(CO2descr)

    if GetClimateFile() != "(External)":
        SetClimData()

    AdjustOnsetSearchPeriod()  # Set initial StartSearch and StopSearchDayNr

    # 2. Calendar
    SetCalendarFile(PI.ProjectInput[NrRun - 1].Calendar_Filename.strip())

    if GetCalendarFile() == "(None)":
        SetCalendarDescription("No calendar for the Seeding/Planting year")
    else:
        SetCalendarFileFull(PI.ProjectInput[NrRun - 1].Calendar_Directory + GetCalendarFile())

        CalendarDescriptionLocal = GetCalendarDescription()
        CalendarDescriptionLocal = GetFileDescription(GetCalendarFileFull(), CalendarDescriptionLocal)
        SetCalendarDescription(CalendarDescriptionLocal)

    # 3. Crop
    SetSimulation_LinkCropToSimPeriod(True)
    SetCropFile(PI.ProjectInput[NrRun - 1].Crop_Filename)
    SetCropFileFull(PI.ProjectInput[NrRun - 1].Crop_Directory + GetCropFile())
    LoadCrop(GetCropFileFull())

    # Adjust crop parameters of Perennials
    if GetCrop_subkind() == subkind_Forage:
        # Valid since Perennials have their own end of season based on Temperature - added Version 7.3
        SetCrop_DayN(GetCrop_LastDayNr())
        # adjust crop characteristics to the Year (Seeding/Planting or Non-seeding/Planting year)
        Crop_Planting_temp = GetCrop_Planting()
        Crop_RootMin_temp = GetCrop_RootMin()
        Crop_SizePlant_temp = GetCrop_SizePlant()
        Crop_CCini_temp = GetCrop_CCini()
        Crop_DaysToCCini_temp = GetCrop_DaysToCCini()
        Crop_GDDaysToCCini_temp = GetCrop_GDDaysToCCini()

        (
            Crop_Planting_temp,
            Crop_RootMin_temp,
            Crop_SizePlant_temp,
            Crop_CCini_temp,
            Crop_DaysToCCini_temp,
            Crop_GDDaysToCCini_temp,
        ) = AdjustYearPerennials(
            GetSimulation_YearSeason(),
            GetCrop_SownYear1(),
            GetCrop_ModeCycle(),
            GetCrop_RootMax(),
            GetCrop_RootMinYear1(),
            GetCrop_CCo(),
            GetCrop_SizeSeedling(),
            GetCrop_CGC(),
            GetCrop_CCx(),
            GetCrop_GDDCGC(),
            GetCrop_PlantingDens(),
            Crop_Planting_temp,
            Crop_RootMin_temp,
            Crop_SizePlant_temp,
            Crop_CCini_temp,
            Crop_DaysToCCini_temp,
            Crop_GDDaysToCCini_temp,
        )

        SetCrop_Planting(Crop_Planting_temp)
        SetCrop_RootMin(Crop_RootMin_temp)
        SetCrop_SizePlant(Crop_SizePlant_temp)
        SetCrop_CCini(Crop_CCini_temp)
        SetCrop_DaysToCCini(Crop_DaysToCCini_temp)
        SetCrop_GDDaysToCCini(Crop_GDDaysToCCini_temp)

        # adjust length of season
        SetCrop_DaysToHarvest(GetCrop_DayN() - GetCrop_Day1() + 1)

        Crop_DaysToSenescence_temp = GetCrop_DaysToSenescence()
        Crop_DaysToHarvest_temp = GetCrop_DaysToHarvest()
        Crop_GDDaysToSenescence_temp = GetCrop_GDDaysToSenescence()
        Crop_GDDaysToHarvest_temp = GetCrop_GDDaysToHarvest()

        (
            Crop_DaysToSenescence_temp,
            Crop_DaysToHarvest_temp,
            Crop_GDDaysToSenescence_temp,
            Crop_GDDaysToHarvest_temp,
        ) = AdjustCropFileParameters(
            GetCropFileSet(),
            GetCrop_DaysToHarvest(),
            GetCrop_Day1(),
            GetCrop_ModeCycle(),
            GetCrop_Tbase(),
            GetCrop_Tupper(),
            Crop_DaysToSenescence_temp,
            Crop_DaysToHarvest_temp,
            Crop_GDDaysToSenescence_temp,
            Crop_GDDaysToHarvest_temp,
        )

        SetCrop_DaysToSenescence(Crop_DaysToSenescence_temp)
        SetCrop_DaysToHarvest(Crop_DaysToHarvest_temp)
        SetCrop_GDDaysToSenescence(Crop_GDDaysToSenescence_temp)
        SetCrop_GDDaysToHarvest(Crop_GDDaysToHarvest_temp)

    AdjustCalendarCrop(GetCrop_Day1())
    # added Version 7.3 since Crop.DayN is no longer READ for annuals
    SetCrop_DayN(GetCrop_Day1() + GetCrop_DaysToHarvest() - 1)

    CompleteCropDescription()

    # Onset.Off := true;
    if GetClimFile() == "(None)":
        Crop_Day1_temp = GetCrop_Day1()
        Crop_DayN_temp = GetCrop_DayN()

        Crop_Day1_temp, Crop_DayN_temp = AdjustCropYearToClimFile(Crop_Day1_temp, Crop_DayN_temp)

        # adjusting Crop.Day1 and Crop.DayN to ClimFile
        SetCrop_Day1(Crop_Day1_temp)
        SetCrop_DayN(Crop_DayN_temp)

    # adjusting ClimRecord.'TO' for undefined year with 365 days
    if (
        (GetClimFile() != "(None)")
        and (GetClimRecord_FromY() == 1901)
        and (GetClimRecord_NrObs() == 365)
    ):
        AdjustClimRecordTo(GetCrop_DayN())

    # adjusting simulation period
    AdjustSimPeriod()

    # 4. Irrigation
    SetIrriFile(PI.ProjectInput[NrRun - 1].Irrigation_Filename)

    if GetIrriFile() == "(None)":
        SetIrriFileFull(GetIrriFile())  # no file
        NoIrrigation()
        # IrriDescription := 'Rainfed cropping';
    else:
        SetIrriFileFull(PI.ProjectInput[NrRun - 1].Irrigation_Directory + GetIrriFile())
        LoadIrriScheduleInfo(GetIrriFileFull())

    # 5. Field Management
    SetManFile(PI.ProjectInput[NrRun - 1].Management_Filename)

    if GetManFile() == "(None)":
        SetManFileFull(GetManFile())
        SetManDescription("No specific field management")
    else:
        SetManFileFull(PI.ProjectInput[NrRun - 1].Management_Directory + GetManFile())
        LoadManagement(GetManFilefull())

        # reset canopy development to soil fertility
        FertStress = GetManagement_FertilityStress()
        Crop_DaysToFullCanopySF_temp = GetCrop_DaysToFullCanopySF()
        RedCGC_temp = GetSimulation_EffectStress_RedCGC()
        RedCCX_temp = GetSimulation_EffectStress_RedCCX()

        (
            Crop_DaysToFullCanopySF_temp,
            RedCGC_temp,
            RedCCX_temp,
            FertStress,
        ) = TimeToMaxCanopySF(
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

        SetCrop_DaysToFullCanopySF(Crop_DaysToFullCanopySF_temp)
        SetManagement_FertilityStress(FertStress)
        SetSimulation_EffectStress_RedCGC(RedCGC_temp)
        SetSimulation_EffectStress_RedCCX(RedCCX_temp)

    # 6. Soil Profile
    SetProfFile(PI.ProjectInput[NrRun - 1].Soil_Filename)

    if GetProfFile() == "(External)":
        SetProfFilefull(GetProfFile())
    elif GetProfFile() == "(None)":
        SetProfFilefull(GetPathNameSimul() + "DEFAULT.SOL")
    else:
        SetProfFilefull(PI.ProjectInput[NrRun - 1].Soil_Directory + GetProfFile())

    # The load of profile is delayed to check if soil water profile need to be
    # reset (see 8.)

    # 7. Groundwater
    SetGroundWaterFile(PI.ProjectInput[NrRun - 1].GroundWater_Filename)

    if GetGroundWaterFile() == "(None)":
        SetGroundWaterFileFull(GetGroundWaterFile())
        SetGroundWaterDescription("no shallow groundwater table")
    else:
        SetGroundWaterFileFull(PI.ProjectInput[NrRun - 1].GroundWater_Directory + GetGroundWaterFile())
        # Loading the groundwater is done after loading the soil profile (see 9.)

    # 8. Set simulation period
    SetSimulation_FromDayNr(PI.ProjectInput[NrRun - 1].Simulation_DayNr1)
    SetSimulation_ToDayNr(PI.ProjectInput[NrRun - 1].Simulation_DayNrN)

    if (GetCrop_Day1() != GetSimulation_FromDayNr()) or (GetCrop_DayN() != GetSimulation_ToDayNr()):
        SetSimulation_LinkCropToSimPeriod(False)

    # 9. Initial conditions
    if PI.ProjectInput[NrRun - 1].SWCIni_Filename == "KeepSWC":
        # No load of soil file (which reset thickness compartments and Soil
        # water content to FC)
        SetSWCIniFile("KeepSWC")
        SetSWCiniDescription("Keep soil water profile of previous run")
    else:
        # start with load and complete profile description (see 5.) which reset
        # SWC to FC by default
        if GetProfFile() == "(External)":
            LoadProfileProcessing(ProjectInput[NrRun - 1].VersionNr)
        else:
            LoadProfile(GetProfFilefull())
        CompleteProfileDescription()

        # Adjust size of compartments if required
        TotDepth = 0.0
        for i in range(1, GetNrCompartments() + 1):
            TotDepth = TotDepth + GetCompartment_Thickness(i)

        if GetSimulation_MultipleRunWithKeepSWC():
            # Project with a sequence of simulation runs and KeepSWC
            if roundc(GetSimulation_MultipleRunConstZrx() * 1000.0, mold="int32") > roundc(
                TotDepth * 1000.0, mold="int32"
            ):
                AdjustSizeCompartments(GetSimulation_MultipleRunConstZrx())
        else:
            if roundc(GetCrop_RootMax() * 1000.0, mold="int32") > roundc(
                TotDepth * 1000.0, mold="int32"
            ):
                if roundc(GetSoil_RootMax() * 1000.0, mold="int32") == roundc(
                    GetCrop_RootMax() * 1000.0, mold="int32"
                ):
                    AdjustSizeCompartments(float(GetCrop_RootMax()))
                    # no restrictive soil layer
                else:
                    # restrictive soil layer
                    if roundc(GetSoil_RootMax() * 1000.0, mold="int32") > roundc(
                        TotDepth * 1000.0, mold="int32"
                    ):
                        AdjustSizeCompartments(float(GetSoil_RootMax()))

        SetSWCIniFile(PI.ProjectInput[NrRun - 1].SWCIni_Filename)
        if GetSWCiniFile() == "(None)":
            SetSWCiniFileFull(GetSWCiniFile())  # no file
            SetSWCiniDescription("Soil water profile at Field Capacity")
        else:
            SetSWCiniFileFull(PI.ProjectInput[NrRun - 1].SWCIni_Directory + GetSWCiniFile())
            SurfaceStorage_temp = GetSurfaceStorage()
            SurfaceStorage_temp = LoadInitialConditions(GetSWCiniFileFull(), SurfaceStorage_temp)
            SetSurfaceStorage(SurfaceStorage_temp)
            # FIX BUG calc Drain (mayo 2026): el bloque que aquí re-detectaba
            # ini_at_fc y volvía a poner Simulation.IniSWC.AtFC=True NO existe
            # en el flujo batch de Pascal (TempProcessing.pas:1517-1565).
            # LoadInitialConditions ya deja AtFC=False (Global.pas:6104) y se debe
            # respetar ese estado. Si AtFC quedaba en True, ResetSWCToFC sobrescribía
            # Compartment.Theta = FCadj/100 ignorando el promedio inter-capa SW0,
            # añadiendo agua espuria a compartimentos en frontera entre capas y
            # produciendo +3-4 mm de Drain extra por campaña. Era un artefacto del
            # flujo GUI (IniCondNew.pas) trasladado por error al batch.

        Compartment_temp = GetCompartment()

        if GetSimulation_IniSWC_AtDepths() is True:
            Compartment_temp = TranslateIniPointsToSWProfile(
                GetSimulation_IniSWC_NrLoc(),
                GetSimulation_IniSWC_Loc(),
                GetSimulation_IniSWC_VolProc(),
                GetSimulation_IniSWC_SaltECe(),
                GetNrCompartments(),
                Compartment_temp,
            )
        else:
            Compartment_temp = TranslateIniLayersToSWProfile(
                GetSimulation_IniSWC_NrLoc(),
                GetSimulation_IniSWC_Loc(),
                GetSimulation_IniSWC_VolProc(),
                GetSimulation_IniSWC_SaltECe(),
                GetNrCompartments(),
                Compartment_temp,
            )

        SetCompartment(Compartment_temp)

        if GetSimulation_ResetIniSWC():
            # to reset SWC and SALT at end of simulation run
            for i in range(1, GetNrCompartments() + 1):
                SetSimulation_ThetaIni_i(i, GetCompartment_theta(i))
                SetSimulation_ECeIni_i(i, ECeComp(GetCompartment_i(i)))

            # ADDED WHEN DESINGNING 4.0 BECAUSE BELIEVED TO HAVE FORGOTTEN -
            # CHECK LATER
            if GetManagement_BundHeight() >= 0.01:
                SetSimulation_SurfaceStorageIni(GetSurfaceStorage())
                SetSimulation_ECStorageIni(GetECstorage())

    # 10. load the groundwater file if it exists (only possible for Version 4.0
    # and higher)
    if (roundc(10 * PI.ProjectInput[NrRun - 1].VersionNr, mold=1) >= 40) and \
    (GetGroundWaterFile() != '(None)'):
        # the groundwater file is only available in Version 4.0 or higher
        ZiAqua_temp = GetZiAqua()
        ECiAqua_temp = GetECiAqua()

        ZiAqua_temp, ECiAqua_temp = LoadGroundWater(
            GetGroundWaterFileFull(),
            GetSimulation_FromDayNr(),
            ZiAqua_temp,
            ECiAqua_temp,
        )

        SetZiAqua(ZiAqua_temp)
        SetECiAqua(ECiAqua_temp)
    else:
        SetZiAqua(undef_int)
        SetECiAqua(float(undef_int))
        SetSimulParam_ConstGwt(True)

    Compartment_temp = GetCompartment()
    Compartment_temp = CalculateAdjustedFC((GetZiAqua() / 100.0), Compartment_temp)
    SetCompartment(Compartment_temp)

    if GetSimulation_IniSWC_AtFC() and (GetSWCiniFile() != 'KeepSWC'):
        ResetSWCToFC()

    # 11. Off-season conditions
    SetOffSeasonFile(PI.ProjectInput[NrRun - 1].OffSeason_Filename)
    if GetOffSeasonFile() == '(None)':
        SetOffSeasonFilefull(GetOffSeasonFile())
        SetOffSeasonDescription('No specific off-season conditions')
    else:
        SetOffSeasonFilefull(
            PI.ProjectInput[NrRun - 1].OffSeason_Directory + GetOffSeasonFile()
        )
        LoadOffSeason(GetOffSeasonFileFull())

    # 12. Field data
    SetObservationsFile(PI.ProjectInput[NrRun - 1].Observations_Filename)
    if GetObservationsFile() == '(None)':
        SetObservationsFilefull(GetObservationsFile())
        SetObservationsDescription('No field observations')
    else:
        SetObservationsFilefull(
            PI.ProjectInput[NrRun - 1].Observations_Directory + GetObservationsFile()
        )
        observations_descr = GetObservationsDescription()
        observations_descr = GetFileDescription(
            GetObservationsFilefull(),
            observations_descr,
        )
        SetObservationsDescription(observations_descr)



def TemperatureFileCoveringCropPeriod(CropFirstDay: int, CropLastDay: int):
    totalnameOUT = ""
    fhandle = None
    i = 0
    RunningDay = 0
    TminDataSet = [rep_DayEventDbl() for _ in range(31 + 1)]  # 1-based (1..31)
    TmaxDataSet = [rep_DayEventDbl() for _ in range(31 + 1)]  # 1-based (1..31)
    Tlow = 0.0
    Thigh = 0.0

    if TemperatureFilefull_exists:
        # open file and find first day of cropping period
        dt = GetTemperatureRecord_DataType()

        if dt == datatype_Daily:
            # Tmin and Tmax arrays contain the TemperatureFilefull data
            i = CropFirstDay - GetTemperatureRecord_FromDayNr() + 1
            Tlow = Tmin[i - 1]
            Thigh = Tmax[i - 1]

        elif dt == datatype_Decadely:
            TminDataSet, TmaxDataSet = GetDecadeTemperatureDataSet(
                CropFirstDay, TminDataSet, TmaxDataSet
            )
            i = 1
            while TminDataSet[i].DayNr != CropFirstDay:
                i += 1
            Tlow = TminDataSet[i].Param
            Thigh = TmaxDataSet[i].Param

        else:  # datatype_monthly
            TminDataSet, TmaxDataSet = GetMonthlyTemperatureDataSet(
                CropFirstDay, TminDataSet, TmaxDataSet
            )
            i = 1
            while TminDataSet[i].DayNr != CropFirstDay:
                i += 1
            Tlow = TminDataSet[i].Param
            Thigh = TmaxDataSet[i].Param

        # create SIM file and record first day
        totalnameOUT = GetPathNameSimul().strip() + "TCrop.SIM"

        # Reduce disk I/O: build all lines in memory and write once
        lines_out = []
        lines_out.append(f"{float(Tlow):10.4f}{float(Thigh):10.4f}")

        # next days of simulation period
        for RunningDay in range(CropFirstDay + 1, CropLastDay + 1):
            dt = GetTemperatureRecord_DataType()

            if dt == datatype_Daily:
                i = i + 1
                if i == len(Tmin):
                    i = 1
                Tlow = Tmin[i - 1]
                Thigh = Tmax[i - 1]

            elif dt == datatype_Decadely:
                if RunningDay > TminDataSet[31].DayNr:
                    TminDataSet, TmaxDataSet = GetDecadeTemperatureDataSet(
                        RunningDay, TminDataSet, TmaxDataSet
                    )
                i = 1
                while TminDataSet[i].DayNr != RunningDay:
                    i += 1
                Tlow = TminDataSet[i].Param
                Thigh = TmaxDataSet[i].Param

            else:  # datatype_monthly
                if RunningDay > TminDataSet[31].DayNr:
                    TminDataSet, TmaxDataSet = GetMonthlyTemperatureDataSet(
                        RunningDay, TminDataSet, TmaxDataSet
                    )
                i = 1
                while TminDataSet[i].DayNr != RunningDay:
                    i += 1
                Tlow = TminDataSet[i].Param
                Thigh = TmaxDataSet[i].Param

            lines_out.append(f"{float(Tlow):10.4f}{float(Thigh):10.4f}")

        name = _strip_quotes(totalnameOUT).strip()
        if os.path.isabs(name):
            full_out_path = os.path.normpath(name)
        else:
            full_out_path = os.path.normpath(
                os.path.join(complete_path_dir, name.lstrip("/\\"))
            )

        with open(full_out_path, "w", encoding="utf-8") as fhandle:
            fhandle.write("\n".join(lines_out) + "\n")
        if os.environ.get("AQUACROP_DEBUG_TRACE", "").strip():
            from .debugtrace import append_file_preview
            append_file_preview(complete_path_dir, "TCrop.SIM", full_out_path)

    else:
        if GetTemperatureFile() != "(External)":
            print("ERROR: no valid air temperature file")
            return
            # fatal error if no air temperature file



def LoadOffSeason(FullName):
    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(FullName).lstrip("/\\"),
        )
    )

    file_exists = os.path.isfile(full_path)

    if not file_exists:
        print("LoadOffSeason file not found")
        return

    with open(full_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    idx = 0

    OffSeasonDescr_temp = lines[idx].strip()
    idx += 1
    SetOffSeasonDescription(OffSeasonDescr_temp)

    VersionNr = float(lines[idx].split()[0])  # AquaCrop Version
    idx += 1

    # mulches
    TempShortInt = int(lines[idx].split()[0])
    idx += 1
    SetManagement_SoilCoverBefore(TempShortInt)

    TempShortInt = int(lines[idx].split()[0])
    idx += 1
    SetManagement_SoilCoverAfter(TempShortInt)

    TempShortInt = int(lines[idx].split()[0])
    idx += 1
    SetManagement_EffectMulchOffS(TempShortInt)

    # irrigation events - initialise
    for Nri in range(1, 5 + 1):
        SetIrriBeforeSeason_DayNr(Nri, 0)
        SetIrriBeforeSeason_Param(Nri, 0)
        SetIrriAfterSeason_DayNr(Nri, 0)
        SetIrriAfterSeason_Param(Nri, 0)

    NrEvents1 = int(lines[idx].split()[0])  # number of irrigation events BEFORE growing period
    idx += 1

    if roundc(10 * VersionNr, mold=1) < 32:  # irrigation water quality BEFORE growing period
        SetIrriECw_PreSeason(0.0)
    else:
        PreSeason_in = float(lines[idx].split()[0])
        idx += 1
        SetIrriECw_PreSeason(PreSeason_in)

    NrEvents2 = int(lines[idx].split()[0])  # number of irrigation events AFTER growing period
    idx += 1

    if roundc(10 * VersionNr, mold=1) < 32:  # irrigation water quality AFTER growing period
        SetIrriECw_PostSeason(0.0)
    else:
        PostSeason_in = float(lines[idx].split()[0])
        idx += 1
        SetIrriECw_PostSeason(PostSeason_in)

    simul_irri_of = int(lines[idx].split()[0])  # percentage of soil surface wetted
    idx += 1
    SetSimulParam_IrriFwOffSeason(simul_irri_of)

    # irrigation events - get events before and after season
    if (NrEvents1 > 0) or (NrEvents2 > 0):
        for Nri in range(1, 3 + 1):
            idx += 1  # title

    if NrEvents1 > 0:
        for Nri in range(1, NrEvents1 + 1):
            # events BEFORE growing period
            ParamString = lines[idx]
            idx += 1
            Par1, Par2 = SplitStringInTwoParams(ParamString, 0.0, 0.0)
            SetIrriBeforeSeason_DayNr(Nri, roundc(Par1, mold=1))
            SetIrriBeforeSeason_Param(Nri, roundc(Par2, mold=1))

    if NrEvents2 > 0:
        for Nri in range(1, NrEvents2 + 1):
            # events AFTER growing period
            ParamString = lines[idx]
            idx += 1
            Par1, Par2 = SplitStringInTwoParams(ParamString, 0.0, 0.0)
            SetIrriAfterSeason_DayNr(Nri, roundc(Par1, mold=1))
            SetIrriAfterSeason_Param(Nri, roundc(Par2, mold=1))


def GDDCDCToCDC(
    PlantDayNr: int,
    D123: int,
    GDDL123: int,
    GDDHarvest: int,
    CCx: float,
    GDDCDC: float,
    Tbase: float,
    Tupper: float,
    NoTempFileTMin: float,
    NoTempFileTMax: float,
    CDC: float,
    Reference: bool,
) -> float:

    # integer(int32) :: ti, GDDi
    # real(dp) :: CCi

    GDDi = int(LengthCanopyDecline(CCx, GDDCDC))

    if (GDDL123 + GDDi) <= GDDHarvest:
        CCi = 0.0  # full decline
    else:
        # partly decline
        if GDDL123 < GDDHarvest:
            GDDi = int(GDDHarvest - GDDL123)
        else:
            GDDi = 5  # Fortran hace asignación real->int32; aquí queda 5

        CCi = CCx * (
            1.0
            - 0.05
            * (
                (math.exp(float(GDDi) * (GDDCDC * 3.33) / (CCx + 2.29)) - 1.0)
            )
        )
        # CC at time ti

    if Reference:
        ti = SumCalendarDaysReferenceTnx(
            GDDi,
            (PlantDayNr + D123),
            (PlantDayNr + D123),
            Tbase,
            Tupper,
            NoTempFileTMin,
            NoTempFileTMax,
        )
    else:
        ti = SumCalendarDays(
            GDDi,
            (PlantDayNr + D123),
            Tbase,
            Tupper,
            NoTempFileTMin,
            NoTempFileTMax,
        )


    if ti > 0:
        CDC = (
            ((CCx + 2.29) / float(ti))
            * math.log(1.0 + ((1.0 - (CCi / CCx)) / 0.05))
        ) / 3.33
    else:
        CDC = undef_int

    return CDC










def AdjustCalendarDays(
    PlantDayNr: int,
    InfoCropType: int,
    Tbase: float,
    Tupper: float,
    NoTempFileTMin: float,
    NoTempFileTMax: float,
    GDDL0: int,
    GDDL12: int,
    GDDFlor: int,
    GDDLengthFlor: int,
    GDDL123: int,
    GDDHarvest: int,
    GDDLZmax: int,
    GDDHImax: int,          # inout en Fortran (aquí lo devolvemos por coherencia)
    GDDCGC: float,
    GDDCDC: float,
    CCo: float,
    CCx: float,
    IsCGCGiven: bool,
    HIndex: int,
    TheDaysToCCini: int,
    TheGDDaysToCCini: int,
    ThePlanting: int,
    D0: int,
    D12: int,
    DFlor: int,
    LengthFlor: int,
    D123: int,
    DHarvest: int,
    DLZmax: int,
    LHImax: int,
    StLength,               # dimension(4) inout (lista/array)
    CGC: float,
    CDC: float,
    dHIdt: float,
    Succes: bool,
):
    tmp_NoTempFileTMin = float(NoTempFileTMin)
    tmp_NoTempFileTMax = float(NoTempFileTMax)

    Succes = True

    if TheDaysToCCini == 0:
        # planting/sowing
        D0 = SumCalendarDays(GDDL0, PlantDayNr, Tbase, Tupper, NoTempFileTMin, NoTempFileTMax)
        D12 = SumCalendarDays(GDDL12, PlantDayNr, Tbase, Tupper, NoTempFileTMin, NoTempFileTMax)
    else:
        # regrowth
        if TheDaysToCCini > 0:
            # CCini < CCx
            ExtraGDDays = GDDL12 - GDDL0 - TheGDDaysToCCini
            ExtraDays = SumCalendarDays(
                ExtraGDDays, PlantDayNr, Tbase, Tupper, NoTempFileTMin, NoTempFileTMax
            )
            D12 = D0 + TheDaysToCCini + ExtraDays

    if InfoCropType != subkind_Forage:
        D123 = SumCalendarDays(GDDL123, PlantDayNr, Tbase, Tupper, tmp_NoTempFileTMin, tmp_NoTempFileTMax)
        DHarvest = SumCalendarDays(GDDHarvest, PlantDayNr, Tbase, Tupper, tmp_NoTempFileTMin, tmp_NoTempFileTMax)

    DLZmax = SumCalendarDays(GDDLZmax, PlantDayNr, Tbase, Tupper, tmp_NoTempFileTMin, tmp_NoTempFileTMax)

    if (InfoCropType == subkind_Grain) or (InfoCropType == subkind_Tuber):
        DFlor = SumCalendarDays(GDDFlor, PlantDayNr, Tbase, Tupper, tmp_NoTempFileTMin, tmp_NoTempFileTMax)
        if DFlor != undef_int:
            if InfoCropType == subkind_Grain:
                LengthFlor = SumCalendarDays(
                    GDDLengthFlor, (PlantDayNr + DFlor), Tbase, Tupper, tmp_NoTempFileTMin, tmp_NoTempFileTMax
                )
            else:
                LengthFlor = 0

            LHImax = SumCalendarDays(
                GDDHImax, (PlantDayNr + DFlor), Tbase, Tupper, tmp_NoTempFileTMin, tmp_NoTempFileTMax
            )
            if (LengthFlor == undef_int) or (LHImax == undef_int):
                Succes = False
        else:
            LengthFlor = undef_int
            LHImax = undef_int
            Succes = False

    elif (InfoCropType == subkind_Vegetative) or (InfoCropType == subkind_Forage):
        LHImax = SumCalendarDays(GDDHImax, PlantDayNr, Tbase, Tupper, tmp_NoTempFileTMin, tmp_NoTempFileTMax)

    if (
        (D0 == undef_int)
        or (D12 == undef_int)
        or (D123 == undef_int)
        or (DHarvest == undef_int)
        or (DLZmax == undef_int)
    ):
        Succes = False

    if Succes:
        CGC = (float(GDDL12) / float(D12)) * float(GDDCGC)

        # call GDDCDCToCDC(...)
        # (CDC es inout en Fortran, aquí lo recogemos como retorno)
        CDC = GDDCDCToCDC(
            PlantDayNr,
            D123,
            GDDL123,
            GDDHarvest,
            CCx,
            GDDCDC,
            Tbase,
            Tupper,
            tmp_NoTempFileTMin,
            tmp_NoTempFileTMax,
            CDC,
            False,
        )

        # call DetermineLengthGrowthStages(...)
        # (D123, StLength, D12, CGC son inout en Fortran)
        D123, StLength, D12, CGC = DetermineLengthGrowthStages(
            CCo,
            CCx,
            CDC,
            D0,
            DHarvest,
            IsCGCGiven,
            TheDaysToCCini,
            ThePlanting,
            D123,
            StLength,
            D12,
            CGC,
        )

        if (InfoCropType == subkind_Grain) or (InfoCropType == subkind_Tuber):
            dHIdt = float(HIndex) / float(LHImax)

        if (InfoCropType == subkind_Vegetative) or (InfoCropType == subkind_Forage):
            if LHImax > 0:
                if LHImax > DHarvest:
                    dHIdt = float(HIndex) / float(DHarvest)
                else:
                    dHIdt = float(HIndex) / float(LHImax)

                if dHIdt > 100.0:
                    dHIdt = 100.0
                    LHImax = 0
            else:
                dHIdt = 100.0
                LHImax = 0

    return (
        GDDHImax,
        D0, D12, DFlor, LengthFlor, D123, DHarvest, DLZmax, LHImax,
        StLength, CGC, CDC, dHIdt,
        Succes,
    )


def AdjustCalendarCrop(FirstCropDay: int):
    Succes = True
    CGCisGiven = True

    Crop_GDDaysToHIo_temp = 0
    Crop_DaysToGermination_temp = 0
    Crop_DaysToFullCanopy_temp = 0
    Crop_DaysToFlowering_temp = 0
    Crop_LengthFlowering_temp = 0
    Crop_DaysToSenescence_temp = 0
    Crop_DaysToHarvest_temp = 0
    Crop_DaysToMaxRooting_temp = 0
    Crop_DaysToHIo_temp = 0
    Crop_Length_temp = None
    Crop_CGC_temp = 0.0
    Crop_CDC_temp = 0.0
    Crop_dHIdt_temp = 0.0

    CGCisGiven = True

    if GetCrop_ModeCycle() == ModeCycle_GDDays:
        # SetCrop_GDDaysToFullCanopy(...)
        tmp = (
            math.log(
                (0.25 * GetCrop_CCx() * GetCrop_CCx() / GetCrop_CCo())
                / (GetCrop_CCx() - (0.98 * GetCrop_CCx()))
            )
            / GetCrop_GDDCGC()
        )
        SetCrop_GDDaysToFullCanopy(
            GetCrop_GDDaysToGermination() + int(roundc(tmp, mold="int32"))
        )

        if GetCrop_GDDaysToFullCanopy() > GetCrop_GDDaysToHarvest():
            SetCrop_GDDaysToFullCanopy(GetCrop_GDDaysToHarvest())

        Crop_GDDaysToHIo_temp = GetCrop_GDDaysToHIo()
        Crop_DaysToGermination_temp = GetCrop_DaysToGermination()
        Crop_DaysToFullCanopy_temp = GetCrop_DaysToFullCanopy()
        Crop_DaysToFlowering_temp = GetCrop_DaysToFlowering()
        Crop_LengthFlowering_temp = GetCrop_LengthFlowering()
        Crop_DaysToSenescence_temp = GetCrop_DaysToSenescence()
        Crop_DaysToHarvest_temp = GetCrop_DaysToHarvest()
        Crop_DaysToMaxRooting_temp = GetCrop_DaysToMaxRooting()
        Crop_DaysToHIo_temp = GetCrop_DaysToHIo()
        Crop_Length_temp = GetCrop_Length()
        Crop_CGC_temp = GetCrop_CGC()
        Crop_CDC_temp = GetCrop_CDC()
        Crop_dHIdt_temp = GetCrop_dHIdt()

        (
            Crop_GDDaysToHIo_temp,
            Crop_DaysToGermination_temp,
            Crop_DaysToFullCanopy_temp,
            Crop_DaysToFlowering_temp,
            Crop_LengthFlowering_temp,
            Crop_DaysToSenescence_temp,
            Crop_DaysToHarvest_temp,
            Crop_DaysToMaxRooting_temp,
            Crop_DaysToHIo_temp,
            Crop_Length_temp,
            Crop_CGC_temp,
            Crop_CDC_temp,
            Crop_dHIdt_temp,
            Succes,
        ) = AdjustCalendarDays(
            FirstCropDay,
            GetCrop_subkind(),
            GetCrop_Tbase(),
            GetCrop_Tupper(),
            GetSimulParam_Tmin(),
            GetSimulParam_Tmax(),
            GetCrop_GDDaysToGermination(),
            GetCrop_GDDaysToFullCanopy(),
            GetCrop_GDDaysToFlowering(),
            GetCrop_GDDLengthFlowering(),
            GetCrop_GDDaysToSenescence(),
            GetCrop_GDDaysToHarvest(),
            GetCrop_GDDaysToMaxRooting(),
            Crop_GDDaysToHIo_temp,
            GetCrop_GDDCGC(),
            GetCrop_GDDCDC(),
            GetCrop_CCo(),
            GetCrop_CCx(),
            CGCisGiven,
            GetCrop_HI(),
            GetCrop_DaysToCCini(),
            GetCrop_GDDaysToCCini(),
            GetCrop_Planting(),
            Crop_DaysToGermination_temp,
            Crop_DaysToFullCanopy_temp,
            Crop_DaysToFlowering_temp,
            Crop_LengthFlowering_temp,
            Crop_DaysToSenescence_temp,
            Crop_DaysToHarvest_temp,
            Crop_DaysToMaxRooting_temp,
            Crop_DaysToHIo_temp,
            Crop_Length_temp,
            Crop_CGC_temp,
            Crop_CDC_temp,
            Crop_dHIdt_temp,
            Succes,
        )

        SetCrop_GDDaysToHIo(Crop_GDDaysToHIo_temp)
        SetCrop_DaysToGermination(Crop_DaysToGermination_temp)
        SetCrop_DaysToFullCanopy(Crop_DaysToFullCanopy_temp)
        SetCrop_DaysToFlowering(Crop_DaysToFlowering_temp)
        SetCrop_LengthFlowering(Crop_LengthFlowering_temp)
        SetCrop_DaysToSenescence(Crop_DaysToSenescence_temp)
        SetCrop_DaysToHarvest(Crop_DaysToHarvest_temp)
        SetCrop_DaysToMaxRooting(Crop_DaysToMaxRooting_temp)
        SetCrop_DaysToHIo(Crop_DaysToHIo_temp)
        SetCrop_Length(Crop_Length_temp)
        SetCrop_CGC(Crop_CGC_temp)
        SetCrop_CDC(Crop_CDC_temp)
        SetCrop_dHIdt(Crop_dHIdt_temp)

    else:
        Succes = True






def AdjustCropFileParameters(
    TheCropFileSet,
    LseasonDays: int,
    TheCropDay1: int,
    TheModeCycle,
    TheTbase: float,
    TheTupper: float,
    L123: int,
    L1234: int,
    GDD123: int,
    GDD1234: int,
):
    Tmin_tmp = 0.0
    Tmax_tmp = 0.0

    # Adjust some crop parameters (CROP.*) as specified by the generated length season (LseasonDays)

    # time to maturity
    L1234 = LseasonDays  # days
    if TheModeCycle == ModeCycle_GDDays:
        Tmin_tmp = GetSimulParam_Tmin()
        Tmax_tmp = GetSimulParam_Tmax()
        GDD1234 = GrowingDegreeDays(
            LseasonDays,
            TheCropDay1,
            TheTbase,
            TheTupper,
            Tmin_tmp,
            Tmax_tmp,
        )
    else:
        GDD1234 = undef_int

    # time to senescence (reference is given in TheCropFileSet)
    if TheModeCycle == ModeCycle_GDDays:
        GDD123 = GDD1234 - TheCropFileSet.GDDaysFromSenescenceToEnd
        if GDD123 >= GDD1234:
            GDD123 = GDD1234
            L123 = LseasonDays
        else:
            Tmin_tmp = GetSimulParam_Tmin()
            Tmax_tmp = GetSimulParam_Tmax()
            L123 = SumCalendarDays(
                GDD123,
                TheCropDay1,
                TheTbase,
                TheTupper,
                Tmin_tmp,
                Tmax_tmp,
            )
    else:
        L123 = L1234 - TheCropFileSet.DaysFromSenescenceToEnd
        if L123 >= L1234:
            L123 = LseasonDays
        GDD123 = undef_int

    return L123, L1234, GDD123, GDD1234


def SumCalendarDays(
    ValGDDays: int,
    FirstDayCrop: int,
    Tbase: float,
    Tupper: float,
    TDayMin: float,
    TDayMax: float,
) -> int:
    i = 0
    NrCDays = 0
    RemainingGDDays = 0.0
    DayGDD = 0.0
    DayNri = 0
    AdjustDayNri = False
    TDayMin_loc = float(TDayMin)
    TDayMax_loc = float(TDayMax)

    # dimension(31) -> usamos 1-based (1..31)
    TminDataSet = [rep_DayEventDbl() for _ in range(31 + 1)]
    TmaxDataSet = [rep_DayEventDbl() for _ in range(31 + 1)]

    if ValGDDays > 0:
        if GetTemperatureFile() == "(None)":
            # given average Tmin and Tmax
            DayGDD = DegreesDay(Tbase, Tupper, TDayMin_loc, TDayMax_loc, GetSimulParam_GDDMethod())

            if abs(DayGDD) < math.ulp(1.0):
                NrCDays = -9
            else:
                NrCDays = int(roundc(float(ValGDDays) / DayGDD, mold="int32"))

        elif GetTemperatureFile() == "(External)":
            DayNri = FirstDayCrop
            RemainingGDDays = float(ValGDDays)

            i = DayNri - GetSimulation_FromDayNr() + 1
            TDayMin_loc = float(GetTminRun_i(i))
            TDayMax_loc = float(GetTmaxRun_i(i))

            DayGDD = DegreesDay(Tbase, Tupper, TDayMin_loc, TDayMax_loc, GetSimulParam_GDDMethod())
            NrCDays = NrCDays + 1
            RemainingGDDays = RemainingGDDays - DayGDD

            while (RemainingGDDays > 0) and (i <= (GetSimulation_ToDayNr() - GetSimulation_FromDayNr() + 1)):
                i = i + 1
                # LIS runs for a period of a calendar year
                if i == 366:
                    i = 1

                TDayMin_loc = float(GetTminRun_i(i))
                TDayMax_loc = float(GetTmaxRun_i(i))

                DayGDD = DegreesDay(Tbase, Tupper, TDayMin_loc, TDayMax_loc, GetSimulParam_GDDMethod())
                NrCDays = NrCDays + 1
                RemainingGDDays = RemainingGDDays - DayGDD

            if RemainingGDDays > 0:
                NrCDays = undef_int

        else:
            DayNri = FirstDayCrop

            if FullUndefinedRecord(
                GetTemperatureRecord_FromY(),
                GetTemperatureRecord_FromD(),
                GetTemperatureRecord_FromM(),
                GetTemperatureRecord_ToD(),
                GetTemperatureRecord_ToM(),
            ):
                AdjustDayNri = True
                DayNri = SetDayNrToYundef(DayNri)
            else:
                AdjustDayNri = False

            if (
                TemperatureFilefull_exists
                and (GetTemperatureRecord_ToDayNr() > DayNri)
                and (GetTemperatureRecord_FromDayNr() <= DayNri)
            ):
                RemainingGDDays = float(ValGDDays)

                dt = GetTemperatureRecord_DataType()

                if dt == datatype_Daily:
                    # Tmin/Tmax contienen el TemperatureFilefull
                    i = DayNri - GetTemperatureRecord_FromDayNr() + 1

                    # En Fortran: Tmin(i), Tmax(i) con i 1-based
                    # En Python: acceso con i-1
                    TDayMin_loc = float(Tmin[i - 1])
                    TDayMax_loc = float(Tmax[i - 1])

                    DayGDD = DegreesDay(Tbase, Tupper, TDayMin_loc, TDayMax_loc, GetSimulParam_GDDMethod())
                    NrCDays = NrCDays + 1
                    RemainingGDDays = RemainingGDDays - DayGDD
                    DayNri = DayNri + 1

                    while (RemainingGDDays > 0) and ((DayNri < GetTemperatureRecord_ToDayNr()) or AdjustDayNri):
                        i = i + 1
                        if i == len(Tmin):
                            i = 1

                        TDayMin_loc = float(Tmin[i - 1])
                        TDayMax_loc = float(Tmax[i - 1])

                        DayGDD = DegreesDay(Tbase, Tupper, TDayMin_loc, TDayMax_loc, GetSimulParam_GDDMethod())
                        NrCDays = NrCDays + 1
                        RemainingGDDays = RemainingGDDays - DayGDD
                        DayNri = DayNri + 1

                    if RemainingGDDays > 0:
                        NrCDays = undef_int

                elif dt == datatype_Decadely:
                    TminDataSet, TmaxDataSet = GetDecadeTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet)

                    i = 1
                    while (i <= 31) and (TminDataSet[i].DayNr != DayNri):
                        i = i + 1

                    TDayMin_loc = float(TminDataSet[i].Param)
                    TDayMax_loc = float(TmaxDataSet[i].Param)

                    DayGDD = DegreesDay(Tbase, Tupper, TDayMin_loc, TDayMax_loc, GetSimulParam_GDDMethod())
                    NrCDays = NrCDays + 1
                    RemainingGDDays = RemainingGDDays - DayGDD
                    DayNri = DayNri + 1

                    while (RemainingGDDays > 0) and ((DayNri < GetTemperatureRecord_ToDayNr()) or AdjustDayNri):
                        if DayNri > TminDataSet[31].DayNr:
                            TminDataSet, TmaxDataSet = GetDecadeTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet)

                        i = 1
                        while (i <= 31) and (TminDataSet[i].DayNr != DayNri):
                            i = i + 1

                        TDayMin_loc = float(TminDataSet[i].Param)
                        TDayMax_loc = float(TmaxDataSet[i].Param)

                        DayGDD = DegreesDay(Tbase, Tupper, TDayMin_loc, TDayMax_loc, GetSimulParam_GDDMethod())
                        NrCDays = NrCDays + 1
                        RemainingGDDays = RemainingGDDays - DayGDD
                        DayNri = DayNri + 1

                    if RemainingGDDays > 0:
                        NrCDays = undef_int

                elif dt == datatype_Monthly:
                    TminDataSet, TmaxDataSet = GetMonthlyTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet)

                    i = 1
                    while (i <= 31) and (TminDataSet[i].DayNr != DayNri):
                        i = i + 1

                    TDayMin_loc = float(TminDataSet[i].Param)
                    TDayMax_loc = float(TmaxDataSet[i].Param)

                    DayGDD = DegreesDay(Tbase, Tupper, TDayMin_loc, TDayMax_loc, GetSimulParam_GDDMethod())
                    NrCDays = NrCDays + 1
                    RemainingGDDays = RemainingGDDays - DayGDD
                    DayNri = DayNri + 1

                    while (RemainingGDDays > 0) and ((DayNri < GetTemperatureRecord_ToDayNr()) or AdjustDayNri):
                        if DayNri > TminDataSet[31].DayNr:
                            TminDataSet, TmaxDataSet = GetMonthlyTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet)

                        i = 1
                        while (i <= 31) and (TminDataSet[i].DayNr != DayNri):
                            i = i + 1

                        TDayMin_loc = float(TminDataSet[i].Param)
                        TDayMax_loc = float(TmaxDataSet[i].Param)

                        DayGDD = DegreesDay(Tbase, Tupper, TDayMin_loc, TDayMax_loc, GetSimulParam_GDDMethod())
                        NrCDays = NrCDays + 1
                        RemainingGDDays = RemainingGDDays - DayGDD
                        DayNri = DayNri + 1

                    if RemainingGDDays > 0:
                        NrCDays = undef_int
            else:
                NrCDays = undef_int
                
    return int(NrCDays)





def GrowingDegreeDays(
    ValPeriod: int,
    FirstDayPeriod: int,
    Tbase: float,
    Tupper: float,
    TDayMin: float,
    TDayMax: float,
) -> int:
    
    global TemperatureFilefull_exists
    i = 0
    RemainingDays = 0
    DayNri = 0
    GDDays = 0.0
    DayGDD = 0.0

    # dimension(31)
    TminDataSet = [rep_DayEventDbl() for _ in range(31 + 1)]
    TmaxDataSet = [rep_DayEventDbl() for _ in range(31 + 1)]

    AdjustDayNri = False
    TDayMin_local = float(TDayMin)
    TDayMax_local = float(TDayMax)

    GDDays = 0.0

    if ValPeriod > 0:
        if GetTemperatureFile() == "(None)":
            # given average Tmin and Tmax
            DayGDD = DegreesDay(
                Tbase,
                Tupper,
                TDayMin_local,
                TDayMax_local,
                GetSimulParam_GDDMethod(),
            )
            GDDays = float(roundc(ValPeriod * DayGDD, mold="int32"))

        elif GetTemperatureFile() == "(External)":
            DayNri = FirstDayPeriod
            RemainingDays = ValPeriod

            i = DayNri - GetSimulation_FromDayNr() + 1
            TDayMin_local = float(GetTminRun_i(i))
            TDayMax_local = float(GetTmaxRun_i(i))

            DayGDD = DegreesDay(
                Tbase,
                Tupper,
                TDayMin_local,
                TDayMax_local,
                GetSimulParam_GDDMethod(),
            )
            GDDays += DayGDD
            RemainingDays -= 1

            while (RemainingDays > 0) and (i <= (GetSimulation_ToDayNr() - GetSimulation_FromDayNr() + 1)):
                i += 1
                # LIS in for now run with a sim period of 365 days
                if i == 366:
                    i = 1

                TDayMin_local = float(GetTminRun_i(i))
                TDayMax_local = float(GetTmaxRun_i(i))
                DayGDD = DegreesDay(
                    Tbase,
                    Tupper,
                    TDayMin_local,
                    TDayMax_local,
                    GetSimulParam_GDDMethod(),
                )
                GDDays += DayGDD
                RemainingDays -= 1

            if RemainingDays > 0:
                GDDays = undef_int

        else:
            # temperature file
            DayNri = FirstDayPeriod

            if FullUndefinedRecord(
                GetTemperatureRecord_FromY(),
                GetTemperatureRecord_FromD(),
                GetTemperatureRecord_FromM(),
                GetTemperatureRecord_ToD(),
                GetTemperatureRecord_ToM(),
            ):
                AdjustDayNri = True
                SetDayNrToYundef(DayNri)
            else:
                AdjustDayNri = False
            
            if (
                TemperatureFilefull_exists
                and (GetTemperatureRecord_ToDayNr() > DayNri)
                and (GetTemperatureRecord_FromDayNr() <= DayNri)
            ):
                RemainingDays = ValPeriod

                dt = GetTemperatureRecord_DataType()
                if dt == datatype_Daily:
                    # Tmin and Tmax arrays contain the TemperatureFilefull data
                    i = DayNri - GetTemperatureRecord_FromDayNr() + 1

                    TDayMin_local = Tmin[i - 1]
                    TDayMax_local = Tmax[i - 1]

                    DayGDD = DegreesDay(
                        Tbase,
                        Tupper,
                        TDayMin_local,
                        TDayMax_local,
                        GetSimulParam_GDDMethod(),
                    )
                    
                    GDDays += DayGDD
                    RemainingDays -= 1
                    DayNri += 1

                    while (RemainingDays > 0) and ((DayNri < GetTemperatureRecord_ToDayNr()) or AdjustDayNri):
                        i += 1
                        if i == len(Tmin):
                            i = 1

                        TDayMin_local = Tmin[i - 1]
                        TDayMax_local = Tmax[i - 1]

                        DayGDD = DegreesDay(
                            Tbase,
                            Tupper,
                            TDayMin_local,
                            TDayMax_local,
                            GetSimulParam_GDDMethod(),
                        )
                        GDDays += DayGDD
                        RemainingDays -= 1
                        DayNri += 1

                    if RemainingDays > 0:
                        GDDays = undef_int

                elif dt == datatype_Decadely:
                    TminDataSet, TmaxDataSet = GetDecadeTemperatureDataSet(
                        DayNri, TminDataSet, TmaxDataSet
                    )

                    i = 1
                    while TminDataSet[i].DayNr != DayNri:
                        i += 1

                    TDayMin_local = TminDataSet[i].Param
                    TDayMax_local = TmaxDataSet[i].Param

                    DayGDD = DegreesDay(
                        Tbase,
                        Tupper,
                        TDayMin_local,
                        TDayMax_local,
                        GetSimulParam_GDDMethod(),
                    )
                    GDDays += DayGDD
                    RemainingDays -= 1
                    DayNri += 1

                    while (RemainingDays > 0) and ((DayNri < GetTemperatureRecord_ToDayNr()) or AdjustDayNri):
                        if DayNri > TminDataSet[31].DayNr:
                            TminDataSet, TmaxDataSet = GetDecadeTemperatureDataSet(
                                DayNri, TminDataSet, TmaxDataSet
                            )

                        i = 1
                        while TminDataSet[i].DayNr != DayNri:
                            i += 1

                        TDayMin_local = TminDataSet[i].Param
                        TDayMax_local = TmaxDataSet[i].Param

                        DayGDD = DegreesDay(
                            Tbase,
                            Tupper,
                            TDayMin_local,
                            TDayMax_local,
                            GetSimulParam_GDDMethod(),
                        )
                        GDDays += DayGDD
                        RemainingDays -= 1
                        DayNri += 1

                    if RemainingDays > 0:
                        GDDays = undef_int

                elif dt == datatype_Monthly:
                    TminDataSet, TmaxDataSet = GetMonthlyTemperatureDataSet(
                        DayNri, TminDataSet, TmaxDataSet
                    )

                    i = 1
                    while TminDataSet[i].DayNr != DayNri:
                        i += 1

                    TDayMin_local = TminDataSet[i].Param
                    TDayMax_local = TmaxDataSet[i].Param

                    DayGDD = DegreesDay(
                        Tbase,
                        Tupper,
                        TDayMin_local,
                        TDayMax_local,
                        GetSimulParam_GDDMethod(),
                    )
                    GDDays += DayGDD
                    RemainingDays -= 1
                    DayNri += 1

                    while (RemainingDays > 0) and ((DayNri < GetTemperatureRecord_ToDayNr()) or AdjustDayNri):
                        if DayNri > TminDataSet[31].DayNr:
                            TminDataSet, TmaxDataSet = GetMonthlyTemperatureDataSet(
                                DayNri, TminDataSet, TmaxDataSet
                            )

                        i = 1
                        while TminDataSet[i].DayNr != DayNri:
                            i += 1

                        TDayMin_local = TminDataSet[i].Param
                        TDayMax_local = TmaxDataSet[i].Param

                        DayGDD = DegreesDay(
                            Tbase,
                            Tupper,
                            TDayMin_local,
                            TDayMax_local,
                            GetSimulParam_GDDMethod(),
                        )
                        GDDays += DayGDD
                        RemainingDays -= 1
                        DayNri += 1

                    if RemainingDays > 0:
                        GDDays = undef_int

    else:
        GDDays = undef_int

    return int(roundc(GDDays, mold="int32"))


def GetParameters(C1: float, C2: float, C3: float, UL: float, LL: float, Mid: float):
    UL = (C1 + C2) / 2.0
    LL = (C2 + C3) / 2.0
    Mid = 2.0 * C2 - (UL + LL) / 2.0
    # --previous decade-->/UL/....... Mid ......../LL/<--next decade--
    return UL, LL, Mid


def GetSetofThree(
    DayN: int,
    Deci: int,
    Monthi: int,
    Yeari: int,
    C1Min: float,
    C1Max: float,
    C2Min: float,
    C2Max: float,
    C3Min: float,
    C3Max: float,
):
    # 1 = previous decade, 2 = Actual decade, 3 = Next decade

    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(GetTemperatureFileFull()).lstrip("/\\"),
        )
    )
    with open(full_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    idx = 0

    # Skip header lines
    idx += 8

    if GetTemperatureRecord_FromD() > 20:
        DecFile = 3
    elif GetTemperatureRecord_FromD() > 10:
        DecFile = 2
    else:
        DecFile = 1

    Mfile = GetTemperatureRecord_FromM()

    if GetTemperatureRecord_FromY() == 1901:
        Yfile = Yeari
    else:
        Yfile = GetTemperatureRecord_FromY()

    OK3 = False

    # Case NrObs <= 2
    if GetTemperatureRecord_NrObs() <= 2:
        StringREAD = lines[idx] if idx < len(lines) else ""
        idx += 1
        C1Min, C1Max = SplitStringInTwoParams(StringREAD, C1Min, C1Max)

        if GetTemperatureRecord_NrObs() == 0:
            C2Min = C1Min
            C3Min = C1Min
            C3Max = C1Max

        elif GetTemperatureRecord_NrObs() == 1:
            DecFile += 1
            if DecFile > 3:
                DecFile, Mfile, Yfile = AdjustDecadeMONTHandYEAR(DecFile, Mfile, Yfile)

            StringREAD = lines[idx] if idx < len(lines) else ""
            idx += 1
            C3Min, C3Max = SplitStringInTwoParams(StringREAD, C3Min, C3Max)

            if Deci == DecFile:
                C2Min, C2Max = C3Min, C3Max
                C3Min = C2Min + (C2Min - C1Min) / 4.0
                C3Max = C2Max + (C2Max - C1Max) / 4.0
            else:
                C2Min, C2Max = C1Min, C1Max
                C1Min = C2Min + (C2Min - C3Min) / 4.0
                C1Max = C2Max + (C2Max - C3Max) / 4.0

        OK3 = True

    if (not OK3) and (Deci == DecFile) and (Monthi == Mfile) and (Yeari == Yfile):
        StringREAD = lines[idx] if idx < len(lines) else ""
        idx += 1
        C1Min, C1Max = SplitStringInTwoParams(StringREAD, C1Min, C1Max)

        C2Min, C2Max = C1Min, C1Max

        StringREAD = lines[idx] if idx < len(lines) else ""
        idx += 1
        C3Min, C3Max = SplitStringInTwoParams(StringREAD, C3Min, C3Max)

        C1Min = C2Min + (C2Min - C3Min) / 4.0
        C1Max = C2Max + (C2Max - C3Max) / 4.0
        OK3 = True

    if (not OK3) and (DayN == GetTemperatureRecord_ToD()) and (Monthi == GetTemperatureRecord_ToM()):
        if (GetTemperatureRecord_FromY() == 1901) or (Yeari == GetTemperatureRecord_ToY()):
            skip_n = GetTemperatureRecord_NrObs() - 2
            if skip_n > 0:
                idx += skip_n

            StringREAD = lines[idx] if idx < len(lines) else ""
            idx += 1
            C1Min, C1Max = SplitStringInTwoParams(StringREAD, C1Min, C1Max)

            StringREAD = lines[idx] if idx < len(lines) else ""
            idx += 1
            C2Min, C2Max = SplitStringInTwoParams(StringREAD, C2Min, C2Max)

            C3Min = C2Min + (C2Min - C1Min) / 4.0
            C3Max = C2Max + (C2Max - C1Max) / 4.0
            OK3 = True

    if not OK3:
        Obsi = 1
        while not OK3:
            if (Deci == DecFile) and (Monthi == Mfile) and (Yeari == Yfile):
                OK3 = True
            else:
                DecFile += 1
                if DecFile > 3:
                    DecFile, Mfile, Yfile = AdjustDecadeMONTHandYEAR(DecFile, Mfile, Yfile)
                Obsi += 1

        if GetTemperatureRecord_FromD() > 20:
            DecFile = 3
        elif GetTemperatureRecord_FromD() > 10:
            DecFile = 2
        else:
            DecFile = 1

        skip_n = Obsi - 2
        if skip_n > 0:
            idx += skip_n

        StringREAD = lines[idx] if idx < len(lines) else ""
        idx += 1
        C1Min, C1Max = SplitStringInTwoParams(StringREAD, C1Min, C1Max)

        StringREAD = lines[idx] if idx < len(lines) else ""
        idx += 1
        C2Min, C2Max = SplitStringInTwoParams(StringREAD, C2Min, C2Max)

        StringREAD = lines[idx] if idx < len(lines) else ""
        idx += 1
        C3Min, C3Max = SplitStringInTwoParams(StringREAD, C3Min, C3Max)

    return C1Min, C1Max, C2Min, C2Max, C3Min, C3Max


def AdjustDecadeMONTHandYEAR(DecFile, Mfile, Yfile):
    DecFile = 1
    Mfile = Mfile + 1
    if Mfile > 12:
        Mfile = 1
        Yfile = Yfile + 1
    return DecFile, Mfile, Yfile


def GetDecadeTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet):
    # DayNri: int
    # TminDataSet, TmaxDataSet: list/array of length 31 with elements having .DayNr and .Param

    Dayi, Monthi, Yeari = DetermineDate(DayNri)

    if Dayi > 20:
        Deci = 3
        Dayi = 21
        DayN = DaysInMonth[Monthi - 1]
        if (Monthi == 2) and LeapYear(Yeari):
            DayN = DayN + 1
        ni = DayN - Dayi + 1
    elif Dayi > 10:
        Deci = 2
        Dayi = 11
        DayN = 20
        ni = 10
    else:
        Deci = 1
        Dayi = 1
        DayN = 10
        ni = 10

    (C1Min, C1Max, C2Min, C2Max, C3Min, C3Max) = GetSetofThree(
        DayN, Deci, Monthi, Yeari,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    )

    DNR = DetermineDayNr(Dayi, Monthi, Yeari)

    ULMin, LLMin, MidMin = GetParameters(C1Min, C2Min, C3Min, 0.0, 0.0, 0.0)

    for Nri in range(1, ni + 1):
        idx = Nri - 1  # Fortran 1-based -> Python 0-based
        TminDataSet[idx].DayNr = DNR + Nri - 1

        if Nri <= (ni / 2.0 + 0.01):
            TminDataSet[idx].Param = (
                2.0 * ULMin
                + (MidMin - ULMin) * (2.0 * Nri - 1.0) / (ni / 2.0)
            ) / 2.0
        else:
            if ((ni == 11) or (ni == 9)) and (Nri < (ni + 1.01) / 2.0):
                TminDataSet[idx].Param = MidMin
            else:
                TminDataSet[idx].Param = (
                    2.0 * MidMin
                    + (LLMin - MidMin) * (2.0 * Nri - (ni + 1)) / (ni / 2.0)
                ) / 2.0

    ULMax, LLMax, MidMax = GetParameters(C1Max, C2Max, C3Max, 0.0, 0.0, 0.0)

    for Nri in range(1, ni + 1):
        idx = Nri - 1  # Fortran 1-based -> Python 0-based
        TmaxDataSet[idx].DayNr = DNR + Nri - 1

        if Nri <= (ni / 2.0 + 0.01):
            TmaxDataSet[idx].Param = (
                2.0 * ULMax
                + (MidMax - ULMax) * (2.0 * Nri - 1.0) / (ni / 2.0)
            ) / 2.0
        else:
            if ((ni == 11) or (ni == 9)) and (Nri < (ni + 1.01) / 2.0):
                TmaxDataSet[idx].Param = MidMax
            else:
                TmaxDataSet[idx].Param = (
                    2.0 * MidMax
                    + (LLMax - MidMax) * (2.0 * Nri - (ni + 1)) / (ni / 2.0)
                ) / 2.0

    for Nri in range(ni + 1, 31 + 1):
        idx = Nri - 1
        TminDataSet[idx].DayNr = DNR + ni - 1
        TminDataSet[idx].Param = 0.0
        TmaxDataSet[idx].DayNr = DNR + ni - 1
        TmaxDataSet[idx].Param = 0.0

    return TminDataSet, TmaxDataSet









def GetFileDescription(TheFileFullName: str, TheDescription: str) -> str:
    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(TheFileFullName).lstrip("/\\"),
        )
    )

    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            with open(full_path, "r", encoding=enc) as f0:
                line = f0.readline()
            return line.strip()
        except UnicodeDecodeError:
            pass

    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        line = f0.readline()

    return line.strip()







def fTnxReference365Days_open(filename: str, mode: str):
    global fTnxReference365Days

    full_path = ResolvePath(filename)
    fTnxReference365Days = open_file(full_path, mode)

def fTnxReference365Days_write(line, advance_in=None):
    # Writes the given line to the fTnxReference365Days file.
    global fTnxReference365Days

    advance = True if advance_in is None else bool(advance_in)

    try:
        s = "" if line is None else str(line)
        s = s.rstrip("\n")  # emula '(a)' sin duplicar saltos
        if advance:
            fTnxReference365Days.write(s + "\n")
        else:
            fTnxReference365Days.write(s)
        fTnxReference365Days.flush()
    except OSError:
        pass


def fTnxReference365Days_close():
    global fTnxReference365Days

    if fTnxReference365Days is None:
        return

    try:
        fTnxReference365Days.flush()
    except OSError:
        pass

    try:
        fTnxReference365Days.close()
    except OSError:
        pass

    fTnxReference365Days = None



def CreateTnxReference365Days():
    totalnameOUT = ""
    TempString = ""
    TminDataSet_temp = [rep_DayEventDbl() for _ in range(31)]
    TmaxDataSet_temp = [rep_DayEventDbl() for _ in range(31)]
    Tlow = 0.0
    Thigh = 0.0

    TnxReferenceFilefull_exists = FileExists(
        ResolvePath(GetTnxReferenceFileFull())
    )

    if TnxReferenceFilefull_exists or (GetTnxReferenceFile() == "(External)"):
        # create SIM file
        if GetTnxReferenceFile() != "(External)":
            totalnameOUT = GetPathNameSimul().strip() + "TnxReference365Days.SIM"
            fTnxReference365Days_open(totalnameOUT, "w")

        # get data set for 1st month
        Monthi = 1
        TminDataSet_temp, TmaxDataSet_temp = GetMonthlyTemperatureDataSetFromTnxReferenceFile(
            Monthi, TminDataSet_temp, TmaxDataSet_temp
        )

        # Tnx for Day 1 to 365
        for DayNri in range(1, 366):
            if DayNri > TminDataSet_temp[30].DayNr:
                # next month
                Monthi = Monthi + 1
                TminDataSet_temp, TmaxDataSet_temp = GetMonthlyTemperatureDataSetFromTnxReferenceFile(
                    Monthi, TminDataSet_temp, TmaxDataSet_temp
                )

            i = 1
            while TminDataSet_temp[i - 1].DayNr != DayNri:
                i = i + 1

            Tlow = float(roundc(100.0 * TminDataSet_temp[i - 1].Param, mold="int32")) / 100.0
            Thigh = float(roundc(100.0 * TmaxDataSet_temp[i - 1].Param, mold="int32")) / 100.0

            SetTminTnxReference365DaysRun_i(DayNri, Tlow)
            SetTmaxTnxReference365DaysRun_i(DayNri, Thigh)

            if GetTnxReferenceFile() != "(External)":
                TempString = f"{Tlow:10.2f}{Thigh:10.2f}"
                fTnxReference365Days_write(TempString.rstrip())

        if GetTnxReferenceFile() != "(External)":
            fTnxReference365Days_close()
            if os.environ.get("AQUACROP_DEBUG_TRACE", "").strip():
                full_preview_path = os.path.normpath(
                    ResolvePath(totalnameOUT)
                )
                from .debugtrace import append_file_preview
                append_file_preview(
                    complete_path_dir,
                    "TnxReference365Days.SIM",
                    full_preview_path,
                )



def ReadTemperatureFileFull():
    # Reads the contents of the TemperatureFilefull file,
    # storing the temperatures in the Tmin and Tmax arrays.

    global Tmin, Tmax

    filename = GetTemperatureFileFull()

    full_path = ResolvePath(filename)

    with open(full_path, "r", encoding="utf-8") as fhandle:
        lines = fhandle.read().splitlines()

    # Count the number of lines
    nlines = len(lines)

    # Now read in the actual content
    nrows = nlines - 8

    Tmin = np.empty(nrows, dtype=float)
    Tmax = np.empty(nrows, dtype=float)

    # description
    # time step
    # day
    # month
    # year
    # (3 extra header lines)
    data_lines = lines[8:8 + nrows]

    for i, line in enumerate(data_lines):
        parts = line.split()
        Tmin[i] = float(parts[0])
        Tmax[i] = float(parts[1])

def CreateTnxReferenceFile(TemperatureFile: str, TnxReferenceFile: str, TnxReferenceYear: int):
    # real(dp), dimension(12) :: MonthVal1, MonthVal2
    MonthVal1 = [0.0] * 12
    MonthVal2 = [0.0] * 12

    # character(len=:), allocatable :: FullName
    FullName = ""

    # integer(int32)   :: fhandle, rc
    fhandle = None
    rc = 0

    # integer(int32) :: i, NrYears
    i = 0
    NrYears = 0

    # integer(int32) :: Yeari, Monthi, MonthDays, MonthDecs, Deci, Dayi
    Yeari = Monthi = MonthDays = MonthDecs = Deci = Dayi = 0

    # real(dp) :: SUM1, SUM2, Val1, Val2
    SUM1 = SUM2 = Val1 = Val2 = 0.0

    # integer(int32) :: DayNri, EndDayNr
    DayNri = 0
    EndDayNr = undef_int

    # logical :: EndMonth
    EndMonth = False

    # integer(int32), dimension(12) :: MonthNrYears
    MonthNrYears = [0] * 12

    # character(len=:), allocatable :: TempString
    TempString = ""

    # character(len=1025) :: TempString2
    TempString2 = ""

    # 1a. Delete existing TnxReferenceFile and adjust TnxReferenceYear
    FullName = GetPathNameSimul().strip() + _strip_quotes(TnxReferenceFile).strip()
    full_path = ResolvePath(FullName)

    if FileExists(full_path):
        try:
            os.remove(full_path)  # unlink
        except OSError:
            pass
        SetTnxReferenceYear(2000)

    # 1b. Delete existing TnxReference365Days.SIM
    FullName = GetPathNameSimul().strip() + "TnxReference365Days.SIM"
    full_path = ResolvePath(FullName)
    if FileExists(full_path):
        try:
            os.remove(full_path)  # unlink
        except OSError:
            pass

    # 1c. Delete existing TCropReference.SIM
    FullName = GetPathNameSimul().strip() + "TCropReference.SIM"
    full_path = ResolvePath(FullName)
    if FileExists(full_path):
        try:
            os.remove(full_path)  # unlink
        except OSError:
            pass

    # 2. Get Mean monthly data
    if TemperatureFile != "(None)":
        # 2.a Preparation
        # Get Number of Years
        NrYears = GetTemperatureRecord_ToY() - GetTemperatureRecord_FromY() + 1
        # Get TnxReferenceYear
        SetTnxReferenceYear(
            roundc(
                (GetTemperatureRecord_FromY() + GetTemperatureRecord_ToY()) / 2.0,
                mold=1,
            )
        )
        if GetTnxReferenceYear() == 1901:
            SetTnxReferenceYear(2000)

        # check number of years for each month
        MonthNrYears = [NrYears] * 12
        if NrYears > 1:
            if GetTemperatureRecord_FromM() > 1:
                for Monthi in range(1, GetTemperatureRecord_FromM()):
                    MonthNrYears[Monthi - 1] = MonthNrYears[Monthi - 1] - 1

            if GetTemperatureRecord_ToM() < 12:
                for Monthi in range(12, GetTemperatureRecord_ToM(), -1):
                    MonthNrYears[Monthi - 1] = MonthNrYears[Monthi - 1] - 1

        # initialize
        MonthVal1 = [0.0] * 12  # Tmin data
        MonthVal2 = [0.0] * 12  # Tmax data

        Yeari = GetTemperatureRecord_FromY()
        Monthi = GetTemperatureRecord_FromM()
        DayNri = GetTemperatureRecord_FromDayNr()
        EndMonth = False
        EndDayNr = undef_int
        Deci = undef_int
        SUM1 = 0.0
        SUM2 = 0.0
        MonthDays = 0
        MonthDecs = 0

        # select case (GetTemperatureRecord_DataType())
        if GetTemperatureRecord_DataType() == datatype_Daily:
            # EndDayNr = DayNr of last day in month
            Dayi = DaysInMonth[Monthi - 1]
            if (LeapYear(Yeari) is True) and (Monthi == 2):
                Dayi = Dayi + 1
            EndDayNr = DetermineDayNr(Dayi, Monthi, Yeari)

        # open temperature file + skip header (8 lines)
        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(GetTemperatureFileFull()).lstrip("/\\"),
            )
        )
        with open(full_path, "r", encoding="utf-8", errors="replace") as fhandle:
            lines = fhandle.read().splitlines()

        # Description, Data type, Day, Month, Year, Title x3
        data_lines = lines[8:] if len(lines) > 8 else []

        # 2.b Determine mean monthly data
        for line in data_lines:
            parts = line.split()
            if len(parts) < 2:
                continue

            Val1 = float(parts[0])  # Tmin
            Val2 = float(parts[1])  # Tmax

            SUM1 = SUM1 + Val1
            SUM2 = SUM2 + Val2

            # check end of month
            dtype = GetTemperatureRecord_DataType()

            if dtype == datatype_Daily:
                MonthDays = MonthDays + 1
                if DayNri == EndDayNr:
                    EndMonth = True

            elif dtype == datatype_Decadely:
                MonthDecs = MonthDecs + 1
                if Deci == 3:
                    EndMonth = True

            else:  # datatype_monthly
                EndMonth = True

            # End of Month
            if EndMonth is True:
                # mean monthly values Tmin and Tmax
                if dtype == datatype_Daily:
                    SUM1 = SUM1 / float(MonthDays)
                    SUM2 = SUM2 / float(MonthDays)
                elif dtype == datatype_Decadely:
                    SUM1 = SUM1 / float(MonthDecs)
                    SUM2 = SUM2 / float(MonthDecs)

                MonthVal1[Monthi - 1] = MonthVal1[Monthi - 1] + (SUM1 / float(MonthNrYears[Monthi - 1]))
                MonthVal2[Monthi - 1] = MonthVal2[Monthi - 1] + (SUM2 / float(MonthNrYears[Monthi - 1]))

                # Next month
                SUM1 = 0.0
                SUM2 = 0.0
                if Monthi == 12:
                    Monthi = 1
                    Yeari = Yeari + 1
                else:
                    Monthi = Monthi + 1

                EndMonth = False

                if dtype == datatype_Daily:
                    # EndDayNr = DayNr of last day in month
                    MonthDays = 0
                    Dayi = DaysInMonth[Monthi - 1]
                    if (LeapYear(Yeari) is True) and (Monthi == 2):
                        Dayi = Dayi + 1
                    EndDayNr = DetermineDayNr(Dayi, Monthi, Yeari)

                elif dtype == datatype_Decadely:
                    MonthDecs = 0
                    Deci = 0

            # Next day, decade, month
            if dtype == datatype_Daily:
                DayNri = DayNri + 1

    # 3. Create and Save TnxReference File
    if TemperatureFile != "(None)":
        # Determine Name of TnxReference File
        i = len(TemperatureFile.strip())
        TempString = TemperatureFile.strip()
        SetTnxReferenceFile(TempString[: i - 4] + "Reference.Tnx")

        FullName = GetPathNameSimul().strip() + GetTnxReferenceFile()
        SetTnxReferenceFileFull(FullName)

        # Save mean monthly data (minimize disk writes)
        lines = []
        lines.append("Reference : " + GetTemperatureDescription().strip())
        lines.append("     3  : Monthly records (1=daily, 2=10-daily and 3=monthly data)")
        lines.append("     1  : First day of record (1, 11 or 21 for 10-day or 1 for months)")
        lines.append("     1  : First month of record")
        lines.append("  1901  : First year of record (1901 if not linked to a specific year)")
        lines.append("")
        lines.append("  Tmin (C)   TMax (C) ")
        lines.append("  =======================")

        for Monthi in range(1, 13):
            # Fortran: write(TempString2,'(2f10.2)') MonthVal1(Monthi), MonthVal2(Monthi)
            TempString2 = f"{MonthVal1[Monthi - 1]:10.2f}{MonthVal2[Monthi - 1]:10.2f}"
            lines.append(TempString2.strip())

            # Fortran rounding: round to 2 decimals via *100, roundc, /100
            SetTminTnxReference12MonthsRun_i(
                Monthi,
                round(100.0 * MonthVal1[Monthi - 1]) / 100.0,
            )
            SetTmaxTnxReference12MonthsRun_i(
                Monthi,
                round(100.0 * MonthVal2[Monthi - 1]) / 100.0,
            )

        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(FullName).lstrip("/\\"),
            )
        )
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8", errors="replace") as f0:
            f0.write("\n".join(lines) + "\n")

            
def GetMonthlyTemperatureDataSetFromTnxReferenceFile(Monthi, TminDataSet, TmaxDataSet):
    # integer(int32), intent(in) :: Monthi
    # type(rep_DayEventDbl), dimension(31), intent(inout) :: TminDataSet, TmaxDataSet

    ni = 30

    if Monthi == 1:
        C1Min = GetTminTnxReference12MonthsRun_i(12)
        C1Max = GetTmaxTnxReference12MonthsRun_i(12)
    else:
        C1Min = GetTminTnxReference12MonthsRun_i(Monthi - 1)
        C1Max = GetTmaxTnxReference12MonthsRun_i(Monthi - 1)

    C2Min = GetTminTnxReference12MonthsRun_i(Monthi)
    C2Max = GetTmaxTnxReference12MonthsRun_i(Monthi)

    if Monthi == 12:
        C3Min = GetTminTnxReference12MonthsRun_i(1)
        C3Max = GetTmaxTnxReference12MonthsRun_i(1)
    else:
        C3Min = GetTminTnxReference12MonthsRun_i(Monthi + 1)
        C3Max = GetTmaxTnxReference12MonthsRun_i(Monthi + 1)

    C1Min = C1Min * ni
    C1Max = C1Max * ni
    C2Min = C2Min * ni
    C2Max = C2Max * ni
    C3Min = C3Min * ni
    C3Max = C3Max * ni

    DNR = DetermineDayNr(1, Monthi, 1901)
    DayN = DaysInMonth[Monthi - 1]  # equivalente a DaysInMonth(Monthi)

    aOver3Min, bOver2Min, cMin = GetInterpolationParameters(C1Min, C2Min, C3Min, 0.0, 0.0, 0.0)
    aOver3Max, bOver2Max, cMax = GetInterpolationParameters(C1Max, C2Max, C3Max, 0.0, 0.0, 0.0)

    t1 = 30
    for Dayi in range(1, DayN + 1):
        t2 = t1 + 1

        idx = Dayi - 1
        TminDataSet[idx].DayNr = DNR + Dayi - 1
        TmaxDataSet[idx].DayNr = DNR + Dayi - 1

        TminDataSet[idx].Param = (
            aOver3Min * (t2 * t2 * t2 - t1 * t1 * t1)
            + bOver2Min * (t2 * t2 - t1 * t1)
            + cMin * (t2 - t1)
        )
        TmaxDataSet[idx].Param = (
            aOver3Max * (t2 * t2 * t2 - t1 * t1 * t1)
            + bOver2Max * (t2 * t2 - t1 * t1)
            + cMax * (t2 - t1)
        )

        t1 = t2

    # Give remaining days (day 29/30/31) the DayNr of the last day of the month
    for Dayi in range(DayN + 1, 32):  # 31 inclusive
        idx = Dayi - 1
        TminDataSet[idx].DayNr = DNR + DayN - 1
        TmaxDataSet[idx].DayNr = DNR + DayN - 1
        TminDataSet[idx].Param = 0.0
        TmaxDataSet[idx].Param = 0.0

    return TminDataSet, TmaxDataSet



def GetInterpolationParameters(C1: float, C2: float, C3: float, aOver3: float, bOver2: float, c: float):
    # n1=n2=n3=30 --> better parabola
    aOver3 = (C1 - 2.0 * C2 + C3) / (6.0 * 30.0 * 30.0 * 30.0)
    bOver2 = (-6.0 * C1 + 9.0 * C2 - 3.0 * C3) / (6.0 * 30.0 * 30.0)
    c = (11.0 * C1 - 7.0 * C2 + 2.0 * C3) / (6.0 * 30.0)
    return aOver3, bOver2, c


def ReadMonth(CiMin, CiMax, fhandle, rc):
    ni = 30

    StringREAD = fhandle.readline()
    if StringREAD == "":
        return CiMin, CiMax, rc

    CiMin, CiMax = SplitStringInTwoParams(StringREAD, CiMin, CiMax)

    # simplification give better results for all cases
    CiMin = CiMin * ni
    CiMax = CiMax * ni

    return CiMin, CiMax, rc


def GetSetofThreeMonths(
    Monthi,
    Yeari,
    C1Min,
    C2Min,
    C3Min,
    C1Max,
    C2Max,
    C3Max,
    X1,
    X2,
    X3,
    t1,
):
    n1 = 30
    n2 = 30
    n3 = 30

    Mfile = 0
    Yfile = 0
    Nri = 0
    Obsi = 0
    rc = 0
    OK3 = False

    # 1. Prepare record
    name = _strip_quotes(GetTemperatureFileFull()).strip()
    full_path = ResolvePath(name)

    with open(full_path, "r", encoding="utf-8") as fhandle:
        fhandle.readline()  # description
        fhandle.readline()  # time step
        fhandle.readline()  # day
        fhandle.readline()  # month
        fhandle.readline()  # year
        fhandle.readline()
        fhandle.readline()
        fhandle.readline()

        Mfile = GetTemperatureRecord_FromM()
        if GetTemperatureRecord_FromY() == 1901:
            Yfile = Yeari
        else:
            Yfile = GetTemperatureRecord_FromY()

        OK3 = False

        # 2. IF 3 or less records
        if GetTemperatureRecord_NrObs() <= 3:
            C1Min, C1Max, rc = ReadMonth(C1Min, C1Max, fhandle, rc)
            X1 = n1

            nr_obs = GetTemperatureRecord_NrObs()

            if nr_obs == 0:
                t1 = X1
                X2 = X1 + n1
                C2Min = C1Min
                C2Max = C1Max
                X3 = X2 + n1
                C3Min = C1Min
                C3Max = C1Max

            elif nr_obs == 1:
                t1 = X1
                Mfile = Mfile + 1
                if Mfile > 12:
                    Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

                C3Min, C3Max, rc = ReadMonth(C3Min, C3Max, fhandle, rc)

                if Monthi == Mfile:
                    C2Min = C3Min
                    C2Max = C3Max
                    X2 = X1 + n3
                    X3 = X2 + n3
                else:
                    C2Min = C1Min
                    C2Max = C1Max
                    X2 = X1 + n1
                    X3 = X2 + n3

            elif nr_obs == 2:
                if Monthi == Mfile:
                    t1 = 0

                Mfile = Mfile + 1
                if Mfile > 12:
                    Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

                C2Min, C2Max, rc = ReadMonth(C2Min, C2Max, fhandle, rc)
                X2 = X1 + n2

                if Monthi == Mfile:
                    t1 = X1

                Mfile = Mfile + 1
                if Mfile > 12:
                    Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

                C3Min, C3Max, rc = ReadMonth(C3Min, C3Max, fhandle, rc)
                X3 = X2 + n3

                if Monthi == Mfile:
                    t1 = X2

            OK3 = True

        # 3. If first observation
        if (not OK3) and ((Monthi == Mfile) and (Yeari == Yfile)):
            t1 = 0
            C1Min, C1Max, rc = ReadMonth(C1Min, C1Max, fhandle, rc)
            X1 = n1

            Mfile = Mfile + 1
            if Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

            C2Min, C2Max, rc = ReadMonth(C2Min, C2Max, fhandle, rc)
            X2 = X1 + n2

            Mfile = Mfile + 1
            if Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

            C3Min, C3Max, rc = ReadMonth(C3Min, C3Max, fhandle, rc)
            X3 = X2 + n3

            OK3 = True

        # 4. If last observation
        if (not OK3) and (Monthi == GetTemperatureRecord_ToM()):
            if (GetTemperatureRecord_FromY() == 1901) or (Yeari == GetTemperatureRecord_ToY()):
                for Nri in range(1, (GetTemperatureRecord_NrObs() - 3) + 1):
                    fhandle.readline()
                    Mfile = Mfile + 1
                    if Mfile > 12:
                        Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

                C1Min, C1Max, rc = ReadMonth(C1Min, C1Max, fhandle, rc)
                X1 = n1

                Mfile = Mfile + 1
                if Mfile > 12:
                    Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

                C2Min, C2Max, rc = ReadMonth(C2Min, C2Max, fhandle, rc)
                X2 = X1 + n2
                t1 = X2

                Mfile = Mfile + 1
                if Mfile > 12:
                    Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

                C3Min, C3Max, rc = ReadMonth(C3Min, C3Max, fhandle, rc)
                X3 = X2 + n3

                OK3 = True

        # 5. IF not previous cases
        if not OK3:
            Obsi = 1
            while not OK3:
                if (Monthi == Mfile) and (Yeari == Yfile):
                    OK3 = True
                else:
                    Mfile = Mfile + 1
                    if Mfile > 12:
                        Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
                    Obsi = Obsi + 1

            Mfile = GetTemperatureRecord_FromM()

            for Nri in range(1, (Obsi - 2) + 1):
                fhandle.readline()
                Mfile = Mfile + 1
                if Mfile > 12:
                    Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

            C1Min, C1Max, rc = ReadMonth(C1Min, C1Max, fhandle, rc)
            X1 = n1
            t1 = X1

            Mfile = Mfile + 1
            if Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

            C2Min, C2Max, rc = ReadMonth(C2Min, C2Max, fhandle, rc)
            X2 = X1 + n2

            Mfile = Mfile + 1
            if Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)

            C3Min, C3Max, rc = ReadMonth(C3Min, C3Max, fhandle, rc)
            X3 = X2 + n3

    return C1Min, C2Min, C3Min, C1Max, C2Max, C3Max, X1, X2, X3, t1


def AdjustMONTHandYEAR(Mfile: int, Yfile: int):
    Mfile = Mfile - 12
    Yfile = Yfile + 1
    return Mfile, Yfile

def GetMonthlyTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet):
    Dayi, Monthi, Yeari = DetermineDate(DayNri)

    C1Min = 0.0
    C2Min = 0.0
    C3Min = 0.0
    C1Max = 0.0
    C2Max = 0.0
    C3Max = 0.0
    X1 = 0
    X2 = 0
    X3 = 0
    t1 = 0
    t2 = 0

    (
        C1Min,
        C2Min,
        C3Min,
        C1Max,
        C2Max,
        C3Max,
        X1,
        X2,
        X3,
        t1,
    ) = GetSetofThreeMonths(
        Monthi,
        Yeari,
        C1Min,
        C2Min,
        C3Min,
        C1Max,
        C2Max,
        C3Max,
        X1,
        X2,
        X3,
        t1,
    )

    Dayi = 1
    DNR = DetermineDayNr(Dayi, Monthi, Yeari)

    DayN = DaysInMonth[Monthi - 1]
    if (Monthi == 2) and LeapYear(Yeari):
        DayN = DayN + 1

    aOver3Min, bOver2Min, cMin = GetInterpolationParameters(
        C1Min, C2Min, C3Min, 0.0, 0.0, 0.0
    )
    aOver3Max, bOver2Max, cMax = GetInterpolationParameters(
        C1Max, C2Max, C3Max, 0.0, 0.0, 0.0
    )

    for Dayi in range(1, DayN + 1):
        t2 = t1 + 1

        if TminDataSet[Dayi] is None:
            TminDataSet[Dayi] = rep_DayEventDbl(DayNr=0, Param=0.0)
        if TmaxDataSet[Dayi] is None:
            TmaxDataSet[Dayi] = rep_DayEventDbl(DayNr=0, Param=0.0)

        TminDataSet[Dayi].DayNr = DNR + Dayi - 1
        TmaxDataSet[Dayi].DayNr = DNR + Dayi - 1

        TminDataSet[Dayi].Param = (
            aOver3Min * (t2 * t2 * t2 - t1 * t1 * t1)
            + bOver2Min * (t2 * t2 - t1 * t1)
            + cMin * (t2 - t1)
        )
        TmaxDataSet[Dayi].Param = (
            aOver3Max * (t2 * t2 * t2 - t1 * t1 * t1)
            + bOver2Max * (t2 * t2 - t1 * t1)
            + cMax * (t2 - t1)
        )

        t1 = t2

    last_daynr = DNR + DayN - 1
    for Dayi in range(DayN + 1, 31 + 1):
        if TminDataSet[Dayi] is None:
            TminDataSet[Dayi] = rep_DayEventDbl(DayNr=0, Param=0.0)
        if TmaxDataSet[Dayi] is None:
            TmaxDataSet[Dayi] = rep_DayEventDbl(DayNr=0, Param=0.0)

        TminDataSet[Dayi].DayNr = last_daynr
        TmaxDataSet[Dayi].DayNr = last_daynr
        TminDataSet[Dayi].Param = 0.0
        TmaxDataSet[Dayi].Param = 0.0

    return TminDataSet, TmaxDataSet









def fTnxReference_write(line: str, advance_in: Optional[bool] = None):
    global fTnxReference
    if fTnxReference is None:
        return

    advance = True if advance_in is None else bool(advance_in)

    s = "" if line is None else str(line)
    s = s.rstrip("\n")

    if advance:
        fTnxReference.write(s + "\n")
    else:
        fTnxReference.write(s)

def fTnxReference_write_bulk(items, default_advance: bool = True):
    global fTnxReference
    if fTnxReference is None:
        return

    chunks = []
    for it in items:
        if isinstance(it, tuple):
            line, adv = it
        else:
            line, adv = it, default_advance

        s = "" if line is None else str(line)
        s = s.rstrip("\n")

        chunks.append(s + ("\n" if adv else ""))

    fTnxReference.write("".join(chunks))


def AdjustYearPerennials(
    TheYearSeason: int,
    Sown1stYear: bool,
    TheCycleMode: int,
    Zmax: float,
    ZminYear1: float,
    TheCCo: float,
    TheSizeSeedling: float,
    TheCGC: float,
    TheCCx: float,
    TheGDDCGC: float,
    ThePlantingDens: int,
    TypeOfPlanting: int,
    Zmin: float,
    TheSizePlant: float,
    TheCCini: float,
    TheDaysToCCini: int,
    TheGDDaysToCCini: int,
):
    # NOTE:
    # - Fortran uses inout args; in Python we return the updated values.
    # - Constants/funcs assumed to exist: plant_seed, plant_transplant, plant_regrowth,
    #   modeCycle_GDDays, undef_int, roundc, TimeToCCini.

    if TheYearSeason == 1:
        # planting year
        if Sown1stYear is True:
            TypeOfPlanting = plant_Seed
        else:
            TypeOfPlanting = plant_transplant
        Zmin = ZminYear1  # rooting depth
    else:
        # non-seeding/planting year
        TypeOfPlanting = plant_regrowth
        Zmin = Zmax

        # plant size by regrowth
        if roundc(100.0 * TheSizePlant, mold="int32") < roundc(100.0 * TheSizeSeedling, mold="int32"):
            TheSizePlant = 10.0 * TheSizeSeedling

        if roundc(100.0 * TheSizePlant, mold="int32") > roundc(
            (100.0 * TheCCx * 10000.0) / (ThePlantingDens / 10000.0),
            mold="int32",
        ):
            # adjust size plant to maximum possible
            TheSizePlant = (TheCCx * 10000.0) / (ThePlantingDens / 10000.0)

    TheCCini = (ThePlantingDens / 10000.0) * (TheSizePlant / 10000.0)

    TheDaysToCCini = TimeToCCini(
        TypeOfPlanting,
        ThePlantingDens,
        TheSizeSeedling,
        TheSizePlant,
        TheCCx,
        TheCGC,
    )

    if TheCycleMode == ModeCycle_GDDays:
        TheGDDaysToCCini = TimeToCCini(
            TypeOfPlanting,
            ThePlantingDens,
            TheSizeSeedling,
            TheSizePlant,
            TheCCx,
            TheGDDCGC,
        )
    else:
        TheGDDaysToCCini = undef_int

    return TypeOfPlanting, Zmin, TheSizePlant, TheCCini, TheDaysToCCini, TheGDDaysToCCini


def SetDayNrToYundef(DayNri: int) -> int:
    Dayi = 0
    Monthi = 0
    Yeari = 0

    Dayi, Monthi, Yeari = DetermineDate(DayNri)
    Yeari = 1901
    DayNri = DetermineDayNr(Dayi, Monthi, Yeari)

    return DayNri

import math

def CropStressParametersSoilSalinity(
    CCxRed: int,
    CCdistortion: int,
    CCo: float,
    CCx: float,
    CGC: float,
    GDDCGC: float,
    CropDeterm: bool,
    L12: int,
    LFlor: int,
    LengthFlor: int,
    L123: int,
    GDDL12: int,
    GDDLFlor: int,
    GDDLengthFlor: int,
    GDDL123: int,
    TheModeCycle: int,
    StressResponse,
):
    # initialize
    StressResponse.RedCCX = int(CCxRed)
    StressResponse.RedWP = 0
    L12Double = float(L12)
    L12SSmax = float(L12)
    GDDL12Double = float(GDDL12)

    # CGC reduction
    CCToReach = 0.98 * CCx
    if (CCo > CCToReach) or (CCo >= CCx) or (CCxRed == 0):
        StressResponse.RedCGC = 0
    else:
        StressResponse.RedCGC = undef_int

        # reference for no salinity stress
        if TheModeCycle == ModeCycle_CalendarDays:
            num = (0.25 * CCx * CCx / CCo)
            den = (CCx - CCToReach)
            if abs(CGC) <= epsilon(1.0) or abs(den) <= epsilon(1.0):
                L12Double = 0.0
                StressResponse.RedCGC = 0
            else:
                L12Double = math.log(num / den) / CGC
                if L12Double <= epsilon(1.0):
                    StressResponse.RedCGC = 0
        else:
            num = (0.25 * CCx * CCx / CCo)
            den = (CCx - CCToReach)
            if abs(GDDCGC) <= epsilon(1.0) or abs(den) <= epsilon(1.0):
                GDDL12Double = 0.0
                StressResponse.RedCGC = 0
            else:
                GDDL12Double = math.log(num / den) / GDDCGC
                if GDDL12Double <= epsilon(1.0):
                    StressResponse.RedCGC = 0

        # with salinity stress
        CCxAdj = 0.90 * CCx * (1.0 - CCxRed / 100.0)
        CCToReach = 0.98 * CCxAdj

        if (StressResponse.RedCGC != 0) and ((CCxAdj - CCToReach) >= 0.0001):
            if TheModeCycle == ModeCycle_CalendarDays:
                num = (0.25 * CCxAdj * CCxAdj / CCo)
                den = (CCxAdj - CCToReach)
                if abs(L12Double) <= epsilon(1.0) or abs(den) <= epsilon(1.0):
                    StressResponse.RedCGC = 0
                else:
                    CGCadjMax = math.log(num / den) / L12Double

                    L12SSmax = L12 + (L123 - L12) / 2.0
                    if CropDeterm and (L12SSmax > (LFlor + roundc(LengthFlor / 2.0, mold="int32"))):
                        L12SSmax = LFlor + roundc(LengthFlor / 2.0, mold="int32")

                    if L12SSmax > L12Double:
                        CGCAdjMin = math.log(num / den) / L12SSmax
                    else:
                        CGCAdjMin = CGCadjMax

                    if CCxRed < 10:  # smooth start required
                        CGCadj = CGCadjMax - (CGCadjMax - CGCAdjMin) * (
                            math.exp(CCxRed * math.log(1.5)) / math.exp(10.0 * math.log(1.5))
                        ) * (CCdistortion / 100.0)
                    else:
                        CGCadj = CGCadjMax - (CGCadjMax - CGCAdjMin) * (CCdistortion / 100.0)

                    if abs(CGC) <= epsilon(1.0):
                        StressResponse.RedCGC = 0
                    else:
                        StressResponse.RedCGC = int(roundc(100.0 * (CGC - CGCadj) / CGC, mold="int8"))
            else:
                num = (0.25 * CCxAdj * CCxAdj / CCo)
                den = (CCxAdj - CCToReach)
                if abs(GDDL12Double) <= epsilon(1.0) or abs(den) <= epsilon(1.0):
                    StressResponse.RedCGC = 0
                else:
                    GDDCGCadjMax = math.log(num / den) / GDDL12Double

                    GDDL12SSmax = GDDL12 + (GDDL123 - GDDL12) / 2.0
                    if CropDeterm and (GDDL12SSmax > (GDDLFlor + roundc(LengthFlor / 2.0, mold="int32"))):
                        GDDL12SSmax = GDDLFlor + roundc(GDDLengthFlor / 2.0, mold="int32")

                    if GDDL12SSmax > GDDL12Double:
                        GDDCGCAdjMin = math.log(num / den) / GDDL12SSmax
                    else:
                        GDDCGCAdjMin = GDDCGCadjMax

                    if CCxRed < 10:  # smooth start required
                        GDDCGCadj = GDDCGCadjMax - (GDDCGCadjMax - GDDCGCAdjMin) * (
                            math.exp(float(CCxRed)) / math.exp(10.0)
                        ) * (CCdistortion / 100.0)
                    else:
                        GDDCGCadj = GDDCGCadjMax - (GDDCGCadjMax - GDDCGCAdjMin) * (CCdistortion / 100.0)

                    if abs(GDDCGC) <= epsilon(1.0):
                        StressResponse.RedCGC = 0
                    else:
                        StressResponse.RedCGC = int(roundc(100.0 * (GDDCGC - GDDCGCadj) / GDDCGC, mold="int8"))
        else:
            StressResponse.RedCGC = 0

    # Canopy decline
    if CCxRed == 0:
        StressResponse.CDecline = 0.0
    else:
        CCxAdj = 0.98 * CCx * (1.0 - CCxRed / 100.0)
        L12SS = L12SSmax - (L12SSmax - L12Double) * (CCdistortion / 100.0)

        if (L123 > L12SS) and (CCdistortion > 0):
            if CCxRed < 10:  # smooth start required
                CCxFinal = CCxAdj - (
                    math.exp(CCxRed * math.log(1.5)) / math.exp(10.0 * math.log(1.5))
                ) * (0.5 * CCdistortion / 100.0) * (CCxAdj - CCo)
            else:
                CCxFinal = CCxAdj - (0.5 * CCdistortion / 100.0) * (CCxAdj - CCo)

            if CCxFinal < CCo:
                CCxFinal = CCo

            denom = float(L123 - L12SS)
            if abs(denom) <= epsilon(1.0):
                StressResponse.CDecline = 0.001  # keep it finite, same intent as Fortran safeguard
            else:
                StressResponse.CDecline = 100.0 * (CCxAdj - CCxFinal) / denom

                if StressResponse.CDecline > 1.0:
                    StressResponse.CDecline = 1.0
                if StressResponse.CDecline <= epsilon(1.0):
                    StressResponse.CDecline = 0.001
        else:
            StressResponse.CDecline = 0.001  # no shift of maturity

    # Stomata closure
    StressResponse.RedKsSto = int(CCxRed)

    return StressResponse

def Bnormalized(
    TheDaysToCCini: int,
    TheGDDaysToCCini: int,
    L0: int,
    L12: int,
    L12SF: int,
    L123: int,
    L1234: int,
    Lend: int,
    LFlor: int,
    GDDL0: int,
    GDDL12: int,
    GDDL12SF: int,
    GDDL123: int,
    GDDL1234: int,
    WPyield: int,
    DaysYieldFormation: int,
    tSwitch: int,
    CCo: float,
    CCx: float,
    CGC: float,
    GDDCGC: float,
    CDC: float,
    GDDCDC: float,
    KcTop: float,
    KcDeclAgeingCumul: float,
    CCeffectProcent: float,
    WPbio: float,
    TheCO2: float,
    Tbase: float,
    Tupper: float,
    TDayMin: float,
    TDayMax: float,
    GDtranspLow: float,
    RatDGDD: float,
    SumKcTop: float,
    StressInPercent: int,
    StrResRedCGC: int,
    StrResRedCCx: int,
    StrResRedWP: int,
    StrResRedKsSto: int,
    WeedStress: int,
    DeltaWeedStress: int,
    StrResCDecline: float,
    ShapeFweed: float,
    TheModeCycle: int,
    FertilityStressOn: bool,
    ReferenceClimate: bool,
) -> float:
    EToStandard = 5.0
    k = 2

    # 1. Adjustment for weed infestation
    if WeedStress > 0:
        if StressInPercent > 0:  # soil fertility stress
            fWeed = 1.0  # no expansion of canopy cover possible
        else:
            fWeed = CCmultiplierWeed(WeedStress, CCx, ShapeFweed)

        CCoadj = CCo * fWeed
        CCxadj = CCx * fWeed
        CDCadj = CDC * (fWeed * CCx + 2.29) / (CCx + 2.29)
        GDDCDCadj = GDDCDC * (fWeed * CCx + 2.29) / (CCx + 2.29)
    else:
        CCoadj = CCo
        CCxadj = CCx
        CDCadj = CDC
        GDDCDCadj = GDDCDC

    # 2. Open Temperature file (bulk read)
    temps = None
    temp_pos = 0
    if (GetTemperatureFile() != "(None)") and (GetTemperatureFile() != "(External)"):
        sim_name = "TCropReference.SIM" if ReferenceClimate else "TCrop.SIM"

        base_dir = _strip_quotes(GetPathNameSimul()).strip()
        base_dir_full = ResolvePath("", base_dir)

        full_path = os.path.normpath(os.path.join(base_dir_full, sim_name.lstrip("/\\")))

        with open(full_path, "r", encoding="utf-8", errors="replace") as fTemp:
            raw_lines = fTemp.read().splitlines()

        parsed = []
        for ln in raw_lines:
            parts = ln.split()
            if len(parts) >= 2:
                try:
                    tmin = float(parts[0])
                    tmax = float(parts[1])
                    parsed.append((tmin, tmax))
                except ValueError:
                    pass

        temps = parsed
        temp_pos = 0

    # 3. Initialize
    SumKcTopSF = (1.0 - float(StressInPercent) / 100.0) * SumKcTop
    # only required for soil fertility stress

    SetSimulation_DelayedDays(0)  # required for CalculateETpot
    SumKci = 0.0
    SumBnor = 0.0
    SumGDDforPlot = float(undef_int)
    SumGDD = float(undef_int)
    SumGDDfromDay1 = 0.0
    GrowthON = False
    GDDTadj = undef_int
    DayFraction = float(undef_int)
    GDDayFraction = float(undef_int)
    CCxWitheredForB = 0.0

    # 4. Initialise 1st day
    if TheDaysToCCini != 0:
        # regrowth which starts on 1st day
        GrowthON = True

        if TheDaysToCCini == undef_int:
            # CCx on 1st day
            Tadj = L12 - L0
            if TheModeCycle == ModeCycle_GDDays:
                GDDTadj = GDDL12 - GDDL0
                SumGDD = float(GDDL12)
            CCinitial = CCxadj * (1.0 - StrResRedCCx / 100.0)
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
                CCoadj,
                CCxadj,
                CGC,
                CDCadj,
                GDDCGC,
                GDDCDCadj,
                SumGDDforPlot,
                TheModeCycle,
                StrResRedCGC,
                StrResRedCCx,
            )

        # Time reduction for days between L12 and L123
        DayFraction = (L123 - L12) * 1.0 / float(Tadj + L0 + (L123 - L12))
        if TheModeCycle == ModeCycle_GDDays:
            GDDayFraction = (GDDL123 - GDDL12) * 1.0 / float(GDDTadj + GDDL0 + (GDDL123 - GDDL12))
    else:
        # growth starts after germination/recover
        Tadj = 0
        if TheModeCycle == ModeCycle_GDDays:
            GDDTadj = 0
            SumGDD = 0.0
        CCinitial = CCoadj

    # 5. Calculate Bnormalized
    i = 0
    for Dayi in range(1, Lend + 1):
        # 5.1 growing degrees for dayi
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
            # From TCrop*.SIM bulk list
            if temps is None or len(temps) == 0:
                Tndayi = float(TDayMin)
                Txdayi = float(TDayMax)
            else:
                if temp_pos >= len(temps):
                    # Fortran rewinds only if ReferenceClimate == true, but re-reading from start is harmless here
                    temp_pos = 0
                Tndayi, Txdayi = temps[temp_pos]
                temp_pos += 1
            GDDi = DegreesDay(Tbase, Tupper, float(Tndayi), float(Txdayi), GetSimulParam_GDDMethod())

        if TheModeCycle == ModeCycle_GDDays:
            SumGDD = float(SumGDD) + GDDi
            SumGDDfromDay1 += GDDi

        # 5.2 green Canopy Cover (CC)
        DayCC = Dayi
        if GrowthON is False:
            # not yet canopy development
            CCi = 0.0
            if TheDaysToCCini != 0:
                # regrowth
                CCi = CCinitial
                GrowthON = True
            else:
                # sowing or transplanting
                if TheModeCycle == ModeCycle_CalendarDays:
                    if Dayi == (L0 + 1):
                        CCi = CCinitial
                        GrowthON = True
                else:
                    if float(SumGDD) > GDDL0:
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
                    SumGDDforPlot = float(SumGDD)
                    if SumGDDforPlot > GDDL1234:
                        SumGDDforPlot = float(GDDL1234)  # special case where L123 > L1234
                    if SumGDDforPlot > GDDL12:
                        if SumGDDfromDay1 <= GDDL123:
                            SumGDDforPlot = float(GDDL12) + float(
                                roundc(
                                    GDDayFraction * (SumGDDfromDay1 + GDDTadj + GDDL0 - GDDL12),
                                    mold="int32",
                                )
                            )  # slow down
                        else:
                            SumGDDforPlot = SumGDDfromDay1  # switch time scale

            CCi = CCiNoWaterStressSF(
                DayCC,
                L0,
                L12SF,
                L123,
                L1234,
                GDDL0,
                GDDL12SF,
                GDDL123,
                GDDL1234,
                CCoadj,
                CCxadj,
                CGC,
                GDDCGC,
                CDCadj,
                GDDCDCadj,
                SumGDDforPlot,
                RatDGDD,
                StrResRedCGC,
                StrResRedCCx,
                StrResCDecline,
                TheModeCycle,
            )

        if CCi > CCxWitheredForB:
            CCxWitheredForB = CCi
        if DayCC >= L12SF:
            CCxWitheredForB = CCxadj * (1.0 - StrResRedCCx / 100.0)

        CCw = CCi

        if CCi > 0.0001:
            # 5.3 potential transpiration of total canopy cover (crop and weed)
            TpotForB = 0.0
            EpotTotForB = 0.0
            TpotForB, EpotTotForB = CalculateETpot(
                DayCC,
                L0,
                L12,
                L123,
                L1234,
                0,
                CCi,
                EToStandard,
                KcTop,
                KcDeclAgeingCumul,
                CCxadj,
                CCxWitheredForB,
                CCeffectProcent,
                TheCO2,
                GDDi,
                GDtranspLow,
                TpotForB,
                EpotTotForB,
            )

            # 5.4 Sum of Kc (only required for soil fertility stress)
            SumKci += (TpotForB / EToStandard)

            # 5.5 potential transpiration of crop canopy cover (without weed)
            if WeedStress > 0:
                # green canopy cover of the crop (CCw) in weed-infested field
                # (CCi is CC of crop and weeds)
                fCCx = 1.0  # only for non perennials (no self-thinning)
                if DeltaWeedStress != 0:
                    DeltaWeedStress_local = DeltaWeedStress
                    WeedCorrection, DeltaWeedStress_local = GetWeedRC(
                        DayCC,
                        SumGDDforPlot,
                        fCCx,
                        WeedStress,
                        GetManagement_WeedAdj(),
                        DeltaWeedStress_local,
                        L12SF,
                        L123,
                        GDDL12SF,
                        GDDL123,
                        TheModeCycle,
                    )
                else:
                    WeedCorrection = WeedStress

                CCw = CCi * (1.0 - WeedCorrection / 100.0)

                # correction for micro-advection
                CCtotStar = 1.72 * CCi - 1.0 * (CCi * CCi) + 0.30 * (CCi * CCi * CCi)
                if CCtotStar < 0.0:
                    CCtotStar = 0.0
                if CCtotStar > 1.0:
                    CCtotStar = 1.0

                if CCw > 0.0001:
                    CCwStar = CCw + (CCtotStar - CCi)
                else:
                    CCwStar = 0.0

                # crop transpiration in weed-infested field
                if CCtotStar <= 0.0001:
                    TpotForB = 0.0
                else:
                    TpotForB = TpotForB * (CCwStar / CCtotStar)
        else:
            TpotForB = 0.0

        # 5.6 biomass water productivity (WP)
        WPi = WPbio  # vegetative stage

        # 5.6a. vegetative versus yield formation stage
        if (
            (GetCrop_subkind() == subkind_Tuber or GetCrop_subkind() == subkind_Grain)
            and (WPyield < 100)
            and (Dayi > LFlor)
        ):
            # yield formation stage
            fSwitch = 1.0
            if (DaysYieldFormation > 0) and (tSwitch > 0):
                fSwitch = (Dayi - LFlor) * 1.0 / float(tSwitch)
                if fSwitch > 1.0:
                    fSwitch = 1.0
            WPi = WPi * (1.0 - (1.0 - WPyield / 100.0) * fSwitch)

        # 5.7 Biomass (B)
        if FertilityStressOn:
            # 5.7a - reduction for soil fertiltiy
            if (StrResRedWP > 0) and (SumKci > 0.0) and (SumKcTopSF > epsilon(1.0)):
                if SumKci < SumKcTopSF:
                    if SumKci > 0.0:
                        WPi = WPi * (1.0 - (StrResRedWP / 100.0) * math.exp(k * math.log(SumKci / SumKcTopSF)))
                else:
                    WPi = WPi * (1.0 - StrResRedWP / 100.0)

            # 5.7b - Biomass (B)
            SumBnor += WPi * (TpotForB / EToStandard)
        else:
            # for salinity stress
            SumBnor += WPi * (1.0 - StrResRedKsSto / 100.0) * (TpotForB / EToStandard)

    # 5. Export
    return float(SumBnor)

def ResetCropDay1(CropDay1IN, SwitchToYear1):
    CropDay1OUT = 0
    dayi = 0
    monthi = 0
    yeari = 0

    dayi, monthi, yeari = DetermineDate(CropDay1IN)
    if GetTemperatureRecord_FromY() == 1901:
        yeari = 1901
        CropDay1OUT = DetermineDayNr(dayi, monthi, yeari, CropDay1OUT)
    else:
        if SwitchToYear1:
            CropDay1OUT = DetermineDayNr(dayi, monthi, GetTemperatureRecord_FromY(), CropDay1OUT)
        else:
            CropDay1OUT = CropDay1IN

    return CropDay1OUT

def MaxAvailableGDD(FromDayNr, Tbase, Tupper, TDayMin, TDayMax):
    i = 0
    MaxGDDays = 100000.0
    DayGDD = 0.0
    DayNri = 0
    TminDataSet = [rep_DayEventDbl(0, 0.0) for _ in range(31)]
    TmaxDataSet = [rep_DayEventDbl(0, 0.0) for _ in range(31)]

    MaxGDDays = 100000.0
    if GetTemperatureFile() == '(None)':
        DayGDD = DegreesDay(Tbase, Tupper, TDayMin, TDayMax,
                            GetSimulParam_GDDMethod())
        if DayGDD <= epsilon(1.0):
            MaxGDDays = 0.0
    elif GetTemperatureFile() == '(External)':
        DayNri = FromDayNr
        MaxGDDays = 0.0
        i = DayNri - GetSimulation_FromDayNr() + 1
        TDayMin = float(GetTminRun_i(i))
        TDayMax = float(GetTmaxRun_i(i))
        DayGDD = DegreesDay(Tbase, Tupper, TDayMin, TDayMax,
                            GetSimulParam_GDDMethod())
        MaxGDDays = MaxGDDays + DayGDD
        while i < (GetSimulation_ToDayNr() - GetSimulation_FromDayNr() + 1):
            i = i + 1
            TDayMin = float(GetTminRun_i(i))
            TDayMax = float(GetTmaxRun_i(i))
            DayGDD = DegreesDay(Tbase, Tupper, TDayMin, TDayMax,
                                GetSimulParam_GDDMethod())
            MaxGDDays = MaxGDDays + DayGDD
    else:
        MaxGDDays = 0.0
        if FullUndefinedRecord(GetTemperatureRecord_FromY(),
                               GetTemperatureRecord_FromD(), GetTemperatureRecord_FromM(),
                               GetTemperatureRecord_ToD(), GetTemperatureRecord_ToM()):
            FromDayNr = GetTemperatureRecord_FromDayNr()
        DayNri = FromDayNr

        if TemperatureFilefull_exists and \
            (GetTemperatureRecord_ToDayNr() > FromDayNr) and \
            (GetTemperatureRecord_FromDayNr() <= FromDayNr):

            if GetTemperatureRecord_DataType() == datatype_Daily:
                i = DayNri - GetTemperatureRecord_FromDayNr() + 1
                i0 = i - 1
                TDayMin = Tmin[i0]
                TDayMax = Tmax[i0]

                DayNri = DayNri + 1
                DayGDD = DegreesDay(Tbase, Tupper, TDayMin, TDayMax,
                                    GetSimulParam_GDDMethod())
                MaxGDDays = MaxGDDays + DayGDD

                while DayNri < GetTemperatureRecord_ToDayNr():
                    i = i + 1
                    if i == len(Tmin):
                        i = 1
                    i0 = i - 1
                    TDayMin = Tmin[i0]
                    TDayMax = Tmax[i0]

                    DayGDD = DegreesDay(Tbase, Tupper, TDayMin, TDayMax,
                                        GetSimulParam_GDDMethod())
                    MaxGDDays = MaxGDDays + DayGDD
                    DayNri = DayNri + 1

            elif GetTemperatureRecord_DataType() == datatype_Decadely:
                TminDataSet, TmaxDataSet = GetDecadeTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet)
                i = 1
                while TminDataSet[i - 1].DayNr != DayNri:
                    i = i + 1
                TDayMin = TminDataSet[i - 1].Param
                TDayMax = TmaxDataSet[i - 1].Param
                DayGDD = DegreesDay(Tbase, Tupper, TDayMin, TDayMax,
                                    GetSimulParam_GDDMethod())
                MaxGDDays = MaxGDDays + DayGDD
                DayNri = DayNri + 1
                while DayNri < GetTemperatureRecord_ToDayNr():
                    if DayNri > TminDataSet[31 - 1].DayNr:
                        TminDataSet, TmaxDataSet = GetDecadeTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet)
                    i = 1
                    while TminDataSet[i - 1].DayNr != DayNri:
                        i = i + 1
                    TDayMin = TminDataSet[i - 1].Param
                    TDayMax = TmaxDataSet[i - 1].Param
                    DayGDD = DegreesDay(Tbase, Tupper, TDayMin, TDayMax,
                                        GetSimulParam_GDDMethod())
                    MaxGDDays = MaxGDDays + DayGDD
                    DayNri = DayNri + 1

            elif GetTemperatureRecord_DataType() == datatype_Monthly:
                TminDataSet, TmaxDataSet = GetMonthlyTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet)
                i = 1
                while TminDataSet[i - 1].DayNr != DayNri:
                    i = i + 1
                TDayMin = TminDataSet[i - 1].Param
                TDayMax = TmaxDataSet[i - 1].Param
                DayGDD = DegreesDay(Tbase, Tupper, TDayMin, TDayMax,
                                    GetSimulParam_GDDMethod())
                MaxGDDays = MaxGDDays + DayGDD
                DayNri = DayNri + 1
                while DayNri < GetTemperatureRecord_ToDayNr():
                    if DayNri > TminDataSet[31 - 1].DayNr:
                        TminDataSet, TmaxDataSet = GetMonthlyTemperatureDataSet(DayNri, TminDataSet, TmaxDataSet)
                    i = 1
                    while TminDataSet[i - 1].DayNr != DayNri:
                        i = i + 1
                    TDayMin = TminDataSet[i - 1].Param
                    TDayMax = TmaxDataSet[i - 1].Param
                    DayGDD = DegreesDay(Tbase, Tupper, TDayMin, TDayMax,
                                        GetSimulParam_GDDMethod())
                    MaxGDDays = MaxGDDays + DayGDD
                    DayNri = DayNri + 1

    return MaxGDDays, FromDayNr, TDayMin, TDayMax
