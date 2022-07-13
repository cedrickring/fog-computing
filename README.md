# Fog Computing Prototyping Assignment
This repository contains code for the Fog Computing Prototyping Assignment from the summer semester 2022 at TU Berlin.

## Contents
1. [Demo](#demo)
1. [Report](#report)
1. [Structure](#structure)
1. [Requirements](#requirements)
1. [Install & Run](#install--run)
1. [License](#license)

## Demo
You can find a short demo video [here](https://tubcloud.tu-berlin.de/s/KkszRBrnz9QFTc6).

## Report
The report can be found [here](report/report.pdf).

## Structure
- `cloud-node` - source code of the cloud node
- `data` - the weather / trainning data
- `deployment` - cloud provisioning code
- `fog-node` - source code of fog node
- `models` - pretrained prediction models
- `report` - all report files
- `util` - code used by both cloud and fog node

## Requirements
- Python 3.9+

## Install & Run

Installation:
```bash
git clone git@github.com:cedrickring/fog-computing.git
cd fog-computing

# Optional: if you want to create a venv first run:
python3 -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
```

Start fog node:
```bash
cd fog-node
# add parent path so util/ is accessible
PYTHONPATH=../ python main.py <node-name> [host]
```
if not specified, `[host]` will default to `localhost`.

Start cloud node:
```bash
cd cloud-node
# add parent path so util/ is accessible
PYTHONPATH=../ python main.py
```

## License

See [LICENSE](LICENSE) for more.
