import csv

import pandas as pd
import matplotlib.pyplot as plt


class DynamicSimulation:

    def __init__(
        self,
        network,
        event_manager,
        solver,
        dt,
        t_end
    ):

        self.network = network

        self.event_manager = event_manager

        self.solver = solver

        self.dt = dt

        self.t_end = t_end

        self.zone_history = []

        self.link_history = []

    # ==================================================
    # ACTUALIZAR PUERTAS
    # ==================================================

    def update_doors(
        self,
        current_time
    ):

        for link in self.network.links:

            #
            # Valor por defecto
            #

            link.dynamic_area = (
                link.area
            )

            if link.dynamic_model is None:

                continue

            event = (
                self.event_manager
                .get_active_event(
                    link.id,
                    current_time
                )
            )

            if event is None:

                continue

            elapsed = (
                self.event_manager
                .elapsed_time(
                    event,
                    current_time
                )
            )

            link.dynamic_area = (

                link.dynamic_model
                .current_area(
                    elapsed
                )

            )

    # ==================================================
    # GUARDAR RESULTADOS
    # ==================================================

    def save_step(
        self,
        current_time
    ):

        #
        # Zonas
        #

        for zone in self.network.zones.values():

            self.zone_history.append(
                {
                    "time": current_time,
                    "zone": zone.id,
                    "pressure": zone.pressure
                }
            )

        #
        # Links
        #

        for link in self.network.links:

            z1 = self.network.get_zone(
                link.node1
            )

            z2 = self.network.get_zone(
                link.node2
            )

            self.link_history.append(
                {
                    "time": current_time,

                    "link": link.id,

                    "area": link.current_area(),

                    "delta_p": (
                        z1.pressure
                        -
                        z2.pressure
                    )
                }
            )

    # ==================================================
    # RUN
    # ==================================================

    def run(self):

        t = 0.0

        while t <= self.t_end:

            #
            # Actualizar áreas
            #

            self.update_doors(
                t
            )

            #
            # Resolver red
            #

            converged = (
                self.solver.solve()
            )

            if not converged:

                print(
                    f"Advertencia: "
                    f"No converge en t={t:.2f}s"
                )

            #
            # Guardar
            #

            self.save_step(
                t
            )

            #
            # Avanzar tiempo
            #

            t += self.dt

    # ==================================================
    # CSV ZONAS
    # ==================================================

    def save_zone_csv(
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
                    "pressure"
                ]
            )

            writer.writeheader()

            writer.writerows(
                self.zone_history
            )

    # ==================================================
    # CSV LINKS
    # ==================================================

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
                    "area",
                    "delta_p"
                ]
            )

            writer.writeheader()

            writer.writerows(
                self.link_history
            )

    # ==================================================
    # GRÁFICO
    # ==================================================

    def plot_link(
        self,
        link_id,
        filename
    ):

        df = pd.DataFrame(
            self.link_history
        )

        df = df[
            df["link"] == link_id
        ]

        fig, ax1 = plt.subplots(
            figsize=(10, 6)
        )

        ax1.plot(
            df["time"],
            df["delta_p"],
            color="black",
            linewidth=2
        )

        ax1.set_ylabel(
            "ΔP [Pa]"
        )

        ax1.grid(True)

        ax2 = ax1.twinx()

        ax2.plot(
            df["time"],
            df["area"],
            "r--",
            linewidth=2
        )

        ax2.set_ylabel(
            "Área [m²]"
        )

        ax1.set_xlabel(
            "Tiempo [s]"
        )

        plt.title(
            f"Link {link_id}"
        )

        plt.tight_layout()

        plt.savefig(
            filename,
            dpi=300
        )

        plt.close()