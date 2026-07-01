import json

from network import (
    Zone,
    Link,
    AirflowNetwork
)

from simulation import (
    Simulation
)

from results import (
    print_air_properties,
    print_link_results,
    print_balance_table,
    save_report
)


# ======================================================
# LECTURA DEL PROYECTO
# ======================================================

with open(
    "project.json",
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


# ======================================================
# CREACIÓN DE LA RED
# ======================================================

network = AirflowNetwork()

p_atm = data["atmosphere"]["pressure"]


# ======================================================
# ZONAS
# ======================================================

for z in data["zones"]:

    zone = Zone(

        zone_id=z["id"],

        volume=z["volume"],

        temperature=z["temperature"],
        rh=z["rh"],

        pressure=z["pressure"],

        supply_m3h=z["supply_m3h"],
        exhaust_m3h=z["exhaust_m3h"],

        is_boundary=z.get(
            "is_boundary",
            False
        ),

        reference_height=z.get(
            "reference_height",
            0.0
        ),

        p_atm=p_atm
    )

    network.add_zone(zone)


# ======================================================
# LINKS
# ======================================================

for l in data["links"]:

    link = Link(

        link_id=l["id"],

        link_type=l["type"],

        node1=l["node1"],
        node2=l["node2"],

        area=l["closed_leakage_area"],

        width=l.get(
            "width",
            None
        ),

        height=l.get(
            "height",
            None
        ),

        cd=l["cd"],

        n=l["n"]
    )

    network.add_link(link)


# ======================================================
# SIMULACIÓN ESTACIONARIA
# ======================================================

sim = Simulation(network)

sim.run_steady_state()


# ======================================================
# RESULTADOS EN PANTALLA
# ======================================================

print_air_properties(network)

print_link_results(
    sim.link_results
)

print_balance_table(
    network
)


# ======================================================
# REPORTE
# ======================================================

report_file = (
    "steady_state_report.txt"
)

save_report(
    report_file,
    network,
    sim.link_results
)

print("\n" + "=" * 80)

print(
    f"Reporte guardado en: "
    f"{report_file}"
)

print("=" * 80)