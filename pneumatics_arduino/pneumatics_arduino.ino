#define SMART_HOOK_PIN 8
#define JUMBO_HOOK_PIN 9
#define SMART_HOOK_CHAR 'a'
#define JUMBO_HOOK_CHAR 'd'

int SMART_HOOK_PIN_state = LOW;
int JUMBO_HOOK_PIN_state = LOW;

void toggle_state(int* state) {
  *state = (*state == LOW) ? HIGH : LOW;
}

void setup() {
  // startup the serial
  Serial.begin(9600);

  // setup the pins
  pinMode(SMART_HOOK_PIN, OUTPUT);
  pinMode(JUMBO_HOOK_PIN, OUTPUT);

  // notidy the serial out that the arduino is ready
  Serial.println("Ready");
}

void loop() {
  // only read the serial if it is ready
  if (Serial.available()) {
    char byteIn = Serial.read();

    // toggle the smart hook if we read the smart hook character
    if (byteIn == SMART_HOOK_CHAR) {
      smart_hook_state = !smart_hook_state;
      digitalWrite(SMART_HOOK_PIN, SMART_HOOK_PIN_state);
    }
    // toggle the jumbo hook if we read the smart hook character
    if (byteIn == JUMBO_HOOK_CHAR) {
      jumbo_hook_state = !jumbo_hook_state;
      digitalWrite(JUMBO_HOOK_PIN, JUMBO_HOOK_PIN_state);
    }


  }
}
