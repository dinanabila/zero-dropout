import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from PIL import Image

# Load model pipeline
model = joblib.load('model.pkl')

# [UI] Judul formulir
st.title("🏫Towards Zero Dropout")

# [UI] Isian formulir berupa permintaan input dataset dalam format csv / xlsx dari user
uploaded_file = st.file_uploader("Upload CSV file dataset mahasiswa aktif", type="csv")

# Menyimpan data ke dalam DataFrame
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=',')
    df = df.drop(columns=['Status'])
    st.write("DataFrame yang diupload:")
    st.dataframe(df, height=200)

# [UI] Tombol Prediksi
submit = st.button("Prediksi")

# Tampilkan hasil prediksi
if submit:
    prediction = model.predict(df)
    label_map = {0: 'Dropout', 1: 'Graduate'}
    predicted_labels = [label_map[p] for p in prediction]
    df['Prediksi'] = predicted_labels
    # [UI] DataFrame hasil prediksi
    st.markdown('#### Hasil Prediksi')
    st.dataframe(df, height=200)

    # [UI] Plot Pie Chart dan Bar Chart Prediksi Status Dropout dan Graduate
    st.markdown('#### Chart Sebaran Prediksi Status Dropout dan Graduate')
    column_name = 'Prediksi'
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    # Barplot horizontal
    sns.countplot(y=column_name, hue=column_name, legend=False, data=df, palette=[ '#FC8D62','#66C2A5'], ax=ax1)
    ax1.set_title(f'Distribusi {column_name} Status Mahasiswa')
    sns.despine(ax=ax1, left=True, bottom=True)
    for p in ax1.patches:
        ax1.annotate(
            f'{int(p.get_width())}',
            (p.get_width(), p.get_y() + p.get_height() / 2),
            ha='left',
            va='center',
            xytext=(5, 0),
            textcoords='offset points'
        )
    # Pie chart
    df[column_name].value_counts().plot.pie(
        autopct='%1.1f%%',
        colors=['#66C2A5', '#FC8D62'],
        startangle=90,
        explode=[0.05] * df[column_name].nunique(),
        ax=ax2
    )
    ax2.set_title(f'Persentase Distribusi {column_name} Status Mahasiswa')
    ax2.set_ylabel('')
    plt.tight_layout()
    st.pyplot(fig)

    # Hitung persentasi hasil prediksi status dropout
    dropout_count = df['Prediksi'].value_counts().get('Dropout', 0)
    total_count = len(df)
    dropout_percent = (dropout_count / total_count) * 100

    # [UI] Teks analisis dan rekomendasi action items
    st.markdown(f"""
    #### Analisis dan Rekomendasi Action Items
    Diprediksi sebanyak **{dropout_percent:.1f}%** dari mahasiswa (353 dari 794 mahasiswa) dalam dataset ini berpotensi mengalami dropout. Untuk memahami lebih lanjut siapa saja yang berisiko, silakan lihat dashboard interaktif yang telah disusun berdasarkan indikator-indikator risiko utama, seperti performa akademik, hingga status keuangan.
    """)

    # [UI] Tampilkan screenshoot dashboard, bikinnya pakai tableau public
    dashboard_img = Image.open('dinanabila-dashboard.png')
    st.image(dashboard_img, use_container_width=True)

    st.markdown(
    "[Klik di sini untuk membuka dashboard interaktif di Tableau Public ↗️](https://public.tableau.com/views/DropoutPreventionDashboard/Dashboard)",
    unsafe_allow_html=True
    )
    
    st.markdown("""
    Berdasarkan indikator pada dashboard, di bawah ini disajikan dataset mahasiswa yang memenuhi kriteria risiko spesifik. Dataset ini dapat **diunduh** dan digunakan untuk menindaklanjuti langkah preventif (action items), seperti:
    - Pendampingan akademik untuk mahasiswa dengan nilai rendah
    - Edukasi keuangan bagi mahasiswa yang belum melunasi biaya kuliah
    - Sediakan **layanan konseling fleksibel** (online atau di luar jam kuliah reguler) yang memahami dinamika mahasiswa di atas 23 tahun.
    - Evaluasi distribusi beasiswa agar lebih tepat sasaran
                
    Silakan gunakan data berikut sebagai dasar pengambilan keputusan di institusi Anda.
    """)
    # st.image(dashboard_img)


    # =====================
    # FILTERING RISK GROUPS
    # =====================

    st.markdown("#### 📌 Dataset Mahasiswa yang Diprediksi Dropout Berdasarkan Indikator Risiko")

    # 1. Nilai semester 1 rendah (< 8)
    low_g1 = df[(df['Curricular_units_1st_sem_grade'] < 8) & (df['Prediksi'] == 'Dropout')]
    st.markdown(f"**1. Nilai Semester 1 di bawah 8** ({len(low_g1)} mahasiswa)")
    st.dataframe(low_g1, height=150)
    csv_low_g1 = low_g1.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Unduh CSV - Nilai Semester 1 < 8", data=csv_low_g1, file_name='low_g1.csv', mime='text/csv')

    # 2. Nilai semester 2 rendah (< 8)
    low_g2 = df[(df['Curricular_units_2nd_sem_grade'] < 8) & (df['Prediksi'] == 'Dropout')]
    st.markdown(f"**2. Nilai Semester 2 di bawah 8** ({len(low_g2)} mahasiswa)")
    st.dataframe(low_g2, height=150)
    csv_low_g2 = low_g2.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Unduh CSV - Nilai Semester 2 < 8", data=csv_low_g2, file_name='low_g2.csv', mime='text/csv')

    # 3. Belum membayar biaya kuliah
    unpaid = df[(df['Tuition_fees_up_to_date'] == 0) & (df['Prediksi'] == 'Dropout')]
    st.markdown(f"**3. Belum Melunasi Biaya Kuliah** ({len(unpaid)} mahasiswa)")
    st.dataframe(unpaid, height=150)
    csv_unpaid = unpaid.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Unduh CSV - Belum Bayar Kuliah", data=csv_unpaid, file_name='unpaid.csv', mime='text/csv')

    # 4. Berstatus Debtor
    debtor = df[(df['Debtor'] == 1) & (df['Prediksi'] == 'Dropout')]
    st.markdown(f"**4. Berstatus Debtor** ({len(debtor)} mahasiswa)")
    st.dataframe(debtor, height=150)
    csv_debtor = debtor.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Unduh CSV - Debitur", data=csv_debtor, file_name='debtor.csv', mime='text/csv')

    # 5. Tidak menerima beasiswa
    no_scholar = df[(df['Scholarship_holder'] == 0) & (df['Prediksi'] == 'Dropout')]
    st.markdown(f"**5. Tidak Menerima Beasiswa** ({len(no_scholar)} mahasiswa)")
    st.dataframe(no_scholar, height=150)
    csv_no_scholar = no_scholar.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Unduh CSV - Tanpa Beasiswa", data=csv_no_scholar, file_name='no_scholar.csv', mime='text/csv')

    # 6. Jalur masuk usia > 23 tahun atau dengan Age_at_enrollment > 23 tahun
    risky_mode = df[((df['Application_mode'] == 39) | (df['Age_at_enrollment'] > 23)) & (df['Prediksi'] == 'Dropout')]
    st.markdown(f"**6. Usia Awal Masuk Kuliah > 23** ({len(risky_mode)} mahasiswa)")
    st.dataframe(risky_mode, height=150)
    csv_risky_mode = risky_mode.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Unduh CSV - Usia Awal Masuk Kuliah > 23 tahun", data=csv_risky_mode, file_name='risky_mode.csv', mime='text/csv')
