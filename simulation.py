from contam_solver import mass_flow


class Simulation:

    def __init__(self, network):

        self.network = network

        self.link_results = []

    def reset_balances(self):

        for zone in self.network.zones.values():

            zone.m_in = 0.0
            zone.m_out = 0.0

    def run_steady_state(self):

        self.reset_balances()

        self.link_results = []

        for link in self.network.links:

            z1 = self.network.get_zone(
                link.node1
            )

            z2 = self.network.get_zone(
                link.node2
            )

            delta_p = (
                z1.pressure
                - z2.pressure
            )

            rho = (
                z1.rho + z2.rho
            ) / 2.0

            nu = (
                z1.nu + z2.nu
            ) / 2.0

            m_dot = mass_flow(
                delta_p,
                link.area,
                link.cd,
                link.n,
                rho,
                nu
            )

            if m_dot >= 0:

                z1.m_out += m_dot
                z2.m_in += m_dot

                direction = (
                    f"{z1.id} -> {z2.id}"
                )

            else:

                m_dot = abs(m_dot)

                z2.m_out += m_dot
                z1.m_in += m_dot

                direction = (
                    f"{z2.id} -> {z1.id}"
                )

            q_m3h = (
                m_dot / rho
            ) * 3600.0

            self.link_results.append(
                {
                    "link": link.id,
                    "type": link.type,
                    "direction": direction,
                    "m_dot": m_dot,
                    "q_m3h": q_m3h
                }
            )