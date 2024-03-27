from fastapi import FastAPI, UploadFile, File
from h2.config import H2Configuration
from h2.connection import H2Connection
from h2.events import RequestReceived, DataReceived
import os
import asyncio

app = FastAPI()


async def handle_h2_connection(reader, writer):
    config = H2Configuration(client_side=False)
    conn = H2Connection(config=config)
    conn.initiate_connection()
    await writer.drain()

    while True:
        try:
            data = await reader.read(65536)
            events = conn.receive_data(data)
            for event in events:
                if isinstance(event, RequestReceived):
                    stream_id = event.stream_id
                    headers = [(name.decode("utf-8"), value.decode("utf-8")) for name, value in event.headers]
                    if headers[0][0] == "content-type" and headers[0][1] == "image/png":
                        file_data = await reader.read()
                        with open("received_images/" + headers[1][1], "wb") as file:
                            file.write(file_data)
                            await writer.drain()
                        await writer.drain()
                        response_headers = (
                            (b":status", b"200"),
                            (b"content-type", b"application/json"),
                        )
                        conn.send_headers(stream_id, response_headers)
                        conn.send_data(stream_id, b'{"message": "Image received successfully"}', end_stream=True)
                        await writer.drain()
                elif isinstance(event, DataReceived):
                    pass

            await writer.write(conn.data_to_send())
            await writer.drain()
        except Exception as e:
            print("Error:", str(e))
            break


@app.post("/receive_images/")
async def receive_images(file: UploadFile = File(...)):
    try:
        file_data = await file.read()
        return {"message": f"Image {file.filename} received successfully."}
    except Exception as e:
        return {"message": f"Error receiving and processing images: {str(e)}"}


async def main():
    server = await asyncio.start_server(handle_h2_connection, host="127.0.0.1", port=8004)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
