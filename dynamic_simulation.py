import csv

import pandas as pd
import matplotlib.pyplot as plt

from contam_solver import (
    mass_flow
)

from large_opening import (
    doorway_flow
)


R_AIR = 287.055


class DynamicSimulation:

    def __init__(
        self,
        network,
        event_manager,
        dt,
        t_end
    ):

        self.network = network

        self.event_manager = event_manager

        self.dt = dt

        self.t_end = t_end

        self.time_history = []

        self.link_history = []

    def initialize(self):

        for zone in self.network.internal_zones():

            zone.excess_mass = (
                zone.initial_excess_mass
            )

            zone.return_mass_flow_fixed = (
                zone.return_mass_flow
            )

    def update_pressure(self, zone):

        t_k = (
            zone.temperature
            + 273.15
        )

        zone.pressure = (

            zone.excess_mass

            * R_AIR

            * t_k

            / zone.volume

        )

    def compute_flows(
        self,
        current_time
    ):

        self.network.reset_balances()

        for link in self.network.links:

            z1 = self.network.get_zone(
                link.node1
            )

            z2 = self.network.get_zone(
                link.node2
            )

            area = link.area

            alpha = 0.0

            event = (
                self.event_manager
                .get_active_event(
                    link.id,
                    current_time
                )
            )

            if (
                event is not None
                and link.dynamic_model
            ):

                elapsed = (
                    self.event_manager
                    .elapsed_time(
                        event,
                        current_time
                    )
                )

                area = (
                    link.dynamic_model
                    .current_area(
                        elapsed
                    )
                )

                area_max = (
                    link.width
                    * link.height
                )

                alpha = (
                    area
                    - link.area
                ) / (
                    area_max
                    - link.area
                )

                alpha = max(
                    0.0,
                    min(
                        1.0,
                        alpha
                    )
                )

            dp = (
                z1.pressure
                - z2.pressure
            )

            rho_avg = (
                z1.rho
                + z2.rho
            ) / 2.0

            nu_avg = (
                z1.nu
                + z2.nu
            ) / 2.0

            m_closed = abs(
                mass_flow(
                    dp,
                    max(area, 1e-12),
                    link.cd,
                    link.n,
                    rho_avg,
                    nu_avg
                )
            )

            m12_open = 0.0
            m21_open = 0.0

            if (
                alpha > 0.0
                and link.width
                and link.height
            ):

                (
                    m12_open,
                    m21_open
                ) = doorway_flow(
                    link.width,
                    link.height,
                    link.cd,
                    101325.0,
                    z1.pressure,
                    z2.pressure,
                    z1.rho,
                    z2.rho
                )

            if dp >= 0.0:

                m12 = (
                    (1.0 - alpha)
                    * m_closed
                    +
                    alpha
                    * m12_open
                )

                m21 = (
                    alpha
                    * m21_open
                )

            else:

                m21 = (
                    (1.0 - alpha)
                    * m_closed
                    +
                    alpha
                    * m21_open
                )

                m12 = (
                    alpha
                    * m12_open
                )

            z1.m_out += m12
            z2.m_in += m12

            z2.m_out += m21
            z1.m_in += m21

            self.link_history.append(
                {
                    "time": current_time,
                    "link": link.id,
                    "delta_p": dp,
                    "area": area,
                    "alpha": alpha,
                    "m12": m12,
                    "m21": m21
                }
            )

    def integrate(self):

        for zone in self.network.internal_zones():

            m_net = (

                zone.m_supply

                + zone.m_in

                - zone.m_exhaust

                - zone.m_out

                - zone.return_mass_flow_fixed

            )

            zone.excess_mass += (
                0.5
                * m_net
                * self.dt
            )

            self.update_pressure(
                zone
            )

    def save_step(
        self,
        time_s
    ):

        for zone in self.network.internal_zones():

            self.time_history.append(
                {
                    "time": time_s,
                    "zone": zone.id,
                    "pressure": zone.pressure,
                    "excess_mass": zone.excess_mass
                }
            )

    def run(self):

        self.initialize()

        t = 0.0

        while t <= self.t_end:

            self.compute_flows(t)

            self.integrate()

            self.save_step(t)

            t += self.dt

    def save_csv(
        self,
        filename
    ):

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "time",
                    "zone",
                    "pressure",
                    "excess_mass"
                ]
            )

            writer.writeheader()

            writer.writerows(
                self.time_history
            )

    def save_link_csv(
        self,
        filename
    ):

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "time",
                    "link",
                    "delta_p",
                    "area",
                    "alpha",
                    "m12",
                    "m21"
                ]
            )

            writer.writeheader()

            writer.writerows(
                self.link_history
            )

    def plot_link_dynamics(
        self,
        link_id,
        filename="link_dynamics.png"
    ):

        df = pd.DataFrame(
            self.link_history
        )

        df = df[
            df["link"] == link_id
        ]

        fig, axs = plt.subplots(
            3,
            1,
            figsize=(12, 10),
            sharex=True
        )

        axs[0].plot(
            df["time"],
            df["delta_p"],
            color="black"
        )

        axs[0].set_ylabel(
            "ΔP [Pa]"
        )

        axs[0].grid(True)

        axs[1].plot(
            df["time"],
            df["area"],
            "--r"
        )

        axs[1].set_ylabel(
            "Área [m²]"
        )

        axs[1].grid(True)

        axs[2].plot(
            df["time"],
            df["m12"],
            label="Nodo1 → Nodo2"
        )

        axs[2].plot(
            df["time"],
            df["m21"],
            label="Nodo2 → Nodo1"
        )

        axs[2].set_ylabel(
            "Flujo [kg/s]"
        )

        axs[2].set_xlabel(
            "Tiempo [s]"
        )

        axs[2].legend()

        axs[2].grid(True)

        plt.tight_layout()

        plt.savefig(
            filename,
            dpi=300
        )

        plt.close()