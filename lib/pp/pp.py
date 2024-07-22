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

def add_devices(project: Siemens.Engineering.Project, devices: list[objects.Device]) -> list[Siemens.Engineering.HW.DeviceImpl]:
    hardware: list[Siemens.Engineering.HW.DeviceImpl] = []
    for dev in devices:
        hw = project.Devices.CreateWithItem(dev.DeviceItemTypeId, dev.DeviceTypeId, dev.DeviceItemName)
        hardware.append(hw)
        add_device_items(project, hw, dev.items, dev.slots_required)

    return hardware

def add_device_items(
        project: Siemens.Engineering.Project,
        device: Siemens.Engineering.HW.DeviceImpl,
        device_items: list[objects.DeviceItem],
        slots_required: int
    ):
    for item in device_items:
        if (device.DeviceItems[0].CanPlugNew(item.TypeIdentifier, item.Name, item.PositionNumber + slots_required)):
            device.DeviceItems[0].PlugNew(item.TypeIdentifier, item.Name, item.PositionNumber + slots_required)
            print(f"{item.TypeIdentifier} PLUGGED on [{item.PositionNumber + slots_required}].")
        else:
            print(f"{item.TypeIdentifier} Not PLUGGED on {item.PositionNumber + slots_required}")



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

