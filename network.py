from psychrometrics import (
    air_density,
    kinematic_viscosity
)


class Zone:

    def __init__(
        self,
        zone_id,
        volume,
        temperature,
        rh,
        pressure,
        supply_m3h,
        exhaust_m3h,
        is_boundary=False,
        reference_height=0.0,
        p_atm=101325,
    ):

        self.id = zone_id

        self.volume = volume

        self.temperature = temperature
        self.rh = rh

        #
        # Presión nodal
        #
        self.pressure = pressure

        self.reference_height = (
            reference_height
        )

        self.is_boundary = (
            is_boundary
        )

        self.rho = air_density(
            temperature,
            rh,
            p_atm
        )

        self.nu = kinematic_viscosity(
            temperature,
            rh,
            p_atm
        )

        #
        # HVAC
        #

        self.supply_m3h = (
            supply_m3h
        )

        self.exhaust_m3h = (
            exhaust_m3h
        )

        self.m_supply = (
            self.rho
            * supply_m3h
            / 3600.0
        )

        self.m_exhaust = (
            self.rho
            * exhaust_m3h
            / 3600.0
        )

        #
        # Se calcula una sola vez
        # a partir del estado inicial
        #

        self.return_mass_flow_fixed = 0.0

        #
        # Variables de balance
        #

        self.m_in = 0.0

        self.m_out = 0.0

        self.mass_residual = 0.0

    def reset_flows(self):

        self.m_in = 0.0

        self.m_out = 0.0

        self.mass_residual = 0.0

    @property
    def return_mass_flow(self):

        return (

            self.m_supply

            + self.m_in

            - self.m_exhaust

            - self.m_out

        )

    @property
    def return_volume_flow(self):

        return (

            self.return_mass_flow

            / self.rho

            * 3600.0

        )


class Link:

    def __init__(
        self,
        link_id,
        link_type,
        node1,
        node2,
        area,
        cd,
        n,
        width=None,
        height=None
    ):

        self.id = link_id

        self.type = link_type

        self.node1 = node1

        self.node2 = node2

        #
        # Área base (puerta cerrada)
        #

        self.area = area

        #
        # Área usada por el solver
        #

        self.dynamic_area = area

        self.width = width

        self.height = height

        self.cd = cd

        self.n = n

        self.dynamic_model = None

    def is_door(self):

        return self.type in (
            "swing_door",
            "sliding_door"
        )

    def current_area(self):

        return self.dynamic_area


class AirflowNetwork:

    def __init__(self):

        self.zones = {}

        self.links = []

    def add_zone(
        self,
        zone
    ):

        self.zones[
            zone.id
        ] = zone

    def add_link(
        self,
        link
    ):

        self.links.append(
            link
        )

    def get_zone(
        self,
        zone_id
    ):

        return self.zones[
            zone_id
        ]

    def get_link(
        self,
        link_id
    ):

        for link in self.links:

            if link.id == link_id:

                return link

        return None

    def reset_balances(self):

        for zone in self.zones.values():

            zone.reset_flows()

    def internal_zones(self):

        return [

            zone

            for zone in self.zones.values()

            if not zone.is_boundary

        ]

    def boundary_zones(self):

        return [

            zone

            for zone in self.zones.values()

            if zone.is_boundary

        ]