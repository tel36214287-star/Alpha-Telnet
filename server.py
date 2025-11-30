#!/usr/bin/env python3
# serverbox.py
import asyncio
import os
import signal
import json
from storage import Storage

HOST = "0.0.0.0"
PORT = int(os.environ.get("USENET_PORT", "11900"))
WELCOME = b"200 Usenet-simulator ready\r\n"

storage = Storage()
DATA_BACKUP = os.environ.get("USENET_BACKUP", "storage_backup.json")

# sample seed
storage.add_group("comp.example")
storage.add_group("talk.example")
storage.add_article("comp.example", "Welcome", "admin@example", "This is a sample article.")

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"[+] Conexão de {addr}")
    try:
        writer.write(WELCOME)
        await writer.drain()
        current_group = None

        while True:
            data = await reader.readline()
            if not data:
                break
            line = data.decode(errors="replace").rstrip("\r\n")
            if not line:
                continue
            parts = line.split(maxsplit=1)
            cmd = parts[0].upper()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "QUIT":
                writer.write(b"205 Goodbye\r\n")
                await writer.drain()
                break

            elif cmd == "LIST":
                groups = storage.list_groups()
                writer.write(b"215 list of newsgroups follows\r\n")
                for g in groups:
                    writer.write(f"{g}\r\n".encode())
                writer.write(b".\r\n")

            elif cmd == "GROUP":
                if not arg:
                    writer.write(b"501 Missing group name\r\n")
                elif not storage.has_group(arg):
                    writer.write(b"411 No such group\r\n")
                else:
                    current_group = arg
                    count = storage.count_articles(arg)
                    writer.write(f"211 {count} {arg}\r\n".encode())

            elif cmd == "ARTICLE":
                if not arg:
                    writer.write(b"501 Missing article id\r\n")
                else:
                    try:
                        aid = int(arg)
                    except ValueError:
                        writer.write(b"501 Invalid article id\r\n")
                        await writer.drain()
                        continue
                    art = storage.get_article(current_group, aid) if current_group else storage.get_article_any(aid)
                    if art is None:
                        writer.write(b"423 No such article number here\r\n")
                    else:
                        writer.write(b"220 Article follows\r\n")
                        writer.write(f"Subject: {art['subject']}\r\n".encode())
                        writer.write(f"From: {art['from']}\r\n".encode())
                        writer.write(b"\r\n")
                        for ln in art['body'].splitlines():
                            # escape leading dot
                            if ln.startswith("."):
                                writer.write(b"." + ln.encode() + b"\r\n")
                            else:
                                writer.write(ln.encode() + b"\r\n")
                        writer.write(b".\r\n")

            elif cmd == "POST":
                writer.write(b"340 Send article; end with <CR-LF>.<CR-LF>\r\n")
                await writer.drain()
                headers = {}
                body_lines = []
                # read headers until blank line
                while True:
                    line_bytes = await reader.readline()
                    if not line_bytes:
                        break
                    line_str = line_bytes.decode(errors="replace").rstrip("\r\n")
                    if line_str == "":
                        break
                    if ":" in line_str:
                        k, v = line_str.split(":", 1)
                        headers[k.strip().lower()] = v.strip()
                # read body until single dot line
                while True:
                    line_bytes = await reader.readline()
                    if not line_bytes:
                        break
                    line_str = line_bytes.decode(errors="replace").rstrip("\r\n")
                    if line_str == ".":
                        break
                    # unescape leading dot
                    if line_str.startswith(".."):
                        line_str = line_str[1:]
                    body_lines.append(line_str)
                subj = headers.get("subject", "No subject")
                frm = headers.get("from", "anonymous")
                group = headers.get("newsgroups", None)
                if not group:
                    writer.write(b"441 Posting failed: no Newsgroups header\r\n")
                else:
                    aid = storage.add_article(group, subj, frm, "\n".join(body_lines))
                    writer.write(f"240 Article posted, assigned number {aid}\r\n".encode())

            else:
                writer.write(b"500 Unknown command\r\n")

            await writer.drain()
    except ConnectionResetError:
        print(f"[-] Cliente {addr} desconectou abruptamente.")
    except Exception as e:
        print(f"[!] Erro no handler de {addr}: {e}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        print(f"[-] Conexão encerrada: {addr}")

def backup_storage():
    try:
        data = {
            "groups": storage.groups,
            "articles": storage.articles,
            "_next_id": next(storage._id_iter)
        }
        with open(DATA_BACKUP, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[i] Backup salvo em {DATA_BACKUP}")
    except Exception as e:
        print(f"[!] Falha ao salvar backup: {e}")

def load_backup():
    if not os.path.exists(DATA_BACKUP):
        return
    try:
        with open(DATA_BACKUP, "r", encoding="utf-8") as f:
            data = json.load(f)
        # restore groups and articles
        storage.groups = {k: v for k, v in data.get("groups", {}).items()}
        storage.articles = {int(k): v for k, v in (data.get("articles") or {}).items()}
        start = int(data.get("_next_id", 1))
        storage._id_iter = iter(range(start, 10**12))  # fallback simple iterator
        print(f"[i] Backup carregado de {DATA_BACKUP}")
    except Exception as e:
        print(f"[!] Falha ao carregar backup: {e}")

async def main():
    load_backup()
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"[i] Servindo em {addrs} (CTRL-C para parar)")
    async with server:
        await server.serve_forever()

def shutdown(loop):
    print("[i] Shut down recebido — salvando backup e finalizando.")
    backup_storage()
    for task in asyncio.all_tasks(loop):
        task.cancel()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda s=sig: shutdown(loop))
        except NotImplementedError:
            # Windows em algumas versões não suporta add_signal_handler em loop
            pass
    try:
        loop.run_until_complete(main())
    except asyncio.CancelledError:
        pass
    finally:
        backup_storage()
        loop.close()
        print("[i] Servidor encerrado.")
