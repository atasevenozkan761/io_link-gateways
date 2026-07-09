import sys
sys.path.insert(0, '/home/pmf04/iol-hat/examples/python')
import iolhat
import struct
import asyncio
import logging

from asyncua import Server, ua

PORT = 1
OPCUA_ENDPOINT = "opc.tcp://0.0.0.0:4840/gateway/server/"

logging.basicConfig(level=logging.WARNING)

def read_kg6000():
    data = iolhat.pd(PORT, 0, 2, None)
    raw = struct.unpack("!H", data)[0]
    switching_state = bool(raw & 0x01)
    measurement = (raw >> 1) & 0x7FFF
    return switching_state, measurement

async def main():
    iolhat.power(PORT, 1)
    await asyncio.sleep(1)

    server = Server()
    await server.init()
    server.set_endpoint(OPCUA_ENDPOINT)
    server.set_server_name("IOL Gateway OPC UA Server")

    # Kendi namespace'imizi tanımla
    uri = "http://tu-berlin.de/iwf/iolink-gateway"
    idx = await server.register_namespace(uri)

    # Nesne modeli: Objects/KG6000Sensor/SwitchingState, Measurement
    objects = server.get_objects_node()
    sensor_obj = await objects.add_object(idx, "KG6000Sensor")

    switching_state_var = await sensor_obj.add_variable(idx, "SwitchingState", False)
    measurement_var = await sensor_obj.add_variable(idx, "Measurement", 0)

    # Değişkenleri yazılabilir yapmıyoruz — sadece okunur (sensör verisi)
    await switching_state_var.set_writable(False)
    await measurement_var.set_writable(False)

    print(f"OPC UA server başladı -> {OPCUA_ENDPOINT}")
    print(f"Namespace index: {idx}")

    async with server:
        while True:
            state, value = read_kg6000()
            await switching_state_var.write_value(state)
            await measurement_var.write_value(value)
            print(f"OPC UA güncellendi: SwitchingState={state}  Measurement={value}")
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
