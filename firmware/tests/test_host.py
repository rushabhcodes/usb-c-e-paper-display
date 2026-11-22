import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"host"))
from epaper import packet, ReplyReader, convert_image, FRAME_SIZE
from PIL import Image

class ProtocolTests(unittest.TestCase):
    def test_fragmented_reply_and_noise(self):
        data = b"noise" + packet(0x82, 123, json.dumps({"mode":"partial"}).encode(), magic=b"EPA1")
        reader = ReplyReader(); replies=[]
        for c in data: replies.extend(reader.feed(bytes([c])))
        self.assertEqual(replies, [(123, 0x82, 0, {"mode":"partial"})])

    def test_corrupt_reply_then_recovery(self):
        good=packet(0x81, 5, b'{}', magic=b"EPA1")
        bad=bytearray(good);bad[-1]^=1
        self.assertEqual(ReplyReader().feed(bad+good),[(5,0x81,0,{})])

    def test_pixel_polarity_and_bit_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"test.png"
            im=Image.new("L",(800,480),255);im.putpixel((0,0),0);im.putpixel((799,479),0);im.save(path)
            _,data=convert_image(path)
            self.assertEqual(len(data),FRAME_SIZE)
            self.assertEqual(data[0],0x7f);self.assertEqual(data[-1],0xfe)

    def test_alpha_composited_white_and_contain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"transparent.png"
            Image.new("RGBA",(20,20),(0,0,0,0)).save(path)
            _,data=convert_image(path)
            self.assertEqual(data,b'\xff'*FRAME_SIZE)

if __name__ == '__main__': unittest.main()
