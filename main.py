from hub import port, motion_sensor
import motor
import runloop
import color_sensor
import motor_pair
import math
import color
import distance_sensor

class Esben:
    def __init__(self, motor_left, motor_right, motor_lift, color_sensor_left, force_sensor, distance_sensor):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.motor_lift = motor_lift
        self.color_sensor_left = color_sensor_left
        self.force_sensor = force_sensor
        self.distance_sensor = distance_sensor


        motor_pair.pair(motor_pair.PAIR_1, self.motor_left, self.motor_right)
        motor.reset_relative_position(self.motor_lift, 0)

    async def follow_line(self, speed=250, aggresive=15, min_reflection_sensitivity= 0, max_reflection_sensitivity=7, distance_to=False):
        
        def _follow():
            median_light = 19
            measure = color_sensor.reflection(self.color_sensor_left)
            change = (median_light - measure)*int(speed/aggresive)
            if change > 0:
                motor_pair.move_tank(motor_pair.PAIR_1, speed-change, speed)
            elif change <0:
                motor_pair.move_tank(motor_pair.PAIR_1, speed, speed+change)

            if distance_to == False:
                return (min_reflection_sensitivity <= color_sensor.reflection(self.color_sensor_left) <= max_reflection_sensitivity and color_sensor.color(self.color_sensor_left) ==color.BLACK)

            else:
                return distance_sensor.distance(esben.distance_sensor) <= distance_to

        await runloop.until(_follow)
        motor_pair.stop(motor_pair.PAIR_1)

    async def move(self, distance, steering=0):
        await motor_pair.move_for_degrees(motor_pair.PAIR_1, int((360 * distance) / (55 * math.pi)), steering)

    async def turn(self, degrees):

        def _turn(degrees):
            degrees *= -1
            if degrees < 0:
                motor_pair.move(motor_pair.PAIR_1, 100, velocity=100)
                return motion_sensor.tilt_angles()[0] / 10 <= degrees
            elif degrees > 0:
                motor_pair.move(motor_pair.PAIR_1, -100, velocity=100)
                return motion_sensor.tilt_angles()[0] / 10 >= degrees
            else:
                return True
        motion_sensor.reset_yaw(0)
        await runloop.sleep_ms(10)
        await runloop.until(lambda: _turn(degrees))
        motor_pair.stop(motor_pair.PAIR_1)

    async def lift_up(self, speed=500, position=300):
        await motor.run_to_relative_position(self.motor_lift, position, speed)

    async def lift_down(self, speed=500):
        await motor.run_to_relative_position(self.motor_lift, 0, speed)

    async def move_to_distance(self, min_distance, speed=100):
        def _move_to_distance():
            dist = distance_sensor.distance(self.distance_sensor)
            motor_pair.move(motor_pair.PAIR_1, motion_sensor.tilt_angles()[0], velocity=speed)
            return dist != -1 and dist <= min_distance

        motion_sensor.reset_yaw(0)
        await runloop.until(_move_to_distance)
        motor_pair.stop(motor_pair.PAIR_1)

    async def find(self, max_distance, velocity=50):
        motor_pair.move(motor_pair.PAIR_1, -100, velocity=velocity)
        await runloop.until(lambda: distance_sensor.distance(self.distance_sensor)<= max_distance)
        motor_pair.stop(motor_pair.PAIR_1)

esben = Esben(port.F, port.B, port.D, port.E, port.A, port.C)

async def main():
    await esben.move_to_distance(400)

runloop.run(main())
