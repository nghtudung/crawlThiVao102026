import csv
import json
import os
import time
import requests

TARGET_SCHOOL = "48"

SCHOOL_LIMITS = {
    "01": "010780",
    "02": "020214",
    "03": "030670",
    "04": "040730",
    "05": "050549",
    "06": "060685",
    "07": "070783",
    "08": "080647",
    "09": "090248",
    "10": "100821",
    "11": "110729",
    "12": "120129",
    "13": "130999",
    "14": "140810",
    "15": "150768",
    "16": "160748",
    "17": "170854",
    "18": "180282",
    "19": "190902",
    "20": "200836",
    "21": "210662",
    "22": "220600",
    "23": "230555",
    "24": "240615",
    "25": "250347",
    "26": "260853",
    "27": "270871",
    "28": "280789",
    "29": "290529",
    "30": "300843",
    "31": "310273",
    "32": "320623",
    "33": "330722",
    "34": "340585",
    "35": "350961",
    "36": "360747",
    "37": "370751",
    "38": "380577",
    "39": "390595",
    "40": "400157",
    "41": "410649",
    "42": "420129",
    "43": "430437",
    "44": "440303",
    "45": "450443",
    "46": "460336",
    "47": "470292",
    "48": "480999",
    "49": "490812",
    "50": "500956",
    "51": "510528",
    "52": "520596",
    "53": "530735",
    "54": "540288",
    "55": "550945",
    "56": "560999",
    "57": "570441",
    "58": "580999",
    "59": "590838",
    "60": "600500",
    "61": "610342",
    "62": "620268",
    "63": "630999",
    "64": "640972",
    "65": "650962",
    "66": "660900",
    "67": "670909",
    "68": "680360",
    "69": "690269",
    "70": "700874",
    "71": "710938",
    "72": "720903",
    "73": "730371",
    "74": "740812",
    "75": "750860",
    "76": "760999",
    "77": "770738"
}

session = requests.Session()

COOKIES = {
    "HstCfa5031342": "1781436798949",
    "HstCmu5031342": "1781436798949",
    "__dtsu": "1040178143680099F73B679CF0E697EE",
    "_pubcid": "7de9ff76-62d7-4a4b-a90c-7e6f0081b866",
    "panoramaId": "28efbbcd905e1cca06ab2a57424ca9fb927a99738161aabc34c7917f5b50af50",
}
session.cookies.update(COOKIES)

COMMON_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-GB,en;q=0.9,vi;q=0.8,en-US;q=0.7",
    "origin": "https://diemthi10.bacninh.edu.vn",
    "referer": "https://diemthi10.bacninh.edu.vn/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
}
session.headers.update(COMMON_HEADERS)


def get_and_solve_captcha():
    captcha_url = "https://diemthi10.bacninh.edu.vn/api/captcha"
    while True:
        try:
            response = session.get(captcha_url, timeout=5)
            if response.status_code == 200:
                inner_data = response.json().get("data", {})
                uuid = inner_data.get("uuid")
                svg_image = inner_data.get("image")

                if uuid and svg_image:
                    import svg_captcha_solver

                    captcha_text = svg_captcha_solver.solve_captcha(
                        str(svg_image)
                    )

                    if (
                        not captcha_text
                        or "MLLQ" in captcha_text
                        or len(captcha_text) < 4
                    ):
                        time.sleep(0.1)
                        continue
                    return uuid, captcha_text
        except Exception:
            pass
        time.sleep(0.5)


def get_student_data(sbd):
    uuid, captcha_text = get_and_solve_captcha()

    lookup_url = "https://diemthi10.bacninh.edu.vn/api/lookup"
    payload = {"uuid": uuid, "captcha": captcha_text, "sbd": sbd}
    headers = {"content-type": "application/json"}

    try:
        response = session.post(
            lookup_url, json=payload, headers=headers, timeout=5
        )
        if response.status_code == 200:
            return response.json().get("data", {}).get("diemthi")
    except Exception:
        pass
    return None


def check_single_student(sbd):
    print(f"[*] Đang tiến hành kiểm tra SBD: {sbd}...")

    uuid, captcha_text = get_and_solve_captcha()
    if not uuid or not captcha_text:
        print("[-] Không thể giải được Captcha để tra cứu.")
        return None

    lookup_url = "https://diemthi10.bacninh.edu.vn/api/lookup"
    payload = {"uuid": uuid, "captcha": captcha_text, "sbd": str(sbd)}
    headers = {"content-type": "application/json"}

    try:
        response = session.post(
            lookup_url, json=payload, headers=headers, timeout=5
        )
        if response.status_code == 200:
            root_res = response.json()
            student_info = root_res.get("data", {}).get("diemthi")

            if student_info:
                print(f"[+] Tìm thấy thông tin thí sinh {sbd}:")
                print("-" * 40)
                print(f" Họ và tên : {student_info.get('FULLNAME')}")
                print(
                    f" Ngày sinh : {student_info.get('BIRTHDATE')} | Giới tính: {student_info.get('GIOIT')}"
                )
                print(f" Trường    : {student_info.get('TENTRUONG')}")
                print("-" * 40)
                print(f" Ngữ Văn   : {student_info.get('NGUVAN')}")
                print(f" Tiếng Anh : {student_info.get('TIENGANH')}")
                print(
                    f" Toán      : {student_info.get('TONGTOAN')} (Trắc nghiệm: {student_info.get('TOANTRN')} | Tự luận: {student_info.get('TOANTULUAN')})"
                )
                if student_info.get("MONCHUYEN"):
                    print(
                        f" Môn chuyên: {student_info.get('MONCHUYEN')} ({student_info.get('DIEMCHUYEN')} điểm)"
                    )
                print(
                    f" Điểm UT/KK: {student_info.get('DIEMUT')} / {student_info.get('DIEMKK')}"
                )
                print(f" TỔNG ĐIỂM : {student_info.get('TONGDT')}")
                print("-" * 40)
                return student_info
            else:
                print(
                    f"[-] Không có dữ liệu cho SBD {sbd} (Có thể sai số hoặc giải sai captcha)."
                )
        else:
            print(
                f"[-] Lỗi kết nối hệ thống. Mã lỗi HTTP: {response.status_code}"
            )
    except Exception as e:
        print(f"[-] Đã xảy ra lỗi khi gửi yêu cầu tra cứu: {e}")

    return None

def crawl_diem_chuyen(input_txt_file, output_csv_file):
    if not os.path.exists(input_txt_file):
        print(f"[-] Lỗi: Không tìm thấy file dữ liệu đầu vào '{input_txt_file}'!")
        return

    with open(input_txt_file, "r", encoding="utf-8") as f:
        sbd_list = [line.strip() for line in f if line.strip()]

    total_sbd = len(sbd_list)
    print(f"[*] Đã tìm thấy {total_sbd} số báo danh trong file '{input_txt_file}'.")
    print(f"[*] Bắt đầu tiến hành tra cứu và lưu vào '{output_csv_file}'...")

    fieldnames = [
        "CODE",
        "FULLNAME",
        "GIOIT",
        "BIRTHDATE",
        "DIEMUT",
        "DIEMKK",
        "NGUVAN",
        "TIENGANH",
        "TOANTRN",
        "TOANTULUAN",
        "TONGTOAN",
        "TONGDT",
        "MONCHUYEN",
        "DIEMCHUYEN",
        "TENTRUONG",
    ]

    with open(output_csv_file, mode="w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        success_count = 0

        for index, sbd in enumerate(sbd_list, start=1):
            if len(sbd) < 6:
                sbd = sbd.zfill(6)

            print(f"[{index}/{total_sbd}] Đang xử lý SBD: {sbd}...", end="", flush=True)

            student_info = None
            for _ in range(3):
                student_info = get_student_data(sbd)
                if student_info:
                    break
                time.sleep(0.5)

            if student_info:
                writer.writerow(student_info)
                success_count += 1
                print(f" -> [OK] Đã lưu: {student_info.get('FULLNAME')} | Chuyên: {student_info.get('MONCHUYEN') or 'Không'}")
            else:
                print(" -> [-] Trống hoặc lỗi kết nối.")

            time.sleep(0.2)

    print("\n" + "=" * 40)
    print(f"[OK] Đã chạy xong toàn bộ danh sách file txt!")
    print(f"[+] Lưu thành công: {success_count}/{total_sbd} thí sinh.")
    print(f"[+] File kết quả lưu tại: {os.path.abspath(output_csv_file)}")

def getDiemAll():
    # check_single_student("480123")
    full_sbd_limit = SCHOOL_LIMITS.get(TARGET_SCHOOL)

    if not full_sbd_limit:
        print(f"[-] Mã trường {TARGET_SCHOOL} không tồn tại trong danh sách.")
        exit()

    max_student = int(full_sbd_limit[-4:])
    filename = f"ket_qua_truong_{TARGET_SCHOOL}.csv"

    print(
        f"[*] Bắt đầu quét TRƯỜNG {TARGET_SCHOOL}. Giới hạn SBD cuối: {full_sbd_limit} (Tổng: {max_student} học sinh)"
    )

    fieldnames = [
        "CODE",
        "FULLNAME",
        "GIOIT",
        "BIRTHDATE",
        "DIEMUT",
        "DIEMKK",
        "NGUVAN",
        "TIENGANH",
        "TOANTRN",
        "TOANTULUAN",
        "TONGTOAN",
        "TONGDT",
        "MONCHUYEN",
        "DIEMCHUYEN",
        "TENTRUONG",
    ]

    with open(
        filename, mode="w", encoding="utf-8-sig", newline=""
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        success_count = 0

        for current_id in range(1, max_student + 1):
            sbd = f"{TARGET_SCHOOL}{current_id:04d}"

            student_info = None
            for _ in range(3):
                student_info = get_student_data(sbd)
                if student_info:
                    break
                time.sleep(0.5)

            if student_info:
                writer.writerow(student_info)
                success_count += 1
                print(
                    f"[+] Đã lưu SBD {sbd}: {student_info.get('FULLNAME')} -> Tổng ĐT: {student_info.get('TONGDT')}"
                )
            else:
                print(f"[-] SBD {sbd}: Trống hoặc lỗi kết nối.")

            time.sleep(0.2)

    print("\n" + "=" * 40)
    print(f"[OK] Quét hoàn tất trường {TARGET_SCHOOL}!")
    print(
        f"[+] Tổng số học sinh đã lưu thành công: {success_count}/{max_student}"
    )
    print(f"[+] Đường dẫn file kết quả: {os.path.abspath(filename)}")


if __name__ == "__main__":
    crawl_diem_chuyen("ket_qua_sbd.txt", "diemchuyen.csv")