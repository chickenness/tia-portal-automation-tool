from __future__ import annotations

from .modules import objects
from .xml import OrganizationBlock as OB
from datetime import datetime
from pathlib import Path
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
    contract_path: Path = Path(path.parent.parent.parent.joinpath(r"Bin/PublicAPI/Siemens.Engineering.Contract.dll"))
    clr.AddReference(contract_path.as_posix()) # C:\\Program Files\\Siemens\\Automation\\Portal V18\\Bin\\PublicAPI\\Siemens.Engineering.Contract.dll
    clr.AddReference(path.as_posix()) # C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll
    
    # Import the Siemens modules
    import Siemens.Engineering as tia
    import Siemens.Engineering.Compiler as comp
    import Siemens.Engineering.HW.Features as hwf
    
    return tia, comp, hwf

tia     = None
comp    = None
hwf     = None


def TiaPortal(config: objects.Config) -> Siemens.Engineering.TiaPortal:
    conf = config
    if conf.enable_ui:
        print("Starting TIA with UI")
        TIA = tia.TiaPortal(tia.TiaPortalMode.WithUserInterface)
    else:
        print("Starting TIA without UI")
        TIA = tia.TiaPortal(tia.TiaPortalMode.WithoutUserInterface)

    return TIA

def create_project(tia: Siemens.Engineering.TiaPortal, name: str, parent_directory: Path, replace=False) -> Siemens.Engineering.Project:
    existing_project_path: DirectoryInfo = DirectoryInfo(parent_directory.joinpath(name).as_posix())

    if existing_project_path.Exists:
        if replace:
            existing_project_path.Delete(True)
        else:
            raise PPError(f"Failed creating project. Project already exists ({existing_project_path})")

    project_path: DirectoryInfo = DirectoryInfo(parent_directory.as_posix())
    project_composition: Siemens.Engineering.ProjectComposition = tia.Projects
    project: Siemens.Engineering.Project = project_composition.Create(project_path, name)

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

def create_plc_block_from_mastercopy(plc_block: Siemens.Engineering.SW.Blocks.PlcBlock,
                                     master_copy: Siemens.Engineering.MasterCopies.MasterCopy
                                     ) -> None:
    block = plc_block.CreateFrom(master_copy)

    return block

def create_io_system(itf: Siemens.Engineering.HW.Features.NetworkInterface,
                     data: objects.Network,
                     ) -> tuple[Siemens.Engineering.HW.Subnet, Siemens.Engineering.HW.IoSystem]:
    subnet: Siemens.Engineering.HW.Subnet = itf.Nodes[0].CreateAndConnectToSubnet(data.subnet_name)
    io_system: Siemens.Engineering.HW.IoSystem = itf.IoControllers[0].CreateIoSystem(data.io_controller)

    return (subnet, io_system)

def create_tag_table(software_base: Siemens.Engineering.HW.Software, data: objects.TagTable) -> Siemens.Engineering.SW.Tags.PlcTagTable:
    return software_base.TagTableGroup.TagTables.Create(data.name)

def create_tag(table: Siemens.Engineering.SW.Tags.PlcTagTable, tag: objects.Tag) -> None:
    table.Tags.Create(tag.tag_name, tag.data_type, tag.logical_address)
    print(f"Creating tags... {tag.tag_name}")

def access_device_item_from_device(device: Siemens.Engineering.HW.Device, index: int = 0) -> Siemens.Engineering.HW.DeviceItem:
    return device.DeviceItems[index]

def access_device_item_from_device_item(device_item: Siemens.Engineering.HW.DeviceItem, index: int = 0) -> Siemens.Engineering.HW.DeviceItem:
    return device_item.DeviceItems[index]

def access_network_interface_feature(device_item: Siemens.Engineering.HW.DeviceItem) -> Siemens.Engineering.HW.Features.NetworkInterface | None:
    itf: Siemens.Engineering.HW.Features.NetworkInterface = tia.IEngineeringServiceProvider(device_item).GetService[hwf.NetworkInterface]()
    if not itf:
        return None

    return itf

def access_software_container(device_item: Siemens.Engineering.HW.DeviceItem) -> Siemens.Engineering.SW.PlcSoftware | None:
    software_container: Siemens.Engineering.SW.PlcSoftware = tia.IEngineeringServiceProvider(device_item).GetService[hwf.SoftwareContainer]()
    if not software_container:
        return None

    return software_container

def find_plc_by_name(project: Siemens.Engineering.Project, name: str) -> Siemens.Engineering.HW.Features.SoftwareContainer:
    devices: Siemens.Engineering.HW.DeviceComposition = project.Devices
    for device in devices:
        for device_item in device.DeviceItems:
            plc: Siemens.Engineering.HW.Features.SoftwareContainer = access_software_container(device_item)
            if not plc:
                continue
            plc_software: Siemens.Engineering.SW.PlcSoftware = plc.Software
            if not isinstance(plc_software, tia.SW.PlcSoftware):
                continue
            if plc_software.Name.lower() == name.lower():
                return plc_software

def find_master_copy_by_name(library: Siemens.Engineering.Library.GlobalLibrary, name: str) -> Siemens.Engineering.Library.MasterCopies.MasterCopy:
    system_folder: Siemens.Engineering.Library.MasterCopies.MasterCopySystemFolder = library.MasterCopyFolder
    mastercopies: Siemens.Engineering.Library.MasterCopies.MasterCopyComposition = system_folder.MasterCopies
    master_copy: Siemens.Engineering.Library.MasterCopies.MasterCopy = mastercopies.Find(name)

    return master_copy

def connect_to_io_system(itf: Siemens.Engineering.HW.Features.NetworkInterface,
                         subnet: Siemens.Enginerring.HW.Subnet,
                         io_system: Siemens.Engineering.HW.IoSystem,
                         ) -> None:
    itf.Nodes[0].ConnectToSubnet(subnet)
    if itf.IoConnectors.Count > 0:
        itf.IoConnectors[0].ConnectToIoSystem(io_system)
    
def set_object_attributes(obj: Siemens.Engineering.IEngineeringObject, **attributes) -> None:
    for attribute, value in attributes.items():
        obj_attrs: Siemens.Engineering.EngineeringAttributeInfo = obj.GetAttributeInfos()
        for attrib in obj_attrs: # we do a lil bit of iteration
            if attrib.Name == attribute:
                obj.SetAttribute(attribute, value)

def query_program_blocks_of_device(plc: Siemens.Engineering.SW.PlcSoftware) -> list[Siemens.Engineering.SW.Blocks.PlcBlocks]:
    software: Siemens.Engineering.SW.PlcSoftware = plc.Software
    if not isinstance(software, tia.SW.PlcSoftware):
        return []

    return software.BlockGroup.Blocks

def enumerate_master_copies_in_system_folder(master_copy_system_folder: Siemens.Engineering.Library.MasterCopies.MasterCopySystemFolder) -> list[Siemens.Engineering.Library.MasterCopies.MasterCopy]:
    return [master_copy for master_copy in master_copy_system_folder.MasterCopies]

def enumerate_open_libraries(tia: Siemens.Engineering.TiaPortal) -> Siemens.Engineering.Library.GlobalLibrary:
    return [library for library in tia.GlobalLibraries]
    
def open_library(portal: Siemens.Engineering.TiaPortal, file_info: FileInfo, is_read_only: bool = True) -> Siemens.Engineering.Library.GlobalLibrary:
    if not is_read_only:
        return portal.GlobalLibraries.Open(file_info, tia.OpenMode.ReadWrite) # Write access to the library. Data can be written to the library.
    return portal.GlobalLibraries.Open(file_info, tia.OpenMode.ReadOnly) # Read access to the library. Data can be read from the library.

def compile_block(block: Siemens.Engineering.SW.Blocks.PlcBlock) -> Siemens.Engineering.Compiler.CompilerResult:
    single_compile: Siemens.Engineering.Compiler.ICompilable = block.GetService[tia.Compiler.ICompilable]();
    result: Siemens.Engineering.Compiler.CompilerResult = single_compile.Compile()

    return result

def export_block_as_xml(block: Siemens.Engineering.SW.Blocks.PlcBlock,
                        directory: Path,
                        ) -> None:
    if not directory.exists():
        raise PPError(f"Directory does not exist: {directory}")
    if not directory.is_dir():
        raise PPError(f"Path is not a directory: {directory}")

    file_path: FileInfo = FileInfo(f"{directory.as_posix()}/{block.Name}.xml")
    if file_path.Exists:
        raise PPError(f"File already exists: {file_path}")

    export_options: Siemens.Engineering.ExportOptions = tia.ExportOptions.WithReadOnly | tia.ExportOptions.WithDefaults   

    block.Export(file_path, export_options)

    return

def import_xml_block(blocks: Siemens.Engineering.SW.Blocks.PlcBlockComposition,
                     xml: FileInfo,
                     ) -> None:
    blocks.Import(xml, tia.ImportOptions.Override)

    return

def create_instance_db(plc: Siemens.Engineering.HW.Features.SoftwareContainer, name: str,
                       number: int, instance_of_name: str) -> Siemens.Engineering.SW.Blocks.InstanceDB:
    name = name + "_DB"
    blocks: Siemens.Engineering.SW.Blocks.PlcBlockComposition = plc.BlockGroup.Blocks
    for block in blocks:
        if name == block.Name:
            raise PPError(f"The block name '{name}' is invalid. An object with this name or this number already exists.")
    instance_db = blocks.CreateInstanceDB(name, True, number, instance_of_name)

    return instance_db

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
