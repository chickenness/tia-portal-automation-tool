# TIA Portal Automation Tool

## Installation

1. Clone repository:

```
git clone https://github.com/chickenness/tia-portal-automation-tool.git
```

2. Change directory:

```
cd tia-portal-automation-tool
```

3. Install requirements:

```
pip install -r requirements.txt
```

And done.

To run, simply `python main.py`.

## TODO

- [X] Raise Exceptions instead of passing error values
- [ ] Add more keys
  - [X] PLC Tags
  - [X] Network addresses
  - [X] Program Blocks
    - [ ] Instances
      - [x] Compile PlcBlock
      - [ ] Export PlcBlock as XML
        - [ ] Export Path as FileInfo
        - [ ] Export Options as Siemens.Engineering.ExportOptions
      - [ ] Add Function Blocks to Organization Block (PlcBlock) thru XML
      - [ ] Import PlcBlock as XML
        - [ ] Import Path as FileInfo
        - [ ] Import Options as Siemens.Engineering.ImportOptions
    - [X] Global library path
    - [X] Master copies
      - [ ] Types
        - [X] PlcBlock
          - [X] PlcBlock Destination
          - [X] Master Copy Source
        - [ ] Device
          - [ ] Master Copy Source
        - [ ] DeviceItem
          - [ ] Device Destination
          - [ ] Master Copy Source
        - [ ] Subnet
          - [ ] Master Copy Source
        - [ ] DeviceGroup
          - [ ] Master Copy Source
- [ ] Fix Contract Reference DLL
- [ ] GUI
  - ~~[X] Proof-of-Concept~~
  - [ ] Showing the json configs
  - ~~[X] wx.StaticBox~~
  - ~~[X] wx.TreeCtrl~~
  - ~~[ ] wx.StyledTextCtrl_2~~
  - ~~[ ] Stopping the portal~~
- ~~[ ] Multithread? (since the gui hangs when tia portal runs)~~
