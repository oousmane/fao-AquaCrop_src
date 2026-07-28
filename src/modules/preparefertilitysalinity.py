from ._global import *
from ._global import _strip_quotes
from .tempprocessing import GDDCDCToCDC
from .tempprocessing import CropStressParametersSoilSalinity
from .tempprocessing import GrowingDegreeDays
from .tempprocessing import Bnormalized
from dataclasses import dataclass
import math

@dataclass
class StressIndexes:
    CCxReduction: int = 0
    # Undocumented
    SaltProc: float = 0.0
    # Undocumented
    SaltSquare: float = 0.0


def StressBiomassRelationshipForTnxReference(TheDaysToCCini, TheGDDaysToCCini,
            L0, L12, L123, L1234, LFlor, LengthFlor, GDDL0, GDDL12,
            GDDL123, GDDL1234, WPyield, RefHI, CCo, CCx, CGC, GDDCGC,
            CDC, GDDCDC, KcTop, KcDeclAgeingCumul, CCeffectProcent,
            Tbase, Tupper, TDayMin, TDayMax, GDtranspLow, WPveg, RatedHIdt,
            CO2TnxReferenceYear, RefCropDay1, CropDeterm, CropSResp, TheCropType,
            TheModeCycle, b0, b1, b2,
            BM10, BM20, BM30, BM40, BM50, BM60, BM70):

    StressMatrix = [StressIndexes(0, 0.0, 0.0) for _ in range(8)]
    Si = 0
    L12SF = 0
    GDDL12SF = 0
    StressResponse = GetSimulation_EffectStress()
    RatDGDD = 0.0
    BNor = 0.0
    BNor100 = 0.0
    Yavg = 0.0
    X1avg = 0.0
    X2avg = 0.0
    y = 0.0
    x1 = 0.0
    x2 = 0.0
    x1y = 0.0
    x2y = 0.0
    x1Sq = 0.0
    x2Sq = 0.0
    x1x2 = 0.0
    SUMx1y = 0.0
    SUMx2y = 0.0
    SUMx1Sq = 0.0
    SUMx2Sq = 0.0
    SUMx1x2 = 0.0
    SiPr = 0
    SumKcTop = 0.0
    HIGC = 0.0
    HIGClinear = 0.0
    DaysYieldFormation = 0
    tSwitch = 0
    TDayMax_temp = 0.0
    TDayMin_temp = 0.0

    # 1. initialize
    SetSimulation_DelayedDays(0)  # required for CalculateETpot
    L12SF = L12  # to calculate SumKcTop (no stress)
    GDDL12SF = GDDL12  # to calculate SumKcTop (no stress)
    # Maximum sum Kc (no stress)
    SumKcTop = SeasonalSumOfKcPot(TheDaysToCCini, TheGDDaysToCCini,
        L0, L12, L123, L1234, L1234, GDDL0, GDDL12, GDDL123, GDDL1234,
        CCo, CCx, CGC, GDDCGC, CDC, GDDCDC, KcTop, KcDeclAgeingCumul,
        CCeffectProcent, Tbase, Tupper, TDayMin, TDayMax,
        GDtranspLow, CO2TnxReferenceYear, TheModeCycle, True)

    # Get PercentLagPhase (for estimate WPi during yield formation)
    if (TheCropType == subkind_Tuber) or (TheCropType == subkind_Grain):
        # DaysToFlowering corresponds with Tuberformation
        DaysYieldFormation = roundc(RefHI / RatedHIdt, mold=1)
        if CropDeterm:
            HIGC = HarvestIndexGrowthCoefficient(float(RefHI), RatedHIdt)
            tSwitch, HIGClinear = GetDaySwitchToLinear(RefHI, RatedHIdt, HIGC)
        else:
            tSwitch = roundc(DaysYieldFormation / 3.0, mold=1)

    # 2. Biomass production for various stress levels
    for Si in range(1, 8 + 1):
        # various stress levels
        # stress effect
        SiPr = int(10 * (Si - 1))
        StressMatrix[Si - 1].StressProc = SiPr
        StressResponse = CropStressParametersSoilFertility(CropSResp, SiPr, StressResponse)
        # adjusted length of Max canopy cover
        RatDGDD = 1
        if (StressResponse.RedCCX == 0) and (StressResponse.RedCGC == 0):
            L12SF = L12
            GDDL12SF = GDDL12
        else:
            (
                L12SF,
                RedCGC_temp,
                RedCCX_temp,
                FertStress,
            ) = TimeToMaxCanopySF(CCo, CGC, CCx, L0, L12, L123, LFlor,
                   LengthFlor, CropDeterm, L12SF, StressResponse.RedCGC,
                   StressResponse.RedCCX, SiPr)
            if TheModeCycle == ModeCycle_GDDays:
                TDayMin_temp = TDayMin
                TDayMax_temp = TDayMax
                GDDL12SF = SumCalendarDaysReferenceTnx(L12SF, RefCropDay1, RefCropDay1, Tbase, Tupper,
                                 TDayMin_temp, TDayMax_temp)
            if (TheModeCycle == ModeCycle_GDDays) and (GDDL12SF < GDDL123):
                RatDGDD = (L123 - L12SF) * 1.0 / (GDDL123 - GDDL12SF)
        # biomass production
        BNor = Bnormalized(TheDaysToCCini, TheGDDaysToCCini,
                L0, L12, L12SF, L123, L1234, L1234, LFlor,
                GDDL0, GDDL12, GDDL12SF, GDDL123, GDDL1234, WPyield,
                DaysYieldFormation, tSwitch, CCo, CCx, CGC, GDDCGC, CDC,
                GDDCDC, KcTop, KcDeclAgeingCumul, CCeffectProcent, WPveg, CO2TnxReferenceYear,
                Tbase, Tupper, TDayMin, TDayMax, GDtranspLow, RatDGDD,
                SumKcTop, SiPr, StressResponse.RedCGC, StressResponse.RedCCX,
                StressResponse.RedWP, StressResponse.RedKsSto, 0, 0,
                StressResponse.CDecline, -0.01, TheModeCycle, True,
                True)
        if Si == 1:
            BNor100 = BNor
            StressMatrix[0].BioMProc = 100.0
        else:
            if BNor100 > 0.00001:
                StressMatrix[Si - 1].BioMProc = 100.0 * BNor / BNor100
            else:
                StressMatrix[Si - 1].BioMProc = 100.0
        StressMatrix[Si - 1].BioMSquare = \
             StressMatrix[Si - 1].BioMProc * \
             StressMatrix[Si - 1].BioMProc
        # end stress level

    # 5. Stress - Biomass relationship
    Yavg = 0.0
    X1avg = 0.0
    X2avg = 0.0
    for Si in range(1, 8 + 1):
        # various stress levels
        Yavg = Yavg + StressMatrix[Si - 1].StressProc
        X1avg = X1avg + StressMatrix[Si - 1].BioMProc
        X2avg = X2avg + StressMatrix[Si - 1].BioMSquare
    Yavg = Yavg / 8.0
    X1avg = X1avg / 8.0
    X2avg = X2avg / 8.0
    SUMx1y = 0.0
    SUMx2y = 0.0
    SUMx1Sq = 0.0
    SUMx2Sq = 0.0
    SUMx1x2 = 0.0
    for Si in range(1, 8 + 1):
        # various stress levels
        y = StressMatrix[Si - 1].StressProc - Yavg
        x1 = StressMatrix[Si - 1].BioMProc - X1avg
        x2 = StressMatrix[Si - 1].BioMSquare - X2avg
        x1y = x1 * y
        x2y = x2 * y
        x1Sq = x1 * x1
        x2Sq = x2 * x2
        x1x2 = x1 * x2
        SUMx1y = SUMx1y + x1y
        SUMx2y = SUMx2y + x2y
        SUMx1Sq = SUMx1Sq + x1Sq
        SUMx2Sq = SUMx2Sq + x2Sq
        SUMx1x2 = SUMx1x2 + x1x2

    if abs(roundc(SUMx1x2 * 1000.0, mold=1)) != 0:
        b2 = (SUMx1y - (SUMx2y * SUMx1Sq) / SUMx1x2) / \
             (SUMx1x2 - (SUMx1Sq * SUMx2Sq) / SUMx1x2)
        b1 = (SUMx1y - b2 * SUMx1x2) / SUMx1Sq
        b0 = Yavg - b1 * X1avg - b2 * X2avg

        BM10 = StressMatrix[1].BioMProc
        BM20 = StressMatrix[2].BioMProc
        BM30 = StressMatrix[3].BioMProc
        BM40 = StressMatrix[4].BioMProc
        BM50 = StressMatrix[5].BioMProc
        BM60 = StressMatrix[6].BioMProc
        BM70 = StressMatrix[7].BioMProc
    else:
        b2 = float(undef_int)
        b1 = float(undef_int)
        b0 = float(undef_int)

    return b0, b1, b2, BM10, BM20, BM30, BM40, BM50, BM60, BM70

def ReferenceStressBiomassRelationship(
    TheDaysToCCini,
    TheGDDaysToCCini,
    L0,
    L12,
    L123,
    L1234,
    LFlor,
    LengthFlor,
    GDDL0,
    GDDL12,
    GDDL123,
    GDDL1234,
    WPyield,
    RefHI,
    CCo,
    CCx,
    CGC,
    GDDCGC,
    CDC,
    GDDCDC,
    KcTop,
    KcDeclAgeingCumul,
    CCeffectProcent,
    Tbase,
    Tupper,
    TDayMin,
    TDayMax,
    GDtranspLow,
    WPveg,
    RatedHIdt,
    CropDNr1,
    CropDeterm,
    CropSResp,
    TheCropType,
    TheModeCycle,
    b0,
    b1,
    b2,
    BM10,
    BM20,
    BM30,
    BM40,
    BM50,
    BM60,
    BM70,
    GDDFlor,
    GDDLengthFlor,
    GDDHImax,
    ThePlanting,
    LHImax,
):

    RefCropDay1 = 0
    Dayi = 0
    Monthi = 0
    Yeari = 0

    CO2TnxReferenceYear = 0.0

    L0_loc = L0
    L12_loc = L12
    LFlor_loc = LFlor
    LengthFlor_loc = LengthFlor
    L123_loc = L123
    L1234_loc = L1234
    LHImax_loc = LHImax
    CGC_loc = CGC
    CDC_loc = CDC
    RatedHIdt_loc = RatedHIdt

    # 1. Day 1 of the GrowingCycle
    Dayi, Monthi, Yeari = DetermineDate(CropDNr1)
    RefCropDay1 = DetermineDayNr(Dayi, Monthi, 1901)  # not linked to a specific year

    # 2. Create TCropReference.SIM (i.e. daily mean Tnx for 365 days from Onset onwards)
    if GetTnxReferenceFile() != "(None)":
        DailyTnxReferenceFileCoveringCropPeriod(RefCropDay1)

    # 3. Determine coresponding calendar days if crop cycle is defined in GDDays
    if TheModeCycle == ModeCycle_GDDays:
        (
            L0_loc,
            L12_loc,
            LFlor_loc,
            LengthFlor_loc,
            L123_loc,
            L1234_loc,
            LHImax_loc,
            CGC_loc,
            CDC_loc,
            RatedHIdt_loc,
        ) = AdjustCalendarDaysReferenceTnx(
            RefCropDay1,
            TheCropType,
            Tbase,
            Tupper,
            TDayMin,
            TDayMax,
            GDDL0,
            GDDL12,
            GDDFlor,
            GDDLengthFlor,
            GDDL123,
            GDDL1234,
            GDDHImax,
            GDDCGC,
            GDDCDC,
            CCo,
            CCx,
            RefHI,
            TheDaysToCCini,
            TheGDDaysToCCini,
            ThePlanting,
            L0_loc,
            L12_loc,
            LFlor_loc,
            LengthFlor_loc,
            L123_loc,
            L1234_loc,
            LHImax_loc,
            CGC_loc,
            CDC_loc,
            RatedHIdt_loc,
        )

    # 4. CO2 concentration for TnxReferenceYear
    if GetTnxReferenceYear() == 2000:
        CO2TnxReferenceYear = CO2Ref
    else:
        CO2TnxReferenceYear = CO2ForTnxReferenceYear(GetTnxReferenceYear())

    # 5. Stress Biomass relationship
    (
        b0,
        b1,
        b2,
        BM10,
        BM20,
        BM30,
        BM40,
        BM50,
        BM60,
        BM70,
    ) = StressBiomassRelationshipForTnxReference(
        TheDaysToCCini,
        TheGDDaysToCCini,
        L0_loc,
        L12_loc,
        L123_loc,
        L1234_loc,
        LFlor_loc,
        LengthFlor_loc,
        GDDL0,
        GDDL12,
        GDDL123,
        GDDL1234,
        WPyield,
        RefHI,
        CCo,
        CCx,
        CGC_loc,
        GDDCGC,
        CDC_loc,
        GDDCDC,
        KcTop,
        KcDeclAgeingCumul,
        CCeffectProcent,
        Tbase,
        Tupper,
        TDayMin,
        TDayMax,
        GDtranspLow,
        WPveg,
        RatedHIdt_loc,
        CO2TnxReferenceYear,
        RefCropDay1,
        CropDeterm,
        CropSResp,
        TheCropType,
        TheModeCycle,
        b0,
        b1,
        b2,
        BM10,
        BM20,
        BM30,
        BM40,
        BM50,
        BM60,
        BM70,
    )

    return (
        b0,
        b1,
        b2,
        BM10,
        BM20,
        BM30,
        BM40,
        BM50,
        BM60,
        BM70,
    )

def ReferenceCCxSaltStressRelationship(
    TheDaysToCCini,
    TheGDDaysToCCini,
    L0,
    L12,
    L123,
    L1234,
    LFlor,
    LengthFlor,
    GDDFlor,
    GDDLengthFlor,
    GDDL0,
    GDDL12,
    GDDL123,
    GDDL1234,
    WPyield,
    RefHI,
    CCo,
    CCx,
    CGC,
    GDDCGC,
    CDC,
    GDDCDC,
    KcTop,
    KcDeclAgeingCumul,
    CCeffectProcent,
    Tbase,
    Tupper,
    TDayMin,
    TDayMax,
    GDbioLow,
    WPveg,
    RatedHIdt,
    CropDNr1,
    CropDeterm,
    TheCropType,
    TheModeCycle,
    TheCCsaltDistortion,
    Coeffb0Salt,
    Coeffb1Salt,
    Coeffb2Salt,
    Salt10,
    Salt20,
    Salt30,
    Salt40,
    Salt50,
    Salt60,
    Salt70,
    Salt80,
    Salt90,
    GDDHImax,
    ThePlanting,
    LHImax,
):

    RefCropDay1 = 0
    Dayi = 0
    Monthi = 0
    Yeari = 0
    CO2TnxReferenceYear = 0.0

    L0_loc = L0
    L12_loc = L12
    L123_loc = L123
    L1234_loc = L1234
    LFlor_loc = LFlor
    LengthFlor_loc = LengthFlor
    LHImax_loc = LHImax
    CGC_loc = CGC
    CDC_loc = CDC
    RatedHIdt_loc = RatedHIdt

    # 1. Day 1 of the GrowingCycle
    Dayi, Monthi, Yeari = DetermineDate(CropDNr1)
    RefCropDay1 = DetermineDayNr(Dayi, Monthi, 1901)  # not linked to a specific year

    # 2. Create TCropReference.SIM (i.e. daily mean Tnx for 365 days from Onset onwards)
    if GetTnxReferenceFile() != "(None)":
        DailyTnxReferenceFileCoveringCropPeriod(RefCropDay1)

    # 3. Determine corresponding calendar days if crop cycle is defined in GDDays
    if TheModeCycle == ModeCycle_GDDays:
        (
            L0_loc,
            L12_loc,
            LFlor_loc,
            LengthFlor_loc,
            L123_loc,
            L1234_loc,
            LHImax_loc,
            CGC_loc,
            CDC_loc,
            RatedHIdt_loc,
        ) = AdjustCalendarDaysReferenceTnx(
            RefCropDay1,
            TheCropType,
            Tbase,
            Tupper,
            TDayMin,
            TDayMax,
            GDDL0,
            GDDL12,
            GDDFlor,
            GDDLengthFlor,
            GDDL123,
            GDDL1234,
            GDDHImax,
            GDDCGC,
            GDDCDC,
            CCo,
            CCx,
            RefHI,
            TheDaysToCCini,
            TheGDDaysToCCini,
            ThePlanting,
            L0_loc,
            L12_loc,
            LFlor_loc,
            LengthFlor_loc,
            L123_loc,
            L1234_loc,
            LHImax_loc,
            CGC_loc,
            CDC_loc,
            RatedHIdt_loc,
        )

    # 4. CO2 concentration for TnxReferenceYear
    if GetTnxReferenceYear() == 2000:
        CO2TnxReferenceYear = CO2Ref
    else:
        CO2TnxReferenceYear = CO2ForTnxReferenceYear(GetTnxReferenceYear())

    # 5. Stress Biomass relationship for salinity
    (
        Coeffb0Salt,
        Coeffb1Salt,
        Coeffb2Salt,
        Salt10,
        Salt20,
        Salt30,
        Salt40,
        Salt50,
        Salt60,
        Salt70,
        Salt80,
        Salt90,
    ) = CCxSaltStressRelationshipForTnxReference(
        TheDaysToCCini,
        TheGDDaysToCCini,
        L0_loc,
        L12_loc,
        L123_loc,
        L1234_loc,
        LFlor_loc,
        LengthFlor_loc,
        GDDFlor,
        GDDLengthFlor,
        GDDL0,
        GDDL12,
        GDDL123,
        GDDL1234,
        WPyield,
        RefHI,
        CCo,
        CCx,
        CGC_loc,
        GDDCGC,
        CDC_loc,
        GDDCDC,
        KcTop,
        KcDeclAgeingCumul,
        CCeffectProcent,
        Tbase,
        Tupper,
        TDayMin,
        TDayMax,
        GDbioLow,
        WPveg,
        RatedHIdt_loc,
        CO2TnxReferenceYear,
        CropDNr1,
        CropDeterm,
        TheCropType,
        TheModeCycle,
        TheCCsaltDistortion,
        Coeffb0Salt,
        Coeffb1Salt,
        Coeffb2Salt,
        Salt10,
        Salt20,
        Salt30,
        Salt40,
        Salt50,
        Salt60,
        Salt70,
        Salt80,
        Salt90,
    )

    return (
        Coeffb0Salt,
        Coeffb1Salt,
        Coeffb2Salt,
        Salt10,
        Salt20,
        Salt30,
        Salt40,
        Salt50,
        Salt60,
        Salt70,
        Salt80,
        Salt90,
    )

def DailyTnxReferenceFileCoveringCropPeriod(CropFirstDay: int):
    DayNr1 = 0
    Dayi = 0
    Monthi = 0
    Yeari = 0
    i = 0
    Tlow = 0.0
    Thigh = 0.0

    # Match Fortran:
    # if (FileExists(GetTnxReferenceFileFull()) .or. (GetTnxReferenceFile() == '(External)')) then
    TnxReferenceFileFull_stripped = _strip_quotes(GetTnxReferenceFileFull())
    if os.path.isabs(TnxReferenceFileFull_stripped):
        TnxReferenceFileFull_path = os.path.normpath(TnxReferenceFileFull_stripped)
    else:
        TnxReferenceFileFull_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                TnxReferenceFileFull_stripped.lstrip("/\\"),
            )
        )
    TnxReferenceFileFull_exists = FileExists(TnxReferenceFileFull_path)

    if TnxReferenceFileFull_exists or (GetTnxReferenceFile() == "(External)"):
        # CropFirstDay = DayNr1 in undefined year
        Dayi, Monthi, Yeari = DetermineDate(CropFirstDay)
        DayNr1 = DetermineDayNr(Dayi, Monthi, 1901)

        lines_out = []
        write_out = (GetTnxReferenceFile() != "(External)")

        if write_out:
            # create SIM file
            PathNameSimul_stripped = _strip_quotes(GetPathNameSimul())
            if os.path.isabs(PathNameSimul_stripped):
                out_full_path = os.path.normpath(os.path.join(PathNameSimul_stripped, "TCropReference.SIM"))
            else:
                out_full_path = os.path.normpath(
                    os.path.join(
                        complete_path_dir,
                        PathNameSimul_stripped.lstrip("/\\"),
                        "TCropReference.SIM",
                    )
                )

        i = 0

        for Dayi in range(DayNr1, 365 + 1):
            i += 1
            Tlow = float(GetTminTnxReference365DaysRun_i(Dayi))
            Thigh = float(GetTmaxTnxReference365DaysRun_i(Dayi))
            SetTminCropReferenceRun_i(i, Tlow)
            SetTmaxCropReferenceRun_i(i, Thigh)
            if write_out:
                lines_out.append(f"{Tlow:10.2f} {Thigh:10.2f}".strip())

        for Dayi in range(1, DayNr1):
            i += 1
            Tlow = float(GetTminTnxReference365DaysRun_i(Dayi))
            Thigh = float(GetTmaxTnxReference365DaysRun_i(Dayi))
            SetTminCropReferenceRun_i(i, Tlow)
            SetTmaxCropReferenceRun_i(i, Thigh)
            if write_out:
                lines_out.append(f"{Tlow:10.2f} {Thigh:10.2f}".strip())

        if write_out:
            # Single disk write (bulk)
            with open(out_full_path, "w", encoding="utf-8", errors="replace") as f:
                if len(lines_out) > 0:
                    f.write("\n".join(lines_out) + "\n")

def AdjustCalendarDaysReferenceTnx(
    PlantDayNr: int,
    TheCropType: int,
    Tbase: float,
    Tupper: float,
    TDayMin: float,
    TDayMax: float,
    GDDL0: int,
    GDDL12: int,
    GDDFlor: int,
    GDDLengthFlor: int,
    GDDL123: int,
    GDDL1234: int,
    GDDHImax: int,
    GDDCGC: float,
    GDDCDC: float,
    CCo: float,
    CCx: float,
    RefHI: int,
    TheDaysToCCini: int,
    TheGDDaysToCCini: int,
    ThePlanting: int,
    L0: int,
    L12: int,
    LFlor: int,
    LengthFlor: int,
    L123: int,
    L1234: int,
    LHImax: int,
    CGC: float,
    CDC: float,
    RatedHIdt: float,
):
    ExtraGDDays = 0
    ExtraDays = 0

    if TheDaysToCCini == 0:
        # planting/sowing
        L0 = SumCalendarDaysReferenceTnx(
            GDDL0, PlantDayNr, PlantDayNr, Tbase, Tupper, TDayMin, TDayMax
        )
        L12 = SumCalendarDaysReferenceTnx(
            GDDL12, PlantDayNr, PlantDayNr, Tbase, Tupper, TDayMin, TDayMax
        )
    else:
        # regrowth
        if TheDaysToCCini > 0:
            # CCini < CCx
            ExtraGDDays = GDDL12 - GDDL0 - TheGDDaysToCCini
            ExtraDays = SumCalendarDaysReferenceTnx(
                ExtraGDDays, PlantDayNr, PlantDayNr, Tbase, Tupper, TDayMin, TDayMax
            )
            L12 = L0 + TheDaysToCCini + ExtraDays

    if TheCropType != subkind_Forage:
        L123 = SumCalendarDaysReferenceTnx(
            GDDL123, PlantDayNr, PlantDayNr, Tbase, Tupper, TDayMin, TDayMax
        )
        L1234 = SumCalendarDaysReferenceTnx(
            GDDL1234, PlantDayNr, PlantDayNr, Tbase, Tupper, TDayMin, TDayMax
        )

    if (TheCropType == subkind_Grain) or (TheCropType == subkind_Tuber):
        LFlor = SumCalendarDaysReferenceTnx(
            GDDFlor, PlantDayNr, PlantDayNr, Tbase, Tupper, TDayMin, TDayMax
        )
        if TheCropType == subkind_Grain:
            LengthFlor = SumCalendarDaysReferenceTnx(
                GDDLengthFlor,
                PlantDayNr,
                PlantDayNr + LFlor,
                Tbase,
                Tupper,
                TDayMin,
                TDayMax,
            )
        else:
            LengthFlor = 0

        LHImax = SumCalendarDaysReferenceTnx(
            GDDHImax,
            PlantDayNr,
            PlantDayNr + LFlor,
            Tbase,
            Tupper,
            TDayMin,
            TDayMax,
        )

    elif (TheCropType == subkind_Vegetative) or (TheCropType == subkind_Forage):
        LHImax = SumCalendarDaysReferenceTnx(
            GDDHImax, PlantDayNr, PlantDayNr, Tbase, Tupper, TDayMin, TDayMax
        )

    CGC = (float(GDDL12) / float(L12)) * float(GDDCGC)

    CDC = GDDCDCToCDC(
        PlantDayNr,
        L123,
        GDDL123,
        GDDL1234,
        CCx,
        GDDCDC,
        Tbase,
        Tupper,
        TDayMin,
        TDayMax,
        CDC,
        True,
    )

    if (TheCropType == subkind_Grain) or (TheCropType == subkind_Tuber):
        RatedHIdt = float(RefHI) / float(LHImax)

    if (TheCropType == subkind_Vegetative) or (TheCropType == subkind_Forage):
        if LHImax > 0:
            if LHImax > L1234:
                RatedHIdt = float(RefHI) / float(L1234)
            else:
                RatedHIdt = float(RefHI) / float(LHImax)

            if RatedHIdt > 100.0:
                RatedHIdt = 100.0  # 100 is maximum TempdHIdt (See SetdHIdt)
                LHImax = 0
        else:
            RatedHIdt = 100.0  # 100 is maximum TempdHIdt (See SetdHIdt)
            LHImax = 0

    return (
        L0,
        L12,
        LFlor,
        LengthFlor,
        L123,
        L1234,
        LHImax,
        CGC,
        CDC,
        RatedHIdt,
    )

def CO2ForTnxReferenceYear(TnxReferenceYear: int):
    i = 0
    rc = 0
    TempString = ""
    TheCO2 = 0.0
    CO2a = 0.0
    CO2b = 0.0
    YearA = 0.0
    YearB = 0.0

    if TnxReferenceYear == 2000:
        TheCO2 = CO2Ref
    else:
        # Single disk read (bulk) + mimic Fortran list-directed reads skipping blank lines
        full_path = os.path.normpath(
            os.path.join(
                complete_path_dir,
                _strip_quotes(GetCO2FileFull()).lstrip("/\\"),
            )
        )
        with open(full_path, "r", encoding="utf-8", errors="replace") as fhandle:
            lines = [ln.strip() for ln in fhandle.read().splitlines() if ln.strip() != ""]

        pos = 0

        # do i=1,3  read(...)  ! Description and Title
        pos += 3

        # read(fhandle, '(a)') TempString
        TempString = lines[pos]
        pos += 1

        YearB, CO2b = SplitStringInTwoParams(TempString.strip(), 0.0, 0.0)

        if int(roundc(YearB, mold="int32")) >= TnxReferenceYear:
            TheCO2 = CO2b
        else:
            while True:
                YearA = YearB
                CO2a = CO2b

                if pos >= len(lines):
                    break

                TempString = lines[pos]
                pos += 1
                YearB, CO2b = SplitStringInTwoParams(TempString.strip(), 0.0, 0.0)

                if int(roundc(YearB, mold="int32")) >= TnxReferenceYear:
                    break

            if TnxReferenceYear > int(roundc(YearB, mold="int32")):
                TheCO2 = CO2b
            else:
                den = int(roundc(YearB, mold="int32")) - int(roundc(YearA, mold="int32"))
                if den == 0:
                    TheCO2 = CO2b
                else:
                    TheCO2 = CO2a + (CO2b - CO2a) * (
                        (TnxReferenceYear - int(roundc(YearA, mold="int32"))) / float(den)
                    )

    return float(TheCO2)


def CCxSaltStressRelationshipForTnxReference(
    TheDaysToCCini: int,
    TheGDDaysToCCini: int,
    L0: int,
    L12: int,
    L123: int,
    L1234: int,
    LFlor: int,
    LengthFlor: int,
    GDDFlor: int,
    GDDLengthFlor: int,
    GDDL0: int,
    GDDL12: int,
    GDDL123: int,
    GDDL1234: int,
    WPyield: int,
    RefHI: int,
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
    GDbioLow: float,
    WPveg: float,
    RatedHIdt: float,
    CO2TnxReferenceYear: float,
    CropDNr1: int,
    CropDeterm: bool,
    TheCropType: int,
    TheModeCycle: int,
    TheCCsaltDistortion: int,
    Coeffb0Salt: float,
    Coeffb1Salt: float,
    Coeffb2Salt: float,
    Salt10: float,
    Salt20: float,
    Salt30: float,
    Salt40: float,
    Salt50: float,
    Salt60: float,
    Salt70: float,
    Salt80: float,
    Salt90: float,
):
    # 1. initialize
    SetSimulation_DelayedDays(0)  # required for CalculateETpot
    GDDL12SS = GDDL12  # to calculate SumKcTop (no stress)
    BNor100 = float(undef_int)  # real(undef_int, kind=dp)

    # Maximum sum Kc (no stress)
    SumKcTop = SeasonalSumOfKcPot(
        TheDaysToCCini,
        TheGDDaysToCCini,
        L0,
        L12,
        L123,
        L1234,
        L1234,
        GDDL0,
        GDDL12,
        GDDL123,
        GDDL1234,
        CCo,
        CCx,
        CGC,
        GDDCGC,
        CDC,
        GDDCDC,
        KcTop,
        KcDeclAgeingCumul,
        CCeffectProcent,
        Tbase,
        Tupper,
        TDayMin,
        TDayMax,
        GDbioLow,
        CO2TnxReferenceYear,
        TheModeCycle,
        True,
    )

    DaysYieldFormation = 0
    tSwitch = 0
    HIGC = 0.0
    HIGClinear = 0.0

    # Get PercentLagPhase (for estimate WPi during yield formation)
    if (TheCropType == subkind_Tuber) or (TheCropType == subkind_Grain):
        # DaysToFlowering corresponds with Tuberformation
        DaysYieldFormation = int(roundc(RefHI / RatedHIdt, mold="int32"))
        if CropDeterm:
            HIGC = HarvestIndexGrowthCoefficient(float(RefHI), RatedHIdt)
            tSwitch, HIGClinear = GetDaySwitchToLinear(RefHI, RatedHIdt, HIGC)
        else:
            tSwitch = int(roundc(DaysYieldFormation / 3.0, mold="int32"))

    # 2. Biomass production (or Salt stress) for various CCx reductions
    StressMatrix = [StressIndexes() for _ in range(10 + 1)]  # 1-based (1..10)

    for Si in range(1, 10 + 1):
        # various CCx reduction
        SiPr = int(10 * (Si - 1))
        StressMatrix[Si].CCxReduction = int(SiPr)

        # adjustment CC
        StressResponse = rep_EffectStress()
        ret = CropStressParametersSoilSalinity(
            int(SiPr),
            TheCCsaltDistortion,
            CCo,
            CCx,
            CGC,
            GDDCGC,
            CropDeterm,
            L12,
            LFlor,
            LengthFlor,
            L123,
            GDDL12,
            GDDFlor,
            GDDLengthFlor,
            GDDL123,
            TheModeCycle,
            StressResponse,
        )
        if ret is not None:
            StressResponse = ret

        # adjusted length of Max canopy cover
        RatDGDD = 1.0
        if (StressResponse.RedCCX == 0) and (StressResponse.RedCGC == 0):
            L12SS = L12
            GDDL12SS = GDDL12
        else:
            CCToReach = 0.98 * (1.0 - StressResponse.RedCCX / 100.0) * CCx
            L12SS = DaysToReachCCwithGivenCGC(
                CCToReach,
                CCo,
                (1.0 - StressResponse.RedCCX / 100.0) * CCx,
                CGC * (1.0 - StressResponse.RedCGC / 100.0),
                L0,
            )

            if TheModeCycle == ModeCycle_GDDays:
                TDayMax_temp = TDayMax
                TDayMin_temp = TDayMin
                GDDL12SS = GrowingDegreeDays(L12SS, CropDNr1, Tbase, Tupper, TDayMin_temp, TDayMax_temp)

            if (TheModeCycle == ModeCycle_GDDays) and (GDDL12SS < GDDL123):
                RatDGDD = (L123 - L12SS) * 1.0 / float(GDDL123 - GDDL12SS)

        # biomass production
        BNor = Bnormalized(
            TheDaysToCCini,
            TheGDDaysToCCini,
            L0,
            L12,
            L12SS,
            L123,
            L1234,
            L1234,
            LFlor,
            GDDL0,
            GDDL12,
            GDDL12SS,
            GDDL123,
            GDDL1234,
            WPyield,
            DaysYieldFormation,
            tSwitch,
            CCo,
            CCx,
            CGC,
            GDDCGC,
            CDC,
            GDDCDC,
            KcTop,
            KcDeclAgeingCumul,
            CCeffectProcent,
            WPveg,
            CO2TnxReferenceYear,
            Tbase,
            Tupper,
            TDayMin,
            TDayMax,
            GDbioLow,
            RatDGDD,
            SumKcTop,
            SiPr,
            StressResponse.RedCGC,
            StressResponse.RedCCX,
            StressResponse.RedWP,
            StressResponse.RedKsSto,
            0,
            0,
            StressResponse.CDecline,
            -0.01,
            TheModeCycle,
            False,
            True,
        )

        if Si == 1:
            BNor100 = BNor
            StressMatrix[1].SaltProc = 0.0
        else:
            if BNor100 > 0.00001:
                BioMProc = 100.0 * BNor / BNor100
                StressMatrix[Si].SaltProc = 100.0 - BioMProc
            else:
                StressMatrix[Si].SaltProc = 0.0

        StressMatrix[Si].SaltSquare = StressMatrix[Si].SaltProc * StressMatrix[Si].SaltProc

    # 3. CCx - Salt stress relationship
    Yavg = 0.0
    X1avg = 0.0
    X2avg = 0.0

    for Si in range(1, 10 + 1):
        Yavg += StressMatrix[Si].CCxReduction
        X1avg += StressMatrix[Si].SaltProc
        X2avg += StressMatrix[Si].SaltSquare

    Yavg /= 10.0
    X1avg /= 10.0
    X2avg /= 10.0

    SUMx1y = 0.0
    SUMx2y = 0.0
    SUMx1Sq = 0.0
    SUMx2Sq = 0.0
    SUMx1x2 = 0.0

    for Si in range(1, 10 + 1):
        y = StressMatrix[Si].CCxReduction - Yavg
        x1 = StressMatrix[Si].SaltProc - X1avg
        x2 = StressMatrix[Si].SaltSquare - X2avg

        SUMx1y += x1 * y
        SUMx2y += x2 * y
        SUMx1Sq += x1 * x1
        SUMx2Sq += x2 * x2
        SUMx1x2 += x1 * x2

    if abs(int(roundc(SUMx1x2 * 1000.0, mold="int32"))) != 0:
        Coeffb2Salt = (SUMx1y - (SUMx2y * SUMx1Sq) / SUMx1x2) / (SUMx1x2 - (SUMx1Sq * SUMx2Sq) / SUMx1x2)
        Coeffb1Salt = (SUMx1y - Coeffb2Salt * SUMx1x2) / SUMx1Sq
        Coeffb0Salt = Yavg - Coeffb1Salt * X1avg - Coeffb2Salt * X2avg

        Salt10 = StressMatrix[2].SaltProc
        Salt20 = StressMatrix[3].SaltProc
        Salt30 = StressMatrix[4].SaltProc
        Salt40 = StressMatrix[5].SaltProc
        Salt50 = StressMatrix[5].SaltProc
        Salt60 = StressMatrix[7].SaltProc
        Salt70 = StressMatrix[8].SaltProc
        Salt80 = StressMatrix[9].SaltProc
        Salt90 = StressMatrix[10].SaltProc
    else:
        Coeffb2Salt = float(undef_int)
        Coeffb1Salt = float(undef_int)
        Coeffb0Salt = float(undef_int)

    return (
        Coeffb0Salt,
        Coeffb1Salt,
        Coeffb2Salt,
        Salt10,
        Salt20,
        Salt30,
        Salt40,
        Salt50,
        Salt60,
        Salt70,
        Salt80,
        Salt90,
    )

def MultiplierCCxSelfThinning(Yeari: int, Yearx: int, ShapeFactor: float) -> float:
    fCCx = 1.0

    if (Yeari >= 2) and (Yearx >= 2) and (roundc(100.0 * ShapeFactor, mold="int32") != 0):
        Year0 = 1.0 + (Yearx - 1.0) * math.exp(ShapeFactor * math.log(10.0))

        if Yeari >= Year0:
            fCCx = 0.0
        else:
            fCCx = 0.9 + 0.1 * (1.0 - math.exp((1.0 / ShapeFactor) * math.log((Yeari - 1.0) / (Yearx - 1.0))))

        if fCCx < 0.0:
            fCCx = 0.0

    return fCCx

import math

def CCmultiplierWeedAdjusted(
    ProcentWeedCover: int,      # int8
    CCxCrop: float,             # dp
    FshapeWeed: float,          # dp (note: in Fortran it's NOT intent(in); it can be modified locally)
    fCCx: float,                # dp
    Yeari: int,                 # int8
    MWeedAdj: int,              # int8
    RCadj: int,                 # int8 inout -> returned
):
    fWeedi = 1.0
    RCadj = ProcentWeedCover

    if ProcentWeedCover > 0:
        fWeedi = CCmultiplierWeed(ProcentWeedCover, CCxCrop, FshapeWeed)

        # FOR perennials when self-thinning
        if (GetCrop_subkind() == subkind_Forage) and (Yeari > 1) and (fCCx < 0.995):
            # need for adjustment
            # step 1 - adjusment of shape factor to degree of crop replacement by weeds
            FshapeMinimum = 10.0 - 20.0 * (
                (math.exp(fCCx * 3.0) - 1.0) / (math.exp(3.0) - 1.0)
                + math.sqrt(MWeedAdj / 100.0)
            )
            if roundc(FshapeMinimum * 10.0, mold="int32") == 0:
                FshapeMinimum = 0.1

            # keep behavior: clamp FshapeWeed to minimum
            if FshapeWeed < FshapeMinimum:
                FshapeWeed = FshapeMinimum

            # step 2 - Estimate of CCxTot
            # A. Total CC (crop and weeds) when self-thinning and 100% weed take over
            fWeedi = CCmultiplierWeed(ProcentWeedCover, CCxCrop, FshapeWeed)
            CCxTot100 = fWeedi * CCxCrop

            # B. Total CC (crop and weeds) when self-thinning and 0% weed take over
            if fCCx > 0.005:
                fWeedi = CCmultiplierWeed(
                    roundc(fCCx * ProcentWeedCover, mold="int8"),
                    (fCCx * CCxCrop),
                    FshapeWeed,
                )
            else:
                fWeedi = 1.0
            CCxTot0 = fWeedi * (fCCx * CCxCrop)

            # C. total CC (crop and weeds) with specified weed take over (MWeedAdj)
            CCxTotM = CCxTot0 + (CCxTot100 - CCxTot0) * (MWeedAdj / 100.0)
            if CCxTotM < (fCCx * CCxCrop * (1.0 - ProcentWeedCover / 100.0)):
                CCxTotM = fCCx * CCxCrop * (1.0 - ProcentWeedCover / 100.0)

            if fCCx > 0.005:
                fWeedi = CCxTotM / (fCCx * CCxCrop)
                fweedMax = 1.0 / (fCCx * CCxCrop)
                if roundc(fWeedi * 1000.0, mold="int32") > roundc(fweedMax * 1000.0, mold="int32"):
                    fWeedi = fweedMax

            # step 3 - Estimate of adjusted weed cover
            RCadjD = ProcentWeedCover + (1.0 - fCCx) * CCxCrop * MWeedAdj

            if fCCx > 0.005:
                lower = 100.0 * (CCxTotM - fCCx * CCxCrop) / CCxTotM
                upper = 100.0 * (1.0 - (fCCx * CCxCrop * (1.0 - ProcentWeedCover / 100.0) / CCxTotM))

                if RCadjD < lower:
                    RCadjD = lower
                if RCadjD > upper:
                    RCadjD = upper

            RCadj = roundc(RCadjD, mold="int8")
            if RCadj > 100:
                RCadj = 100

    return fWeedi, RCadj