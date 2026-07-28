from ._global import *
from .utils import *
from .kinds import *

import sys


def AdjustedRootingDepth(CCAct, CCpot, Tpot, Tact, StressLeaf, StressSenescence, DAP, L0,
                         LZmax, L1234, GDDL0, GDDLZmax, GDDL1234, SumGDDPrev, SumGDD, Zmin,
                         Zmax, Ziprev, ShapeFactor, TypeDays):
    Zi = 0.0
    ZiUnlimM1 = 0.0
    ZiUnlim = 0.0
    dZ = 0.0
    ZiTest = 0.0
    Zsoil = 0.0
    ThetaTreshold = 0.0
    TAWcompi = 0.0
    Wrel = 0.0
    pZexp = 0.0
    Zlimit = 0.0
    ZiMax = 0.0
    KsShapeFactorRoot = 0.0
    compi = 0
    layer = 0

    if roundc(Ziprev, mold=1) == undef_int:
        Zi = ActualRootingDepth(DAP, L0, LZmax, L1234, GDDL0, GDDLZmax,
                                SumGDD, Zmin, Zmax, ShapeFactor, TypeDays)
    else:
        # 1. maximum rooting depth (ZiMax) that could have been reached at
        #    time t
        # -- 1.1 Undo effect of restrictive soil layer(s)
        if roundc(GetSoil_RootMax() * 1000.0, mold=1) < roundc(Zmax * 1000.0, mold=1):
            Zlimit = GetSoil_RootMax()
            SetSoil_RootMax(float(Zmax))
        else:
            Zlimit = Zmax

        # -- 1.2 Calculate ZiMax
        ZiMax = ActualRootingDepth(DAP, L0, LZmax, L1234, GDDL0, GDDLZmax,
                                   SumGDD, Zmin, Zmax, ShapeFactor, TypeDays)
        # -- 1.3 Restore effect of restrive soil layer(s)
        SetSoil_RootMax(float(Zlimit))

        # 2. increase (dZ) at time t
        ZiUnlimM1 = ActualRootingDepth(DAP - 1, L0, LZmax, L1234, GDDL0, GDDLZmax,
                                       SumGDDPrev, Zmin, Zmax, ShapeFactor, TypeDays)
        ZiUnlim = ActualRootingDepth(DAP, L0, LZmax, L1234, GDDL0, GDDLZmax,
                                     SumGDD, Zmin, Zmax, ShapeFactor, TypeDays)
        dZ = ZiUnlim - ZiUnlimM1

        # 3. corrections of dZ
        # -- 3.1 correction for restrictive soil layer is already considered
        #    in ActualRootingDepth

        # -- 3.2 correction for stomatal closure
        if (Tpot > 0.0) and (Tact < Tpot) and (GetSimulParam_KsShapeFactorRoot() != undef_int):
            if GetSimulParam_KsShapeFactorRoot() >= 0:
                dZ = dZ * (Tact / Tpot)   # linear
            else:
                KsShapeFactorRoot = float(GetSimulParam_KsShapeFactorRoot())
                dZ = dZ * (math.exp((Tact / Tpot) * KsShapeFactorRoot) - 1.0) \
                        / (math.exp(KsShapeFactorRoot) - 1.0)  # exponential

        # -- 3.2 correction for dry soil at expansion front of actual root
        #        zone
        if dZ > 0.001:
            # soil water depletion threshold for root deepening
            pZexp = GetCrop_pdef() + (1 - GetCrop_pdef()) / 2.0
            # restrictive soil layer is considered by ActualRootingDepth
            ZiTest = Ziprev + dZ
            compi = 0
            Zsoil = 0.0
            while (Zsoil < ZiTest) and (compi < GetNrCompartments()):
                compi = compi + 1
                Zsoil = Zsoil + GetCompartment_Thickness(compi)
            layer = GetCompartment_Layer(compi)
            TAWcompi = GetSoilLayer_FC(layer) / 100.0 - GetSoilLayer_WP(layer) / 100.0
            ThetaTreshold = GetSoilLayer_FC(layer) / 100.0 - pZexp * TAWcompi
            if GetCompartment_theta(compi) < ThetaTreshold:
                # expansion is limited due to soil water content at
                # expansion front
                if GetCompartment_theta(compi) <= GetSoilLayer_WP(layer) / 100.0:
                    dZ = 0.0
                else:
                    Wrel = (GetSoilLayer_FC(layer) / 100.0 -
                            GetCompartment_theta(compi)) / TAWcompi
                    dZ = dZ * KsAny(Wrel, pZexp, 1.0,
                                    GetCrop_KsShapeFactorStomata())

        # -- 3.3 correction for early senescence
        if (CCAct <= 0.0) and (CCpot > 50.0):
            dZ = 0.0

        # -- 3.4 correction for no germination
        if not GetSimulation_Germinate():
            dZ = 0.0

        # 4. actual rooting depth (Zi)
        Zi = Ziprev + dZ

        # 5. Correction for root density if root deepening is restricted
        #    (dry soil and/or restricitive layers)
        if roundc(Zi * 1000, mold=1) < roundc(ZiMax * 1000, mold=1):
            # Total extraction in restricted root zone (Zi) and max root
            # zone (ZiMax) should be identical
            SetSimulation_SCor(float((2 * (ZiMax / Zi)
                          * ((GetCrop_SmaxTop() + GetCrop_SmaxBot()) / 2.0)
                          - GetCrop_SmaxTop()) / GetCrop_SmaxBot()))
            # consider part of the restricted deepening due to water stress
            # (= less roots)
            if GetSumWaBal_Tpot() > 0.0:
                SetSimulation_SCor(float(GetSimulation_SCor()
                      * (GetSumWaBal_Tact() / GetSumWaBal_Tpot())))
                if GetSimulation_SCor() < 1.0:
                    SetSimulation_SCor(1.0)
        else:
            SetSimulation_SCor(1.0)

    AdjustedRootingDepth = Zi
    return AdjustedRootingDepth
