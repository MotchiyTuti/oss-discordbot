from pathlib import Path
from tomlkit import table, dumps #type: ignore
import subprocess
import tomllib
import random
import os


def execute(command):
    # シェルコマンドを実行
    subprocess.run(command, shell=True, check=True)


def load_system_messages():
    try:
        message_toml = tomllib.load("message.toml")
        return message_toml.get("system", {})
    except Exception:
        return {}
    
system_messages = load_system_messages()


def get_permission(member):
    roles_order = ['admin', 'mod', 'staff', 'everyone']
    member_roles = {role.name for role in getattr(member, 'roles', [])}
    for role in roles_order:
        if role in member_roles:
            return role
    return 'everyone'


def hasPermission(member, required_role):
    roles_order = ['everyone', 'staff', 'mod', 'admin']
    member_role = get_permission(member)
    try:
        member_idx = roles_order.index(member_role)
        required_idx = roles_order.index(required_role)
        return member_idx >= required_idx
    except ValueError:
        return False


class send:
    async def message(content, msg):
        print(content)
        if msg is None:
            return
        await msg.channel.send(content)
        


def select_option(items):
    options = [x for x in items if x.startswith('--')]
    args = [x for x in items if not x.startswith('--')]
    return options, args


def random_path():
    chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    while True:
        dirname = ''.join(random.choices(chars, k=8))
        full_path = os.path.join('output', dirname)
        if not os.path.exists(full_path):
            return dirname


def create_empty_toml(path: Path):
    """
    指定されたパスに空のTOMLファイルを作成or上書きする。
    """
    empty_data = table()
    with path.open('w', encoding='utf-8') as f:
        f.write(dumps(empty_data))