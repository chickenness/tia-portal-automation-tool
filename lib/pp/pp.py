from .modules import objects
from pathlib import Path
import json
import os


class Portal:
    def __init__(self, config: objects.Config) -> None:
        self.config = config

        import clr
        clr.AddReference(self.config.dll.as_posix())

        from System.IO import DirectoryInfo, FileInfo
        import Siemens.Engineering as tia
        import Siemens.Engineering.Compiler as comp
        import Siemens.Engineering.HW.Features as hwf

        self.DirectoryInfo = DirectoryInfo
        self.FileInfo = FileInfo
        self.tia = tia
        self.comp = comp
        self.hwf = hwf

    def run(self) -> None:
        # probs make this part run multithreaded since it hangs the gui process
        conf = self.config
        if conf.enable_ui:
            print("Starting TIA with UI")
            TIA = self.tia.TiaPortal(self.tia.TiaPortalMode.WithUserInterface)
        else:
            print("Starting TIA without UI")
            TIA = self.tia.TiaPortal(self.tia.TiaPortalMode.WithoutUserInterface)

        project_path = conf.project.directory.as_posix()
        project_name = conf.project.name

        PROJECT = TIA.Projects.Create(self.DirectoryInfo(project_path), project_name)


        PLC1 = PROJECT.Devices.CreateWithItem(conf.project.devices[0].device, conf.project.devices[0].device_name, 'PLC1')


def parse(path: str) -> Portal | ValueError:
    """
    Initialize TIA Portal config parser with the path to the configuration file
    Loads and process the JSON configuration file into python classes.

    :param path: String path to the JSON configuration file
    """

    config_file_path: Path = Path(path)
    
    if not config_file_path.exists():
        return ValueError(f"JSON config file does not exist: {config_file_path}")

    if not config_file_path.is_file():
        return ValueError(f"JSON config is not a file: {config_file_path}")

    with open(config_file_path, 'r') as file:
        conf: dict = json.load(file)

    config: objects.Config = objects.start(**conf)

    if isinstance(config, ValueError):
        return ValueError(f"Error: {config}")

    return Portal(config)


