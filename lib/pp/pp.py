from __future__ import annotations

from .modules import objects
from datetime import datetime
from pathlib import Path
from typing import Union
import json

class PPLogger:
    def __init__(self, message: str) -> None:
        self.message: str = message
        self.timestamp: datetime = datetime.now()

    def __repr__(self) -> str:
        return f"[{self.timestamp}] {self.message}"

class PPError(Exception):
    def __init__(self, err: str) -> None:
        self.err: str = err

class ProjectExistsError(PPError):
    def __init__(self, err: str) -> None:
        super().__init__(err)

    def __repr__(self) -> str:
        return f"ProjectExistsError: {self.err}"

import clr
from System.IO import DirectoryInfo, FileInfo

def import_siemens_module(path: Path):
    """
    Imports Siemens modules dynamically based on the provided path.
    
    Args:
        path (str): The path to the Siemens assembly.
    
    Returns:
        tuple: A tuple containing the imported modules.
    """
    clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V18\\Bin\\PublicAPI\\Siemens.Engineering.Contract.dll')
    clr.AddReference(path.as_posix())
    
    # Import the Siemens modules
    import Siemens.Engineering as tia
    import Siemens.Engineering.Compiler as comp
    import Siemens.Engineering.HW.Features as hwf
    
    return tia, comp, hwf

tia     = None
comp    = None
hwf     = None


def TiaPortal(config: objects.Config) -> Siemens.Engineering.TiaPortal:
    # probs make this part run multithreaded since it hangs the gui process
    conf = config
    if conf.enable_ui:
        print("Starting TIA with UI")
        TIA = tia.TiaPortal(tia.TiaPortalMode.WithUserInterface)
    else:
        print("Starting TIA without UI")
        TIA = tia.TiaPortal(tia.TiaPortalMode.WithoutUserInterface)

    return TIA

def create_project(tia: Siemens.Engineering.Tia, name: str, project_directory: Path) -> Siemens.Engineering.Project:
    project_path: DirectoryInfo = DirectoryInfo(project_directory.joinpath(name).as_posix())
    if project_path.Exists:
        raise PPError(f"Failed creating project. Project already exists ({project_path})")

    project_directory: DirectoryInfo = DirectoryInfo(project_directory.as_posix())

    project_composition: Siemens.Engineering.ProjectComposition = tia.Projects
    project: Siemens.Engineering.Project = project_composition.Create(project_directory, name)

    return project

def add_devices(project: Siemens.Engineering.Project,
                objects: list[objects.Device],
                ) -> tuple[list[Siemens.Engineering.HW.DeviceImpl], list[Siemens.Engineering.HW.Features.NetworkInterface]]:
    devices: list[Siemens.Engineering.HW.Device] = []
    interface: list[Siemens.Engineering.HW.Features.NetworkInterface] = []
    for data in objects:
        device_composition: Siemens.Engineering.HW.DeviceComposition = project.Devices
        device: Siemens.Engineering.HW.Device = create_device(device_composition, data)
        devices.append(device)
        hw_object: Siemens.Engineering.HW.HardwareObject = device.DeviceItems[0]
        for data_dev_item in data.items:
            create_and_plug_device_item(hw_object, data_dev_item, data.slots_required)
        network_service = assign_device_address(device, data.network_address)
        interface.append(network_service)

        # tag_table = create_tag_table(hw, dev.tag_table, siemens)
        # if isinstance(tag_table, siemens.tia.SW.Tags.PlcTagTable):
        #     add_tags(tag_table, dev.tag_table.tags)

    return devices, [i for i in interface if i is not None]

def create_device(devices: Siemens.Engineering.HW.DeviceComposition, data: objects.Device) -> Siemens.Engineering.HW.Device:
    device: Siemens.Engineering.HW.Device = devices.CreateWithItem(data.DeviceItemTypeId, data.DeviceTypeId, data.DeviceItemName)

    return device

def create_and_plug_device_item(hw_object: Siemens.Engineering.HW.HardwareObject,
                                data: objects.DeviceItem,
                                slots_required: int
                                ) -> None:
    if hw_object.CanPlugNew(data.TypeIdentifier, data.Name, data.PositionNumber + slots_required):
        hw_object.PlugNew(data.TypeIdentifier, data.Name, data.PositionNumber + slots_required)
        print(f"{data.TypeIdentifier} PLUGGED on [{data.PositionNumber + slots_required}].")

        return

    print(f"{data.TypeIdentifier} Not PLUGGED on {data.PositionNumber + slots_required}")

def access_device_item_from_device(device: Siemens.Engineering.HW.Device, index: int = 0) -> Siemens.Engineering.HW.DeviceItem:
    return device.DeviceItems[index]

def access_device_item_from_device_item(device_item: Siemens.Engineering.HW.DeviceItem, index: int = 0) -> Siemens.Engineering.HW.DeviceItem:
    return device_item.DeviceItems[index]

def access_network_interface_feature(device_item: Siemens.Engineering.HW.DeviceItem) -> Siemens.Engineering.HW.Features.NetworkInterface | None:
    itf: Siemens.Engineering.HW.Features.NetworkInterface = tia.IEngineeringServiceProvider(device_item).GetService[hwf.NetworkInterface]()
    if itf:
        return itf

    return None
    
def set_node_attributes(node: Siemens.Engineering.HW.Node, **attributes) -> None:
    for attribute, value in attributes.items():
        if node.GetAttribute == attribute:
            node.SetAttribute(attribute, value)

def assign_device_address(device: Siemens.Engineering.HW.DeviceImpl, address: str) -> list[Siemens.Engineering.HW.Features.NetworkInterface] | None: 
    device_items = access_device_item_from_device(device, 1).DeviceItems
    for item in device_items:
        network_service = access_network_interface_feature(item)
        if type(network_service) is hwf.NetworkInterface:
            node: Siemens.Engineeering.HW.Node = network_service.Nodes[0]
            attributes = {"Address" : address}
            set_node_attributes(node, **attributes)
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

def create_tag_table(device: Siemens.Engineering.HW.DeviceImpl,
                     tag_table: objects.TagTable,
                     siemens: Siemens
                     ) -> Siemens.Engineering.SW.Tags.PlcTagTable:
    for device_item in device.DeviceItems:
        software_container = device_item.GetService[siemens.hwf.SoftwareContainer]()
        if software_container:
            software_base = software_container.Software
            if isinstance(software_base, siemens.tia.SW.PlcSoftware):

                table = software_base.TagTableGroup.TagTables.Create(tag_table.name)
                return table

def add_tags(table: Siemens.Engineering.SW.Tags.PlcTagTable, tags: list[objects.Tag]) -> None:
    for tag in tags:
        table.Tags.Create(tag.tag_name, tag.data_type, tag.logical_address)
        print(f"Creating tags... {tag.tag_name}")

def parse(path: str) -> objects.Config:
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

    return config

def execute(config: objects.Config):
    portal = TiaPortal(config)
    project = create_project(portal, config.project.name, config.project.directory)
    hardware = add_devices(project, config.project.devices)
    # connect_device_interface(hardware[1], self.config.project.networks)
