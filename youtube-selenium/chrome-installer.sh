#!/bin/bash
set -e

# הורדת הנתונים על הגרסאות האחרונות של Chrome ו-Chromedriver
latest_stable_json="https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

# קבלת הנתונים מה-JSON
json_data=$(curl -s "$latest_stable_json")
latest_chrome_linux_download_url="$(echo "$json_data" | jq -r ".channels.Stable.downloads.chrome[0].url")"
latest_chrome_driver_linux_download_url="$(echo "$json_data" | jq -r ".channels.Stable.downloads.chromedriver[0].url")"

# נתיבים להורדה
download_path_chrome_linux="/opt/chrome-headless-shell-linux.zip"
download_path_chrome_driver_linux="/opt/chrome-driver-linux.zip"

# יצירת תיקיות היעד אם הן לא קיימות
mkdir -p "/opt/chrome"
mkdir -p "/opt/chrome-driver"

# הורדת Chrome
echo "🔽 מוריד את Google Chrome..."
curl -Lo $download_path_chrome_linux $latest_chrome_linux_download_url
unzip -q $download_path_chrome_linux -d "/opt/chrome"
rm -rf $download_path_chrome_linux
echo "✅ Chrome הותקן בהצלחה."

# הזזת הקובץ Chrome למיקום הנכון
if [ -f "/opt/chrome/chrome-linux64/chrome" ]; then
    mv /opt/chrome/chrome-linux64/chrome /opt/chrome/chrome
    chmod +x /opt/chrome/chrome
    echo "✅ Chrome הועבר לנתיב הנכון: /opt/chrome/chrome"
else
    echo "❌ שגיאה: קובץ Chrome לא נמצא בתיקייה הצפויה!"
    ls -R /opt/chrome  # הדפסת מבנה התיקייה
    exit 1
fi

# הורדת Chromedriver
echo "🔽 מוריד את ChromeDriver..."
curl -Lo $download_path_chrome_driver_linux $latest_chrome_driver_linux_download_url
unzip -q $download_path_chrome_driver_linux -d "/opt/chrome-driver"
rm -rf $download_path_chrome_driver_linux
echo "✅ ChromeDriver הותקן בהצלחה."

# הגדרת הרשאות
chmod +x /opt/chrome-driver/chromedriver
echo "✅ Chromedriver מסומן כניתן להרצה."
