kfrom hub import light_matrix, port, motion_sensor
import motor
import runloop
import distance_sensor
import color_sensor
import motor_pair
import math
import color

MOTOR_LEFT = port.B
MOTOR_RIGHT = port.F

class Esben:
    def __init__(self, motor_left, motor_right, motor_lift, color_sensor_left, color_sensor_right, distance_sensor):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.motor_lift = motor_lift
        self.color_sensor_left = color_sensor_left
        self.color_sensor_right = color_sensor_right
        self.distance_sensor = distance_sensor

        motor_pair.pair(motor_pair.PAIR_1, self.motor_left, self.motor_right)

    async def follow(self, speed=15, reflection_sensitivity=7):
        def _follow():
            motor_pair.move_tank(motor_pair.PAIR_1,
                color_sensor.reflection(self.color_sensor_left) * speed,
                color_sensor.reflection(self.color_sensor_right) * speed)

            return (color_sensor.reflection(self.color_sensor_left) < reflection_sensitivity
                and color_sensor.reflection(self.color_sensor_right) < reflection_sensitivity
                and color_sensor.color(self.color_sensor_left) == color.BLACK
                and color_sensor.color(self.color_sensor_right) == color.BLACK)

        await runloop.until(_follow)
        motor_pair.stop(motor_pair.PAIR_1)

    async def move(self, distance):
        motor_pair.move_for_degrees(motor_pair.PAIR_1, int((360 * distance) / (5.5 * math.pi)), 0)

    async def turn(self, degrees, radius):
        pass

esben = Esben(port.F, port.B, port.D, port.E, port.A, port.C)

def move_straight():
    motor_pair.move(motor_pair.PAIR_1, motion_sensor.tilt_angles()[0])
    return False


async def main():
    await esben.follow_ai()

runloop.run(main())
