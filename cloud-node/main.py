import asyncio
import logging

import zmq

from message_handler import MessageHandler
from prediction_histories import PredictionHistories
from util.log import get_logger
from util.message_socket import MessageSocket

logger = get_logger(__name__)

model_path = "../models/random_forest.sav"
socket = MessageSocket(socket_type=zmq.ROUTER)
prediction_histories = PredictionHistories()
message_handler = MessageHandler(model_path=model_path, message_socket=socket, prediction_histories=prediction_histories)


async def main():
    port = 5555
    socket.bind(port=5555)
    logger.info(f'Listening on port: {port}')
    await message_handler.listen()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Shutting down...')
        socket.shutdown()
