import logging
from colorama import Fore, Style, init

# Initialize colorama
init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages."""
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        # Store the original level name
        original_levelname = record.levelname
        
        # Add color to the level name
        if original_levelname in self.COLORS:
            record.levelname = f"{self.COLORS[original_levelname]}{original_levelname}{Style.RESET_ALL}"
        
        # Add color to the message for WARNING and above
        if record.levelno >= logging.WARNING:
            record.msg = f"{self.COLORS[original_levelname]}{record.msg}{Style.RESET_ALL}"
        
        return super().format(record)

def setup_logging():
    """Set up logging with colored output."""
    # Create a handler that writes to stdout
    handler = logging.StreamHandler()
    
    # Create the colored formatter
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set the formatter for the handler
    handler.setFormatter(formatter)
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Remove any existing handlers
    root_logger.handlers = []
    
    # Add our handler
    root_logger.addHandler(handler)
    
    # Set the logging level
    root_logger.setLevel(logging.INFO) 