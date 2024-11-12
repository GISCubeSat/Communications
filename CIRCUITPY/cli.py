import asyncio

async def ainput(string: str) -> str:
    await asyncio.to_thread(sys.stdout.write, f'{string} ')
    return await asyncio.to_thread(sys.stdin.readline)

async def monitor_cmd():
    line = await ainput('Is this your line? ')
    print(line)