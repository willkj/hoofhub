import yt_dlp
import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk


# =====================
# FUNÇÃO PRINCIPAL
# =====================


def baixar_video():

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes')

            if total and downloaded:
                percent = downloaded / total * 100
                app.after(0, lambda: progress.config(value=percent))

        elif d['status'] == 'finished':
            app.after(0, lambda: progress.config(value=100))

    url = entry_url.get().strip()

    if not url:
        messagebox.showerror("Erro", "Cole a URL do vídeo")
        return

    btn_baixar.config(state="disabled")
    status_label.config(text="Buscando informações...")

    def pegar_titulo():
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                titulo = info.get("title", "video")

            caracteres_invalidos = r'<>:"/\|?*'
            for c in caracteres_invalidos:
                titulo = titulo.replace(c, "")

            app.after(0, lambda: abrir_salvar(titulo))

        except Exception as e:
                msg = str(e)
                app.after(0, lambda m=msg: erro(m))

    def abrir_salvar(titulo):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("Arquivo MP4", "*.mp4")],
            initialfile=f"{titulo}.mp4",
            title="Salvar vídeo como"
        )

        if not save_path:
            btn_baixar.config(state="normal")
            status_label.config(text="")
            return

        baixar_arquivo(save_path)

    def baixar_arquivo(save_path):
        status_label.config(text="Baixando...")
        progress.config(value=0)  # 👈 RESETA A BARRA AQUI


        def task():
            try:
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': save_path,
                    'noplaylist': True,
                    'geo_bypass': True,
                    'progress_hooks': [progress_hook],

                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'Referer': url
                    },

                    'concurrent_fragment_downloads': 5,
                    'fragment_retries': 10,
                    'skip_unavailable_fragments': True
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                app.after(0, lambda: finalizar(save_path))

            except Exception as e:
                    msg = str(e)
                    app.after(0, lambda m=msg: erro(m))

        threading.Thread(target=task, daemon=True).start()

    def finalizar(save_path):
        nome_arquivo = os.path.basename(save_path)

        status_label.config(text=f"✔ Download {nome_arquivo} finalizado")
        messagebox.showinfo("Sucesso", f"Download concluído:\n\n{nome_arquivo}")

        progress.config(value=0)
        btn_baixar.config(state="normal")

    def erro(msg):
        status_label.config(text="Erro")
        messagebox.showerror("Erro", msg)
        btn_baixar.config(state="normal")

    threading.Thread(target=pegar_titulo, daemon=True).start()

# =====================
# INTERFACE GRÁFICA
# =====================
app = tk.Tk()
app.title("HoofHub Downloader")
app.geometry("500x170")
app.resizable(False, False)

tk.Label(app, text="URL do vídeo:").pack(pady=(15, 5))

entry_url = tk.Entry(app, width=65)
entry_url.pack(pady=5)

btn_baixar = tk.Button(app, text="Salvar como e Baixar", width=22, command=baixar_video)
btn_baixar.pack(pady=10)

status_label = tk.Label(app, text="")
status_label.pack()

progress = ttk.Progressbar(app, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=5)

app.mainloop()
