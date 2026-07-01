class DoorEvent:

    def __init__(
        self,
        event_id,
        link_id,
        start_time,
    ):

        self.id = event_id

        self.link_id = link_id

        self.start_time = start_time


class EventManager:

    def __init__(self):

        self.events = []

    def add_event(self, event):

        self.events.append(event)

    def get_active_event(
        self,
        link_id,
        current_time,
    ):

        for event in self.events:

            if (
                event.link_id
                ==
                link_id
            ):

                if (
                    current_time
                    >=
                    event.start_time
                ):

                    return event

        return None

    def elapsed_time(
        self,
        event,
        current_time,
    ):

        return (
            current_time
            -
            event.start_time
        )