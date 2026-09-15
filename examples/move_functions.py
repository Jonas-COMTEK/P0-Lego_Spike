from hub import light_matrix, port, motion_sensor
import motor
import runloop
import distance_sensor
import motor_pair
import math

MOTOR_LEFT = port.B
MOTOR_RIGHT = port.F

def move_straight():
    motor_pair.move(motor_pair.PAIR_1, motion_sensor.tilt_angles()[0])
    return False

def move_distance(distance):
    motor_pair.move_for_degrees(motor_pair.PAIR_1, int((360 * distance) / (5.5 * math.pi)), 0)

async def main():
    motor_pair.pair(motor_pair.PAIR_1, MOTOR_LEFT, MOTOR_RIGHT)
    move_distance(10)
    pass

runloop.run(main())
