from hub import port, motion_sensor,sound
import motor
import runloop
import color_sensor
import motor_pair
import math
import color
import distance_sensor
import time
import force_sensor


class Anna:
    def __init__(
        self,
        motor_left,
        motor_right,
        color_sensor_left,
        color_sensor_right,
        force_sensor,
        distance_sensor,
    ):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.color_sensor_left = color_sensor_left
        self.color_sensor_right = color_sensor_right
        self.force_sensor = force_sensor
        self.distance_sensor = distance_sensor

        motor_pair.pair(motor_pair.PAIR_1, self.motor_left, self.motor_right)

    async def follow(self, speed=500, aggressive=16, to_distance=0):
            def _follow():
                median_light = 15
                measure = color_sensor.reflection(self.color_sensor)
                change = (median_light - measure)*int(speed/aggressive)
                if change > 0:
                    motor_pair.move_tank(motor_pair.PAIR_1, speed-change, speed)
                elif change < 0:
                    motor_pair.move_tank(motor_pair.PAIR_1, speed, speed+change)

                if not to_distance:
                    return (color_sensor.reflection(self.color_sensor) <= 7
                        and color_sensor.color(self.color_sensor) == color.BLACK)
                else:
                    return (distance_sensor.distance(self.distance_sensor) <= to_distance
                        and distance_sensor.distance(self.distance_sensor) != -1)

            await runloop.until(_follow)
            motor_pair.stop(motor_pair.PAIR_1)

    async def follow_2(self,speed=20):
        def _follow_2():
            motor_pair.move_tank(motor_pair.PAIR_1,
                color_sensor.reflection(self.color_sensor_left) * speed,
                color_sensor.reflection(self.color_sensor_right) * speed)

            return (color_sensor.reflection(self.color_sensor_left) < 10
                or color_sensor.reflection(self.color_sensor_right) < 10)
        
        await runloop.until(_follow_2)



    async def move(self, distance, steering=0, speed=250):
        await motor_pair.move_for_degrees(
            motor_pair.PAIR_1,
            int((360 * distance) / (55 * math.pi)),
            steering,
            velocity=speed,
        )

    async def turn(self, degrees, speed=250):
        def _turn():
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

    async def lift_up(self):
        await motor.run_to_relative_position(self.motor_lift, 300, 500)

    async def lift_down(self):
        await motor.run_to_relative_position(self.motor_lift, 0, 500)

    async def move_to_distance(self, min_distance, speed=100):
        def _move_to_distance():
            dist = distance_sensor.distance(self.distance_sensor)
            motor_pair.move(
                motor_pair.PAIR_1, int(motion_sensor.tilt_angles()[0]/10), velocity=speed
            )
            return dist != -1 and dist <= min_distance

        motion_sensor.reset_yaw(0)
        await runloop.sleep_ms(20)
        await runloop.until(_move_to_distance)
        motor_pair.stop(motor_pair.PAIR_1)

    async def find(self):
        def _find():
            nonlocal yaw_to_move_to
            nonlocal direction
            nonlocal distance
            motor_pair.move(motor_pair.PAIR_1, 100*direction, velocity=50)
            yaw = motion_sensor.tilt_angles()[0]
            distance = distance_sensor.distance(self.distance_sensor)

            if distance <= max_distance and distance != -1:
                motor_pair.stop(motor_pair.PAIR_1)
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

        yaw_to_move_to = 10
        max_yaw_minus = -100
        max_yaw_plus = 100
        max_distance = 400
        direction = -1
        distance = 2000
        yaw_left = 0
        yaw_right = 0
        motion_sensor.reset_yaw(0)
        print("Finding")
        await runloop.until(_find)
        print(distance)
        await self.move(distance-220)
        max_distance = 300
        await runloop.until(_find)
        yaw_to_move_to = motion_sensor.tilt_angles()[0] - 10
        await runloop.sleep_ms(10)
        print("finding left")
        await runloop.until(_find_left)
        print("turning back")
        yaw_to_move_to = motion_sensor.tilt_angles()[0] - 120
        max_yaw_minus = motion_sensor.tilt_angles()[0] - 250
        max_yaw_plus = motion_sensor.tilt_angles()[0] - 120
        max_distance = 500
        direction = 1
        await runloop.until(_find)

        yaw_to_move_to = motion_sensor.tilt_angles()[0] - 10
        print("Finding right")
        await runloop.until(_find_right)
        print(yaw_right)
        print(yaw_left)
        await self.turn(-(yaw_left-yaw_right)/20,speed=100)
        motor_pair.stop(motor_pair.PAIR_1)
        print(distance)
        await self.move(distance-35,speed=100)

anna = Anna(port.B, port.F, port.E, port.A, port.C, port.D)

async def brudt_streg():
    await anna.turn(45)
    await anna.move(250, speed=500)
    await anna.turn(-35)
    await anna.follow_2(40)
    await anna.turn(-45)
    await anna.move(275, speed= 500)
    await anna.turn(35)

async def parrallel():
    await anna.turn(-20)
    await anna.move(500,speed=1100)
    await anna.turn(20)

async def short_cut():
    await runloop.sleep_ms(50)
    await anna.follow_2(40)
    await anna.move(240, speed=1100)
    await anna.turn(-85)
    await anna.follow_2(30)
    await anna.move(100, speed=1100)
    await anna.turn(85)
    await anna.move(750, speed=1100)
    await anna.turn(-75)

async def short_cut_2():
    def _short_cut_2():
        return color_sensor.reflection(anna.color_sensor_left) < 20 or color_sensor.reflection(anna.color_sensor_right) < 20
    await runloop.sleep_ms(50)
    await anna.follow_2(40)
    await anna.turn(65)
    motor_pair.move(motor_pair.PAIR_1,0,velocity=1100)
    await runloop.until(_short_cut_2)
    motor_pair.stop(motor_pair.PAIR_1)
    await runloop.sleep_ms(10)
    await anna.move(150,speed=1100)
    await anna.turn(-70)
    await anna.move(300,speed=1100)
    await anna.turn(80, speed=500)
    await anna.move(950,speed=1100)

async def main():

    obstacles = {
        brudt_streg:   40 ,
        short_cut:      40,
        parrallel:    35,
        short_cut_2: 0,
    }
    obstacle_list = [brudt_streg, short_cut, parrallel,short_cut_2]

    await anna.follow_2(40)
    for obstacle in obstacle_list:
        await obstacle()
        await anna.follow_2(obstacles[obstacle])


runloop.run(main())