from hub import light_matrix, port
import runloop
import color_sensor
import color


def move_cycle():
    return color_sensor.color(port.A) is color.RED


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
