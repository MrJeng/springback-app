# เครื่องคำนวณสปริงสตริปเปอร์ — แม่พิมพ์กดตัด

เว็บแอปพลิเคชัน (Streamlit) สำหรับคำนวณแรงตัด แรงสตริป แรงกดรวมที่เครื่องปั๊มต้องรับ
และแนะนำสเปกสปริงสตริปเปอร์มาตรฐาน (อ้างอิงรหัสสี ISO 10243) สำหรับงานออกแบบแม่พิมพ์กดตัด (Blanking / Piercing Die)

## โครงสร้างไฟล์

```
.
├── streamlit_app.py       # โค้ดหลักของแอป (ไฟล์นี้ Streamlit Cloud จะหาเจอเองอัตโนมัติ)
├── train_model.py         # สคริปต์ฝึกโมเดล Machine Learning (รันครั้งเดียวถ้าต้องการฝึกใหม่)
├── requirements.txt       # ไลบรารีที่ต้องติดตั้ง
├── models/
│   ├── pipe_duty.joblib     # โมเดล Neural Network ทำนายระดับงานสปริง
│   ├── pipe_n.joblib        # โมเดล Neural Network ทำนายจำนวนสปริง
│   └── meta.joblib          # ข้อมูลประกอบ (ความแม่นยำโมเดล ฯลฯ)
├── fonts/
│   └── Loma.otf            # ฟอนต์ภาษาไทย ฝังไปกับแอปเพื่อให้ภาพประกอบสปริงแสดงผลถูกต้อง
├── .gitignore
└── README.md
```

⚠️ **สำคัญ:** ต้องอัปโหลดโฟลเดอร์ `fonts/` (พร้อมไฟล์ `Loma.otf` ข้างใน) ขึ้น GitHub ไปพร้อมกับ
`streamlit_app.py` ด้วยเสมอ ไม่งั้นตัวอักษรไทยในภาพประกอบสปริงจะกลายเป็นกล่องสี่เหลี่ยม (□□□)
เพราะเซิร์ฟเวอร์ของ Streamlit Cloud ไม่มีฟอนต์ไทยติดตั้งไว้

⚠️ **สำคัญ:** ต้องอัปโหลดโฟลเดอร์ `models/` (พร้อมไฟล์ `.joblib` ทั้ง 3 ไฟล์ข้างใน) ขึ้น GitHub
ไปพร้อมกันด้วยเสมอ ไม่งั้นส่วนเปรียบเทียบผลกับ Machine Learning ในแอปจะไม่ขึ้น (แอปยังใช้งานได้ปกติ
แค่ไม่มีส่วนเปรียบเทียบ AI)

## เกี่ยวกับส่วน Machine Learning (Neural Network) ในแอป

แอปนี้มีส่วน **"🤖 เปรียบเทียบกับผลทำนายจาก Machine Learning"** เพิ่มเข้ามา โดย:

- ฝึก Neural Network (Multi-Layer Perceptron จาก scikit-learn) จากข้อมูลจำลองที่สร้างจาก
  สูตรวิศวกรรม/มาตรฐาน ISO 10243 เดิม (ไฟล์ `train_model.py`) แล้วบันทึกโมเดลไว้ในโฟลเดอร์ `models/`
- แอปหลัก (`streamlit_app.py`) โหลดโมเดลที่ฝึกไว้แล้วมาทำนายผลคู่ขนานกับสูตรตรง เพื่อเปรียบเทียบ
  ให้เห็นว่า AI ทำนายใกล้เคียงสูตรจริงแค่ไหน
- **สูตรวิศวกรรมยังคงเป็นคำตอบหลักที่ใช้ออกแบบจริงเสมอ** เพราะแม่นยำ 100% และตรวจสอบย้อนกลับ
  ได้ ส่วน AI ใช้เพื่อสาธิต/เปรียบเทียบเท่านั้น

หากต้องการฝึกโมเดลใหม่ (เช่น ปรับพารามิเตอร์) ให้รัน:
```bash
python train_model.py
```
จะได้ไฟล์โมเดลใหม่ในโฟลเดอร์ `models/` แทนที่ของเดิม

## รันบนเครื่องตัวเอง (Local)

ต้องมี Python 3.9 ขึ้นไป

```bash
# 1) สร้างและเปิดใช้งาน virtual environment (แนะนำ ไม่บังคับ)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2) ติดตั้งไลบรารีที่ต้องใช้
pip install -r requirements.txt

# 3) รันแอป
streamlit run streamlit_app.py
```

เบราว์เซอร์จะเปิดขึ้นเองที่ `http://localhost:8501`

## อัปโหลดขึ้น GitHub

ทำในโฟลเดอร์นี้ (โฟลเดอร์ที่มี `streamlit_app.py`, `requirements.txt`, `fonts/`)

```bash
git init
git add .
git commit -m "Initial commit: spring calculator streamlit app"

# สร้าง repo เปล่าบน GitHub ก่อน (ผ่านหน้าเว็บ github.com -> New repository)
# แล้วเชื่อมกับ repo ที่สร้าง (แก้ URL ให้ตรงกับ repo ของคุณ)
git remote add origin https://github.com/<ชื่อผู้ใช้ของคุณ>/<ชื่อ-repo>.git
git branch -M main
git push -u origin main
```

> ถ้ายังไม่เคยตั้งค่า git บนเครื่อง ให้รันครั้งเดียวก่อน:
> ```bash
> git config --global user.name "ชื่อของคุณ"
> git config --global user.email "อีเมลของคุณ"
> ```

> ถ้าอัปโหลดผ่านหน้าเว็บ GitHub (Add file > Upload files) ให้ลากทั้งโฟลเดอร์ `fonts/` เข้าไปด้วย —
> GitHub จะสร้างโฟลเดอร์ย่อยให้เองถ้าลากทั้งโฟลเดอร์เข้าไป

## Deploy ขึ้น Streamlit Community Cloud (ฟรี)

1. ไปที่ [share.streamlit.io](https://share.streamlit.io) แล้วล็อกอินด้วยบัญชี GitHub
2. กด **"New app"**
3. เลือก repository, branch (`main`), และ Main file path เป็น `streamlit_app.py`
4. กด **"Deploy"** — รอสักครู่แอปจะขึ้นออนไลน์พร้อมลิงก์ให้แชร์/ส่งอาจารย์ได้ทันที

ทุกครั้งที่ `git push` โค้ดใหม่ขึ้น GitHub แอปบน Streamlit Cloud จะอัปเดตให้อัตโนมัติ

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ModuleNotFoundError: matplotlib` (หรือ pandas/streamlit) | ไม่มีไฟล์ `requirements.txt` ใน repo หรือชื่อไฟล์ผิด | ตรวจว่ามี `requirements.txt` (ตัวพิมพ์เล็กทั้งหมด) อยู่ระดับ root แล้ว Reboot app |
| ตัวอักษรไทยในภาพประกอบสปริงเป็นกล่อง □□□ | ไม่ได้อัปโหลดโฟลเดอร์ `fonts/Loma.otf` ขึ้น GitHub | อัปโหลดโฟลเดอร์ `fonts/` ให้ครบ แล้ว Reboot app |
| `SyntaxError` ตอนรัน | คัดลอก/วางโค้ดแล้วมีบรรทัดตกหล่น | อัปโหลดไฟล์ `.py` ตัวจริงแทนการคัดลอก-วางข้อความ |

## หมายเหตุ

ค่าอัตราสปริง (k) และสัมประสิทธิ์แรงสตริปในโปรแกรมเป็นค่าประมาณเชิงวิศวกรรมเพื่อการศึกษา
ก่อนนำไปใช้งานจริงควรตรวจสอบกับแคตตาล็อกของผู้ผลิต เช่น Misumi, Raymond, Danly

ฟอนต์ Loma (`fonts/Loma.otf`) เป็นฟอนต์ไทยจากโครงการ TLWG (Thai Linux Working Group)
เผยแพร่ภายใต้สัญญาอนุญาต GPL-2+ with Font Exception ใช้งานและแจกจ่ายร่วมกับซอฟต์แวร์นี้ได้โดยเสรี
