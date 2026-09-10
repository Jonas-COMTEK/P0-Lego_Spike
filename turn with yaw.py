from hub import light_matrix, motion_sensor
import runloop

# Fjern 'async' her - det skal være en helt almindelig funktion
def drej(vinkel):
    x = motion_sensor.tilt_angles()
    # x[0] er yaw (drejning) i decigrader
    y = x[0]
    grader = y / 10

    # Returner direkte om det er sandt eller falsk i stedet for at bruge await
    return grader > float(vinkel)

async def main():
    motion_sensor.reset_yaw(0)

    # Nu spørger runloop en almindelig funktion igen og igen, indtil den returnerer True
    await runloop.until(lambda: drej(45))
    print('graderne skulle gerne være 45',motion_sensor.tilt_angles())
    await light_matrix.write("Hi!")

runloop.run(main())