
async def maal_skive():
    await esben.move(230, speed=400)
    await esben.turn(-90)
    await esben.follow_line(speed=300)
    #Drives to the middle
    await esben.move(620,speed=300)
    #Turns to the direction-ish of the bottle
    await esben.turn(-35)
    #Finds the bottle and 
    await esben.find()
    await esben.lift_up()
    await esben.move(-520)
    await esben.lift_down()
    
    await esben.move(-200,speed=400)
    await esben.turn(45)
    await esben.move(-880,speed=400)
    await esben.turn(75)