def drej(vinkel, diameter):
    
    motion_sensor.reset_yaw(0)
    x = motion_sensor.tilt_angles()
    R = diameter
    print(R)
    R_wheel = math.sqrt(diameter**2-15.4**2)
    L = 12.5
    V_outer = 300
    R_inner = R_wheel-(L/2)
    R_outer = R_wheel+(L/2)
    V_inner = V_outer*((R_inner/R_outer))
    print(V_inner)
    # x[0] er yaw (drejning) i decigrader
    y = x[0]
    grader = y / 10
    
    print("vinkel2", vinkel, "grader",grader)
    if vinkel > 0:
        print("vinkel", vinkel, "grader",grader)
        while float(grader) < float(vinkel):
            x = motion_sensor.tilt_angles()
            y = x[0]
            grader = y / 10
            motor_pair.move_tank(motor_pair.PAIR_1, int(V_inner), V_outer)
    if vinkel < 0:
        print("vinkel2", vinkel, "grader",grader)
        while float(grader) > float(vinkel):
            x = motion_sensor.tilt_angles()
            y = x[0]
            grader = y / 10
            motor_pair.move_tank(motor_pair.PAIR_1, V_outer, int(V_inner))
    # Returner direkte om det er sandt eller falsk i stedet for at bruge await
    motor_pair.stop(motor_pair.PAIR_1)
    return True