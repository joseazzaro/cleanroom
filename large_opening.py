import math

G = 9.81


def doorway_flow(
    width,
    height,
    cd,
    p_atm,
    pressure_1,
    pressure_2,
    rho_1,
    rho_2,
):

    delta_p = (
        pressure_1
        - pressure_2
    )

    area = (
        width
        * height
    )

    rho_avg = (
        rho_1
        + rho_2
    ) / 2.0

    #
    # Flujo impulsado por presión
    #

    m_pressure = (
        cd
        * area
        * math.sqrt(
            max(
                0.0,
                2.0
                * rho_avg
                * abs(delta_p)
            )
        )
    )

    #
    # Limitar contribución
    # para estabilizar V1
    #

    m_pressure *= 0.15

    if delta_p >= 0:

        m12_pressure = m_pressure
        m21_pressure = 0.0

    else:

        m12_pressure = 0.0
        m21_pressure = m_pressure

    #
    # Intercambio por flotación
    #

    delta_rho = abs(
        rho_1
        - rho_2
    )

    m_buoyancy = (
        0.05
        *
        cd
        *
        width
        *
        height
        *
        math.sqrt(
            G
            *
            height
            *
            delta_rho
        )
    )

    m12 = (
        m12_pressure
        +
        0.5
        * m_buoyancy
    )

    m21 = (
        m21_pressure
        +
        0.5
        * m_buoyancy
    )

    return (
        m12,
        m21
    )