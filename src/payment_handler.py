import RPi.GPIO as GPIO
import time
from threading import Thread, Lock
from queue import Queue

class BillAcceptor:
    # Pulse mappings for different bills
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
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.bill_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Add event detection for the bill pulses
        GPIO.add_event_detect(self.bill_pin, GPIO.FALLING, 
                            callback=self._pulse_detected, 
                            bouncetime=50)  # 50ms debounce

    def _pulse_detected(self, channel):
        """Called when a pulse is detected on the bill pin"""
        current_time = time.time()
        
        with self.payment_lock:
            # If it's been longer than timeout since last pulse, reset count
            if (current_time - self.last_pulse_time) > self.pulse_timeout:
                self.pulse_count = 0
            
            self.pulse_count += 1
            self.last_pulse_time = current_time
            self.pulse_queue.put(self.pulse_count)

    def _process_pulses(self):
        """Process pulses in the background"""
        while self.running:
            try:
                pulse_count = self.pulse_queue.get(timeout=1.0)
                current_time = time.time()
                
                # Wait for pulse sequence to complete
                time.sleep(self.pulse_timeout)
                
                # If this is a valid bill pulse count
                if pulse_count in self.BILL_PULSE_MAP:
                    bill_info = self.BILL_PULSE_MAP[pulse_count]
                    with self.payment_lock:
                        self.received_amount += bill_info['value']
                        print(f"Received: {bill_info['description']} "
                              f"(₱{bill_info['value']:.2f})")
                        
                self.pulse_count = 0
                
            except Exception as e:
                if self.running:  # Only print if we're still supposed to be running
                    print(f"Error processing pulses: {e}")

    def start_payment_session(self, required_amount):
        """Start a new payment session"""
        with self.payment_lock:
            self.received_amount = 0.0
            self.pulse_count = 0
            self.running = True
            
        # Start the pulse processing thread
        self.process_thread = Thread(target=self._process_pulses)
        self.process_thread.start()
        
        return True

    def stop_payment_session(self):
        """Stop the current payment session"""
        self.running = False
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        
        return self.received_amount

    def get_current_amount(self):
        """Get the current received amount"""
        with self.payment_lock:
            return self.received_amount

    def cleanup(self):
        """Clean up GPIO on shutdown"""
        if self.running:
            self.stop_payment_session()
        GPIO.cleanup(self.bill_pin)


import RPi.GPIO as GPIO
import time
from threading import Thread, Lock
from queue import Queue

class BillAcceptor:
    # Pulse mappings for different bills
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
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.bill_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Add event detection for the bill pulses
        GPIO.add_event_detect(self.bill_pin, GPIO.FALLING, 
                            callback=self._pulse_detected, 
                            bouncetime=50)  # 50ms debounce

    def _pulse_detected(self, channel):
        """Called when a pulse is detected on the bill pin"""
        current_time = time.time()
        
        with self.payment_lock:
            # If it's been longer than timeout since last pulse, reset count
            if (current_time - self.last_pulse_time) > self.pulse_timeout:
                self.pulse_count = 0
            
            self.pulse_count += 1
            self.last_pulse_time = current_time
            self.pulse_queue.put(self.pulse_count)

    def _process_pulses(self):
        """Process pulses in the background"""
        while self.running:
            try:
                pulse_count = self.pulse_queue.get(timeout=1.0)
                current_time = time.time()
                
                # Wait for pulse sequence to complete
                time.sleep(self.pulse_timeout)
                
                # If this is a valid bill pulse count
                if pulse_count in self.BILL_PULSE_MAP:
                    bill_info = self.BILL_PULSE_MAP[pulse_count]
                    with self.payment_lock:
                        self.received_amount += bill_info['value']
                        print(f"Received: {bill_info['description']} "
                              f"(₱{bill_info['value']:.2f})")
                        
                self.pulse_count = 0
                
            except Exception as e:
                if self.running:  # Only print if we're still supposed to be running
                    print(f"Error processing pulses: {e}")

    def start_payment_session(self, required_amount):
        """Start a new payment session"""
        with self.payment_lock:
            self.received_amount = 0.0
            self.pulse_count = 0
            self.running = True
            
        # Start the pulse processing thread
        self.process_thread = Thread(target=self._process_pulses)
        self.process_thread.start()
        
        return True

    def stop_payment_session(self):
        """Stop the current payment session"""
        self.running = False
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        
        return self.received_amount

    def get_current_amount(self):
        """Get the current received amount"""
        with self.payment_lock:
            return self.received_amount

    def cleanup(self):
        """Clean up GPIO on shutdown"""
        if self.running:
            self.stop_payment_session()
        GPIO.cleanup(self.bill_pin)


class PaymentHandler:
    def __init__(self, coin_pin=17, bill_pin=27):
        self.coin_selector = CoinSelector(coin_pin)
        self.bill_acceptor = BillAcceptor(bill_pin)
        self.payment_lock = Lock()
        self.total_received = 0.0

    def start_payment_session(self, required_amount):
        """Start a new payment session accepting both coins and bills"""
        self.total_received = 0.0
        self.coin_selector.start_payment_session(required_amount)
        self.bill_acceptor.start_payment_session(required_amount)
        return True

    def get_current_amount(self):
        """Get the total amount received from both coins and bills"""
        with self.payment_lock:
            coin_amount = self.coin_selector.get_current_amount()
            bill_amount = self.bill_acceptor.get_current_amount()
            self.total_received = coin_amount + bill_amount
            return self.total_received

    def stop_payment_session(self):
        """Stop the payment session and return total amount received"""
        coin_amount = self.coin_selector.stop_payment_session()
        bill_amount = self.bill_acceptor.stop_payment_session()
        return coin_amount + bill_amount

    def cleanup(self):
        """Clean up both coin and bill acceptor GPIO pins"""
        self.coin_selector.cleanup()
        self.bill_acceptor.cleanup()


class CoinSelector:
    # Pulse mappings for different coins
    COIN_PULSE_MAP = {
        2: {'value': 1.0, 'description': 'Old 1 Peso'},
        3: {'value': 1.0, 'description': 'New 1 Peso'},
        5: {'value': 5.0, 'description': 'Old 5 Peso'},
        6: {'value': 5.0, 'description': 'New 5 Peso'},
        10: {'value': 10.0, 'description': 'Old 10 Peso'},
        11: {'value': 10.0, 'description': 'New 10 Peso'}
    }

    def __init__(self, coin_pin=17):  # Default to GPIO17
        self.coin_pin = coin_pin
        self.pulse_count = 0
        self.last_pulse_time = 0
        self.pulse_timeout = 0.5  # 500ms timeout between coin insertions
        self.running = False
        self.payment_lock = Lock()
        self.received_amount = 0.0
        self.pulse_queue = Queue()
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.coin_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Add event detection for the coin pulses
        GPIO.add_event_detect(self.coin_pin, GPIO.FALLING, 
                            callback=self._pulse_detected, 
                            bouncetime=50)  # 50ms debounce

    def _pulse_detected(self, channel):
        """Called when a pulse is detected on the coin pin"""
        current_time = time.time()
        
        with self.payment_lock:
            # If it's been longer than timeout since last pulse, reset count
            if (current_time - self.last_pulse_time) > self.pulse_timeout:
                self.pulse_count = 0
            
            self.pulse_count += 1
            self.last_pulse_time = current_time
            self.pulse_queue.put(self.pulse_count)

    def _process_pulses(self):
        """Process pulses in the background"""
        while self.running:
            try:
                pulse_count = self.pulse_queue.get(timeout=1.0)
                current_time = time.time()
                
                # Wait for pulse sequence to complete
                time.sleep(self.pulse_timeout)
                
                # If this is a valid coin pulse count
                if pulse_count in self.COIN_PULSE_MAP:
                    coin_info = self.COIN_PULSE_MAP[pulse_count]
                    with self.payment_lock:
                        self.received_amount += coin_info['value']
                        print(f"Received: {coin_info['description']} "
                              f"(₱{coin_info['value']:.2f})")
                        
                self.pulse_count = 0
                
            except Exception as e:
                if self.running:  # Only print if we're still supposed to be running
                    print(f"Error processing pulses: {e}")

    def start_payment_session(self, required_amount):
        """Start a new payment session"""
        with self.payment_lock:
            self.received_amount = 0.0
            self.pulse_count = 0
            self.running = True
            
        # Start the pulse processing thread
        self.process_thread = Thread(target=self._process_pulses)
        self.process_thread.start()
        
        return True

    def stop_payment_session(self):
        """Stop the current payment session"""
        self.running = False
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        
        return self.received_amount

    def get_current_amount(self):
        """Get the current received amount"""
        with self.payment_lock:
            return self.received_amount

    def cleanup(self):
        """Clean up GPIO on shutdown"""
        self.running = False
        GPIO.cleanup(self.coin_pin)

# Example usage:
if __name__ == "__main__":
    try:
        coin_selector = CoinSelector()
        print("Starting payment session... Insert coins.")
        coin_selector.start_payment_session(50.0)  # Example: ₱50 payment
        
        # Run for 30 seconds as a test
        time.sleep(30)
        
        final_amount = coin_selector.stop_payment_session()
        print(f"Session ended. Total received: ₱{final_amount:.2f}")
        
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        coin_selector.cleanup()