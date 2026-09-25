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
            if degrees < 0:
                motor_pair.move(motor_pair.PAIR_1, 100, velocity=speed)
                return motion_sensor.tilt_angles()[0] / 10 <= degrees
            elif degrees > 0:
                motor_pair.move(motor_pair.PAIR_1, -100, velocity=speed)
                return motion_sensor.tilt_angles()[0] / 10 >= degrees
            else:
                return True

        degrees *= -1
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

    async def find(self):
        def _find():
            nonlocal yaw_to_move_to
            nonlocal direction
            nonlocal distance
            nonlocal first_hit
            motor_pair.move(motor_pair.PAIR_1, 100*direction, velocity=50)
            yaw = motion_sensor.tilt_angles()[0]
            distance = distance_sensor.distance(self.distance_sensor)

            if distance <= max_distance and distance != -1:
                first_hit = yaw
                return True
            if direction == 1:
                if yaw < max_yaw_minus:
                    direction *= -1
                elif yaw < yaw_to_move_to:
                    yaw_to_move_to -= 10
                    motor_pair.stop(motor_pair.PAIR_1)
                    time.sleep_ms(100)
            elif direction == -1:
                if yaw > max_yaw_plus:
                    direction *= -1
                elif yaw > yaw_to_move_to:
                    yaw_to_move_to += 10
                    motor_pair.stop(motor_pair.PAIR_1)
                    time.sleep_ms(100)
            return False
        
        def _find_left ():
            nonlocal yaw_left
            nonlocal yaw_to_move_to
            motor_pair.move(motor_pair.PAIR_1, -100, velocity=50)
            yaw = motion_sensor.tilt_angles()[0]
            distance = distance_sensor.distance(self.distance_sensor)
            if distance == -1 or distance > 500:
                yaw_left = yaw
                motor_pair.stop(motor_pair.PAIR_1)
                return True
            if yaw < yaw_to_move_to:
                yaw_to_move_to -= 10
                motor_pair.stop(motor_pair.PAIR_1)
                time.sleep_ms(100)
            return False

        def _find_right ():
            nonlocal yaw_right
            nonlocal yaw_to_move_to
            motor_pair.move(motor_pair.PAIR_1, 100, velocity=50)
            yaw = motion_sensor.tilt_angles()[0]
            distance = distance_sensor.distance(self.distance_sensor)
            if distance == -1 or distance > 500:
                yaw_right = yaw
                motor_pair.stop(motor_pair.PAIR_1)
                return True
            if yaw > yaw_to_move_to:
                yaw_to_move_to += 10
                motor_pair.stop(motor_pair.PAIR_1)
                time.sleep_ms(100)
            return False

        yaw_to_move_to = -10
        max_yaw_minus = -100
        max_yaw_plus = 100
        max_distance = 400
        direction = -1
        distance=2000
        first_hit = 0
        yaw_left = 0
        yaw_right = 0
        motion_sensor.reset_yaw(0)
        print("Finding")
        await runloop.until(_find)
        motor_pair.stop(motor_pair.PAIR_1)
        print(distance)
        await self.move(distance-200)
        max_distance = 300
        await runloop.until(_find)
        yaw_to_move_to = motion_sensor.tilt_angles()[0] - 10
        await runloop.sleep_ms(10)
        print("finding left")
        await runloop.until(_find_left)
        print("turning back")
        yaw_to_move_to = motion_sensor.tilt_angles()[0] + 10
        max_yaw_minus = motion_sensor.tilt_angles()[0] - 200
        max_yaw_plus = motion_sensor.tilt_angles()[0] + 100
        max_distance = 500
        direction = 1
        await runloop.until(_find)

        yaw_to_move_to = motion_sensor.tilt_angles()[0] + 10
        print("Finding right")
        await runloop.until(_find_right)
        print(yaw_right)
        print(yaw_left)
        await self.turn(-(yaw_left-yaw_right)/20)
        motor_pair.stop(motor_pair.PAIR_1)
        print(distance)
        await self.move(distance-35)
