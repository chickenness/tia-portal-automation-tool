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
