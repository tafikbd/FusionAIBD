from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from database import get_stats, get_pending_payments, get_user, update_user, activate_premium
from keyboards import admin_panel_keyboard

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def admin_cmd(update, context):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("Admin Panel:", reply_markup=admin_panel_keyboard())

async def stats_cmd(update, context):
    if not is_admin(update.effective_user.id):
        return
    s = get_stats()
    m = "Statistics" + chr(10) + chr(10)
    m += "Users: " + str(s['total_users']) + chr(10)
    m += "Premium: " + str(s['premium_users']) + chr(10)
    m += "Asks: " + str(s['total_asks']) + chr(10)
    m += "Payments: " + str(s['approved_payments']) + chr(10)
    m += "Revenue: Tk " + str(s['revenue'])
    await update.message.reply_text(m)

async def pending_cmd(update, context):
    if not is_admin(update.effective_user.id):
        return
    ps = get_pending_payments()
    if not ps:
        await update.message.reply_text("No pending payment")
        return
    for p in ps[:5]:
        m = "#" + str(p['payment_id']) + chr(10)
        m += "User: " + p['user_name'] + " (" + str(p['user_id']) + ")" + chr(10)
        m += p['plan'].upper() + " - Tk " + str(p['amount']) + chr(10)
        m += "Method: " + p['method'] + chr(10)
        m += "TrxID: " + p['trx_id']
        await update.message.reply_text(m)

async def approve_cmd(update, context):
    if not is_admin(update.effective_user.id):
        return
    try:
        parts = update.message.text.split()
        uid = int(parts[1])
        plan = parts[2]
        days = int(parts[3])
        activate_premium(uid, plan, days)
        await update.message.reply_text(str(uid) + " got " + str(days) + " days " + plan)
    except:
        await update.message.reply_text("Usage: /approve user_id plan days")

async def remove_premium_cmd(update, context):
    if not is_admin(update.effective_user.id):
        return
    try:
        uid = int(update.message.text.split()[1])
        update_user(uid, plan="free", premium_until=None)
        await update.message.reply_text(str(uid) + " premium removed")
    except:
        await update.message.reply_text("Usage: /removepremium user_id")

async def ban_cmd(update, context):
    if not is_admin(update.effective_user.id):
        return
    try:
        uid = int(update.message.text.split()[1])
        update_user(uid, banned=1)
        await update.message.reply_text(str(uid) + " banned")
    except:
        await update.message.reply_text("Usage: /ban user_id")

async def unban_cmd(update, context):
    if not is_admin(update.effective_user.id):
        return
    try:
        uid = int(update.message.text.split()[1])
        update_user(uid, banned=0)
        await update.message.reply_text(str(uid) + " unbanned")
    except:
        await update.message.reply_text("Usage: /unban user_id")

async def userinfo_cmd(update, context):
    if not is_admin(update.effective_user.id):
        return
    try:
        uid = int(update.message.text.split()[1])
        u = get_user(uid)
        if not u:
            await update.message.reply_text("User not found")
            return
        m = "Name: " + str(u['name']) + chr(10)
        m += "ID: " + str(u['user_id']) + chr(10)
        m += "Plan: " + str(u['plan']) + chr(10)
        m += "Until: " + str(u['premium_until'] or 'N/A') + chr(10)
        m += "Total: " + str(u['total_ask']) + chr(10)
        m += "Today: " + str(u['daily_count']) + chr(10)
        m += "Refer count: " + str(u['refer_count'])
        await update.message.reply_text(m)
    except:
        await update.message.reply_text("Usage: /userinfo user_id")

async def broadcast_cmd(update, context):
    if not is_admin(update.effective_user.id):
        return
    msg = update.message.text.replace("/broadcast", "").strip()
    if not msg:
        await update.message.reply_text("Usage: /broadcast message")
        return
    import sqlite3
    from database import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE banned=0")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    sent = 0
    failed = 0
    for uid in users:
        try:
            await context.bot.send_message(uid, msg)
            sent += 1
        except:
            failed += 1
    await update.message.reply_text("Sent: " + str(sent) + ", Failed: " + str(failed))
