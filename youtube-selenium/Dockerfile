FROM amazon/aws-lambda-python:3.12

# התקנת ספריות נדרשות עבור Chrome ו-Chromedriver
RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm jq unzip

# התקנת Chrome ו-Chromedriver
COPY ./chrome-installer.sh /opt/chrome-installer.sh
RUN chmod +x /opt/chrome-installer.sh && /opt/chrome-installer.sh

# התקנת Selenium
RUN pip install selenium

# העתקת קובץ הקוד של Lambda
COPY lambda_function.py /var/task/

# הפעלת Lambda
CMD [ "lambda_function.lambda_handler" ]
