import new_protocol_receive

import asyncio
# from cli import monitor_cmd
# t1 = asyncio.create_task(new_protocol_receive.main())
# t2 = asyncio.create_task(monitor_cmd())

async def main():
    # await asyncio.gather(
    #     t2,
    #     t1
    # )
    await new_protocol_receive.main()

if __name__ == "__main__":
    asyncio.run(main())