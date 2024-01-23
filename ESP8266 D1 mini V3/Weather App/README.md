# Amazing Weather Display

## Overview

Amazing Weather Display is an Arduino-based project that fetches weather information from OpenWeatherMap API and displays it on an SSD1306 OLED screen. The application provides current weather and forecast data for a specified location.

## Components Needed

To set up the Amazing Weather Display, you will need the following components:

1. **ESP8266 Board:** The application is designed to work with ESP8266-based microcontrollers.

2. **SSD1306 OLED Display:** A 128x64 monochrome OLED display is required for visualizing weather information.

3. **WiFi Module:** Ensure your ESP8266 board has a working WiFi module to connect to the internet.

4. **OpenWeatherMap API Key:** Obtain a free API key from [OpenWeatherMap](https://openweathermap.org/) to access weather data.

5. **Arduino Libraries:**
   - ESP8266WiFi
   - ESP8266HTTPClient
   - ArduinoJson
   - Wire
   - Adafruit_GFX
   - Adafruit_SSD1306

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/amazing-weather-display.git
   
2. **Install Arduino Libraries:**
- Open Arduino IDE.
- Go to Sketch -> Include Library -> Manage Libraries...
- Search for each library mentioned above and install them.

3. **Configure Credentials:**
- Open the Arduino sketch (amazing_weather.ino).
- Replace the placeholder values in the code with your WiFi SSID, password, and OpenWeatherMap API key.

3. **Upload the Code:**
- Connect your ESP8266 board to your computer.
- Select the correct board and port in Arduino IDE.
- Click the "Upload" button to flash the code to your board.

4. **Connect OLED Display:**
- Connect the SSD1306 OLED display to the I2C pins on your ESP8266 board.

5. **Power On:**
- Power on your ESP8266 board.

6. **View Weather Information:**
- The OLED display should now show weather information for your specified location.

## Acknowledgments
- Special thanks to OpenWeatherMap for providing the weather data API.
- Thanks to the Arduino community for the libraries and support.

Feel free to contribute, report issues, or suggest improvements!