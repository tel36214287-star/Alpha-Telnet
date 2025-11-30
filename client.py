#!/usr/bin/env python3
import argparse
import asyncio

async def run_client(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    # read welcome
    welcome = await reader.readline()
    print(welcome.decode().rstrip())

    async def send(cmd):
        writer.write((cmd + "\r\n").encode())
        await writer.drain()
        # read response lines until a single dot or a single-line response (codes)
        lines = []
        while True:
            line = await reader.readline()
            if not line:
                break
            s = line.decode().rstrip("\r\n")
            lines.append(s)
            # responses that open multiline: "215", "220", "340"
            if s.startswith("215") or s.startswith("220") or s.startswith("340"):
                # read multiline until dot
                while True:
                    l = await reader.readline()
                    if not l:
                        break
                    ls = l.decode().rstrip("\r\n")
                    if ls == ".":
                        break
                    lines.append(ls)
                break
            # single-line codes end here
            if s and s[0].isdigit():
                break
            # not a numeric code -> probably raw lines
            if s == ".":
                break
        return lines

    print("Comandos: list, group <name>, article <id>, post, quit")
    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue
        if cmd == "quit":
            await send("QUIT")
            break
        if cmd == "list":
            res = await send("LIST")
            print("\n".join(res))
        elif cmd.startswith("group "):
            res = await send(cmd.upper())
            print("\n".join(res))
        elif cmd.startswith("article "):
            res = await send(cmd.upper())
            print("\n".join(res))
        elif cmd == "post":
            # interactive post
            ng = input("Newsgroups: ").strip()
            subj = input("Subject: ").strip()
            frm = input("From: ").strip()
            print("Enter body lines. Finish with a single dot on its own line.")
            body_lines = []
            while True:
                ln = input()
                if ln == ".":
                    break
                # escape leading dot
                if ln.startswith("."):
                    ln = "." + ln
                body_lines.append(ln)
            writer.write(b"POST\r\n")
            await writer.drain()
            # read 340
            l = await reader.readline()
            print(l.decode().rstrip())
            # send headers
            writer.write(f"Newsgroups: {ng}\r\n".encode())
            writer.write(f"Subject: {subj}\r\n".encode())
            writer.write(f"From: {frm}\r\n".encode())
            writer.write(b"\r\n")
            for ln in body_lines:
                writer.write((ln + "\r\n").encode())
            writer.write(b".\r\n")
            await writer.drain()
            # read response
            resp = await reader.readline()
            print(resp.decode().rstrip())
        else:
            print("Comando não reconhecido.")

    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=11900)
    args = parser.parse_args()
    asyncio.run(run_client(args.host, args.port))
