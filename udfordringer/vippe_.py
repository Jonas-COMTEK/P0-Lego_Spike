async def over_vippe():
    await esben.follow_line(speed= 500, aggresive=23)
    await esben.turn(-2)
    motion_sensor.reset_yaw(0)

    while motion_sensor.tilt_angles()[2] < 180-35:
        motor_pair.move(motor_pair.PAIR_1, motion_sensor.tilt_angles()[0], velocity=800)
    for i in range(2):
        speed = 400
        aggresive = 17
        while motion_sensor.tilt_angles()[2] != 0:
            median_light = 15
            measure = color_sensor.reflection(esben.color_sensor_left)
            change = (median_light - measure)*int(speed/aggresive)
            if change > 0:
                motor_pair.move_tank(motor_pair.PAIR_1, speed-change, speed)
            elif change <0:
                motor_pair.move_tank(motor_pair.PAIR_1, speed, speed+change)
        await esben.move(20, speed = 500)
    
async def vippe():
    await esben.move((2+6.6+15.4/2)*10+75)
    await esben.turn(-65, speed=250)
    for j in range(2):
        await over_vippe()
        await esben.move(425, speed=350)
        await esben.turn(80)
        await esben.follow_line(speed=750, aggresive=23)
        await esben.move(10)
        await esben.turn(85, speed=250)

    await over_vippe()
    await esben.move(300, speed=350)
    await esben.turn(-85)