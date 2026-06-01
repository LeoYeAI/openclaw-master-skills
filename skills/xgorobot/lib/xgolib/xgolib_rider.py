import serial
import struct
import time
import math

__version__ = '1.4.2'
__last_modified__ = '2024/2/25'

"""
XGOorder 用来存放命令地址和对应数据
XGOorder is used to store the command address and corresponding data
"""

XGOorder = {
    "BATTERY": [0x01, 100],
    "PERFORM": [0x03, 0],
    "CALIBRATION": [0x04, 0],
    "UPGRADE": [0x05, 0],
    "SET_ORIGIN": [0x06, 1],
    "FIRMWARE_VERSION": [0x07],
    "GAIT_TYPE": [0x09, 0x00],
    "BT_NAME": [0x13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "UNLOAD_MOTOR": [0x20, 0],
    "LOAD_MOTOR": [0x20, 0],
    "VX": [0x30, 128],
    "VY": [0x31, 128],
    "VYAW": [0x32, 128],
    "TRANSLATION": [0x33, 0, 0, 0],
    "ATTITUDE": [0x36, 0, 0, 0],
    "PERIODIC_ROT": [0x39, 0, 0, 0],
    "MarkTime": [0x3C, 0],
    "MOVE_MODE": [0x3D, 0],
    "ACTION": [0x3E, 0],
    "MOVE_TO": [0x3F, 0, 0],
    "PERIODIC_TRAN": [0x80, 0, 0, 0],
    "MOTOR_ANGLE": [0x50, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128],
    "MOTOR_SPEED": [0x5C, 1],
    "MOVE_TO_MID": [0x5F, 1],
    "LEG_POS": [0x40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "IMU": [0x61, 0],
    "ROLL": [0x62, 0],
    "PITCH": [0x63, 0],
    "TEACH_RECORD": [0x21, 0],
    "TEACH_PLAY": [0x22, 0],
    "TEACH_ARM_RECORD": [0x23, 0],
    "TEACH_ARM_PLAY": [0x24, 0],
    "YAW": [0x64, 0],
    "CLAW": [0x71, 0],
    "ARM_MODE": [0x72, 0],
    "ARM_X": [0x73, 0],
    "ARM_Z": [0x74, 0],
    "ARM_SPEED": [0x75, 0],
    "ARM_THETA": [0x76, 0],
    "ARM_R": [0x77, 0],
    "OUTPUT_ANALOG": [0x90, 0],
    "OUTPUT_DIGITAL": [0x91, 0],
    "LED_COLOR": [0x69, 0, 0, 0]
}

"""
XGOparam 用来存放机器狗的参数限制范围
Xgoparam is used to store the parameter limit range of the robot dog
"""
XGOparam = {}

"""
数据处理部分（公共部分）
"""
def search(data, list):
    for i in range(len(list)):
        if data == list[i]:
            return i + 1
    return -1


def conver2u8(data, limit, min_value=0):
    """
    将实际参数转化为0到255的单字节数据
    Convert the actual parameters to single byte data from 0 to 255
    """
    max_value = 0xff
    if not isinstance(limit, list):
        limit = [-limit, limit]
    if data >= limit[1]:
        return max_value
    elif data <= limit[0]:
        return min_value
    else:
        return int(255 / (limit[1] - limit[0]) * (data - limit[0]))


def conver2float(data, limit):
    if not isinstance(limit, list):
        return (data - 128.0) / 255.0 * limit
    else:
        return data / 255.0 * (limit[1] - limit[0]) + limit[0]


def Byte2Float(rawdata):
    a = bytearray()
    a.append(rawdata[3])
    a.append(rawdata[2])
    a.append(rawdata[1])
    a.append(rawdata[0])
    return struct.unpack("!f", a)[0]


def Byte2Short(rawdata):
    a = bytearray()
    a.append(rawdata[0])
    a.append(rawdata[1])
    return struct.unpack('>h', a)[0]


def changePara(version):
    global XGOparam
    if version == "xgorider":
        XGOparam = {
            "TRANSLATION_LIMIT": [1, 1, [60, 120]],
            "ATTITUDE_LIMIT": [17, 1, 1],
            "LEG_LIMIT": [1, 1, [60, 120]],
            "MOTOR_LIMIT": [[-1, 1], [-1, 1], [-1, 1], [-1, 1], [-1, 1], [-1, 1]],
            "PERIOD_LIMIT": [[1, 2]],
            "MARK_TIME_LIMIT": [-1, 1],
            "VX_LIMIT": 1.5,
            "VY_LIMIT": 1.0,
            "VYAW_LIMIT": 360,
            "ARM_LIMIT": [[-1, 1], [-1, 1], [-1, 1], [-1, 1]],
            "ActionTime": {
                1: 3, 2: 3, 3: 5, 4: 5, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 10: 7,
                11: 7, 12: 5, 13: 7, 14: 10, 15: 6, 16: 6, 17: 4, 18: 6, 19: 10, 20: 9,
                21: 8, 22: 7, 23: 6, 24: 7, 128: 10, 129: 10, 130: 10, 255: 1}
        }


class XGO_RIDER():
    """
    在实例化XGO时需要指定上位机与机器狗的串口通讯接口
    When instantiating XGO, you need to specify the serial
    communication interface between the upper computer and the machine dog
    """

    def __init__(self, port, baud=115200, version="xgorider", verbose=False):
        self.verbose = verbose
        self.ser = serial.Serial("/dev/ttyAMA0", baud, timeout=0.5)
        self.ser.flushOutput()
        self.ser.flushInput()
        self.port = port
        self.rx_FLAG = 0
        self.rx_COUNT = 0
        self.rx_ADDR = 0
        self.rx_LEN = 0
        self.rx_data = bytearray(50)
        time.sleep(0.1)
        self.version = self.read_firmware()
        # if self.version[0] == 'M':
        #     changePara('xgomini')
        # elif self.version[0] == 'L':
        #     changePara('xgolite')
        if self.version[0] == 'R':
            changePara('xgorider')
        else:
            changePara('xgorider')
            print(self.version)
        self.mintime = 0.65
        self.reset()
        self.init_yaw = self.read_yaw()
        pass

    def __send(self, key, index=1, len=1):
        mode = 0x01
        order = XGOorder[key][0] + index - 1
        value = []
        value_sum = 0
        for i in range(0, len):
            value.append(XGOorder[key][index + i])
            value_sum = value_sum + XGOorder[key][index + i]
        sum_data = ((len + 0x08) + mode + order + value_sum) % 256
        sum_data = 255 - sum_data
        tx = [0x55, 0x00, (len + 0x08), mode, order]
        tx.extend(value)
        tx.extend([sum_data, 0x00, 0xAA])
        self.ser.write(tx)
        if self.verbose:
            print("tx_data: ", tx)

    def __read(self, addr, read_len=1):
        self.ser.flushInput()
        mode = 0x02
        sum_data = (0x09 + mode + addr + read_len) % 256
        sum_data = 255 - sum_data
        tx = [0x55, 0x00, 0x09, mode, addr, read_len, sum_data, 0x00, 0xAA]
        self.ser.flushInput()
        self.ser.write(tx)
        if self.verbose:
            print("tx_data: ", tx)

    def __change_baud(self, baud):
        self.ser.flush()
        self.ser.close()
        self.ser = serial.Serial(self.port, baud, timeout=0.5)

    def stop(self):
        self.move_x(0)
        self.move_y(0)
        self.mark_time(0)
        self.turn(0)

    def move(self, direction, step):
        if direction in ['x', 'X']:
            self.move_x(step)
        elif direction in ['y', 'Y']:
            self.move_y(step)
        else:
            print("ERROR!Invalid direction!")

    def move_x(self, step, runtime=0):
        XGOorder["VX"][1] = conver2u8(step, XGOparam["VX_LIMIT"])
        self.__send("VX")
        if runtime:
            time.sleep(runtime)
            XGOorder["VX"][1] = conver2u8(0, XGOparam["VX_LIMIT"])
            self.__send("VX")

    def move_y(self, step, runtime=0):
        XGOorder["VY"][1] = conver2u8(step, XGOparam["VY_LIMIT"])
        self.__send("VY")
        if runtime:
            time.sleep(runtime)
            XGOorder["VY"][1] = conver2u8(0, XGOparam["VY_LIMIT"])
            self.__send("VY")

    def turn(self, step, runtime=0):
        XGOorder["VYAW"][1] = conver2u8(step, XGOparam["VYAW_LIMIT"])
        self.__send("VYAW")
        if runtime:
            time.sleep(runtime)
            XGOorder["VYAW"][1] = conver2u8(0, XGOparam["VYAW_LIMIT"])
            self.__send("VYAW")

    def forward(self, step):
        self.move_x(abs(step))

    def back(self, step):
        self.move_x(-abs(step))

    def left(self, step):
        self.move_y(abs(step))

    def right(self, step):
        self.move_y(-abs(step))

    def turnleft(self, step):
        self.turn(abs(step))

    def turnright(self, step):
        self.turn(-abs(step))

    def move_by(self, distance, vx, vy, k, mintime):
        runtime = k * abs(distance) + mintime
        self.move_x(math.copysign(vx, distance))
        self.move_y(math.copysign(vy, distance))
        time.sleep(runtime)
        self.move_x(0)
        self.move_y(0)
        time.sleep(0.2)

    def move_x_by(self, distance, vx=18, k=0.035, mintime=0.55):
        self.move_by(distance, vx, 0, k, mintime)
        pass

    def move_y_by(self, distance, vy=18, k=0.0373, mintime=0.5):
        self.move_by(distance, 0, vy, k, mintime)
        pass

    def turn_by(self, theta, mintime, vyaw=16, k=0.08):
        runtime = abs(theta) * k + mintime
        self.turn(math.copysign(vyaw, theta))
        time.sleep(runtime)
        self.turn(0)
        pass

    def turn_to(self, theta, vyaw=60, emax=10):
        cur_yaw = self.read_yaw()
        des_yaw = self.init_yaw + theta
        while abs(des_yaw - cur_yaw) >= emax:
            self.turn(math.copysign(vyaw, des_yaw - cur_yaw))
            cur_yaw = self.read_yaw()
        self.turn(0)
        time.sleep(0.2)
        pass

    def __translation(self, direction, data):
        index = search(direction, ['x', 'y', 'z'])
        if index == -1:
            print("ERROR!Direction must be 'x', 'y' or 'z'")
            return
        XGOorder["TRANSLATION"][index] = conver2u8(data, XGOparam["TRANSLATION_LIMIT"][index - 1])
        self.__send("TRANSLATION", index)

    def translation(self, direction, data):
        """
        使机器狗足端不动，身体进行三轴平动
        Keep the robot's feet stationary and the body makes three-axis translation
        """
        if isinstance(direction, list):
            if len(direction) != len(data):
                print("ERROR!The length of direction and data don't match!")
                return
            for i in range(len(data)):
                self.__translation(direction[i], data[i])
        else:
            self.__translation(direction, data)

    def __attitude(self, direction, data):
        index = search(direction, ['r', 'p', 'y'])
        if index == -1:
            print("ERROR!Direction must be 'r', 'p' or 'y'")
            return
        XGOorder["ATTITUDE"][index] = conver2u8(data, XGOparam["ATTITUDE_LIMIT"][index - 1])
        self.__send("ATTITUDE", index)

    def attitude(self, direction, data):
        """
        使机器狗足端不动，身体进行三轴转动
        Keep the robot's feet stationary and the body makes three-axis rotation
        """
        if isinstance(direction, list):
            if len(direction) != len(data):
                print("ERROR!The length of direction and data don't match!")
                return
            for i in range(len(data)):
                self.__attitude(direction[i], data[i])
        else:
            self.__attitude(direction, data)

    def action(self, action_id, wait=False):
        """
        使机器狗狗指定的预设动作
        Make the robot do the specified preset action
        """
        if action_id <= 0 or action_id > 255:
            print("ERROR!Illegal Action ID!")
            return
        XGOorder["ACTION"][1] = action_id
        self.__send("ACTION")
        if wait:
            st = ActionTime.get(action_id)
            if st:
                time.sleep(st)

    def reset(self):
        """
        机器狗停止运动，所有参数恢复到初始状态
        The robot dog stops moving and all parameters return to the initial state
        """
        self.action(255)
        time.sleep(0.1)

    def leg(self, leg_id, data):
        """
        控制机器狗的单腿的三轴移动
        Control the three-axis movement of a single leg of the robot
        """
        value = [0, 0, 0]
        if leg_id not in [1, 2, 3, 4]:
            print("Error!Illegal Index!")
            return
        if len(data) != 3:
            message = "Error!Illegal Value!"
            return
        for i in range(3):
            try:
                value[i] = conver2u8(data[i], XGOparam["LEG_LIMIT"][i])
            except:
                print("Error!Illegal Value!")
        for i in range(3):
            index = 3 * (leg_id - 1) + i + 1
            XGOorder["LEG_POS"][index] = value[i]
            self.__send("LEG_POS", index)

    def __motor(self, index, data):
        if index < 13:
            XGOorder["MOTOR_ANGLE"][index] = conver2u8(data, XGOparam["MOTOR_LIMIT"][(index - 1) % 3])
        elif index == 13:
            self.claw(conver2u8(data, XGOparam["MOTOR_LIMIT"][3]))
            return
        else:
            XGOorder["MOTOR_ANGLE"][index] = conver2u8(data, XGOparam["MOTOR_LIMIT"][index - 10])
        self.__send("MOTOR_ANGLE", index)

    def motor(self, motor_id, data):
        """
        控制机器狗单个舵机转动
        Control the rotation of a single steering gear of the robot
        """
        MOTOR_ID = [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43, 51, 52, 53]

        if isinstance(motor_id, list):
            if len(motor_id) != len(data):
                print("Error!Length Mismatching!")
                return
            index = []
            for i in range(len(motor_id)):
                temp_index = search(motor_id[i], MOTOR_ID)
                if temp_index == -1:
                    print("Error!Illegal Index!")
                    return
                index.append(temp_index)
            for i in range(len(index)):
                self.__motor(index[i], data[i])
        else:
            index = search(motor_id, MOTOR_ID)
            self.__motor(index, data)

    def unload_motor(self, leg_id):
        if leg_id not in [1, 2, 3, 4, 5]:
            print('ERROR!leg_id must be 1, 2, 3 ,4 or 5')
            return
        XGOorder["UNLOAD_MOTOR"][1] = 0x10 + leg_id
        self.__send("UNLOAD_MOTOR")

    def unload_allmotor(self):
        XGOorder["UNLOAD_MOTOR"][1] = 0x01
        self.__send("UNLOAD_MOTOR")

    def load_motor(self, leg_id):
        if leg_id not in [1, 2, 3, 4, 5]:
            print('ERROR!leg_id must be 1, 2, 3 ,4 or 5')
            return
        XGOorder["LOAD_MOTOR"][1] = 0x20 + leg_id
        self.__send("LOAD_MOTOR")

    def load_allmotor(self):
        XGOorder["LOAD_MOTOR"][1] = 0x00
        self.__send("LOAD_MOTOR")

    def __periodic_rot(self, direction, period):
        index = search(direction, ['r', 'p', 'y'])
        if index == -1:
            print("ERROR!Direction must be 'r', 'p' or 'y'")
            return
        if period == 0:
            XGOorder["PERIODIC_ROT"][index] = 0
        else:
            XGOorder["PERIODIC_ROT"][index] = conver2u8(period, XGOparam["PERIOD_LIMIT"][0], min_value=1)
        self.__send("PERIODIC_ROT", index)

    def periodic_rot(self, direction, period):
        """
        使机器狗周期性转动
        Make the robot rotate periodically
        """
        if (isinstance(direction, list)):
            if (len(direction) != len(period)):
                print("ERROR!The length of direction and data don't match!")
                return
            for i in range(len(period)):
                self.__periodic_rot(direction[i], period[i])
        else:
            self.__periodic_rot(direction, period)

    def __periodic_tran(self, direction, period):
        index = search(direction, ['x', 'y', 'z'])
        if index == -1:
            print("ERROR!Direction must be 'x', 'y' or 'z'")
            return
        if period == 0:
            XGOorder["PERIODIC_TRAN"][index] = 0
        else:
            XGOorder["PERIODIC_TRAN"][index] = conver2u8(period, XGOparam["PERIOD_LIMIT"][0], min_value=1)
        self.__send("PERIODIC_TRAN", index)

    def periodic_tran(self, direction, period):
        """
        使机器狗周期性平动
        Make the robot translate periodically
        """
        if isinstance(direction, list):
            if len(direction) != len(period):
                print("ERROR!The length of direction and data don't match!")
                return
            for i in range(len(period)):
                self.__periodic_tran(direction[i], period[i])
        else:
            self.__periodic_tran(direction, period)

    def mark_time(self, data):
        """
        使机器狗原地踏步
        Make the robot marks time
        """
        if data == 0:
            XGOorder["MarkTime"][1] = 0
        else:
            XGOorder["MarkTime"][1] = conver2u8(data, XGOparam["MARK_TIME_LIMIT"], min_value=1)
        self.__send("MarkTime")


    def imu(self, mode):
        """
        开启/关闭机器狗自稳状态
        Turn on / off the self stable state of the robot dog
        """
        if mode != 0 and mode != 1:
            print("ERROR!Illegal Value!")
            return
        XGOorder["IMU"][1] = mode
        self.__send("IMU")

    def perform(self, mode):
        """
        开启/关闭机器狗循环做动作状态
        Turn on / off the action status of the robot dog cycle
        """
        if mode != 0 and mode != 1:
            print("ERROR!Illegal Value!")
            return
        XGOorder["PERFORM"][1] = mode
        self.__send("PERFORM")

    def motor_speed(self, speed):
        """
        调节舵机转动速度，只在单独控制舵机的情况下有效
        Adjust the steering gear rotation speed,
        only effective when control the steering gear separately
        """
        if speed < 0 or speed > 255:
            print("ERROR!Illegal Value!The speed parameter needs to be between 0 and 255!")
            return
        if speed == 0:
            speed = 1
        XGOorder["MOTOR_SPEED"][1] = speed
        self.__send("MOTOR_SPEED")

    def bt_rename(self, name):
        if type(name) != str:
            print("ERROR!The input value must be of string type!")
            return
        len_name = len(name)
        if len_name > 10:
            print("ERROR!The length of the input string cannot be longer than 10!")
            return
        try:
            XGOorder["BT_NAME"][1:len_name + 1] = list(name.encode('ascii'))
            self.__send("BT_NAME", len=len_name)
        except:
            print("ERROR!Name only supports characters in ASCII code!")

    def read_motor(self):
        """
        读取15个舵机的角度
        """
        self.__read(XGOorder["MOTOR_ANGLE"][0], 15)
        angle = []
        if self.__unpack():
            for i in range(self.rx_COUNT + 1):
                if i < 12:
                    angle.append(round(conver2float(self.rx_data[i], XGOparam["MOTOR_LIMIT"][i % 3]), 2))
                else:
                    angle.append(round(conver2float(self.rx_data[i], XGOparam["MOTOR_LIMIT"][i - 9]), 2))
        return angle

    def read_battery(self):
        self.__read(XGOorder["BATTERY"][0], 1)
        battery = 0
        if self.__unpack():
            battery = int(self.rx_data[0])
        return battery

    def read_firmware(self):
        self.__read(XGOorder["FIRMWARE_VERSION"][0], 10)
        firmware_version = 'Null'
        if self.__unpack():
            data = self.rx_data[0:10]
            try:
                firmware_version = data.decode("ascii").strip('\0')
            except Exception as e:
                print(e)
        return firmware_version

    def read_roll(self):
        self.__read(XGOorder["ROLL"][0], 4)
        roll = 0
        if self.__unpack():
            roll = Byte2Float(self.rx_data)
        return round(roll, 2)

    def read_pitch(self):
        self.__read(XGOorder["PITCH"][0], 4)
        pitch = 0
        if self.__unpack():
            pitch = Byte2Float(self.rx_data)
        return round(pitch, 2)

    def read_yaw(self):
        self.__read(XGOorder["YAW"][0], 4)
        yaw = 0
        if self.__unpack():
            yaw = Byte2Float(self.rx_data)
        return round(yaw, 2)

    def __unpack(self, timeout=1):
        t = time.time()
        rx_msg = []
        while time.time() - t < timeout:
            n = self.ser.inWaiting()
            rx_CHECK = 0
            if n:
                data = self.ser.read(n)
                for num in data:
                    rx_msg.append(num)
                    if self.rx_FLAG == 0:
                        if num == 0x55:
                            self.rx_FLAG = 1
                        else:
                            self.rx_FLAG = 0

                    elif self.rx_FLAG == 1:
                        if num == 0x00:
                            self.rx_FLAG = 2
                        else:
                            self.rx_FLAG = 0

                    elif self.rx_FLAG == 2:
                        self.rx_LEN = num
                        self.rx_FLAG = 3

                    elif self.rx_FLAG == 3:
                        self.rx_TYPE = num
                        self.rx_FLAG = 4

                    elif self.rx_FLAG == 4:
                        self.rx_ADDR = num
                        self.rx_FLAG = 5
                        self.rx_COUNT = 0

                    elif self.rx_FLAG == 5:
                        if self.rx_COUNT == (self.rx_LEN - 9):
                            self.rx_data[self.rx_COUNT] = num
                            self.rx_FLAG = 6
                        elif self.rx_COUNT < self.rx_LEN - 9:
                            self.rx_data[self.rx_COUNT] = num
                            self.rx_COUNT = self.rx_COUNT + 1

                    elif self.rx_FLAG == 6:
                        for i in self.rx_data[0:(self.rx_LEN - 8)]:
                            rx_CHECK = rx_CHECK + i
                        rx_CHECK = 255 - (self.rx_LEN + self.rx_TYPE + self.rx_ADDR + rx_CHECK) % 256
                        if num == rx_CHECK:
                            self.rx_FLAG = 7
                        else:
                            self.rx_FLAG = 0
                            self.rx_COUNT = 0
                            self.rx_ADDR = 0
                            self.rx_LEN = 0

                    elif self.rx_FLAG == 7:
                        if num == 0x00:
                            self.rx_FLAG = 8
                        else:
                            self.rx_FLAG = 0
                            self.rx_COUNT = 0
                            self.rx_ADDR = 0
                            self.rx_LEN = 0

                    elif self.rx_FLAG == 8:
                        if num == 0xAA:
                            self.rx_FLAG = 0
                            if self.verbose:
                                print("rx_data: ", rx_msg)
                            return True
                        else:
                            self.rx_FLAG = 0
                            self.rx_COUNT = 0
                            self.rx_ADDR = 0
                            self.rx_LEN = 0
        return False

    def set_move_mintime(self, mintime):
        self.mintime = mintime

    def upgrade(self, filename):
        XGOorder["UPGRADE"][1] = 1
        self.ser.flush()
        self.__send("UPGRADE")
        if self.__unpack(10):
            if self.rx_data[0] == 0x55:
                time.sleep(1)
                print("Start!")
                self.__send_bin(filename)
            else:
                print("Upgrade Response Error!")
        else:
            print("Upgrade Timeout!")

    def read_lib_version(self):
        return __version__

    def __send_bin(self, filename):
        """
        处于测试阶段，请勿使用
        """
        try:
            self.__change_baud(350000)
            with open(filename, 'rb') as f:
                file = f.read()
            print("The file size is", len(file), ' bytes.')
            print("The expected upgrade time is", round(len(file) / 350000 * 8 * 1.3), ' s.')
            self.ser.write(file)
            print("Done!")
            self.__change_baud(115200)
        except Exception as e:
            print("Send bin file error!")
            print(e)

    def calibration(self, state):
        """
        用于软件标定，请谨慎使用！！！
        """
        if state == 'start':
            XGOorder["CALIBRATION"][1] = 1
        elif state == 'end':
            XGOorder["CALIBRATION"][1] = 0
        else:
            print("ERROR!")
        self.__send("CALIBRATION")
        return

    def btRename(self, name):
        length = len(name)
        if not isinstance(name, str):
            print("Wrong type!")
            return

        if length > 20:
            print("The length of the name needs to be less than 20")
            return

        if not name.isalnum():
            print("The name can only contain numbers and letters")
            return

        XGOorder["BT_NAME"] = [0x13]
        for c in list(name):
            if ord(c) > 255:
                print("The name can only contain numbers and letters")
                return
            else:
                XGOorder["BT_NAME"].append(ord(c))
        print(XGOorder["BT_NAME"])
        self.__send("BT_NAME", len=length)

    def moveToMid(self):
        self.__send("MOVE_TO_MID")

    def teach(self, mode, pos_id):
        if mode == "play":
            XGOorder["TEACH_PLAY"][1] = pos_id
            self.__send("TEACH_PLAY")
        if mode == "record":
            XGOorder["TEACH_RECORD"][1] = pos_id
            self.__send("TEACH_RECORD")
        else:
            return


    def read_imu(self):
        self.__read(0x65, 24)
        result = []
        if self.__unpack():
            result = self.unpack_imu()
        return result

    def read_imu_int16(self, direction):
        if direction == "roll":
            self.__read(0x66, 2)
        elif direction == "pitch":
            self.__read(0x67, 2)
        elif direction == "yaw":
            self.__read(0x68, 2)
        else:
            return None
        result = []
        if self.__unpack():
            result = Byte2Short(self.rx_data)
        return result

    def unpack_imu(self):
        result = []
        for i in range(9):
            a = bytearray()
            if i < 6:
                a.append(self.rx_data[2 * i + 1])
                a.append(self.rx_data[2 * i])
                if i < 3:
                    result.append(struct.unpack("!h", a)[0] / 16384 * 9.8)
                else:
                    result.append(struct.unpack("!h", a)[0] / 16.4)
            else:
                a.append(self.rx_data[4 * i - 9])
                a.append(self.rx_data[4 * i - 10])
                a.append(self.rx_data[4 * i - 11])
                a.append(self.rx_data[4 * i - 12])
                result.append(struct.unpack("!f", a)[0] / 180 * 3.14)
        return result

    def set_origin(self):
        XGOorder["SET_ORIGIN"][1] = 1
        self.__send("SET_ORIGIN")

    def move_to(self, data):
        packed_data = struct.pack('>h', data)
        XGOorder["MOVE_TO"][1] = packed_data[0]
        XGOorder["MOVE_TO"][2] = packed_data[1]
        self.__send("MOVE_TO", len=2)

    def output_analog(self, data):
        XGOorder["OUTPUT_ANALOG"][1] = data
        self.__send("OUTPUT_ANALOG")
        pass

    def output_digital(self, data):
        XGOorder["OUTPUT_DIGITAL"][1] = data
        self.__send("OUTPUT_DIGITAL")
        pass

    ############# RIDER ################

    def rider_move_x(self, speed, runtime=0):
        XGOorder["VX"][1] = conver2u8(speed, XGOparam["VX_LIMIT"])
        self.__send("VX")
        if runtime:
            time.sleep(runtime)
            XGOorder["VX"][1] = conver2u8(0, XGOparam["VX_LIMIT"])
            self.__send("VX")

    def rider_turn(self, speed, runtime=0):
        XGOorder["VYAW"][1] = conver2u8(speed, XGOparam["VYAW_LIMIT"])
        self.__send("VYAW")
        if runtime:
            time.sleep(runtime)
            XGOorder["VYAW"][1] = conver2u8(0, XGOparam["VYAW_LIMIT"])
            self.__send("VYAW")

    def rider_reset_odom(self):
        XGOorder["SET_ORIGIN"][1] = 1
        self.__send("SET_ORIGIN")

    def rider_action(self, action_id, wait=False):
        if action_id <= 0 or action_id > 255:
            print("ERROR!Illegal Action ID!")
            return
        XGOorder["ACTION"][1] = action_id
        self.__send("ACTION")
        if wait:
            st = XGOparam["ActionTime"].get(action_id)
            if st:
                time.sleep(st)

    def rider_balance_roll(self, mode):
        if mode != 0 and mode != 1:
            print("ERROR!Illegal Value!")
            return
        XGOorder["IMU"][1] = mode
        self.__send("IMU")

    def rider_perform(self, mode):
        if mode != 0 and mode != 1:
            print("ERROR!Illegal Value!")
            return
        XGOorder["PERFORM"][1] = mode
        self.__send("PERFORM")

    def rider_calibration(self, state):
        """
        用于软件标定，请谨慎使用！！！
        """
        if state == 'start':
            XGOorder["CALIBRATION"][1] = 1
        elif state == 'end':
            XGOorder["CALIBRATION"][1] = 0
        else:
            print("ERROR!")
        self.__send("CALIBRATION")
        return

    def rider_height(self, data):
        self.__translation("z", data)

    def rider_roll(self, data):
        self.__attitude("r", data)

    def rider_periodic_roll(self, period):
        self.__periodic_rot("r", period)

    def rider_periodic_z(self, period):
        self.__periodic_tran("z", period)

    def rider_read_battery(self):
        self.__read(XGOorder["BATTERY"][0], 1)
        battery = 0
        if self.__unpack():
            battery = int(self.rx_data[0])
        return battery

    def rider_read_firmware(self):
        self.__read(XGOorder["FIRMWARE_VERSION"][0], 10)
        firmware_version = 'Null'
        if self.__unpack():
            data = self.rx_data[0:10]
            try:
                firmware_version = data.decode("ascii").strip('\0')
            except Exception as e:
                print(e)
        return firmware_version

    def rider_read_roll(self):
        self.__read(XGOorder["ROLL"][0], 4)
        roll = 0
        if self.__unpack():
            roll = Byte2Float(self.rx_data)
        return round(roll, 2)

    def rider_read_pitch(self):
        self.__read(XGOorder["PITCH"][0], 4)
        pitch = 0
        if self.__unpack():
            pitch = Byte2Float(self.rx_data)
        return round(pitch, 2)

    def rider_read_yaw(self):
        self.__read(XGOorder["YAW"][0], 4)
        yaw = 0
        if self.__unpack():
            yaw = Byte2Float(self.rx_data)
        return round(yaw, 2)

    def rider_read_imu_int16(self, direction):
        if direction == "roll":
            self.__read(0x66, 2)
        elif direction == "pitch":
            self.__read(0x67, 2)
        elif direction == "yaw":
            self.__read(0x68, 2)
        else:
            return None
        result = []
        if self.__unpack():
            result = Byte2Short(self.rx_data)
        return result

    def rider_reset(self):
        return self.reset()

    def rider_upgrade(self, filename):
        XGOorder["UPGRADE"][1] = 1
        self.ser.flush()
        self.__send("UPGRADE")
        if self.__unpack(10):
            if self.rx_data[0] == 0x55:
                time.sleep(1)
                print("Start!")
                self.__send_bin(filename)
            else:
                print("Upgrade Response Error!")
        else:
            print("Upgrade Timeout!")

    def rider_led(self, index, color):
        XGOorder["LED_COLOR"][0] = 0x68 + index
        XGOorder["LED_COLOR"][1:4] = color
        self.__send("LED_COLOR", len=3)

