import RPi.GPIO as GPIO
import time
from threading import Thread, Lock
from queue import Queue

from coin_handler import CoinAcceptor


class BillAcceptor:
    """Handles bill acceptor pulses and maps them to bill values.

    The bill acceptor used by the project emits a series of pulses per
    bill; the mapping below should match the hardware's configuration.
    """
    BILL_PULSE_MAP = {
        4: {'value': 20.0, 'description': '20 Peso Bill'},
        8: {'value': 50.0, 'description': '50 Peso Bill'},
        12: {'value': 100.0, 'description': '100 Peso Bill'},
        16: {'value': 200.0, 'description': '200 Peso Bill'},
        20: {'value': 500.0, 'description': '500 Peso Bill'},
        24: {'value': 1000.0, 'description': '1000 Peso Bill'}
    }

    def __init__(self, bill_pin=27):  # Default to GPIO27
        self.bill_pin = bill_pin
        self.pulse_count = 0
        self.last_pulse_time = 0
        self.pulse_timeout = 1.0  # 1 second timeout between bill insertions
        self.running = False
        self.payment_lock = Lock()
        self.received_amount = 0.0
        self.pulse_queue = Queue()

        # Initialize GPIO input for bill pulses
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.bill_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Add event detection for falling pulses
        GPIO.add_event_detect(self.bill_pin, GPIO.FALLING,
                              callback=self._pulse_detected,
                              bouncetime=50)

    def _pulse_detected(self, channel):
        current_time = time.time()

        with self.payment_lock:
            if (current_time - self.last_pulse_time) > self.pulse_timeout:
                self.pulse_count = 0

            self.pulse_count += 1
            self.last_pulse_time = current_time
            self.pulse_queue.put(self.pulse_count)

    def _process_pulses(self):
        while self.running:
            try:
                pulse_count = self.pulse_queue.get(timeout=1.0)
                # wait a short time to allow pulse sequence to finish
                time.sleep(self.pulse_timeout)

                if pulse_count in self.BILL_PULSE_MAP:
                    bill_info = self.BILL_PULSE_MAP[pulse_count]
                    with self.payment_lock:
                        self.received_amount += bill_info['value']
                        print(f"Received: {bill_info['description']} (₱{bill_info['value']:.2f})")

                self.pulse_count = 0

            except Exception as e:
                if self.running:
                    print(f"Error processing bill pulses: {e}")

    def start_payment_session(self, required_amount=None):
        with self.payment_lock:
            self.received_amount = 0.0
            self.pulse_count = 0
            self.running = True

        self.process_thread = Thread(target=self._process_pulses)
        self.process_thread.start()
        return True

    def stop_payment_session(self):
        self.running = False
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        return self.received_amount

    def get_current_amount(self):
        with self.payment_lock:
            return self.received_amount

    def cleanup(self):
        if self.running:
            self.stop_payment_session()
        try:
            GPIO.remove_event_detect(self.bill_pin)
        except Exception:
            pass


class PaymentHandler:
    """Unified payment handler that wraps coin and bill acceptors."""
    def __init__(self, coin_pin=17, bill_pin=27, counter_pin=None):
        # coin_handler.CoinAcceptor provides get_received_amount(), reset_amount(), cleanup()
        self.coin_acceptor = CoinAcceptor(coin_pin=coin_pin, counter_pin=counter_pin)
        self.bill_acceptor = BillAcceptor(bill_pin=bill_pin)
        self._lock = Lock()

    def start_payment_session(self, required_amount=None):
        # Reset coin counter and start bill processing thread
        self.coin_acceptor.reset_amount()
        self.bill_acceptor.start_payment_session(required_amount)
        return True

    def get_current_amount(self):
        with self._lock:
            coins = self.coin_acceptor.get_received_amount()
            bills = self.bill_acceptor.get_current_amount()
            return coins + bills

    def stop_payment_session(self):
        bills = self.bill_acceptor.stop_payment_session()
        coins = self.coin_acceptor.get_received_amount()
        self.coin_acceptor.reset_amount()
        return coins + bills

    def cleanup(self):
        try:
            self.coin_acceptor.cleanup()
        except Exception:
            pass
        try:
            self.bill_acceptor.cleanup()
        except Exception:
            pass
