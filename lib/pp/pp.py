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
    
def create_io_system(itf: Siemens.Engineering.HW.Features.NetworkInterface,
                     data: objects.Network,
                     ) -> tuple[Siemens.Engineering.HW.Subnet, Siemens.Engineering.HW.IoSystem]:
    subnet: Siemens.Engineering.HW.Subnet = itf.Nodes[0].CreateAndConnectToSubnet(data.subnet_name)
    io_system: Siemens.Engineering.HW.IoSystem = itf.IoControllers[0].CreateIoSystem(data.io_controller)

    return (subnet, io_system)

def connect_to_io_system(itf: Siemens.Engineering.HW.Features.NetworkInterface,
                         subnet: Siemens.Enginerring.HW.Subnet,
                         io_system: Siemens.Engineering.HW.IoSystem,
                         ) -> None:
    itf.Nodes[0].ConnectToSubnet(subnet)
    if itf.IoConnectors.Count > 0: # why is this a bit shift?
        itf.IoConnectors[0].ConnectToIoSystem(io_system)
    
def set_node_attributes(node: Siemens.Engineering.HW.Node, **attributes) -> None:
    for attribute, value in attributes.items():
        print(f"    {attribute}:{value}")
        if node.GetAttribute == attribute:
            print(f"    node attribute has been set ({attribute}:{value})")
            node.SetAttribute(attribute, value)

def access_software_container(device_item: Siemens.Engineering.HW.DeviceItem) -> Siemens.Engineering.HW.Features.SoftwareContainer | None:
    software_container: Siemens.Engineering.HW.Features.SoftwareContainer = tia.IEngineeringServiceProvider(device_item).GetService[hwf.SoftwareContainer]()
    if not software_container:
        return None

    return software_container

def create_tag_table(software_base: Siemens.Engineering.HW.Software, data: objects.TagTable) -> Siemens.Engineering.SW.Tags.PlcTagTable:
    return software_base.TagTableGroup.TagTables.Create(data.name)

def create_tag(table: Siemens.Engineering.SW.Tags.PlcTagTable, tag: objects.Tag) -> None:
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

    devices: list[Siemens.Engineering.HW.Device] = []
    interfaces: list[Siemens.Engineering.HW.Features.NetworkInterface] = []
    for data in config.project.devices:
        device_composition: Siemens.Engineering.HW.DeviceComposition = project.Devices
        device: Siemens.Engineering.HW.Device = create_device(device_composition, data)
        devices.append(device)
        hw_object: Siemens.Engineering.HW.HardwareObject = device.DeviceItems[0]
        for data_dev_item in data.items:
            create_and_plug_device_item(hw_object, data_dev_item, data.slots_required)
        device_items = access_device_item_from_device(device, 1).DeviceItems
        for item in device_items:
            network_service = access_network_interface_feature(item)
            if type(network_service) is hwf.NetworkInterface:
                node: Siemens.Engineeering.HW.Node = network_service.Nodes[0]
                attributes = {"Address" : data.network_address}
                print(node, attributes)
                # set_node_attributes(node, **attributes)
                network_service.Nodes[0].SetAttribute('Address', data.network_address)
                print(f"Added a network address: {data.network_address}")
                interfaces.append(network_service)

        for device_item in device.DeviceItems:
            software_container: Siemens.Engineering.HW.Features.SoftwareContainer = access_software_container(device_item)
            if not software_container:
                continue
            software_base: Siemens.Engineering.HW.Software = software_container.Software
            if not isinstance(software_base, tia.SW.PlcSoftware):
                continue
            tag_table = create_tag_table(software_base, data.tag_table)
            if not isinstance(tag_table, tia.SW.Tags.PlcTagTable):
                continue
            for tag in data.tag_table.tags:
                create_tag(tag_table, tag)

    subnet: Siemens.Engineering.HW.Subnet = None
    io_system: Siemens.Engineering.HW.IoSystem = None
    network: list[objects.Network] = config.project.networks

    for i in range(len(network)):
        for n in range(len(interfaces)):
            if interfaces[n].Nodes[0].GetAttribute('Address') != network[i].address:
                continue
            if i == 0:
                subnet, io_system = create_io_system(interfaces[0], network[0])
                print(f"Creating Subnet and IO system: {network[0].subnet_name} <{network[0].io_controller}>")
                continue
            connect_to_io_system(interfaces[n], subnet, io_system)
            print(f"Connecting to Subnet and IO system: {network[i].subnet_name} <{network[i].io_controller}>")
