from typing import Any
import json
from gmqtt import Client as MQTTClient
from fastapi_mqtt import FastMQTT, MQTTConfig
from models import AitiaoPasswd, AijiuStartEnd, AijiuRemainingTime, AitiaoLife, AijiuTemperature, CatalystTemperature, FanRpm, db
mqtt_config = MQTTConfig()
mqtt_data_subscribe = FastMQTT(config=mqtt_config)

@mqtt_data_subscribe.subscribe("艾条密码/+")
async def 艾条密码(client: MQTTClient, topic: str, payload: bytes, qos: int, properties: Any):
    client_id = topic.split('/')[1]
    密码 = json.loads(payload.decode())['密码']
    # TODO: verify passwd; send 艾条有效秒数增加/设置艾条有效秒数
    print(client_id, json.loads(payload.decode()))

@mqtt_data_subscribe.subscribe("灸疗开始/+")
async def 灸疗开始(client: MQTTClient, topic: str, payload: bytes, qos: int, properties: Any):
    client_id = topic.split('/')[1]
    payload = json.loads(payload.decode())
    定时, timestamp = payload['定时'], payload['ts']
    async with db.create_session() as s:
        s.add(AijiuStartEnd(client_id=client_id, timestamp=timestamp, start_end=True))
        s.add(AijiuRemainingTime(client_id=client_id, timestamp=timestamp, remaining_time=定时))

@mqtt_data_subscribe.subscribe("灸疗结束/+")
async def 灸疗结束(client: MQTTClient, topic: str, payload: bytes, qos: int, properties: Any):
    client_id = topic.split('/')[1]
    payload = json.loads(payload.decode())
    timestamp = payload['ts']
    async with db.create_session() as s:
        s.add(AijiuStartEnd(client_id=client_id, timestamp=timestamp, start_end=False))
        s.add(AijiuRemainingTime(client_id=client_id, timestamp=timestamp, remaining_time=0))

@mqtt_data_subscribe.subscribe("灸疗剩余时间/+")
async def 灸疗剩余时间(client: MQTTClient, topic: str, payload: bytes, qos: int, properties: Any):
    client_id = topic.split('/')[1]
    payload = json.loads(payload.decode())
    剩余时间, timestamp = payload['剩余时间'], payload['ts']
    async with db.create_session() as s:
        s.add(AijiuRemainingTime(client_id=client_id, timestamp=timestamp, remaining_time=剩余时间))

@mqtt_data_subscribe.subscribe("灸疗温度/+")
async def 灸疗温度(client: MQTTClient, topic: str, payload: bytes, qos: int, properties: Any):
    client_id = topic.split('/')[1]
    payload = json.loads(payload.decode())
    温度, timestamp = payload['温度'], payload['ts']
    async with db.create_session() as s:
        s.add(AijiuTemperature(client_id=client_id, timestamp=timestamp, temperature=温度))

@mqtt_data_subscribe.subscribe("三元催化温度/+")
async def 三元催化温度(client: MQTTClient, topic: str, payload: bytes, qos: int, properties: Any):
    client_id = topic.split('/')[1]
    payload = json.loads(payload.decode())
    温度, timestamp = payload['温度'], payload['ts']
    async with db.create_session() as s:
        s.add(CatalystTemperature(client_id=client_id, timestamp=timestamp, temperature=温度))

@mqtt_data_subscribe.subscribe("散热风机转速/+")
async def 散热风机转速(client: MQTTClient, topic: str, payload: bytes, qos: int, properties: Any):
    client_id = topic.split('/')[1]
    payload = json.loads(payload.decode())
    转速, timestamp = payload['转速'], payload['ts']
    async with db.create_session() as s:
        s.add(FanRpm(client_id=client_id, timestamp=timestamp, rpm=转速))

