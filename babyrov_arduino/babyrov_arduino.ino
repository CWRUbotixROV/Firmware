#define THRUSTER_PIN 9
#define MIN_VALUE 0
#define MAX_VALUE 100
#define SERIAL_WAIT_DELAY 10
#define BAUD_RATE 9600
#define LIGHT_PIN 4

int value = 0;

// A zero comes after every number sent over serial,
// so we need two zeros in a row to actually set the
// thruster to 0.
bool nonzero = true;

void setup() {
    Serial.begin(BAUD_RATE);

    // turn off the thruster
    digitalWrite(THRUSTER_PIN, LOW);
    
    digitalWrite(LIGHT_PIN, HIGH);
}

void loop() {
    // wait for something to come in the serial
    if (Serial.available()) {
        int tmpValue = Serial.parseInt();
        // check that the value received is valid
        if (tmpValue >= MIN_VALUE && tmpValue <= MAX_VALUE) {
            // turn on the thruster to the read value
            if (tmpValue != 0 || (tmpValue==0 && !nonzero)){
              value = tmpValue;
              Serial.print("New value: ");
              Serial.println(value);
              analogWrite(THRUSTER_PIN, value);
              nonzero = true;
            } else { //tmpValue==0 && nonzero
              nonzero = false;
            }
        }
    }
    // wait a short period before checking the serial again
    else {
//        analogWrite(THRUSTER_PIN, value);
        delay(SERIAL_WAIT_DELAY);
    }

}