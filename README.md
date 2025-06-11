# Visvim Web Scraper and Automated Checkout System

A powerful automation tool for purchasing products from the Visvim online store. This application provides a user-friendly GUI interface to manage product purchases, handle PayPal payments, and schedule automated checkouts.

## Features

- **User Authentication**: Secure login system for Visvim store access
- **Product Management**: 
  - Add multiple products with specific colors and sizes
  - Real-time availability checking
  - Dynamic product list management
- **Payment Processing**:
  - PayPal account integration
  - Credit card payment support
  - Automated payment form filling
- **Scheduled Checkout**: Set specific times for automated purchases
- **Real-time Status Updates**: Monitor the progress of your purchases
- **Error Handling**: Comprehensive error handling and user feedback

## Requirements

- Python 3.7+
- Chrome Browser
- Required Python packages:
  ```
  selenium
  undetected_chromedriver
  webdriver_manager
  tkinter
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd [repository-name]
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Chrome browser is installed on your system

## Usage

1. Run the application:
   ```bash
   python GUI.py
   ```

2. Login with your Visvim store credentials

3. Add products:
   - Enter product IDs
   - Select colors and sizes
   - Add multiple products as needed

4. Configure payment details:
   - Enter PayPal credentials
   - Add credit card information
   - Fill in billing details

5. Set checkout time (optional):
   - Use format: YYYY-MM-DD HH:MM:SS
   - Leave empty for immediate checkout

6. Click "Run Scraper" to start the automated process

## Project Structure

- `GUI.py`: Main application interface
  - Login system
  - Product management
  - Payment configuration
  - Status monitoring

- `Scraper.py`: Core automation functionality
  - Web scraping
  - Cart management
  - Payment processing
  - Error handling

## Security Considerations

- All sensitive information (passwords, credit card details) is handled securely
- No data is stored locally
- Secure communication with payment gateways

## Error Handling

The application includes comprehensive error handling for:
- Network issues
- Invalid credentials
- Product unavailability
- Payment processing errors
- Timeout scenarios

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Users are responsible for complying with the terms of service of the Visvim online store and PayPal. 