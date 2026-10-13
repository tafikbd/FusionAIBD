from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import PLANS, PRICING

def premium_plans_keyboard():
    btns = []
    for pid, p in PLANS.items():
        if pid == "free":
            continue
        btns.append([InlineKeyboardButton(p['name'] + " - Tk " + str(p['price_bdt']), callback_data="plan_" + pid)])
    btns.append([InlineKeyboardButton("Close", callback_data="close")])
    return InlineKeyboardMarkup(btns)

def durations_keyboard(plan_id):
    btns = []
    if plan_id in PRICING:
        for did, d in PRICING[plan_id].items():
            btns.append([InlineKeyboardButton(d['label'] + " - Tk " + str(d['price']), callback_data="dur_" + plan_id + "_" + did)])
    btns.append([InlineKeyboardButton("Back", callback_data="back_premium")])
    return InlineKeyboardMarkup(btns)

def payment_methods_keyboard(plan_id, dur_id):
    btns = []
    btns.append([InlineKeyboardButton("bKash", callback_data="pay_bkash_" + plan_id + "_" + dur_id)])
    btns.append([InlineKeyboardButton("Rocket", callback_data="pay_rocket_" + plan_id + "_" + dur_id)])
    btns.append([InlineKeyboardButton("Binance Pay", callback_data="pay_binance_" + plan_id + "_" + dur_id)])
    btns.append([InlineKeyboardButton("USDT TRC20", callback_data="pay_usdt_trc_" + plan_id + "_" + dur_id)])
    btns.append([InlineKeyboardButton("USDT BSC20", callback_data="pay_usdt_bsc_" + plan_id + "_" + dur_id)])
    btns.append([InlineKeyboardButton("Back", callback_data="plan_" + plan_id)])
    return InlineKeyboardMarkup(btns)

def admin_payment_keyboard(payment_id):
    btns = []
    btns.append([InlineKeyboardButton("Approve", callback_data="adm_ok_" + str(payment_id)), InlineKeyboardButton("Reject", callback_data="adm_no_" + str(payment_id))])
    return InlineKeyboardMarkup(btns)

def admin_panel_keyboard():
    btns = []
    btns.append([InlineKeyboardButton("Stats", callback_data="adm_stats")])
    btns.append([InlineKeyboardButton("Pending", callback_data="adm_pending")])
    btns.append([InlineKeyboardButton("Close", callback_data="close")])
    return InlineKeyboardMarkup(btns)

def my_account_keyboard():
    btns = []
    btns.append([InlineKeyboardButton("Buy Premium", callback_data="open_premium")])
    btns.append([InlineKeyboardButton("Refer Link", callback_data="show_refer")])
    btns.append([InlineKeyboardButton("Close", callback_data="close")])
    return InlineKeyboardMarkup(btns)
