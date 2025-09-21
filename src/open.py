from pathlib import Path
from tomlkit import parse #type: ignore
from .util import execute, system_messages, send, create_empty_toml
from . import status as status_module
import asyncio

# TOMLファイルの読み込み（存在しない場合は空の table を返す）
def load_servers():
    servers_file = Path('/mnt/game/default.toml')
    if servers_file.exists():
        with servers_file.open('r', encoding='utf-8') as f:
            return parse(f.read())
    else:  
        create_empty_toml(servers_file)
    return {}


async def run_shell(message, server_dir):
    run_sh = Path(f'/mnt/game/server/{server_dir}/run.sh')
    if run_sh.exists():
        backend_name = server_dir
        execute(f'tmux send-keys -t {backend_name} "source {run_sh}" ENTER')
        await send.message('Opening with run.sh', message)
        return True  # run.shで処理完了
    return False  # run.shが存在しない

async def server(message, server_name, status_val):
    servers = load_servers()
    backend_name = server_name + '_sv'
    java_version = servers[server_name].get('java_version', '')
    if status_val == 'running':
        await send.message(f'{server_name} is already running!', message)
        return

    execute(f'tmux new -s {backend_name} -d')
    execute(f'tmux send-keys -t {backend_name} "cd /mnt/game/server/{backend_name}" ENTER')
    used_run_sh = await run_shell(message, backend_name)

    if not used_run_sh:
        await send.message('Opening with jarFile', message)
        if server_name != 'proxy':
            execute(f'tmux send-keys -t {backend_name} "java{java_version} -jar *.jar nogui" ENTER')
            execute(f'tmux send-keys -t {backend_name} "save-off" ENTER')
            await asyncio.sleep(2)
            output = status_module.tmux_output(backend_name)
            if "Automatic saving is now disabled" in output:
                await send.message(f'save-off was successfully executed for {server_name}', message)
        else:
            execute(f'tmux send-keys -t {backend_name} "java{java_version} -jar *.jar" ENTER')

    await send.message(f'{server_name} has been started!', message)

async def all(message):
    servers_file = Path('/mnt/game/default.toml')
    if not servers_file.exists():
        await send.message('default.toml not found. Please add servers to it.', message)
        return

    servers = load_servers()
    if not servers:
        await send.message('No servers found in default.toml.', message)
        return

    for server_name in servers:
        backend_name = server_name + '_sv'
        status_val = status_module.read(backend_name) 
        java_version = servers[server_name].get('java_version', '')
        if status_val == 'running':
            await send.message(f'{server_name} is already running!', message)
        else:
            execute(f'tmux new -s {backend_name} -d')
            execute(f'tmux send-keys -t {backend_name} "cd /mnt/game/server/{backend_name}" ENTER')
            used_run_sh = await run_shell(message, backend_name)
            if not used_run_sh:
                await send.message('Opening with jarFile', message)
                if backend_name != 'proxy_sv':
                    if server_name in servers:
                        execute(f'tmux send-keys -t {backend_name} "java{java_version} -jar *.jar nogui" ENTER')
                        execute(f'tmux send-keys -t {backend_name} "save-off" ENTER')
                    else:
                        execute(f'tmux send-keys -t {backend_name} "java -jar *.jar nogui" ENTER')
                        execute(f'tmux send-keys -t {backend_name} "save-off" ENTER')
                    await asyncio.sleep(2)
                    output = status_module.tmux_output(backend_name)
                    if "Automatic saving is now disabled" in output:
                        await send.message(f'{server_name} has been started!', message)
                else:
                    execute(f'tmux send-keys -t {backend_name} "java{java_version} -jar *.jar" ENTER')

    await send.message('All servers from default.toml have been started.', message)

async def main(command, message):
    if len(command) > 1 and command[1] == 'all':
        await all(message)
    elif len(command) > 1:
        server_name = command[1]
        backend_name = server_name + '_sv'
        status_val = status_module.read(backend_name)
        await server(message, server_name, status_val)
    else:
        await send.message(system_messages.get("Invalid command format for 'open'.", message))