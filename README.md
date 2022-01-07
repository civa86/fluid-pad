# Fluid Pad

FluidSynth + Novation Launchpad MK1

## Requirements

- Python ^3.8
- Poetry ^1.1.6

## Setup

```bash
poetry install
```
## Development

```bash
poetry run develop
```

# TODO:
- bottone panic per reset all
- porta launchpad con ricerca di sottostringa...sul rasp sembra essere Launchpad:Launchpad MIDI 1 20:0
- script autoinstallante con virtualenv etc...
- service per partenza al boot
  - https://domoticproject.com/creating-raspberry-pi-service/
  - https://blog.markvincze.com/download-artifacts-from-a-latest-github-release-in-sh-and-powershell/

## Raspberry

TODO: generate short link https://gist.github.com/dikiaap/01f5e2ba3c738012aef0a8f524a6e207

```bash
sudo apt install git fluidsynth python3-pip python3-wxgtk4.0
sudo pip3 install oyaml mido python-rtmidi
# Do we need it?
# sudo pip3 install RPLCD RPi.GPIO


```
