const int relayPin = 8; // Match this to your physical wire in Pin 8

void setup() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH); // Start LOCKED
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'O') {
      digitalWrite(relayPin, LOW);  // Unlock
    } else if (command == 'C') {
      digitalWrite(relayPin, HIGH); // Lock
    }
  }
}