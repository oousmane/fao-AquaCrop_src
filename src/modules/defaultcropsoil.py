from ._global import *

# Función terminada
def ResetDefaultSoil(use_default_soil_file):

    cra_temp = crb_temp = 0.0
    TempString = ""

    SetProfDescription('deep loamy soil profile')
    SetSoil_CNvalue(61) # For an initial abstraction of 0.05 S
    SetSoil_REW(9)
    SetSoil_NrSoilLayers(1)
    SetSoilLayer_Thickness(1, 4.0)
    SetSoilLayer_SAT(1, 50.0)
    SetSoilLayer_FC(1, 30.0)
    SetSoilLayer_WP(1, 10.0)
    SetSoilLayer_InfRate(1, 500)
    SetSoilLayer_Penetrability(1, 100)
    SetSoilLayer_GravelMass(1, 0)
    SetSoilLayer_GravelVol(1, 0.0)
    TempString = "Loamy soil horizon"
    SetSoilLayer_Description(1, TempString)
    
    soil_class = NumberSoilClass(
        GetSoilLayer_SAT(1),
        GetSoilLayer_FC(1),
        GetSoilLayer_WP(1),
        GetSoilLayer_InfRate(1),
    )
    SetSoilLayer_SoilClass(1, soil_class)

    cra_temp = GetSoilLayer_CRa(1)
    crb_temp = GetSoilLayer_CRb(1)
    cra_temp, crb_temp = DetermineParametersCR(GetSoilLayer_SoilClass(1), GetSoilLayer_InfRate(1), cra_temp, crb_temp)
    
    SetSoilLayer_CRa(1, cra_temp)
    SetSoilLayer_CRb(1, crb_temp)

    if(use_default_soil_file):
        SetProfFilefull(GetPathNameSimul() + 'DEFAULT.SOL')
        SaveProfile(GetProfFilefull())



def ResetDefaultCrop(use_default_crop_file):
    # Whether to write a 'DEFAULT.CRO' file.
    SetCropDescription('a generic crop')
    SetCrop_subkind(subkind_Grain)
    SetCrop_Planting(plant_Seed)
    SetCrop_SownYear1(True)  # for perennials
    SetCrop_ModeCycle(ModeCycle_CalendarDays)
    SetCrop_pMethod(pMethod_FAOCorrection)
    SetCrop_Tbase(5.5)            # Basal temperature (degC)
    SetCrop_Tupper(30.0)          # Cut-off temperature (degC)
    SetCrop_pLeafDefUL(0.25)      # p-leaf Upper Limit
    SetCrop_pLeafDefLL(0.60)      # p-leaf Lower Limit
    SetCrop_KsShapeFactorLeaf(3.0)  # Ks Leaf expansion (0 = straight line)
    SetCrop_pdef(0.50)            # p-stomatal
    SetCrop_KsShapeFactorStomata(3.0)  # Ks Stomatal Control (0 = straight line)
    SetCrop_pSenescence(0.85)     # p-senescence
    SetCrop_KsShapeFactorSenescence(3.0)  # Ks Canopy Senescence (0 = straight line)
    SetCrop_SumEToDelaySenescence(50)     # Sum(ETo) before senescence is triggered
    SetCrop_pPollination(0.90)
    SetCrop_AnaeroPoint(5)        # Vol% for Anaerobiotic point
    SetCrop_StressResponse_Stress(50)        # Soil fertility stress at calibration (%)
    SetCrop_StressResponse_ShapeCGC(2.16)    # Shape factor CGC vs fertility stress
    SetCrop_StressResponse_ShapeCCX(0.79)    # Shape factor CCx vs fertility stress
    SetCrop_StressResponse_ShapeWP(1.67)     # Shape factor WP vs fertility stress
    SetCrop_StressResponse_ShapeCDecline(1.67)   # Shape factor CC decline vs fertility stress
    SetCrop_PrematureEnd(undef_int) # day at which annual crops cannot survive (daynumber counting from 1 January of planting year)
    SetCrop_StressResponse_Calibrated(True)
    SetCrop_ECemin(2)            # EC at which salinity starts to affect crop (dS/m)
    SetCrop_ECemax(12)           # EC at which crop can no longer grow (dS/m)
    SetCrop_CCsaltDistortion(25) # Distortion canopy cover for salinity calibration (%)
    SetCrop_ResponseECsw(100)    # Response of Ks stomata to ECsw (0..125)
    SetCrop_Tcold(8)             # Min air T for pollination (cold stress) (degC)
    SetCrop_Theat(40)            # Max air T for pollination (heat stress) (degC)
    SetCrop_GDtranspLow(11.1)    # Min growing degrees for full transpiration (degC-day)
    SetCrop_KcTop(1.10)          # Kc when complete cover and prior to senescence
    SetCrop_KcDeclineCumul(11.0) # Decline crop coefficient (%/day) as a result of ageing, nitrogen defficiency, etc.
    SetCrop_RootMin(0.30)        # Minimum rooting depth (m)
    SetCrop_RootMax(1.00)        # Maximum rooting depth (m)
    SetCrop_RootMinYear1(GetCrop_RootMin())  # Min rooting depth in first year (perennials)
    SetCrop_RootShape(15)        # Shape factor root zone expansion
    SetCrop_SmaxTopQuarter(0.048)  # Max root water extraction top quarter (m3/m3.day)
    SetCrop_SmaxBotQuarter(0.012)  # Max root water extraction bottom quarter (m3/m3.day)
    SetCrop_CCEffectEvapLate(50)   # Effect of CC on reducing soil evap in late season
    SetCrop_SizeSeedling(6.50)     # Canopy cover per seedling (cm2)
    SetCrop_SizePlant(GetCrop_SizeSeedling())  # Canopy cover when regrowth (cm2)
    SetCrop_PlantingDens(185000)   # Plants per hectare
    SetCrop_CCo((GetCrop_SizeSeedling()/10000.0) * (GetCrop_PlantingDens()/10000.0))  # CCo fraction
    SetCrop_CCini(GetCrop_CCo())
    SetCrop_CGC(0.15)              # Canopy growth coefficient (fraction/day)
    SetCrop_YearCCx(int(undef_int))    # Years at which CCx declines to 90% (perennials)
    SetCrop_CCxRoot(float(undef_int))  # Shape factor of CCx decline over years (perennials)
    SetCrop_CCx(0.80)              # Maximum canopy cover (fraction)
    SetCrop_CDC(0.1275)            # Canopy decline coefficient (fraction/day)
    SetCrop_DaysToCCini(0)
    SetCrop_DaysToGermination(5)       # Calendar Days: sowing → germination
    SetCrop_DaysToMaxRooting(100)      # Calendar Days: sowing → max rooting depth
    SetCrop_DaysToSenescence(110)      # Calendar Days: sowing → start senescence
    SetCrop_DaysToHarvest(125)         # Calendar Days: sowing → maturity
    SetCrop_DaysToFlowering(70)        # Calendar Days: sowing → flowering
    SetCrop_LengthFlowering(10)        # Length of flowering stage (days)
    SetCrop_DaysToHIo(50)
    SetCrop_DeterminancyLinked(True)
    SetCrop_fExcess(50)            # Potential excess of fruits (%)
    SetCrop_WP(17.0)               # Normalized Water productivity (g/m2)
    SetCrop_WPy(100)               # WP during yield formation (% of WP)
    SetCrop_AdaptedToCO2(100)      # % adapted to elevated atmospheric CO2
    SetCrop_HI(50)                 # Harvest index (%)
    SetCrop_DryMatter(25)          # Dry matter content (%) of fresh yield
    SetCrop_HIincrease(5)          # Possible HI increase (%) due to pre-flowering water stress
    SetCrop_aCoeff(10.0)           # Positive impact coeff. on HI
    SetCrop_bCoeff(8.0)            # Reduction coeff. of stomatal closure impact on HI
    SetCrop_DHImax(15)             # Max allowable increase (%) of specified HI
    SetCrop_dHIdt(-9.0)            # Calculated as Crop_HI/Crop_DaysToHIo
    SetCrop_GDDaysToCCini(-9)


    SetCrop_GDDaysToGermination(-9)    # GDD: sowing → germination
    SetCrop_GDDaysToMaxRooting(-9)     # GDD: sowing → max rooting depth
    SetCrop_GDDaysToSenescence(-9)     # GDD: sowing → start senescence
    SetCrop_GDDaysToHarvest(-9)        # GDD: sowing → harvest
    SetCrop_GDDaysToFlowering(-9)      # GDD: sowing → flowering
    SetCrop_GDDLengthFlowering(-9)     # Length of flowering stage (GDD)
    SetCrop_GDDaysToHIo(-9)
    SetCrop_GDDCGC(-9.0)               # CGC in GDD (fraction per GDD)
    SetCrop_GDDCDC(-9.0)               # CDC in GDD (fraction per GDD)

    SetCrop_Assimilates_On(False)    # No transfer of assimilates to roots
    SetCrop_Assimilates_Period(0)    # Days before end of season at which storage starts
    SetCrop_Assimilates_Stored(0)    # % of assimilates transferred to roots at end of season
    SetCrop_Assimilates_Mobilized(0) # % stored assimilates mobilized next season

    if use_default_crop_file:
        SetCropFileFull(GetPathNameSimul() + 'DEFAULT.CRO')
        SaveCrop(GetCropFileFull())
