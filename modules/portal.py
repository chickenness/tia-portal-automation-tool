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
