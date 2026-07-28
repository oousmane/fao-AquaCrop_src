from ._global import *
from ._global import _strip_quotes
from dataclasses import dataclass

import math
import os


@dataclass
class rep_EventObsSim:
    Obsi: float
    # Undocumented

    StdObsi: float
    # Undocumented

    Simi: float
    # Undocumented

    DDi: int
    # Undocumented

    MMi: int
    # Undocumented

    YYYYi: int
    # Undocumented


def StatisticAnalysis(TypeObsSim, RangeObsMin, RangeObsMax, StrNr,
                      Nobs, ObsAver, SimAver, PearsonCoeff, RMSE,
                      NRMSE, NScoeff, IndexAg, ArrayObsSim):
    Nri = 0
    dDeNom = 0.0
    R2tel = 0.0
    SumSqrDobs = 0.0
    SumSqrDsim = 0.0
    SumSqrDiv = 0.0
    DeNom = 0.0

    # get data
    Nobs, ArrayObsSim, ObsAver, SimAver = GetObsSim(
        TypeObsSim,
        RangeObsMin,
        RangeObsMax,
        StrNr,
        Nobs,
        ArrayObsSim,
        ObsAver,
        SimAver,
    )

    # statistical evaluation
    if Nobs > 1:
        R2tel = 0.0
        SumSqrDobs = 0.0
        SumSqrDsim = 0.0
        SumSqrDiv = 0.0
        dDeNom = 0.0
        for Nri in range(1, Nobs + 1):
            R2tel = R2tel + (ArrayObsSim[Nri - 1].Obsi - ObsAver) * (ArrayObsSim[Nri - 1].Simi - SimAver)
            SumSqrDobs = SumSqrDobs + (ArrayObsSim[Nri - 1].Obsi - ObsAver) ** 2
            SumSqrDsim = SumSqrDsim + (ArrayObsSim[Nri - 1].Simi - SimAver) ** 2
            SumSqrDiv = SumSqrDiv + (ArrayObsSim[Nri - 1].Obsi - ArrayObsSim[Nri - 1].Simi) ** 2
            dDeNom = dDeNom + (
                abs(ArrayObsSim[Nri - 1].Simi - ObsAver) +
                abs(ArrayObsSim[Nri - 1].Obsi - ObsAver)
            ) ** 2

        # R2
        DeNom = math.sqrt(SumSqrDobs * SumSqrDsim)
        if DeNom > 0.0:
            PearsonCoeff = R2tel / DeNom
        else:
            PearsonCoeff = float(undef_int)

        # RMSE
        RMSE = math.sqrt(SumSqrDiv / Nobs)

        # NRMSE
        if ObsAver > 0.0:
            NRMSE = 100.0 * (RMSE / ObsAver)
        else:
            NRMSE = float(undef_int)

        # Nash-Sutcliffe coefficient (EF)
        if SumSqrDobs > 0.0:
            NScoeff = 1.0 - (SumSqrDiv / SumSqrDobs)
        else:
            NScoeff = float(undef_int)

        # Index of agreement (d)
        if dDeNom > 0.0:
            IndexAg = 1.0 - (SumSqrDiv / dDeNom)
        else:
            IndexAg = float(undef_int)
    else:
        ObsAver = float(undef_int)
        SimAver = float(undef_int)
        PearsonCoeff = float(undef_int)
        RMSE = float(undef_int)
        NRMSE = float(undef_int)
        NScoeff = float(undef_int)
        IndexAg = float(undef_int)

    return Nobs, ObsAver, SimAver, PearsonCoeff, RMSE, NRMSE, NScoeff, IndexAg, ArrayObsSim


def GetObsSim(TypeObsSim, RangeObsMin, RangeObsMax, StrNr, Nobs,
              ArrayObsSim, ObsAver, SimAver):
    OutputName = ""
    Nobs = 0
    ObsAver = 0.0
    SimAver = 0.0

    # open file
    OutputName = GetPathNameSimul() + "EvalData" + StrNr + ".OUT"
    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(OutputName).lstrip("/\\"),
        )
    )

    # number of dummy observation columns before Sim/Obs/StdObs
    if TypeObsSim == typeObsSim_ObsSimCC:
        NCobs = 2
    elif TypeObsSim == typeObsSim_ObsSimB:
        NCobs = 5
    elif TypeObsSim == typeObsSim_ObsSimSWC:
        NCobs = 8
    else:
        NCobs = 5

    min_cols = 6 + NCobs

    def is_valid_data_line(parts):
        if len(parts) < min_cols:
            return False

        try:
            # day, month, year
            int(parts[0])
            int(parts[1])
            int(parts[2])

            # dummy columns
            for j in range(3, 3 + NCobs):
                float(parts[j])

            # sim, obs, std
            float(parts[3 + NCobs])
            float(parts[4 + NCobs])
            float(parts[5 + NCobs])

            return True
        except (ValueError, IndexError):
            return False

    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        lines = f0.read().splitlines()

    # keep only real data rows
    data_lines = []
    for buffer in lines:
        parts = buffer.split()
        if is_valid_data_line(parts):
            data_lines.append(parts)

    # find first day relative to simulation start
    SkipLines = RangeObsMin - GetSimulation_FromDayNr()
    if SkipLines < 0:
        SkipLines = 0

    # number of days requested
    n_days = RangeObsMax - RangeObsMin + 1
    end_idx = min(SkipLines + n_days, len(data_lines))

    for idx in range(SkipLines, end_idx):
        parts = data_lines[idx]

        Dayi = int(parts[0])
        Monthi = int(parts[1])
        Yeari = int(parts[2])

        VarSimi = float(parts[3 + NCobs])
        VarObsi = float(parts[4 + NCobs])
        VarStdi = float(parts[5 + NCobs])

        if (roundc(VarObsi, mold=1) != undef_int) and (Nobs < 100):
            Nobs = Nobs + 1
            ArrayObsSim[Nobs - 1].DDi = Dayi
            ArrayObsSim[Nobs - 1].MMi = Monthi
            ArrayObsSim[Nobs - 1].YYYYi = Yeari
            ArrayObsSim[Nobs - 1].Simi = VarSimi
            ArrayObsSim[Nobs - 1].Obsi = VarObsi
            ArrayObsSim[Nobs - 1].StdObsi = VarStdi
            SimAver = SimAver + VarSimi
            ObsAver = ObsAver + VarObsi

    # calculate averages
    if Nobs > 0:
        ObsAver = ObsAver / float(Nobs)
        SimAver = SimAver / float(Nobs)

    return Nobs, ArrayObsSim, ObsAver, SimAver


def WriteAssessmentSimulation(StrNr, totalnameEvalStat, TheProjectType, RangeMin, RangeMax):
    fAssm = None
    TypeObsSim = 0
    Nobs = 0
    Nri = 0
    ObsAver = 0.0
    SimAver = 0.0
    PearsonCoeff = 0.0
    RMSE = 0.0
    NRMSE = 0.0
    NScoeff = 0.0
    IndexAg = 0.0
    ArrayObsSim = [rep_EventObsSim(0.0, 0.0, 0.0, 0, 0, 0) for _ in range(100)]
    YearString = ""

    # 1. Open file for assessment
    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(totalnameEvalStat).lstrip("/\\"),
        )
    )

    out_lines = []
    out_lines.append(GetAquaCropDescriptionWithTimeStamp())
    out_lines.append("Evaluation of simulation results - Statistics")
    if TheProjectType == typeproject_typeprm:
        out_lines.append(f"** Run number:{StrNr}")
    out_lines.append("")

    # 2. Run analysis

    # 2.1 Canopy Cover
    TypeObsSim = typeObsSim_ObsSimCC
    Nobs, ObsAver, SimAver, PearsonCoeff, RMSE, NRMSE, NScoeff, IndexAg, ArrayObsSim = StatisticAnalysis(
        TypeObsSim,
        RangeMin,
        RangeMax,
        StrNr,
        Nobs,
        ObsAver,
        SimAver,
        PearsonCoeff,
        RMSE,
        NRMSE,
        NScoeff,
        IndexAg,
        ArrayObsSim,
    )

    out_lines.append("")
    out_lines.append("  ASSESSMENT OF CANOPY COVER --------------------------------------")
    if Nobs > 1:
        out_lines.append("              --------- Canopy Cover (%) ---------")
        out_lines.append("    Nr        Observed    +/- St Dev     Simulated    Date")
        out_lines.append("  ----------------------------------------------------------------")
        for Nri in range(1, Nobs + 1):
            if ArrayObsSim[Nri - 1].YYYYi <= 1901:
                YearString = ""
            else:
                YearString = f"{ArrayObsSim[Nri - 1].YYYYi:4d}"
            out_lines.append(
                f"{Nri:6d}"
                f"{ArrayObsSim[Nri - 1].Obsi:14.1f}"
                f"{ArrayObsSim[Nri - 1].StdObsi:14.1f}"
                f"{ArrayObsSim[Nri - 1].Simi:14.1f}"
                f"      "
                f"{ArrayObsSim[Nri - 1].DDi:2d}"
                f" "
                f"{NameMonth(ArrayObsSim[Nri - 1].MMi).strip()}"
                f" "
                f"{YearString.rstrip()}"
            )
        out_lines.append("")
        out_lines.append(f"  Valid observations/simulations sets (n) ....... : {Nobs:5d}")
        out_lines.append(f"  Average of observed Canopy Cover .............. : {ObsAver:7.1f}   %")
        out_lines.append(f"  Average of simulated Canopy Cover ............. : {SimAver:7.1f}   %")
        out_lines.append("")
        out_lines.append(f"  Pearson Correlation Coefficient (r) ........... : {PearsonCoeff:8.2f}")
        out_lines.append(f"  Root mean square error (RMSE) ................. : {RMSE:7.1f}   % CC")
        out_lines.append(f"  Normalized root mean square error  CV(RMSE).... : {NRMSE:7.1f}   %")
        out_lines.append(f"  Nash-Sutcliffe model efficiency coefficient (EF): {NScoeff:8.2f}")
        out_lines.append(f"  Willmotts index of agreement (d) .............. : {IndexAg:8.2f}")
    else:
        out_lines.append("  No statistic analysis (insufficient data)")
    out_lines.append("  ----------------------------------------------------------------")

    # 2.2 Biomass production
    TypeObsSim = typeObsSim_ObsSimB
    Nobs, ObsAver, SimAver, PearsonCoeff, RMSE, NRMSE, NScoeff, IndexAg, ArrayObsSim = StatisticAnalysis(
        TypeObsSim,
        RangeMin,
        RangeMax,
        StrNr,
        Nobs,
        ObsAver,
        SimAver,
        PearsonCoeff,
        RMSE,
        NRMSE,
        NScoeff,
        IndexAg,
        ArrayObsSim,
    )
    out_lines.append("")
    out_lines.append("")
    out_lines.append("  ASSESSMENT OF BIOMASS PRODUCTION --------------------------------")
    if Nobs > 1:
        out_lines.append("              --------- Biomass (ton/ha) ---------")
        out_lines.append("    Nr        Observed    +/- St Dev     Simulated    Date")
        out_lines.append("  ----------------------------------------------------------------")
        for Nri in range(1, Nobs + 1):
            if ArrayObsSim[Nri - 1].YYYYi <= 1901:
                YearString = ""
            else:
                YearString = f"{ArrayObsSim[Nri - 1].YYYYi:4d}"
            out_lines.append(
                f"{Nri:6d}"
                f"{ArrayObsSim[Nri - 1].Obsi:16.3f}"
                f"{ArrayObsSim[Nri - 1].StdObsi:14.3f}"
                f"{ArrayObsSim[Nri - 1].Simi:14.3f}"
                f"      "
                f"{ArrayObsSim[Nri - 1].DDi:2d}"
                f" "
                f"{NameMonth(ArrayObsSim[Nri - 1].MMi).strip()}"
                f" "
                f"{YearString.rstrip()}"
            )
        out_lines.append("")
        out_lines.append(f"  Valid observations/simulations sets (n) ....... : {Nobs:5d}")
        out_lines.append(f"  Average of observed Biomass production ........ : {ObsAver:9.3f}   ton/ha")
        out_lines.append(f"  Average of simulated Biomass production ....... : {SimAver:9.3f}   ton/ha")
        out_lines.append("")
        out_lines.append(f"  Pearson Correlation Coefficient (r) ........... : {PearsonCoeff:8.2f}")
        out_lines.append(f"  Root mean square error (RMSE) ................. : {RMSE:9.3f}   ton/ha")
        out_lines.append(f"  Normalized root mean square error  CV(RMSE).... : {NRMSE:7.1f}   %")
        out_lines.append(f"  Nash-Sutcliffe model efficiency coefficient (EF): {NScoeff:8.2f}")
        out_lines.append(f"  Willmotts index of agreement (d) .............. : {IndexAg:8.2f}")
    else:
        out_lines.append("  No statistic analysis (insufficient data)")
    out_lines.append("  ----------------------------------------------------------------")

    # 2.3 Soil Water Content
    TypeObsSim = typeObsSim_ObsSimSWC
    Nobs, ObsAver, SimAver, PearsonCoeff, RMSE, NRMSE, NScoeff, IndexAg, ArrayObsSim = StatisticAnalysis(
        TypeObsSim,
        RangeMin,
        RangeMax,
        StrNr,
        Nobs,
        ObsAver,
        SimAver,
        PearsonCoeff,
        RMSE,
        NRMSE,
        NScoeff,
        IndexAg,
        ArrayObsSim,
    )
    out_lines.append("")
    out_lines.append("")
    out_lines.append("  ASSESSMENT OF SOIL WATER CONTENT --------------------------------")
    if Nobs > 1:
        out_lines.append("              ------ Soil water content (mm) -----")
        out_lines.append("    Nr        Observed    +/- St Dev     Simulated    Date")
        out_lines.append("  ----------------------------------------------------------------")
        for Nri in range(1, Nobs + 1):
            if ArrayObsSim[Nri - 1].YYYYi <= 1901:
                YearString = ""
            else:
                YearString = f"{ArrayObsSim[Nri - 1].YYYYi:4d}"
            out_lines.append(
                f"{Nri:6d}"
                f"{ArrayObsSim[Nri - 1].Obsi:14.1f}"
                f"{ArrayObsSim[Nri - 1].StdObsi:14.1f}"
                f"{ArrayObsSim[Nri - 1].Simi:14.1f}"
                f"      "
                f"{ArrayObsSim[Nri - 1].DDi:2d}"
                f" "
                f"{NameMonth(ArrayObsSim[Nri - 1].MMi).strip()}"
                f" "
                f"{YearString.rstrip()}"
            )
        out_lines.append("")
        out_lines.append(f"  Valid observations/simulations sets (n) ....... : {Nobs:5d}")
        out_lines.append(f"  Average of observed Soil water content ........ : {ObsAver:7.1f}   mm")
        out_lines.append(f"  Average of simulated Soil water content ....... : {SimAver:7.1f}   mm")
        out_lines.append("")
        out_lines.append(f"  Pearson Correlation Coefficient (r) ........... : {PearsonCoeff:8.2f}")
        out_lines.append(f"  Root mean square error (RMSE) ................. : {RMSE:7.1f}   mm")
        out_lines.append(f"  Normalized root mean square error  CV(RMSE).... : {NRMSE:7.1f}   %")
        out_lines.append(f"  Nash-Sutcliffe model efficiency coefficient (EF): {NScoeff:8.2f}")
        out_lines.append(f"  Willmotts index of agreement (d) .............. : {IndexAg:8.2f}")
    else:
        out_lines.append("  No statistic analysis (insufficient data)")
    out_lines.append("  ----------------------------------------------------------------")
    out_lines.append("")

    # 3. Close file for assessment
    with open(full_path, "w", encoding="utf-8", errors="replace") as f0:
        f0.write("\n".join(out_lines) + "\n")