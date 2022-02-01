import logging
logging.basicConfig(filename="logfilename.log",filemode="w", level=logging.INFO)
name = 'Jyotirmay'
logging.info(f"\t\thello {name}")
logging.error(f"\t\thello {name}")
logging.warning(f"\thello {name}")
