from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
import time
import boto3
import json


def lambda_handler():
    # הגדרת הדפדפן
    driver = webdriver.Chrome()

    print("מנסה להיכנס למערכת...")
    driver.get('https://e-services.clalit.co.il/onlinewebquick/nvgq/tamuz/he-il')

    # הזנת תעודת זהות ושנת לידה
    id_input = driver.find_element(By.ID, 'ctl00_ctl00_cphBody_bodyContent_ucQuickLogin_userId')
    birth_year_input = driver.find_element(By.ID, 'ctl00_ctl00_cphBody_bodyContent_ucQuickLogin_userYearOfBirth')
    id_input.send_keys('23594526')
    birth_year_input.send_keys('1968')
    driver.find_element(By.ID, 'ctl00_ctl00_cphBody_bodyContent_ucQuickLogin_btnLogin_lblInnerText').click()
    # המתנה לטעינת הדף
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

    # בדיקת iframes
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    print(f"נמצאו {len(iframes)} iframes בדף.")

    # חיפוש הכפתור בתוך iframes
    for index, iframe in enumerate(iframes):
        print(f"בודק Iframe {index}...")
        driver.switch_to.frame(iframe)
        try:
            profession_button = driver.find_element(By.ID, 'ProfessionVisitButton')
            print("הכפתור נמצא בתוך iframe!")
            profession_button.click()
            break  # מצאנו את הכפתור, אין צורך לבדוק עוד iframes
        except:
            driver.switch_to.default_content()  # חזרה למסך הראשי אם לא נמצא

    # חזרה למסך הראשי בסיום הבדיקה
    driver.switch_to.default_content()

    # סיום
    print("סיום הבדיקה.")

    # המתנה לטעינת הדף לאחר הלחיצה
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

    # בדיקת כל ה-iframes
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    print(f"נמצאו {len(iframes)} iframes לאחר הלחיצה.")

    specialization_dropdown = None
    selected_iframe = None  # נשמור את ה-iframe המתאים

    for index, iframe in enumerate(iframes):
        driver.switch_to.frame(iframe)
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'SelectedSpecializationCode')))
            elements = driver.find_elements(By.ID, 'SelectedSpecializationCode')

            if elements:
                for elem in elements:
                    print(f"נמצא אלמנט: {elem.get_attribute('outerHTML')}")

                # נוודא שזה באמת select
                if elements[0].tag_name.lower() == "select":
                    specialization_dropdown = elements[0]
                    selected_iframe = iframe  # שומרים את ה-iframe שבו מצאנו את האלמנט
                    print(f"סוג הרפואה נמצא בתוך iframe {index}")
                    break
        except Exception as e:
            print(f"שגיאה בבדיקת iframe {index}: {e}")
            driver.switch_to.default_content()  # חזרה לדף הראשי

    # אם האלמנט נמצא בתוך iframe, נישאר בו לעבודה עליו
    if specialization_dropdown:
        print(f"tag_name: {specialization_dropdown.tag_name}")  # לוודא שזה באמת select
        Select(specialization_dropdown).select_by_value('58')
        print("✅ נבחרה התמחות: אורתופדיה.")
    else:
        print("❌ שגיאה: לא ניתן לבחור התמחות, השדה לא נמצא.")

    wait = WebDriverWait(driver, 10)

    # הזנת עיר
    city_input = wait.until(EC.presence_of_element_located((By.ID, 'SelectedCityName')))
    city_input.clear()
    city_input.send_keys('תל אביב - יפו')


    # הזנת שם רופא
    doctor_input = wait.until(EC.presence_of_element_located((By.ID, 'SelectedDoctorName')))
    doctor_input.clear()
    doctor_input.send_keys('זאב אשכול')


    # לחיצה על כפתור חיפוש
    search_button = wait.until(EC.presence_of_element_located((By.ID, 'searchBtnSpec')))
    search_button.click()

    print("בודק זמינות תורים...")
    appointments_list = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'diary'))
    )

    # תאריך נוכחי
    today = datetime.now()
    available_appointments = []

    # בדיקת כל תור
    for appointment in appointments_list:
        try:
            # ננסה למצוא את שם הרופא, ואם לא נמצא - נשים טקסט ברירת מחדל
            try:
                doctor_name = appointment.find_element(By.CLASS_NAME, 'doctorName').text
            except:
                doctor_name = "לא צוין רופא"
            date_element = appointment.find_element(By.CLASS_NAME, 'visitDateTime')
            date_text = date_element.find_element(By.TAG_NAME, 'span').text
            location = appointment.find_element(By.CLASS_NAME, 'clinicDetails').text

            appointment_date = datetime.strptime(date_text, "%d.%m.%Y")

            if today <= appointment_date <= today + timedelta(days=30):
                #print(f"תור זמין:\nרופא: {doctor_name}\nתאריך: {date_text}\nמיקום: {location}")
                available_appointments.append({
                    "doctor": doctor_name,
                    "date": date_text,
                    "location": location
                })

        except Exception as e:
            print(f"שגיאה בעיבוד תור: {e}")

    # שמירת התוצאות ל-S3 אם נמצאו תורים
    if available_appointments:
        save_to_s3(available_appointments, "appointments.json")
        message = f"תור פנוי:\nרופא: {doctor_name}\nתאריך: {appointment_date}\nמיקום: {location}"

        # הזן את מספר הטלפון בפורמט הבינלאומי
        phone_number = "+972544609312"  # מספר טלפון (החלף אותו במספר שלך)

        send_sms_alert(message, phone_number)
    else:
        print("לא נמצאו תורים זמינים.")

    print("סיום הסקריפט בהצלחה.")
    # סגירת הדפדפן
    driver.quit()


# הגדרת חיבור ל-S3
s3 = boto3.client('s3')
bucket_name = "my-appointments-bucket"


# פונקציה לשמירת נתונים ב-S3
def save_to_s3(data, file_name):
    s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=json.dumps(data, indent=4, ensure_ascii=False),
        ContentType='application/json'
    )
    print(f"📁 הנתונים נשמרו בהצלחה ל-S3: {file_name}")


# יצירת חיבור ל-SNS
sns = boto3.client('sns')
topic_arn = "arn:aws:sns:your-region:your-account-id:AppointmentsAlert"  # ARN של ה-topic שלך


# פונקציה לשליחת התראה ב-SMS
def send_sms_alert(message, phone_number):
    response = sns.publish(
        PhoneNumber=phone_number,  # מספר הטלפון שיקבל את ההתראה
        Message=message,
        Subject='תור פנוי!',
    )
    print(f"📱 SMS נשלח: {message}")

lambda_handler()