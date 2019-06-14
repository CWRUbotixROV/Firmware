#include <Servo.h>

#define THRUSTER_PIN 9
#define MIN_VALUE 0
#define MAX_VALUE 255
#define SERIAL_WAIT_DELAY 10
#define BAUD_RATE 9600

Servo motor;
void setup() {
    Serial.begin(BAUD_RATE);

    // setup the thruster
    motor.attach(THRUSTER_PIN);

    // turn off the thruster
    motor.writeMicroseconds(MIN_VALUE);
}

void loop() {
    // wait for something to come in the serial
    if (Serial.available()) {
        unsigned char value = Serial.read();

        // check that the value received is valid
        if (value >= MIN_VALUE && value <= MAX_VALUE) {
            // turn on the thruster to the read value
            motor.writeMicroseconds(value);
        }
    }
    // wait a short period before checking the serial again
    else {
        delay(SERIAL_WAIT_DELAY);
    }

}
