import json

from network import (
    Zone,
    Link,
    AirflowNetwork
)

from door_models import (
    SwingDoor
)

from event_manager import (
    EventManager,
    DoorEvent
)

from simulation import (
    Simulation
)

from dynamic_network_solver import (
    DynamicNetworkSolver
)

from dynamic_simulation import (
    DynamicSimulation
)


# ==================================================
# LEER PROYECTO
# ==================================================

with open(
    "project.json",
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


# ==================================================
# CREAR RED
# ==================================================

network = AirflowNetwork()

p_atm = data["atmosphere"]["pressure"]


# ==================================================
# ZONAS
# ==================================================

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
            1.5
        ),

        p_atm=p_atm

    )

    network.add_zone(zone)


# ==================================================
# LINKS
# ==================================================

for l in data["links"]:

    link = Link(

        link_id=l["id"],

        link_type=l["type"],

        node1=l["node1"],

        node2=l["node2"],

        area=l["closed_leakage_area"],

        width=l.get(
            "width"
        ),

        height=l.get(
            "height"
        ),

        cd=l["cd"],

        n=l["n"]

    )

    network.add_link(link)


# ==================================================
# RESOLUCIÓN ESTACIONARIA
# ==================================================

print()
print("=" * 70)
print("RESOLVIENDO ESTADO ESTACIONARIO")
print("=" * 70)
print()

steady = Simulation(network)

steady.run_steady_state()

print()
print("=" * 70)
print("ESTADO ESTACIONARIO")
print("=" * 70)

for zone in network.internal_zones():

    print(
        f"{zone.id:20s}"
        f" P={zone.pressure:8.3f} Pa"
        f" Ret={zone.return_mass_flow:8.4f} kg/s"
    )

print("=" * 70)
print()


# ==================================================
# CONGELAR RETORNOS
# ==================================================

for zone in network.internal_zones():

    zone.return_mass_flow_fixed = (
        zone.return_mass_flow
    )


# ==================================================
# EVENTOS
# ==================================================

event_manager = EventManager()

for e in data["events"]:

    event = DoorEvent(

        event_id=e["id"],

        link_id=e["link"],

        start_time=e["start_time"]

    )

    event_manager.add_event(
        event
    )

    link = network.get_link(
        e["link"]
    )

    if link is None:

        continue

    if link.type == "swing_door":

        link.dynamic_model = SwingDoor(

            width=link.width,

            height=link.height,

            closed_leakage_area=link.area,

            opening_speed_deg_s=e[
                "opening_speed_deg_s"
            ],

            max_angle_deg=e[
                "max_angle_deg"
            ],

            hold_open_time_s=e[
                "hold_open_time_s"
            ]

        )


# ==================================================
# DIAGNÓSTICO INICIAL
# ==================================================

print()
print("=" * 70)
print("CONDICIONES INICIALES DINÁMICAS")
print("=" * 70)

for zone in network.internal_zones():

    print(
        f"{zone.id:20s}"
        f" P={zone.pressure:8.3f} Pa"
        f" Supply={zone.m_supply:8.4f} kg/s"
        f" Exhaust={zone.m_exhaust:8.4f} kg/s"
        f" Return={zone.return_mass_flow_fixed:8.4f} kg/s"
    )

print("=" * 70)
print()


# ==================================================
# SOLVER DINÁMICO
# ==================================================

solver = DynamicNetworkSolver(

    network=network,

    max_iterations=50,

    mass_tolerance=1e-4,

    relaxation=0.75

)


# ==================================================
# SIMULACIÓN
# ==================================================

simulation = DynamicSimulation(

    network=network,

    event_manager=event_manager,

    solver=solver,

    dt=data["simulation"]["dt"],

    t_end=data["simulation"]["t_end"]

)


# ==================================================
# EJECUCIÓN
# ==================================================

print()
print("=" * 70)
print("INICIANDO SIMULACIÓN DINÁMICA")
print("=" * 70)
print()

simulation.run()


# ==================================================
# EXPORTAR
# ==================================================

simulation.save_zone_csv(
    "dynamic_zones.csv"
)

simulation.save_link_csv(
    "dynamic_links.csv"
)


# ==================================================
# GRÁFICO
# ==================================================

if len(data["events"]) > 0:

    simulation.plot_link(

        data["events"][0]["link"],

        "pressure_dip.png"

    )


# ==================================================
# FIN
# ==================================================

print()
print("=" * 70)
print("SIMULACIÓN FINALIZADA")
print("=" * 70)

print()

print("Archivos generados:")

print("  dynamic_zones.csv")
print("  dynamic_links.csv")
print("  pressure_dip.png")

print()