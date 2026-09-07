from hub import light_matrix, port
import runloop
import color_sensor
import color
import motor_pair

#Pairing the two motors
motor_pair.pair(motor_pair.PAIR_1, port.F, port.B)

#Speed constant multiplies in the speed calculation
speed = 12


def move_cycle():
    """
    Function for the forward movement.
    The speed is set by the light-reflection value measured by the same-side sensor multiplied by the speed variable
    It returns True if the light-reflection is low and the sensor measures the color black
    """
    motor_pair.move_tank(motor_pair.PAIR_1, color_sensor.reflection(port.E)*speed, color_sensor.reflection(port.A)*speed)
    return color_sensor.reflection(port.E) < 7 and color_sensor.reflection(port.A) < 7 and color_sensor.color(port.E) is color.BLACK and color_sensor.color(port.A) is color.BLACK

async def obstacle_1():
    await light_matrix.write("HAIIII")
    print("obstacle_1")

async def obstacle_2():
    await light_matrix.write("HELLOO")
    print("obstacle_2")

async def main():
    obstacles = [obstacle_1, obstacle_2]

    for obstacle in obstacles:
        await runloop.until(move_cycle)
        await obstacle()

    print("done!")

runloop.run(main())