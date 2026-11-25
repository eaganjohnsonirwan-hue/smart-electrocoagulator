# Paket rakit terbuka — Smart Electrocoagulator, unit tutup C1
Versi v07, 25 November 2026. Tim STEAM Pahoa. Lisensi: CERN-OHL-P-2.0 (perangkat keras) dan MIT (kode); lihat bagian Licence.

Paket ini berisi berkas untuk membuat ulang sel elektrokoagulasi 1,5 L dengan empat pelat Al 1100, tutup cetak 3D, pencatat INA219 + ESP32, dan ruang optik ESP32-CAM. Daftar bahan berharga, rencana uji, dan risiko ada di Bagian 3 makalah. Kamera menghasilkan indeks optik, bukan nilai kekeruhan, sampai divalidasi dengan turbidimeter.

## Isi
- `gambar/`: Gambar 3.1–3.4 (potongan, tampak atas tutup, diagram kabel, ruang optik dan isi kotak elektronik), 3.5a dan 3.5b (model 3D terakit dan terurai), 3.6 (skema listrik), 3.7 (cetak biru A3, PNG dan PDF).
- `stl/`: berkas cetak tutup, batang penggantung (cetak 2), badan dan atap kotak elektronik, badan dan pintu ruang optik.
- `cad/`: skrip Blender 2026-11-15_c1_model_v08.py, fit_report.txt (ukuran untuk wadah 130 × 130 × 150 mm), print_volumes.txt.

## Urutan kerja
1. Ukur wadah (dalam 130–140 mm, tinggi dalam 145–160 mm), pelat setelah dipotong, papan ESP32, papan ESP32-CAM, sakelar DPDT, dan tinggi rumah Dupont.
2. Jalankan skrip dengan ukuran terukur (Blender 5.2, tanpa tampilan); skrip berhenti jika ada lubang yang mengenai bibir tutup atau bagian di kotak elektronik saling bertabrakan:
   `blender.exe --background --factory-startup --python 2026-11-15_c1_model_v08.py -- <folder_keluaran> --box 130 --h 150 --plw 99 --plh 149`
   Baca fit_report.txt untuk tanda isi, ujung sifon, tanda henti sifon, tanda celup pipet, luas aktif, dan arus untuk 1, 2, 3 mA/cm².
3. Cetak potongan uji (slot, bibir tutup, rel kamera, rel pintu), lalu semua bagian: PLA, lapisan 0,2 mm, dinding 3 lapis, isian 40 % (± 165 g).
4. Rakit dengan langkah di bawah dan kabel pada tabel di bawah.

## Langkah perakitan (sama dengan Bagian 3, Langkah 3)
1. Ukur ukuran dalam wadah dengan jangka sorong atau penggaris. Wadah dipakai jika lebar dan panjang dalam 13,0–14,0 cm dan tinggi dalam 14,5–16,0 cm. Masukkan ukuran terukur ke skrip model 3D (pilihan --box dan --h; setelah pelat dipotong, ukuran pelat terukur dengan --plw dan --plh). Skrip berhenti dengan pesan jika ada lubang yang mengenai bibir tutup, lalu membuat ulang berkas cetak dan berkas fit_report.txt yang memuat kedalaman air 1,5 L, tinggi ujung hisap sifon, tanda henti sifon, dan tanda celup pipet.
2. Cetak bagian pada Tabel 3.2 dari berkas cetak yang baru dibuat. Cetak lebih dulu potongan uji slot, bibir tutup, rel kamera, dan rel pintu (R18).
3. Potong lembar aluminium 200 × 300 mm dengan gergaji besi menjadi empat pelat. Haluskan tepi dengan kikir dan amplas, ukur ukuran setiap pelat, dan beri nomor 1–4 pada ujung atas.
4. Pada setiap pelat, buat dua lubang Ø3,2 mm untuk spacer, 105 mm dari tepi bawah dan 40 mm di kiri dan kanan garis tengah (± 10 mm dari tepi samping). Buat juga dua slot 4 × 11 mm untuk batang penggantung (bor tiga lubang Ø4 mm berderet, lalu ratakan sisinya dengan kikir), 40 mm di kiri dan kanan garis tengah, dengan tepi bawah slot 132 mm dari tepi bawah pelat. Pada pelat 1, buat dua lubang Ø4 mm, 5 mm dari tepi kiri, pada ketinggian 60 dan 90 mm dari tepi bawah, untuk mengikat selang sifon.
5. Rangkai keempat pelat dengan spacer nilon M3 jantan-betina 10 mm sehingga jarak antarpelat 10 mm. Kedua ujung tumpukan ditutup dengan baut nilon M3 di sisi luar pelat 1 dan mur nilon di sisi luar pelat 4, keduanya dari set spacer.
6. Masukkan ujung atas rangkaian pelat ke slot tutup dari bawah sampai slot penggantung pada pelat muncul di atas tutup. Selipkan dua batang penggantung melalui slot pelat dengan sisi 10 mm tegak sehingga batang bertumpu di atas tutup. Pada posisi ini, ujung bawah pelat berada pada tinggi dalam wadah dikurangi 130 mm (20 mm untuk wadah setinggi 150 mm) dan ujung atas pelat ± 16 mm di atas tutup.
7. Sebelum unit tutup dimasukkan ke wadah, masukkan selang sifon melalui lubang Ø7 mm dan ikat pada pelat 1 dengan dua pengikat kabel melalui lubang Ø4 mm. Ujung hisap diatur tepat di setengah tinggi air terukur (46 mm untuk wadah 13 × 13 cm), sesuai butir 11 subbab 1.5.
8. Dengan spidol permanen, buat dua tanda pada dinding luar wadah: tanda batas isi setinggi permukaan air 1,5 L (92 mm untuk wadah 13 × 13 cm) dan tanda henti sifon 5 mm di atas ujung hisap (51 mm). Untuk wadah lain, kedua angka diambil dari fit_report.txt.
9. Siapkan kabel sesuai Tabel 3.8. Kabel buaya no. 1 dan no. 5 dipakai utuh untuk kabel A dan C (klip di salah satu ujung dipotong); kabel no. 2 dan no. 3 dipotong menjadi dua (E–H); kabel no. 4 dipotong menjadi tiga (B, L1, L2). Ujung potongan dikupas lalu diberi skun 4,8 mm berisolasi dengan tang skun. Skun untuk kaki 1, 3, 4, dan 6 masing-masing menjepit dua kabel, yaitu kabel ke pelat dan kabel penghubung L1 atau L2. Jepit satu klip pada setiap pelat, 3 mm dari ujung: pelat 1 dan pelat 3 di ujung kiri (kabel E dan F), pelat 2 dan pelat 4 di ujung kanan (kabel G dan H). Klip yang berlawanan polaritas berjarak ± 90 mm, dan tidak ada kabel jembatan antarpelat.
10. Pasang lebih dulu kabel Dupont D1–D5 pada pin ESP32 (Tabel 3.8), karena pin di bawah papan tidak dapat dijangkau setelah papan direkatkan. Letakkan ESP32 beserta kabelnya di atas dua batang tumpu di dalam kotak elektronik, rapat ke dinding depan, dengan port micro-USB menghadap jendela USB, lalu rekatkan pada potongan pita busa dua sisi 6 × 20 mm yang sudah ditempel di atas setiap batang tumpu; tekan papan pada bagian ujungnya, bukan pada modul atau kaki pin. Ikat INA219 ke dinding belakang melalui empat slot dengan dua pengikat kabel (Gambar 3.4b); kabel dilewatkan melalui celah 4 mm di sisi belakang papan menuju INA219. Pasang sakelar DPDT pada lubang di sisi kiri atap kotak; skun pada kaki sakelar ditekuk ke samping agar kabelnya tidak menekan ESP32 di bawahnya. Sebelum menyambung, cari pasangan kaki dengan mode uji sambung multimeter: kaki tengah (2 dan 5) tersambung ke kaki atas pada satu posisi sakelar dan ke kaki bawah pada posisi lain. Letakkan PSU paling jauh 15 cm dari wadah, masukkan kabel melalui takik kabel di dinding depan kotak, lalu sambung sesuai Tabel 3.8, Gambar 3.3, dan Gambar 3.6: PSU (+) → sekring 1 A → INA219 Vin+ (kabel A, dudukan sekring disolder di luar kotak); INA219 Vin− → kaki 2 (kabel B); PSU (−) → kaki 5 (kabel C). Kaki 1 dan 6 menjadi bus X, sedangkan kaki 3 dan 4 menjadi bus Y, sehingga posisi sakelar menentukan bus mana yang menjadi anode. GND INA219 disambung ke GND ESP32 (kabel D1), dan satu kabel Dupont dari pin GND ESP32 yang lain dikerut ke dalam skun kaki 5 (kabel D2), bukan ke kabel pelat. Setelah semua kabel terpasang dan sebelum PSU dihubungkan, periksa dengan mode uji sambung multimeter bahwa kabel B dan C tidak tersambung pada kedua posisi sakelar maupun pada posisi tengah.
11. Pasang kotak elektronik dan ruang optik di atas tutup dengan baut nilon M3 × 10 mm dan mur di bawah tutup. Pasang kipas di atas empat tiang cetak sehingga pasak masuk ke lubang sudut kipas, lalu ikat dengan dua pengikat kabel; kipas menghadap ke luar. Sambungkan kabel kipas ke potongan kabel USB bekas dengan solder dan tutup sambungan dengan selongsong bakar.
12. Potong strip LED menjadi dua bagian pada tanda potong terdekat (± 50 mm), sambungkan keduanya dengan dua kabel Dupont yang disolder dan ditutup selongsong bakar (kabel K4), lalu pasang pada alur dinding kiri dan kanan ruang optik; kabel K4 direkatkan dengan isolasi hitam di sepanjang dinding belakang, di atas vial. Kabel USB bawaan strip (kabel K3) dipotong 3 cm dari strip, dimasukkan melalui lubang kabel LED Ø4, disolder kembali, dan ditutup selongsong bakar; celah di lubang ditutup isolasi hitam. Pasang kertas putih di atas dudukan vial. Unggah program ke ESP32-CAM dengan papan pemrogram, lalu lepaskan papan itu. Program mematikan LED kilat (GPIO 4) agar cahaya hanya berasal dari strip LED, dan mengirim foto melalui Wi-Fi ke laptop dengan nama berkas sesuai kode batch. Selipkan ESP32-CAM ke dua rel di atap dengan kamera menghadap ke bawah; papan bertumpu pada tepi rel, 8 mm di atas atap, dan lensa berada di atas lubang Ø8 (Gambar 3.4). Rel tidak memakai baut karena papan ESP32-CAM yang umum tidak memiliki lubang baut. Ukuran rel dibuat untuk papan AI-Thinker 27 × 40,5 mm. Papan milik tim diukur lebih dulu dengan jangka sorong, dan jika ukurannya atau posisi lensanya berbeda, nilainya diubah di skrip model 3D sebelum ruang optik dicetak. Tutup celah di sekitar lensa dan ujung rel yang terbuka dengan isolasi listrik hitam. Untuk daya 5 V, potong kabel USB bekas kedua, solder kabel merah dan hitamnya ke dua kabel Dupont betina, tutup sambungan dengan selongsong bakar, lalu pasang ke pin 5V dan GND ESP32-CAM (kabel K1). Terakhir, turunkan pintu ruang optik di antara dua rel pintu sampai bertumpu pada tutup; pintu diangkat dengan tonjolan di atasnya saat vial diganti.
13. Sebelum air dimasukkan, periksa dengan multimeter bahwa tidak ada hubungan langsung antara bus X dan bus Y.
## Daftar kabel (sama dengan Tabel 3.8)
Kabel jumper buaya-buaya 46 cm diberi nomor 1–10; nomor 6–10 cadangan.

| Kode | Dari | Ke | Ujung kabel | Dibuat dari | Panjang |
|---|---|---|---|---|---|
| A | PSU (+) | INA219 Vin+, melalui sekring 1 A | Klip di PSU; kawat terkupas di terminal sekrup INA219; dudukan sekring disolder di tengah kabel dan ditutup selongsong bakar | Kabel buaya no. 1 utuh, satu klip dipotong | ± 44 cm |
| B | INA219 Vin− | Kaki 2 sakelar | Kawat terkupas; skun | Potongan kabel no. 4, klip dibuang | ± 14 cm |
| C | PSU (−) | Kaki 5 sakelar | Klip; skun yang juga menjepit D2 | Kabel no. 5 utuh, satu klip dipotong | ± 44 cm |
| D1 | GND INA219 | GND ESP32 | Dupont–Dupont | Kabel Dupont | 20 cm |
| D2 | Pin GND kedua ESP32 | Kaki 5 sakelar | Dupont; kawat terkupas di skun kaki 5 | Kabel Dupont, satu ujung dipotong | ± 18 cm |
| D3–D5 | VCC, SDA, SCL INA219 | 3V3, GPIO 21, GPIO 22 ESP32 | Dupont–Dupont | Tiga kabel Dupont | 20 cm |
| E | Kaki 1 sakelar | Pelat 1, ujung kiri | Skun bersama L1; klip | Separuh kabel no. 2 | ± 22 cm |
| F | Kaki 6 sakelar | Pelat 3, ujung kiri | Skun bersama L1; klip | Separuh kabel no. 2 | ± 22 cm |
| G | Kaki 3 sakelar | Pelat 2, ujung kanan | Skun bersama L2; klip | Separuh kabel no. 3 | ± 22 cm |
| H | Kaki 4 sakelar | Pelat 4, ujung kanan | Skun bersama L2; klip | Separuh kabel no. 3 | ± 22 cm |
| L1 | Kaki 1 sakelar | Kaki 6 sakelar | Skun–skun | Potongan kabel no. 4 | ± 12 cm |
| L2 | Kaki 3 sakelar | Kaki 4 sakelar | Skun–skun | Potongan kabel no. 4 | ± 12 cm |
| K1 | Pengisi daya USB | Pin 5V dan GND ESP32-CAM | Steker USB; dua Dupont betina disolder dan ditutup selongsong bakar | Kabel USB bekas kedua, dua kabel Dupont | panjang kabel bekas |
| K2 | Pengisi daya USB | Kipas 5 V | Steker USB; solder dan selongsong bakar | Kabel USB bekas pertama | panjang kabel bekas |
| K3 | Pengisi daya USB | Potongan strip LED pertama | Steker USB bawaan; disambung ulang dengan solder setelah melewati lubang Ø4 | Kabel bawaan strip LED | panjang bawaan |
| K4 | Potongan strip LED pertama | Potongan strip LED kedua | Solder dan selongsong bakar di kedua ujung | Dua kabel Dupont, kedua ujung dipotong | ± 10 cm |

Strip LED memakai steker USB bawaannya (kabel K3). Kabel A, C, dan E–H keluar dari kotak elektronik melalui takik kabel di dinding depan, sedangkan kabel USB ESP32 ke laptop keluar melalui jendela USB di dinding kiri.

## Keselamatan
Kipas menyala sebelum PSU. Batas tegangan PSU 24 V, sekring 1 A. Tanpa api atau percikan di dekat alat (gas H₂). Air hasil tidak diminum.

## Firmware
- `firmware/logger/`: pencatat ESP32 + INA219, CSV setiap 1 detik.
- `firmware/camera/`: server foto ESP32-CAM.
- `firmware/README.md` dan `firmware/2026-11-25_compile-log_v01.txt`: catatan dan log kompilasi.

Dikompilasi dengan arduino-cli 1.6.0, inti ESP32 3.3.13, 0 galat; belum diuji pada perangkat keras. Salin `camera/secrets.h.example` menjadi `secrets.h` dan isi Wi-Fi Anda.

## Lisensi
Berkas perangkat keras (`cad`, `stl`, `gambar`) berlisensi CERN-OHL-P-2.0 (`LICENSE-HARDWARE.txt`). Kode (`firmware`, `cad/*.py`) berlisensi MIT (`LICENSE-SOFTWARE.txt`).
