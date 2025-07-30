import os
import json
import requests
from datetime import datetime

def load_api_list(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

def select_api(api_list):
    print("\n📡 เลือก API ที่ต้องการส่งข้อมูล:")
    for idx, api in enumerate(api_list, 1):
        print(f"{idx}. {api['name']} (expire date: {api['expire date']})")
    print("พิมพ์ 'back' เพื่อกลับไปเมนูหลัก")

    while True:
        choice = input("เลือกหมายเลข: ").strip().lower()
        if choice == "back":
            return "back"
        if choice.isdigit() and 1 <= int(choice) <= len(api_list):
            return api_list[int(choice) - 1]
        print("❌ เลือกไม่ถูกต้อง")

def list_subfolders(directory):
    return [f for f in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, f)) and not f.startswith("__")]


def list_json_files(directory):
    return [f for f in os.listdir(directory) if f.endswith(".json")]

def select_from_list(items, prompt="เลือก:", allow_back=True, allow_exit=True):
        for idx, item in enumerate(items, 1):
            print(f"{idx}. {item}")
        if allow_back:
            print("พิมพ์ 'back' เพื่อย้อนกลับ")
        if allow_exit:
            print("พิมพ์ 'exit' เพื่อจบโปรแกรม")

        while True:
            choice = input(prompt).strip().lower()
            if allow_back and choice == "back":
                return "back"
            if allow_exit and choice == "exit":
                return "exit"
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(items):
                    return items[index]
            print("❌ เลือกไม่ถูกต้อง")
    
def select_json_files(json_files):
    print("\n📄 เลือกไฟล์ JSON ที่ต้องการส่ง:")
    for idx, file in enumerate(json_files, 1):
        print(f"{idx}. {file}")
    print("พิมพ์ 'back' เพื่อย้อนกลับ | พิมพ์ 'all' เพื่อเลือกทั้งหมด")

    while True:
        choice = input("ใส่หมายเลข: ").strip().lower()
        if choice == "back":
            return "back"
        if choice == "all":
            return json_files
        try:
            indices = parse_range_selection(choice, len(json_files))
            selected = [json_files[i] for i in indices]
            if selected:
                return selected
        except:
            pass
        print("❌ รูปแบบไม่ถูกต้อง")

def parse_range_selection(selection_str, max_index):
    result = set()
    parts = selection_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if 1 <= start <= end <= max_index:
                    result.update(range(start - 1, end))
            except:
                continue
        elif part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < max_index:
                result.add(idx)
    return sorted(result)

def run_to_tag():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, ".."))
    api_file_path = os.path.join(script_dir, "api_write.txt")

    try:
        while True:
            api_list = load_api_list(api_file_path)
            selected_api = select_api(api_list)
            if selected_api == "back":
                return "back"

            print(f"\n🚀 คุณเลือก: {selected_api['name']}")
            print(f"URL: {selected_api['url']}")

            headers = {
                "Content-Type": "application/json",
                "Authorization": selected_api["token"]
            }

            while True:
                print("\n📁 เลือกโฟลเดอร์ที่มีไฟล์ JSON:")
                folders = list_subfolders(base_dir)
                if not folders:
                    print("❌ ไม่พบโฟลเดอร์ย่อยใด ๆ")
                    break

                selected_folder = select_from_list(folders, prompt="เลือกโฟลเดอร์หมายเลข: ")
                if selected_folder == "exit":
                    print("👋 จบโปรแกรม")
                    return
                if selected_folder == "back":
                    break

                folder_path = os.path.join(base_dir, selected_folder)

                while True:
                    json_files = list_json_files(folder_path)
                    if not json_files:
                        print("❌ ไม่พบไฟล์ .json ในโฟลเดอร์นี้")
                        break

                    selected_files = select_json_files(json_files)
                    if selected_files == "back":
                        break
                    if not selected_files:
                        continue

                    print("\n📤 ไฟล์ที่กำลังจะส่ง:")
                    for f in selected_files:
                        print(f"- {f}")
                    print(f"\n📊 รวมทั้งหมด {len(selected_files)} ไฟล์ที่เลือกไว้")
                    confirm = input(f"ยืนยันการส่งไฟล์ที่เลือกไปยัง {selected_api['name']}? (y/n): ").strip().lower()
                    if confirm != "y":
                        print("❌ ยกเลิกการส่ง")
                        continue

                    # prepare log file
                    log_dir = os.path.join(base_dir, "log_to_tag")
                    os.makedirs(log_dir, exist_ok=True)
                    log_filename = f"log-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"
                    log_path = os.path.join(log_dir, log_filename)
                    log_lines = []

                    success_count = 0
                    fail_count = 0

                    for file_name in selected_files:
                        try:
                            file_path = os.path.join(folder_path, file_name)
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)

                            response = requests.post(selected_api["url"], headers=headers, json=data)

                            if response.status_code == 200:
                                msg = f"✅ ส่งสำเร็จ: {file_name}"
                                print(msg)
                                log_lines.append(msg)
                                success_count += 1
                            else:
                                try:
                                    error_detail = response.json()
                                    error_message = error_detail.get("error") or error_detail.get("message") or str(error_detail)
                                except Exception:
                                    error_message = response.text

                                if response.status_code == 400:
                                    msg = f"⚠️ ส่งไม่สำเร็จ: {file_name} ({response.status_code}) {error_message} 💡อาจเกิดจาก: มีชื่อ tag นี้อยู่แล้ว"
                                elif response.status_code == 500:
                                    msg = f"⚠️ ส่งไม่สำเร็จ: {file_name} ({response.status_code}) {error_message} 💡อาจเกิดจาก: มี col ตรงกับคำห้ามใช้ หรือ data type ผิด"
                                else:
                                    msg = f"⚠️ ส่งไม่สำเร็จ: {file_name} ({response.status_code}) {error_message}"
                                print(msg)
                                log_lines.append(msg)
                                fail_count += 1

                        except Exception as e:
                            msg = f"❌ เกิดข้อผิดพลาดกับไฟล์ {file_name}: {e}"
                            print(msg)
                            log_lines.append(msg)
                            fail_count += 1

                    total = success_count + fail_count
                    print("\n📈 สรุปผลการส่ง:")
                    print(f" - ✅ สำเร็จ: {success_count} ไฟล์")
                    print(f" - ❌ ไม่สำเร็จ: {fail_count} ไฟล์")
                    if total > 0:
                        success_percent = (success_count / total) * 100
                        fail_percent = (fail_count / total) * 100
                        print(f" - 📊 คิดเป็น: {success_percent:.2f}% สำเร็จ | {fail_percent:.2f}% ไม่สำเร็จ")

                    # บันทึก log
                    with open(log_path, "w", encoding="utf-8") as log_file:
                        for line in log_lines:
                            log_file.write(line + "\n")

                    print(f"\n📝 Log ถูกบันทึกไว้ที่: {log_path}")

    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาดหลัก: {e}")