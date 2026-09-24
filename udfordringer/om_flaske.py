async def om_flaske():

    print("vinkel1",motion_sensor.tilt_angles()[0])
    await esben.turn(40)
    print("vinkel2",motion_sensor.tilt_angles()[0])
    await esben.move(820,-10)
    await esben.turn(20)
    #await esben.turn(15)
    print("om flaske")