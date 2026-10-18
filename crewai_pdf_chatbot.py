
import argparse
from pathlib import Path

import requests
from pypdf import PdfReader

OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_MODELS = ("qwen2.5:1.5b", "llama3.2:3b")

def read_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(
                f"[Page {page_number + 1}]\n{text}"
            )
    return "\n\n".join(pages)

def get_installed_models():
    response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict) or not isinstance(data.get("models"), list):
        raise ValueError("รูปแบบรายการโมเดลจาก Ollama ไม่ถูกต้อง")

    models = []
    for model in data["models"]:
        if not isinstance(model, dict) or not isinstance(model.get("name"), str):
            raise ValueError("ข้อมูลโมเดลจาก Ollama ไม่ถูกต้อง")
        models.append(model["name"])

    return models


def generate_answer(prompt, model):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["response"]

def build_prompt(question, pdf_text):
    document_context = pdf_text[:12000]
    if document_context:
        return f"""
คำถามของผู้ใช้:
{question}

เนื้อหาจาก PDF:
{document_context}

คำแนะนำ:
- ถ้าถามเกี่ยวกับ PDF ให้ยึดเนื้อหาที่ให้มาเป็นหลัก
- ระบุหมายเลขหน้าจากข้อความ [Page N] เมื่อทำได้
- หากไม่มีข้อมูลในเอกสาร ให้บอกว่าไม่พบข้อมูลในส่วนที่ได้รับ
- ถ้าเป็นคำถามทั่วไป ให้ตอบจากความรู้ทั่วไป
- ตอบเป็นภาษาเดียวกับคำถามและใช้คำที่เข้าใจง่าย
"""
    return f"""
คำถามทั่วไปของผู้ใช้:
{question}

ตอบให้ถูกต้อง ชัดเจน และเข้าใจง่าย
หากไม่แน่ใจให้ระบุข้อจำกัดของคำตอบ
"""


def main():
    parser = argparse.ArgumentParser(
        description="แชตถามตอบทั่วไปหรือถามจากไฟล์ PDF ผ่าน Ollama"
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        help="พาธไปยังไฟล์ PDF (ไม่บังคับ)",
    )
    args = parser.parse_args()

    print("เลือกโหมดการใช้งาน")
    print("1. แชต AI ทั่วไป")
    print("2. แชตถามตอบจากไฟล์ PDF")

    try:
        while True:
            mode = input("เลือก 1 หรือ 2: ").strip()
            if mode in {"1", "2"}:
                break
            print("กรุณาเลือก 1 หรือ 2")
    except (EOFError, KeyboardInterrupt):
        print("\nจบการทำงาน")
        return 0

    pdf_text = ""
    if mode == "2":
        pdf_name = args.pdf or input(
            "พิมพ์ชื่อไฟล์ PDF ในโฟลเดอร์เดียวกับโปรแกรม: "
        ).strip()
        if not pdf_name:
            print("ไม่ได้ระบุชื่อไฟล์ PDF")
            return 1

        pdf_path = Path(pdf_name).expanduser()
        if not pdf_path.is_absolute():
            pdf_path = Path(__file__).resolve().parent / pdf_path

        try:
            pdf_text = read_pdf(pdf_path)
        except (OSError, ValueError) as error:
            print(f"อ่าน PDF ไม่สำเร็จ ({pdf_path}): {error}")
            return 1

        if pdf_text.strip():
            print(f"อ่าน PDF สำเร็จ: {pdf_path.name} ({len(pdf_text):,} ตัวอักษร)")
        else:
            print("ไม่พบข้อความใน PDF อาจเป็นไฟล์สแกนที่ต้องใช้ OCR")

    try:
        installed_models = get_installed_models()
    except (requests.RequestException, ValueError) as error:
        print(f"ดึงรายการโมเดลจาก Ollama ไม่สำเร็จ: {error}")
        print("ตรวจสอบว่า Ollama ทำงานอยู่ที่ " + OLLAMA_URL)
        return 1

    print("\nเลือกโมเดล AI")
    for index, model in enumerate(OLLAMA_MODELS, start=1):
        status = "" if model in installed_models else " (ยังไม่ได้ติดตั้ง)"
        print(f"{index}. {model}{status}")

    try:
        while True:
            model_choice = input("เลือกหมายเลขโมเดล: ").strip()
            if model_choice.isdigit() and 1 <= int(model_choice) <= len(OLLAMA_MODELS):
                selected_model = OLLAMA_MODELS[int(model_choice) - 1]
                break
            print(f"กรุณาเลือกหมายเลข 1 ถึง {len(OLLAMA_MODELS)}")
    except (EOFError, KeyboardInterrupt):
        print("\nจบการทำงาน")
        return 0

    if selected_model not in installed_models:
        print(f"ยังไม่มีโมเดล {selected_model} ใน Ollama")
        print(f"ติดตั้งด้วยคำสั่ง: ollama pull {selected_model}")
        return 1

    print(f"\nแชตกับ Ollama ({selected_model})")
    print("พิมพ์ exit หรือ quit เพื่อออกจากโปรแกรม")

    try:
        while True:
            question = input("\nคุณ: ").strip()
            if question.lower() in {"exit", "quit"}:
                break
            if not question:
                continue

            try:
                answer = generate_answer(
                    build_prompt(question, pdf_text),
                    selected_model,
                )
            except requests.RequestException as error:
                print(f"เรียก Ollama ไม่สำเร็จ: {error}")
                continue

            print(f"\nผู้ช่วย: {answer}")
    except (EOFError, KeyboardInterrupt):
        print("\nจบการสนทนา")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
