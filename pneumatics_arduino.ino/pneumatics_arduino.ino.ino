#define A 8
#define B 9
#define C 10

int a_state = LOW;
int b_state = LOW;
int c_state = LOW;

void toggle_state(int* state) {
  *state = (*state == LOW) ? HIGH : LOW;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(A, OUTPUT);
  pinMode(B, OUTPUT);
  pinMode(C, OUTPUT);
  Serial.println("Ready");
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()) {
    char byteIn = Serial.read();

    if (byteIn == 'a') {
      Serial.println("Hello");
      toggle_state(&a_state);
      Serial.println(a_state);
    }

    digitalWrite(A, a_state);
  }
}
