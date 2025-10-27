# Electronics Vending Machine UI

A touch-friendly graphical user interface for an electronics component vending machine, built with Python and Tkinter. This application provides a simple interface for customers to browse and purchase items, as well as a password-protected admin panel for inventory management.

 <!-- Placeholder: Replace with a real screenshot URL -->

## Features

- **Kiosk Mode:**
  - Visually browse a grid of available electronic components with images.
  - View item details including name, description, price, and stock quantity.
  - Add items to a shopping cart.
  - Drag-to-scroll and mouse-wheel support for easy navigation.
- **Shopping Cart:**
  - View all items in the cart.
  - Adjust item quantities or remove items.
  - See a running grand total.
  - "Checkout" functionality (simulated).
- **Admin Panel:**
  - View a complete list of all items in the inventory.
  - **Add** new items to the inventory via a pop-up form.
  - **Edit** existing item details (name, description, price, quantity, image path).
  - **Remove** items from the inventory with a confirmation dialog.
  - Changes are saved directly to `item_list.json`.

## Installation

Follow these steps to get the application running on your local machine.

### Prerequisites

- Python 3.6 or newer. You can download it from python.org.
- `pip` (Python's package installer), which is usually included with Python.

### Steps

1.  **Clone the repository or download the source code.**
    If you have Git installed, you can use:

    ```sh
    git clone https://github.com/amalej/py-electronics-vending-machine.git
    cd py-electronics-vending-machine
    ```

2.  **Create and activate a virtual environment.**
    It's highly recommended to use a virtual environment to keep dependencies isolated.

    - On **Windows**:
      ```sh
      python -m venv venv
      .\venv\Scripts\activate
      ```
    - On **macOS and Linux**:
      ```sh
      python3 -m venv venv
      . /venv/bin/activate
      ```

3.  **Install the required dependencies.**
    Run the following command in your terminal. This will install the `Pillow` library, which is needed for image handling.
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the application, navigate to the `src` directory and execute the `main.py` script from the project root:

```sh
python src/main.py
```

The application will start in fullscreen mode, presenting the Kiosk/Admin selection screen.

## Kiosk header/footer configuration

When running in kiosk mode the UI now shows a fixed top header (2.5 inches tall) with the machine name "RAON" and subtitle, and a fixed bottom footer (1 inch tall) showing the group members. These sizes are calculated from your display's pixel dimensions and the physical diagonal (default 13.3").

You can configure the physical diagonal and the footer text in `config.json`:

- `display_diagonal_inches`: (number) physical diagonal size of the display in inches (default: 13.3)
- `group_members`: an array of strings that will be displayed in the footer (e.g. `["Alice","Bob","Carol"]`).

Edit `config.json` and restart the app to see changes appear in kiosk mode.

Alternatively you can edit these values from inside the app: open the **Admin** screen and click **Kiosk Config**. From there you can change the machine name, subtitle, choose a header logo image, set the display diagonal (in inches), and edit the list of group members. Saving writes `config.json` and updates the kiosk header/footer immediately.

## Coin acceptor (Allan Universal 123A-Pro) — wiring & testing

This project includes support for coin acceptors. If you're using the Allan Universal 123A-Pro model (the one with 4 pins: `12VDC`, `COIN`, `GND`, and `COUNTER`) follow the wiring and test instructions below.

Parts you'll need
- Raspberry Pi (any model with 40-pin GPIO header)
- Allan Universal 123A-Pro coin acceptor
- 12V DC power supply (capable of at least 1 A)
- Jumper wires (male/female as needed)
- Common ground between Pi and coin acceptor (connect coin acceptor GND to Pi GND)
- Optional: small breadboard for tidy wiring

Wiring (pin names on Allan 123A-Pro -> Raspberry Pi / power)

 - 12VDC (Allan)  ->  12V power supply positive (+)
 - GND (Allan)    ->  12V power supply negative (-) AND Raspberry Pi GND (any GND pin, e.g., Pin 6)
 - COIN (Allan)   ->  Raspberry Pi GPIO17 (BCM 17, physical Pin 11)
 - COUNTER (Allan)->  Optional (not required for basic operation)

Notes:
- Do not power the Allan coin acceptor from the Raspberry Pi 5V or 3.3V rails — it requires 12V.
- The COIN output from Allan is suitable to connect directly to a Pi GPIO (the acceptor provides a pulled-up/pulled-down signal and internal isolation). Always confirm your model's documentation first.

Programming the Allan 123A-Pro

1. Power the coin acceptor (12V and GND connected).
2. Locate the programming button on the coin acceptor (refer to the acceptor's manual).
3. Enter programming mode (usually press-and-hold the programming button until the LED blinks).
4. For each denomination you want the acceptor to recognise, insert the coin several times as required by the acceptor (many acceptors want 3–10 samples per coin type).
5. Press the programming button to move to the next coin type.
6. Save and exit programming mode (typically press-and-hold or follow manufacturer instructions).

Testing with this project

1. Place the Raspberry Pi and coin acceptor wiring as described above.
2. From the project root on the Raspberry Pi, run the test script:

```sh
python src/test_coin_acceptor.py
```

3. Insert coins. The test program will print the received amount each time a coin is detected.

Integration notes

- The code includes `src/coin_handler.py` (Allan 123A-Pro specific) and a `PaymentHandler` wrapper in `src/payment_handler.py` that uses both the coin and bill acceptors. `PaymentHandler.get_current_amount()` returns the sum of coins and bills received.
- If you plan to use the bill acceptor as well, wire its signal to the `bill_pin` configured in `payment_handler.py` (default BCM 27 / physical pin 13).

Safety

- Always disconnect power before changing wiring.
- Avoid connecting 12V directly to any Raspberry Pi pin — only connect the acceptor's COIN signal and common GND to the Pi.

