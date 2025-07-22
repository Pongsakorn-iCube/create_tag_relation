# .py/to_json.py

import os
import json
from openpyxl import load_workbook

# mapping data types -> PostgreSQL format
type_mapping = {
    "string": "text",
    "boolean": "boolean",
    "double": "double precision",
    "integer": "integer"
}

def run_to_json():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))

    # หาไฟล์ .xlsx ทั้งหมด
    xlsx_files = [f for f in os.listdir(base_dir) if f.lower().endswith(".xlsx")]

    if not xlsx_files:
        print("❌ ไม่พบไฟล์ .xlsx ในโฟลเดอร์")
        return

    # แสดงรายการให้เลือก
    print("\n📄 พบไฟล์ .xlsx ดังต่อไปนี้:")
    for idx, file in enumerate(xlsx_files, 1):
        print(f"{idx}. {file}")
    print("พิมพ์ 'back' เพื่อย้อนกลับ")

    while True:
        choice = input("เลือกหมายเลขไฟล์: ").strip().lower()
        if choice == "back":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(xlsx_files)):
            print("❌ เลือกหมายเลขที่อยู่ในรายการ")
            continue

        selected_file = xlsx_files[int(choice) - 1]
        break

    file_stem = os.path.splitext(selected_file)[0]
    file_path = os.path.join(base_dir, selected_file)
    output_dir = os.path.join(base_dir, file_stem)
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n🔎 กำลังเปิดไฟล์: {file_path}")

    try:
        wb = load_workbook(filename=file_path, data_only=True)

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]

            mappings = []
            row = 12  # เริ่มจาก D12, E12, F12
            position = 1

            while True:
                field_name = sheet[f"D{row}"].value
                data_type = sheet[f"E{row}"].value
                is_identity = sheet[f"F{row}"].value

                if field_name is None and data_type is None and is_identity is None:
                    break

                data_type_lower = (data_type or "").strip().lower()
                pg_data_type = type_mapping.get(data_type_lower, data_type)

                mapping = {
                    "fieldName": field_name,
                    "dataType": pg_data_type,
                    "isNotNull": False,
                    "isIdentity": bool(is_identity),
                    "position": position
                }
                mappings.append(mapping)

                row += 1
                position += 1

            result = {
                "tagGroupName": sheet_name,
                "description": sheet_name,
                "enableHyperTable": False,
                "isView": False,
                "sqlQueryScript": None,
                "tagRelationFieldMappings": mappings
            }

            output_file = os.path.join(output_dir, f"{sheet_name}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"✅ บันทึกไฟล์ JSON สำหรับ sheet '{sheet_name}' ที่: {output_file}")

    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
