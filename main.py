from hub import port, motion_sensor
import motor
import runloop
import color_sensor
import motor_pair
import math
import color
import distance_sensor


class Esben:
    def __init__(
        self,
        motor_left,
        motor_right,
        motor_lift,
        color_sensor,
        force_sensor,
        distance_sensor,
    ):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.motor_lift = motor_lift
        self.color_sensor = color_sensor
        self.force_sensor = force_sensor
        self.distance_sensor = distance_sensor

        motor_pair.pair(motor_pair.PAIR_1, self.motor_left, self.motor_right)

    async def follow_line(
        self,
        speed=700,
        aggresive=3,
        min_reflection_sensitivity=0,
        max_reflection_sensitivity=7,
        to_distance=0,
    ):
        median_light = 15

        def _follow():
            measure = color_sensor.reflection(self.color_sensor)
            change = int((median_light - measure) * aggresive)

            motor_pair.move(motor_pair.PAIR_1, -change, velocity=speed)

            if not to_distance:
                return (
                    min_reflection_sensitivity
                    <= color_sensor.reflection(self.color_sensor)
                    <= max_reflection_sensitivity
                    and color_sensor.color(self.color_sensor) == color.BLACK
                )
            else:
                return distance_sensor.distance(self.distance_sensor) <= to_distance

        await runloop.until(_follow)
        motor_pair.stop(motor_pair.PAIR_1)

    async def move(self, distance, steering=0, speed=250):
        await motor_pair.move_for_degrees(
            motor_pair.PAIR_1,
            int((360 * distance) / (55 * math.pi)),
            steering,
            velocity=speed,
        )

    async def turn(self, degrees, speed=250):
        def _turn():
            nonlocal degrees
            degrees *= -1
            if degrees < 0:
                motor_pair.move(motor_pair.PAIR_1, 100, velocity=speed)
                return motion_sensor.tilt_angles()[0] / 10 <= degrees
            elif degrees > 0:
                motor_pair.move(motor_pair.PAIR_1, -100, velocity=speed)
                return motion_sensor.tilt_angles()[0] / 10 >= degrees
            else:
                return True

        motion_sensor.reset_yaw(0)
        await runloop.sleep_ms(10)
        await runloop.until(_turn)
        motor_pair.stop(motor_pair.PAIR_1)

    async def lift_up(self, speed=500, position=300):
        await motor.run_to_relative_position(self.motor_lift, position, speed)

    async def lift_down(self, speed=500):
        await motor.run_to_relative_position(self.motor_lift, 0, speed)

    async def move_to_distance(self, min_distance, speed=100):
        def _move_to_distance():
            dist = distance_sensor.distance(self.distance_sensor)
            motor_pair.move(
                motor_pair.PAIR_1, motion_sensor.tilt_angles()[0], velocity=speed
            )
            return dist != -1 and dist <= min_distance

        motion_sensor.reset_yaw(0)
        await runloop.until(_move_to_distance)
        motor_pair.stop(motor_pair.PAIR_1)

    async def find(self, max_distance, velocity=50):
        motor_pair.move(motor_pair.PAIR_1, -100, velocity=velocity)
        await runloop.until(
            lambda: distance_sensor.distance(self.distance_sensor) <= max_distance
        )
        motor_pair.stop(motor_pair.PAIR_1)
