import numpy as np

from contam_solver import (
    mass_flow,
    dmass_flow_dpressure
)


class DynamicNetworkSolver:

    def __init__(
        self,
        network,
        max_iterations=50,
        mass_tolerance=1e-4,
        relaxation=0.75
    ):

        self.network = network

        self.max_iterations = max_iterations

        self.mass_tolerance = mass_tolerance

        self.relaxation = relaxation

    def unknown_zones(self):

        return [

            z

            for z

            in self.network.internal_zones()

        ]

    def residual_vector(self):

        zones = self.unknown_zones()

        residual = np.zeros(
            len(zones)
        )

        index = {

            z.id: i

            for i, z in enumerate(zones)

        }

        total_flow = np.zeros(
            len(zones)
        )

        #
        # HVAC
        #

        for i, zone in enumerate(zones):

            residual[i] = (

                zone.m_supply

                - zone.m_exhaust

                - zone.return_mass_flow_fixed

            )

            total_flow[i] = (

                abs(zone.m_supply)

                + abs(zone.m_exhaust)

                + abs(zone.return_mass_flow_fixed)

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

            dp = (

                z1.pressure

                - z2.pressure

            )

            rho = (
                z1.rho
                + z2.rho
            ) / 2.0

            nu = (
                z1.nu
                + z2.nu
            ) / 2.0

            flow = mass_flow(

                dp,

                link.current_area(),

                link.cd,

                link.n,

                rho,

                nu

            )

            if not z1.is_boundary:

                i = index[z1.id]

                residual[i] -= flow

                total_flow[i] += abs(flow)

            if not z2.is_boundary:

                i = index[z2.id]

                residual[i] += flow

                total_flow[i] += abs(flow)

        return (
            residual,
            total_flow
        )

    def jacobian(self):

        zones = self.unknown_zones()

        n = len(zones)

        J = np.zeros(
            (n, n)
        )

        index = {

            z.id: i

            for i, z in enumerate(zones)

        }

        for link in self.network.links:

            z1 = self.network.get_zone(
                link.node1
            )

            z2 = self.network.get_zone(
                link.node2
            )

            dp = (

                z1.pressure

                - z2.pressure

            )

            rho = (
                z1.rho
                + z2.rho
            ) / 2.0

            nu = (
                z1.nu
                + z2.nu
            ) / 2.0

            dmdp = dmass_flow_dpressure(

                dp,

                link.current_area(),

                link.cd,

                link.n,

                rho,

                nu

            )

            if (

                not z1.is_boundary

                and

                not z2.is_boundary

            ):

                i = index[z1.id]

                j = index[z2.id]

                J[i, i] += dmdp

                J[j, j] += dmdp

                J[i, j] -= dmdp

                J[j, i] -= dmdp

            elif not z1.is_boundary:

                i = index[z1.id]

                J[i, i] += dmdp

            elif not z2.is_boundary:

                j = index[z2.id]

                J[j, j] += dmdp

        return J

    def converged(

        self,

        residual,

        total_flow

    ):

        max_error = 0.0

        for R, F in zip(
            residual,
            total_flow
        ):

            err = abs(R) / max(
                F,
                1e-10
            )

            max_error = max(
                max_error,
                err
            )

        return (
            max_error
            <
            self.mass_tolerance
        )

    def solve(self):

        zones = self.unknown_zones()

        for iteration in range(
            self.max_iterations
        ):

            residual, total_flow = (
                self.residual_vector()
            )

            max_residual = np.max(
                np.abs(residual)
            )

            print(
                f"Iter {iteration:02d} "
                f"MaxResidual={max_residual:.6e}"
            )

            if self.converged(

                residual,

                total_flow

            ):

                return True

            J = self.jacobian()

            try:

                correction = np.linalg.solve(
                    J,
                    residual
                )

            except np.linalg.LinAlgError:

                print(
                    "Jacobiana singular"
                )

                return False

            for i, zone in enumerate(zones):

                zone.pressure -= (

                    self.relaxation

                    * correction[i]

                )

        return False