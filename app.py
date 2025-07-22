# app.py

from pyscript.to_json import run_to_json
from pyscript.to_tag import run_to_tag

def main():
    while True:
        print("\n📌 เลือกโหมดที่ต้องการ:")
        print("1. แปลง xlsx เป็น JSON")
        print("2. ส่ง Tag ผ่าน API")
        print("พิมพ์ 'exit' เพื่อออกจากโปรแกรม")

        choice = input("ใส่หมายเลขโหมด: ").strip().lower()

        if choice == '1':
            run_to_json()
        elif choice == '2':
            run_to_tag()
        elif choice == 'exit':
            print("👋 ออกจากโปรแกรมเรียบร้อยแล้ว")
            break
        else:
            print("❌ เลือกไม่ถูกต้อง กรุณาเลือก 1 หรือ 2 หรือพิมพ์ 'exit'")

if __name__ == "__main__":
    main()
