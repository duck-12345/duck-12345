import socket
import concurrent.futures
import time
import os

def send_packet(server_ip, server_port, packet, packet_count, thread_id):
    total_sent = 0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Tối ưu socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2 * 1024 * 1024)  # 2MB buffer
            s.settimeout(10)

            try:
                s.connect((server_ip, server_port))
                s.settimeout(None)
            except socket.timeout:
                print(f"[Luồng {thread_id}] ❌ Kết nối timeout.")
                return 0
            except Exception as e:
                print(f"[Luồng {thread_id}] ❌ Lỗi khi kết nối: {e}")
                return 0

            for i in range(packet_count):
                try:
                    s.sendall(packet)
                    total_sent += 1
                    # Giảm tải hệ thống nếu gửi quá nhanh
                    if i % 100 == 0:
                        time.sleep(0.001)
                except Exception as e:
                    print(f"[Luồng {thread_id}] ❌ Gói {i+1} lỗi: {e}")
                    break

            print(f"[Luồng {thread_id}] ✅ Gửi xong {total_sent}/{packet_count} gói.")
            return total_sent

    except Exception as e:
        print(f"[Luồng {thread_id}] ❌ Lỗi tổng thể: {e}")
        return 0

def main():
    try:
        server_address = input("Nhập địa chỉ server (IP:PORT): ").strip()
        if ":" not in server_address:
            raise ValueError("Sai định dạng. Ví dụ: 192.168.1.1:8080")
        server_ip, server_port = server_address.split(":")
        server_port = int(server_port)

        packet_size_kb = int(input("Nhập kích thước mỗi gói (KB): "))
        packet_count = int(input("Số gói mỗi luồng gửi: "))
        thread_count = int(input("Số luồng gửi đồng thời: "))

        total_data_mb = packet_size_kb * packet_count * thread_count / 1024
        if total_data_mb > 1000:
            confirm = input(f"⚠️ Tổng dữ liệu là {total_data_mb:.2f} MB. Bạn có chắc muốn tiếp tục? (y/n): ")
            if confirm.lower() != "y":
                return

        packet = b"\x00" * (packet_size_kb * 1024)

        print(f"\n➡️ Đang gửi {packet_count} gói/luồng * {thread_count} luồng = {packet_count * thread_count} gói")
        print(f"➡️ Mỗi gói: {packet_size_kb} KB | Tổng dữ liệu: ~{total_data_mb:.2f} MB\n")

        start = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(send_packet, server_ip, server_port, packet, packet_count, i)
                       for i in range(thread_count)]

            total_sent = 0
            for i, future in enumerate(futures):
                try:
                    sent = future.result(timeout=60)  # Tăng timeout nếu gói nhiều
                    total_sent += sent
                except concurrent.futures.TimeoutError:
                    print(f"[Luồng {i}] ⚠️ Timeout sau 60 giây.")

        end = time.time()
        duration = end - start

        print(f"\n✅ Tổng số gói gửi thành công: {total_sent}/{packet_count * thread_count}")
        print(f"⏱️ Thời gian thực thi: {duration:.2f} giây")
        print(f"🚀 Tốc độ trung bình: {total_sent * packet_size_kb / duration:.2f} KB/s")

        # Thêm dòng TikTok sau khi hoàn thành
        print("\ncre_buy tik tok@Dogmeomeoz")

    except Exception as e:
        print(f"❌ Lỗi chung: {e}")

if __name__ == "__main__":
    main()
