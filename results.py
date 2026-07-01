from datetime import datetime


def print_air_properties(network):

    print("\nPROPIEDADES DEL AIRE")
    print("-" * 120)

    for z in network.zones.values():

        print(
            f"{z.id:20s}"
            f" rho={z.rho:.4f} kg/m3"
            f"  nu={z.nu:.8e} m2/s"
            f"  T={z.temperature:.1f} °C"
            f"  HR={z.rh:.1f} %"
        )


def print_link_results(results):

    print("\nTRANSFERENCIAS")
    print("-" * 120)

    header = (
        f"{'Link':8s}"
        f"{'Tipo':15s}"
        f"{'Dirección':40s}"
        f"{'m_dot [kg/s]':>15s}"
        f"{'Q [m3/h]':>15s}"
    )

    print(header)
    print("-" * 120)

    for r in results:

        print(
            f"{r['link']:8s}"
            f"{r['type']:15s}"
            f"{r['direction']:40s}"
            f"{r['m_dot']:15.4f}"
            f"{r['q_m3h']:15.1f}"
        )


def print_balance_table(network):

    print("\nBALANCE DE MASA")
    print("-" * 120)

    header = (
        f"{'Zona':20s}"
        f"{'m_sup':>12s}"
        f"{'m_ext':>12s}"
        f"{'m_in':>12s}"
        f"{'m_out':>12s}"
        f"{'m_ret':>12s}"
    )

    print(header)
    print("-" * 120)

    for z in network.zones.values():

        if z.id == "EXTERIOR":
            continue

        print(
            f"{z.id:20s}"
            f"{z.m_supply:12.4f}"
            f"{z.m_exhaust:12.4f}"
            f"{z.m_in:12.4f}"
            f"{z.m_out:12.4f}"
            f"{z.return_mass_flow:12.4f}"
        )


def save_report(
    filename,
    network,
    link_results
):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("SIMULACION MULTIZONA HVAC\n")
        f.write("=" * 80 + "\n")
        f.write(
            f"Fecha de ejecución: {datetime.now()}\n\n"
        )

        # --------------------------------------------------
        # PROPIEDADES
        # --------------------------------------------------

        f.write("PROPIEDADES DEL AIRE\n")
        f.write("-" * 80 + "\n")

        for z in network.zones.values():

            f.write(
                f"{z.id:20s}"
                f" T={z.temperature:.1f} °C"
                f"  HR={z.rh:.1f} %"
                f"  rho={z.rho:.4f} kg/m3"
                f"  nu={z.nu:.8e} m2/s\n"
            )

        # --------------------------------------------------
        # TRANSFERENCIAS
        # --------------------------------------------------

        f.write("\n")
        f.write("TRANSFERENCIAS ENTRE NODOS\n")
        f.write("-" * 80 + "\n")

        for r in link_results:

            f.write(
                f"{r['link']:8s}"
                f"{r['type']:15s}"
                f"{r['direction']:40s}"
                f"{r['m_dot']:10.4f} kg/s "
                f"{r['q_m3h']:10.1f} m3/h\n"
            )

        # --------------------------------------------------
        # BALANCE
        # --------------------------------------------------

        f.write("\n")
        f.write("BALANCE DE MASA POR ZONA\n")
        f.write("-" * 80 + "\n")

        f.write(
            f"{'Zona':20s}"
            f"{'m_sup':>12s}"
            f"{'m_ext':>12s}"
            f"{'m_in':>12s}"
            f"{'m_out':>12s}"
            f"{'m_ret':>12s}\n"
        )

        f.write("-" * 80 + "\n")

        for z in network.zones.values():

            if z.id == "EXTERIOR":
                continue

            f.write(
                f"{z.id:20s}"
                f"{z.m_supply:12.4f}"
                f"{z.m_exhaust:12.4f}"
                f"{z.m_in:12.4f}"
                f"{z.m_out:12.4f}"
                f"{z.return_mass_flow:12.4f}\n"
            )

        f.write("\n")

        f.write(
            "NOTA: El retorno indicado es el requerido para "
            "mantener la presión especificada en régimen estacionario.\n"
        )