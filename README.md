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

## Caveats

The JSON configuration allows adding of instances for every plc blocks.
However, when the source of the plc block points to a mastercopy or plc, it won't create any instances for that plc block but it will still create the nested blocks (labeled as instances).
