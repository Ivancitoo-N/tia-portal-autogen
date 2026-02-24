import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import io
import zipfile

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestTIAApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.analyze_image')
    def test_process_route(self, mock_analyze):
        """
        Test the /process route with a mocked vision service.
        """
        # Mock Response
        mock_analyze.return_value = {
            "tags": [
                {"Name": "StartBtn", "Path": "Default tag table", "DataType": "Bool", "LogicalAddress": "%I0.0", "Comment": "Start"},
                {"Name": "Motor", "Path": "Default tag table", "DataType": "Bool", "LogicalAddress": "%Q0.0", "Comment": "Motor O/P"}
            ],
            "scl_code": "REGION Control\n\t#Motor := #StartBtn;\nEND_REGION",
            "block_name": "MotorControl"
        }

        # create a dummy image file
        data = {
            'image': (io.BytesIO(b"fake image data"), 'test.jpg'),
            'api_key': 'fake-api-key'
        }

        response = self.app.post('/process', data=data, content_type='multipart/form-data')

        if response.status_code != 200:
            print(f"Server Error: {response.data.decode('utf-8')}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/zip')

        # Verify ZIP content
        with zipfile.ZipFile(io.BytesIO(response.data)) as z:
            self.assertIn('PLC_Tags.xlsx', z.namelist())
            self.assertIn('Block.xml', z.namelist())
            
            # Check XML Content
            xml_content = z.read('Block.xml').decode('utf-8')
            self.assertIn('MotorControl', xml_content)
            self.assertIn('REGION Control', xml_content)

if __name__ == '__main__':
    unittest.main()
