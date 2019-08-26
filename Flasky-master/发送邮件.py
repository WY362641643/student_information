from flask import Flask
from flask.ext.mail import Mail
from flask.ext.mail import Message
import os

app = Flask(__name__)
app.config.update(
    DEBUG = True,
    MAIL_SERVER='smtp.qq.com',
    MAIL_PROT=25,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = '362641643@qq.com',
    MAIL_PASSWORD = 'wyysvc',
    MAIL_DEBUG = True
)

mail = Mail(app)

@app.route('/')
def index():
# sender 发送方哈，recipients 邮件接收方列表
    msg = Message("Hi!This is a test ",sender='362641643@qq.com', recipients=['504629278@qq.com'])
# msg.body 邮件正文 
    msg.body = "This is a first email"
# msg.attach 邮件附件添加
# msg.attach("文件名", "类型", 读取文件）
    print('等待发送')
    with app.open_resource("D:\ss70622131955_h4eZS.thumb.700_0.jpg") as fp:
        msg.attach("image.jpg", "image/jpg", fp.read())

    mail.send(msg)
    print("Mail sent")
    return "Sent"

if __name__ == "__main__":
    app.run()
