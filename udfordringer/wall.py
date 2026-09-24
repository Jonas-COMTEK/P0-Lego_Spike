async def mur():
    await esben.turn(10)
    await esben.move_to_distance(100, speed = 200)
    await esben.turn(117)

    while not force_sensor.pressed(esben.force_sensor):
        motor_pair.move_tank(motor_pair.PAIR_1,-350, -350)
    await esben.move(40)
    await esben.turn(-45)
    await esben.move(550,-19)