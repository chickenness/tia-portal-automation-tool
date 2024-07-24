from __future__ import annotations

from .modules import objects
from datetime import datetime
from pathlib import Path
from typing import Union
import json
import os

class PPLogger:
    def __init__(self, message: str) -> None:
        self.message: str = message
        self.timestamp: datetime = datetime.now()

    def __repr(self) -> str:
        return f"[{self.timestamp}] {self.message}"

class PPError(Exception):
    def __init__(self, err: str) -> None:
        self.err: str = err

class ProjectExistsError(PPError):
    def __init__(err: str) -> None:
        super().__init__(self, err)

    def __repr__(self) -> str:
        return f"ProjectExistsError: {self.err}"

class Siemens:
    def __init__(self, clr_path: Path) -> Siemens:
        import clr
        clr.AddReference(clr_path.as_posix())

        from System.IO import DirectoryInfo, FileInfo
        import Siemens.Engineering as tia
        import Siemens.Engineering.Compiler as comp
        import Siemens.Engineering.HW.Features as hwf

        self.DirectoryInfo = DirectoryInfo
        self.FileInfo = FileInfo
        self.tia = tia
        self.comp = comp
        self.hwf = hwf


def create_tia_instance(siemens: Siemens, config: objects.Config) -> Siemens.Engineering.TiaPortal:
    TIA: Siemens.Engineering.TiaPortal = siemens.tia.TiaPortal()
    # probs make this part run multithreaded since it hangs the gui process
    conf = config
    if conf.enable_ui:
        print("Starting TIA with UI")
        TIA = siemens.tia.TiaPortal(siemens.tia.TiaPortalMode.WithUserInterface)
    else:
        print("Starting TIA without UI")
        TIA = siemens.tia.TiaPortal(siemens.tia.TiaPortalMode.WithoutUserInterface)

    return TIA

def create_project(siemens: Siemens, tia: Siemens.Engineering.Tia, name: str, directory: Path) -> Siemens.Engineering.Project:
    path = siemens.DirectoryInfo(directory.joinpath(name).as_posix())
    if path.Exists:
        raise PPError(f"Failed creating project. Project already exists ({path})")

    directory = siemens.DirectoryInfo(directory.as_posix())

    project = tia.Projects.Create(directory, name)

    return project

def add_devices(project: Siemens.Engineering.Project, devices: list[objects.Device], siemens: Siemens) -> list[Siemens.Engineering.HW.DeviceImpl]:
    hardware: list[Siemens.Engineering.HW.DeviceImpl] = []
    interface: list[Siemens.Engineering.HW.Features.NetworkInterface] = []
    for dev in devices:
        hw = project.Devices.CreateWithItem(dev.DeviceItemTypeId, dev.DeviceTypeId, dev.DeviceItemName)
        hardware.append(hw)
        add_device_items(project, hw, dev.items, dev.slots_required)
        network_service = assign_device_address(hw, dev.network_address, siemens)
        interface.append(network_service)

    return hardware, [i for i in interface if i is not None]
    # return list(zip(hardware, [i for i in interface if i is not None]))

def add_device_items(project: Siemens.Engineering.Project,
                     device: Siemens.Engineering.HW.DeviceImpl,
                     device_items: list[objects.DeviceItem],
                     slots_required: int
                     ):
    for item in device_items:
        # why is this 0? no idea but it can only use 0 and 1. not sure about 2+ since it returns errors
        if (device.DeviceItems[0].CanPlugNew(item.TypeIdentifier, item.Name, item.PositionNumber + slots_required)):
            device.DeviceItems[0].PlugNew(item.TypeIdentifier, item.Name, item.PositionNumber + slots_required)
            print(f"{item.TypeIdentifier} PLUGGED on [{item.PositionNumber + slots_required}].")
        else:
            print(f"{item.TypeIdentifier} Not PLUGGED on {item.PositionNumber + slots_required}")

def assign_device_address(device: Siemens.Engineering.HW.DeviceImpl, address: str, siemens: Siemens) -> list[Union[Siemens.Engineering.HW.Features.NetworkInterface, None]]:
    items = device.DeviceItems[1].DeviceItems
    for item in items:
        network_service = siemens.tia.IEngineeringServiceProvider(item).GetService[siemens.hwf.NetworkInterface]()
        if type(network_service) is siemens.hwf.NetworkInterface:
            network_service.Nodes[0].SetAttribute('Address', address)
            print(f"Added a network address: {address}")
            return network_service

    return None

def connect_device_interface(interface: list[Siemens.Engineering.HW.Features.NetworkInterface], network: list[objects.Network]):
    subnet = None
    io_system = None
    for i in range(len(network)):
        for n in range(len(interface)):
            if interface[n].Nodes[0].GetAttribute('Address') != network[i].address:
                continue
            if i == 0:
                subnet = interface[0].Nodes[0].CreateAndConnectToSubnet(network[0].subnet_name)
                io_system = interface[0].IoControllers[0].CreateIoSystem(network[0].io_controller)
                print(f"Creating Subnet and IO system: {network[0].subnet_name} <{network[0].io_controller}>")
                continue
            interface[n].Nodes[0].ConnectToSubnet(subnet)
            if (interface[n].IoConnectors.Count) >> 0:
                interface[n].IoConnectors[0].ConnectToIoSystem(io_system)
            print(f"Connecting to Subnet and IO system: {network[i].subnet_name} <{network[i].io_controller}>")


def parse(path: str) -> dict[str, Union[Siemens, objects.Config]]:
    """
    Initialize TIA Portal config parser with the path to the configuration file
    Loads and process the JSON configuration file into python classes.

    :param path: String path to the JSON configuration file
    """

    config_file_path: Path = Path(path)
    
    if not config_file_path.exists():
        raise ValueError(f"JSON config file does not exist: {config_file_path}")

    if not config_file_path.is_file():
        raise ValueError(f"JSON config is not a file: {config_file_path}")

    with open(config_file_path, 'r') as file:
        conf: dict = json.load(file)

    config: objects.Config = objects.start(**conf)
    siemens: Siemens = Siemens(config.dll)

    data: dict[str, Union[Siemens, objects.Config]] = {}
    data['config'] = config
    data['siemens'] = siemens

    return data

