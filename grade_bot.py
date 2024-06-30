import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict
from threading import Thread
import telebot
import logging

# تكوين سجل الأخطاء
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# استبدل 'YOUR_TELEGRAM_BOT_TOKEN' برمز بوت تلغرام الخاص بك
bot = telebot.TeleBot('7296304236:AAGfHWbzrbh1e0fm9czpU57rbkizp7ZwwGs')

URL = 'https://exam.albaath-univ.edu.sy/exam-it/re.php'
RESULTS_URL = "https://exam.albaath-univ.edu.sy/exam-it/re.php"

# قاموس لتخزين النتائج لكل طالب
old_results = defaultdict(set)

# قاموس لتتبع الطلاب الذين يتحقق منهم البوت
students_being_checked = {}

def get_grades_html(student_id):
    data = {'number1': student_id, 'nospy': ''}
    try:
        response = requests.post(URL, data=data)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"حدث خطأ أثناء الاتصال بالموقع: {e}")
        return None

def extract_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the student's name using a more specific selector
    student_name_cell = soup.find('td', {'colspan': "4"})  
    student_name = student_name_cell.text.strip() if student_name_cell else "اسم الطالب غير موجود"  

    table = soup.find('table')
    results = {}
    if table:
        rows = table.find_all('tr')[2:]  # Skip header and name rows
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:  # Ensure enough columns
                subject = cols[0].text.strip()
                final_grade = cols[3].text.strip()
                results[subject] = final_grade
    return student_name, results  # Return a tuple of student_name and the results dictionary
    

def check_student(student_id, chat_id):
    html_content = get_grades_html(student_id)
    if html_content:
        if "window.location" in html_content.decode('utf-8'):
            bot.send_message(chat_id, f"تم إعادة توجيهك إلى صفحة أخرى. إعادة المحاولة للطالب {student_id}...")
            return

        student_name, new_results = extract_results(html_content)  # Unpack the tuple correctly

        if new_results:
            # Check if there are any new results or if it's the first check
            if student_id not in old_results:
                old_results[student_id] = new_results
                message = f"نتائج جديدة لـ {student_name} ({student_id}):\n\n"
                for subject, grade in new_results.items():
                    mark = "✅" if int(grade) >= 60 else "❌"
                    message += f"*{subject}:* {grade} {mark}\n"
                bot.send_message(chat_id, message, parse_mode='Markdown')
            else:
                # Check for changes in existing results
                changes_found = False
                for subject, grade in new_results.items():
                    if subject in old_results[student_id] and grade != old_results[student_id][subject]:
                        changes_found = True
                        mark = "✅" if int(grade) >= 60 else "❌"
                        bot.send_message(chat_id, f"تغيير في نتيجة مادة {subject} لـ {student_name} ({student_id}):\n*{subject}:* {grade} {mark}", parse_mode='Markdown')

                if not changes_found:
                    # Only send a message if there are no changes
                    bot.send_message(chat_id, f"لا توجد نتائج جديدة للرقم الجامعي {student_id}")

                # Update old_results to reflect the new results
                old_results[student_id] = new_results
        else:
            bot.send_message(chat_id, f"لا توجد نتائج متاحة للرقم الجامعي {student_id}")
    else:
        bot.send_message(chat_id, f"حدث خطأ أثناء جلب نتائج {student_id}.")

    html_content = get_grades_html(student_id)
    if html_content:
        if "window.location" in html_content.decode('utf-8'):
            bot.send_message(chat_id, f"تم إعادة توجيهك إلى صفحة أخرى. إعادة المحاولة للطالب {student_id}...")
            return

        student_name, new_results = extract_results(html_content)
        if new_results:
            if student_id not in old_results or new_results != old_results[student_id]:
                old_results[student_id] = new_results
                message = f"نتائج جديدة لـ {student_name} ({student_id}):\n\n"
                for subject, grade in new_results.items():
                    mark = "✅" if int(grade) >= 60 else "❌"  # إضافة إشارة النجاح/الرسوب
                    message += f"*{subject}:* {grade} {mark}\n" 
                bot.send_message(chat_id, message, parse_mode='Markdown')
        else:
            bot.send_message(chat_id, f"لا توجد نتائج متاحة للرقم الجامعي {student_id}")
    else:
        bot.send_message(chat_id, f"حدث خطأ أثناء جلب نتائج {student_id}.")
    html_content = get_grades_html(student_id)
    if html_content:
        if "window.location" in html_content.decode('utf-8'):
            bot.send_message(chat_id, f"تم إعادة توجيهك إلى صفحة أخرى. إعادة المحاولة للطالب {student_id}...")
            return

        new_results = extract_results(html_content)
        if new_results:
            if student_id not in old_results or new_results != old_results[student_id]:
                old_results[student_id] = new_results
                message = f"تم العثور على نتائج جديدة للرقم الجامعي {student_id}:\n\n"
                for subject, grade in new_results.items():
                    message += f"*{subject}:* {grade}\n"  # تنسيق ب Markdown
                bot.send_message(chat_id, message, parse_mode='Markdown')
        else:
            bot.send_message(chat_id, f"لا توجد نتائج متاحة للرقم الجامعي {student_id}")
    else:
        bot.send_message(chat_id, f"حدث خطأ أثناء جلب نتائج {student_id}.")
    html_content = get_grades_html(student_id)
    if html_content:
        if "window.location" in html_content.decode('utf-8'):
            bot.send_message(chat_id, f"تم إعادة توجيهك إلى صفحة أخرى. إعادة المحاولة للطالب {student_id}...")
            return

        new_results = extract_results(html_content)
        if new_results:
            if student_id not in old_results or new_results != old_results[student_id]:
                old_results[student_id] = new_results
                message = f"تم العثور على نتائج جديدة للرقم الجامعي {student_id}:\n"
                for subject, grade in new_results:
                    message += f"- {subject}: {grade}\n"
                bot.send_message(chat_id, message)
            # لا ترسل رسالة إذا لم تكن هناك نتائج جديدة لتجنب إزعاج المستخدم
        else:
            bot.send_message(chat_id, f"لا توجد نتائج متاحة للرقم الجامعي {student_id}")
    else:
        bot.send_message(chat_id, f"حدث خطأ أثناء جلب نتائج {student_id}.")

def check_student_loop(student_id, chat_id):
    while student_id in students_being_checked:
        check_student(student_id, chat_id)
        time.sleep(30)  # Check every 60 seconds (adjust as needed)
    while student_id in students_being_checked:
        check_student(student_id, chat_id)
        time.sleep(30)  # Check every 60 seconds (adjust as needed)
# معالج الأمر /check_continuously
@bot.message_handler(commands=['check_continuously'])
def check_continuously(message):
    student_id = message.text.split()[1]  # الحصول على الرقم الجامعي من الأمر
    chat_id = message.chat.id

    if student_id in students_being_checked:
        bot.reply_to(message, "أنا بالفعل أتحقق من النتائج لهذا الرقم الجامعي.")
        return

    students_being_checked[student_id] = True
    thread = Thread(target=check_student_loop, args=(student_id, chat_id))
    thread.start()
    bot.reply_to(message, f"سأقوم بالتحقق من النتائج للرقم الجامعي {student_id} بشكل مستمر وإرسالها إليك عند توفرها.")
# معالج الأمر /start
@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, "أهلا بك في بوت نتائج جامعة البعث. أرسل لي رقمك الجامعي للتحقق من النتائج.")

# معالج الرسائل النصية (الأرقام الجامعية)
@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_student_id(message):
    student_id = message.text
    chat_id = message.chat.id

    if student_id in students_being_checked:
        bot.reply_to(message, "أنا بالفعل أتحقق من النتائج لهذا الرقم الجامعي.")
        return

    students_being_checked[student_id] = True
    thread = Thread(target=check_student_loop, args=(student_id, chat_id))
    thread.start()
    bot.reply_to(message, f"سأقوم بالتحقق من النتائج للرقم الجامعي {student_id} وإرسالها إليك عند توفرها.")

# تشغيل البوت
bot.polling()
