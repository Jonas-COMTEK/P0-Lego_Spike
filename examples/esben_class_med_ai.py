from hub import light_matrix, port, motion_sensor
import motor
import runloop
import distance_sensor
import color_sensor
import motor_pair
import math
import color

MOTOR_LEFT = port.B
MOTOR_RIGHT = port.F

class Esben:
    def __init__(self, motor_left, motor_right, motor_lift, color_sensor_left, color_sensor_right, distance_sensor):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.motor_lift = motor_lift
        self.color_sensor_left = color_sensor_left
        self.color_sensor_right = color_sensor_right
        self.distance_sensor = distance_sensor

        motor_pair.pair(motor_pair.PAIR_1, self.motor_left, self.motor_right)

    async def follow(self, speed=15, reflection_sensitivity=7):
        def _follow():
            motor_pair.move_tank(motor_pair.PAIR_1,
                color_sensor.reflection(self.color_sensor_left) * speed,
                color_sensor.reflection(self.color_sensor_right) * speed)

            return (color_sensor.reflection(self.color_sensor_left) < reflection_sensitivity
                and color_sensor.reflection(self.color_sensor_right) < reflection_sensitivity
                and color_sensor.color(self.color_sensor_left) == color.BLACK
                and color_sensor.color(self.color_sensor_right) == color.BLACK)

        await runloop.until(_follow)
        motor_pair.stop(motor_pair.PAIR_1)

    async def follow_ai(self, base_speed=300, gain=1.2):
        def _follow():
            # 1. Læs sensorværdier (typisk mellem 0 og 100)
            left_light = color_sensor.reflection(self.color_sensor_left)
            right_light = color_sensor.reflection(self.color_sensor_right)

            print(left_light, right_light)
            runloop.sleep_ms(200)

            # 2. Beregn fejlen (hvor langt er vi fra midten?)
            # Hvis fejlen er positiv, skal vi dreje til den ene side. Hvis negativ, til den anden.
            error = left_light - right_light

            # 3. Beregn styresignal (gain bestemmer hvor aggressivt robotten retter op)
            turn_rate = error * gain

            # 4. Juster motorerne (Konstant fart +/- sving-hastighed)
            motor_pair.move_tank(
                motor_pair.PAIR_1,
                int(base_speed + turn_rate),
                int(base_speed - turn_rate)
            )

            # 5. Stop-betingelse: Stop når BEGGE sensorer ser sort (f.eks. en tværlinje)
            # Vi tjekker både lysrefleksion (< 15) OG farve-id for en sikkerheds skyld
            is_left_black = left_light < 7 and color_sensor.color(self.color_sensor_left) == color.BLACK
            is_right_black = right_light < 7 and color_sensor.color(self.color_sensor_right) == color.BLACK

            return is_left_black and is_right_black

        # Kør loopet asynkront indtil _follow returnerer True
        await runloop.until(_follow)

        # Stop motorerne helt, når linjen er slut / tværlinjen rammes
        motor_pair.stop(motor_pair.PAIR_1)

    async def move(self, distance):
        motor_pair.move_for_degrees(motor_pair.PAIR_1, int((360 * distance) / (5.5 * math.pi)), 0)

    async def turn(self, degrees, radius):
        pass

esben = Esben(port.F, port.B, port.D, port.E, port.A, port.C)

def move_straight():
    motor_pair.move(motor_pair.PAIR_1, motion_sensor.tilt_angles()[0])
    return False


async def main():
    await esben.follow_ai()

runloop.run(main())
