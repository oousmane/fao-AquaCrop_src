from ._global import *
from .defaultcropsoil import *

def InitializeSettings(use_default_soil_file, use_default_crop_file):

    TempString1 = TempString2 = CO2descr = ""
    Nri = Crop_Day1_temp = Crop_DayN_temp = 0
    SumWaBal_temp = rep_sum()
    global undef_int

    # 1. Program settings
    #Settings of Program parameters

    # ---------------------------
    # 1a. General.PAR
    # Threshold [% of RAW] for determination of Inet
    SetSimulParam_PercRAW(50)

    # Number of soil compartments (maximum is 12) (not a program parameter)
    SetNrCompartments(12)

    # Default thickness of soil compartments [m]
    SetSimulParam_CompDefThick(0.1)

    # DayNumber of first day cropping period (1..365)
    SetSimulParam_CropDay1(81)

    # Default base temperature (degC) below which no crop development
    SetSimulParam_Tbase(10.0)

    # Default upper temperature threshold for crop development
    SetSimulParam_Tupper(30.0)

    # Percentage of soil surface wetted by irrigation in crop season
    SetSimulParam_IrriFwInSeason(100)

    # Percentage of soil surface wetted by irrigation off-season
    SetSimulParam_IrriFwOffSeason(100)

    # ---------------------------
    # 1b. Soil.PAR - 6 parameters

    # Considered depth (m) of soil profile for calculation of mean soil water content
    SetSimulParam_RunoffDepth(0.3)

    SetSimulParam_CNcorrection(True)

    # Salt diffusion factor (%)
    SetSimulParam_SaltDiff(20)

    # Salt solubility (g/liter)
    SetSimulParam_SaltSolub(100)

    # Shape factor capilFlary rise factor
    SetSimulParam_RootNrDF(16)

    # Fixed in Version 5.0 cannot be changed since linked with equations for CN AMCII and CN converions
    SetSimulParam_IniAbstract(5)

    # ---------------------------
    # 1c. Rainfall.PAR - 4 parameters

    SetSimulParam_EffectiveRain_Method(EffectiveRainMethod_USDA)

    # If Method is Percentage
    SetSimulParam_EffectiveRain_PercentEffRain(70)

    # For estimation of surface run-off
    SetSimulParam_EffectiveRain_ShowersInDecade(2)

    # For reduction of soil evaporation
    SetSimulParam_EffectiveRain_RootNrEvap(5)

    # ---------------------------
    # 1d. Crop.PAR  - 12 parameters

    # Evaporation decline factor in stage 2
    SetSimulParam_EvapDeclineFactor(4)

    # Kc wet bare soil [-]
    SetSimulParam_KcWetBare(1.1)

    # CC threshold below which HI no longer increase(% of 100)
    SetSimulParam_PercCCxHIfinal(5)

    # Starting depth of root sine function (% of Zmin)
    SetSimulParam_RootPercentZmin(70)

    # Fixed at 5 cm/day
    SetSimulParam_MaxRootZoneExpansion(5.0)

    # Shape factor for effect water stress on rootzone expansion
    SetSimulParam_KsShapeFactorRoot(-6)

    # Soil water content (% TAW) required at sowing depth for germination
    SetSimulParam_TAWGermination(20)

    # Adjustment factor for FAO-adjustment soil water depletion (p) for various ET
    SetSimulParam_pAdjFAO(1)

    # Number of days for full effect of deficient aeration
    SetSimulParam_DelayLowOxygen(3)

    # Exponent of senescence factor adjusting drop in photosynthetic activity of dying crop
    SetSimulParam_ExpFsen(1.00)

    # Decrease (percentage) of p(senescence) once early canopy senescence is triggered
    SetSimulParam_Beta(12)

    # Thickness top soil (cm) in which soil water depletion has to be determined
    SetSimulParam_ThicknessTopSWC(10)

    # ---------------------------
    # 1e. Field.PAR  - 1 parameter

    # Maximum water extraction depth by soil evaporation [cm]
    SetSimulParam_EvapZmax(30)

    # ---------------------------
    # 1f. Temperature.PAR  - 3 parameters

    # Default minimum temperature (degC) if no temperature file is specified
    SetSimulParam_Tmin(12)

    # Default maximum temperature (degC) if no temperature file is specified
    SetSimulParam_Tmax(28)

    # Default method for GDD calculations
    SetSimulParam_GDDMethod(3)


    # ---

    SetPreDay(False)

    # Default Value for Percentage TAW for Display in Initial Soil Water Content Menu
    SetIniPercTAW(50)

    # Default for soil compartments
    if GetNrCompartments() > max_No_compartments:
        # Savety check of value in General.PAR
        SetNrCompartments(max_No_compartments)

    for Nri in range(1, max_No_compartments + 1):
        # required for formactivate ParamNew
        SetCompartment_Thickness(Nri, GetSimulParam_CompDefThick())

    # Default CropDay1 - Savety check of value in General.PAR
    while GetSimulParam_CropDay1() > 365:
        SetSimulParam_CropDay1(GetSimulParam_CropDay1() - 365)

    if GetSimulParam_CropDay1() < 1:
        SetSimulParam_CropDay1(1)

    # ---------------------------
    # 2a. Ground water table
    SetGroundWaterFile('(None)')
    SetGroundWaterFileFull(GetGroundWaterFile())  # no file
    SetGroundWaterDescription('no shallow groundwater table')
    SetZiAqua(undef_int)
    SetECiAqua(float(undef_int))
    SetSimulParam_ConstGwt(True)


    # ---------------------------
    # 2b. Soil profile and initial soil water content
    # Reset the soil profile to its default values
    # required for  SetSoil_RootMax(RootMaxInSoilProfile(GetCrop().RootMax, 
    #               GetCrop().RootMin,GetSoil().NrSoilLayers,
    #               SoilLayer)) in LoadProfile
    ResetDefaultSoil(use_default_soil_file)

    SetCrop_RootMin(0.3) # Minimum rooting depth (m)
    SetCrop_RootMax(1.0) # Maximum rooting depth (m)

    if use_default_soil_file:
        SetProfFile('DEFAULT.SOL')
        SetProfFilefull(GetPathNameSimul() + GetProfFile())
        # Crop.RootMin, RootMax, and Soil.RootMax are
        # correctly calculated in LoadCrop
        LoadProfile(GetProfFilefull())

    # Simulation.ResetIniSWC AND
    # specify_soil_layer whcih contains
    # PROCEDURE DeclareInitialCondAtFCandNoSalt,
    # in which SWCiniFile := '(None)', and settings
    # for Soil water and Salinity content
    CompleteProfileDescription()

    # ---------------------------
    # 2c. Complete initial conditions (crop development)
    SetSimulation_CCini(float(undef_int))  # CCini = real(undef_int, dp)
    SetSimulation_Bini(0.0)                # Bini  = 0.000_dp
    SetSimulation_Zrini(float(undef_int))  # Zrini = real(undef_int, dp)

    # 3. Crop characteristics and cropping period
    ResetDefaultCrop(use_default_crop_file)  # Reset the crop to its default values
    SetCropFile('DEFAULT.CRO')
    SetCropFileFull(GetPathNameSimul() + GetCropFile())
    # LoadCrop ==============================
    SetCrop_CCo((GetCrop_PlantingDens()/10000.0) * (GetCrop_SizeSeedling()/10000.0))
    SetCrop_CCini((GetCrop_PlantingDens()/10000.0) * (GetCrop_SizePlant()/10000.0))
    # maximum rooting depth in given soil profile
    SetSoil_RootMax(
        RootMaxInSoilProfile(
            GetCrop_RootMax(),
            GetSoil_NrSoilLayers(),
            GetSoilLayer()
        )
    )
    # determine miscellaneous
    SetCrop_Day1(GetSimulParam_CropDay1())
    CompleteCropDescription()
    SetSimulation_YearSeason(1)
    NoCropCalendar()

    # 4. Field Management
    SetManFile('(None)')
    SetManFileFull(GetManFile())  # no file
    NoManagement()

    # 5. Climate
    # 5.1 Temperature
    SetTemperatureFile('(None)')
    SetTemperatureFileFull(GetTemperatureFile())  # no file
    SetTnxReferenceFile(GetTemperatureFile())  # no file
    SetTnxReferenceYear(2000)  # for refernce CO2 concentration

    TempString1 = f"{GetSimulParam_Tmin():8.1f}"
    TempString2 = f"{GetSimulParam_Tmax():8.1f}"

    SetTemperatureDescription('')
    SetTemperatureRecord_DataType(datatype_Daily)
    SetTemperatureRecord_NrObs(0)
    SetTemperatureRecord_FromString('any date')
    SetTemperatureRecord_ToString('any date')
    SetTemperatureRecord_FromY(1901)

    # 5.2 ETo
    SetEToFile('(None)')
    SetEToFileFull(GetEToFile())  # no file
    SetEToDescription('')
    SetEToRecord_DataType(datatype_Daily)
    SetEToRecord_NrObs(0)
    SetEToRecord_FromString('any date')
    SetEToRecord_ToString('any date')
    SetEToRecord_FromY(1901)

    # 5.3 Rain
    SetRainFile('(None)')
    SetRainFileFull(GetRainFile())  # no file
    SetRainDescription('')
    SetRainRecord_DataType(datatype_Daily)
    SetRainRecord_NrObs(0)
    SetRainRecord_FromString('any date')
    SetRainRecord_ToString('any date')
    SetRainRecord_FromY(1901)

    # 5.4 CO2
    SetCO2File('MaunaLoa.CO2')
    SetCO2FileFull(GetPathNameSimul() + GetCO2File())
    CO2descr = GetCO2Description()
    CO2descr = GenerateCO2Description(GetCO2FileFull(), CO2descr)
    SetCO2Description(CO2descr)

    # 5.5 Climate file
    SetClimateFile('(None)')
    SetClimateFileFull(GetClimateFile())
    SetClimateDescription('')

    # 5.6 Set Climate and Simulation Period
    SetClimData()
    SetSimulation_LinkCropToSimPeriod(True)
    # adjusting Crop.Day1 and Crop.DayN to ClimFile
    Crop_Day1_temp = GetCrop_Day1()
    Crop_DayN_temp = GetCrop_DayN()
    Crop_Day1_temp, Crop_DayN_temp = AdjustCropYearToClimFile(Crop_Day1_temp, Crop_DayN_temp)
    SetCrop_Day1(Crop_Day1_temp)
    SetCrop_DayN(Crop_DayN_temp)

    # adjusting ClimRecord.'TO' for undefined year with 365 days
    if ((GetClimFile() != '(None)') and (GetClimRecord_FromY() == 1901) and (GetClimRecord_NrObs() == 365)):
        AdjustClimRecordTo(GetCrop_DayN())
    
    # adjusting simulation period
    AdjustSimPeriod()

    # 6. irrigation
    SetIrriFile('(None)')
    SetIrriFileFull(GetIrriFile()) # no file
    NoIrrigation()

    # 7. Off-season
    SetOffSeasonFile('(None)')
    SetOffSeasonFilefull(GetOffSeasonFile())
    NoManagementOffSeason()

    # 8. Project and Multiple Project file
    SetProjectFile('(None)')
    SetProjectFileFull(GetProjectFile())
    SetProjectDescription('No specific project')
    SetSimulation_MultipleRun(False)  # No sequence of simulation runs in the project
    SetSimulation_NrRuns(1)
    SetSimulation_MultipleRunWithKeepSWC(False)
    SetSimulation_MultipleRunConstZrx(float(undef_int))
    SetMultipleProjectFile(GetProjectFile())
    SetMultipleProjectFileFull(GetProjectFileFull())
    SetMultipleProjectDescription(GetProjectDescription())

    # 9. Observations file
    SetObservationsFile('(None)')
    SetObservationsFilefull(GetObservationsFile())
    SetObservationsDescription('No field observations')

    # 10. Output files
    SetOutputName('Project')

    # 11. Onset
    SetOnset_Criterion(Criterion_RainPeriod)
    SetOnset_AirTCriterion(AirTCriterion_CumulGDD)
    AdjustOnsetSearchPeriod()


    # 12. Simulation run
    SetETo(5.0)
    SetRain(0.0)
    SetIrrigation(0.0)
    SetSurfaceStorage(0.0)
    SetECstorage(0.0)
    SetDaySubmerged(0)


    SumWaBal_temp = GetSumWaBal()
    SumWaBal_temp = GlobalZero(SumWaBal_temp)
    SetSumWaBal(SumWaBal_temp)

    SetDrain(0.0)       # added 4.0
    SetRunoff(0.0)      # added 4.0
    SetInfiltrated(0.0) # added 4.0
    SetCRwater(0.0)     # added 4.0
    SetCRsalt(0.0)      # added 4.0

    SetSimulation_ResetIniSWC(True)
    SetSimulation_EvapLimitON(False)
    SetMaxPlotNew(50)
    SetMaxPlotTr(10)
    SetSimulation_InitialStep(10)          # Length of period (days) for displaying
                                        # intermediate results during simulation run
    SetSimulation_LengthCuttingInterval(40)  # Default length of cutting interval (days)
