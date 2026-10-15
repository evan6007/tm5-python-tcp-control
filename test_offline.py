"""Offline tests: python -m unittest -v test_offline. No physical robot connection."""
import struct
import unittest
from unittest.mock import patch
import tm_tcp as tm


class FakeSocket:
    def __init__(self, data=b""):
        self.data = data
        self.sent = []

    def settimeout(self, value):
        pass

    def recv(self, count):
        part, self.data = self.data[:min(count, 2)], self.data[min(count, 2):]
        return part

    def sendall(self, data):
        self.sent.append(data)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class Tests(unittest.TestCase):
    def test_known_query_and_fragmented_response(self):
        self.assertEqual(tm.packet('TMSTA', '00'), b'$TMSTA,2,00,*41\r\n')
        s = FakeSocket(b'$TMSTA,15,00,true,Listen1,*79\r\n')
        self.assertEqual(tm.receive(s), (b'$TMSTA', b'00,true,Listen1'))

    def test_corrupt_checksum_and_disconnect(self):
        for raw in (b'$TMSTA,15,00,true,Listen1,*00\r\n', b'$TMSTA,15,00'):
            with self.assertRaises((ValueError, ConnectionError)):
                tm.receive(FakeSocket(raw))

    def test_state_decode_and_error(self):
        def field(name, value):
            return struct.pack('<H',len(name)) + name.encode() + struct.pack('<H',len(value)) + value
        joints = [1, 2, 3, 4, 5, 6]
        prefix = b'0,1,' + field('Robot_Link', b'\x01')
        suffix = field('Joint_Angle', struct.pack('<6f', *joints))
        self.assertEqual(tm.decode_state(prefix + field('Robot_Error', b'\x00') + suffix), joints)
        with self.assertRaises(RuntimeError):
            tm.decode_state(prefix + field('Robot_Error', b'\x01') + suffix)

    def test_invalid_targets(self):
        for target in ([0]*5, [0]*7, [float('nan')]*6, [float('inf')]*6):
            with self.assertRaises(ValueError):
                tm.validate_target([0]*6, target)

    def test_zero_delta_no_motion(self):
        with patch.object(tm, 'read_joints', return_value=[0]*6), patch('builtins.input', return_value=''), patch.object(tm.socket, 'create_connection') as connect:
            tm.move_joint('unused', 6, 0)
            connect.assert_not_called()

    def test_one_motion_and_readback(self):
        s = FakeSocket(tm.packet('TMSTA','00,true,Listen1') + tm.packet('TMSCT','301,OK'))
        start = [62,23,-137,87,14,-25]
        goal = [62,23,-137,87,14,-15]
        with patch.object(tm, 'read_joints', side_effect=[start,start,start,goal,goal,goal]), patch('builtins.input', side_effect=AssertionError('No second confirmation allowed')), patch.object(tm.socket, 'create_connection', return_value=s), patch.object(tm.time, 'sleep'):
            tm.move_joint('unused', 6, 10)
        self.assertEqual(len(s.sent), 2)
        expected = f'PTP("JPP",62.000000,23.000000,-137.000000,87.000000,14.000000,-15.000000,{tm.SPEED_PERCENT},1000,0,false)'
        self.assertIn(expected.encode('ascii'), s.sent[1])

    def test_missing_ack_never_retries(self):
        s = FakeSocket(tm.packet('TMSTA','00,true,Listen1'))
        with patch.object(tm, 'read_joints', return_value=[0]*6), patch('builtins.input', return_value='MOVE'), patch.object(tm.socket, 'create_connection', return_value=s), patch.object(tm.time, 'sleep'):
            with self.assertRaises(ConnectionError):
                tm.move_joint('unused',6,1)
        self.assertEqual(len(s.sent),2)

    def test_invalid_relative_input_never_connects(self):
        with patch.object(tm.socket, 'create_connection') as connect:
            for joint, delta in ((0,1),(7,1),(1.5,1),(6,float('nan')),(6,float('inf'))):
                with self.assertRaises(ValueError):
                    tm.move_joint('unused',joint,delta)
            tm.move_joint('unused',6,0)
            connect.assert_not_called()

    def test_changed_pose_blocks_motion(self):
        s = FakeSocket(tm.packet('TMSTA','00,true,Listen1'))
        changed = [0,0,0,0,0,0.2]
        with patch.object(tm, 'read_joints', side_effect=[[0]*6,changed,changed]), patch('builtins.input', return_value='MOVE'), patch.object(tm.socket, 'create_connection', return_value=s), patch.object(tm.time, 'sleep'):
            with self.assertRaises(RuntimeError):
                tm.move_joint('unused',6,1)
        self.assertEqual(len(s.sent),1)  # Status query only; no motion.


if __name__ == '__main__':
    unittest.main()
