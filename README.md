# TIA Portal Automation Tool

## Building

### Clone repository:

```
git clone https://github.com/TitusTech/tia-portal-automation-tool.git
```

### Install requirements:

```
cd tia-portal-automation-tool
pip install -r requirements.txt
```

### Compile (Optional)

```
pyinstaller --noconfirm --onefile --windowed --name "tia-portal-automation-tool" "main.py"
cp -r res dist
```

And done.

To run, simply `python main.py`.

## Caveats

The JSON configuration allows adding of instances for every plc blocks.
However, when the source of the plc block points to a mastercopy or plc, it won't create any instances for that plc block but it will still create the nested blocks (labeled as instances).
