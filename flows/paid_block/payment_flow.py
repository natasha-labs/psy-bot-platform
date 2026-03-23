import os
from telegram import LabeledPrice

from storage.results_store import set_payment_info
from flows.paid_block.paid_access import grant_paid_access
from flows.paid_block.paid_entry import send_paid_entry

PROVIDER_TOKEN = os.getenv("TELEGRAM_PROVIDER_TOKEN", "")
PAYMENT_CURRENCY = os.getenv("PAYMENT_CURRENCY", "EUR")
PAYMENT_AMOUNT = int(os.getenv("PAYMENT_AMOUNT", "990"))


async def send_deep_profile_invoice(update, context):
    if not PROVIDER_TOKEN:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Оплата пока не подключена. Нужен TELEGRAM_PROVIDER_TOKEN.",
        )
        return

    user = update.effective_user
    user_id = user.id if user else "unknown"

    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Полный код личности",
        description="Углублённый разбор второго блока",
        payload=f"deep_profile:{user_id}",
        provider_token=PROVIDER_TOKEN,
        currency=PAYMENT_CURRENCY,
        prices=[LabeledPrice("Полный код личности", PAYMENT_AMOUNT)],
        start_parameter="deep-profile-access",
    )


async def handle_pre_checkout(update, context):
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def handle_successful_payment(update, context):
    payment = update.message.successful_payment
    user = update.effective_user
    user_id = user.id if user else "unknown"

    grant_paid_access(user_id)

    set_payment_info(
        user_id,
        {
            "currency": payment.currency,
            "total_amount": payment.total_amount,
            "telegram_payment_charge_id": payment.telegram_payment_charge_id,
            "provider_payment_charge_id": payment.provider_payment_charge_id,
        },
    )

    await send_paid_entry(update, context)
