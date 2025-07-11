# 🚀 Dashboard Streamlit dengan Login Keren

Dashboard modern dengan halaman login yang stylish menggunakan Streamlit.

## ✨ Fitur

- 🔐 Halaman login dengan UI modern dan gradient design
- 📊 Dashboard dengan metrics dan charts
- 🎨 CSS kustom dengan efek glassmorphism
- 🔒 Sistem autentikasi sederhana
- 📱 Responsive design

## 🛠️ Instalasi

1. **Clone atau download project ini**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi:**
   ```bash
   streamlit run app.py
   ```

4. **Buka browser dan akses:**
   ```
   http://localhost:8501
   ```

## 🔑 Demo Credentials

Gunakan salah satu dari credentials berikut untuk login:

| Username | Password |
|----------|----------|
| `admin`  | `admin123` |
| `user`   | `password` |
| `demo`   | `demo123` |

## 📋 Struktur Project

```
GOOGLE FORM/
├── app.py              # Aplikasi utama Streamlit
├── requirements.txt    # Dependencies Python
└── README.md          # Dokumentasi project
```

## 🎨 Fitur UI

- **Glassmorphism Design**: Background blur dengan transparansi
- **Gradient Colors**: Warna gradient yang modern dan menarik
- **Hover Effects**: Animasi saat hover pada tombol
- **Responsive Layout**: Tampilan yang responsif di berbagai ukuran layar
- **Custom CSS**: Styling khusus untuk pengalaman pengguna yang lebih baik

## 📊 Dashboard Features

- **Metrics Cards**: Menampilkan KPI utama (Users, Revenue, Growth)
- **Interactive Charts**: Bar chart dan line chart untuk analytics
- **Sidebar Navigation**: Menu navigasi dengan info user dan logout
- **Real-time Data**: Simulasi data real-time (dapat diintegrasikan dengan database)

## 🔧 Customization

Anda dapat dengan mudah menyesuaikan:

- **Warna dan Theme**: Edit CSS di function `load_css()`
- **User Database**: Tambah user di dictionary `USERS`
- **Dashboard Content**: Modifikasi function `dashboard_page()`
- **Charts dan Metrics**: Update data di section analytics

## 🚀 Next Steps

Untuk pengembangan lebih lanjut, Anda bisa menambahkan:

- Database integration (PostgreSQL, MySQL, MongoDB)
- User registration dan forgot password
- Role-based access control
- File upload dan download
- Email notifications
- API integrations
- Export data functionality

## 📝 Notes

- Password di-hash menggunakan SHA256 untuk keamanan dasar
- Session state digunakan untuk manage user authentication
- CSS kustom memungkinkan styling yang fleksibel
- Struktur modular memudahkan pengembangan lebih lanjut

Selamat coding! 🎉 