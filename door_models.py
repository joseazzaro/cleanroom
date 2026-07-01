from enum import Enum
import math


class DoorState(Enum):

    CLOSED = 0
    OPENING = 1
    OPEN = 2
    CLOSING = 3


class SwingDoor:

    def __init__(
        self,
        width,
        height,
        closed_leakage_area,
        opening_speed_deg_s,
        max_angle_deg,
        hold_open_time_s,
    ):

        self.width = width
        self.height = height

        self.closed_leakage_area = closed_leakage_area

        self.opening_speed_deg_s = opening_speed_deg_s

        self.max_angle_deg = max_angle_deg

        self.hold_open_time_s = hold_open_time_s

    def opening_time(self):

        return (
            self.max_angle_deg
            / self.opening_speed_deg_s
        )

    def cycle_duration(self):

        return (
            2.0 * self.opening_time()
            +
            self.hold_open_time_s
        )

    def angle(self, elapsed_time):

        t_open = self.opening_time()

        t_hold_start = t_open
        t_hold_end = (
            t_open
            +
            self.hold_open_time_s
        )

        t_close_end = (
            t_hold_end
            +
            t_open
        )

        if elapsed_time < 0:

            return 0.0

        if elapsed_time <= t_open:

            return (
                self.opening_speed_deg_s
                * elapsed_time
            )

        if elapsed_time <= t_hold_end:

            return self.max_angle_deg

        if elapsed_time <= t_close_end:

            return (
                self.max_angle_deg
                -
                self.opening_speed_deg_s
                *
                (elapsed_time - t_hold_end)
            )

        return 0.0

    def state(self, elapsed_time):

        t_open = self.opening_time()

        t_hold_end = (
            t_open
            +
            self.hold_open_time_s
        )

        t_close_end = (
            t_hold_end
            +
            t_open
        )

        if elapsed_time < 0:
            return DoorState.CLOSED

        if elapsed_time < t_open:
            return DoorState.OPENING

        if elapsed_time < t_hold_end:
            return DoorState.OPEN

        if elapsed_time < t_close_end:
            return DoorState.CLOSING

        return DoorState.CLOSED

    def current_area(self, elapsed_time):

        theta = self.angle(
            elapsed_time
        )

        if theta <= 0.0:

            return (
                self.closed_leakage_area
            )

        if theta <= 60.0:

            theta_rad = math.radians(
                theta
            )

            area = (
                2.0
                * self.height
                * self.width
                *
                math.sin(
                    theta_rad / 2.0
                )
            )

        else:

            area = (
                self.height
                *
                self.width
            )

        return max(
            area,
            self.closed_leakage_area
        )
    
    def current_alpha(
        self,
        elapsed_time
    ):

        area = self.current_area(
            elapsed_time
        )

        full_area = (

            self.width
            *
            self.height

        )

        return (

            area
            -
            self.closed_leakage_area

        ) / (

            full_area
            -
            self.closed_leakage_area

        )