import sys,copy,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'image-context-v4/ratings'))
from corner_transport import validate_corners
class Transport(unittest.TestCase):
 def test_geometry_and_raw_preserved(self):
  d={'completed':True,'pictures':[{'box':[.1,.2,.9,.8],'category':'PL','note':''}]};old=copy.deepcopy(d);z=validate_corners(d);self.assertEqual(d,old);self.assertAlmostEqual(z['pictures'][0]['box'][2],.8);self.assertAlmostEqual(z['pictures'][0]['box'][3],.6)
 def test_edge(self):self.assertEqual(validate_corners({'completed':True,'pictures':[{'box':[0,0,1,1],'category':'OT','note':''}]})['pictures'][0]['box'],[0,0,1,1])
 def test_invalid_not_clipped(self):
  with self.assertRaises(ValueError):validate_corners({'completed':True,'pictures':[{'box':[.5,0,.2,1],'category':'OT','note':''}]})
 def test_empty_complete(self):self.assertEqual(validate_corners({'completed':True,'pictures':[]}),{'completed':True,'pictures':[]})
if __name__=='__main__':unittest.main()
