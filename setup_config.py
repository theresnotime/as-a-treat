with open('config.py', 'w') as f:
    f.write('API_URL = "https://mastodon.social"\n')
    f.write('ACCESS_TOKEN = "dummy_token"\n')
    f.write('FTP_HOST = "ftp.example.com"\n')
    f.write('FTP_USER = "user"\n')
    f.write('FTP_PASS = "pass"\n')
    f.write('DONT_UPLOAD_LOGS = True\n')
    f.write('ARCHIVE_INTERVAL_SECONDS = 86400\n')
    f.write('ARCHIVE_FILE_PATH = "archive.json"\n')
