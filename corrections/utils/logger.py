class color_text:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

   CMS_yellow = '#F5BB54'
   CMS_green = '#607641' 

def print_error(message, logger = None):
   print(f"{color_text.RED}[ERROR]{color_text.END} {message}")
   if logger: logger.write(message+'\n')
def print_warning(message, logger = None):
   print(f"{color_text.YELLOW}[WARNING]{color_text.END} {message}")
   if logger: logger.write(message+'\n')
def print_info(message, logger = None):
   print(f"{color_text.BLUE}[INFO]{color_text.END} {message}")
   if logger: logger.write(message+'\n')
def print_success(message, logger = None):
   print(f"{color_text.GREEN}[DONE!]{color_text.END} {message}")
   if logger: logger.write(message+'\n')
def print_bold(message, logger = None):
   print(f"{color_text.BOLD}{message}{color_text.END}")
   if logger: logger.write(message+'\n')
def print_addition(message, logger = None):
   print(f"{color_text.BOLD}[+]{color_text.END} {message}")
   if logger: logger.write(message+'\n')
def print_exe(message, logger = None):
   print(f"{color_text.GREEN}[EXE >]{color_text.END} {message}")
   if logger: logger.write(message+'\n')