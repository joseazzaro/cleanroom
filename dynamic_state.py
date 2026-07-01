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

from dynamic_simulation import (
    DynamicSimulation
)


with open(
    "project.json",
    encoding="utf-8"
) as f:

    data = json.load(f)


network = AirflowNetwork()

p_atm = data["atmosphere"]["pressure"]

#
# Zonas
#
for zone in network.internal_zones():

    zone.return_mass_flow_fixed = (
        zone.return_mass_flow
    )
    
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

#
# Links
#

for l in data["links"]:

    link = Link(
        link_id=l["id"],
        link_type=l["type"],
        node1=l["node1"],
        node2=l["node2"],
        area=l["closed_leakage_area"],
        width=l.get("width"),
        height=l.get("height"),
        cd=l["cd"],
        n=l["n"]
    )

    network.add_link(link)

#
# Eventos
#

manager = EventManager()

for e in data["events"]:

    manager.add_event(
        DoorEvent(
            e["id"],
            e["link"],
            e["start_time"]
        )
    )

    link = network.get_link(
        e["link"]
    )

    link.dynamic_model = SwingDoor(
        width=link.width,
        height=link.height,
        closed_leakage_area=link.area,
        opening_speed_deg_s=e["opening_speed_deg_s"],
        max_angle_deg=e["max_angle_deg"],
        hold_open_time_s=e["hold_open_time_s"]
    )

#
# Simulación
#

sim = DynamicSimulation(
    network=network,
    event_manager=manager,
    dt=data["simulation"]["dt"],
    t_end=data["simulation"]["t_end"]
)

sim.run()

sim.save_csv(
    "dynamic_results.csv"
)

print(
    "Resultados guardados en "
    "dynamic_results.csv"
)

sim.save_link_csv(
    "dynamic_links.csv"
)

sim.plot_link_dynamics(
    "L1",
    "L1_dynamics.png"
)