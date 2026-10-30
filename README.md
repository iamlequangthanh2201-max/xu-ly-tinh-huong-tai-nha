# Sunny time

Xử lý tình huống tại nhà. Web app (PWA) tra cứu các bước xử lý tại nhà khi bé hoặc mẹ gặp vấn đề sau sinh: trớ sữa, sốt, vàng da, tắc tia sữa, và các dấu hiệu phải đi cấp cứu.

Mở app: https://iamlequangthanh2201-max.github.io/xu-ly-tinh-huong-tai-nha/

Cùng bộ với [Giấc ngủ cho con](https://iamlequangthanh2201-max.github.io/giac-ngu-cho-con/) và [Dinh dưỡng cho con](https://iamlequangthanh2201-max.github.io/dinh-duong-cho-con/).

## Có gì trong app

- **Lịch trình** theo giai đoạn: 2 tuần đầu (chỉ bú mẹ), tuần 3-4 (bắt đầu bú bình sữa mẹ), rồi từng tháng 1-12. Mỗi giai đoạn có 3 phần: Ban ngày (thức, bú, chơi, tắm, ngủ), Ban đêm (kế hoạch chia ca Mẹ/Bố để mẹ ngủ liền 5-6 tiếng), Bú & hút sữa (giờ hút, cách hâm và cho bú bình sữa mẹ, bảo quản sữa, khi nào dùng sữa công thức). Nhập ngày sinh để app tự chọn đúng giai đoạn, có đánh dấu "Bây giờ" theo giờ thực
- 37 tình huống (28 của bé, 9 của mẹ), chia 8 nhóm, mỗi tình huống có mức độ xanh, vàng, đỏ
- Mỗi tình huống: **Đây là gì?** (giải thích ngắn hiện tượng, mặc định gập lại), **Làm ngay** (các bước đánh số, chạm để đánh dấu đã làm), **Phòng ngừa**, **Không nên**, **Đi khám khi**
- 15 kỹ năng cơ bản (ợ hơi, hút mũi, đo nhiệt độ, đếm nhịp thở, kiểm tra mất nước, sơ cứu hóc dị vật, quấn bé, vệ sinh rốn, tập cho bé tự ngủ, phân biệt ngày đêm, tắm, thay tã, rửa tiệt trùng bình, dỗ bé khóc 5S, nằm sấp và massage), mở nhanh dạng bảng trượt ngay trong từng bước
- 60 từ chuyên môn (thóp, li bì, rút lõm ngực...) được gạch chân, chạm vào để xem nghĩa, có trang Giải thích từ ngữ riêng
- Tìm kiếm có dấu hoặc không dấu ("tro sua", "tắc sữa")
- Trang Cấp cứu: nút gọi 115, danh sách dấu hiệu nguy hiểm của bé và mẹ
- Công cụ: đồng hồ đếm nhịp thở 60 giây, hẹn giờ đo lại nhiệt độ
- Cài lên màn hình chính điện thoại, chạy được khi mất mạng, có giao diện tối cho ban đêm

## Cấu trúc

| File | Vai trò |
|---|---|
| `noi-dung.md` | Nội dung các tình huống, kỹ năng, từ ngữ |
| `lich-trinh.md` | Lịch trình theo giai đoạn: ban ngày, ban đêm, bú và hút sữa, sữa công thức |
| `build.py` | Đọc `noi-dung.md`, xếp nhóm, gắn từ khoá tìm kiếm, tách nền icon từ `assets/app-icon-source.png` và xuất đủ các cỡ, dựng app vào `docs/` |
| `src/` | Khung trang, giao diện, mã app, service worker |
| `docs/` | Bản đã dựng, GitHub Pages phục vụ thư mục này |

## Giao diện

Theo ngôn ngữ thiết kế iOS 27 (Liquid Glass): thanh tab kính nổi có viên chọn trượt, nút tròn bằng kính, tiêu đề lớn thu nhỏ vào thanh trên khi cuộn, danh sách bo góc kiểu iOS, màu hệ thống của Apple, bảng trượt kính, hiệu ứng nhún khi chạm.

## Sửa nội dung và cập nhật

```bash
python3 build.py
git add -A && git commit -m "Cập nhật nội dung" && git push
```

Quy ước trong `noi-dung.md`:
- `### A1. Tên tình huống 🟢` (🟢 🟡 🔴, có thể ghép `🟢/🔴`)
- `**Đây là gì:** ...` ngay dưới tiêu đề, một đoạn giải thích ngắn
- `**Làm ngay:**` rồi danh sách `1. 2. 3.` thành checklist
- `**Phòng ngừa:**`, `**Không nên:**`, `**Đi khám khi:**` thành các phần riêng
- Phần D cuối file: `- **Từ / tên gọi khác:** giải thích`. Từ nào có ở đây sẽ tự được gạch chân trong app
- Ghi `(K2)` hoặc `(xem A5)` để tạo nút mở nhanh kỹ năng, tình huống khác

Tình huống mới cần được thêm vào một nhóm trong `CATEGORIES` ở `build.py`, nếu không build sẽ báo lỗi.

## Không thay bác sĩ

Thông tin tham khảo theo khuyến nghị phổ biến của WHO, AAP và Bộ Y tế. Khi có dấu hiệu nguy hiểm, hoặc khi bố mẹ thấy bất an, hãy đưa bé đi khám.
