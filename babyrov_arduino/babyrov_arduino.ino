#include <Servo.h>

#define MOTOR_PIN 9
#define MIN_VALUE 0
#define MAX_VALUE 255
#define SERIAL_WAIT_DELAY 10

Servo motor;
void setup() {
    Serial.begin(9600);
    motor.attach(MOTOR_PIN);
    motor.writeMicroseconds(MIN_VALUE);// put your setup code here, to run onc
}

void loop() {
    if (Serial.available()) {
        unsigned char value = Serial.read();

        if (value >= MIN_VALUE && value <= MAX_VALUE) {
            motor.writeMicroseconds(value);
        }
    }
    else {
        delay(SERIAL_WAIT_DELAY);
    }

}
