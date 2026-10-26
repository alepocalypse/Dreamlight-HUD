import argparse
import threading

from . import app, config, server

p = argparse.ArgumentParser(prog="ddvhud", description="Read-only Dreamlight Valley HUD")
p.add_argument("--save", default=None,
               help="game save folder (containing steam_*) or a profile.json file")
p.add_argument("--port", type=int, default=8765)
p.add_argument("--window", action="store_true",
               help="show the HUD in its own window instead of a browser tab")
p.add_argument("--duty", action="store_true",
               help="open window mode in a narrow window (about 400 x 900) straight into Duty mode")
a = p.parse_args()
save = a.save or config.load_save_path() or app.DEFAULT_ROOT

if not (a.window or a.duty):
    server.serve(save, a.port)
else:
    def pick_save():
        """Native folder dialog; the chosen folder (or profile.json's folder) or None."""
        import webview
        got = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        return got[0] if got else None

    try:
        import webview
    except ImportError:
        webview = None
    httpd = server.make_server(save, 0 if a.port == 8765 else a.port,
                               pick_save if webview else None)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url, width, height = server.window_spec(httpd.server_address[1], a.duty)
    if webview:
        webview.create_window("Duty mode" if a.duty else "Dreamlight HUD", url, width=width, height=height)
        webview.start()
    else:
        import webbrowser
        print(f"pywebview not installed; opening {url} in your browser (Ctrl+C to quit)")
        webbrowser.open(url)
        threading.Event().wait()
