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
        motor.reset_relative_position(self.motor_lift, 0)

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

esben = Esben(port.F, port.B, port.D, port.E, port.A, port.C)

async def brudt_streg():
    await esben.turn(45,150)
    await esben.move(250, speed=500)
    await esben.turn(-35,150)
    await esben.follow(speed = 500, aggressive=17)
    await esben.turn(-45,150)
    await esben.move(275, speed= 500)
    await esben.turn(35)



async def loeft_flaske():
    #Moves and turns
    await esben.move(230, speed=400)
    await esben.turn(85, speed=100)
    #Follow lines until it reads something closer than 10 cm.
    await esben.follow(200, aggressive=30, to_distance=80)
    #Moves 1 cm. from the bottle
    await esben.move(distance_sensor.distance(esben.distance_sensor)-10,speed=100)
    #Lifts bottle and moves
    await esben.lift_up()
    await esben.move(200)
    await esben.lift_down()
    #Drives away to show the bottle has been put down.
    await esben.move(-200)
    await runloop.sleep_ms(1000)
    await esben.move(200)
    await esben.lift_up()
    #Turns around to put the bottle on the maalskive
    await esben.turn(-178)
    await esben.move(880, speed=400)
    await esben.lift_down()
    await esben.move(-420, speed=400)
    await esben.turn(75)

async def over_vippe():
    await esben.follow(speed= 500, aggressive=23)
    await esben.turn(-3)
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(20)
    await esben.move(350, steering=-5 , speed=800)
    '''
    while motion_sensor.tilt_angles()[2] < 180-35:
        motor_pair.move(motor_pair.PAIR_1, motion_sensor.tilt_angles()[0], velocity=900)
        '''
    def _over_vippe():
        median_light = 15
        measure = color_sensor.reflection(esben.color_sensor)
        change = int((median_light - measure) * aggressive)
        if change > 0:
                motor_pair.move_tank(motor_pair.PAIR_1, speed-change, speed)
        elif change < 0:
            motor_pair.move_tank(motor_pair.PAIR_1, speed, speed+change)

        return motion_sensor.tilt_angles()[2] == 0

    for i in range(2):
        speed = 500
        aggressive = 10
        await runloop.until(_over_vippe)
        await esben.move(20, speed = 500)

async def vippe():
    await esben.move((2+6.6+15.4/2)*10+75)
    await esben.turn(-85, speed=250)
    for i in range(2):
        await over_vippe()
        await esben.move(425, speed=350)
        await esben.turn(80)
        await esben.follow(speed=600, aggressive=15)
        #await esben.move(10)
        await esben.turn(75, speed=250)

    await over_vippe()
    await esben.move(380, speed=200)
    await esben.turn(-85)

async def parrallel():
    await esben.turn(-20)
    await esben.move(380,speed=200)


async def maal_skive():
    await esben.move(230, speed=400)
    await esben.turn(-90)
    await esben.follow(speed=300)
    #Drives to the middle
    await esben.move(620,speed=300)
    #Turns to the direction-ish of the bottle
    await esben.turn(-33,speed=150)
    #Finds the bottle and
    await esben.find()
    await esben.lift_up()
    await esben.move(-520)
    await esben.lift_down()

    await esben.move(-200,speed=400)
    await esben.turn(45)
    await esben.move(-880,speed=400)
    await esben.turn(75)

async def om_flaske():
    await esben.turn(-40)
    await esben.move(720,10)
    #await esben.turn(20)


async def mur():
    def _pressed():
        motor_pair.move(motor_pair.PAIR_1, 0, velocity=-350)
        return force_sensor.pressed(esben.force_sensor)
    await esben.turn(10)
    await esben.move_to_distance(150, speed = 200)
    await esben.turn(110)
    await runloop.until(_pressed)
    await esben.move(40)
    await esben.turn(-40)
    await esben.move(535,-19)

async def om_flaske_2():
    await esben.turn(40)
    await esben.move(850,-10)
    #await esben.turn(-20)

async def landingsbane():
    def _landingsbane():
        motor_pair.move(motor_pair.PAIR_1, -100, velocity=100)
        return  -1400 > motion_sensor.tilt_angles()[0] >= -1800
    
    await runloop.until(_landingsbane)
    #await esben.turn(-13)
    await esben.move_to_distance(1350, speed=500)
    await esben.move(-160)

async def main():

    obstacles = {
        brudt_streg:    (500, 17),
        loeft_flaske:(500, 17),
        vippe:        (500, 15),
        parrallel:    (400, 10),
        maal_skive:    (400, 17),
        om_flaske:    (500, 17),
        mur:            (500, 16),
        om_flaske_2:    (400,10),
        landingsbane:(0, 10)
    }
    obstacle_list = [vippe, parrallel, maal_skive, om_flaske, mur,om_flaske_2,landingsbane]

    await esben.follow()
    for obstacle in obstacle_list:
        await obstacle()
        await esben.follow(*obstacles[obstacle])


runloop.run(main())