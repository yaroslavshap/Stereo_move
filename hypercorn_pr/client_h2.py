import os
import h2.connection
import h2.events
import asyncio
from h2.connection import H2Connection
import time


async def send_files():
    folder = "/Users/aroslavsapoval/myProjects/data/images"
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    total_time = 0

    conn = await open_connection("127.0.0.1", 8004)
    try:
        stream_id = conn.get_next_available_stream_id()
        conn.send_headers(stream_id, [
            (b":method", b"POST"),
            (b":scheme", b"https"),
            (b":path", b"/receive_images/"),
            (b":authority", b"127.0.0.1:8004"),
            (b"content-type", b"image/png"),  # assuming images are PNGs
        ], end_stream=False)

        for file_name in files:
            file_path = os.path.join(folder, file_name)
            with open(file_path, "rb") as file:
                file_data = file.read()
                start_time = time.time()
                while file_data:
                    chunk = file_data[:conn.local_flow_control_window(stream_id)]
                    conn.send_data(stream_id, chunk, end_stream=False)
                    file_data = file_data[len(chunk):]
                    await conn.flush()
                end_time = time.time()
                transfer_time = end_time - start_time
                total_time += transfer_time
                print(f"Transfer time for {file_name}: {transfer_time} seconds")

        print(f"Total time: {total_time} seconds")
    finally:
        await conn.close_connection()


async def open_connection(host, port):
    reader, writer = await asyncio.open_connection(host, port, ssl=False)
    config = h2.config.H2Configuration(client_side=True)
    connection = h2.connection.H2Connection(config=config)
    connection.initiate_connection()
    writer.write(connection.data_to_send())
    await writer.drain()

    return connection


asyncio.run(send_files())
