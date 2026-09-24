
async def loeft_flaske():
    #Moves and turns
    await esben.move(230, speed=400)
    await esben.turn(90, speed=100)
    #Follow lines until it reads something closer than 10 cm.
    await esben.follow_line(300, to_distance=100)
    #Moves 1 cm. from the bottle
    await esben.move(100-10)
    #Lifts bottle and moves
    await esben.lift_up()
    await esben.move(200)
    await esben.lift_down()
    #Drives away to show the bottle has been put down.
    await esben.move(-200)
    await runloop.sleep_ms(1000)
    await esben.move(200)
    await esben.lift_up()
    #Turns around to put the bottle on maalskiven 
    await esben.turn(-178)
    await esben.move(880, speed=400)
    await esben.lift_down()
    await esben.move(-370, speed=400)
    await esben.turn(90)