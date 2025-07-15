"""Module to import logging"""
import logging
import sys

def configure_logging():
    """Information about logging default"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
