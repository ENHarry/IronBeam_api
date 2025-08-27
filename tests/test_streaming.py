import unittest
from unittest.mock import patch, Mock, AsyncMock
from ironbeam.streaming import IronBeamStream

class TestIronBeamStream(unittest.TestCase):

    @patch('websockets.connect', new_callable=AsyncMock)
    def test_connect(self, mock_connect):
        async def run_test():
            stream = IronBeamStream(token="test_token")
            # Mock the internal _create_stream_id to avoid a real API call
            stream._create_stream_id = AsyncMock(return_value="mock_stream_id")
            
            await stream.connect()
            mock_connect.assert_called_with("wss://demo.ironbeamapi.com/v2/stream/mock_stream_id?token=test_token")

        import asyncio
        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
