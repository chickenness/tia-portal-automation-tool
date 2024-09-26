from __future__ import annotations

from .modules import objects
from .xml import OB, FB
from datetime import datetime
from pathlib import Path
import logging
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

logger = logging.getLogger(__name__)

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

    logger.debug(f"config data: {config}")

    if conf.enable_ui:
        TIA = tia.TiaPortal(tia.TiaPortalMode.WithUserInterface)
    else:
        TIA = tia.TiaPortal(tia.TiaPortalMode.WithoutUserInterface)

    current_process = TIA.GetCurrentProcess()
    logger.info(f"Started TIA Portal Openness ({current_process.Id}) {current_process.Mode} at {current_process.AcquisitionTime}")

    return TIA

def create_project(tia: Siemens.Engineering.TiaPortal, name: str, parent_directory: Path, replace=False) -> Siemens.Engineering.Project:
    logger.info(f"Creating project {name} at \"{parent_directory}\"...")

    existing_project_path: DirectoryInfo = DirectoryInfo(parent_directory.joinpath(name).as_posix())

    logger.info(f"Checking for existing project: {existing_project_path}")

    if existing_project_path.Exists:

        logger.info(f"{name} already exists...")

        if replace:

            logger.info(f"Deleting project {name}...")

            existing_project_path.Delete(True)

            logger.info(f"Deleted project {name}")

        else:
            err = f"Failed creating project. Project already exists ({existing_project_path})"
            logger.error(err)
            raise PPError(err)

    logger.info("Creating project...")

    project_path: DirectoryInfo = DirectoryInfo(parent_directory.as_posix())

    logger.debug(f"Project Path: {project_path}")

    project_composition: Siemens.Engineering.ProjectComposition = tia.Projects
    project: Siemens.Engineering.Project = project_composition.Create(project_path, name)

    logger.info(f"Created project {name} at {parent_directory}")

    return project

def create_device(devices: Siemens.Engineering.HW.DeviceComposition, data: objects.Device) -> Siemens.Engineering.HW.Device:
    device: Siemens.Engineering.HW.Device = devices.CreateWithItem(data.DeviceItemTypeId, data.DeviceTypeId, data.DeviceItemName)

    logger.info(f"Created device: ({data.DeviceItemName}, {data.DeviceItemTypeId, data.DeviceTypeId}) on {device.Name}")

    return device

def create_and_plug_device_item(hw_object: Siemens.Engineering.HW.HardwareObject,
                                data: objects.DeviceItem,
                                slots_required: int
                                ) -> None:
    logger.info(f"Plugging {data.TypeIdentifier} on [{data.PositionNumber + slots_required}]...")

    if hw_object.CanPlugNew(data.TypeIdentifier, data.Name, data.PositionNumber + slots_required):
        hw_object.PlugNew(data.TypeIdentifier, data.Name, data.PositionNumber + slots_required)

        logger.info(f"{data.TypeIdentifier} PLUGGED on [{data.PositionNumber + slots_required}]")

        return

    logger.info(f"{data.TypeIdentifier} Not PLUGGED on {data.PositionNumber + slots_required}")

def create_plc_block_from_mastercopy(plc_block: Siemens.Engineering.SW.Blocks.PlcBlock,
                                     master_copy: Siemens.Engineering.MasterCopies.MasterCopy
                                     ) -> Siemens.Engineering.SW.Blocks.PlcBlock:
    logger.info(f"Creating PLC block from {master_copy.Name} Mastercopy")

    block: Siemens.Engineering.SW.Blocks.PlcBlock = plc_block.CreateFrom(master_copy)

    logger.info(f"Successfully created PLC block from {master_copy.Name} Mastercopy")
    logger.debug(f"""PLC Block: {block.Name}
    Number: {block.Number}
    ProgrammingLanguage: {block.ProgrammingLanguage}""")

    return block

def create_io_system(itf: Siemens.Engineering.HW.Features.NetworkInterface,
                     data: objects.Network,
                     ) -> tuple[Siemens.Engineering.HW.Subnet, Siemens.Engineering.HW.IoSystem]:
    logger.info(f"Creating ({data.subnet_name} subnet, {data.io_controller} IO Controller)")

    subnet: Siemens.Engineering.HW.Subnet = itf.Nodes[0].CreateAndConnectToSubnet(data.subnet_name)
    io_system: Siemens.Engineering.HW.IoSystem = itf.IoControllers[0].CreateIoSystem(data.io_controller)

    logger.info(f"Successfully created ({data.subnet_name} subnet, {data.io_controller} IO Controller)")
    logger.debug(f"""Subnet: {subnet.Name}
    NetType: {subnet.NetType}
    TypeIdentifier: {subnet.TypeIdentifier}
IO System: {io_system.Name}
    Number: {io_system.Number}
    Subnet: {io_system.Subnet.Name}""")

    return (subnet, io_system)

def create_tag_table(software_base: Siemens.Engineering.HW.Software, data: objects.TagTable) -> Siemens.Engineering.SW.Tags.PlcTagTable:
    logger.info(f"Creating Tag Table: {data.name} ({software_base.Name} Software)")

    table: Siemens.Engineering.SW.Tags.PlcTagTable = software_base.TagTableGroup.TagTables.Create(data.name)

    logger.info(f"Created Tag Table: {data.name} ({software_base.Name} Software)")
    logger.debug(f"Table: {table.Name}")

    return table

def create_tag(table: Siemens.Engineering.SW.Tags.PlcTagTable, tag: objects.Tag) -> None:
    logger.info(f"Creating Tag: {tag.tag_name} ({table.Name} Table@0x{tag.logical_address} Address)")

    table.Tags.Create(tag.tag_name, tag.data_type, tag.logical_address)

    logger.info(f"Created Tag: {tag.tag_name} ({table.Name} Table@0x{tag.logical_address} Address)")

def access_device_item_from_device(device: Siemens.Engineering.HW.Device, index: int = 0) -> Siemens.Engineering.HW.DeviceItem:
    logger.debug(f"Accessing a DeviceItem Index {index} at Device {device.Name}")

    return device.DeviceItems[index]

def access_device_item_from_device_item(device_item: Siemens.Engineering.HW.DeviceItem, index: int = 0) -> Siemens.Engineering.HW.DeviceItem:
    logger.debug(f"Accessing a DeviceItem Index {index} at DeviceItem {device_item.Name}")

    return device_item.DeviceItems[index]

def access_network_interface_feature(device_item: Siemens.Engineering.HW.DeviceItem) -> Siemens.Engineering.HW.Features.NetworkInterface | None:
    logger.debug(f"Accessing a NetworkInterface at DeviceItem {device_item.Name}")

    itf: Siemens.Engineering.HW.Features.NetworkInterface = tia.IEngineeringServiceProvider(device_item).GetService[hwf.NetworkInterface]()
    if not itf:

        logger.debug(f"No NetworkInterface found for DeviceItem {device_item.Name}")

        return None

    logger.debug(f"Found NetworkInterface for DeviceItem {device_item.Name}")

    return itf

def access_software_container(device_item: Siemens.Engineering.HW.DeviceItem) -> Siemens.Engineering.SW.PlcSoftware | None:
    logger.debug(f"Accessing a PlcSoftware from DeviceItem {device_item.Name}")

    software_container: Siemens.Engineering.SW.PlcSoftware = tia.IEngineeringServiceProvider(device_item).GetService[hwf.SoftwareContainer]()
    if not software_container:

        logger.debug(f"No PlcSoftware found for DeviceItem {device_item.Name}")

        return None

    logger.debug(f"Found PlcSoftware for DeviceItem {device_item.Name}")

    return software_container

def find_plc_by_name(project: Siemens.Engineering.Project, name: str) -> Siemens.Engineering.HW.Features.SoftwareContainer:
    logger.debug(f"Searching PlcSoftware by name: {name}")

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

                logger.debug(f"Found PlcSoftware: {plc_software.Name}")

                return plc_software

    logger.debug(f"PlcSoftware Not Found: {name}")

def find_plc_block_by_name(block: Siemens.Engineering.SW.Blocks.PlcBlockComposition, name: str) -> Siemens.Engineering.SW.Blocks:
    logger.debug(f"Searching PlcBlock by name: {name}")

    plc_block: Siemens.Engineering.SW.Blocks = block.Find(name)

    if not plc_block:
        logger.debug(f"PlcBlock Not Found: {name}")

        return None

    logger.debug(f"Found PlcBlock: {plc_block.Name}")

    return plc_block

def find_master_copy_by_name(library: Siemens.Engineering.Library.GlobalLibrary, name: str) -> Siemens.Engineering.Library.MasterCopies.MasterCopy:
    logger.debug(f"Searching MasterCopy {name} in GlobalLibrary {library.Name}")

    system_folder: Siemens.Engineering.Library.MasterCopies.MasterCopySystemFolder = library.MasterCopyFolder
    mastercopies: Siemens.Engineering.Library.MasterCopies.MasterCopyComposition = system_folder.MasterCopies
    master_copy: Siemens.Engineering.Library.MasterCopies.MasterCopy = mastercopies.Find(name)

    if not master_copy:

        logger.debug(f"No MasterCopy found in GlobalLibrary {library.Name}")

    logger.debug(f"Found MasterCopy {master_copy.Name} in GlobalLibrary {library.Name}")

    return master_copy

def connect_to_io_system(itf: Siemens.Engineering.HW.Features.NetworkInterface,
                         subnet: Siemens.Enginerring.HW.Subnet,
                         io_system: Siemens.Engineering.HW.IoSystem,
                         ) -> None:
    logger.info(f"Connecting Subnet {subnet.Name} to IoSystem {io_system.Name}")

    itf.Nodes[0].ConnectToSubnet(subnet)

    logger.debug(f"Subnet {subnet.Name} connected to NetworkInterface Subnets")

    if itf.IoConnectors.Count > 0:
        itf.IoConnectors[0].ConnectToIoSystem(io_system)

        logger.info(f"IoSystem {io_system.Name} connected to NetworkInterface IoConnectors")
    
def set_object_attributes(obj: Siemens.Engineering.IEngineeringObject, **attributes) -> None:
    logger.debug(f"Setting Object Attributes: {obj} with attributes {attributes}")

    for attribute, value in attributes.items():
        obj_attrs: Siemens.Engineering.EngineeringAttributeInfo = obj.GetAttributeInfos()
        for attrib in obj_attrs: # we do a lil bit of iteration
            if attrib.Name == attribute:
                obj.SetAttribute(attribute, value)

                logger.debug(f"{obj} attribute {attrib.Name} set to {value}")

def query_program_blocks_of_device(plc: Siemens.Engineering.SW.PlcSoftware) -> list[Siemens.Engineering.SW.Blocks.PlcBlocks]:
    logger.debug(f"Querying program blocks {plc.Name}...")

    software: Siemens.Engineering.SW.PlcSoftware = plc.Software
    if not isinstance(software, tia.SW.PlcSoftware):

        logger.debug(f"Program blocks {plc.Name} empty.")

        return []

    block: list[Siemens.Engineering.SW.Blocks.PlcBlocks] = software.BlockGroup.Blocks

    logger.debug(f"Found {plc.Name}.BlockGroup.Blocks: {block}")

    return block

def enumerate_master_copies_in_system_folder(master_copy_system_folder: Siemens.Engineering.Library.MasterCopies.MasterCopySystemFolder) -> list[Siemens.Engineering.Library.MasterCopies.MasterCopy]:
    logger.debug(f"Querying MasterCopies in SystemFolder...")

    mastercopies: list[Siemens.Engineering.Library.MasterCopies.MasterCopy] = [master_copy for master_copy in master_copy_system_folder.MasterCopies]

    logger.debug(f"Found MasterCopies: {[copy.Name for copy in mastercopies]}")

    return mastercopies

def enumerate_open_libraries(tia: Siemens.Engineering.TiaPortal) -> list[Siemens.Engineering.Library.GlobalLibrary]:
    logger.debug(f"Querying Open GlobalLibraries...")

    global_libraries: list[Siemens.Engineering.Library.GlobalLibrary] = [library for library in tia.GlobalLibraries]

    logger.debug(f"Found GlobalLibraries: {[lib.Name for lib in global_libraries]}")

    return global_libraries
    
def open_library(portal: Siemens.Engineering.TiaPortal, file_info: FileInfo, is_read_only: bool = True) -> Siemens.Engineering.Library.GlobalLibrary:
    logger.info(f"Opening GlobalLibrary: {file_info} (ReadOnly: {is_read_only})")

    library: Siemens.Engineering.Library.GlobalLibrary = tia.Library.GlobalLibrary
    if is_read_only:
        library = portal.GlobalLibraries.Open(file_info, tia.OpenMode.ReadOnly) # Read access to the library. Data can be read from the library.
    else:
        library = portal.GlobalLibraries.Open(file_info, tia.OpenMode.ReadWrite) # Write access to the library. Data can be written to the library.

    logger.info(f"Successfully opened GlobalLibrary: {library.Name}")

    return library

def compile_block(block: Siemens.Engineering.SW.Blocks.PlcBlock) -> Siemens.Engineering.Compiler.CompilerResult:
    logger.info(f"Compiling PlcBlock {block.Name}...")

    single_compile: Siemens.Engineering.Compiler.ICompilable = block.GetService[tia.Compiler.ICompilable]();
    result: Siemens.Engineering.Compiler.CompilerResult = single_compile.Compile()

    logger.info(f"Compiled PlcBlock {block.Name}")
    logger.debug(f"""Compile PlcBlock {block.Name} Result:
    Messages: ({result.Messages[0]}, {result.Messages[1]}
    State: {result.State}
    WarningCount: {result.WarningCount}
    ErroCount: {result.ErroCount}""")

    return result

def export_block_as_xml(block: Siemens.Engineering.SW.Blocks.PlcBlock,
                        directory: Path,
                        ) -> None:
    logger.info(f"Exporting PlcBlock {block.Name} as XML to {directory.as_posix()}")

    if not directory.exists():
        err = f"Directory does not exist: {directory}"
        logger.error(err)
        raise PPError(err)
    if not directory.is_dir():
        err = f"Path is not a directory: {directory}"
        logger.error(err)
        raise PPError(err)

    file_path: FileInfo = FileInfo(f"{directory.as_posix()}/{block.Name}.xml")
    if file_path.Exists:
        err = f"File already exists: {file_path}"
        logger.error(err)
        raise PPError(err)

    export_options: Siemens.Engineering.ExportOptions = tia.ExportOptions.WithReadOnly | tia.ExportOptions.WithDefaults   

    block.Export(file_path, export_options)

    logger.debug(f"Exported PlcBlock {block.Name}: {file_path}")

    return

def import_xml_block(blocks: Siemens.Engineering.SW.Blocks.PlcBlockComposition,
                     xml: FileInfo,
                     ) -> None:
    blocks.Import(xml, tia.ImportOptions.Override)

    logger.info(f"Imported XML ({xml}) to PlcBlockGroup {blocks}")

    return

def create_single_instance_db(plc: Siemens.Engineering.HW.Features.SoftwareContainer, name: str,
                       number: int, instance_of_name: str) -> Siemens.Engineering.SW.Blocks.InstanceDB:
    logger.debug(f"Creating InstanceDB {{{name}, {number}}} for PlcSoftware {plc.Name}...")

    name = name + "_DB"
    blocks: Siemens.Engineering.SW.Blocks.PlcBlockComposition = plc.BlockGroup.Blocks
    for block in blocks:
        if name == block.Name:
            err = f"The block name '{name}' is invalid. An object with this name or this number already exists."
            logger.error(err)
            raise PPError(err)
    instance_db = blocks.CreateInstanceDB(name, True, number, instance_of_name)

    logger.debug(f"Created InstanceDB {instance_db.Name} with Number {number}")

    return instance_db

def parse(path: str) -> objects.Config:
    """
    Initialize TIA Portal config parser with the path to the configuration file
    Loads and process the JSON configuration file into python classes.

    :param path: String path to the JSON configuration file
    """

    logger.debug(f"Parsing config: {path}")

    config_file_path: Path = Path(path)
    
    if not config_file_path.exists():
        err = f"JSON config file does not exist: {config_file_path}"
        logger.error(err)
        raise ValueError(err)

    if not config_file_path.is_file():
        err = f"JSON config is not a file: {config_file_path}"
        logger.error(err)
        raise ValueError(err)

    with open(config_file_path, 'r') as file:

        logger.debug(f"Opening config: {config_file_path.as_posix()}")

        conf: dict = json.load(file)

    config: objects.Config = objects.start(**conf)

    logger.debug(f"Config has been parsed.")

    return config
