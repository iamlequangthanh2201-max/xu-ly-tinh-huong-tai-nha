# Xử lý tại nhà

Web app (PWA) tra cứu các bước xử lý tại nhà khi bé hoặc mẹ gặp vấn đề sau sinh: trớ sữa, sốt, vàng da, tắc tia sữa, và các dấu hiệu phải đi cấp cứu.

Mở app: https://iamlequangthanh2201-max.github.io/xu-ly-tai-nha/

Cùng bộ với [Giấc ngủ cho con](https://iamlequangthanh2201-max.github.io/giac-ngu-cho-con/) và [Dinh dưỡng cho con](https://iamlequangthanh2201-max.github.io/dinh-duong-cho-con/).

## Có gì trong app

- 34 tình huống (25 của bé, 9 của mẹ), chia 8 nhóm, mỗi tình huống có mức độ xanh, vàng, đỏ
- Mỗi tình huống: **Làm ngay** (các bước đánh số, chạm để đánh dấu đã làm), **Phòng ngừa**, **Không nên**, **Đi khám khi**
- 7 kỹ năng cơ bản (ợ hơi, hút mũi, đo nhiệt độ, đếm nhịp thở, kiểm tra mất nước, sơ cứu hóc dị vật, quấn bé), mở nhanh dạng bảng trượt ngay trong từng bước
- Tìm kiếm có dấu hoặc không dấu ("tro sua", "tắc sữa")
- Trang Cấp cứu: nút gọi 115, danh sách dấu hiệu nguy hiểm của bé và mẹ
- Công cụ: đồng hồ đếm nhịp thở 60 giây, hẹn giờ đo lại nhiệt độ
- Cài lên màn hình chính điện thoại, chạy được khi mất mạng, có giao diện tối cho ban đêm

## Cấu trúc

| File | Vai trò |
|---|---|
| `noi-dung.md` | Toàn bộ nội dung. Sửa ở đây |
| `build.py` | Đọc `noi-dung.md`, xếp nhóm, gắn từ khoá tìm kiếm, dựng app vào `docs/` |
| `src/` | Khung trang, giao diện, mã app, service worker |
| `docs/` | Bản đã dựng, GitHub Pages phục vụ thư mục này |

## Sửa nội dung và cập nhật

```bash
python3 build.py
git add -A && git commit -m "Cập nhật nội dung" && git push
```

Quy ước trong `noi-dung.md`:
- `### A1. Tên tình huống 🟢` (🟢 🟡 🔴, có thể ghép `🟢/🔴`)
- `**Làm ngay:**` rồi danh sách `1. 2. 3.` thành checklist
- `**Phòng ngừa:**`, `**Không nên:**`, `**Đi khám khi:**` thành các phần riêng
- Ghi `(K2)` hoặc `(xem A5)` để tạo nút mở nhanh kỹ năng, tình huống khác

Tình huống mới cần được thêm vào một nhóm trong `CATEGORIES` ở `build.py`, nếu không build sẽ báo lỗi.

## Không thay bác sĩ

Thông tin tham khảo theo khuyến nghị phổ biến của WHO, AAP và Bộ Y tế. Khi có dấu hiệu nguy hiểm, hoặc khi bố mẹ thấy bất an, hãy đưa bé đi khám.
