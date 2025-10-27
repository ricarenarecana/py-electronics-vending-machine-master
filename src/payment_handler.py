from threading import Lock
from coin_handler import CoinAcceptor

class PaymentHandler:
    """Payment handler that manages the Allan 123A-Pro coin acceptor."""
    def __init__(self, coin_pin=17, counter_pin=None):
        """Initialize the payment handler with an Allan 123A-Pro coin acceptor.
        
        Args:
            coin_pin (int): GPIO pin number (BCM) for the coin signal
            counter_pin (int, optional): GPIO pin for the counter signal if used
        """
        self.coin_acceptor = CoinAcceptor(coin_pin=coin_pin, counter_pin=counter_pin)
        self._lock = Lock()
        self._callback = None  # Optional callback for UI updates

    def start_payment_session(self, required_amount=None, on_payment_update=None):
        """Start a new payment session.
        
        Args:
            required_amount (float, optional): Target amount to collect
            on_payment_update (callable, optional): Callback(amount) when coins received
        """
        self._callback = on_payment_update
        self.coin_acceptor.reset_amount()
        return True

    def get_current_amount(self):
        """Get the total amount received in the current session."""
        with self._lock:
            return self.coin_acceptor.get_received_amount()

    def stop_payment_session(self):
        """Stop the current payment session and return total received."""
        amount = self.coin_acceptor.get_received_amount()
        self.coin_acceptor.reset_amount()
        self._callback = None
        return amount

    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            self.coin_acceptor.cleanup()
        except Exception:
            pass
