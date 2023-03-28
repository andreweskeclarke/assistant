import pytest

from assistant.message_bus.assistant_manager import Client, MessageRouter, RoutingError
from assistant.message_bus.client import JsonMessageClient


def test_route_message_between_a_few_clients() -> None:
    router = MessageRouter()
    trip_bookings = Client(
        name="Trip Bookings",
        client=JsonMessageClient("trip-bookings.uuid_a"),
        client_uuid="uuid_a",
        topic="trip-bookings.uuid_a",
        description="This plugin is responsible for booking trips. It can also list trip options and cancel trips.",
    )
    wikipedia = Client(
        name="Wikipedia Queries",
        client=JsonMessageClient("wikipedia.uuid_b"),
        client_uuid="uuid_b",
        topic="wikipedia.uuid_b",
        description="This plugin can query wikipedia and return the contents of an article. It is useful for answering general knowledge questions and current event questions.",
    )
    fallback = Client(
        name="Fallback",
        client=JsonMessageClient("fallback.uuid_c"),
        client_uuid="uuid_c",
        topic="fallback.uuid_c",
        description="This plugin is the generic fallback plugin. It is used when no other plugin can handle a message.",
    )
    router.add(trip_bookings)
    router.add(wikipedia)
    router.add(fallback)
    assert (
        router.route_message("What kind of flights can I find from Chicago to Paris?")
        == trip_bookings
    )
    assert (
        router.route_message("Can you find me a hotel in Mexico City?") == trip_bookings
    )
    assert router.route_message("Who was Napoleon?") == wikipedia
    assert router.route_message("What can you tell me about Mexico City?") == wikipedia
    assert router.route_message("When did dinosaurs become extinct?") == wikipedia
    assert router.route_message("How are you doing today?") == fallback

    with pytest.raises(RoutingError):
        router.route_message("")
