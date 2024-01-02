## PingTool
> Lightweight socket application, built to ping annoying colleagues who won't respond.

![GitHub release](https://img.shields.io/github/v/release/DeadlyFirex/PingTool)
![Python package](https://github.com/DeadlyFirex/PingTool/actions/workflows/pylint.yml/badge.svg)
![wakatime](https://wakatime.com/badge/user/a56c956d-565b-4ddd-a43e-fb7d155c4232/project/e919eb0d-9447-46a2-a32f-107ff8f939c4.svg)
![GitHub License](https://img.shields.io/github/license/DeadlyFirex/PingTool)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/DeadlyFirex/PingTool/main)
![GitHub repo size](https://img.shields.io/github/repo-size/DeadlyFirex/PingTool)
![PyPI - License](https://img.shields.io/pypi/l/PingTool?label=PyPi%20License)
![PyPI - Format](https://img.shields.io/pypi/format/PingTool)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/PingTool)
![PyPI - Version](https://img.shields.io/pypi/v/PingTool)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PingTool)

PingTool is an application with a client / server implementation that allows you to ping other users. \
This project aims to demonstrate modern socket and threading capabilities in a Python format.

## Features
- Lightweight client / server implementation.
- Simple command system.
- Argument parsing.
- Logging system.
- Configurable settings.
- Multithreading server for multiple connections.
- Threaded client for sending and receiving data.
- Easy to use command system.

## Installation
You can install and update the project through PyPi;
```bash
$ pip install PingTool
```
Optionally, you can install and run manually by pulling from the latest 
[release](https://github.com/DeadlyFirex/PingTool/releases/latest)
1. Run the `client` by running `python client.py` 
2. The `server` is executable via `python server.py`
3. Configuration is done via `config.json` and arguments.

## Description
Program makes use of built-in the Python `sockets` library. \
Server accepts commands, by sending and receiving specific commands.

All responses and commands are sent following a static format, `cmd:arg`. \
This also goes for responses, which follow the same format.

Sending an end-line is recommended, but not required. \
Data is sent in `utf-8` encoded bytes.

## Configuration
The server makes use of `config.json` for configuration. \
Furthermore, both client and server make use arguments for runtime configuration.

Make use of `--help` or `-h` to see all available arguments.

## Details
For more information, see the [wiki](https://github.com/DeadlyFirex/PingTool/wiki)

## Dependencies
Credits go to these awesome projects for making this possible!
- [loguru](https://github.com/Delgan/loguru)