import numpy as np

from contam_solver import (
    mass_flow,
    dmass_flow_dpressure
)


class DynamicNetworkSolver:

    def __init__(

        self,

        network,

        max_iterations=25,

        tolerance=1e-5

    ):

        self.network = network

        self.max_iterations = max_iterations

        self.tolerance = tolerance

    def unknown_zones(self):

        return [

            z

            for z

            in self.network.internal_zones()

        ]

    def residual_vector(self):

        zones = self.unknown_zones()

        n = len(zones)

        R = np.zeros(n)

        index = {

            z.id: i

            for i, z in enumerate(zones)

        }

        for i, z in enumerate(zones):

            R[i] = (

                z.m_supply

                - z.m_exhaust

                - z.return_mass_flow_fixed

            )

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

                R[
                    index[z1.id]
                ] -= flow

            if not z2.is_boundary:

                R[
                    index[z2.id]
                ] += flow

        return R

    def jacobian(self):

        zones = self.unknown_zones()

        n = len(zones)

        J = np.zeros((n, n))

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

    def solve(self):

        zones = self.unknown_zones()

        for _ in range(
            self.max_iterations
        ):

            R = self.residual_vector()

            if np.max(
                np.abs(R)
            ) < self.tolerance:

                return True

            J = self.jacobian()

            try:

                correction = np.linalg.solve(
                    J,
                    R
                )

            except Exception:

                return False

            for i, zone in enumerate(zones):

                zone.pressure -= correction[i]

        return False