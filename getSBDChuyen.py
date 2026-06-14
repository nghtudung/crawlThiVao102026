import re

with open("danh_sach.txt", "r", encoding="utf-8") as file:
    content = file.read()

sbd_list = re.findall(r"\b\d{6}\b", content)

with open("ket_qua_sbd.txt", "w", encoding="utf-8") as file_out:
    for sbd in sbd_list:
        file_out.write(sbd + "\n")

print(f"Đã trích xuất thành công {len(sbd_list)} số báo danh vào file 'ket_qua_sbd.txt'!")