# README

## Bot Penghitung Maxim

Bot Penghitung Maxim adalah bot Telegram yang dirancang untuk membantu pengguna dalam mencatat dan mengelola order dan pengeluaran. Bot ini memungkinkan pengguna untuk menambah, menghapus, dan mengedit data order dan pengeluaran, serta menghasilkan laporan harian dan bulanan.

### Fitur Utama

- **Tambah Order**: Pengguna dapat menambahkan order dengan memasukkan tanggal, jumlah order, total nominal, dan tips.
- **Tambah Pengeluaran**: Pengguna dapat mencatat pengeluaran dengan memasukkan tanggal dan jumlah pengeluaran.
- **Laporan Bulanan**: Menghasilkan laporan bulanan berdasarkan tanggal yang ditentukan.
- **Laporan Harian**: Menghasilkan laporan harian untuk tanggal yang ditentukan atau untuk hari ini.
- **Hapus Order**: Menghapus order berdasarkan tanggal dan ID order.
- **Hapus Pengeluaran**: Menghapus pengeluaran berdasarkan tanggal dan ID pengeluaran.
- **Edit Order**: Mengedit detail order yang sudah ada.
- **Edit Pengeluaran**: Mengedit detail pengeluaran yang sudah ada.
- **Cancel/Back**: Menghentikan proses yang sedang berlangsung dan kembali ke menu utama.

### Teknologi yang Digunakan

- **Python**: Bahasa pemrograman yang digunakan untuk mengembangkan bot.
- **Aiogram**: Framework untuk membangun bot Telegram dengan Python.
- **SQLAlchemy**: ORM untuk berinteraksi dengan database.
- **SQLite**: Database yang digunakan untuk menyimpan data order dan pengeluaran.

### Instalasi

1. **Clone Repository**:

   ```bash
   git clone https://github.com/Musc0de/maxim_income_bot.git
   cd repo-name
   ```

2. **Install Dependencies**:\
   Pastikan Anda memiliki Python 3.7 atau lebih baru. Kemudian, instal dependensi yang diperlukan:

   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi**:

   - Buat file `.env` dan tambahkan token bot Anda:

     ```
     BOT_TOKEN=your_bot_token_here
     ```

4. **Jalankan Bot**:\
   Setelah semua konfigurasi selesai, Anda dapat menjalankan bot dengan perintah:

   ```bash
   python main.py
   ```

### Penggunaan

Setelah bot berjalan, Anda dapat memulai interaksi dengan mengirimkan perintah `/start` di chat dengan bot. Anda akan melihat menu utama dengan berbagai opsi yang tersedia.

### Kontribusi

Jika Anda ingin berkontribusi pada proyek ini, silakan lakukan fork repository ini, buat perubahan yang diinginkan, dan kirimkan pull request.

### Lisensi

Proyek ini dilisensikan di bawah MIT License. Lihat file LICENSE untuk informasi lebih lanjut.

### Kontak

Jika Anda memiliki pertanyaan atau saran, silakan hubungi saya di devmustest@gmail.com.

---

Terima kasih telah menggunakan Bot Penghitung Maxim! Semoga bot ini bermanfaat untuk Anda dalam mengelola order dan pengeluaran.
