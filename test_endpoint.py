import httpx
import asyncio
request = "lên báo giá bản vẽ này https://heli.com.vn/wp-content/uploads/2024/08/ban-ve-van-phong-lam-viec-voi-day-du-cac-khong-gian-chuc-nang.jpg"
async def get_stream():
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", "http://127.0.0.1:8000/api/v1/chatbot/stream_chat", json = {"request":request,"session_id":"3"}) as response:
            async for line in response.aiter_lines():
                if "```json```" in line:
                    continue
                print("Received:", line)

asyncio.run(get_stream())
