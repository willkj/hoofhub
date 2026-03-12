import yt_dlp
import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk

download_list = []


# =====================
# PROGRESS HOOK
# =====================

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes')

        if total and downloaded:
            percent = downloaded / total * 100
            app.after(0, lambda: progress.config(value=percent))

    elif d['status'] == 'finished':
        app.after(0, lambda: progress.config(value=100))


# =====================
# DOWNLOAD ÚNICO
# =====================

def baixar_video():

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

            save_path = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                initialfile=f"{titulo}.mp4",
                title="Salvar vídeo como"
            )

            if not save_path:
                app.after(0, lambda: btn_baixar.config(state="normal"))
                return

            baixar_arquivo(save_path)

        except Exception as e:
            msg = str(e)
            app.after(0, lambda: erro(msg))

    def baixar_arquivo(save_path):

        status_label.config(text="Baixando...")
        progress.config(value=0)

        def task():
            try:

                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': save_path,
                    'geo_bypass': True,
                    'progress_hooks': [progress_hook],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                app.after(0, lambda: finalizar(save_path))

            except Exception as e:
                msg = str(e)
                app.after(0, lambda: erro(msg))

        threading.Thread(target=task, daemon=True).start()

    def finalizar(save_path):

        nome = os.path.basename(save_path)

        status_label.config(text=f"✔ Download {nome} finalizado")
        messagebox.showinfo("Sucesso", f"Download concluído:\n\n{nome}")

        progress.config(value=0)
        btn_baixar.config(state="normal")

    def erro(msg):
        status_label.config(text="Erro")
        messagebox.showerror("Erro", msg)
        btn_baixar.config(state="normal")

    threading.Thread(target=pegar_titulo, daemon=True).start()


# =====================
# ADICIONAR À LISTA
# =====================

def adicionar_lista():

    url = entry_url.get().strip()

    if not url:
        messagebox.showerror("Erro", "Cole uma URL")
        return

    download_list.append(url)

    status_label.config(text=f"{len(download_list)} vídeo(s) na lista")

    entry_url.delete(0, tk.END)


# =====================
# BAIXAR LISTA
# =====================

def baixar_lista():

    if not download_list:
        messagebox.showerror("Erro", "Lista vazia")
        return

    folder = filedialog.askdirectory(title="Escolha a pasta para salvar")

    if not folder:
        return

    btn_baixar.config(state="disabled")

    def task():

        total = len(download_list)

        for i, url in enumerate(download_list, start=1):

            try:

                progress.config(value=0)

                status_label.config(text=f"Buscando info ({i}/{total})")

                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    titulo = info.get("title", "video")

                caracteres_invalidos = r'<>:"/\|?*'
                for c in caracteres_invalidos:
                    titulo = titulo.replace(c, "")

                save_path = os.path.join(folder, f"{titulo}.mp4")

                status_label.config(text=f"Baixando ({i}/{total})")

                with yt_dlp.YoutubeDL({
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': save_path,
                    'progress_hooks': [progress_hook],

                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'Referer': url
                    },

                    'concurrent_fragment_downloads': 5,
                    'fragment_retries': 10,
                    'skip_unavailable_fragments': True
                }) as ydl:

                    ydl.download([url])

            except Exception as e:
                print(e)

        download_list.clear()

        app.after(0, lambda: status_label.config(text="✔ Lista finalizada"))
        app.after(0, lambda: btn_baixar.config(state="normal"))
        app.after(0, lambda: progress.config(value=0))

    threading.Thread(target=task, daemon=True).start()


# =====================
# INTERFACE
# =====================

app = tk.Tk()
app.title("HoofHub Downloader")
app.geometry("500x300")
app.resizable(False, False)

tk.Label(app, text="URL do vídeo:").pack(pady=(15, 5))

entry_url = tk.Entry(app, width=65)
entry_url.pack(pady=5)

btn_baixar = tk.Button(app, text="Salvar como e Baixar", width=22, command=baixar_video)
btn_baixar.pack(pady=10)

btn_add = tk.Button(app, text="Adicionar à Lista", width=22, command=adicionar_lista)
btn_add.pack(pady=5)

btn_lista = tk.Button(app, text="Baixar Lista", width=22, command=baixar_lista)
btn_lista.pack(pady=5)

status_label = tk.Label(app, text="")
status_label.pack()

progress = ttk.Progressbar(app, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=5)

app.mainloop()
