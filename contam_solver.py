RHO0 = 1.2041
NU0 = 1.5083e-5


def mass_flow(
    delta_p,
    area,
    cd,
    n,
    rho,
    nu
):

    c0 = (
        cd
        * area
        * (2.0 * RHO0) ** 0.5
    )

    kc = (
        (RHO0 / rho) ** (n - 1.0)
        *
        (NU0 / nu) ** (2.0 * n - 1.0)
    )

    if abs(delta_p) < 1e-12:

        return 0.0

    sign = 1.0 if delta_p > 0 else -1.0

    return (

        sign
        * kc
        * c0
        * abs(delta_p) ** n

    )


def dmass_flow_dpressure(
    delta_p,
    area,
    cd,
    n,
    rho,
    nu
):

    c0 = (
        cd
        * area
        * (2.0 * RHO0) ** 0.5
    )

    kc = (
        (RHO0 / rho) ** (n - 1.0)
        *
        (NU0 / nu) ** (2.0 * n - 1.0)
    )

    if abs(delta_p) < 1e-12:

        return 0.0

    return (

        n
        * kc
        * c0
        * abs(delta_p) ** (n - 1.0)

    )