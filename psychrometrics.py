import math

R_DA = 287.055
R_V = 461.52


def saturation_pressure(t_c):

    return 610.94 * math.exp(
        (17.625 * t_c) /
        (t_c + 243.04)
    )


def air_density(
    t_c,
    rh,
    p_atm=101325
):

    t_k = t_c + 273.15

    pv = (
        rh / 100.0
    ) * saturation_pressure(t_c)

    return (
        (p_atm - pv) / (R_DA * t_k)
        +
        pv / (R_V * t_k)
    )


def dynamic_viscosity(t_c):

    t_k = t_c + 273.15

    return (
        3.7143e-6
        +
        4.9286e-8 * t_k
    )


def kinematic_viscosity(
    t_c,
    rh,
    p_atm=101325
):

    rho = air_density(
        t_c,
        rh,
        p_atm
    )

    return dynamic_viscosity(t_c) / rho