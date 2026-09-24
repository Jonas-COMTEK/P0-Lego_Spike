async def brudt_streg():
    await esben.move(200,15)
    await esben.follow_line(speed = 500)
    await esben.move(350,-15)
    await esben.turn(20)