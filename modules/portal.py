from __future__ import annotations

from . import logger
import logging
from typing import Any

logger.setup(None, 10)
log = logging.getLogger(__name__)

def execute(SE: Siemens.Engineering, config: dict[Any, Any], settings: dict[str, Any]):
    logging.debug(f"config data: {config}")
    logging.debug(f"settings: {settings}")

    DirectoryInfo = settings['DirectoryInfo']
    FileInfo = settings['FileInfo']

    if settings['enable_ui']:
        TIA = SE.TiaPortal(SE.TiaPortalMode.WithUserInterface)
    else:
        TIA = SE.TiaPortal(SE.TiaPortalMode.WithoutUserInterface)

    current_process = TIA.GetCurrentProcess()

    logging.info(f"Started TIA Portal Openness ({current_process.Id}) {current_process.Mode} at {current_process.AcquisitionTime}")





    logging.info(f"Creating project {config['name']} at \"{config['directory']}\"...")

    existing_project_path: DirectoryInfo = DirectoryInfo(config['directory'].joinpath(config['name']).as_posix())

    logging.info(f"Checking for existing project: {existing_project_path}")

    if existing_project_path.Exists:

        logging.info(f"{config['name']} already exists...")

        if config['overwrite']:

            logging.info(f"Deleting project {config['name']}...")

            existing_project_path.Delete(True)

            logging.info(f"Deleted project {config['name']}")

        else:
            err = f"Failed creating project. Project already exists ({existing_project_path})"
            logging.error(err)
            raise ValueError

    logging.info("Creating project...")

    project_path: DirectoryInfo = DirectoryInfo(config['directory'].as_posix())

    logging.debug(f"Project Path: {project_path}")

    project_composition: Siemens.Engineering.ProjectComposition = TIA.Projects
    project: Siemens.Engineering.Project = project_composition.Create(project_path, config['name'])

    logging.info(f"Created project {config['name']} at {config['directory']}")





    devices: list[Siemens.Engineering.HW.Device] = []
    interfaces: list[Siemens.Engineering.HW.Features.NetworkInterface] = []
    for device_data in config['devices']:
        device_composition: Siemens.Engineering.HW.DeviceComposition = project.Devices
        device: Siemens.Engineering.HW.Device = device_composition.CreateWithItem(device_data['p_typeIdentifier'],
                                                                                  device_data['p_name'],
                                                                                  device_data['p_deviceName']
                                                                                  )

        logging.info(f"Created device: ({device_data['p_deviceName']}, {device_data['p_typeIdentifier']}) on {device.Name}")

        devices.append(device)
        hw_object: Siemens.Engineering.HW.HardwareObject = device.DeviceItems[0]
        for module in device_data['Local modules']:
            logging.info(f"Plugging {module['TypeIdentifier']} on [{module['PositionNumber'] + device_data['slots_required']}]...")

            if hw_object.CanPlugNew(module['TypeIdentifier'], module['Name'], module['PositionNumber'] + device_data['slots_required']):
                hw_object.PlugNew(module['TypeIdentifier'], module['Name'], module['PositionNumber'] + device_data['slots_required'])

                logging.info(f"{module['TypeIdentifier']} PLUGGED on [{module['PositionNumber'] + device_data['slots_required']}]")

                continue

            logging.info(f"{module['TypeIdentifier']} Not PLUGGED on {module['PositionNumber'] + device_data['slots_required']}")

        logging.debug(f"Accessing a DeviceItem Index {1} at Device {device.Name}")

        device_items: Siemens.Engineering.HW.DeviceItem = device.DeviceItems[1].DeviceItems
        for device_item in device_items:
            logging.debug(f"Accessing a NetworkInterface at DeviceItem {device_item.Name}")

            network_service: Siemens.Engineering.HW.Features.NetworkInterface = SE.IEngineeringServiceProvider(device_item).GetService[SE.HW.Features.NetworkInterface]()
            if not network_service:

                logging.debug(f"No NetworkInterface found for DeviceItem {device_item.Name}")

            logging.debug(f"Found NetworkInterface for DeviceItem {device_item.Name}")

            if type(network_service) is SE.HW.Features.NetworkInterface:
                node: Siemens.Engineeering.HW.Node = network_service.Nodes[0]
                node.SetAttribute("Address", device_data['network_address'])

                logging.info(f"Added a network address: {device_data['network_address']}")

                interfaces.append(network_service)

        for device_item in device.DeviceItems:

            logging.debug(f"Accessing a PlcSoftware from DeviceItem {device_item.Name}")

            software_container: Siemens.Engineering.HW.Features.SoftwareContainer = SE.IEngineeringServiceProvider(device_item).GetService[SE.HW.Features.SoftwareContainer]()
            if not software_container:

                logging.debug(f"No PlcSoftware found for DeviceItem {device_item.Name}")

            logging.debug(f"Found PlcSoftware for DeviceItem {device_item.Name}")

            if not software_container:
                continue
            software_base: Siemens.Engineering.HW.Software = software_container.Software
            if not isinstance(software_base, SE.SW.PlcSoftware):
                continue

            for tag_table_data in device_data['PLC tags']:
                logging.info(f"Creating Tag Table: {tag_table_data['Name']} ({software_base.Name} Software)")

                tag_table: Siemens.Engineering.SW.Tags.PlcTagTable = software_base.TagTableGroup.TagTables.Create(tag_table_data['Name'])

                logging.info(f"Created Tag Table: {tag_table_data['Name']} ({software_base.Name} Software)")
                logging.debug(f"PLC Tag Table: {tag_table.Name}")

                if not isinstance(tag_table, SE.SW.Tags.PlcTagTable):
                    continue

                for tag_data in tag_table_data['Tags']:
                    logging.info(f"Creating Tag: {tag_data['Name']} ({tag_table.Name} Table@0x{tag_data['LogicalAddress']} Address)")

                    tag_table.Tags.Create(tag_data['Name'], tag_data['DataTypeName'], tag_data['LogicalAddress'])

                    logging.info(f"Created Tag: {tag_data['Name']} ({tag_table.Name} Table@0x{tag_data['LogicalAddress']} Address)")
