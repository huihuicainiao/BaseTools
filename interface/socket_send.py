#!/usr/bin/python3
# 主要功能：创建1个基本的websocket server, 符合asyncio 开发要求
import asyncio
import websockets
import json
import websockets_routes

# 初始化一个router对象
router = websockets_routes.Router()


@router.route("/algorithm")
async def handler(websocket):
    while True:
        reply = {
            "uid": 5,  # uuid
            "lon": 108.825736,  # 经度，random.random()
            "lat": 34.2127641,  # 纬度
            "altitude": 1.0,  # 海拔高度
            "yaw": 1.0,  # 偏航角
            "pitch": 30.0,  # 俯仰角
            "roll": 1.0,  # 翻滚角
            "pod_yaw": 1.0,  # 相机偏航角
            "pod_pitch": 30.0,  # 相机俯仰角
            "pod_roll": 1.0,  # 相机翻滚角
            "alt_height": 1.0,  # 相对起飞点的高度
            "speed": 1.0,  # 飞行速度
            }
        print(reply)
        await websocket.send(json.dumps(reply))
        await asyncio.sleep(1)


async def main():
    async with websockets.serve(handler, "192.168.200.113", 3008):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

