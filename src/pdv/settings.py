import os
from dotenv import load_dotenv

load_dotenv()

# Ttest
CONTROLLED_CATEGORY_NAME: str = 'Antibiotico'
ITEMS_PER_PAGE: int = int(os.getenv('PUVEFA_ITEMS_PER_PAGE', 25))
MAX_SEARCH_RESULTS: int = int(os.getenv('PUVEFA_MAX_SEARCH_RESULTS', 12))
MAX_PAYMENT_PER_SALE: int = int(os.getenv('PUVEFA_MAX_PAYMENT_PER_SALE', 10_000))
PRINTER_NAME: str = os.getenv('PUVEFA_PRINTER_NAME', 'termal-printer')
RECIPT_DIR: str = os.getenv('PUVEFA_RECIPT_DIR', '/tmp')
