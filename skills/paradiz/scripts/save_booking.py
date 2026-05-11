#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from urllib import parse, request
import re
import zipfile


def send_telegram(bot_token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = request.Request(url, data=payload, method="POST")
    with request.urlopen(req, timeout=15) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Telegram HTTP {resp.status}")


def _extract_amount(s: str) -> float:
    cleaned = re.sub(r"[^0-9,\.]", "", s or "").replace(",", ".")
    if not cleaned:
        return 0.0
    try:
        return float(cleaned)
    except Exception:
        return 0.0


def rtf_escape(value: str) -> str:
    out = []
    for ch in value:
        code = ord(ch)
        if ch in ['\\', '{', '}']:
            out.append('\\' + ch)
        elif code > 127:
            signed = code if code < 32768 else code - 65536
            out.append(f"\\u{signed}?")
        else:
            out.append(ch)
    return ''.join(out)


def _build_repl(data: dict) -> dict:
    total_num = _extract_amount(data.get("total", ""))
    prepay_num = _extract_amount(data.get("prepay", ""))
    rest_num = max(0.0, total_num - prepay_num)
    status = data.get("booking_status", "Предварительное")

    checkin = data.get("checkin", "")
    checkout = data.get("checkout", "")
    period = f"Заезд: {checkin} | Выезд: {checkout}".strip()

    return {
        "BKGNFIO": data.get("guest", ""),
        "BKGNNUMBER": data.get("booking_number", ""),
        "BKGNDATE": data.get("created_at", ""),
        "BKGNBEGINDATE": period,
        "BKGNENDDATE": status,
        "BKGNCATEGORY": data.get("room", ""),
        "BKGNNPEOPLE": str(data.get("guests", "")),
        "BKGNCOSTFULL": data.get("total", ""),
        "BKGNCOSTPAYFULL": data.get("prepay", ""),
        "BKGNCOSTRESTFULL": f"{rest_num:,.0f} ₽".replace(",", " "),
        "BKGNNUMDAYS": str(data.get("nights", "")),
        "CICLSERVICENAME": data.get("room", ""),
        "CICLNUMDAYS": str(data.get("nights", "")),
        "CICLDAYDICOST": data.get("day_price", ""),
        "BKGNSTATUS": status,
    }


def render_booking_rtf(template_path: Path, output_path: Path, data: dict) -> None:
    if not template_path.exists():
        return

    raw = template_path.read_bytes()
    txt = None
    for enc in ("utf-8", "cp1251", "utf-8-sig"):
        try:
            txt = raw.decode(enc)
            break
        except Exception:
            continue
    if txt is None:
        txt = raw.decode("utf-8", errors="ignore")

    repl = _build_repl(data)
    for k, v in repl.items():
        txt = txt.replace(k, rtf_escape(str(v)))

    # Явная пометка статуса в теле документа и подписи полей
    status = repl["BKGNSTATUS"]
    txt = txt.replace("подтверждаем бронирование", f"оформляем {status} бронирование")
    txt = txt.replace("Дата заезда:", "Период проживания:")
    txt = txt.replace("Дата выезда:", "Статус брони:")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(txt, encoding="utf-8")


def render_booking_dotx(template_path: Path, output_path: Path, data: dict) -> None:
    if not template_path.exists():
        return

    repl = _build_repl(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    xml_targets = {
        "word/document.xml",
        "word/header1.xml",
        "word/header2.xml",
        "word/footer1.xml",
        "word/footer2.xml",
    }

    to_docx = output_path.suffix.lower() == '.docx'

    with zipfile.ZipFile(template_path, 'r') as zin, zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            raw = zin.read(info.filename)

            if info.filename in xml_targets:
                try:
                    txt = raw.decode('utf-8')
                    for k, v in repl.items():
                        txt = txt.replace(k, str(v))

                    status = repl["BKGNSTATUS"]
                    txt = txt.replace("подтверждаем бронирование", f"оформляем {status} бронирование")
                    txt = txt.replace("подтверждаем бронирование,", f"оформляем {status} бронирование,")
                    txt = txt.replace("Дата заезда:", "Период проживания:")
                    txt = txt.replace("Дата выезда:", "Статус брони:")
                    raw = txt.encode('utf-8')
                except Exception:
                    pass

            if to_docx and info.filename == '[Content_Types].xml':
                try:
                    txt = raw.decode('utf-8')
                    txt = txt.replace(
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml',
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'
                    )
                    raw = txt.encode('utf-8')
                except Exception:
                    pass

            zout.writestr(info, raw)


def load_telegram_from_config():
    cfg = Path('/home/openclaw/.openclaw/openclaw.json')
    if not cfg.exists():
        return "", ""
    try:
        j = json.loads(cfg.read_text(encoding='utf-8'))
    except Exception:
        return "", ""

    bot = ""
    chat = ""

    # 1) dedicated env for paradiz skill
    try:
        env = j.get('skills', {}).get('entries', {}).get('paradiz', {}).get('env', {})
        bot = (env.get('PARADIZ_TG_BOT_TOKEN') or "").strip()
        chat = str(env.get('PARADIZ_TG_CHAT_ID') or "").strip()
    except Exception:
        pass

    # 2) fallback to channel token format
    if not bot:
        bt = str(j.get('channels', {}).get('telegram', {}).get('botToken', '')).strip()
        if bt.startswith('https://api.telegram.org/bot'):
            bt = bt.replace('https://api.telegram.org/bot', '', 1)
        bot = bt

    return bot, chat


def main():
    p = argparse.ArgumentParser(description="Сохранить бронь и отправить уведомление в Telegram")
    p.add_argument("--guest", required=True, help="ФИО гостя")
    p.add_argument("--phone", required=True, help="Телефон")
    p.add_argument("--email", required=True, help="E-mail")
    p.add_argument("--checkin", required=True, help="Дата заезда YYYY-MM-DD")
    p.add_argument("--checkout", required=True, help="Дата выезда YYYY-MM-DD")
    p.add_argument("--guests", required=True, type=int, help="Количество гостей")
    p.add_argument("--room", required=True, help="Категория номера")
    p.add_argument("--total", required=True, help="Итоговая сумма")
    p.add_argument("--prepay", required=True, help="Сумма предоплаты")
    p.add_argument("--payment-confirmed-by-manager", action="store_true", help="Явное подтверждение менеджера на внесение предоплаты")
    p.add_argument("--notes", default="", help="Комментарий")
    p.add_argument("--file", default="/home/openclaw/.openclaw/workspace/skills/paradiz/data/bookings.txt")
    p.add_argument("--notify", action="store_true", help="Отправить Telegram-уведомление")
    p.add_argument("--template", default="/home/openclaw/.openclaw/workspace/skills/paradiz/data/shablon_broni.dotx", help="Путь к шаблону брони (.dotx/.rtf)")
    p.add_argument("--doc-out", default="", help="Путь сохранения заполненного листа брони (.docx/.doc)")
    p.add_argument("--booking-status", choices=["preliminary", "booked"], default="preliminary", help="Устарело: статус теперь вычисляется автоматически по предоплате")
    args = p.parse_args()

    dt_now = datetime.now()
    now = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    booking_number = dt_now.strftime("PDZ-%Y%m%d-%H%M%S")

    d1 = datetime.strptime(args.checkin, "%Y-%m-%d")
    d2 = datetime.strptime(args.checkout, "%Y-%m-%d")
    nights = max(0, (d2 - d1).days)
    total_num = _extract_amount(args.total)
    day_price = f"{(total_num / nights):,.0f} ₽".replace(",", " ") if nights else ""

    # Жёсткое правило по бизнес-логике:
    # - предоплату можно вносить только после явного подтверждения менеджера
    # - если подтверждения нет, предоплата считается 0 и статус "Предварительное"
    prepay_num = _extract_amount(args.prepay)
    if prepay_num > 0 and not args.payment_confirmed_by_manager:
        raise SystemExit("Предоплата > 0 запрещена без флага --payment-confirmed-by-manager")

    booking_status = "Забронировано" if prepay_num > 0 else "Предварительное"

    entry = {
        "created_at": now,
        "booking_number": booking_number,
        "booking_status": booking_status,
        "guest": args.guest,
        "phone": args.phone,
        "email": args.email,
        "checkin": args.checkin,
        "checkout": args.checkout,
        "guests": args.guests,
        "room": args.room,
        "total": args.total,
        "prepay": args.prepay,
        "notes": args.notes,
        "nights": nights,
        "day_price": day_price,
    }

    out = Path(args.file)
    out.parent.mkdir(parents=True, exist_ok=True)

    prepay_state = "внесена" if prepay_num > 0 else "не внесена"

    human = (
        f"[{now}] БРОНЬ {booking_number} ({booking_status})\n"
        f"Гость: {args.guest}\n"
        f"Телефон: {args.phone}\n"
        f"Email: {args.email}\n"
        f"Период: {args.checkin} → {args.checkout}\n"
        f"Гостей: {args.guests}\n"
        f"Номер: {args.room}\n"
        f"Итого: {args.total}\n"
        f"Предоплата: {args.prepay} ({prepay_state})\n"
        f"Комментарий: {args.notes or '-'}\n"
        f"---\n"
    )

    with out.open("a", encoding="utf-8") as f:
        f.write(human)

    jsonl = out.with_suffix(".jsonl")
    with jsonl.open("a", encoding="utf-8") as jf:
        jf.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Генерируем клиентский лист брони из шаблона (.dotx/.rtf)
    default_doc_dir = out.parent / "listbroni"
    template_path = Path(args.template)
    if args.doc_out:
        doc_out = args.doc_out.strip()
    else:
        ext = ".docx" if template_path.suffix.lower() == ".dotx" else ".doc"
        doc_out = str(default_doc_dir / f"booking_{booking_number}{ext}")

    try:
        if template_path.suffix.lower() == ".dotx":
            render_booking_dotx(template_path, Path(doc_out), entry)
        else:
            render_booking_rtf(template_path, Path(doc_out), entry)
    except Exception:
        pass

    sent = False
    err = None
    if args.notify:
        bot_token = os.getenv("PARADIZ_TG_BOT_TOKEN", "").strip()
        chat_id = os.getenv("PARADIZ_TG_CHAT_ID", "").strip()
        if not (bot_token and chat_id):
            cfg_bot, cfg_chat = load_telegram_from_config()
            bot_token = bot_token or cfg_bot
            chat_id = chat_id or cfg_chat

        if bot_token and chat_id:
            text = (
                "📌 Новая бронь Парадиз\n"
                f"Номер брони: {booking_number}\n"
                f"Статус: {booking_status}\n"
                f"Гость: {args.guest}\n"
                f"Телефон: {args.phone}\n"
                f"Email: {args.email}\n"
                f"Период: {args.checkin} → {args.checkout}\n"
                f"Гостей: {args.guests}\n"
                f"Номер: {args.room}\n"
                f"Итого: {args.total}\n"
                f"Предоплата: {args.prepay} ({prepay_state})\n"
                f"Комментарий: {args.notes or '-'}"
            )
            try:
                send_telegram(bot_token, chat_id, text)
                sent = True
            except Exception as e:
                err = str(e)
        else:
            err = "PARADIZ_TG_BOT_TOKEN / PARADIZ_TG_CHAT_ID не заданы"

    print(json.dumps({"ok": True, "booking_number": booking_number, "saved": str(out), "jsonl": str(jsonl), "doc": str(doc_out), "telegram_sent": sent, "telegram_error": err}, ensure_ascii=False))


if __name__ == "__main__":
    main()
