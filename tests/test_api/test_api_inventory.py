from unittest import TestCase

from pyinfra.api import Inventory


class TestInventoryApi(TestCase):
    def test_create_inventory(self):
        inventory = Inventory((["somehost", "anotherhost", "anotherotherhost"], {}))
        assert len(inventory) == 3

    def test_create_inventory_data(self):
        default_data = {"default_data": "default_data"}
        inventory = Inventory((["somehost"], default_data))
        assert inventory.get_data() == default_data
        assert inventory.get_host_data("somehost") == {}

    def test_create_inventory_host_data(self):
        default_data = {"default_data": "default_data", "host_data": "none"}
        somehost_data = {"host_data": "host_data"}

        inventory = Inventory(
            (
                [("somehost", somehost_data), "anotherhost"],
                default_data,
            ),
        )

        assert inventory.get_data() == default_data
        assert inventory.get_host_data("somehost") == somehost_data
        assert inventory.get_host_data("anotherhost") == {}
        assert inventory.get_host("anotherhost").data.host_data == "none"

    def test_create_inventory_override_data(self):
        default_data = {"default_data": "default_data", "override_data": "ignored"}
        override_data = {"override_data": "override_data"}
        somehost_data = {"host_data": "host_data"}

        inventory = Inventory(
            (
                [("somehost", somehost_data), "anotherhost"],
                default_data,
            ),
            override_data=override_data,
        )

        assert inventory.get_data() == default_data
        assert inventory.get_override_data() == override_data

        assert inventory.get_host("somehost").data.host_data == "host_data"
        assert inventory.get_host("anotherhost").data.get("host_data") is None

        assert inventory.get_host("somehost").data.override_data == "override_data"
        assert inventory.get_host("anotherhost").data.override_data == "override_data"

    def test_inventory_group_data_not_shared(self):
        group_data = {"test": {}}
        hosts = ["hosthost", "anotherhost"]

        inventory = Inventory(
            (hosts, {}),
            group=(hosts, group_data),
        )

        hosthost = inventory.get_host("hosthost")

        # Test that modifying host.data.<X> *does not* stick (both on the same
        # host and also other hosts).
        hosthost.data.test["hi"] = "no"
        assert hosthost.data.test == {}
        assert inventory.get_host("anotherhost").data.test == {}

        # Test that setting host.data.<X> *does* persist
        hosthost.data.somethingelse = {"hello": "world"}
        assert hosthost.data.somethingelse == {"hello": "world"}
