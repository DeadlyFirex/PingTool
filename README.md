[![Python package](https://github.com/DeadlyFirex/OrderServer/actions/workflows/pylint.yml/badge.svg)](https://github.com/DeadlyFirex/PingTool/actions/workflows/pylint.yml)
[![wakatime](https://wakatime.com/badge/user/a56c956d-565b-4ddd-a43e-fb7d155c4232/project/e919eb0d-9447-46a2-a32f-107ff8f939c4.svg)](https://wakatime.com/badge/user/a56c956d-565b-4ddd-a43e-fb7d155c4232/project/e919eb0d-9447-46a2-a32f-107ff8f939c4)
## PingTool
Small application written in Python, socket-based. to ping annoying colleague's who won't respond.\
Made to refresh Python knowledge, and for anyone who has annoying colleague's who won't respond to your messages.

## Usage
Program uses basic Python `sockets`.\
Works by sending and receiving specific commands.

All responses and commands are sent following a static format, `cmd:arg`, 
for example,`Name:Deadly` to verify user on connection, 
command with required argument`Exit:?` to disconnect, argument is not parsed, but required to fit format.

This also goes for responses, whomst follow the same format.\
Sending an end-line is recommended, but not required.\
Send data in bytes, encode using UTF-8, soon configurable.

## Commandlist
#### Manual
- Name <sub>(used to confirm name)</sub>
- Fetch <sub>(fetch all users)</sub>
- Ping <sub>(ping a different user)</sub>
- Exit <sub>(disconnect gracefully)</sub>
#### Automatic
- S-Ping <sub>(confirms sent ping)</sub>
- X-Ping <sub>(sent to pinged user)</sub>
#### Responses
- Error <sub>(indicates bad request)</sub>
- Connected <sub>(indicates successful connection)</sub>
- Bye <sub>(indicates successful disconnect)</sub>

## Function
1. Connect to the server.
2. Login to the server using the `Name` command.
3. You can now use any command.
4. Disconnect by using `Exit`.

## Technical Details
Server uses the built-in `sockets` to create a IPv4 socket, on the TCP protocol.

## Libraries
- [loguru](https://github.com/Delgan/loguru)