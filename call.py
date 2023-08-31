import smtplib
from email.mime.text import MIMEText

msg = MIMEText('Test from local')
msg['Subject'] = 'Test Email'
msg['From'] = 'xllxlex@gmail.com'
msg['To'] = 'xllxlex@gmail.com'

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('xllxlex@gmail.com', 'ksjjgnrtcflzqgok')
server.send_message(msg)  # Pass the MIMEText object here
server.quit()
