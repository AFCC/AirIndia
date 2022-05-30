import os

# AWS S3 credentials
s3_creds = {
    "access_key": "AKIAWVKQBF2LUPKH655D",
    "secret_key": "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",
    "bucket": "webscraping-permanent-bucket",
    "folder": "AirIndia/",
    "region": "ap-south-1"
}

# chrome download directory waiting time
dd_prefix = os.path.abspath(os.getcwd()) + '\\pdf_directory\\'

# pdf invoices and csv files
dump = dd_prefix + 'dump'

# csv for checking working credentials
creds = os.path.abspath(os.getcwd()) + '\\creds'

# chrome file download waiting time (in seconds)
waiting_time = 120

# target url to open in chrome
target_url = 'https://gst-ai.accelyakale.net/gstportal/login.htm'
search_url = 'https://gst-ai.accelyakale.net/gstportal/ui/ticket/TicketSearch.htm'

#sleep delay start and end (in seconds)
sd_s = 1
sd_e = 3

# cred checker dump
cred_dump = []