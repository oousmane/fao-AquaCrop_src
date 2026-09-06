from ._global import *
from ._global import _strip_quotes
import sys

def GetParameters(C1, C2, C3, UL, LL, Mid):
    UL = (C1 + C2) / 2.0
    LL = (C2 + C3) / 2.0
    Mid = 2.0 * C2 - (UL + LL) / 2.0
    # --previous decade-->/UL/....... Mid ......../LL/<--next decade--

    return UL, LL, Mid

def GetDecadeEToDataSet(DayNri, EToDataSet):
    Nri = 0
    ni = 0
    Dayi = 0
    Deci = 0
    Monthi = 0
    Yeari = 0
    DayN = 0
    DNR = 0
    C1 = 0.0
    C2 = 0.0
    C3 = 0.0
    Ul = 0.0
    LL = 0.0
    Mid = 0.0

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

    C1, C2, C3 = GetSetofThree(DayN, Deci, Monthi, Yeari, C1, C2, C3)
    DNR = DetermineDayNr(Dayi, Monthi, Yeari)

    if abs(C2) < sys.float_info.epsilon:
        for Nri in range(1, ni + 1):
            EToDataSet[Nri - 1].DayNr = DNR + Nri - 1
            EToDataSet[Nri - 1].Param = 0.0
    else:
        Ul, LL, Mid = GetParameters(C1, C2, C3, Ul, LL, Mid)
        for Nri in range(1, ni + 1):
            EToDataSet[Nri - 1].DayNr = DNR + Nri - 1
            if Nri <= (ni / 2.0 + 0.01):
                EToDataSet[Nri - 1].Param = (2.0 * Ul + (Mid - Ul) * (2.0 * Nri - 1.0)
                                             / (ni / 2.0)) / 2.0
            else:
                if (((ni == 11) or (ni == 9)) and (Nri < (ni + 1.01) / 2.0)):
                    EToDataSet[Nri - 1].Param = Mid
                else:
                    EToDataSet[Nri - 1].Param = (2.0 * Mid
                                                 + (LL - Mid)
                                                 * (2.0 * Nri
                                                    - (ni + 1.0)) / (ni / 2.0)) / 2.0
            if EToDataSet[Nri - 1].Param < 0.0:
                EToDataSet[Nri - 1].Param = 0.0

    for Nri in range(ni + 1, 32):
        EToDataSet[Nri - 1].DayNr = DNR + ni - 1
        EToDataSet[Nri - 1].Param = 0.0

    return EToDataSet

def AdjustDecadeMONTHandYEAR(DecFile, Mfile, Yfile):
    DecFile = 1
    Mfile = Mfile + 1
    if Mfile > 12:
        Mfile = 1
        Yfile = Yfile + 1

    return DecFile, Mfile, Yfile


def GetSetofThree(DayN, Deci, Monthi, Yeari, C1, C2, C3):
    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(GetEToFileFull()).lstrip("/\\"),
        )
    )
    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        lines = f0.read().splitlines()

    data_lines = lines[8:]

    DecFile = 0
    Mfile = 0
    Yfile = 0
    Nri = 0
    Obsi = 0
    OK3 = False

    if GetEToRecord_FromD() > 20:
        DecFile = 3
    elif GetEToRecord_FromD() > 10:
        DecFile = 2
    else:
        DecFile = 1

    Mfile = GetEToRecord_FromM()
    if GetEToRecord_FromY() == 1901:
        Yfile = Yeari
    else:
        Yfile = GetEToRecord_FromY()

    if GetEToRecord_NrObs() <= 2:
        C1 = float(data_lines[0].split()[0])
        if GetEToRecord_NrObs() == 1:
            C2 = C1
            C3 = C1
        elif GetEToRecord_NrObs() == 2:
            DecFile = DecFile + 1
            if DecFile > 3:
                DecFile, Mfile, Yfile = AdjustDecadeMONTHandYEAR(DecFile, Mfile, Yfile)
            C3 = float(data_lines[1].split()[0])
            if Deci == DecFile:
                C2 = C3
                C3 = C2 + (C2 - C1) / 4.0
            else:
                C2 = C1
                C1 = C2 + (C2 - C3) / 4.0
        OK3 = True

    if ((not OK3) and ((Deci == DecFile)
                    and (Monthi == Mfile)
                    and (Yeari == Yfile))):
        C1 = float(data_lines[0].split()[0])
        C2 = C1
        C3 = float(data_lines[1].split()[0])
        C1 = C2 + (C2 - C3) / 4.0
        OK3 = True

    if ((not OK3) and ((DayN == GetEToRecord_ToD())
                    and (Monthi == GetEToRecord_ToM()))):
        if ((GetEToRecord_FromY() == 1901)
                    or (Yeari == GetEToRecord_ToY())):
            C1 = float(data_lines[GetEToRecord_NrObs() - 2].split()[0])
            C2 = float(data_lines[GetEToRecord_NrObs() - 1].split()[0])
            C3 = C2 + (C2 - C1) / 4.0
            OK3 = True

    if not OK3:
        Obsi = 1
        while True:
            if ((Deci == DecFile) and (Monthi == Mfile)
                                  and (Yeari == Yfile)):
                OK3 = True
            else:
                DecFile = DecFile + 1
                if DecFile > 3:
                    DecFile, Mfile, Yfile = AdjustDecadeMONTHandYEAR(DecFile, Mfile, Yfile)
                Obsi = Obsi + 1
            if OK3:
                break

        if GetEToRecord_FromD() > 20:
            DecFile = 3
        elif GetEToRecord_FromD() > 10:
            DecFile = 2
        else:
            DecFile = 1

        C1 = float(data_lines[Obsi - 2].split()[0])
        C2 = float(data_lines[Obsi - 1].split()[0])
        C3 = float(data_lines[Obsi].split()[0])

    return C1, C2, C3

def GetSetofThreeMonthsETo(Monthi, Yeari, C1, C2, C3, X1, X2, X3, t1):
    ni = 30

    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(GetEToFileFull()).lstrip("/\\"),
        )
    )
    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        lines = f0.read().splitlines()

    data_lines = lines[8:]

    Mfile = GetEToRecord_FromM()
    if GetEToRecord_FromY() == 1901:
        Yfile = Yeari
    else:
        Yfile = GetEToRecord_FromY()
    OK3 = False

    # 1. Prepare record

    # 2. IF 3 or less records
    if GetEToRecord_NrObs() <= 3:
        C1 = float(data_lines[0].split()[0])
        C1 = C1 * ni
        X1 = ni
        if GetEToRecord_NrObs() == 1:
            t1 = X1
            X2 = X1 + ni
            C2 = C1
            X3 = X2 + ni
            C3 = C1
        elif GetEToRecord_NrObs() == 2:
            t1 = X1
            Mfile = Mfile + 1
            if Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
            C3 = float(data_lines[1].split()[0])
            C3 = C3 * ni
            if Monthi == Mfile:
                C2 = C3
                X2 = X1 + ni
                X3 = X2 + ni
            else:
                C2 = C1
                X2 = X1 + ni
                X3 = X2 + ni
        elif GetEToRecord_NrObs() == 3:
            if Monthi == Mfile:
                t1 = 0
            Mfile = Mfile + 1
            if Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
            C2 = float(data_lines[1].split()[0])
            C2 = C2 * ni
            X2 = X1 + ni
            if Monthi == Mfile:
                t1 = X1
            Mfile = Mfile + 1
            if Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
            C3 = float(data_lines[2].split()[0])
            C3 = C3 * ni
            X3 = X2 + ni
            if Monthi == Mfile:
                t1 = X2
        OK3 = True

    # 3. If first observation
    if ((not OK3) and ((Monthi == Mfile) and (Yeari == Yfile))):
        t1 = 0
        C1 = float(data_lines[0].split()[0])
        C1 = C1 * ni
        X1 = ni
        Mfile = Mfile + 1
        if Mfile > 12:
            Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
        C2 = float(data_lines[1].split()[0])
        C2 = C2 * ni
        X2 = X1 + ni
        Mfile = Mfile + 1
        if Mfile > 12:
            Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
        C3 = float(data_lines[2].split()[0])
        C3 = C3 * ni
        X3 = X2 + ni
        OK3 = True

    # 4. If last observation
    if ((not OK3) and (Monthi == GetEToRecord_ToM())):
        if ((GetEToRecord_FromY() == 1901)
                    or (Yeari == GetEToRecord_ToY())):
            idx = GetEToRecord_NrObs() - 3
            C1 = float(data_lines[idx].split()[0])
            C1 = C1 * ni
            X1 = ni
            Mfile = Mfile + (GetEToRecord_NrObs() - 2)
            while Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
            C2 = float(data_lines[idx + 1].split()[0])
            C2 = C2 * ni
            X2 = X1 + ni
            t1 = X2
            Mfile = Mfile + 1
            if Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
            C3 = float(data_lines[idx + 2].split()[0])
            C3 = C3 * ni
            X3 = X2 + ni
            OK3 = True

    # 5. IF not previous cases
    if not OK3:
        Obsi = 1
        while True:
            if ((Monthi == Mfile) and (Yeari == Yfile)):
                OK3 = True
            else:
                Mfile = Mfile + 1
                if Mfile > 12:
                    Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
                Obsi = Obsi + 1
            if OK3:
                break
        Mfile = GetEToRecord_FromM()
        Yfile = Yeari if GetEToRecord_FromY() == 1901 else GetEToRecord_FromY()
        idx = Obsi - 2
        C1 = float(data_lines[idx].split()[0])
        C1 = C1 * ni
        X1 = ni
        t1 = X1
        Mfile = Mfile + (Obsi - 1)
        while Mfile > 12:
            Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
        C2 = float(data_lines[idx + 1].split()[0])
        C2 = C2 * ni
        X2 = X1 + ni
        Mfile = Mfile + 1
        if Mfile > 12:
            Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
        C3 = float(data_lines[idx + 2].split()[0])
        C3 = C3 * ni
        X3 = X2 + ni

    return C1, C2, C3, X1, X2, X3, t1

def AdjustMONTHandYEAR(Mfile, Yfile):
    Mfile = Mfile - 12
    Yfile = Yfile + 1

    return Mfile, Yfile

def GetInterpolationParameters(C1, C2, C3, aOver3, bOver2, c):
    # n1=n2=n3=30 --> better parabola
    aOver3 = (C1 - 2 * C2 + C3) / (6 * 30 * 30 * 30)
    bOver2 = (-6 * C1 + 9 * C2 - 3 * C3) / (6 * 30 * 30)
    c = (11 * C1 - 7 * C2 + 2 * C3) / (6 * 30)

    return aOver3, bOver2, c

def GetMonthlyEToDataSet(DayNri, EToDataSet):
    Dayi = 0
    Monthi = 0
    Yeari = 0
    DayN = 0
    DNR = 0
    X1 = 0
    X2 = 0
    X3 = 0
    t1 = 0
    t2 = 0
    C1 = 0.0
    C2 = 0.0
    C3 = 0.0
    aOver3 = 0.0
    bOver2 = 0.0
    c = 0.0

    # GetMonthlyEToDataSet
    Dayi, Monthi, Yeari = DetermineDate(DayNri)
    C1, C2, C3, X1, X2, X3, t1 = GetSetofThreeMonthsETo(Monthi, Yeari, C1, C2, C3, X1, X2, X3, t1)

    Dayi = 1
    DNR = DetermineDayNr(Dayi, Monthi, Yeari)
    DayN = DaysInMonth[Monthi - 1]
    if (Monthi == 2) and LeapYear(Yeari):
        DayN = DayN + 1

    aOver3, bOver2, c = GetInterpolationParameters(C1, C2, C3, aOver3, bOver2, c)
    for Dayi in range(1, DayN + 1):
        t2 = t1 + 1
        EToDataSet[Dayi - 1].DayNr = DNR + Dayi - 1
        EToDataSet[Dayi - 1].Param = aOver3 * (t2 * t2 * t2 - t1 * t1 * t1) \
                                    + bOver2 * (t2 * t2 - t1 * t1) \
                                    + c * (t2 - t1)
        if EToDataSet[Dayi - 1].Param < 0:
            EToDataSet[Dayi - 1].Param = 0
        t1 = t2

    for Dayi in range(DayN + 1, 32):
        EToDataSet[Dayi - 1].DayNr = DNR + DayN - 1
        EToDataSet[Dayi - 1].Param = 0.0

    return EToDataSet

def GetDecadeRainDataSet(DayNri, RainDataSet):
    Nri = 0
    Day1 = 0
    Deci = 0
    Monthi = 0
    Yeari = 0
    ni = 0
    DecFile = 0
    Mfile = 0
    Yfile = 0
    DNR = 0
    OKRain = False
    C = 0.0

    Day1, Monthi, Yeari = DetermineDate(DayNri)

    # 0. Set Monthly Parameters

    # 1. Which decade ?
    if Day1 > 20:
        Deci = 3
        Day1 = 21
        ni = DaysInMonth[Monthi - 1] - Day1 + 1
        if (Monthi == 2) and LeapYear(Yeari):
            ni = ni + 1
    elif Day1 > 10:
        Deci = 2
        Day1 = 11
        ni = 10
    else:
        Deci = 1
        Day1 = 1
        ni = 10

    # 2. Load datafile
    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(GetRainFileFull()).lstrip("/\\"),
        )
    )
    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        lines = f0.read().splitlines()

    data_lines = lines[8:]

    if GetRainRecord_FromD() > 20:
        DecFile = 3
    elif GetRainRecord_FromD() > 10:
        DecFile = 2
    else:
        DecFile = 1
    Mfile = GetRainRecord_FromM()
    if GetRainRecord_FromY() == 1901:
        Yfile = Yeari
    else:
        Yfile = GetRainRecord_FromY()

    # 3. Find decade
    OKRain = False
    C = 999.0
    idx = 0
    while True:
        if ((Deci == DecFile) and (Monthi == Mfile)
                              and (Yeari == Yfile)):
            C = float(data_lines[idx].split()[0])
            OKRain = True
        else:
            DecFile = DecFile + 1
            if DecFile > 3:
                DecFile, Mfile, Yfile = AdjustDecadeMONTHandYEAR(DecFile, Mfile, Yfile)
            idx = idx + 1
        if OKRain:
            break

    # 4. Process data
    DNR = DetermineDayNr(Day1, Monthi, Yeari)
    for Nri in range(1, ni + 1):
        RainDataSet[Nri - 1].DayNr = DNR + Nri - 1
        RainDataSet[Nri - 1].Param = C / ni
    for Nri in range(ni + 1, 32):
        RainDataSet[Nri - 1].DayNr = DNR + ni - 1
        RainDataSet[Nri - 1].Param = 0.0

    return RainDataSet

def GetSetofThreeMonths(Monthi, Yeari, C1, C2, C3):
    full_path = os.path.normpath(
        os.path.join(
            complete_path_dir,
            _strip_quotes(GetRainFileFull()).lstrip("/\\"),
        )
    )
    with open(full_path, "r", encoding="utf-8", errors="replace") as f0:
        lines = f0.read().splitlines()

    data_lines = lines[8:]

    Mfile = GetRainRecord_FromM()
    if GetRainRecord_FromY() == 1901:
        Yfile = Yeari
    else:
        Yfile = GetRainRecord_FromY()
    OK3 = False

    # 1. Prepare record

    # 2. IF 2 or less records
    if GetRainRecord_NrObs() <= 2:
        C1 = float(data_lines[0].split()[0])
        if GetRainRecord_NrObs() == 1:
            C2 = C1
            C3 = C1
        elif GetRainRecord_NrObs() == 2:
            Mfile = Mfile + 1
            if Mfile > 12:
                Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
            C3 = float(data_lines[1].split()[0])
            if Monthi == Mfile:
                C2 = C3
            else:
                C2 = C1
        OK3 = True

    # 3. If first observation
    if ((not OK3) and ((Monthi == Mfile)
                    and (Yeari == Yfile))):
        C1 = float(data_lines[0].split()[0])
        C2 = C1
        C3 = float(data_lines[1].split()[0])
        OK3 = True

    # 4. If last observation
    if ((not OK3) and (Monthi == GetRainRecord_ToM())):
        if ((GetRainRecord_FromY() == 1901) or (Yeari == GetRainRecord_ToY())):
            idx = GetRainRecord_NrObs() - 2
            C1 = float(data_lines[idx].split()[0])
            C2 = float(data_lines[idx + 1].split()[0])
            C3 = C2
            OK3 = True

    # 5. IF not previous cases
    if not OK3:
        Obsi = 1
        while True:
            if ((Monthi == Mfile) and (Yeari == Yfile)):
                OK3 = True
            else:
                Mfile = Mfile + 1
                if Mfile > 12:
                    Mfile, Yfile = AdjustMONTHandYEAR(Mfile, Yfile)
                Obsi = Obsi + 1
            if OK3:
                break

        Mfile = GetRainRecord_FromM()
        idx = Obsi - 2
        C1 = float(data_lines[idx].split()[0])
        C2 = float(data_lines[idx + 1].split()[0])
        C3 = float(data_lines[idx + 2].split()[0])

    return C1, C2, C3

def GetMonthlyRainDataSet(DayNri, RainDataSet):
    Dayi = 0
    DayN = 0
    Monthi = 0
    Yeari = 0
    C1 = 0.0
    C2 = 0.0
    C3 = 0.0
    RainDec1 = 0.0
    RainDec2 = 0.0
    RainDec3 = 0.0
    DNR = 0

    Dayi, Monthi, Yeari = DetermineDate(DayNri)

    # Set Monthly Parameters

    C1, C2, C3 = GetSetofThreeMonths(Monthi, Yeari, C1, C2, C3)

    Dayi = 1
    DNR = DetermineDayNr(Dayi, Monthi, Yeari)
    DayN = DaysInMonth[Monthi - 1]
    if (Monthi == 2) and LeapYear(Yeari):
        DayN = DayN + 1
    if C2 > sys.float_info.epsilon:
        RainDec1 = (5.0 * C1 + 26.0 * C2 - 4.0 * C3) / (27.0 * 3.0)  # mm/dec
        RainDec2 = (-C1 + 29.0 * C2 - C3) / (27.0 * 3.0)
        RainDec3 = (-4.0 * C1 + 26.0 * C2 + 5.0 * C3) / (27.0 * 3.0)
        for Dayi in range(1, 11):
            RainDataSet[Dayi - 1].DayNr = DNR + Dayi - 1
            RainDataSet[Dayi - 1].Param = RainDec1 / 10.0
            if RainDataSet[Dayi - 1].Param < sys.float_info.epsilon:
                RainDataSet[Dayi - 1].Param = 0.0
        for Dayi in range(11, 21):
            RainDataSet[Dayi - 1].DayNr = DNR + Dayi - 1
            RainDataSet[Dayi - 1].Param = RainDec2 / 10.0
            if RainDataSet[Dayi - 1].Param < sys.float_info.epsilon:
                RainDataSet[Dayi - 1].Param = 0.0
        for Dayi in range(21, DayN + 1):
            RainDataSet[Dayi - 1].DayNr = DNR + Dayi - 1
            RainDataSet[Dayi - 1].Param = RainDec3 / (DayN - 21.0 + 1.0)
            if RainDataSet[Dayi - 1].Param < sys.float_info.epsilon:
                RainDataSet[Dayi - 1].Param = 0.0
    else:
        for Dayi in range(1, DayN + 1):
            RainDataSet[Dayi - 1].DayNr = DNR + Dayi - 1
            RainDataSet[Dayi - 1].Param = 0.0

    for Dayi in range(DayN + 1, 32):
        RainDataSet[Dayi - 1].DayNr = DNR + DayN - 1
        RainDataSet[Dayi - 1].Param = 0.0

    return RainDataSet